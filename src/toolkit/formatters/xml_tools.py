"""Secure XML formatting and validation functions."""

from __future__ import annotations

from xml.etree import ElementTree as ET

from defusedxml import ElementTree as DefusedET  # type: ignore[import-untyped]


def format_xml(data: str) -> str:
    root = _parse_xml(data)
    ET.indent(root, space="  ")
    return ET.tostring(root, encoding="unicode")


def minify_xml(data: str) -> str:
    root = _parse_xml(data)
    return ET.tostring(root, encoding="unicode", method="xml")


def validate_xml(data: str) -> tuple[bool, str]:
    try:
        _parse_xml(data)
    except ValueError as exc:
        return (False, str(exc))
    return (True, "Valid XML")


def _parse_xml(data: str) -> ET.Element:
    try:
        parsed: ET.Element = DefusedET.fromstring(data)
        return parsed
    except DefusedET.ParseError as exc:
        raise ValueError(f"Invalid XML: {exc}") from exc
