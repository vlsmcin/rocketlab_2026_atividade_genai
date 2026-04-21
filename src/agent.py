import os
from dotenv import load_dotenv
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider
from pydantic_ai import Agent, RunContext
from pydantic import BaseModel, Field
from dataclasses import dataclass

try:
    from . import db as db_ops
except ImportError:
    import db as db_ops

@dataclass
class TextToSQLDeps:
    db_path: str
    schema: str

class SQLResult(BaseModel):
    query: str = Field(description="A consulta SQL gerada para responder à pergunta")
    result: list[tuple] = Field(description="Resultados da execução da consulta SQL, limitados a 100 linhas")
    confidence: float = Field(description="Confiança do modelo na consulta gerada, entre 0 e 1")

class AgentMultiStep:
    def __init__(self):
        self.model = self._call_model()
        self.agent = self._create_agent()

    def _call_model(self):
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        provider = GoogleProvider(api_key=api_key)
        return GoogleModel("gemini-2.5-flash-lite", provider=provider)
    
    def _create_agent(self) -> Agent:
        agent = Agent(
            self._call_model(),
            deps_type=TextToSQLDeps,
            output_type=SQLResult,
            instructions="""
            Você é um analista de dados sênior, especialista em bancos de dados SQL.
            Seu objetivo é responder perguntas em linguagem natural consultando o banco SQLite.

            Regras importantes:
            1. Antes de escrever SQL, use `get_database_schema` para entender o esquema do banco e `get_table_sample`
             para ver exemplos de dados. Isso é crucial para evitar erros de sintaxe e lógica.
            1.1. Use SOMENTE nomes de tabelas e colunas exatamente como aparecem no schema retornado pelas tools.
            1.2. Nunca invente nomes em inglês se o schema estiver em português (ex.: não use orders/order_items).
            2. Gere apenas SELECT (com ou sem CTE WITH).
            3. Sempre retorne uma consulta executável no SQLite.
            4. Seja conservador com joins e filtros para evitar resultados incorretos.
            5. Se a pergunta for ambígua, faça suposições razoáveis e indique-as.
            6. Teste sua consulta usando `run_sql_query` antes de retorná-la. Se houver erros ou resultados inesperados,
            corrija a consulta e teste novamente.
            7. Se `run_sql_query` retornar uma linha iniciando com '__SQL_ERROR__', leia o erro, ajuste a SQL e tente de novo.
            """
        )

        self._register_db_tools(agent)
        return agent

    def _register_db_tools(self, agent: Agent) -> None:
        @agent.tool
        def get_database_schema(ctx: RunContext[TextToSQLDeps]) -> str:
            """Retorna o esquema completo do banco (tabela: colunas)."""
            return db_ops.schema_as_text(ctx.deps.db_path)

        @agent.tool
        def get_table_info(ctx: RunContext[TextToSQLDeps], table_name: str) -> dict[str, object]:
            """Retorna informações detalhadas de uma tabela específica."""
            return db_ops.get_table_info(table_name=table_name, db_path=ctx.deps.db_path)

        @agent.tool
        def get_table_sample(
            ctx: RunContext[TextToSQLDeps], table_name: str, limit: int = 5
        ) -> list[tuple]:
            """Retorna linhas de exemplo de uma tabela para ajudar no schema linking."""
            safe_limit = max(1, min(limit, 20))
            return db_ops.get_sample_rows(table_name=table_name, limit=safe_limit, db_path=ctx.deps.db_path)

        @agent.tool
        def run_sql_query(ctx: RunContext[TextToSQLDeps], query: str) -> list[tuple]:
            """Executa SELECT/CTE com limite de segurança."""
            sql = db_ops.extract_sql(query)
            try:
                return db_ops.execute_query(query=sql, db_path=ctx.deps.db_path, max_rows=100)
            except Exception as exc:
                return [("__SQL_ERROR__", str(exc), sql)]


def create_text_to_sql_agent() -> Agent:
    """Factory para uso externo em fluxos que precisam do agente text-to-sql."""
    return AgentMultiStep().agent