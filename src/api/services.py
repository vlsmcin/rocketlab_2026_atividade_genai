import re

from .schemas import AskResponse
from ..formatters import format_result
from ..services import run_text_to_sql


ANSI_ESCAPE_RE = re.compile(r"\x1b\[[0-9;]*m")


def strip_ansi(text: str) -> str:
    return ANSI_ESCAPE_RE.sub("", text)


async def process_question(question: str) -> AskResponse:
    result = await run_text_to_sql(question)
    formatted = strip_ansi(format_result(result))
    return AskResponse(
        status=result.get("status", "error"),
        formatted_output=formatted,
        result=result,
    )