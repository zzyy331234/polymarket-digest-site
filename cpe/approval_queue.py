#!/usr/bin/env python3
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat()


@dataclass
class ApprovalRequest:
    request_id: str
    task_id: str
    capability_id: str
    expected_cost: float
    expected_benefit: str
    reason: str
    status: str = "pending"
    created_at: str = field(default_factory=now_iso)
    reviewed_at: str = ""
    reviewer_note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ApprovalQueue:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("[]\n", encoding="utf-8")

    def _load(self) -> List[Dict[str, Any]]:
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _save(self, rows: List[Dict[str, Any]]) -> None:
        self.path.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def add(self, req: ApprovalRequest) -> Dict[str, Any]:
        rows = self._load()
        payload = req.to_dict()
        rows.append(payload)
        self._save(rows)
        return payload

    def list_all(self) -> List[Dict[str, Any]]:
        return self._load()

    def list_by_status(self, status: str) -> List[Dict[str, Any]]:
        return [row for row in self._load() if row.get("status") == status]

    def update_status(self, request_id: str, status: str, reviewer_note: str = "") -> Dict[str, Any] | None:
        rows = self._load()
        updated = None
        for row in rows:
            if row.get("request_id") == request_id:
                row["status"] = status
                row["reviewed_at"] = now_iso()
                row["reviewer_note"] = reviewer_note
                updated = row
                break
        self._save(rows)
        return updated
