from fastapi import APIRouter

from app.api.v1 import sync_status, wagons

router = APIRouter(prefix="/api/v1")
router.include_router(wagons.router)
router.include_router(sync_status.router)
