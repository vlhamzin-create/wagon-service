from __future__ import annotations

from pathlib import Path

import pytest

from app.nsi_loader.etran.xml_parsers import parse_cargos, parse_stations, parse_wagon_types

FIXTURES = Path(__file__).parent / "fixtures"


class TestParseStations:
    def _load(self) -> str:
        return (FIXTURES / "station_list_response.xml").read_text(encoding="utf-8")

    def test_parses_all_stations(self) -> None:
        records = parse_stations(self._load())
        assert len(records) == 3

    def test_station_fields(self) -> None:
        records = parse_stations(self._load())
        msk = records[0]
        assert msk.code == "060005"
        assert msk.name == "Москва-Товарная"
        assert msk.short_name == "Мск-Тов"
        assert msk.country_code == "RU"
        assert msk.country_name == "Россия"
        assert msk.railway_code == "16"
        assert msk.railway_name == "Московская"
        assert msk.is_active is True
        assert msk.etran_version == 100500

    def test_inactive_station(self) -> None:
        records = parse_stations(self._load())
        minsk = records[2]
        assert minsk.code == "200105"
        assert minsk.is_active is False

    def test_skips_records_without_code(self) -> None:
        xml = "<Response><Station><Name>NoCode</Name></Station></Response>"
        assert parse_stations(xml) == []


class TestParseWagonTypes:
    def _load(self) -> str:
        return (FIXTURES / "wagon_nsi_response.xml").read_text(encoding="utf-8")

    def test_parses_all_wagon_types(self) -> None:
        records = parse_wagon_types(self._load())
        assert len(records) == 2

    def test_wagon_type_fields(self) -> None:
        records = parse_wagon_types(self._load())
        kryt = records[0]
        assert kryt.type_code == "01"
        assert kryt.type_name == "Крытый"
        assert kryt.cargo_capacity == 68.0
        assert kryt.volume == 120.0
        assert kryt.tare_weight == 22.0
        assert kryt.axle_count == 4
        assert kryt.is_active is True
        assert kryt.etran_version == 200100

    def test_skips_records_without_type_code(self) -> None:
        xml = "<R><WagonType><TypeName>NoCode</TypeName></WagonType></R>"
        assert parse_wagon_types(xml) == []


class TestParseCargos:
    def _load(self) -> str:
        return (FIXTURES / "cargo_list_response.xml").read_text(encoding="utf-8")

    def test_parses_all_cargos(self) -> None:
        records = parse_cargos(self._load())
        assert len(records) == 3

    def test_cargo_fields(self) -> None:
        records = parse_cargos(self._load())
        wheat = records[0]
        assert wheat.etsng_code == "011001"
        assert wheat.etsng_name == "Пшеница"
        assert wheat.gng_code == "1001100000"
        assert wheat.gng_name == "Wheat"
        assert wheat.cargo_group == "Зерно"
        assert wheat.is_dangerous is False
        assert wheat.etran_version == 300100

    def test_dangerous_cargo(self) -> None:
        records = parse_cargos(self._load())
        benzin = records[1]
        assert benzin.etsng_code == "421005"
        assert benzin.is_dangerous is True

    def test_optional_gng_fields(self) -> None:
        records = parse_cargos(self._load())
        coal = records[2]
        assert coal.etsng_code == "241010"
        assert coal.gng_code is None
        assert coal.gng_name is None

    def test_skips_records_without_etsng_code(self) -> None:
        xml = "<R><Cargo><EtsngName>NoCode</EtsngName></Cargo></R>"
        assert parse_cargos(xml) == []
