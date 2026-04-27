#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MRAS-Lite v4 - Mean Revert Parameter Scan
=========================================

目标：
- 仅针对 mean_revert 策略做参数网格扫描
- 复用 v3 的数据装载 / 特征构建 / 未来收益评估
- 输出每组参数在 raw / dedup 下的 4h/8h/12h/24h 表现
- 自动挑出 best combo，并导出该组合信号

输出：
- outputs/backtest_mras_lite_v4_scan_summary.json
- outputs/backtest_mras_lite_v4_scan_summary.md
- outputs/backtest_mras_lite_v4_scan_results.jsonl
- outputs/backtest_mras_lite_v4_best_signals_raw.jsonl
- outputs/backtest_mras_lite_v4_best_signals_dedup.jsonl
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from dataclasses import dataclass, asdict
from datetime import datetime
from itertools import product
from pathlib import Path
from typing import Dict, List, Optional

from backtest_mras_lite_v3 import (
    DB_PATH,
    OUTPUT_DIR,
    HORIZONS,
    MarketMeta,
    aggregate_bars,
    build_feature,
    compute_outcome,
    dedupe_signals,
    find_future_bar,
    iso,
    load_markets,
    load_raw_points,
    segment_bars,
    summarize_horizon,
)
from core.scoring import build_signal, clamp


@dataclass(frozen=True)
class MRParams:
    pct_low: float
    rsi_low: int
    chg24h_min: float
    noise_max: float
    min_strength: int

    @property
    def pct_high(self) -> float:
        return round(1.0 - self.pct_low, 4)

    @property
    def rsi_high(self) -> int:
        return 100 - self.rsi_low

    def key(self) -> str:
        return (
            f"pct{self.pct_low:.2f}_rsi{self.rsi_low}_"
            f"chg{self.chg24h_min:.3f}_noise{self.noise_max:.1f}_s{self.min_strength}"
        )


@dataclass
class Candidate:
    token_id: str
    question: str
    slug: Optional[str]
    entry_ts: str
    entry_yes_price: float
    entry_samples: int
    quality_ratio_24h: float
    liquidity: float
    volume: float
    hours_to_event: Optional[float]
    feature: Dict
    outcomes: Dict[str, Dict]


def evaluate_mean_revert(feature: Dict, params: MRParams) -> Optional[Dict]:
    yes_price = feature.get("yes_price") or 0.0
    liquidity = feature.get("liquidity") or 0.0
    chg_24h = feature.get("chg_24h")
    rsi = feature.get("rsi_14")
    pct_rank = feature.get("pct_rank_recent")
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

    mr_reasons: List[str] = []
    mr_strength = 0
    is_pct_extreme = False
    is_rsi_extreme = False
    is_chg_extreme = False
    is_noise_ok = False

    if pct_rank is not None and (pct_rank <= params.pct_low or pct_rank >= params.pct_high):
        mr_strength += 1
        is_pct_extreme = True
        mr_reasons.append("recent percentile extreme")
    if rsi is not None and (rsi <= params.rsi_low or rsi >= params.rsi_high):
        mr_strength += 1
        is_rsi_extreme = True
        mr_reasons.append("RSI extreme")
    if chg_24h is not None and abs(chg_24h) >= params.chg24h_min:
        mr_strength += 1
        is_chg_extreme = True
        mr_reasons.append("24h move extended")
    if noise is not None and noise <= params.noise_max:
        mr_strength += 1
        is_noise_ok = True
        mr_reasons.append("noise acceptable")

    if not is_pct_extreme or mr_strength < params.min_strength:
        return None

    direction = None
    if pct_rank <= params.pct_low and yes_price <= 0.45:
        direction = "YES"
        mr_reasons.insert(0, "recent lower percentile bounce")
    elif pct_rank >= params.pct_high and yes_price >= 0.55:
        direction = "NO"
        mr_reasons.insert(0, "recent upper percentile fade")
    if not direction:
        return None

    setup = 0.68 if liquidity >= 50000 else 0.60
    if is_noise_ok:
        setup += 0.03
    edge = 0.50
    if is_rsi_extreme:
        edge += 0.08
    if is_chg_extreme and chg_24h is not None and abs(chg_24h) >= max(0.06, params.chg24h_min + 0.01):
        edge += 0.05
    execution = 0.72 if "event_near" not in advisory_flags else 0.46
    if noise is not None and noise > min(params.noise_max, 2.2):
        execution -= 0.08

    return build_signal(
        feature,
        "mean_revert",
        direction,
        setup_score=clamp(setup),
        edge_score=clamp(edge),
        execution_score=clamp(execution),
        reasons=mr_reasons,
        risk_flags=advisory_flags + blocking_flags,
        advisory_flags=advisory_flags,
        blocking_flags=blocking_flags,
    )


def precompute_candidates(
    min_liquidity: float,
    min_samples_per_bar: int,
    min_quality_ratio: float,
    recent_pct_bars: int,
    max_markets: int,
) -> Dict[str, object]:
    conn = sqlite3.connect(DB_PATH)
    markets = load_markets(conn, min_liquidity=min_liquidity)
    if max_markets > 0:
        markets = markets[:max_markets]

    quality = {
        "markets_scanned": len(markets),
        "markets_with_bars": 0,
        "candidate_markets": 0,
        "segments_total": 0,
        "segments_ge_24h": 0,
        "bars_total": 0,
        "candidates_total": 0,
    }
    candidates: List[Candidate] = []

    for idx_market, meta in enumerate(markets, start=1):
        points = load_raw_points(conn, meta.token_id)
        bars = aggregate_bars(points)
        if not bars:
            continue
        quality["markets_with_bars"] += 1
        quality["bars_total"] += len(bars)
        segments = segment_bars(bars)
        quality["segments_total"] += len(segments)
        global_idx_by_ts = {bar.ts: pos for pos, bar in enumerate(bars)}
        market_candidate_count = 0

        for seg in segments.values():
            if len(seg) >= 97:
                quality["segments_ge_24h"] += 1
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
                entry_bar = seg[i]
                global_idx = global_idx_by_ts.get(entry_bar.ts)
                if global_idx is None:
                    continue
                outcomes = {}
                for label in HORIZONS:
                    future_bar = find_future_bar(bars, global_idx, label)
                    if not future_bar:
                        continue
                    outcomes[label] = compute_outcome(entry_bar.close, future_bar.close, "YES")
                    outcomes[label]["future_yes_price"] = round(future_bar.close, 6)
                    outcomes[label]["future_ts"] = iso(future_bar.ts)
                if not outcomes:
                    continue
                candidates.append(
                    Candidate(
                        token_id=meta.token_id,
                        question=meta.question,
                        slug=meta.slug,
                        entry_ts=iso(entry_bar.ts),
                        entry_yes_price=round(entry_bar.close, 6),
                        entry_samples=feature["entry_samples"],
                        quality_ratio_24h=round(feature["quality_ratio_24h"], 4),
                        liquidity=round(meta.liquidity, 2),
                        volume=round(meta.volume, 2),
                        hours_to_event=round(feature["hours_to_event"], 4) if feature.get("hours_to_event") is not None else None,
                        feature=feature,
                        outcomes=outcomes,
                    )
                )
                market_candidate_count += 1

        if market_candidate_count > 0:
            quality["candidate_markets"] += 1
        if idx_market % 25 == 0:
            print(f"precompute {idx_market}/{len(markets)} markets | candidates={len(candidates)}")

    conn.close()
    quality["candidates_total"] = len(candidates)
    return {"quality": quality, "candidates": candidates}


def render_row(candidate: Candidate, signal: Dict) -> Dict:
    row = {
        "token_id": candidate.token_id,
        "question": candidate.question,
        "slug": candidate.slug,
        "entry_ts": candidate.entry_ts,
        "entry_yes_price": candidate.entry_yes_price,
        "entry_samples": candidate.entry_samples,
        "quality_ratio_24h": candidate.quality_ratio_24h,
        "regime": signal["regime"],
        "direction": signal["direction"],
        "confidence": signal["confidence"],
        "position": signal["position"],
        "liquidity": candidate.liquidity,
        "volume": candidate.volume,
        "hours_to_event": candidate.hours_to_event,
        "features": {
            "chg_1h": signal.get("chg_1h"),
            "chg_4h": signal.get("chg_4h"),
            "chg_24h": signal.get("chg_24h"),
            "pct_rank_recent": candidate.feature.get("pct_rank_recent"),
            "rsi_14": candidate.feature.get("rsi_14"),
            "trend_slope_4h": candidate.feature.get("trend_slope_4h"),
            "trend_slope_24h": candidate.feature.get("trend_slope_24h"),
            "noise_score": candidate.feature.get("noise_score"),
        },
        "reasons": signal.get("reasons", []),
        "risk_flags": signal.get("risk_flags", []),
        "outcomes": {},
    }
    for label, out in candidate.outcomes.items():
        future_yes_price = out["future_yes_price"]
        computed = compute_outcome(candidate.entry_yes_price, future_yes_price, signal["direction"])
        computed["future_yes_price"] = future_yes_price
        computed["future_ts"] = out["future_ts"]
        row["outcomes"][label] = computed
    return row


def summarize_items(items: List[Dict]) -> Dict:
    return {label: summarize_horizon(items, label) for label in HORIZONS}


def combo_score(dedup_perf: Dict[str, Dict]) -> float:
    count24 = dedup_perf["24h"]["count"] or 0
    if count24 < 5:
        return -999
    avg24 = dedup_perf["24h"]["avg_roi"] or -999
    avg12 = dedup_perf["12h"]["avg_roi"] or -999
    avg8 = dedup_perf["8h"]["avg_roi"] or -999
    hit24 = dedup_perf["24h"]["hit_rate"] or 0
    penalty = 0.002 * max(0, 10 - count24)
    return (avg24 * 1.0) + (avg12 * 0.6) + (avg8 * 0.35) + (hit24 * 0.01) - penalty


def main() -> None:
    parser = argparse.ArgumentParser(description="MRAS-Lite v4 mean_revert parameter scan")
    parser.add_argument("--min-liquidity", type=float, default=20000)
    parser.add_argument("--min-samples-per-bar", type=int, default=10)
    parser.add_argument("--recent-pct-bars", type=int, default=96)
    parser.add_argument("--min-quality-ratio", type=float, default=0.7)
    parser.add_argument("--cooldown-hours", type=float, default=12.0)
    parser.add_argument("--max-markets", type=int, default=0)
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    pre = precompute_candidates(
        min_liquidity=args.min_liquidity,
        min_samples_per_bar=args.min_samples_per_bar,
        min_quality_ratio=args.min_quality_ratio,
        recent_pct_bars=args.recent_pct_bars,
        max_markets=args.max_markets,
    )
    candidates: List[Candidate] = pre["candidates"]

    grid = [
        MRParams(*vals)
        for vals in product(
            [0.08, 0.10, 0.12],
            [30, 33, 35, 38],
            [0.03, 0.035, 0.05],
            [1.8, 2.2, 2.6],
            [2, 3],
        )
    ]

    combo_results = []
    best_combo = None
    best_raw_rows: List[Dict] = []
    best_dedup_rows: List[Dict] = []

    for idx_combo, params in enumerate(grid, start=1):
        raw_rows: List[Dict] = []
        for cand in candidates:
            signal = evaluate_mean_revert(cand.feature, params)
            if not signal or signal.get("position") == "skip":
                continue
            raw_rows.append(render_row(cand, signal))
        dedup_rows = dedupe_signals(raw_rows, cooldown_hours=args.cooldown_hours)
        raw_perf = summarize_items(raw_rows)
        dedup_perf = summarize_items(dedup_rows)
        result = {
            "params": asdict(params) | {"pct_high": params.pct_high, "rsi_high": params.rsi_high},
            "raw_signals": len(raw_rows),
            "dedup_signals": len(dedup_rows),
            "raw_performance": raw_perf,
            "dedup_performance": dedup_perf,
        }
        result["score"] = round(combo_score(dedup_perf), 6)
        combo_results.append(result)

        if best_combo is None or result["score"] > best_combo["score"]:
            best_combo = result
            best_raw_rows = raw_rows
            best_dedup_rows = dedup_rows

        if idx_combo % 20 == 0:
            print(
                f"scan {idx_combo}/{len(grid)} combos | current_best={best_combo['params']} score={best_combo['score']} dedup24={best_combo['dedup_performance']['24h']['avg_roi']}"
            )

    combo_results_sorted = sorted(combo_results, key=lambda x: x["score"], reverse=True)
    top10 = combo_results_sorted[:10]

    summary = {
        "generated_at": iso(datetime.now()),
        "config": {
            "db_path": str(DB_PATH),
            "min_liquidity": args.min_liquidity,
            "min_samples_per_bar": args.min_samples_per_bar,
            "min_quality_ratio": args.min_quality_ratio,
            "recent_pct_bars": args.recent_pct_bars,
            "cooldown_hours": args.cooldown_hours,
            "max_markets": args.max_markets,
            "grid_size": len(grid),
            "strategy_focus": "mean_revert_parameter_scan",
        },
        "quality": pre["quality"],
        "best_combo": best_combo,
        "top10": top10,
    }

    summary_path = OUTPUT_DIR / "backtest_mras_lite_v4_scan_summary.json"
    md_path = OUTPUT_DIR / "backtest_mras_lite_v4_scan_summary.md"
    results_path = OUTPUT_DIR / "backtest_mras_lite_v4_scan_results.jsonl"
    best_raw_path = OUTPUT_DIR / "backtest_mras_lite_v4_best_signals_raw.jsonl"
    best_dedup_path = OUTPUT_DIR / "backtest_mras_lite_v4_best_signals_dedup.jsonl"

    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    with open(results_path, "w", encoding="utf-8") as f:
        for row in combo_results_sorted:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    with open(best_raw_path, "w", encoding="utf-8") as f:
        for row in best_raw_rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    with open(best_dedup_path, "w", encoding="utf-8") as f:
        for row in best_dedup_rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    lines: List[str] = []
    lines.append("# MRAS-Lite v4 Mean Revert 参数扫描")
    lines.append("")
    lines.append(f"生成时间：{summary['generated_at']}")
    lines.append("")
    lines.append("## 配置")
    lines.append("")
    for k, v in summary["config"].items():
        lines.append(f"- {k}: `{v}`")
    lines.append("")
    lines.append("## 数据质量")
    lines.append("")
    for k, v in summary["quality"].items():
        lines.append(f"- {k}: **{v}**")
    lines.append("")
    lines.append("## Best Combo")
    lines.append("")
    lines.append(f"- params: `{json.dumps(best_combo['params'], ensure_ascii=False)}`")
    lines.append(f"- score: **{best_combo['score']}**")
    lines.append(f"- raw_signals: **{best_combo['raw_signals']}**")
    lines.append(f"- dedup_signals: **{best_combo['dedup_signals']}**")
    lines.append("")
    lines.append("### Best Combo DEDUP Performance")
    lines.append("")
    for label, perf in best_combo["dedup_performance"].items():
        lines.append(
            f"- {label}: count={perf['count']}, hit_rate={perf['hit_rate']}, avg_roi={perf['avg_roi']}, median_roi={perf['median_roi']}, max_consecutive_losses={perf['max_consecutive_losses']}"
        )
    lines.append("")
    lines.append("## Top 10 Combos")
    lines.append("")
    for idx, row in enumerate(top10, start=1):
        perf24 = row["dedup_performance"]["24h"]
        perf12 = row["dedup_performance"]["12h"]
        perf8 = row["dedup_performance"]["8h"]
        lines.append(
            f"{idx}. score={row['score']} | params={json.dumps(row['params'], ensure_ascii=False)} | dedup={row['dedup_signals']} | 8h={perf8['avg_roi']} | 12h={perf12['avg_roi']} | 24h={perf24['avg_roi']}"
        )
    lines.append("")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"summary={summary_path} md={md_path} results={results_path}")
    print(f"best_params={best_combo['params']} score={best_combo['score']}")
    for label, perf in best_combo["dedup_performance"].items():
        print(f"best:dedup:{label}: count={perf['count']} hit_rate={perf['hit_rate']} avg_roi={perf['avg_roi']}")


if __name__ == "__main__":
    main()
