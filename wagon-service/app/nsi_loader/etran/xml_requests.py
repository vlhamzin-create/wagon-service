from __future__ import annotations

from typing import Optional


def build_station_list_params(chg_date_time: Optional[str] = None) -> dict[str, str]:
    """Параметры запроса справочника станций (раздел 5.5.3)."""
    params: dict[str, str] = {"NsiType": "StationList"}
    if chg_date_time:
        params["ChgDateTime"] = chg_date_time
    return params


def build_wagon_nsi_params(chg_date_time: Optional[str] = None) -> dict[str, str]:
    """Параметры запроса НСИ вагонов (раздел 5.5.8)."""
    params: dict[str, str] = {"NsiType": "WagonNSI"}
    if chg_date_time:
        params["ChgDateTime"] = chg_date_time
    return params


def build_cargo_list_params(chg_date_time: Optional[str] = None) -> dict[str, str]:
    """Параметры запроса справочника грузов."""
    params: dict[str, str] = {"NsiType": "CargoList"}
    if chg_date_time:
        params["ChgDateTime"] = chg_date_time
    return params
