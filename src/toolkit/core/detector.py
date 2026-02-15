"""Input type detection utilities."""

from __future__ import annotations

import base64
import json
import re
from pathlib import Path
from urllib.parse import urlparse

from defusedxml import ElementTree as DefusedET  # type: ignore[import-untyped]

_BINARY_RE = re.compile(r"^[01\s]+$")
_HEX_RE = re.compile(r"^[0-9a-fA-F]+$")
_EXTENSION_MAP: dict[str, str] = {
    ".json": "json",
    ".xml": "xml",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".txt": "text",
    ".html": "html",
    ".htm": "html",
    ".png": "image",
    ".jpg": "image",
    ".jpeg": "image",
    ".gif": "image",
}


def detect_from_path(path: Path) -> str:
    """Detect content type from a file extension."""
    return _EXTENSION_MAP.get(path.suffix.lower(), "unknown")


def detect_from_text(data: str) -> str:
    """Detect content type heuristically from raw text."""
    stripped = data.strip()
    if not stripped:
        return "empty"

    if _is_url(stripped):
        return "url"
    if _is_json(stripped):
        return "json"
    if _is_xml(stripped):
        return "xml"
    if _is_binary(stripped):
        return "binary"
    if _is_hex(stripped):
        return "hex"
    if _is_base64(stripped):
        return "base64"
    return "text"


def _is_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _is_json(value: str) -> bool:
    try:
        json.loads(value)
    except json.JSONDecodeError:
        return False
    return True


def _is_xml(value: str) -> bool:
    try:
        DefusedET.fromstring(value)
    except DefusedET.ParseError:
        return False
    return True


def _is_base64(value: str) -> bool:
    try:
        decoded = base64.b64decode(value, validate=True)
        if not decoded:
            return False
        decoded.decode("utf-8")
    except Exception:
        return False
    return True


def _is_binary(value: str) -> bool:
    compact = "".join(value.split())
    return bool(compact) and len(compact) % 8 == 0 and bool(_BINARY_RE.match(value))


def _is_hex(value: str) -> bool:
    compact = value.replace(" ", "")
    return bool(compact) and len(compact) % 2 == 0 and bool(_HEX_RE.match(compact))
