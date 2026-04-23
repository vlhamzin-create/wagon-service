from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from etran_adapter.status.codes import (
    ETRAN_CODE_TO_STATUS,
    EtranDocumentStatus,
    EtranDocumentType,
    resolve_status,
)


class TestEtranDocumentType:
    def test_all_types_defined(self):
        assert EtranDocumentType.GU12 == "GU12"
        assert EtranDocumentType.WAYBILL == "WAYBILL"
        assert EtranDocumentType.REDIRECTION == "REDIRECTION"


class TestEtranDocumentStatus:
    def test_common_statuses(self):
        assert EtranDocumentStatus.DRAFT == "DRAFT"
        assert EtranDocumentStatus.SENDING == "SENDING"
        assert EtranDocumentStatus.SENT == "SENT"
        assert EtranDocumentStatus.ACCEPTED == "ACCEPTED"
        assert EtranDocumentStatus.REJECTED == "REJECTED"
        assert EtranDocumentStatus.ERROR == "ERROR"

    def test_gu12_statuses(self):
        assert EtranDocumentStatus.GU12_UNDER_REVIEW == "GU12_UNDER_REVIEW"
        assert EtranDocumentStatus.GU12_APPROVED == "GU12_APPROVED"
        assert EtranDocumentStatus.GU12_DENIED == "GU12_DENIED"

    def test_waybill_statuses(self):
        assert EtranDocumentStatus.WAYBILL_VISA_PENDING == "WAYBILL_VISA_PENDING"
        assert EtranDocumentStatus.WAYBILL_VISA_GRANTED == "WAYBILL_VISA_GRANTED"
        assert EtranDocumentStatus.WAYBILL_LOADED == "WAYBILL_LOADED"

    def test_redirection_statuses(self):
        assert EtranDocumentStatus.REDIR_PENDING == "REDIR_PENDING"
        assert EtranDocumentStatus.REDIR_APPROVED == "REDIR_APPROVED"
        assert EtranDocumentStatus.REDIR_DENIED == "REDIR_DENIED"


class TestResolveStatus:
    def test_known_codes(self):
        assert resolve_status("1") == EtranDocumentStatus.ACCEPTED
        assert resolve_status("3") == EtranDocumentStatus.GU12_UNDER_REVIEW
        assert resolve_status("10") == EtranDocumentStatus.WAYBILL_VISA_PENDING
        assert resolve_status("21") == EtranDocumentStatus.REDIR_APPROVED

    def test_unknown_code_defaults_to_accepted(self):
        assert resolve_status("999") == EtranDocumentStatus.ACCEPTED

    def test_all_mapped_codes_resolve(self):
        for code, expected_status in ETRAN_CODE_TO_STATUS.items():
            assert resolve_status(code) == expected_status


def _make_settings():
    s = MagicMock()
    s.etran_login = "test_login"
    s.etran_password = MagicMock()
    s.etran_password.get_secret_value.return_value = "secret"
    s.etran_asu_go_id = "ASU001"
    return s


class TestDocumentRegistry:
    def test_get_mapper_returns_correct_types(self):
        from etran_adapter.documents.registry import get_mapper

        gu12 = get_mapper("GU12", _make_settings())
        assert gu12.doc_type == "GU12"

        waybill = get_mapper("WAYBILL", _make_settings())
        assert waybill.doc_type == "WAYBILL"

        redir = get_mapper("REDIRECTION", _make_settings())
        assert redir.doc_type == "REDIRECTION"

    def test_get_mapper_raises_on_unknown(self):
        from etran_adapter.documents.registry import get_mapper

        with pytest.raises(KeyError, match="Unknown document type"):
            get_mapper("NONEXISTENT", _make_settings())

    def test_registered_types(self):
        from etran_adapter.documents.registry import registered_types

        types = registered_types()
        assert "GU12" in types
        assert "WAYBILL" in types
        assert "REDIRECTION" in types
