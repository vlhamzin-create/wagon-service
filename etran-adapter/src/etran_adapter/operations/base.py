from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from etran_adapter.soap.client import EtranSoapClient


class BaseOperation(ABC):
    """Базовый класс бизнес-операции ЭТРАН.

    Каждая операция умеет:
    - построить XML-запрос из параметров;
    - выполнить синхронный вызов (для GetBlock);
    - выполнить асинхронный вызов (для SendBlock, через RQ worker).
    """

    @abstractmethod
    def build_xml(self, params: dict[str, Any]) -> str:
        """Построить XML для параметра Text."""
        ...

    def execute_sync(self, client: EtranSoapClient, params: dict[str, Any]) -> str:
        """Синхронное выполнение через GetBlock."""
        xml = self.build_xml(params)
        return client.get_block(xml)

    def execute_async(self, client: EtranSoapClient, params: dict[str, Any]) -> str:
        """Асинхронное выполнение через SendBlock."""
        xml = self.build_xml(params)
        return client.send_block(xml)
