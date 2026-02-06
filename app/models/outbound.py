"""Modelo de saida da API."""
from typing import Any

from pydantic import BaseModel


class SapProxyResponse(BaseModel):
    """Resposta padronizada contendo status e payload do SAP."""

    sap_status_code: int
    sap_payload: Any
