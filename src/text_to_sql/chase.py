import hashlib
import json
import re
from dataclasses import dataclass

from guardrails import Guard
from guardrails.validators import (
    FailResult,
    PassResult,
    Validator,
    register_validator,
)

from . import db as db_ops
from .agent import TextToSQLDeps, create_text_to_sql_agent


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


def _schema_terms(schema_text: str) -> set[str]:
    terms: set[str] = set()
    for token in re.findall(r"[a-zA-Z0-9_]+", schema_text.lower()):
        terms.add(token)
        if "_" in token:
            terms.update(part for part in token.split("_") if part)
    return terms


def _question_terms(question: str) -> set[str]:
    return {token for token in re.findall(r"[a-zA-Z0-9_]+", question.lower()) if token}


@register_validator(name="database-question", data_type="string")
class DatabaseQuestionValidator(Validator):
    def __init__(self, schema_text: str, on_fail=None, **kwargs):
        super().__init__(on_fail=on_fail, schema_text=schema_text, **kwargs)
        self.schema_text = schema_text

    def validate(self, value, metadata) -> object:
        question_terms = _question_terms(value)
        schema_terms = _schema_terms(self.schema_text)
        analytics_terms = {
            "top",
            "total",
            "quantidade",
            "contagem",
            "media",
            "média",
            "receita",
            "taxa",
            "ranking",
            "maior",
            "menor",
            "percentual",
            "percentagem",
            "comparar",
            "comparacao",
            "comparação",
        }
        business_terms = {
            "pedido",
            "pedidos",
            "produto",
            "produtos",
            "categoria",
            "categorias",
            "estado",
            "estados",
            "avaliacao",
            "avaliacoes",
            "avaliação",
            "avaliações",
            "review",
            "reviews",
            "atraso",
            "atrasos",
            "vendedor",
            "vendedores",
            "cliente",
            "clientes",
            "consumidor",
            "consumidores",
        }
        generic_terms = {
            "poema",
            "piada",
            "clima",
            "filme",
            "música",
            "musica",
            "esporte",
            "politica",
            "política",
            "religiao",
            "religião",
            "saude",
            "saúde",
            "noticia",
            "notícias",
            "noticias",
        }

        if question_terms & generic_terms:
            return FailResult(error_message="Pergunta fora do domínio do banco de dados.")

        has_business_signal = bool(question_terms & business_terms or question_terms & schema_terms)
        has_analytics_signal = bool(question_terms & analytics_terms)

        if has_business_signal and has_analytics_signal:
            return PassResult()

        if has_business_signal and ("maior" in question_terms or "menor" in question_terms or "top" in question_terms):
            return PassResult()

        return FailResult(
            error_message="Pergunta bloqueada: não está claramente ancorada no schema do banco de dados."
        )


def _run_guardrail(question: str, schema_text: str) -> dict[str, object]:
    guard = Guard.for_string(
        validators=[DatabaseQuestionValidator(schema_text=schema_text, on_fail="noop")],
        string_description="Pergunta sobre banco de dados",
        name="text-to-sql-guardrail",
    )
    outcome = guard.validate(question)

    return {
        "allowed": bool(getattr(outcome, "validation_passed", False)),
        "score": 0,
        "signals": [],
        "reason": getattr(outcome, "error", None) or getattr(outcome, "error_message", None) or "Pergunta validada pelo guard rail.",
        "guardrails_used": True,
    }


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
    schema_text = deps.schema.strip() if deps.schema else db_ops.schema_as_text(deps.db_path)
    guardrail_result = _run_guardrail(question, schema_text)
    is_allowed = bool(guardrail_result["allowed"])
    guardrail_message = str(guardrail_result["reason"])

    if not is_allowed:
        return {
            "status": "blocked",
            "question": question,
            "message": guardrail_message,
            "failed_candidates": [],
            "guardrail": {
                "allowed": False,
                "reason": guardrail_message,
                "score": guardrail_result["score"],
                "signals": guardrail_result["signals"],
                "engine": "guardrails",
            },
        }

    agent = create_text_to_sql_agent()
    temperatures = _temperature_schedule(max(1, n_candidates))
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
        "guardrail": {
            "allowed": True,
            "reason": guardrail_message,
            "score": guardrail_result["score"],
            "signals": guardrail_result["signals"],
            "engine": "guardrails",
        },
    }