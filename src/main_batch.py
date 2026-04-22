import asyncio

from .app_core import Colors, format_result, run_text_to_sql


async def run_batch_questions() -> None:
    """Executa as 10 perguntas principais em lote."""
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
    asyncio.run(run_batch_questions())
