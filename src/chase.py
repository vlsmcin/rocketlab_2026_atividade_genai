import hashlib
import json
from dataclasses import dataclass

from .agent import TextToSQLDeps, create_text_to_sql_agent
from . import db as db_ops


@dataclass
class Candidate:
    temperature: float
    query: str
    result: list[tuple]
    confidence: float


@dataclass
class CandidateError:
    temperature: float
    stage: str
    error: str
    query: str | None = None


def _temperature_schedule(n_candidates: int) -> list[float]:
    base = [0.0, 0.2, 0.4, 0.6, 0.8]
    if n_candidates <= len(base):
        return base[:n_candidates]

    extra = [min(0.95, 0.1 * i) for i in range(len(base), n_candidates)]
    return base + extra


def _result_signature(rows: list[tuple]) -> str:
    payload = json.dumps([list(row) for row in rows], ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _build_grounded_prompt(question: str, schema_text: str) -> str:
    return (
        "Use estritamente o schema abaixo. "
        "Nao invente tabelas/colunas fora da lista.\n\n"
        f"SCHEMA:\n{schema_text}\n\n"
        f"PERGUNTA:\n{question}"
    )


async def run_chase_self_consistency(
    question: str,
    deps: TextToSQLDeps,
    n_candidates: int = 5,
) -> dict:
    """Executa self-consistency no estilo CHASE e escolhe o candidato por consenso de resultado."""
    agent = create_text_to_sql_agent()
    temperatures = _temperature_schedule(max(1, n_candidates))
    schema_text = deps.schema.strip() if deps.schema else db_ops.schema_as_text(deps.db_path)
    grounded_prompt = _build_grounded_prompt(question, schema_text)

    valid_candidates: list[Candidate] = []
    failed_candidates: list[CandidateError] = []

    for temperature in temperatures:
        run_result = None
        extracted_sql: str | None = None

        try:
            run_result = await agent.run(
                grounded_prompt,
                deps=deps,
                model_settings={"temperature": temperature},
            )

        except Exception as exc:
            failed_candidates.append(
                CandidateError(
                    temperature=temperature,
                    stage="agent_run",
                    error=str(exc),
                )
            )
            continue

        try:
            extracted_sql = db_ops.extract_sql(run_result.output.query)
        except Exception as exc:
            failed_candidates.append(
                CandidateError(
                    temperature=temperature,
                    stage="extract_sql",
                    error=str(exc),
                    query=getattr(run_result.output, "query", None),
                )
            )
            continue

        try:
            verified_rows = db_ops.execute_query(
                query=extracted_sql,
                db_path=deps.db_path,
                max_rows=100,
            )

            if verified_rows and isinstance(verified_rows[0], tuple) and verified_rows[0]:
                if verified_rows[0][0] == "__SQL_ERROR__":
                    failed_candidates.append(
                        CandidateError(
                            temperature=temperature,
                            stage="execute_query",
                            error=str(verified_rows[0][1]),
                            query=str(verified_rows[0][2]),
                        )
                    )
                    continue

            valid_candidates.append(
                Candidate(
                    temperature=temperature,
                    query=extracted_sql,
                    result=verified_rows,
                    confidence=run_result.output.confidence,
                )
            )
        except Exception as exc:
            failed_candidates.append(
                CandidateError(
                    temperature=temperature,
                    stage="execute_query",
                    error=str(exc),
                    query=extracted_sql,
                )
            )

    if not valid_candidates:
        return {
            "status": "error",
            "message": "Nenhum candidato SQL válido foi gerado.",
            "question": question,
            "failed_candidates": [c.__dict__ for c in failed_candidates],
        }

    groups: dict[str, list[Candidate]] = {}
    for candidate in valid_candidates:
        signature = _result_signature(candidate.result)
        groups.setdefault(signature, []).append(candidate)

    ranked_groups = sorted(
        groups.values(),
        key=lambda group: (len(group), max(c.confidence for c in group)),
        reverse=True,
    )
    winning_group = ranked_groups[0]

    winner = max(
        winning_group,
        key=lambda candidate: candidate.confidence,
    )

    return {
        "status": "ok",
        "question": question,
        "query": winner.query,
        "result": winner.result,
        "confidence": winner.confidence,
        "candidate_queries": [
            {
                "temperature": c.temperature,
                "query": c.query,
                "confidence": c.confidence,
                "rows": len(c.result),
            }
            for c in valid_candidates
        ],
        "agreement": {
            "votes": len(winning_group),
            "total_valid": len(valid_candidates),
            "temperatures": [c.temperature for c in winning_group],
        },
        "failed_candidates": [c.__dict__ for c in failed_candidates],
    }
