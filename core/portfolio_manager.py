#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import defaultdict
from typing import Dict, List

CLUSTER_KEYWORDS = {
    "world_cup": ["fifa world cup", "world cup"],
    "us_election": ["presidential nomination", "presidential election", "democratic nomination", "republican nomination", "2028"],
    "gta_vi": ["gta vi"],
    "crypto_launch": ["market cap", "fdv", "launch", "token"],
}

REGIME_CAPS = {
    "carry_no": 20,
    "trend": 40,
    "mean_revert": 20,
    "contrarian": 10,
}

CLUSTER_CAPS = {
    "world_cup": 12,
    "us_election": 12,
    "gta_vi": 6,
    "crypto_launch": 8,
    "other": 20,
}


def classify_cluster(question: str) -> str:
    q = (question or "").lower()
    for cluster, keywords in CLUSTER_KEYWORDS.items():
        if any(k in q for k in keywords):
            return cluster
    return "other"


def apply_portfolio_caps(signals: List[Dict]) -> List[Dict]:
    kept: List[Dict] = []
    cluster_count = defaultdict(int)
    regime_count = defaultdict(int)

    for sig in signals:
        regime = sig.get("regime", "other")
        cluster = classify_cluster(sig.get("question", ""))

        if regime_count[regime] >= REGIME_CAPS.get(regime, 15):
            continue
        if cluster_count[cluster] >= CLUSTER_CAPS.get(cluster, 10):
            continue

        sig = dict(sig)
        sig["cluster"] = cluster
        sig.setdefault("advisory_flags", [])
        sig.setdefault("blocking_flags", [])
        sig["risk_flags"] = list(dict.fromkeys(sig.get("advisory_flags", []) + sig.get("blocking_flags", [])))
        sig.setdefault("reasons", [])
        sig["reasons"].append(f"cluster={cluster}")
        kept.append(sig)
        regime_count[regime] += 1
        cluster_count[cluster] += 1

    return kept
