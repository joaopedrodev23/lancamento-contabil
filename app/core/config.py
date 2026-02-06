"""Configuracoes da aplicacao via variaveis de ambiente."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Carrega variaveis de ambiente necessarias para a aplicacao."""

    SAP_OAUTH_URL: str | None = None
    SAP_CLIENT_ID: str | None = None
    SAP_CLIENT_SECRET: str | None = None
    SAP_API_URL: str | None = None
    HTTP_TIMEOUT_SECONDS: float = 15.0
    ENVIRONMENT: str = "dev"
    LOG_LEVEL: str = "INFO"
    USE_MOCK_AUTH: bool = False
    USE_MOCK_SAP: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Retorna instancia singleton das configuracoes."""
    return Settings()
