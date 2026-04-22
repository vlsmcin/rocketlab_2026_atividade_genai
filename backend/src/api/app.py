from fastapi import FastAPI

from .routes import router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Text-to-SQL Backend",
        description="Backend FastAPI para executar o pipeline CHASE de Text-to-SQL.",
        version="1.0.0",
    )
    app.include_router(router)
    return app


app = create_app()