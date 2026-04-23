from __future__ import annotations

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as api_v1_router
from app.config import settings
from app.jobs.scheduler import create_scheduler

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = create_scheduler()
    scheduler.start()
    logger.info("scheduler.started", interval_minutes=settings.sync_interval_minutes)
    yield
    scheduler.shutdown(wait=False)
    logger.info("scheduler.stopped")


app = FastAPI(
    title="Wagon Service",
    version="1.0.0",
    description="REST API для управления парком вагонов",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(api_v1_router)


@app.get("/healthz", tags=["infra"], include_in_schema=False)
async def healthz() -> dict:
    return {"status": "ok"}
