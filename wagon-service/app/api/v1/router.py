from fastapi import APIRouter

from app.api.v1 import sync_status, sync_trigger, wagons

router = APIRouter(prefix="/api/v1")
router.include_router(wagons.router)
router.include_router(sync_status.router)
router.include_router(sync_trigger.router)
