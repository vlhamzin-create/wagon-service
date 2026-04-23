from __future__ import annotations

from etran_adapter.soap.exceptions import (
    EtranBaseError,
    EtranBusinessError,
    EtranProtocolError,
    EtranSoapFaultError,
    EtranTransportError,
)


class TestExceptionHierarchy:
    def test_all_inherit_from_base(self):
        assert issubclass(EtranTransportError, EtranBaseError)
        assert issubclass(EtranSoapFaultError, EtranBaseError)
        assert issubclass(EtranProtocolError, EtranBaseError)
        assert issubclass(EtranBusinessError, EtranBaseError)

    def test_transport_error_attrs(self):
        err = EtranTransportError("timeout", status_code=504, cause=TimeoutError())
        assert err.status_code == 504
        assert isinstance(err.cause, TimeoutError)
        assert "timeout" in str(err)

    def test_soap_fault_attrs(self):
        err = EtranSoapFaultError("soap:Server", "Internal", detail="<d/>")
        assert err.fault_code == "soap:Server"
        assert err.fault_string == "Internal"
        assert err.detail == "<d/>"
        assert "SOAP Fault" in str(err)

    def test_business_error_attrs(self):
        err = EtranBusinessError("E001", "Not found", doc_id="DOC-42")
        assert err.error_code == "E001"
        assert err.error_message == "Not found"
        assert err.doc_id == "DOC-42"
        assert "Business error" in str(err)
