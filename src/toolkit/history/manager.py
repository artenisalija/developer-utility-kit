"""History manager for CLI invocations."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from toolkit.core.io_utils import ensure_directory


@dataclass(frozen=True)
class HistoryEntry:
    timestamp: str
    command: str
    status: str
    details: str


class HistoryManager:
    """Append-only local history with bounded reads."""

    def __init__(self, base_dir: Path | None = None) -> None:
        home = Path.home()
        default_dir = home / ".developer_utility_toolkit" / "history"
        self._base_dir = ensure_directory(base_dir or default_dir)
        self._history_file = self._base_dir / "history.jsonl"
        if not self._history_file.exists():
            self._history_file.touch()

    @property
    def history_file(self) -> Path:
        return self._history_file

    def add(self, command: str, status: str, details: str) -> None:
        payload = {
            "timestamp": datetime.now(UTC).isoformat(),
            "command": command.strip(),
            "status": status.strip(),
            "details": details.strip(),
        }
        with self._history_file.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")

    def recent(self, limit: int = 10) -> list[HistoryEntry]:
        if limit < 1:
            raise ValueError("limit must be >= 1")
        with self._history_file.open("r", encoding="utf-8") as handle:
            lines = handle.readlines()[-limit:]
        output: list[HistoryEntry] = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                parsed = json.loads(line)
            except json.JSONDecodeError:
                continue
            output.append(
                HistoryEntry(
                    timestamp=str(parsed.get("timestamp", "")),
                    command=str(parsed.get("command", "")),
                    status=str(parsed.get("status", "")),
                    details=str(parsed.get("details", "")),
                )
            )
        return output

    def clear(self) -> None:
        self._history_file.write_text("", encoding="utf-8")
