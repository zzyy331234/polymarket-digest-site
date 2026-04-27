#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

HISTORY_FILE = Path("/Users/mac/.openclaw/workspace/polymarket/outputs/signals_v2_history.jsonl")
COOLDOWN_HOURS = 6


def _parse_ts(value: str):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except Exception:
        return None


def load_recent_history(hours: int = 48) -> List[Dict]:
    if not HISTORY_FILE.exists():
        return []
    cutoff = datetime.now() - timedelta(hours=hours)
    rows: List[Dict] = []
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            ts = _parse_ts(obj.get("saved_at"))
            if ts and ts >= cutoff:
                rows.append(obj)
    return rows


def apply_cooldown(signals: List[Dict], cooldown_hours: int = COOLDOWN_HOURS) -> List[Dict]:
    recent = load_recent_history(hours=max(48, cooldown_hours * 2))
    last_seen = {}
    for row in recent:
        key = (row.get("token_id"), row.get("direction"), row.get("regime"))
        ts = _parse_ts(row.get("saved_at"))
        if ts and (key not in last_seen or ts > last_seen[key]):
            last_seen[key] = ts

    now = datetime.now()
    out: List[Dict] = []
    for sig in signals:
        key = (sig.get("token_id"), sig.get("direction"), sig.get("regime"))
        prev = last_seen.get(key)
        sig = dict(sig)
        if prev and (now - prev).total_seconds() < cooldown_hours * 3600:
            advisory = list(sig.get("advisory_flags", []))
            blocking = list(sig.get("blocking_flags", []))
            if "cooldown_active" not in advisory:
                advisory.append("cooldown_active")
            sig["advisory_flags"] = advisory
            sig["blocking_flags"] = blocking
            sig["risk_flags"] = list(dict.fromkeys(advisory + blocking))
        out.append(sig)
    return out


def save_history(signals: List[Dict]):
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    saved_at = datetime.now().isoformat(timespec="seconds")
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        for sig in signals:
            row = {
                "saved_at": saved_at,
                "token_id": sig.get("token_id"),
                "question": sig.get("question"),
                "slug": sig.get("slug"),
                "cluster": sig.get("cluster"),
                "regime": sig.get("regime"),
                "direction": sig.get("direction"),
                "confidence": sig.get("confidence"),
                "yes_price": sig.get("yes_price"),
                "latest_ts": sig.get("latest_ts"),
                "event_time": sig.get("event_time") or sig.get("end_date_iso"),
            }
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
