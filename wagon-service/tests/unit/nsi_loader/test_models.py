from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.nsi_loader.models.cargo import CargoRecord
from app.nsi_loader.models.station import StationRecord
from app.nsi_loader.models.wagon_type import WagonTypeRecord


class TestStationRecord:
    def test_required_fields(self) -> None:
        r = StationRecord(code="060005", name="Москва-Товарная")
        assert r.code == "060005"
        assert r.is_active is True

    def test_all_fields(self) -> None:
        r = StationRecord(
            code="060005",
            name="Москва-Товарная",
            short_name="Мск-Тов",
            country_code="RU",
            country_name="Россия",
            railway_code="16",
            railway_name="Московская",
            is_active=False,
            etran_version=123,
        )
        assert r.railway_code == "16"
        assert r.etran_version == 123
        assert r.is_active is False

    def test_missing_required(self) -> None:
        with pytest.raises(ValidationError):
            StationRecord(code="060005")  # name is required


class TestWagonTypeRecord:
    def test_required_fields(self) -> None:
        r = WagonTypeRecord(type_code="01", type_name="Крытый")
        assert r.cargo_capacity is None
        assert r.axle_count is None

    def test_numeric_fields(self) -> None:
        r = WagonTypeRecord(
            type_code="01",
            type_name="Крытый",
            cargo_capacity=68.0,
            volume=120.0,
            tare_weight=22.0,
            axle_count=4,
        )
        assert r.cargo_capacity == 68.0
        assert r.axle_count == 4


class TestCargoRecord:
    def test_required_fields(self) -> None:
        r = CargoRecord(etsng_code="011001", etsng_name="Пшеница")
        assert r.is_dangerous is False
        assert r.gng_code is None

    def test_dangerous_flag(self) -> None:
        r = CargoRecord(
            etsng_code="421005",
            etsng_name="Бензин",
            is_dangerous=True,
        )
        assert r.is_dangerous is True
