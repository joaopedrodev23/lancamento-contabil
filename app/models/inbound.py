"""Modelos de entrada da API."""
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class JournalEntryItem(BaseModel):
    """Item de lancamento contabil."""

    ReferenceDocumentItem: Optional[str] = None
    GLAccount: Optional[str] = None
    AmountInTransactionCurrency: Optional[str] = None
    DebitCreditCode: Optional[float] = None
    DocumentItemText: Optional[str] = None
    AssignmentReference: Optional[str] = None
    TradingPartner: Optional[str] = None
    ValueDate: Optional[str] = None
    ProfitCenter: Optional[str] = None
    CostCenter: Optional[str] = None

    model_config = ConfigDict(extra="allow")


class JournalEntryRequest(BaseModel):
    """Modelo de entrada para criacao de Journal Entry."""

    OriginalReferenceDocumentType: Optional[str] = None
    OriginalReferenceDocument: Optional[str] = None
    OriginalReferenceDocumentLogicalSystem: Optional[str] = None
    BusinessTransactionType: Optional[str] = None
    AccountingDocumentType: Optional[str] = None
    DocumentReferenceID: Optional[str] = None
    DocumentHeaderText: Optional[str] = None
    CreatedByUser: Optional[str] = None
    CompanyCode: Optional[str] = None
    DocumentDate: Optional[str] = None
    PostingDate: Optional[str] = None
    itens: List[JournalEntryItem] = Field(default_factory=list)

    model_config = ConfigDict(extra="allow")
