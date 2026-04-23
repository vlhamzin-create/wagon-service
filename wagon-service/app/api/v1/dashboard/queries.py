from __future__ import annotations

from typing import Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

# Базовый CTE с категоризацией каждого вагона (один проход).
# destination_station_code IS NULL = нет назначения.
# distance_to_destination > 0 = в пути.
# status = 'груженый' — прокси загруженности (колонка weight отсутствует).
_CATEGORIZE_CTE = """
WITH categorized AS (
    SELECT
        destination_railway,
        wagon_type,
        owner_type,
        requires_assignment,
        status,
        CASE
            WHEN destination_station_code IS NULL AND COALESCE(distance_to_destination, 0) = 0
                THEN 'without_assignment'
            WHEN destination_station_code IS NULL AND COALESCE(distance_to_destination, 0) > 0
                THEN 'without_assignment_in_transit'
            WHEN destination_station_code IS NOT NULL AND COALESCE(distance_to_destination, 0) = 0 AND status != 'груженый'
                THEN 'under_loading'
            WHEN destination_station_code IS NOT NULL AND COALESCE(distance_to_destination, 0) > 0 AND status != 'груженый'
                THEN 'going_to_loading'
            WHEN destination_station_code IS NOT NULL AND COALESCE(distance_to_destination, 0) = 0 AND status = 'груженый'
                THEN 'under_unloading'
            WHEN destination_station_code IS NOT NULL AND COALESCE(distance_to_destination, 0) > 0 AND status = 'груженый'
                THEN 'going_to_unloading'
            ELSE 'unknown'
        END AS category
    FROM wagon_service.wagon
    WHERE deleted_at IS NULL {filter_clause}
)
"""

_PIVOT_COLUMNS = """
    COUNT(CASE WHEN category = 'under_loading'                 THEN 1 END) AS under_loading,
    COUNT(CASE WHEN category = 'going_to_loading'              THEN 1 END) AS going_to_loading,
    COUNT(CASE WHEN category = 'under_unloading'               THEN 1 END) AS under_unloading,
    COUNT(CASE WHEN category = 'going_to_unloading'            THEN 1 END) AS going_to_unloading,
    COUNT(CASE WHEN category = 'without_assignment'            THEN 1 END) AS without_assignment,
    COUNT(CASE WHEN category = 'without_assignment_in_transit' THEN 1 END) AS without_assignment_in_transit
"""

_QUERY_BY_DESTINATION_RAILWAY = (
    _CATEGORIZE_CTE
    + "SELECT destination_railway, "
    + _PIVOT_COLUMNS
    + " FROM categorized GROUP BY destination_railway ORDER BY destination_railway"
)

_QUERY_BY_WAGON_TYPE = (
    _CATEGORIZE_CTE
    + "SELECT wagon_type, "
    + _PIVOT_COLUMNS
    + " FROM categorized GROUP BY wagon_type ORDER BY wagon_type"
)

_QUERY_BY_OWNER_TYPE = (
    _CATEGORIZE_CTE
    + "SELECT owner_type, "
    + _PIVOT_COLUMNS
    + " FROM categorized GROUP BY owner_type ORDER BY owner_type"
)

_QUERY_TOTALS = """
SELECT
    COUNT(CASE WHEN status = 'active' THEN 1 END) AS in_work,
    COUNT(CASE WHEN requires_assignment = TRUE THEN 1 END) AS requires_assignment
FROM wagon_service.wagon
WHERE deleted_at IS NULL {filter_clause}
"""


def _build_filter(wagon_type: Optional[str]) -> tuple[str, dict]:
    if wagon_type:
        return "AND wagon_type = :wagon_type", {"wagon_type": wagon_type}
    return "", {}


async def fetch_dashboard_data(
    session: AsyncSession,
    wagon_type: Optional[str],
) -> dict:
    filter_clause, params = _build_filter(wagon_type)

    rows_railway = (
        await session.execute(
            text(_QUERY_BY_DESTINATION_RAILWAY.format(filter_clause=filter_clause)),
            params,
        )
    ).mappings().all()

    rows_wagon_type = (
        await session.execute(
            text(_QUERY_BY_WAGON_TYPE.format(filter_clause=filter_clause)),
            params,
        )
    ).mappings().all()

    rows_owner_type = (
        await session.execute(
            text(_QUERY_BY_OWNER_TYPE.format(filter_clause=filter_clause)),
            params,
        )
    ).mappings().all()

    totals_row = (
        await session.execute(
            text(_QUERY_TOTALS.format(filter_clause=filter_clause)),
            params,
        )
    ).mappings().one()

    return {
        "destination_railways": [dict(r) for r in rows_railway],
        "summary_by_wagon_type": [dict(r) for r in rows_wagon_type],
        "summary_by_owner_type": [dict(r) for r in rows_owner_type],
        "totals": dict(totals_row),
    }
