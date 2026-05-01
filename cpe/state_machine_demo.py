#!/usr/bin/env python3
from __future__ import annotations

import json

from state_machine import run_happy_path


def main() -> None:
    auto_flow = run_happy_path(needs_external_support=True, requires_manual_approval=False)
    manual_flow = run_happy_path(needs_external_support=True, requires_manual_approval=True)
    local_only = run_happy_path(needs_external_support=False, requires_manual_approval=False)

    print(json.dumps({
        "auto_flow": auto_flow.to_dict(),
        "manual_flow": manual_flow.to_dict(),
        "local_only": local_only.to_dict(),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
