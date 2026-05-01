#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat()


@dataclass
class Task:
    task_id: str
    task_type: str
    topic: str
    expected_value: float
    urgency: float
    risk_level: str
    budget_cap: float
    target_confidence: float = 0.60
    description: str = ""
    created_at: str = field(default_factory=now_iso)
    context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class State:
    confidence: float
    evidence_count: int
    spent: float
    remaining_budget: float
    need_external_support: bool = True
    current_stage: str = "initial_screening"
    selected_capabilities: List[str] = field(default_factory=list)
    blocked_reasons: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Capability:
    capability_id: str
    category: str
    provider: str
    unit_cost: float
    latency_sec: float
    quality_score: float
    reliability_score: float
    supported_tasks: List[str]
    name: str = ""
    provider_type: str = "api"
    currency: str = "USD"
    trust_score: float = 1.0
    approval_mode: str = "auto"
    cost_class: str = "low"
    historical_success_rate: float = 0.5
    historical_confidence_delta_avg: float = 0.0
    historical_roi_avg: float = 1.0
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Policy:
    auto_buy_threshold: float = 0.05
    max_budget_ratio: float = 0.15
    min_expected_roi: float = 2.0
    confidence_upgrade_trigger: float = 0.60
    high_risk_requires_double_verify: bool = True
    min_procurement_score: float = 0.15
    policy_id: str = "default_v0"
    blocked_providers: List[str] = field(default_factory=list)
    allowed_currencies: List[str] = field(default_factory=lambda: ["USD", "USDC"])
    allowed_networks: List[str] = field(default_factory=lambda: ["base"])
    manual_review_threshold: float = 0.05
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DecisionRecord:
    task_id: str
    selected: Optional[Dict[str, Any]]
    buy_candidates: List[Dict[str, Any]]
    all_decisions: List[Dict[str, Any]]
    created_at: str = field(default_factory=now_iso)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class OutcomeRecord:
    task_id: str
    capability_id: str
    executed: bool
    actual_cost: float
    confidence_before: float
    confidence_after: float
    notes: str = ""
    created_at: str = field(default_factory=now_iso)

    @property
    def confidence_delta(self) -> float:
        return round(self.confidence_after - self.confidence_before, 4)

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["confidence_delta"] = self.confidence_delta
        return payload
