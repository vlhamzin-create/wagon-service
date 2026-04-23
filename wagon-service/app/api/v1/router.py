from fastapi import APIRouter

from app.api.v1 import assign_route, dicts, sync_status, sync_trigger, wagons

router = APIRouter(prefix="/api/v1")
router.include_router(wagons.router)
router.include_router(assign_route.router)
router.include_router(dicts.router)
router.include_router(sync_status.router)
router.include_router(sync_trigger.router)
