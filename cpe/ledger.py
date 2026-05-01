#!/usr/bin/env python3
from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, Dict

from schemas import DecisionRecord, OutcomeRecord, now_iso


class JsonlLedger:
    def __init__(self, base_dir: str | Path):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.decision_path = self.base_dir / "decision_records.jsonl"
        self.outcome_path = self.base_dir / "outcome_records.jsonl"

    def _normalize(self, payload: Any) -> Dict[str, Any]:
        if is_dataclass(payload):
            payload = asdict(payload)
        elif not isinstance(payload, dict):
            payload = {"value": payload}
        if "created_at" not in payload:
            payload["created_at"] = now_iso()
        return payload

    def append_decision(self, payload: Any) -> Dict[str, Any]:
        record = self._normalize(payload)
        with self.decision_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        return record

    def append_outcome(self, payload: Any) -> Dict[str, Any]:
        record = self._normalize(payload)
        with self.outcome_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        return record

    def summary(self) -> Dict[str, Any]:
        def _count(path: Path) -> int:
            if not path.exists():
                return 0
            with path.open("r", encoding="utf-8") as f:
                return sum(1 for _ in f)

        return {
            "base_dir": str(self.base_dir),
            "decision_records": _count(self.decision_path),
            "outcome_records": _count(self.outcome_path),
        }


def build_decision_record(task_id: str, selected: Dict[str, Any] | None, raw_result: Dict[str, Any]) -> DecisionRecord:
    return DecisionRecord(
        task_id=task_id,
        selected=selected,
        buy_candidates=raw_result.get("buy_candidates", []),
        all_decisions=raw_result.get("all_decisions", []),
    )


def build_outcome_record(
    task_id: str,
    capability_id: str,
    executed: bool,
    actual_cost: float,
    confidence_before: float,
    confidence_after: float,
    notes: str = "",
) -> OutcomeRecord:
    return OutcomeRecord(
        task_id=task_id,
        capability_id=capability_id,
        executed=executed,
        actual_cost=actual_cost,
        confidence_before=confidence_before,
        confidence_after=confidence_after,
        notes=notes,
    )
