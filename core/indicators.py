#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from math import sqrt
from statistics import pstdev
from typing import List, Optional, Sequence, Tuple


PricePoint = Tuple[str, float]


def pct_change(current: Optional[float], reference: Optional[float]) -> Optional[float]:
    if current is None or reference is None or reference == 0:
        return None
    try:
        return (float(current) - float(reference)) / float(reference)
    except Exception:
        return None


def nearest_price_at_or_before(points: Sequence[PricePoint], target_ts: str) -> Optional[float]:
    """points must be sorted ascending by timestamp (ISO format)."""
    candidate = None
    for ts, price in points:
        if ts <= target_ts:
            candidate = price
        else:
            break
    return candidate


def rolling_percentile(current: Optional[float], values: Sequence[float]) -> Optional[float]:
    if current is None:
        return None
    clean = [float(v) for v in values if v is not None]
    if len(clean) < 5:
        return None
    less_equal = sum(1 for v in clean if v <= current)
    return less_equal / len(clean)


def compute_rsi(prices: Sequence[float], period: int = 14) -> Optional[float]:
    clean = [float(p) for p in prices if p is not None]
    if len(clean) < period + 1:
        return None
    deltas = [clean[i] - clean[i - 1] for i in range(1, len(clean))]
    gains = [max(d, 0.0) for d in deltas]
    losses = [max(-d, 0.0) for d in deltas]
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    for i in range(period, len(deltas)):
        avg_gain = ((avg_gain * (period - 1)) + gains[i]) / period
        avg_loss = ((avg_loss * (period - 1)) + losses[i]) / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100.0 - (100.0 / (1.0 + rs))


def compute_volatility(changes: Sequence[float]) -> Optional[float]:
    clean = [float(c) for c in changes if c is not None]
    if len(clean) < 5:
        return None
    return pstdev(clean)


def compute_slope(values: Sequence[float]) -> Optional[float]:
    clean = [float(v) for v in values if v is not None]
    n = len(clean)
    if n < 3:
        return None
    xs = list(range(n))
    mean_x = sum(xs) / n
    mean_y = sum(clean) / n
    denom = sum((x - mean_x) ** 2 for x in xs)
    if denom == 0:
        return None
    numer = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, clean))
    return numer / denom


def simple_noise_score(changes: Sequence[float]) -> Optional[float]:
    clean = [abs(float(c)) for c in changes if c is not None]
    if len(clean) < 5:
        return None
    avg = sum(clean) / len(clean)
    if avg == 0:
        return 0.0
    vol = pstdev(clean)
    return vol / avg if avg else None
