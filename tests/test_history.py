from __future__ import annotations

from pathlib import Path

import pytest

from toolkit.history.manager import HistoryManager


def test_history_add_and_recent(tmp_path: Path) -> None:
    manager = HistoryManager(base_dir=tmp_path)
    manager.add("analyze", "success", "json")
    manager.add("convert", "error", "unsupported")

    entries = manager.recent(limit=2)
    assert len(entries) == 2
    assert entries[0].command == "analyze"
    assert entries[1].status == "error"


def test_history_clear(tmp_path: Path) -> None:
    manager = HistoryManager(base_dir=tmp_path)
    manager.add("analyze", "success", "json")
    manager.clear()
    assert manager.recent(limit=10) == []


def test_history_limit_validation(tmp_path: Path) -> None:
    manager = HistoryManager(base_dir=tmp_path)
    with pytest.raises(ValueError):
        manager.recent(limit=0)
