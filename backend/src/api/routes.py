from fastapi import APIRouter, HTTPException

from .schemas import AskRequest, AskResponse, HealthResponse
from .services import process_question


router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok")


@router.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest) -> AskResponse:
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="A pergunta nao pode ser vazia.")

    try:
        return await process_question(question)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro ao processar pergunta: {exc}") from exc