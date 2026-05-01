#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from approval_queue import ApprovalQueue, ApprovalRequest


def main() -> None:
    queue = ApprovalQueue(Path(__file__).resolve().parent / "runtime" / "approval_queue.json")

    req = ApprovalRequest(
        request_id="apr_demo_001",
        task_id="pm_breakout_001",
        capability_id="deep_reasoning_model",
        expected_cost=0.08,
        expected_benefit="higher confidence on high-value verification task",
        reason="manual approval required for expensive capability",
    )
    added = queue.add(req)
    approved = queue.update_status(req.request_id, "approved", "demo approval granted")

    print(json.dumps({
        "added": added,
        "approved": approved,
        "all_requests": queue.list_all(),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
