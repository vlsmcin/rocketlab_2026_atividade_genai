from typing import Any

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, description="Pergunta em linguagem natural sobre o banco")


class AskResponse(BaseModel):
    status: str
    formatted_output: str
    result: dict[str, Any]


class HealthResponse(BaseModel):
    status: str