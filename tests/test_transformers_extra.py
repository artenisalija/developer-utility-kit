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


def test_binary_round_trip() -> None:
    registry = TransformerRegistry()
    binary = registry.transform("hi", "text", "binary")
    assert binary == "01101000 01101001"
    decoded = registry.transform(binary, "binary", "text")
    assert decoded == "hi"


def test_hex_round_trip() -> None:
    registry = TransformerRegistry()
    hex_value = registry.transform("hi", "text", "hex")
    assert hex_value == "6869"
    decoded = registry.transform(hex_value, "hex", "text")
    assert decoded == "hi"


def test_binary_to_base64() -> None:
    registry = TransformerRegistry()
    base64_value = registry.transform("01101000 01101001", "binary", "base64")
    assert base64_value == "aGk="


def test_base64_to_binary() -> None:
    registry = TransformerRegistry()
    binary_value = registry.transform("aGk=", "base64", "binary")
    assert binary_value == "01101000 01101001"


def test_binary_invalid_input() -> None:
    registry = TransformerRegistry()
    with pytest.raises(ValueError):
        registry.transform("01012", "binary", "text")


def test_binary_short_input_is_padded() -> None:
    registry = TransformerRegistry()
    result = registry.transform("1010", "binary", "hex")
    assert result == "0a"


def test_hex_invalid_input() -> None:
    registry = TransformerRegistry()
    with pytest.raises(ValueError):
        registry.transform("xyz", "hex", "text")


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
