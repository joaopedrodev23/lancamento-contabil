"""Cliente HTTP para envio de attachment no SAP via Connectivity."""
from __future__ import annotations

from typing import Any

import httpx

from app.core.config import get_settings


class SapAttachmentClientError(Exception):
    """Erro de comunicacao com endpoint de attachment SAP."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


async def send_attachment(payload: dict, token: str) -> dict[str, Any]:
    """Envia attachment para o SAP e retorna JSON da resposta."""
    settings = get_settings()

    if not settings.SAP_ATTACHMENT_URL:
        raise SapAttachmentClientError(
            "Variavel de ambiente ausente: SAP_ATTACHMENT_URL"
        )

    timeout = httpx.Timeout(settings.HTTP_TIMEOUT_SECONDS)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                settings.SAP_ATTACHMENT_URL,
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise SapAttachmentClientError(
            message=f"Erro HTTP no attachment SAP: {exc.response.status_code}",
            status_code=exc.response.status_code,
        ) from exc
    except httpx.RequestError as exc:
        raise SapAttachmentClientError("Erro de rede ao enviar attachment SAP.") from exc

    try:
        return response.json()
    except ValueError as exc:
        raise SapAttachmentClientError(
            message="Resposta de attachment SAP nao esta em JSON.",
            status_code=response.status_code,
        ) from exc
