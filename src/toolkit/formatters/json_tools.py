"""JSON formatting and validation functions."""

from __future__ import annotations

import json


def format_json(data: str, indent: int = 2) -> str:
    parsed = _parse_json(data)
    return json.dumps(parsed, indent=indent, ensure_ascii=False, sort_keys=True)


def minify_json(data: str) -> str:
    parsed = _parse_json(data)
    return json.dumps(parsed, separators=(",", ":"), ensure_ascii=False, sort_keys=True)


def validate_json(data: str) -> tuple[bool, str]:
    try:
        _parse_json(data)
    except ValueError as exc:
        return (False, str(exc))
    return (True, "Valid JSON")


def _parse_json(data: str) -> object:
    try:
        return json.loads(data)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Invalid JSON: {exc.msg} at line {exc.lineno}, column {exc.colno}"
        ) from exc
