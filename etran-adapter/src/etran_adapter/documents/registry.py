from __future__ import annotations

from typing import TYPE_CHECKING

from etran_adapter.documents.base import DocumentMapper
from etran_adapter.documents.gu12 import Gu12Mapper
from etran_adapter.documents.redirection import RedirectionMapper
from etran_adapter.documents.waybill import WaybillMapper

if TYPE_CHECKING:
    from etran_adapter.config import Settings

_DOC_TYPES = ["GU12", "REDIRECTION", "WAYBILL"]


def get_mapper(doc_type: str, settings: Settings) -> DocumentMapper:
    """Возвращает маппер по типу документа или KeyError."""
    factories: dict[str, type] = {
        "GU12": Gu12Mapper,
        "WAYBILL": WaybillMapper,
        "REDIRECTION": RedirectionMapper,
    }
    cls = factories.get(doc_type)
    if cls is None:
        raise KeyError(
            f"Unknown document type: {doc_type}. "
            f"Available: {sorted(factories)}"
        )
    return cls(settings)


def registered_types() -> list[str]:
    """Список зарегистрированных типов документов."""
    return sorted(_DOC_TYPES)
