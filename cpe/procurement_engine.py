#!/usr/bin/env python3
"""Basic procurement decision engine for agent auto-purchasing external capabilities.

V0 goals:
- keep logic explainable
- enforce budget / ROI / confidence guards
- rank candidate capabilities for a task

Usage:
  python3 procurement_engine.py --demo
  python3 procurement_engine.py --task task.json --state state.json --caps capabilities.json --policy policy.json
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from schemas import Capability, Policy, State, Task


@dataclass
class DecisionResult:
    capability_id: str
    provider: str
    decision: str
    score: float
    expected_roi: float
    unit_cost: float
    reason: str
    metadata: Dict[str, Any]


class ProcurementEngine:
    def __init__(self, policy: Policy):
        self.policy = policy

    def _risk_weight(self, risk_level: str) -> float:
        return {
            "high": 1.2,
            "medium": 1.0,
            "low": 0.8,
        }.get(risk_level, 1.0)

    def _quality_weight(self, capability: Capability) -> float:
        historical_bonus = (
            0.5 * capability.historical_success_rate
            + 0.3 * capability.historical_confidence_delta_avg
            + 0.2 * min(capability.historical_roi_avg / 10.0, 1.0)
        )
        base = capability.quality_score * capability.reliability_score
        return base * (1.0 + historical_bonus)

    def evaluate_capability(
        self,
        task: Task,
        state: State,
        capability: Capability,
    ) -> Tuple[bool, DecisionResult]:
        if task.task_type not in capability.supported_tasks:
            return False, DecisionResult(
                capability_id=capability.capability_id,
                provider=capability.provider,
                decision="skip",
                score=0.0,
                expected_roi=0.0,
                unit_cost=capability.unit_cost,
                reason="unsupported_task_type",
                metadata={},
            )

        if not state.need_external_support:
            return False, DecisionResult(
                capability_id=capability.capability_id,
                provider=capability.provider,
                decision="skip",
                score=0.0,
                expected_roi=0.0,
                unit_cost=capability.unit_cost,
                reason="external_support_not_needed",
                metadata={},
            )

        if state.remaining_budget <= 0 or state.spent >= task.budget_cap:
            return False, DecisionResult(
                capability_id=capability.capability_id,
                provider=capability.provider,
                decision="skip",
                score=0.0,
                expected_roi=0.0,
                unit_cost=capability.unit_cost,
                reason="no_budget",
                metadata={},
            )

        target_conf = max(task.target_confidence, self.policy.confidence_upgrade_trigger)
        if state.confidence >= target_conf:
            return False, DecisionResult(
                capability_id=capability.capability_id,
                provider=capability.provider,
                decision="skip",
                score=0.0,
                expected_roi=0.0,
                unit_cost=capability.unit_cost,
                reason="confidence_enough",
                metadata={"current_confidence": state.confidence, "target_confidence": target_conf},
            )

        if capability.unit_cost > state.remaining_budget:
            return False, DecisionResult(
                capability_id=capability.capability_id,
                provider=capability.provider,
                decision="skip",
                score=0.0,
                expected_roi=0.0,
                unit_cost=capability.unit_cost,
                reason="over_remaining_budget",
                metadata={"remaining_budget": state.remaining_budget},
            )

        if capability.unit_cost > task.expected_value * self.policy.max_budget_ratio:
            return False, DecisionResult(
                capability_id=capability.capability_id,
                provider=capability.provider,
                decision="skip",
                score=0.0,
                expected_roi=0.0,
                unit_cost=capability.unit_cost,
                reason="over_budget_ratio",
                metadata={"max_budget_ratio": self.policy.max_budget_ratio},
            )

        expected_roi = task.expected_value / max(capability.unit_cost, 0.001)
        if expected_roi < self.policy.min_expected_roi:
            return False, DecisionResult(
                capability_id=capability.capability_id,
                provider=capability.provider,
                decision="skip",
                score=0.0,
                expected_roi=round(expected_roi, 4),
                unit_cost=capability.unit_cost,
                reason="roi_too_low",
                metadata={"min_expected_roi": self.policy.min_expected_roi},
            )

        value_score = min(task.expected_value / 10.0, 1.0)
        confidence_gap = max(target_conf - state.confidence, 0.0)
        urgency_weight = 0.5 + task.urgency * 0.5
        risk_weight = self._risk_weight(task.risk_level)
        quality_weight = self._quality_weight(capability)
        cost_weight = capability.unit_cost / max(task.budget_cap, 0.01)
        latency_penalty = min(capability.latency_sec / 30.0, 0.5)

        raw_score = (
            value_score
            * confidence_gap
            * urgency_weight
            * risk_weight
            * quality_weight
            / max(cost_weight + latency_penalty, 0.01)
        )

        approval_mode = capability.approval_mode or ("auto" if capability.unit_cost <= self.policy.auto_buy_threshold else "manual")
        if raw_score < self.policy.min_procurement_score:
            return False, DecisionResult(
                capability_id=capability.capability_id,
                provider=capability.provider,
                decision="skip",
                score=round(raw_score, 4),
                expected_roi=round(expected_roi, 4),
                unit_cost=capability.unit_cost,
                reason="score_too_low",
                metadata={"approval_mode": approval_mode},
            )

        reason = f"buy_{approval_mode}"
        if task.risk_level == "high" and self.policy.high_risk_requires_double_verify:
            reason += "_double_verify"

        return True, DecisionResult(
            capability_id=capability.capability_id,
            provider=capability.provider,
            decision="buy",
            score=round(raw_score, 4),
            expected_roi=round(expected_roi, 4),
            unit_cost=capability.unit_cost,
            reason=reason,
            metadata={
                "approval_mode": approval_mode,
                "value_score": round(value_score, 4),
                "confidence_gap": round(confidence_gap, 4),
                "urgency_weight": round(urgency_weight, 4),
                "risk_weight": round(risk_weight, 4),
                "quality_weight": round(quality_weight, 4),
                "cost_weight": round(cost_weight, 4),
                "latency_penalty": round(latency_penalty, 4),
            },
        )

    def choose_capability(
        self,
        task: Task,
        state: State,
        capabilities: List[Capability],
        exclude_capability_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        exclude = set(exclude_capability_ids or [])
        decisions: List[DecisionResult] = []
        buy_candidates: List[DecisionResult] = []

        for capability in capabilities:
            if capability.capability_id in exclude:
                decisions.append(DecisionResult(
                    capability_id=capability.capability_id,
                    provider=capability.provider,
                    decision="skip",
                    score=0.0,
                    expected_roi=0.0,
                    unit_cost=capability.unit_cost,
                    reason="already_used_in_task",
                    metadata={},
                ))
                continue
            ok, result = self.evaluate_capability(task, state, capability)
            decisions.append(result)
            if ok:
                buy_candidates.append(result)

        buy_candidates.sort(key=lambda x: x.score, reverse=True)
        best = buy_candidates[0] if buy_candidates else None

        return {
            "task_id": task.task_id,
            "selected": asdict(best) if best else None,
            "buy_candidates": [asdict(x) for x in buy_candidates],
            "all_decisions": [asdict(x) for x in decisions],
        }


def load_json(path: Optional[str]) -> Dict[str, Any]:
    if not path:
        return {}
    return json.loads(Path(path).read_text())


def load_task(data: Dict[str, Any]) -> Task:
    return Task(**data)


def load_state(data: Dict[str, Any]) -> State:
    return State(**data)


def load_policy(data: Dict[str, Any]) -> Policy:
    return Policy(**data) if data else Policy()


def load_capabilities(data: List[Dict[str, Any]]) -> List[Capability]:
    return [Capability(**item) for item in data]


def demo_payload() -> Tuple[Task, State, Policy, List[Capability]]:
    task = Task(
        task_id="pm_breakout_001",
        task_type="market_verification",
        topic="Polymarket 异动验证",
        expected_value=6.5,
        urgency=0.9,
        risk_level="medium",
        budget_cap=0.10,
        target_confidence=0.60,
    )
    state = State(
        confidence=0.42,
        evidence_count=1,
        spent=0.00,
        remaining_budget=0.10,
        need_external_support=True,
    )
    policy = Policy(
        auto_buy_threshold=0.05,
        max_budget_ratio=0.15,
        min_expected_roi=2.0,
        confidence_upgrade_trigger=0.60,
        high_risk_requires_double_verify=True,
        min_procurement_score=0.15,
    )
    caps = [
        Capability(
            capability_id="cheap_news_search",
            category="search",
            provider="provider_a",
            unit_cost=0.01,
            latency_sec=2,
            quality_score=0.55,
            reliability_score=0.80,
            historical_success_rate=0.62,
            historical_confidence_delta_avg=0.10,
            historical_roi_avg=8.0,
            supported_tasks=["market_verification", "event_research"],
        ),
        Capability(
            capability_id="premium_news_verify",
            category="verification",
            provider="provider_b",
            unit_cost=0.03,
            latency_sec=4,
            quality_score=0.82,
            reliability_score=0.88,
            historical_success_rate=0.81,
            historical_confidence_delta_avg=0.18,
            historical_roi_avg=5.5,
            supported_tasks=["market_verification", "event_research"],
        ),
        Capability(
            capability_id="deep_reasoning_model",
            category="reasoning",
            provider="provider_c",
            unit_cost=0.08,
            latency_sec=10,
            quality_score=0.91,
            reliability_score=0.90,
            historical_success_rate=0.73,
            historical_confidence_delta_avg=0.22,
            historical_roi_avg=2.1,
            supported_tasks=["market_verification", "report_synthesis"],
        ),
    ]
    return task, state, policy, caps


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--task")
    p.add_argument("--state")
    p.add_argument("--caps")
    p.add_argument("--policy")
    p.add_argument("--demo", action="store_true")
    return p.parse_args()


def main() -> None:
    args = parse_args()

    if args.demo:
        task, state, policy, capabilities = demo_payload()
    else:
        if not (args.task and args.state and args.caps):
            raise SystemExit("Need --task --state --caps, or use --demo")
        task = load_task(load_json(args.task))
        state = load_state(load_json(args.state))
        policy = load_policy(load_json(args.policy))
        capabilities = load_capabilities(load_json(args.caps))

    engine = ProcurementEngine(policy)
    result = engine.choose_capability(task, state, capabilities)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
