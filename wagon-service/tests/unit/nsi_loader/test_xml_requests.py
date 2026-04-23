from __future__ import annotations

from app.nsi_loader.etran.xml_requests import (
    build_cargo_list_params,
    build_station_list_params,
    build_wagon_nsi_params,
)


class TestBuildStationListParams:
    def test_full_load(self) -> None:
        params = build_station_list_params()
        assert params == {"NsiType": "StationList"}

    def test_incremental_load(self) -> None:
        params = build_station_list_params(chg_date_time="2026-04-20T00:00:00")
        assert params == {
            "NsiType": "StationList",
            "ChgDateTime": "2026-04-20T00:00:00",
        }


class TestBuildWagonNsiParams:
    def test_full_load(self) -> None:
        params = build_wagon_nsi_params()
        assert params == {"NsiType": "WagonNSI"}

    def test_incremental_load(self) -> None:
        params = build_wagon_nsi_params(chg_date_time="2026-04-20T00:00:00")
        assert params["ChgDateTime"] == "2026-04-20T00:00:00"


class TestBuildCargoListParams:
    def test_full_load(self) -> None:
        params = build_cargo_list_params()
        assert params == {"NsiType": "CargoList"}

    def test_incremental_load(self) -> None:
        params = build_cargo_list_params(chg_date_time="2026-04-20T00:00:00")
        assert params["ChgDateTime"] == "2026-04-20T00:00:00"
