"""JSON/XML transformation helpers."""

from __future__ import annotations

import json
from xml.etree import ElementTree as ET

from defusedxml import ElementTree as DefusedET  # type: ignore[import-untyped]

from toolkit.core.base_transformer import BaseTransformer
from toolkit.core.registry import TransformerRegistry


class JsonToXmlTransformer(BaseTransformer):
    input_type = "json"
    output_type = "xml"

    def transform(self, data: str) -> str:
        try:
            parsed = json.loads(data)
        except json.JSONDecodeError as exc:
            raise ValueError("Invalid JSON input") from exc
        root = ET.Element("root")
        _json_to_xml(root, parsed)
        return ET.tostring(root, encoding="unicode")


class XmlToJsonTransformer(BaseTransformer):
    input_type = "xml"
    output_type = "json"

    def transform(self, data: str) -> str:
        try:
            root = DefusedET.fromstring(data)
        except DefusedET.ParseError as exc:
            raise ValueError("Invalid XML input") from exc
        converted = _xml_to_dict(root)
        return json.dumps(converted, ensure_ascii=False)


def _json_to_xml(parent: ET.Element, value: object) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            child = ET.SubElement(parent, str(key))
            _json_to_xml(child, item)
        return
    if isinstance(value, list):
        for item in value:
            child = ET.SubElement(parent, "item")
            _json_to_xml(child, item)
        return
    parent.text = "" if value is None else str(value)


def _xml_to_dict(element: ET.Element) -> dict[str, object]:
    children = list(element)
    if not children:
        return {element.tag: element.text or ""}

    grouped: dict[str, list[object]] = {}
    for child in children:
        child_value = _xml_to_dict(child)[child.tag]
        grouped.setdefault(child.tag, []).append(child_value)

    output: dict[str, object] = {}
    for key, values in grouped.items():
        output[key] = values[0] if len(values) == 1 else values
    return {element.tag: output}


def register(registry: TransformerRegistry) -> None:
    registry.register_transformer(JsonToXmlTransformer)
    registry.register_transformer(XmlToJsonTransformer)
