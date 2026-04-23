from __future__ import annotations

from typing import Annotated

import structlog
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from etran_adapter.api.deps import get_db, verify_api_key
from etran_adapter.main import get_soap_client
from etran_adapter.operations.registry import get_operation
from etran_adapter.schemas.etran_request import EtranSyncRequest
from etran_adapter.schemas.etran_response import EtranSyncResponse

logger = structlog.get_logger(__name__)

router = APIRouter(
    prefix="/v1/etran/sync",
    tags=["sync"],
    dependencies=[Depends(verify_api_key)],
)


@router.post("", response_model=EtranSyncResponse)
async def sync_call(
    payload: EtranSyncRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> EtranSyncResponse:
    """Синхронный вызов ЭТРАН (НСИ, статусы, данные документа).

    wagon-service ждёт ответа до таймаута (30 сек).
    """
    client = get_soap_client()
    operation = get_operation(payload.operation)
    result_xml = operation.execute_sync(client=client, params=payload.params)
    return EtranSyncResponse(
        success=True,
        operation=payload.operation,
        data=result_xml,
    )
