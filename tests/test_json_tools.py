from __future__ import annotations

from toolkit.formatters.json_tools import format_json, minify_json, validate_json


def test_format_json() -> None:
    result = format_json('{"b":2,"a":1}')
    assert '"a": 1' in result
    assert result.splitlines()[0] == "{"


def test_minify_json() -> None:
    result = minify_json('{"b": 2, "a": 1}')
    assert result == '{"a":1,"b":2}'


def test_validate_json_invalid() -> None:
    ok, message = validate_json('{"a":')
    assert not ok
    assert "Invalid JSON" in message
