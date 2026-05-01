#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from procurement_engine import ProcurementEngine, demo_payload
from ledger import JsonlLedger, build_decision_record, build_outcome_record


def main() -> None:
    task, state, policy, capabilities = demo_payload()
    engine = ProcurementEngine(policy)
    result = engine.choose_capability(task, state, capabilities)

    ledger = JsonlLedger(Path(__file__).resolve().parent / "ledger")
    selected = result.get("selected")

    decision_record = build_decision_record(task.task_id, selected, result)
    ledger.append_decision(decision_record)

    if selected:
        outcome_record = build_outcome_record(
            task_id=task.task_id,
            capability_id=selected["capability_id"],
            executed=True,
            actual_cost=selected["unit_cost"],
            confidence_before=state.confidence,
            confidence_after=min(state.confidence + 0.14, 1.0),
            notes="demo simulated outcome",
        )
        ledger.append_outcome(outcome_record)

    print(json.dumps({
        "selected": selected,
        "ledger_summary": ledger.summary(),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
