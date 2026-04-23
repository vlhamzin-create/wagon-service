from __future__ import annotations

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from etran_adapter.api.router import router as api_router
from etran_adapter.config import settings
from etran_adapter.soap.client import EtranSoapClient

logger = structlog.get_logger(__name__)

_soap_client: EtranSoapClient | None = None


def get_soap_client() -> EtranSoapClient:
    assert _soap_client is not None, "SOAP client not initialised"
    return _soap_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _soap_client  # noqa: PLW0603
    _soap_client = EtranSoapClient(settings)
    logger.info("etran_adapter.started")
    yield
    _soap_client = None
    logger.info("etran_adapter.stopped")


app = FastAPI(
    title="ЭТРАН Adapter",
    version="0.1.0",
    description="Интеграционный адаптер для АС ЭТРАН НП",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(api_router)


@app.get("/healthz", tags=["infra"], include_in_schema=False)
async def healthz() -> dict:
    return {"status": "ok"}
