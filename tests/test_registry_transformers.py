from __future__ import annotations

import pytest

from toolkit.core.registry import TransformerRegistry


def test_registry_has_core_transformers() -> None:
    registry = TransformerRegistry()
    available = registry.available_transformations("text")
    assert ("text", "upper") in available
    assert ("text", "base64") in available


def test_transform_upper() -> None:
    registry = TransformerRegistry()
    assert registry.transform("hello", "text", "upper") == "HELLO"


def test_transform_json_to_xml() -> None:
    registry = TransformerRegistry()
    result = registry.transform('{"name":"dev"}', "json", "xml")
    assert "<name>dev</name>" in result


def test_transform_missing_raises() -> None:
    registry = TransformerRegistry()
    with pytest.raises(ValueError):
        registry.transform("hello", "text", "xml")


def test_available_transformations_all_and_load_errors() -> None:
    registry = TransformerRegistry()
    all_pairs = registry.available_transformations()
    assert ("json", "xml") in all_pairs
    assert isinstance(registry.load_errors(), dict)
