from __future__ import annotations

from fastapi import HTTPException, status

from etran_adapter.operations.application import ApplicationOperation
from etran_adapter.operations.base import BaseOperation
from etran_adapter.operations.nsi import NsiOperation
from etran_adapter.operations.redirection import RedirectionOperation
from etran_adapter.operations.vpu import VpuOperation
from etran_adapter.operations.vuk import VukOperation
from etran_adapter.operations.waybill import WaybillOperation

_OPERATIONS: dict[str, BaseOperation] = {
    "nsi": NsiOperation(),
    "application": ApplicationOperation(),
    "waybill": WaybillOperation(),
    "redirection": RedirectionOperation(),
    "vpu": VpuOperation(),
    "vuk": VukOperation(),
}


def get_operation(name: str) -> BaseOperation:
    """Возвращает экземпляр операции по имени или 400."""
    op = _OPERATIONS.get(name)
    if op is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown operation: {name}. Available: {sorted(_OPERATIONS)}",
        )
    return op
