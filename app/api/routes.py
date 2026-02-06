"""Rotas da API REST."""
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.logging import get_logger
from app.models.inbound import JournalEntryRequest
from app.models.outbound import SapProxyResponse
from app.services.auth_service import AuthError, AuthService
from app.services.sap_service import SapCommunicationError, SapService

router = APIRouter()
settings = get_settings()
logger = get_logger(__name__)
auth_service = AuthService(settings)
sap_service = SapService(settings)


@router.post("/journal-entry", response_model=SapProxyResponse, tags=["journal-entry"])
async def create_journal_entry(payload: JournalEntryRequest):
    """Recebe o payload do ServiceNow e encaminha para o SAP via BTP."""
    try:
        token = await auth_service.get_token()
    except AuthError as exc:
        logger.error("Erro ao obter token OAuth2: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "mensagem": "Falha ao obter token OAuth2 no SAP BTP.",
                "status_upstream": exc.status_code,
            },
        ) from exc

    try:
        sap_response = await sap_service.post_journal_entry(
            token=token,
            payload=payload.model_dump(exclude_none=True),
        )
    except SapCommunicationError as exc:
        logger.error("Falha de comunicacao com o SAP: %s", exc)
        raise HTTPException(
            status_code=(
                status.HTTP_504_GATEWAY_TIMEOUT
                if exc.is_timeout
                else status.HTTP_502_BAD_GATEWAY
            ),
            detail={
                "mensagem": "Falha de comunicacao com o SAP.",
                "detalhe": str(exc),
            },
        ) from exc

    response_body = SapProxyResponse(
        sap_status_code=sap_response.status_code,
        sap_payload=sap_response.payload,
    ).model_dump()

    return JSONResponse(status_code=sap_response.status_code, content=response_body)
