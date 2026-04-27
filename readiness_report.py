#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from collections import Counter
from pathlib import Path

REVIEW_FILE = Path('/Users/mac/.openclaw/workspace/polymarket/outputs/review_status.json')
PORTFOLIO_FILE = Path('/Users/mac/.openclaw/workspace/polymarket/portfolio_state.json')
CONFIG_FILE = Path('/Users/mac/.openclaw/workspace/polymarket/trading_config.json')
OUTPUT_MD = Path('/Users/mac/.openclaw/workspace/polymarket/outputs/readiness_report.md')
OUTPUT_JSON = Path('/Users/mac/.openclaw/workspace/polymarket/outputs/readiness_report.json')


def load(path):
    if not path.exists():
        return {} if path.suffix == '.json' else []
    return json.loads(path.read_text(encoding='utf-8'))


def main():
    reviews = load(REVIEW_FILE) or []
    portfolio = load(PORTFOLIO_FILE) or {}
    config = load(CONFIG_FILE) or {}

    outcome_counter = Counter(r.get('outcome') for r in reviews)
    judged = outcome_counter.get('hit', 0) + outcome_counter.get('miss', 0)
    hit_rate = (outcome_counter.get('hit', 0) / judged * 100) if judged else 0.0
    ready_6h = sum(1 for r in reviews if r.get('window_6h_ready'))
    ready_24h = sum(1 for r in reviews if r.get('window_24h_ready'))
    ready_48h = sum(1 for r in reviews if r.get('window_48h_ready'))
    health = portfolio.get('portfolio_health', {})

    checklist = {
        '6h_samples_ge_30': ready_6h >= 30,
        '24h_samples_ge_20': ready_24h >= 20,
        '48h_samples_ge_10': ready_48h >= 10,
        'judged_samples_ge_20': judged >= 20,
        'hit_rate_ge_55pct': hit_rate >= 55.0,
        'live_disabled': not config.get('live_trade_enabled', False),
        'not_halted': not health.get('halted', False),
    }
    ready_score = sum(1 for v in checklist.values() if v)

    report = {
        'review_count': len(reviews),
        'judged_samples': judged,
        'hit_rate_pct': round(hit_rate, 2),
        'window_ready': {'6h': ready_6h, '24h': ready_24h, '48h': ready_48h},
        'portfolio_health': health,
        'checklist': checklist,
        'ready_score': ready_score,
        'ready_total': len(checklist),
        'status': 'paper_only' if ready_score < len(checklist) else 'ready_for_tiny_live_trial',
    }

    lines = [
        '# Polymarket Readiness Report',
        '',
        f"- Review samples: **{len(reviews)}**",
        f"- Judged samples: **{judged}**",
        f"- Hit rate: **{hit_rate:.1f}%**",
        f"- Window ready: 6h={ready_6h}, 24h={ready_24h}, 48h={ready_48h}",
        f"- Portfolio halted: **{health.get('halted', False)}**",
        f"- Ready score: **{ready_score}/{len(checklist)}**",
        f"- Status: **{report['status']}**",
        '',
        '## Checklist',
    ]
    for k, v in checklist.items():
        lines.append(f"- {'✅' if v else '⬜'} {k}")

    OUTPUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    OUTPUT_MD.write_text('\n'.join(lines), encoding='utf-8')
    print(f'readiness_status={report["status"]} ready_score={ready_score}/{len(checklist)} output={OUTPUT_MD}')


if __name__ == '__main__':
    main()
