#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from pathlib import Path

from core.data_adapter import DataAdapter
from core.mras_v2 import scan_features
from core.ops_rules import apply_cooldown, save_history
from core.portfolio_manager import apply_portfolio_caps

OUTPUT = Path("/Users/mac/.openclaw/workspace/polymarket/outputs/signals_v2_latest.json")
ALERT_OUTPUT = Path("/Users/mac/.openclaw/workspace/polymarket/outputs/signals_v2_alerts.json")
CONFIG_FILE = Path("/Users/mac/.openclaw/workspace/polymarket/trading_config.json")


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        return {}
    try:
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def main():
    adapter = DataAdapter()
    config = load_config()
    features = adapter.load_feature_markets()
    raw_signals = scan_features(features, config=config)
    portfolio_signals = apply_portfolio_caps(raw_signals)
    alert_signals = apply_cooldown(portfolio_signals)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(portfolio_signals, f, ensure_ascii=False, indent=2)
    with open(ALERT_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(alert_signals, f, ensure_ascii=False, indent=2)
    save_history(alert_signals)
    print(f"features={len(features)} raw_signals={len(raw_signals)} portfolio_signals={len(portfolio_signals)} alert_signals={len(alert_signals)} output={OUTPUT}")
    for sig in portfolio_signals[:10]:
        print(
            f"[{sig['regime']}] {sig['direction']} conf={sig['confidence']:.2f} pos={sig['position']} yes={sig['yes_price']:.4f} | {sig['question'][:70]}"
        )


if __name__ == "__main__":
    main()
