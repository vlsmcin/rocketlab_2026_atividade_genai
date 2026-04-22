from typing import Any

from ..text_to_sql.agent import TextToSQLDeps
from ..text_to_sql.chase import run_chase_self_consistency
from ..text_to_sql.db import DEFAULT_DB_PATH


def _build_deps(db_path: str | None = None, schema: str = "") -> TextToSQLDeps:
    return TextToSQLDeps(db_path=db_path or DEFAULT_DB_PATH, schema=schema)


async def run_text_to_sql(
    question: str,
    db_path: str | None = None,
    schema: str = "",
    n_candidates: int = 4,
) -> dict[str, Any]:
    """Executa o agente CHASE e retorna o resultado estruturado."""
    deps = _build_deps(db_path=db_path, schema=schema)
    return await run_chase_self_consistency(
        question=question,
        deps=deps,
        n_candidates=n_candidates,
    )