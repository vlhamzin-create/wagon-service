from __future__ import annotations

import enum


class MessageDirection(str, enum.Enum):
    INBOUND = "INBOUND"
    OUTBOUND = "OUTBOUND"


class ProcessingStatus(str, enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    ETRAN_ERROR = "ETRAN_ERROR"


class DocumentCategory(str, enum.Enum):
    APPLICATION = "APPLICATION"
    WAYBILL = "WAYBILL"
    ACT = "ACT"
    REFERENCE = "REFERENCE"
    FINANCE = "FINANCE"


class DocumentLifecycleStatus(str, enum.Enum):
    # Общие
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"
    CORRUPTED = "CORRUPTED"
    # Накладная-специфичные
    UNDER_VISA = "UNDER_VISA"
    LOADED = "LOADED"
    IN_TRANSIT = "IN_TRANSIT"
    ARRIVED = "ARRIVED"
    # Переадресовка
    REDIRECT_PENDING = "REDIRECT_PENDING"
    REDIRECT_APPROVED = "REDIRECT_APPROVED"
    REDIRECT_REJECTED = "REDIRECT_REJECTED"
    # ВПУ/ВУК
    VPU_AGREED = "VPU_AGREED"


class StatusTrigger(str, enum.Enum):
    USER = "USER"
    ETRAN_RESPONSE = "ETRAN_RESPONSE"
    SCHEDULER = "SCHEDULER"
    SYSTEM = "SYSTEM"
