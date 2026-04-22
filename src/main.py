import asyncio
from .app_core import Colors, format_result, run_text_to_sql
from .main_batch import run_batch_questions


async def main() -> None:
    """Inicia um chat interativo no terminal para perguntas text-to-sql."""
    print(f"\n{Colors.BOLD}{Colors.MAGENTA}💬 CHAT TEXT-TO-SQL (CHASE + GUARDRAILS){Colors.RESET}")
    print(f"{Colors.DIM}Digite sua pergunta sobre o banco de dados.{Colors.RESET}")
    print(f"{Colors.DIM}Comandos: /sair, /exit, /quit, /lote{Colors.RESET}\n")

    while True:
        try:
            user_question = input(f"{Colors.CYAN}Você > {Colors.RESET}").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{Colors.YELLOW}Encerrando chat...{Colors.RESET}")
            break

        if not user_question:
            continue

        lowered = user_question.lower()
        if lowered in {"/sair", "/exit", "/quit"}:
            print(f"{Colors.YELLOW}Até mais!{Colors.RESET}")
            break

        if lowered == "/lote":
            await run_batch_questions()
            continue

        print(f"\n{Colors.BOLD}{Colors.MAGENTA}Pergunta:{Colors.RESET} {user_question}\n")
        result = await run_text_to_sql(user_question)
        print(format_result(result))
        print()


if __name__ == "__main__":
    asyncio.run(main())
