import asyncio
from typing import Any

from .agent import TextToSQLDeps
from .chase import run_chase_self_consistency
from .db import DEFAULT_DB_PATH


class Colors:
    """ANSI color codes for terminal output."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    CYAN = "\033[36m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"


def _format_failed_candidates(failed_candidates: list[dict[str, Any]]) -> list[str]:
    lines: list[str] = []
    if not failed_candidates:
        return lines

    lines.append(f"{Colors.BOLD}{Colors.RED}🧪 DEBUG DE FALHAS POR CANDIDATO:{Colors.RESET}")
    for idx, failed in enumerate(failed_candidates, start=1):
        lines.append(
            f"  {idx}. temp={failed.get('temperature')} stage={failed.get('stage', 'unknown')}"
        )
        lines.append(f"     erro: {failed.get('error', 'sem mensagem')}")
        if failed.get("query"):
            lines.append(f"     sql: {failed['query']}")

    return lines


def format_result(result: dict[str, Any]) -> str:
    """Formata o resultado de forma visual e clara."""
    if result["status"] != "ok":
        output = [
            f"{Colors.RED}❌ Erro na geração de SQL{Colors.RESET}",
            f"  Mensagem: {result['message']}",
            f"  Falhas: {len(result['failed_candidates'])} candidatos falharam",
        ]
        output.extend(_format_failed_candidates(result.get("failed_candidates", [])))
        return "\n".join(output)

    agreement = result["agreement"]
    query = result["query"]
    confidence = result["confidence"]
    rows = result["result"]

    agreement_pct = (agreement["votes"] / agreement["total_valid"]) * 100 if agreement["total_valid"] > 0 else 0
    agreement_bar = "█" * int(agreement_pct / 10) + "░" * (10 - int(agreement_pct / 10))

    output = []
    output.append(f"{Colors.GREEN}✓ SQL Gerada com Sucesso{Colors.RESET}")
    output.append(f"{Colors.BOLD}{'─' * 100}{Colors.RESET}")

    output.append(f"\n{Colors.BOLD}{Colors.CYAN}📋 CONSULTA SQL:{Colors.RESET}")
    output.append(f"{Colors.BLUE}{query}{Colors.RESET}\n")

    output.append(f"{Colors.BOLD}{Colors.CYAN}📊 MÉTRICAS:{Colors.RESET}")
    output.append(f"  Confiança:    {Colors.YELLOW}{confidence:.2%}{Colors.RESET}")
    output.append(f"  Consenso:     [{agreement_bar}] {Colors.YELLOW}{agreement_pct:.0f}%{Colors.RESET} ({agreement['votes']}/{agreement['total_valid']} candidatos)")
    output.append(f"  Temperaturas: {Colors.DIM}{agreement['temperatures']}{Colors.RESET}")

    failed_candidates = result.get("failed_candidates", [])
    if failed_candidates:
        output.append(f"  Tentativas com falha: {Colors.YELLOW}{len(failed_candidates)}{Colors.RESET}")

    output.append(f"\n{Colors.BOLD}{Colors.CYAN}📈 RESULTADOS ({len(rows)} linhas):{Colors.RESET}")

    if not rows:
        output.append(f"{Colors.YELLOW}  (Nenhuma linha retornada){Colors.RESET}")
    else:
        max_rows_display = 10
        for i, row in enumerate(rows[:max_rows_display], start=1):
            output.append(f"  {i:>2}. {row}")

        if len(rows) > max_rows_display:
            output.append(f"  {Colors.DIM}... e mais {len(rows) - max_rows_display} linhas{Colors.RESET}")

    output.extend(["", *_format_failed_candidates(failed_candidates)])

    output.append(f"\n{Colors.BOLD}{'─' * 100}{Colors.RESET}")

    return "\n".join(output)


async def run_text_to_sql(question: str) -> dict[str, Any]:
    """Executa o agente CHASE e retorna o resultado estruturado."""
    deps = TextToSQLDeps(db_path=DEFAULT_DB_PATH, schema="")
    result = await run_chase_self_consistency(question=question, deps=deps, n_candidates=4)
    return result


async def main():
    """Executa as perguntas e exibe resultados formatados."""
    questions = [
        "Quais são os top 10 produtos mais vendidos?",
        "Qual a receita total por categoria de produto?",
        "Qual a quantidade de pedidos por status?",
        "Qual a '%' de pedidos entregues no prazo por estado dos consumidores?",
        "Qual a média de avaliação geral dos pedidos?",
        "Qual o top 10 de avaliação por vendedor?",
        "Quais os estados com maior volume de pedidos e maior ticket médio?",
        "Quais os estados com maior atraso?",
        "Quais os produtos mais vendidos por estado?",
        "Quais as categorias com maior taxa de avaliação negativa?",
    ]

    print(f"\n{Colors.BOLD}{Colors.MAGENTA}🚀 INICIANDO TEXT-TO-SQL COM SELF-CONSISTENCY (CHASE){Colors.RESET}\n")

    for idx, user_question in enumerate(questions, start=1):
        print(f"{Colors.BOLD}{Colors.MAGENTA}Pergunta {idx}/{len(questions)}{Colors.RESET}")
        print(f"{Colors.CYAN}❓ {user_question}{Colors.RESET}\n")

        result = await run_text_to_sql(user_question)
        output = format_result(result)
        print(output)
        print()


if __name__ == "__main__":
    asyncio.run(main())
