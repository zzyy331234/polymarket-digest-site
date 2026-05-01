#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from approval_queue import ApprovalQueue, ApprovalRequest
from capability_store import CapabilityStore
from ledger import JsonlLedger, build_decision_record, build_outcome_record
from procurement_engine import ProcurementEngine, demo_payload
from state_machine import ProcurementStateMachine


SIMULATED_CONFIDENCE_LIFTS = {
    "cheap_news_search": 0.14,
    "premium_news_verify": 0.18,
    "deep_reasoning_model": 0.10,
}


def explain_score_change(before: dict | None, after: dict | None) -> dict | None:
    if not before or not after:
        return None

    delta_success = round(after.get("historical_success_rate", 0.0) - before.get("historical_success_rate", 0.0), 4)
    delta_conf = round(after.get("historical_confidence_delta_avg", 0.0) - before.get("historical_confidence_delta_avg", 0.0), 4)
    delta_roi = round(after.get("historical_roi_avg", 0.0) - before.get("historical_roi_avg", 0.0), 4)

    drivers = []
    if delta_success > 0:
        drivers.append("success_rate_up")
    if delta_conf > 0:
        drivers.append("confidence_delta_avg_up")
    if delta_roi > 0:
        drivers.append("roi_avg_up")
    if not drivers:
        drivers.append("no_positive_change")

    return {
        "delta_success_rate": delta_success,
        "delta_confidence_delta_avg": delta_conf,
        "delta_roi_avg": delta_roi,
        "drivers": drivers,
        "summary": f"success {delta_success:+.4f}, conf_delta {delta_conf:+.4f}, roi {delta_roi:+.4f}",
    }


def main() -> None:
    task, state, policy, _ = demo_payload()
    base_dir = Path(__file__).resolve().parent
    engine = ProcurementEngine(policy)
    ledger = JsonlLedger(base_dir / "ledger")
    capability_store = CapabilityStore(base_dir / "runtime" / "procurement_capabilities.runtime.json")
    approval_queue = ApprovalQueue(base_dir / "runtime" / "approval_queue.json")
    sm = ProcurementStateMachine()

    used_capabilities = []
    rounds = []
    current_confidence = state.confidence
    current_spent = state.spent
    remaining_budget = state.remaining_budget

    sm.transition("assessing", "task received")
    if not state.need_external_support:
        sm.transition("completed", "local workflow was sufficient")
        print(json.dumps({"task": task.to_dict(), "state_machine": sm.to_dict()}, ensure_ascii=False, indent=2))
        return

    sm.transition("discovering", "external support required")

    for round_no in range(1, 4):
        round_state = state.__class__(
            confidence=current_confidence,
            evidence_count=state.evidence_count + len(used_capabilities),
            spent=current_spent,
            remaining_budget=remaining_budget,
            need_external_support=current_confidence < task.target_confidence,
            current_stage="verification" if round_no > 1 else "initial_screening",
            selected_capabilities=list(used_capabilities),
            blocked_reasons=[],
        )

        if current_confidence >= task.target_confidence or remaining_budget <= 0:
            break

        current_capabilities = capability_store.load_models()
        capability_snapshot_before = {
            cap.capability_id: {
                "historical_success_rate": cap.historical_success_rate,
                "historical_confidence_delta_avg": cap.historical_confidence_delta_avg,
                "historical_roi_avg": cap.historical_roi_avg,
                "quality_score": cap.quality_score,
                "reliability_score": cap.reliability_score,
            }
            for cap in current_capabilities
        }
        sm.transition("deciding", f"round {round_no} candidate evaluation")
        result = engine.choose_capability(task, round_state, current_capabilities, exclude_capability_ids=used_capabilities)
        selected = result.get("selected")

        decision_record = build_decision_record(task.task_id, selected, result)
        ledger.append_decision(decision_record)

        if not selected:
            sm.transition("fallback", f"round {round_no} no suitable capability selected")
            break

        approval_mode = selected.get("metadata", {}).get("approval_mode", "auto")
        approval_record = None
        if approval_mode == "manual":
            sm.transition("awaiting_approval", f"round {round_no} manual review required")
            approval_request = ApprovalRequest(
                request_id=f"apr_{task.task_id}_r{round_no}",
                task_id=task.task_id,
                capability_id=selected["capability_id"],
                expected_cost=selected["unit_cost"],
                expected_benefit=f"round {round_no} capability may improve confidence",
                reason="selected capability requires manual approval",
            )
            approval_queue.add(approval_request)
            approval_record = approval_queue.update_status(approval_request.request_id, "approved", "demo auto-approved manual gate")

        sm.transition("executing", f"round {round_no} executing {selected['capability_id']}")

        lift = SIMULATED_CONFIDENCE_LIFTS.get(selected["capability_id"], 0.08)
        confidence_after = min(current_confidence + lift, 1.0)
        actual_cost = selected["unit_cost"]
        outcome_record = build_outcome_record(
            task_id=task.task_id,
            capability_id=selected["capability_id"],
            executed=True,
            actual_cost=actual_cost,
            confidence_before=current_confidence,
            confidence_after=confidence_after,
            notes=f"round {round_no} simulated outcome",
        )
        ledger.append_outcome(outcome_record)
        updated_capabilities = capability_store.update_from_outcome(outcome_record.to_dict())

        sm.transition("evaluating_outcome", f"round {round_no} outcome evaluated")

        updated_capability = next((c for c in updated_capabilities if c.get("capability_id") == selected["capability_id"]), None)
        capability_snapshot_after = None
        if updated_capability:
            capability_snapshot_after = {
                "historical_success_rate": updated_capability.get("historical_success_rate"),
                "historical_confidence_delta_avg": updated_capability.get("historical_confidence_delta_avg"),
                "historical_roi_avg": updated_capability.get("historical_roi_avg"),
                "quality_score": updated_capability.get("quality_score"),
                "reliability_score": updated_capability.get("reliability_score"),
            }
        capability_before = capability_snapshot_before.get(selected["capability_id"])
        rounds.append({
            "round": round_no,
            "selected": selected,
            "approval_record": approval_record,
            "decision_record": decision_record.to_dict(),
            "outcome_record": outcome_record.to_dict(),
            "capability_before": capability_before,
            "capability_after": capability_snapshot_after,
            "score_change_explanation": explain_score_change(capability_before, capability_snapshot_after),
            "updated_capability": updated_capability,
        })

        used_capabilities.append(selected["capability_id"])
        current_confidence = confidence_after
        current_spent = round(current_spent + actual_cost, 4)
        remaining_budget = round(max(task.budget_cap - current_spent, 0.0), 4)

        if current_confidence >= task.target_confidence:
            sm.transition("completed", f"target confidence reached after round {round_no}")
            break

        sm.transition("discovering", f"round {round_no} completed, evaluating next capability")
    else:
        sm.transition("completed", "max rounds reached")

    if sm.state not in {"completed", "aborted"}:
        sm.transition("completed", "multi-round demo finished")

    print(json.dumps({
        "task": task.to_dict(),
        "final_confidence": current_confidence,
        "total_spent": current_spent,
        "used_capabilities": used_capabilities,
        "rounds": rounds,
        "state_machine": sm.to_dict(),
        "ledger_summary": ledger.summary(),
        "approval_queue": approval_queue.list_all(),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
