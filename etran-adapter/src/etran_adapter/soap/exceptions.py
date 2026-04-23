from __future__ import annotations


class EtranBaseError(Exception):
    """Корневое исключение модуля."""


class EtranTransportError(EtranBaseError):
    """Ошибка HTTP-слоя: таймаут, сеть, TLS."""

    def __init__(
        self, message: str, status_code: int | None = None, cause: Exception | None = None
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.cause = cause


class EtranSoapFaultError(EtranBaseError):
    """SOAP Fault получен от сервера (HTTP 500 с телом Fault)."""

    def __init__(self, fault_code: str, fault_string: str, detail: str | None = None) -> None:
        super().__init__(f"SOAP Fault [{fault_code}]: {fault_string}")
        self.fault_code = fault_code
        self.fault_string = fault_string
        self.detail = detail


class EtranProtocolError(EtranBaseError):
    """Ответ не является валидным SOAP 1.1 XML."""


class EtranBusinessError(EtranBaseError):
    """Бизнес-ошибка в теле XML-ответа (ErrorCode/ErrorMessage в ЭТРАН)."""

    def __init__(
        self, error_code: str, error_message: str, doc_id: str | None = None
    ) -> None:
        super().__init__(f"Business error [{error_code}]: {error_message}")
        self.error_code = error_code
        self.error_message = error_message
        self.doc_id = doc_id
