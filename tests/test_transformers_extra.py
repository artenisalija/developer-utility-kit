from __future__ import annotations

import pytest

from toolkit.core.registry import TransformerRegistry
from toolkit.transformers.structured import JsonToXmlTransformer, XmlToJsonTransformer


def test_base64_round_trip() -> None:
    registry = TransformerRegistry()
    encoded = registry.transform("hello", "text", "base64")
    decoded = registry.transform(encoded, "base64", "text")
    assert decoded == "hello"


def test_base64_invalid_input() -> None:
    registry = TransformerRegistry()
    with pytest.raises(ValueError):
        registry.transform("%%notbase64%%", "base64", "text")


def test_url_encode_decode_round_trip() -> None:
    registry = TransformerRegistry()
    encoded = registry.transform("a b", "text", "urlencode")
    assert encoded == "a%20b"
    decoded = registry.transform(encoded, "urlencode", "text")
    assert decoded == "a b"


def test_xml_to_json_invalid() -> None:
    transformer = XmlToJsonTransformer()
    with pytest.raises(ValueError):
        transformer.transform("<broken>")


def test_json_to_xml_invalid() -> None:
    transformer = JsonToXmlTransformer()
    with pytest.raises(ValueError):
        transformer.transform("{broken")


def test_xml_to_json_valid_nested() -> None:
    transformer = XmlToJsonTransformer()
    result = transformer.transform("<root><item>1</item><item>2</item></root>")
    assert '"item": ["1", "2"]' in result
