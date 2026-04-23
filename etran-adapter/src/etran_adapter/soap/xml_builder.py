from __future__ import annotations

from lxml import etree

from etran_adapter.config import Settings


def build_access_params(settings: Settings) -> etree._Element:
    """Блок параметров доступа АСУ ГО (раздел 5.1.1 спецификации ЭТРАН)."""
    root = etree.Element("AccessParams")
    etree.SubElement(root, "Login").text = settings.etran_login
    etree.SubElement(root, "Password").text = settings.etran_password.get_secret_value()
    etree.SubElement(root, "AsuGoId").text = settings.etran_asu_go_id
    return root


def wrap_request(tag: str, settings: Settings, body: etree._Element | None = None) -> str:
    """Формирует полный XML-запрос с AccessParams для передачи в Text.

    Возвращает строку XML::

        <{tag}>
          <AccessParams>...</AccessParams>
          {body}
        </{tag}>
    """
    root = etree.Element(tag)
    root.append(build_access_params(settings))
    if body is not None:
        root.append(body)
    return etree.tostring(root, encoding="unicode", xml_declaration=False)
