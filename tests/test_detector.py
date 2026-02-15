from __future__ import annotations

from pathlib import Path

from toolkit.core.detector import detect_from_path, detect_from_text


def test_detect_json() -> None:
    assert detect_from_text('{"a": 1}') == "json"


def test_detect_xml() -> None:
    assert detect_from_text("<root><a>1</a></root>") == "xml"


def test_detect_url() -> None:
    assert detect_from_text("https://example.com/path") == "url"


def test_detect_base64() -> None:
    assert detect_from_text("aGVsbG8=") == "base64"


def test_detect_text_fallback() -> None:
    assert detect_from_text("hello world") == "text"


def test_detect_file_extension() -> None:
    assert detect_from_path(Path("example.json")) == "json"
