"""Safe file and path operations for CLI commands."""

from __future__ import annotations

from pathlib import Path


def ensure_directory(path: Path) -> Path:
    """Create directory if missing and return normalized path."""
    resolved = path.expanduser().resolve()
    resolved.mkdir(parents=True, exist_ok=True)
    return resolved


def safe_output_path(base_dir: Path, file_name: str) -> Path:
    """Build an output path constrained to a base directory."""
    normalized_name = Path(file_name).name
    if not normalized_name:
        raise ValueError("Output filename is required")

    base = ensure_directory(base_dir)
    candidate = (base / normalized_name).resolve()
    if not candidate.is_relative_to(base):
        raise ValueError("Refusing to write outside of configured output directory")
    return candidate


def read_text_file(path: Path) -> str:
    """Read UTF-8 text from file."""
    return path.read_text(encoding="utf-8")


def write_text_file(path: Path, content: str) -> None:
    """Write UTF-8 text to file."""
    path.write_text(content, encoding="utf-8")
