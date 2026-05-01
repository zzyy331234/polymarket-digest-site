#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from schemas import Capability
from update_capability_stats import update_capability_stats


class CapabilityStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def load(self) -> List[Dict[str, Any]]:
        return json.loads(self.path.read_text(encoding="utf-8"))

    def save(self, capabilities: List[Dict[str, Any]]) -> None:
        self.path.write_text(json.dumps(capabilities, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def load_models(self) -> List[Capability]:
        return [Capability(**item) for item in self.load()]

    def update_from_outcome(self, outcome: Dict[str, Any]) -> List[Dict[str, Any]]:
        capabilities = self.load()
        updated: List[Dict[str, Any]] = []
        for cap in capabilities:
            if cap.get("capability_id") == outcome.get("capability_id"):
                updated.append(update_capability_stats(cap, outcome))
            else:
                updated.append(cap)
        self.save(updated)
        return updated
