#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


VALID_TRANSITIONS: Dict[str, List[str]] = {
    "created": ["assessing", "aborted"],
    "assessing": ["discovering", "completed", "aborted"],
    "discovering": ["deciding", "fallback", "aborted"],
    "deciding": ["awaiting_approval", "executing", "completed", "fallback", "aborted"],
    "awaiting_approval": ["executing", "fallback", "aborted"],
    "executing": ["evaluating_outcome", "fallback", "aborted"],
    "evaluating_outcome": ["discovering", "deciding", "completed", "fallback", "aborted"],
    "fallback": ["discovering", "deciding", "aborted", "completed"],
    "completed": [],
    "aborted": [],
}


@dataclass
class TransitionRecord:
    from_state: str
    to_state: str
    reason: str = ""


@dataclass
class ProcurementStateMachine:
    state: str = "created"
    history: List[TransitionRecord] = field(default_factory=list)

    def can_transition(self, to_state: str) -> bool:
        return to_state in VALID_TRANSITIONS.get(self.state, [])

    def transition(self, to_state: str, reason: str = "") -> None:
        if not self.can_transition(to_state):
            raise ValueError(f"Invalid transition: {self.state} -> {to_state}")
        self.history.append(TransitionRecord(from_state=self.state, to_state=to_state, reason=reason))
        self.state = to_state

    def to_dict(self) -> Dict:
        return {
            "state": self.state,
            "history": [
                {"from_state": h.from_state, "to_state": h.to_state, "reason": h.reason}
                for h in self.history
            ],
        }


def run_happy_path(needs_external_support: bool = True, requires_manual_approval: bool = False) -> ProcurementStateMachine:
    sm = ProcurementStateMachine()
    sm.transition("assessing", "task received")

    if not needs_external_support:
        sm.transition("completed", "local workflow was sufficient")
        return sm

    sm.transition("discovering", "external support required")
    sm.transition("deciding", "candidate capabilities discovered")

    if requires_manual_approval:
        sm.transition("awaiting_approval", "cost or policy requires manual approval")

    sm.transition("executing", "selected capability approved")
    sm.transition("evaluating_outcome", "procurement executed")
    sm.transition("completed", "confidence target reached or task advanced")
    return sm
