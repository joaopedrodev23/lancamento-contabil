"""Service de attachment para Journal Entry."""
from __future__ import annotations

import base64
from typing import Any

from app.core.config import Settings
from app.core.logging import get_logger
from app.integrations.sap_attachment_client import send_attachment

logger = get_logger(__name__)


class AttachmentServiceError(Exception):
    """Erro de regra de negocio para envio de attachment."""


class AttachmentService:
    """Responsavel por construir e enviar attachment vinculado ao Journal Entry."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def send_for_journal_entry(
        self,
        journal_payload: dict[str, Any],
        sap_payload: Any,
        token: str,
    ) -> dict[str, Any] | None:
        """Envia attachment quando habilitado e houver conteudo PDF disponivel."""
        if not self._settings.ENABLE_ATTACHMENT:
            logger.info(
                "attachment.disabled",
                extra={"enable_attachment": False},
            )
            return None

        if self._settings.USE_MOCK_SAP:
            logger.info("attachment.mock.enabled")
            return {
                "mock": True,
                "mensagem": "Resposta simulada do attachment.",
            }

        document_number = self._extract_document_number(sap_payload, journal_payload)
        if not document_number:
            raise AttachmentServiceError(
                "Nao foi possivel identificar document_number para LinkedSAPObjectKey."
            )

        pdf_base64 = self._extract_pdf_base64(journal_payload)
        if not pdf_base64:
            logger.info("attachment.skipped.no_pdf_content")
            return None

        attachment_payload = {
            "BusinessObjectTypeName": "BKPF",
            "LinkedSAPObjectKey": document_number,
            "Content-Type": "application/pdf",
            "Slug": "Comprovante.pdf",
            "FileName": "Comprovante",
            "MimeType": "application/pdf",
            "Content": pdf_base64,
        }

        logger.info(
            "attachment.send.start",
            extra={"linked_sap_object_key": document_number},
        )
        return await send_attachment(payload=attachment_payload, token=token)

    @staticmethod
    def _extract_document_number(
        sap_payload: Any,
        journal_payload: dict[str, Any],
    ) -> str | None:
        if isinstance(sap_payload, dict):
            for key in (
                "document_number",
                "DocumentNumber",
                "AccountingDocument",
                "journalEntryId",
                "JournalEntry",
            ):
                value = sap_payload.get(key)
                if value:
                    return str(value)

        reference_id = journal_payload.get("DocumentReferenceID")
        if reference_id:
            return str(reference_id)
        return None

    @staticmethod
    def _extract_pdf_base64(journal_payload: dict[str, Any]) -> str | None:
        raw_content = (
            journal_payload.get("AttachmentContent")
            or journal_payload.get("AttachmentPdf")
            or journal_payload.get("pdf_content")
            or journal_payload.get("pdf")
        )
        if raw_content is None:
            return None

        if isinstance(raw_content, bytes):
            return base64.b64encode(raw_content).decode("utf-8")

        if isinstance(raw_content, str):
            try:
                base64.b64decode(raw_content, validate=True)
                return raw_content
            except Exception:
                return base64.b64encode(raw_content.encode("utf-8")).decode("utf-8")

        raise AttachmentServiceError("Campo de attachment PDF em formato invalido.")
