#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MRAS-Lite v5 - Best Combo Validation
====================================

目标：
- 固化 v4 最优 mean_revert 参数
- 输出 fixed-params 全量回测结果
- 对 dedup 样本做审计（类别/Top/Bottom）
- 做 walk-forward 验证：每折在 train 上选参，在 next fold 上测试

输出：
- outputs/backtest_mras_lite_v5_summary.json
- outputs/backtest_mras_lite_v5_summary.md
- outputs/backtest_mras_lite_v5_fixed_signals_raw.jsonl
- outputs/backtest_mras_lite_v5_fixed_signals_dedup.jsonl
- outputs/backtest_mras_lite_v5_walkforward_folds.json
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from itertools import product
from typing import Dict, List, Tuple

from backtest_mras_lite_v3 import OUTPUT_DIR, iso, summarize_horizon
from backtest_mras_lite_v4_scan import (
    MRParams,
    combo_score,
    evaluate_mean_revert,
    precompute_candidates,
    render_row,
)
from backtest_mras_lite_v3 import dedupe_signals

BEST_PARAMS = MRParams(
    pct_low=0.12,
    rsi_low=38,
    chg24h_min=0.05,
    noise_max=1.8,
    min_strength=3,
)

GRID = [
    MRParams(*vals)
    for vals in product(
        [0.08, 0.10, 0.12],
        [30, 33, 35, 38],
        [0.03, 0.035, 0.05],
        [1.8, 2.2, 2.6],
        [2, 3],
    )
]


def summarize_items(items: List[Dict], horizons: List[str]) -> Dict[str, Dict]:
    return {label: summarize_horizon(items, label) for label in horizons}


def evaluate_candidates(candidates: List, params: MRParams, cooldown_hours: float, horizons: List[str]) -> Dict:
    raw_rows: List[Dict] = []
    for cand in candidates:
        signal = evaluate_mean_revert(cand.feature, params)
        if not signal or signal.get("position") == "skip":
            continue
        raw_rows.append(render_row(cand, signal))
    dedup_rows = dedupe_signals(raw_rows, cooldown_hours=cooldown_hours)
    return {
        "params": asdict(params) | {"pct_high": params.pct_high, "rsi_high": params.rsi_high},
        "raw_rows": raw_rows,
        "dedup_rows": dedup_rows,
        "raw_performance": summarize_items(raw_rows, horizons),
        "dedup_performance": summarize_items(dedup_rows, horizons),
    }


def choose_best_on_train(candidates: List, cooldown_hours: float, horizons: List[str]) -> Dict:
    best = None
    for idx, params in enumerate(GRID, start=1):
        result = evaluate_candidates(candidates, params, cooldown_hours=cooldown_hours, horizons=horizons)
        score = combo_score(result["dedup_performance"])
        candidate = {
            "params": result["params"],
            "score": round(score, 6),
            "raw_signals": len(result["raw_rows"]),
            "dedup_signals": len(result["dedup_rows"]),
            "raw_performance": result["raw_performance"],
            "dedup_performance": result["dedup_performance"],
        }
        if best is None or candidate["score"] > best["score"]:
            best = candidate
    return best


def classify_market(row: Dict) -> str:
    slug = (row.get("slug") or "").lower()
    question = (row.get("question") or "").lower()
    text = slug + " " + question
    if "world-cup" in text or "fifa" in text:
        return "world_cup"
    if "stanley-cup" in text or "nhl" in text:
        return "nhl"
    if "nba-finals" in text or "nba finals" in text:
        return "nba"
    if "democratic-presidential-nomination" in text or "democratic presidential nomination" in text:
        return "dem_nomination"
    if "us-presidential-election" in text or "presidential election" in text:
        return "us_election"
    return "other"


def safe_roi(row: Dict, horizon: str = "24h") -> float:
    return row.get("outcomes", {}).get(horizon, {}).get("roi", -999)


def audit_samples(rows: List[Dict], horizons: List[str]) -> Dict:
    by_category: Dict[str, List[Dict]] = {}
    for row in rows:
        category = classify_market(row)
        by_category.setdefault(category, []).append(row)

    category_summary = {}
    for category, items in sorted(by_category.items()):
        category_summary[category] = {
            "count": len(items),
            "performance": summarize_items(items, horizons),
            "examples": [
                {
                    "question": r["question"],
                    "entry_ts": r["entry_ts"],
                    "entry_yes_price": r["entry_yes_price"],
                    "roi_24h": safe_roi(r, "24h"),
                }
                for r in sorted(items, key=lambda x: safe_roi(x, "24h"), reverse=True)[:3]
            ],
        }

    top_24h = sorted(rows, key=lambda x: safe_roi(x, "24h"), reverse=True)[:5]
    bottom_24h = sorted(rows, key=lambda x: safe_roi(x, "24h"))[:5]
    return {
        "count": len(rows),
        "category_summary": category_summary,
        "top_24h": top_24h,
        "bottom_24h": bottom_24h,
    }


def build_time_folds(candidates: List, n_folds: int = 4) -> List[Tuple[List, List, Dict]]:
    unique_ts = sorted({cand.entry_ts for cand in candidates})
    if len(unique_ts) < n_folds:
        return []
    chunks: List[List[str]] = []
    for i in range(n_folds):
        start = i * len(unique_ts) // n_folds
        end = (i + 1) * len(unique_ts) // n_folds
        chunks.append(unique_ts[start:end])

    folds = []
    for i in range(1, len(chunks)):
        train_ts = {ts for chunk in chunks[:i] for ts in chunk}
        test_ts = set(chunks[i])
        train = [cand for cand in candidates if cand.entry_ts in train_ts]
        test = [cand for cand in candidates if cand.entry_ts in test_ts]
        meta = {
            "fold": i,
            "train_ts_min": min(train_ts) if train_ts else None,
            "train_ts_max": max(train_ts) if train_ts else None,
            "test_ts_min": min(test_ts) if test_ts else None,
            "test_ts_max": max(test_ts) if test_ts else None,
            "train_candidates": len(train),
            "test_candidates": len(test),
        }
        if train and test:
            folds.append((train, test, meta))
    return folds


def strip_rows(rows: List[Dict]) -> List[Dict]:
    out = []
    for row in rows:
        out.append(
            {
                "question": row["question"],
                "slug": row.get("slug"),
                "entry_ts": row["entry_ts"],
                "entry_yes_price": row["entry_yes_price"],
                "direction": row["direction"],
                "confidence": row["confidence"],
                "liquidity": row["liquidity"],
                "hours_to_event": row.get("hours_to_event"),
                "roi_4h": safe_roi(row, "4h"),
                "roi_8h": safe_roi(row, "8h"),
                "roi_12h": safe_roi(row, "12h"),
                "roi_24h": safe_roi(row, "24h"),
                "reasons": row.get("reasons", []),
            }
        )
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="MRAS-Lite v5 validation")
    parser.add_argument("--min-liquidity", type=float, default=20000)
    parser.add_argument("--min-samples-per-bar", type=int, default=10)
    parser.add_argument("--recent-pct-bars", type=int, default=96)
    parser.add_argument("--min-quality-ratio", type=float, default=0.7)
    parser.add_argument("--cooldown-hours", type=float, default=12.0)
    parser.add_argument("--max-markets", type=int, default=0)
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    horizons = ["4h", "8h", "12h", "24h"]

    pre = precompute_candidates(
        min_liquidity=args.min_liquidity,
        min_samples_per_bar=args.min_samples_per_bar,
        min_quality_ratio=args.min_quality_ratio,
        recent_pct_bars=args.recent_pct_bars,
        max_markets=args.max_markets,
    )
    candidates = pre["candidates"]

    fixed = evaluate_candidates(candidates, BEST_PARAMS, cooldown_hours=args.cooldown_hours, horizons=horizons)
    fixed_summary = {
        "params": fixed["params"],
        "raw_signals": len(fixed["raw_rows"]),
        "dedup_signals": len(fixed["dedup_rows"]),
        "raw_performance": fixed["raw_performance"],
        "dedup_performance": fixed["dedup_performance"],
    }
    audit = audit_samples(fixed["dedup_rows"], horizons)

    folds = build_time_folds(candidates, n_folds=4)
    walkforward = []
    aggregate_test_selected: List[Dict] = []
    aggregate_test_fixed: List[Dict] = []

    for train, test, meta in folds:
        best_train = choose_best_on_train(train, cooldown_hours=args.cooldown_hours, horizons=horizons)
        selected_params = MRParams(
            pct_low=best_train["params"]["pct_low"],
            rsi_low=best_train["params"]["rsi_low"],
            chg24h_min=best_train["params"]["chg24h_min"],
            noise_max=best_train["params"]["noise_max"],
            min_strength=best_train["params"]["min_strength"],
        )
        test_selected = evaluate_candidates(test, selected_params, cooldown_hours=args.cooldown_hours, horizons=horizons)
        test_fixed = evaluate_candidates(test, BEST_PARAMS, cooldown_hours=args.cooldown_hours, horizons=horizons)
        aggregate_test_selected.extend(test_selected["dedup_rows"])
        aggregate_test_fixed.extend(test_fixed["dedup_rows"])
        walkforward.append(
            {
                **meta,
                "train_best": best_train,
                "test_selected": {
                    "params": test_selected["params"],
                    "raw_signals": len(test_selected["raw_rows"]),
                    "dedup_signals": len(test_selected["dedup_rows"]),
                    "dedup_performance": test_selected["dedup_performance"],
                },
                "test_fixed": {
                    "params": fixed["params"],
                    "raw_signals": len(test_fixed["raw_rows"]),
                    "dedup_signals": len(test_fixed["dedup_rows"]),
                    "dedup_performance": test_fixed["dedup_performance"],
                },
            }
        )
        print(
            f"walkforward fold={meta['fold']} train={meta['train_candidates']} test={meta['test_candidates']} selected24={test_selected['dedup_performance']['24h']['avg_roi']} fixed24={test_fixed['dedup_performance']['24h']['avg_roi']}"
        )

    walkforward_summary = {
        "folds": walkforward,
        "aggregate_selected_test": summarize_items(aggregate_test_selected, horizons),
        "aggregate_fixed_test": summarize_items(aggregate_test_fixed, horizons),
    }

    summary = {
        "generated_at": iso(__import__('datetime').datetime.now()),
        "config": {
            "min_liquidity": args.min_liquidity,
            "min_samples_per_bar": args.min_samples_per_bar,
            "recent_pct_bars": args.recent_pct_bars,
            "min_quality_ratio": args.min_quality_ratio,
            "cooldown_hours": args.cooldown_hours,
            "max_markets": args.max_markets,
            "strategy_focus": "mean_revert_best_combo_validation",
            "best_params": fixed["params"],
        },
        "quality": pre["quality"],
        "fixed_summary": fixed_summary,
        "sample_audit": audit,
        "walkforward_summary": walkforward_summary,
    }

    summary_path = OUTPUT_DIR / "backtest_mras_lite_v5_summary.json"
    md_path = OUTPUT_DIR / "backtest_mras_lite_v5_summary.md"
    raw_path = OUTPUT_DIR / "backtest_mras_lite_v5_fixed_signals_raw.jsonl"
    dedup_path = OUTPUT_DIR / "backtest_mras_lite_v5_fixed_signals_dedup.jsonl"
    wf_path = OUTPUT_DIR / "backtest_mras_lite_v5_walkforward_folds.json"

    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    with open(raw_path, "w", encoding="utf-8") as f:
        for row in fixed["raw_rows"]:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    with open(dedup_path, "w", encoding="utf-8") as f:
        for row in fixed["dedup_rows"]:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    with open(wf_path, "w", encoding="utf-8") as f:
        json.dump(walkforward, f, ensure_ascii=False, indent=2)

    lines: List[str] = []
    lines.append("# MRAS-Lite v5 Best Combo Validation")
    lines.append("")
    lines.append(f"生成时间：{summary['generated_at']}")
    lines.append("")
    lines.append("## 固化参数")
    lines.append("")
    lines.append(f"- params: `{json.dumps(fixed['params'], ensure_ascii=False)}`")
    lines.append(f"- raw_signals: **{fixed_summary['raw_signals']}**")
    lines.append(f"- dedup_signals: **{fixed_summary['dedup_signals']}**")
    lines.append("")
    lines.append("## Fixed Params DEDUP Performance")
    lines.append("")
    for label, perf in fixed_summary["dedup_performance"].items():
        lines.append(
            f"- {label}: count={perf['count']}, hit_rate={perf['hit_rate']}, avg_roi={perf['avg_roi']}, median_roi={perf['median_roi']}, max_consecutive_losses={perf['max_consecutive_losses']}"
        )
    lines.append("")
    lines.append("## 样本审计（DEDUP）")
    lines.append("")
    for category, info in audit["category_summary"].items():
        perf24 = info["performance"]["24h"]
        lines.append(
            f"- {category}: count={info['count']}, 24h_avg_roi={perf24['avg_roi']}, 24h_hit_rate={perf24['hit_rate']}"
        )
    lines.append("")
    lines.append("### Top 24h Cases")
    lines.append("")
    for row in strip_rows(audit["top_24h"]):
        lines.append(
            f"- {row['question']} | {row['entry_ts']} | 24h={row['roi_24h']} | 12h={row['roi_12h']} | 8h={row['roi_8h']}"
        )
    lines.append("")
    lines.append("### Bottom 24h Cases")
    lines.append("")
    for row in strip_rows(audit["bottom_24h"]):
        lines.append(
            f"- {row['question']} | {row['entry_ts']} | 24h={row['roi_24h']} | 12h={row['roi_12h']} | 8h={row['roi_8h']}"
        )
    lines.append("")
    lines.append("## Walk-forward")
    lines.append("")
    for fold in walkforward:
        sel24 = fold["test_selected"]["dedup_performance"]["24h"]
        fix24 = fold["test_fixed"]["dedup_performance"]["24h"]
        lines.append(
            f"- fold {fold['fold']}: train_best={json.dumps(fold['train_best']['params'], ensure_ascii=False)} | selected_test_24h={sel24['avg_roi']} ({sel24['count']}) | fixed_test_24h={fix24['avg_roi']} ({fix24['count']})"
        )
    lines.append("")
    lines.append("### Walk-forward Aggregate Test")
    lines.append("")
    for mode in ["aggregate_selected_test", "aggregate_fixed_test"]:
        lines.append(f"- {mode}:")
        for label, perf in walkforward_summary[mode].items():
            lines.append(
                f"  - {label}: count={perf['count']}, hit_rate={perf['hit_rate']}, avg_roi={perf['avg_roi']}"
            )
    lines.append("")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"summary={summary_path} md={md_path} wf={wf_path}")
    print(f"fixed_params={fixed['params']}")
    for label, perf in fixed_summary["dedup_performance"].items():
        print(f"fixed:dedup:{label}: count={perf['count']} hit_rate={perf['hit_rate']} avg_roi={perf['avg_roi']}")
    for mode in ["aggregate_selected_test", "aggregate_fixed_test"]:
        for label, perf in walkforward_summary[mode].items():
            print(f"walkforward:{mode}:{label}: count={perf['count']} hit_rate={perf['hit_rate']} avg_roi={perf['avg_roi']}")


if __name__ == "__main__":
    main()
