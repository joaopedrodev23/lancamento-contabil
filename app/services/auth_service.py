"""Servico de autenticacao OAuth2 via SAP BTP."""
from __future__ import annotations

import httpx

from app.core.config import Settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class AuthError(Exception):
    """Erro ao obter token OAuth2."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class AuthService:
    """Responsavel por obter token OAuth2 usando client_credentials."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def get_token(self) -> str:
        """Solicita um token OAuth2 no SAP BTP e retorna o access_token."""
        if self._settings.USE_MOCK_AUTH:
            logger.info("Autenticacao mock ativada. Usando token ficticio.")
            return "mock-token"

        missing = [
            name
            for name, value in {
                "SAP_OAUTH_URL": self._settings.SAP_OAUTH_URL,
                "SAP_CLIENT_ID": self._settings.SAP_CLIENT_ID,
                "SAP_CLIENT_SECRET": self._settings.SAP_CLIENT_SECRET,
            }.items()
            if not value
        ]
        if missing:
            raise AuthError("Variaveis de ambiente ausentes: " + ", ".join(missing))

        data = {
            "grant_type": "client_credentials",
            "client_id": self._settings.SAP_CLIENT_ID,
            "client_secret": self._settings.SAP_CLIENT_SECRET,
        }

        timeout = httpx.Timeout(self._settings.HTTP_TIMEOUT_SECONDS)

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    self._settings.SAP_OAUTH_URL,
                    data=data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )
        except httpx.TimeoutException as exc:
            raise AuthError("Timeout ao obter token OAuth2.") from exc
        except httpx.RequestError as exc:
            raise AuthError("Erro de rede ao obter token OAuth2.") from exc

        if response.status_code != 200:
            raise AuthError(
                message=f"Resposta invalida do OAuth2: {response.status_code}",
                status_code=response.status_code,
            )

        try:
            payload = response.json()
        except ValueError as exc:
            raise AuthError(
                "Resposta do OAuth2 nao e JSON.",
                status_code=response.status_code,
            ) from exc

        token = payload.get("access_token")

        if not token:
            raise AuthError(
                "Resposta do OAuth2 sem access_token.",
                status_code=response.status_code,
            )

        return token
