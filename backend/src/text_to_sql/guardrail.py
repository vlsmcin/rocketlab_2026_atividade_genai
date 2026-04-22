"""
Módulo de guard rails para validação de perguntas sobre banco de dados.

Utiliza um modelo LLM (Gemini) para validar semanticamente se uma pergunta
é relevante ao contexto do banco de dados, funcionando em qualquer idioma.
"""

import re
import unicodedata
from pydantic import BaseModel
from pydantic_ai import Agent
from guardrails import Guard
from guardrails.validators import (
    FailResult,
    PassResult,
    Validator,
    register_validator,
)
from pydantic_ai.models.google import GoogleModel



class RelevanceCheckResult(BaseModel):
    is_relevant: bool
    reasoning: str


def _normalized_text(text: str) -> str:
    """Normaliza texto para comparação case-insensitive e sem acentos."""
    normalized_text = unicodedata.normalize("NFKD", text.lower())
    return "".join(char for char in normalized_text if not unicodedata.combining(char))


def _question_terms(question: str) -> set[str]:
    """Extrai termos da pergunta normalizada."""
    normalized_question = _normalized_text(question)
    return {token for token in re.findall(r"[a-z0-9_]+", normalized_question) if token}


async def validate_with_model(question: str, schema_text: str) -> dict[str, object]:
    """
    Valida se a pergunta é relevante ao banco de dados usando um modelo LLM.

    Args:
        question: Pergunta do usuário
        schema_text: Schema do banco de dados

    Returns:
        Dict com 'allowed' (bool) e 'reason' (str)
    """
    try:
        model = GoogleModel("gemini-2.5-flash-lite")

        agent = Agent(
            model,
            result_type=RelevanceCheckResult,
        )

        prompt = f"""Você é um validador que verifica se uma pergunta é relevante para consultas em um banco de dados.

        SCHEMA DO BANCO DE DADOS:
        {schema_text}

        PERGUNTA DO USUÁRIO:
        {question}

        Determine se a pergunta é relevante para fazer consultas ou análises neste banco de dados.
        - Perguntas sobre dados, tabelas, colunas, análises, relatórios sobre os dados: RELEVANTE
        - Perguntas completamente off-topic (clima, piadas, filmes, política, etc.): NÃO RELEVANTE
        - Perguntas abstratas sobre os dados: RELEVANTE

        Responda em JSON com:
        - is_relevant: true ou false
        - reasoning: breve explicação em 1-2 linhas"""

        result = await agent.run(prompt)

        return {
            "allowed": result.data.is_relevant,
            "reason": result.data.reasoning,
        }
    except Exception as e:
        # Fallback: se o modelo falhar, deixa passar (assume que é relevante)
        return {
            "allowed": True,
            "reason": f"Validação com modelo falhou ({str(e)}), deixando passar por segurança.",
        }


@register_validator(name="database-question", data_type="string")
class DatabaseQuestionValidator(Validator):
    """Validador Guardrails que bloqueia tópicos claramente off-topic."""

    def __init__(self, schema_text: str, on_fail=None, **kwargs):
        super().__init__(on_fail=on_fail, schema_text=schema_text, **kwargs)
        self.schema_text = schema_text

    def validate(self, value, metadata) -> object:
        """
        Validação rápida baseada em listas de tópicos bloqueados.
        """
        normalized_question = _normalized_text(value)
        question_terms = _question_terms(value)

        # Tópicos completamente fora do escopo que devem ser bloqueados
        blocked_topics = {
            "poema",
            "piada",
            "piadas",
            "clima",
            "previsao",
            "previsão",
            "filme",
            "filmes",
            "cinema",
            "música",
            "musica",
            "cancao",
            "canção",
            "esporte",
            "esportes",
            "futebol",
            "politica",
            "política",
            "eleicao",
            "eleição",
            "voto",
            "religiao",
            "religião",
            "deus",
            "saude",
            "saúde",
            "doenca",
            "doença",
            "medicamento",
            "noticia",
            "notícia",
            "noticias",
            "notícias",
            "receita",
            "culinaria",
            "culinária",
            "comida",
            "viagem",
            "turismo",
            "hotel",
            "voo",
            "aviao",
            "avião",
        }

        # Se a pergunta tem APENAS tópicos bloqueados, rejeita
        if question_terms & blocked_topics and not any(
            term in normalized_question
            for term in ["dado", "tabela", "coluna", "sql", "banco", "consulta"]
        ):
            return FailResult(
                error_message="Pergunta fora do escopo do banco de dados."
            )

        # Qualquer coisa que mencione dados, banco, tabelas, etc. passa
        if any(
            term in normalized_question
            for term in [
                "dado",
                "dados",
                "tabela",
                "coluna",
                "sql",
                "banco",
                "base",
                "consulta",
                "registro",
                "registros",
            ]
        ):
            return PassResult()

        # Se tem pelo menos 2 palavras, assume que é uma pergunta legítima sobre dados
        if len(question_terms) >= 2:
            return PassResult()

        # Perguntas muito curtas (1 palavra) que não mencionam dados explicitamente são bloqueadas
        return FailResult(
            error_message="Pergunta muito vaga ou muito curta para processar."
        )


async def run_guardrail(
    question: str, schema_text: str
) -> dict[str, object]:
    """
    Executa a validação com modelo LLM.

    Args:
        question: Pergunta do usuário
        schema_text: Schema do banco de dados

    Returns:
        Dict com resultado da validação
    """
    result = await validate_with_model(question, schema_text)

    return {
        "allowed": result["allowed"],
        "score": 0,
        "signals": [],
        "reason": result["reason"],
        "guardrails_used": True,
    }
