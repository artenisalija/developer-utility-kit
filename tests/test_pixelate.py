from __future__ import annotations

from pathlib import Path

import pytest

from toolkit.image_tools.pixelate import pixelate_image


def test_pixelate_image_with_mocked_pil(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    input_file = tmp_path / "input.png"
    output_file = tmp_path / "output.png"
    input_file.write_bytes(b"fake")

    class FakeImage:
        def __init__(self) -> None:
            self.size = (20, 20)

        def __enter__(self) -> FakeImage:
            return self

        def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
            return None

        def resize(self, size: tuple[int, int], resample: int) -> FakeImage:
            assert size[0] >= 1
            assert size[1] >= 1
            assert resample == 1
            return self

        def save(self, path: object) -> None:
            assert str(path).endswith(".png")

    class FakeImageModule:
        class Resampling:
            NEAREST = 1

        @staticmethod
        def open(path: object) -> FakeImage:
            assert str(path).endswith("input.png")
            return FakeImage()

    fake_pil = type("FakePIL", (), {"Image": FakeImageModule})()
    monkeypatch.setitem(__import__("sys").modules, "PIL", fake_pil)

    result = pixelate_image(input_file, output_file, block_size=5)
    assert result == output_file


def test_pixelate_invalid_block_size(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        pixelate_image(tmp_path / "x.png", tmp_path / "y.png", block_size=0)


def test_pixelate_missing_input(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        pixelate_image(tmp_path / "missing.png", tmp_path / "out.png", block_size=2)
