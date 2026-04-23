from datetime import datetime

from pydantic import BaseModel


class SourceStatus(BaseModel):
    source: str
    last_success_at: datetime | None
    last_status: str
    last_error: str | None


class SyncStatusResponse(BaseModel):
    sources: list[SourceStatus]
