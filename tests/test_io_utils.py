from __future__ import annotations

from pathlib import Path

import pytest

from toolkit.core.io_utils import (
    ensure_directory,
    read_text_file,
    safe_output_path,
    write_text_file,
)


def test_ensure_directory(tmp_path: Path) -> None:
    target = tmp_path / "a" / "b"
    result = ensure_directory(target)
    assert result.exists()
    assert result.is_dir()


def test_safe_output_path_sanitizes_filename(tmp_path: Path) -> None:
    output = safe_output_path(tmp_path, "../unsafe.txt")
    assert output.parent == tmp_path.resolve()
    assert output.name == "unsafe.txt"


def test_safe_output_path_requires_filename(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        safe_output_path(tmp_path, "")


def test_read_write_text_file(tmp_path: Path) -> None:
    file = tmp_path / "data.txt"
    write_text_file(file, "abc")
    assert read_text_file(file) == "abc"
