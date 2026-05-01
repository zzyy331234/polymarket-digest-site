#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from ledger import JsonlLedger, build_decision_record, build_outcome_record
from procurement_engine import ProcurementEngine, demo_payload
from state_machine import ProcurementStateMachine


def main() -> None:
    task, state, policy, capabilities = demo_payload()
    engine = ProcurementEngine(policy)
    ledger = JsonlLedger(Path(__file__).resolve().parent / "ledger")
    sm = ProcurementStateMachine()

    sm.transition("assessing", "task received")

    if not state.need_external_support:
        sm.transition("completed", "local workflow was sufficient")
        print(json.dumps({
            "task": task.to_dict(),
            "state_machine": sm.to_dict(),
            "decision": None,
            "ledger_summary": ledger.summary(),
        }, ensure_ascii=False, indent=2))
        return

    sm.transition("discovering", "external support required")
    sm.transition("deciding", "candidate capabilities discovered")

    result = engine.choose_capability(task, state, capabilities)
    selected = result.get("selected")

    decision_record = build_decision_record(task.task_id, selected, result)
    ledger.append_decision(decision_record)

    if not selected:
        sm.transition("fallback", "no suitable capability selected")
        sm.transition("completed", "task ended without procurement")
        print(json.dumps({
            "task": task.to_dict(),
            "state_machine": sm.to_dict(),
            "decision": result,
            "ledger_summary": ledger.summary(),
        }, ensure_ascii=False, indent=2))
        return

    approval_mode = selected.get("metadata", {}).get("approval_mode", "auto")
    if approval_mode == "manual":
        sm.transition("awaiting_approval", "selected capability requires manual review")

    sm.transition("executing", "selected capability approved")

    simulated_confidence_after = min(state.confidence + 0.14, 1.0)
    outcome_record = build_outcome_record(
        task_id=task.task_id,
        capability_id=selected["capability_id"],
        executed=True,
        actual_cost=selected["unit_cost"],
        confidence_before=state.confidence,
        confidence_after=simulated_confidence_after,
        notes="demo simulated outcome",
    )
    ledger.append_outcome(outcome_record)

    sm.transition("evaluating_outcome", "procurement executed")
    if simulated_confidence_after >= task.target_confidence:
        sm.transition("completed", "confidence target reached")
    else:
        sm.transition("fallback", "confidence still below target")
        sm.transition("completed", "demo stopped after one procurement round")

    print(json.dumps({
        "task": task.to_dict(),
        "selected": selected,
        "state_machine": sm.to_dict(),
        "decision_record": decision_record.to_dict(),
        "outcome_record": outcome_record.to_dict(),
        "ledger_summary": ledger.summary(),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
