"""Image pixelation functions."""

from __future__ import annotations

from pathlib import Path


def pixelate_image(input_path: Path, output_path: Path, block_size: int = 8) -> Path:
    """Pixelate image using pillow if installed."""
    if block_size < 1:
        raise ValueError("Block size must be >= 1")
    if not input_path.exists() or not input_path.is_file():
        raise ValueError("Input image does not exist")

    try:
        from PIL import Image  # type: ignore[import-untyped]
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Pillow is required for image operations. Install with: pip install .[image]"
        ) from exc

    with Image.open(input_path) as img:
        width, height = img.size
        resized = img.resize(
            (max(1, width // block_size), max(1, height // block_size)),
            resample=Image.Resampling.NEAREST,
        )
        pixelated = resized.resize((width, height), Image.Resampling.NEAREST)
        pixelated.save(output_path)
    return output_path
