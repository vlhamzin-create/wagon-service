from __future__ import annotations

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import router as api_v1_router
from app.auth.exceptions import AuthError, ForbiddenError
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
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(api_v1_router)


@app.exception_handler(AuthError)
async def auth_error_handler(request: Request, exc: AuthError) -> JSONResponse:
    return JSONResponse(
        status_code=401,
        content={"error_code": exc.error_code, "message": exc.message},
        headers={"WWW-Authenticate": "Bearer"},
    )


@app.exception_handler(ForbiddenError)
async def forbidden_error_handler(request: Request, exc: ForbiddenError) -> JSONResponse:
    return JSONResponse(
        status_code=403,
        content={"error_code": exc.error_code, "message": exc.message},
    )


@app.get("/healthz", tags=["infra"], include_in_schema=False)
async def healthz() -> dict:
    return {"status": "ok"}
