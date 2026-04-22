import re

from .schemas import AskResponse
from ..formatters import format_result
from ..services import run_text_to_sql


ANSI_ESCAPE_RE = re.compile(r"\x1b\[[0-9;]*m")

PRIVATE_RESULT_KEYS = {
    "candidate_queries",
    "failed_candidates",
    "agreement",
}


def strip_ansi(text: str) -> str:
    return ANSI_ESCAPE_RE.sub("", text)


def sanitize_result_for_frontend(result: dict) -> dict:
    """Remove campos de debug interno antes de enviar ao frontend."""
    return {k: v for k, v in result.items() if k not in PRIVATE_RESULT_KEYS}


async def process_question(question: str) -> AskResponse:
    result = await run_text_to_sql(question)
    formatted = strip_ansi(format_result(result))
    public_result = sanitize_result_for_frontend(result)
    return AskResponse(
        status=result.get("status", "error"),
        formatted_output=formatted,
        result=public_result,
    )