"""
Módulo de guard rails para validação de perguntas sobre banco de dados.

Utiliza um modelo LLM (Gemini) para validar semanticamente se uma pergunta
é relevante ao contexto do banco de dados, funcionando em qualquer idioma.
"""

import re

from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel



class RelevanceCheckResult(BaseModel):
    is_relevant: bool
    reasoning: str


def _normalized_text(text: str) -> str:
    return text.casefold()


def _schema_terms(schema_text: str) -> set[str]:
    normalized_schema = _normalized_text(schema_text)
    return {
        token
        for token in re.findall(r"[a-z0-9_]+", normalized_schema)
        if token
    }


def _question_terms(question: str) -> set[str]:
    normalized_question = _normalized_text(question)
    return {
        token
        for token in re.findall(r"[a-z0-9_]+", normalized_question)
        if token
    }


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
        normalized_question = _normalized_text(question)
        question_terms = ", ".join(sorted(_question_terms(question)))
        schema_terms = ", ".join(sorted(_schema_terms(schema_text)))

        agent = Agent(
            model,
            result_type=RelevanceCheckResult,
        )

        prompt = f"""Você é um validador que verifica se uma pergunta é relevante para consultas em um banco de dados.

        SCHEMA DO BANCO DE DADOS:
        {schema_text}

        PERGUNTA DO USUÁRIO:
        {question}

        TERMOS EXTRAÍDOS DA PERGUNTA:
        {question_terms}

        Determine se a pergunta é relevante para fazer consultas ou análises neste banco de dados.
        Regras:
        - Perguntas sobre dados, tabelas, colunas, análises, relatórios sobre os dados: RELEVANTE
        - Perguntas abstratas sobre os dados ou sobre a estrutura do banco: RELEVANTE
        - Perguntas sobre pessoas, políticos, celebridades, religião, salário, idade, cargo ou fatos externos a menos que estejam explicitamente presentes no schema: NÃO RELEVANTE
        - Perguntas completamente off-topic (clima, piadas, filmes, política, etc.): NÃO RELEVANTE
        - Considere equivalências semânticas amplas: siglas, abreviações, plurais, variações de idioma, capitalização e acentos devem ser tratados como a mesma intenção quando o assunto continuar ligado ao schema.
        - Não rejeite uma pergunta só porque ela contém uma entidade nomeada, capitalização incomum ou uma abreviação.

        Exemplos de NÃO RELEVANTE:
        - "Qual o salário médio de Trump?"
        - "Qual a religião de Lula?"
        - "What is Trump's salary average?"
        - "What is Lula's religion?"

        Exemplos de RELEVANTE:
        - "Liste todas as tabelas"
        - "Resuma as tabelas"
        - "Quais colunas existem no schema?"
        - "What tables are available in the database?"

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
