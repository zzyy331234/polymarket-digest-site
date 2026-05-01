#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any


def update_capability_stats(capability: Dict[str, Any], outcome: Dict[str, Any]) -> Dict[str, Any]:
    prev_success = capability.get("historical_success_rate", 0.5)
    prev_delta = capability.get("historical_confidence_delta_avg", 0.0)
    prev_roi = capability.get("historical_roi_avg", 1.0)

    improved = 1.0 if outcome.get("confidence_delta", 0.0) > 0 else 0.0
    new_delta = float(outcome.get("confidence_delta", 0.0))
    actual_cost = max(float(outcome.get("actual_cost", 0.0)), 0.001)
    new_roi = max(new_delta / actual_cost, 0.0)

    alpha = 0.3
    capability["historical_success_rate"] = round((1 - alpha) * prev_success + alpha * improved, 4)
    capability["historical_confidence_delta_avg"] = round((1 - alpha) * prev_delta + alpha * new_delta, 4)
    capability["historical_roi_avg"] = round((1 - alpha) * prev_roi + alpha * new_roi, 4)
    return capability


def main() -> None:
    sample_cap_path = Path(__file__).resolve().parent / "samples" / "procurement_capabilities.sample.json"
    capabilities = json.loads(sample_cap_path.read_text())
    outcome = {
        "capability_id": "cheap_news_search",
        "actual_cost": 0.01,
        "confidence_delta": 0.14,
    }

    updated = []
    for cap in capabilities:
        if cap["capability_id"] == outcome["capability_id"]:
            updated.append(update_capability_stats(cap, outcome))
        else:
            updated.append(cap)

    print(json.dumps(updated, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
