"""Ponto de entrada da aplicacao FastAPI."""
from fastapi import FastAPI

from app.api.routes import router as api_router
from app.core.config import get_settings
from app.core.logging import init_logging


def create_app() -> FastAPI:
    """Cria e configura a aplicacao FastAPI."""
    settings = get_settings()
    init_logging(settings.LOG_LEVEL)

    app = FastAPI(
        title="microservico-lancamento-contabil",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    app.include_router(api_router)
    return app


app = create_app()
