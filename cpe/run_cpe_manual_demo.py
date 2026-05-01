#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from approval_queue import ApprovalQueue, ApprovalRequest
from capability_store import CapabilityStore
from ledger import JsonlLedger, build_decision_record, build_outcome_record
from procurement_engine import ProcurementEngine, demo_payload
from state_machine import ProcurementStateMachine
from schemas import Capability


def main() -> None:
    task, state, policy, _ = demo_payload()
    base_dir = Path(__file__).resolve().parent
    ledger = JsonlLedger(base_dir / "ledger")
    approval_queue = ApprovalQueue(base_dir / "runtime" / "approval_queue.json")
    sm = ProcurementStateMachine()

    # Force a manual-only scenario so the approval gate is exercised end-to-end.
    manual_capabilities = [
        Capability(
            capability_id="deep_reasoning_model",
            category="reasoning",
            provider="provider_c",
            unit_cost=0.04,
            latency_sec=10,
            quality_score=0.95,
            reliability_score=0.92,
            historical_success_rate=0.78,
            historical_confidence_delta_avg=0.24,
            historical_roi_avg=4.8,
            approval_mode="manual",
            supported_tasks=["market_verification", "report_synthesis"],
        )
    ]

    policy.min_procurement_score = 0.05
    engine = ProcurementEngine(policy)

    sm.transition("assessing", "task received")
    sm.transition("discovering", "manual-only capability scenario")
    sm.transition("deciding", "forced manual capability evaluation")

    result = engine.choose_capability(task, state, manual_capabilities)
    selected = result.get("selected")
    decision_record = build_decision_record(task.task_id, selected, result)
    ledger.append_decision(decision_record)

    if not selected:
        sm.transition("fallback", "no manual capability selected")
        sm.transition("completed", "manual demo ended without selection")
        print(json.dumps({
            "task": task.to_dict(),
            "state_machine": sm.to_dict(),
            "decision": result,
            "approval_queue": approval_queue.list_all(),
        }, ensure_ascii=False, indent=2))
        return

    sm.transition("awaiting_approval", "manual capability requires approval")
    approval_request = ApprovalRequest(
        request_id=f"apr_{task.task_id}_manual_demo",
        task_id=task.task_id,
        capability_id=selected["capability_id"],
        expected_cost=selected["unit_cost"],
        expected_benefit="force exercise manual approval flow",
        reason="manual demo path",
    )
    added = approval_queue.add(approval_request)
    approved = approval_queue.update_status(approval_request.request_id, "approved", "manual demo auto-approved")

    sm.transition("executing", "approval granted")
    confidence_after = min(state.confidence + 0.22, 1.0)
    outcome_record = build_outcome_record(
        task_id=task.task_id,
        capability_id=selected["capability_id"],
        executed=True,
        actual_cost=selected["unit_cost"],
        confidence_before=state.confidence,
        confidence_after=confidence_after,
        notes="manual demo simulated outcome",
    )
    ledger.append_outcome(outcome_record)

    sm.transition("evaluating_outcome", "manual capability outcome evaluated")
    if confidence_after >= task.target_confidence:
        sm.transition("completed", "manual capability reached target confidence")
    else:
        sm.transition("fallback", "manual capability still below target confidence")
        sm.transition("completed", "manual demo finished")

    print(json.dumps({
        "task": task.to_dict(),
        "selected": selected,
        "decision_record": decision_record.to_dict(),
        "approval_added": added,
        "approval_approved": approved,
        "outcome_record": outcome_record.to_dict(),
        "state_machine": sm.to_dict(),
        "ledger_summary": ledger.summary(),
        "approval_queue": approval_queue.list_all(),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
