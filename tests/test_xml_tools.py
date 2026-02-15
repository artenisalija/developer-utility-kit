from __future__ import annotations

from toolkit.formatters.xml_tools import format_xml, minify_xml, validate_xml


def test_format_xml() -> None:
    result = format_xml("<root><item>1</item></root>")
    assert "<root>" in result
    assert "  <item>1</item>" in result


def test_minify_xml() -> None:
    result = minify_xml("<root>\n  <item>1</item>\n</root>")
    assert "<item>1</item>" in result


def test_validate_xml_invalid() -> None:
    ok, message = validate_xml("<root>")
    assert not ok
    assert "Invalid XML" in message
