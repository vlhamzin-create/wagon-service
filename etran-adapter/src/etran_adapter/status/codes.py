from __future__ import annotations

import enum


class EtranDocumentType(str, enum.Enum):
    GU12 = "GU12"
    WAYBILL = "WAYBILL"
    REDIRECTION = "REDIRECTION"


class EtranDocumentStatus(str, enum.Enum):
    # Общие
    DRAFT = "DRAFT"
    SENDING = "SENDING"
    SENT = "SENT"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    ERROR = "ERROR"

    # Специфичные для ГУ-12
    GU12_UNDER_REVIEW = "GU12_UNDER_REVIEW"
    GU12_APPROVED = "GU12_APPROVED"
    GU12_DENIED = "GU12_DENIED"

    # Специфичные для накладной
    WAYBILL_VISA_PENDING = "WAYBILL_VISA_PENDING"
    WAYBILL_VISA_GRANTED = "WAYBILL_VISA_GRANTED"
    WAYBILL_VISA_DENIED = "WAYBILL_VISA_DENIED"
    WAYBILL_LOADED = "WAYBILL_LOADED"
    WAYBILL_DEPARTED = "WAYBILL_DEPARTED"

    # Специфичные для переадресовки
    REDIR_PENDING = "REDIR_PENDING"
    REDIR_APPROVED = "REDIR_APPROVED"
    REDIR_DENIED = "REDIR_DENIED"


ETRAN_CODE_TO_STATUS: dict[str, EtranDocumentStatus] = {
    "1": EtranDocumentStatus.ACCEPTED,
    "2": EtranDocumentStatus.REJECTED,
    "3": EtranDocumentStatus.GU12_UNDER_REVIEW,
    "4": EtranDocumentStatus.GU12_APPROVED,
    "5": EtranDocumentStatus.GU12_DENIED,
    "10": EtranDocumentStatus.WAYBILL_VISA_PENDING,
    "11": EtranDocumentStatus.WAYBILL_VISA_GRANTED,
    "12": EtranDocumentStatus.WAYBILL_VISA_DENIED,
    "20": EtranDocumentStatus.REDIR_PENDING,
    "21": EtranDocumentStatus.REDIR_APPROVED,
    "22": EtranDocumentStatus.REDIR_DENIED,
}


def resolve_status(etran_code: str) -> EtranDocumentStatus:
    """Маппинг кода ответа ЭТРАН в наш статус."""
    return ETRAN_CODE_TO_STATUS.get(etran_code, EtranDocumentStatus.ACCEPTED)
