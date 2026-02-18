"""Modelo de saida da API."""
from typing import Any, Literal

from pydantic import BaseModel


class AttachmentResult(BaseModel):
    """Resultado do envio de attachment."""

    status: Literal[
        "disabled",
        "not_attempted",
        "skipped_no_pdf",
        "sent",
        "failed",
        "mock",
    ]
    status_code: int | None = None
    error: str | None = None
    response: Any | None = None


class SapProxyResponse(BaseModel):
    """Resposta padronizada contendo status, payload do SAP e attachment."""

    sap_status_code: int
    sap_payload: Any
    attachment: AttachmentResult
