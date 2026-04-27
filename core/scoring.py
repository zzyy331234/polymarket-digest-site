#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Dict, List, Tuple


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def choose_position(confidence: float) -> str:
    if confidence >= 0.78:
        return "large"
    if confidence >= 0.64:
        return "medium"
    if confidence >= 0.52:
        return "small"
    return "skip"


def combine_scores(setup_score: float, edge_score: float, execution_score: float) -> float:
    return clamp(0.4 * setup_score + 0.4 * edge_score + 0.2 * execution_score)


def _merge_flags(*groups: List[str]) -> List[str]:
    merged: List[str] = []
    for group in groups:
        for flag in group or []:
            if flag and flag not in merged:
                merged.append(flag)
    return merged


def build_signal(
    feature: Dict,
    regime: str,
    direction: str,
    setup_score: float,
    edge_score: float,
    execution_score: float,
    reasons: List[str],
    risk_flags: List[str],
    advisory_flags: List[str] = None,
    blocking_flags: List[str] = None,
) -> Dict:
    confidence = combine_scores(setup_score, edge_score, execution_score)
    position = choose_position(confidence)
    risk_score = clamp(1.0 - execution_score)
    quality = clamp((setup_score + edge_score) / 2.0)
    advisory_flags = _merge_flags(advisory_flags if advisory_flags is not None else list(risk_flags))
    blocking_flags = _merge_flags(blocking_flags if blocking_flags is not None else [])
    risk_flags = _merge_flags(advisory_flags, blocking_flags)
    return {
        "token_id": feature["token_id"],
        "question": feature["question"],
        "slug": feature.get("slug"),
        "regime": regime,
        "direction": direction,
        "confidence": round(confidence, 4),
        "position": position,
        "quality": round(quality, 4),
        "risk_score": round(risk_score, 4),
        "reasons": reasons,
        "risk_flags": risk_flags,
        "advisory_flags": advisory_flags,
        "blocking_flags": blocking_flags,
        "yes_price": round(feature.get("yes_price", 0.0), 6),
        "no_price": round(feature.get("no_price", 0.0), 6),
        "liquidity": round(feature.get("liquidity", 0.0), 2),
        "volume": round(feature.get("volume", 0.0), 2),
        "chg_1h": feature.get("chg_1h"),
        "chg_4h": feature.get("chg_4h"),
        "chg_24h": feature.get("chg_24h"),
        "chg_7d": feature.get("chg_7d"),
        "latest_ts": feature.get("latest_ts"),
        "features": feature,
    }
