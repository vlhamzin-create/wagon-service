from __future__ import annotations

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dashboard.queries import fetch_dashboard_data


class DashboardService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_dashboard_data(self, wagon_type: Optional[str]) -> dict:
        return await fetch_dashboard_data(self._session, wagon_type)
