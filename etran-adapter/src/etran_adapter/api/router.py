from __future__ import annotations

from fastapi import APIRouter

from etran_adapter.api.v1.sync import router as sync_router
from etran_adapter.api.v1.async_ import router as async_router

router = APIRouter(prefix="/api")
router.include_router(sync_router)
router.include_router(async_router)
