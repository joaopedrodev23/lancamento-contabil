"""Servico de comunicacao com a API do SAP."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

from app.core.config import Settings
from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class SapResponse:
    """Representa a resposta do SAP."""

    status_code: int
    payload: Any


class SapCommunicationError(Exception):
    """Erro de comunicacao com a API SAP."""

    def __init__(self, message: str, is_timeout: bool = False) -> None:
        super().__init__(message)
        self.is_timeout = is_timeout


class SapService:
    """Responsavel por chamar a API do SAP usando token OAuth2."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def post_journal_entry(self, token: str, payload: dict) -> SapResponse:
        """Envia o payload para a API SAP e retorna status e conteudo."""
        if self._settings.USE_MOCK_SAP:
            logger.info("SAP mock ativado. Retornando resposta simulada.")
            return SapResponse(
                status_code=201,
                payload={
                    "mock": True,
                    "mensagem": "Resposta simulada do SAP.",
                    "echo": payload,
                },
            )

        if not self._settings.SAP_API_URL:
            raise SapCommunicationError("Variavel de ambiente ausente: SAP_API_URL")

        headers = {"Authorization": f"Bearer {token}"}
        timeout = httpx.Timeout(self._settings.HTTP_TIMEOUT_SECONDS)

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    self._settings.SAP_API_URL,
                    json=payload,
                    headers=headers,
                )
        except httpx.TimeoutException as exc:
            raise SapCommunicationError(
                "Timeout ao chamar a API SAP.",
                is_timeout=True,
            ) from exc
        except httpx.RequestError as exc:
            raise SapCommunicationError("Erro de rede ao chamar a API SAP.") from exc

        try:
            data = response.json()
        except ValueError:
            data = {"raw": response.text}

        return SapResponse(status_code=response.status_code, payload=data)
