#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MRAS-Lite Backtest v1
=====================

目标：
- 基于 collector SQLite 原始数据生成 15m close bars
- 过滤低质量 bar（默认每根 bar 至少 10 个原始样本）
- 按连续 15m 段做回测，自动切断缺口污染
- 仅使用 1h / 4h / 24h + slope + liquidity + hours_to_event 等短窗特征
- 不依赖 7d 窗口和 ta_snapshots

输出：
- outputs/backtest_mras_lite_v1_summary.json
- outputs/backtest_mras_lite_v1_summary.md
- outputs/backtest_mras_lite_v1_signals.jsonl
"""

from __future__ import annotations

import argparse
import json
import math
import sqlite3
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from statistics import median
from typing import Dict, Iterable, List, Optional, Tuple

from core.indicators import (
    compute_rsi,
    compute_slope,
    pct_change,
    rolling_percentile,
    simple_noise_score,
)
from core.scoring import build_signal, clamp

BASE_DIR = Path("/Users/mac/.openclaw/workspace/polymarket")
DB_PATH = BASE_DIR / "collector" / "polymarket_data.db"
OUTPUT_DIR = BASE_DIR / "outputs"

BAR_MINUTES = 15
BAR_DELTA = timedelta(minutes=BAR_MINUTES)
HORIZONS = {
    "4h": 16,
    "12h": 48,
    "24h": 96,
}
HORIZON_TOLERANCE = {
    "4h": timedelta(hours=2),
    "12h": timedelta(hours=4),
    "24h": timedelta(hours=6),
}


@dataclass
class RawPoint:
    ts: datetime
    yes_price: float


@dataclass
class Bar:
    ts: datetime
    close: float
    samples: int
    segment_id: int
    idx_in_segment: int


@dataclass
class MarketMeta:
    token_id: str
    question: str
    slug: Optional[str]
    liquidity: float
    volume: float
    event_time: Optional[str]


def iso(dt: datetime) -> str:
    return dt.replace(microsecond=0).isoformat()


def parse_dt(text: Optional[str]) -> Optional[datetime]:
    if not text:
        return None
    try:
        return datetime.fromisoformat(str(text).replace("Z", "+00:00"))
    except Exception:
        return None


def floor_to_bar(ts: datetime, minutes: int = BAR_MINUTES) -> datetime:
    floored_minute = (ts.minute // minutes) * minutes
    return ts.replace(minute=floored_minute, second=0, microsecond=0)


def load_markets(conn: sqlite3.Connection, min_liquidity: float) -> List[MarketMeta]:
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    rows = cur.execute(
        """
        SELECT token_id,
               question,
               slug,
               liquidity,
               volume,
               COALESCE(event_time, close_time, end_date_iso) AS event_time
        FROM markets
        WHERE liquidity >= ?
        ORDER BY liquidity DESC, volume DESC, token_id ASC
        """,
        (min_liquidity,),
    ).fetchall()
    return [
        MarketMeta(
            token_id=row["token_id"],
            question=row["question"] or row["slug"] or row["token_id"],
            slug=row["slug"],
            liquidity=float(row["liquidity"] or 0.0),
            volume=float(row["volume"] or 0.0),
            event_time=row["event_time"],
        )
        for row in rows
    ]


def load_raw_points(conn: sqlite3.Connection, token_id: str) -> List[RawPoint]:
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    rows = cur.execute(
        """
        SELECT timestamp, yes_price
        FROM price_history
        WHERE token_id = ?
          AND yes_price IS NOT NULL
        ORDER BY timestamp ASC
        """,
        (token_id,),
    ).fetchall()
    out: List[RawPoint] = []
    for row in rows:
        try:
            price = float(row["yes_price"])
            if price <= 0 or price >= 1:
                continue
            out.append(RawPoint(ts=datetime.fromisoformat(row["timestamp"]), yes_price=price))
        except Exception:
            continue
    return out


def aggregate_bars(points: List[RawPoint]) -> List[Bar]:
    if not points:
        return []

    buckets: List[Tuple[datetime, List[RawPoint]]] = []
    current_bucket_ts = floor_to_bar(points[0].ts)
    current_items: List[RawPoint] = []

    for p in points:
        bucket_ts = floor_to_bar(p.ts)
        if bucket_ts != current_bucket_ts:
            buckets.append((current_bucket_ts, current_items))
            current_bucket_ts = bucket_ts
            current_items = [p]
        else:
            current_items.append(p)
    if current_items:
        buckets.append((current_bucket_ts, current_items))

    bars: List[Bar] = []
    segment_id = -1
    prev_ts: Optional[datetime] = None
    idx_in_segment = -1
    for bucket_ts, items in buckets:
        samples = len(items)
        close = items[-1].yes_price
        if prev_ts is None or (bucket_ts - prev_ts) != BAR_DELTA:
            segment_id += 1
            idx_in_segment = 0
        else:
            idx_in_segment += 1
        bars.append(
            Bar(
                ts=bucket_ts,
                close=close,
                samples=samples,
                segment_id=segment_id,
                idx_in_segment=idx_in_segment,
            )
        )
        prev_ts = bucket_ts
    return bars


def segment_bars(bars: List[Bar]) -> Dict[int, List[Bar]]:
    segments: Dict[int, List[Bar]] = defaultdict(list)
    for bar in bars:
        segments[bar.segment_id].append(bar)
    return segments


def hours_to_event(event_time: Optional[str], current_ts: datetime) -> Optional[float]:
    if not event_time:
        return None
    event_dt = parse_dt(event_time)
    if not event_dt:
        return None
    if event_dt.tzinfo is None:
        event_dt = event_dt.replace(tzinfo=timezone.utc)
    current_utc = current_ts.replace(tzinfo=timezone.utc)
    return (event_dt - current_utc).total_seconds() / 3600.0


def build_feature(
    meta: MarketMeta,
    segment: List[Bar],
    idx: int,
    recent_pct_bars: int,
    min_samples_per_bar: int,
    min_quality_ratio: float,
) -> Optional[Dict]:
    if idx < 96:
        return None

    cur = segment[idx]
    yes_price = cur.close
    if yes_price <= 0 or yes_price >= 1:
        return None

    recent_24h_bars = segment[idx - 95 : idx + 1]
    quality_hits = sum(1 for b in recent_24h_bars if b.samples >= min_samples_per_bar)
    quality_ratio = quality_hits / len(recent_24h_bars)
    if cur.samples < min_samples_per_bar:
        return None
    if quality_ratio < min_quality_ratio:
        return None

    ref_1h = segment[idx - 4].close
    ref_4h = segment[idx - 16].close
    ref_24h = segment[idx - 96].close

    recent_4h = [b.close for b in segment[idx - 15 : idx + 1]]
    recent_24h = [b.close for b in recent_24h_bars]
    recent_pct_window = [b.close for b in segment[max(0, idx - recent_pct_bars + 1) : idx + 1]]

    changes: List[float] = []
    start_idx = max(1, idx - 48)
    for i in range(start_idx, idx + 1):
        chg = pct_change(segment[i].close, segment[i - 1].close)
        if chg is not None:
            changes.append(chg)

    feature = {
        "token_id": meta.token_id,
        "question": meta.question,
        "slug": meta.slug,
        "yes_price": float(yes_price),
        "no_price": float(1.0 - yes_price),
        "liquidity": float(meta.liquidity),
        "volume": float(meta.volume),
        "latest_ts": iso(cur.ts),
        "history_points": idx + 1,
        "chg_1h": pct_change(yes_price, ref_1h),
        "chg_4h": pct_change(yes_price, ref_4h),
        "chg_24h": pct_change(yes_price, ref_24h),
        "chg_7d": None,
        "rsi_14": compute_rsi(recent_24h, 14),
        "volatility": None,
        "trend_slope_4h": compute_slope(recent_4h),
        "trend_slope_24h": compute_slope(recent_24h),
        "pct_rank_7d": rolling_percentile(yes_price, recent_pct_window),
        "pct_rank_recent": rolling_percentile(yes_price, recent_pct_window),
        "noise_score": simple_noise_score(changes),
        "hours_to_event": hours_to_event(meta.event_time, cur.ts),
        "event_time": meta.event_time,
        "spread": None,
        "entry_samples": cur.samples,
        "quality_ratio_24h": quality_ratio,
    }
    return feature


def evaluate_mras_lite(feature: Dict) -> Optional[Dict]:
    yes_price = feature.get("yes_price") or 0.0
    liquidity = feature.get("liquidity") or 0.0
    chg_4h = feature.get("chg_4h")
    chg_24h = feature.get("chg_24h")
    rsi = feature.get("rsi_14")
    pct_rank = feature.get("pct_rank_recent")
    slope_4h = feature.get("trend_slope_4h")
    slope_24h = feature.get("trend_slope_24h")
    noise = feature.get("noise_score")
    hours_evt = feature.get("hours_to_event")

    advisory_flags: List[str] = []
    blocking_flags: List[str] = []

    if liquidity < 20000:
        return None
    if hours_evt is not None:
        if hours_evt <= 6:
            return None
        if hours_evt <= 24:
            advisory_flags.append("event_near")
            blocking_flags.append("event_near")
        elif hours_evt <= 48:
            advisory_flags.append("event_soon")
    if noise is not None and noise > 2.5:
        advisory_flags.append("high_noise")
        blocking_flags.append("high_noise")

    # 1) carry_no
    if yes_price <= 0.03:
        setup = 0.85 if liquidity >= 50000 else 0.65
        edge = 0.55 if (chg_24h is None or abs(chg_24h) < 0.03) else 0.35
        execution = 0.75
        if "event_near" in advisory_flags:
            execution -= 0.25
        elif "event_soon" in advisory_flags:
            execution -= 0.12
        return build_signal(
            feature,
            regime="carry_no",
            direction="NO",
            setup_score=setup,
            edge_score=edge,
            execution_score=execution,
            reasons=["ultra low YES price", "carry_no lite"],
            risk_flags=advisory_flags + blocking_flags,
            advisory_flags=advisory_flags,
            blocking_flags=blocking_flags,
        )

    # 2) trend lite（只用 4h/24h）
    trend_hits = 0
    reasons: List[str] = []
    local_advisory = list(advisory_flags)
    local_blocking = list(blocking_flags)

    if chg_4h is not None and abs(chg_4h) >= 0.02:
        trend_hits += 1
        reasons.append("4h move visible")
    if chg_24h is not None and abs(chg_24h) >= 0.05:
        trend_hits += 1
        reasons.append("24h move strong")
    if chg_4h is not None and chg_24h is not None and chg_4h * chg_24h > 0:
        trend_hits += 1
        reasons.append("4h and 24h aligned")
    if slope_4h is not None and slope_24h is not None and slope_4h * slope_24h > 0:
        trend_hits += 1
        reasons.append("4h and 24h slope aligned")
    if liquidity >= 50000:
        trend_hits += 1
        reasons.append("liquidity good")

    if trend_hits >= 4 and chg_24h is not None:
        direction = "YES" if chg_24h > 0 else "NO"
        setup = clamp(0.55 + (0.15 if liquidity >= 100000 else 0.0))
        edge = clamp(0.42 + min(abs(chg_24h) * 2.3, 0.23))
        execution = 0.75
        if "event_near" in local_advisory:
            execution -= 0.22
        elif "event_soon" in local_advisory:
            execution -= 0.10
        if noise is not None and noise > 1.8:
            execution -= 0.15
            local_advisory.append("trend_noisy")
            local_blocking.append("trend_noisy")
        return build_signal(
            feature,
            "trend",
            direction,
            setup,
            edge,
            execution,
            reasons,
            local_advisory + local_blocking,
            advisory_flags=local_advisory,
            blocking_flags=local_blocking,
        )

    # 3) mean_revert lite（recent percentile，不标称7d）
    mr_reasons: List[str] = []
    if pct_rank is not None and ((pct_rank <= 0.10) or (pct_rank >= 0.90)):
        edge = 0.45
        if rsi is not None and (rsi <= 35 or rsi >= 65):
            edge += 0.15
            mr_reasons.append("RSI extreme")
        if chg_24h is not None and abs(chg_24h) >= 0.03:
            edge += 0.10
            mr_reasons.append("24h move extended")
        direction = None
        if pct_rank <= 0.10:
            direction = "YES"
            mr_reasons.insert(0, "recent lower percentile bounce")
        elif pct_rank >= 0.90:
            direction = "NO"
            mr_reasons.insert(0, "recent upper percentile fade")
        if direction:
            return build_signal(
                feature,
                "mean_revert",
                direction,
                setup_score=0.62,
                edge_score=clamp(edge),
                execution_score=0.68 if "event_near" not in advisory_flags else 0.42,
                reasons=mr_reasons,
                risk_flags=advisory_flags + blocking_flags,
                advisory_flags=advisory_flags,
                blocking_flags=blocking_flags,
            )

    # 4) contrarian lite
    con_reasons: List[str] = []
    if yes_price >= 0.65 and chg_24h is not None and chg_24h < -0.03:
        edge = 0.55
        if rsi is not None and rsi < 55:
            edge += 0.05
            con_reasons.append("RSI not overheated")
        return build_signal(
            feature,
            "contrarian",
            "NO",
            setup_score=0.66,
            edge_score=clamp(edge),
            execution_score=0.62 if "event_near" not in advisory_flags else 0.40,
            reasons=["crowded YES fading"] + con_reasons,
            risk_flags=advisory_flags + blocking_flags,
            advisory_flags=advisory_flags,
            blocking_flags=blocking_flags,
        )

    return None


def compute_outcome(entry_yes: float, future_yes: float, direction: str) -> Dict[str, float]:
    if direction == "YES":
        edge = future_yes - entry_yes
        denom = entry_yes
    else:
        edge = entry_yes - future_yes
        denom = 1.0 - entry_yes
    roi = edge / denom if denom and denom > 0 else 0.0
    return {
        "edge": round(edge, 6),
        "roi": round(roi, 6),
        "hit": edge > 0,
    }


def find_future_bar(bars: List[Bar], start_idx: int, label: str) -> Optional[Bar]:
    target_ts = bars[start_idx].ts + (BAR_DELTA * HORIZONS[label])
    tolerance = HORIZON_TOLERANCE[label]
    for j in range(start_idx + 1, len(bars)):
        if bars[j].ts >= target_ts:
            if bars[j].ts <= target_ts + tolerance:
                return bars[j]
            return None
    return None


def max_consecutive_losses(items: List[Dict], horizon: str) -> int:
    streak = 0
    max_streak = 0
    for row in sorted(items, key=lambda x: x["entry_ts"]):
        out = row.get("outcomes", {}).get(horizon)
        if not out:
            continue
        if out["hit"]:
            streak = 0
        else:
            streak += 1
            max_streak = max(max_streak, streak)
    return max_streak


def summarize_horizon(items: List[Dict], horizon: str) -> Dict:
    subset = [row for row in items if row.get("outcomes", {}).get(horizon)]
    if not subset:
        return {
            "count": 0,
            "hit_rate": None,
            "avg_edge": None,
            "median_edge": None,
            "avg_roi": None,
            "median_roi": None,
            "max_consecutive_losses": None,
        }
    edges = [row["outcomes"][horizon]["edge"] for row in subset]
    rois = [row["outcomes"][horizon]["roi"] for row in subset]
    hits = [1 if row["outcomes"][horizon]["hit"] else 0 for row in subset]
    return {
        "count": len(subset),
        "hit_rate": round(sum(hits) / len(hits), 4),
        "avg_edge": round(sum(edges) / len(edges), 6),
        "median_edge": round(median(edges), 6),
        "avg_roi": round(sum(rois) / len(rois), 6),
        "median_roi": round(median(rois), 6),
        "max_consecutive_losses": max_consecutive_losses(subset, horizon),
    }


def summarize_by_regime(items: List[Dict], horizon: str) -> Dict[str, Dict]:
    grouped: Dict[str, List[Dict]] = defaultdict(list)
    for row in items:
        grouped[row["regime"]].append(row)
    return {regime: summarize_horizon(rows, horizon) for regime, rows in sorted(grouped.items())}


def backtest(
    min_liquidity: float,
    min_samples_per_bar: int,
    min_quality_ratio: float,
    recent_pct_bars: int,
    max_markets: int = 0,
) -> Dict:
    conn = sqlite3.connect(DB_PATH)
    markets = load_markets(conn, min_liquidity=min_liquidity)
    if max_markets > 0:
        markets = markets[:max_markets]

    all_rows: List[Dict] = []
    quality_stats = {
        "markets_scanned": len(markets),
        "markets_with_bars": 0,
        "markets_with_signals": 0,
        "segments_total": 0,
        "segments_ge_24h": 0,
        "bars_total": 0,
    }

    for idx_market, meta in enumerate(markets, start=1):
        points = load_raw_points(conn, meta.token_id)
        bars = aggregate_bars(points)
        if not bars:
            continue
        quality_stats["markets_with_bars"] += 1
        quality_stats["bars_total"] += len(bars)
        segments = segment_bars(bars)
        quality_stats["segments_total"] += len(segments)

        market_signal_count = 0

        global_idx_by_ts = {bar.ts: pos for pos, bar in enumerate(bars)}

        for segment_id, seg in segments.items():
            if len(seg) >= 97:
                quality_stats["segments_ge_24h"] += 1
            if len(seg) < 97:
                continue
            for i in range(96, len(seg)):
                feature = build_feature(
                    meta,
                    seg,
                    i,
                    recent_pct_bars=recent_pct_bars,
                    min_samples_per_bar=min_samples_per_bar,
                    min_quality_ratio=min_quality_ratio,
                )
                if not feature:
                    continue
                signal = evaluate_mras_lite(feature)
                if not signal or signal.get("position") == "skip":
                    continue

                entry_bar = seg[i]
                global_idx = global_idx_by_ts.get(entry_bar.ts)
                if global_idx is None:
                    continue

                row = {
                    "token_id": meta.token_id,
                    "question": meta.question,
                    "slug": meta.slug,
                    "entry_ts": iso(entry_bar.ts),
                    "entry_yes_price": round(entry_bar.close, 6),
                    "entry_samples": feature["entry_samples"],
                    "quality_ratio_24h": round(feature["quality_ratio_24h"], 4),
                    "regime": signal["regime"],
                    "direction": signal["direction"],
                    "confidence": signal["confidence"],
                    "position": signal["position"],
                    "liquidity": round(meta.liquidity, 2),
                    "volume": round(meta.volume, 2),
                    "hours_to_event": round(feature["hours_to_event"], 4) if feature.get("hours_to_event") is not None else None,
                    "features": {
                        "chg_1h": signal.get("chg_1h"),
                        "chg_4h": signal.get("chg_4h"),
                        "chg_24h": signal.get("chg_24h"),
                        "pct_rank_recent": feature.get("pct_rank_recent"),
                        "rsi_14": feature.get("rsi_14"),
                        "trend_slope_4h": feature.get("trend_slope_4h"),
                        "trend_slope_24h": feature.get("trend_slope_24h"),
                        "noise_score": feature.get("noise_score"),
                    },
                    "reasons": signal.get("reasons", []),
                    "risk_flags": signal.get("risk_flags", []),
                    "outcomes": {},
                }

                for label in HORIZONS:
                    future_bar = find_future_bar(bars, global_idx, label)
                    if not future_bar:
                        continue
                    row["outcomes"][label] = compute_outcome(entry_bar.close, future_bar.close, signal["direction"])
                    row["outcomes"][label]["future_yes_price"] = round(future_bar.close, 6)
                    row["outcomes"][label]["future_ts"] = iso(future_bar.ts)

                if not row["outcomes"]:
                    continue

                all_rows.append(row)
                market_signal_count += 1

        if market_signal_count > 0:
            quality_stats["markets_with_signals"] += 1

        if idx_market % 25 == 0:
            print(f"progress {idx_market}/{len(markets)} markets | signals={len(all_rows)}")

    conn.close()

    regime_counter = Counter(row["regime"] for row in all_rows)
    position_counter = Counter(row["position"] for row in all_rows)
    direction_counter = Counter(row["direction"] for row in all_rows)

    summary = {
        "generated_at": iso(datetime.now()),
        "config": {
            "db_path": str(DB_PATH),
            "min_liquidity": min_liquidity,
            "min_samples_per_bar": min_samples_per_bar,
            "min_quality_ratio": min_quality_ratio,
            "recent_pct_bars": recent_pct_bars,
            "bar_minutes": BAR_MINUTES,
            "horizons": HORIZONS,
            "max_markets": max_markets,
        },
        "quality": quality_stats,
        "signals": {
            "total": len(all_rows),
            "by_regime": dict(sorted(regime_counter.items())),
            "by_position": dict(sorted(position_counter.items())),
            "by_direction": dict(sorted(direction_counter.items())),
        },
        "performance": {
            label: summarize_horizon(all_rows, label) for label in HORIZONS
        },
        "performance_by_regime": {
            label: summarize_by_regime(all_rows, label) for label in HORIZONS
        },
        "top_examples": sorted(
            all_rows,
            key=lambda x: (
                x["confidence"],
                x.get("outcomes", {}).get("24h", {}).get("roi", x.get("outcomes", {}).get("12h", {}).get("roi", x.get("outcomes", {}).get("4h", {}).get("roi", -999))),
            ),
            reverse=True,
        )[:20],
    }
    return {
        "summary": summary,
        "rows": all_rows,
    }


def render_markdown(summary: Dict) -> str:
    lines: List[str] = []
    lines.append("# MRAS-Lite 回测结果 v1")
    lines.append("")
    lines.append(f"生成时间：{summary['generated_at']}")
    lines.append("")
    lines.append("## 配置")
    cfg = summary["config"]
    lines.append("")
    lines.append(f"- 数据库：`{cfg['db_path']}`")
    lines.append(f"- 最低流动性：`{cfg['min_liquidity']}`")
    lines.append(f"- 15m bar 最低样本数：`{cfg['min_samples_per_bar']}`")
    lines.append(f"- recent percentile 窗口：`{cfg['recent_pct_bars']}` bars")
    lines.append(f"- 最近 24h 高质量 bar 比例门槛：`{cfg['min_quality_ratio']}`")
    if cfg.get("max_markets"):
        lines.append(f"- 限制市场数：`{cfg['max_markets']}`")
    lines.append("")
    lines.append("## 数据质量")
    lines.append("")
    q = summary["quality"]
    for key in [
        "markets_scanned",
        "markets_with_bars",
        "markets_with_signals",
        "segments_total",
        "segments_ge_24h",
        "bars_total",
    ]:
        lines.append(f"- {key}: **{q[key]}**")
    lines.append("")
    lines.append("## 信号概览")
    lines.append("")
    sig = summary["signals"]
    lines.append(f"- 总信号数：**{sig['total']}**")
    lines.append(f"- Regime 分布：`{json.dumps(sig['by_regime'], ensure_ascii=False)}`")
    lines.append(f"- 仓位分布：`{json.dumps(sig['by_position'], ensure_ascii=False)}`")
    lines.append(f"- 方向分布：`{json.dumps(sig['by_direction'], ensure_ascii=False)}`")
    lines.append("")
    lines.append("## 总体表现")
    lines.append("")
    for label, perf in summary["performance"].items():
        lines.append(f"### {label}")
        lines.append("")
        for k in [
            "count",
            "hit_rate",
            "avg_edge",
            "median_edge",
            "avg_roi",
            "median_roi",
            "max_consecutive_losses",
        ]:
            lines.append(f"- {k}: **{perf[k]}**")
        lines.append("")
    lines.append("## 分 Regime 表现")
    lines.append("")
    for label, regimes in summary["performance_by_regime"].items():
        lines.append(f"### {label}")
        lines.append("")
        for regime, perf in regimes.items():
            lines.append(
                f"- **{regime}**: count={perf['count']}, hit_rate={perf['hit_rate']}, avg_roi={perf['avg_roi']}, max_consecutive_losses={perf['max_consecutive_losses']}"
            )
        lines.append("")
    lines.append("## Top Examples")
    lines.append("")
    for row in summary["top_examples"][:10]:
        lines.append(
            f"- [{row['regime']}] {row['direction']} conf={row['confidence']} 24h_roi={row['outcomes']['24h']['roi']} | {row['question']} | {row['entry_ts']}"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="MRAS-Lite 回测 v1")
    parser.add_argument("--min-liquidity", type=float, default=20000)
    parser.add_argument("--min-samples-per-bar", type=int, default=10)
    parser.add_argument("--recent-pct-bars", type=int, default=96, help="recent percentile window (bars)")
    parser.add_argument("--min-quality-ratio", type=float, default=0.7, help="required ratio of qualified bars over recent 24h window")
    parser.add_argument("--max-markets", type=int, default=0, help="0 = all")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    result = backtest(
        min_liquidity=args.min_liquidity,
        min_samples_per_bar=args.min_samples_per_bar,
        min_quality_ratio=args.min_quality_ratio,
        recent_pct_bars=args.recent_pct_bars,
        max_markets=args.max_markets,
    )
    summary = result["summary"]
    rows = result["rows"]

    summary_path = OUTPUT_DIR / "backtest_mras_lite_v1_summary.json"
    md_path = OUTPUT_DIR / "backtest_mras_lite_v1_summary.md"
    signals_path = OUTPUT_DIR / "backtest_mras_lite_v1_signals.jsonl"

    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(render_markdown(summary))
    with open(signals_path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"signals={len(rows)} summary={summary_path} md={md_path} jsonl={signals_path}")
    for horizon, perf in summary["performance"].items():
        print(
            f"{horizon}: count={perf['count']} hit_rate={perf['hit_rate']} avg_roi={perf['avg_roi']} max_consecutive_losses={perf['max_consecutive_losses']}"
        )


if __name__ == "__main__":
    main()
