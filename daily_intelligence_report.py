#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from intelligence_schema import enrich_signal

ROOT = Path('/Users/mac/.openclaw/workspace/polymarket')
CONFIG_FILE = ROOT / 'trading_config.json'
SIGNALS_FILE = ROOT / 'outputs' / 'signals_v2_latest.json'
ALERTS_FILE = ROOT / 'outputs' / 'alerts_ready.json'
REVIEW_FILE = ROOT / 'outputs' / 'review_status.json'
SUMMARY_FILE = ROOT / 'outputs' / 'paper_summary.json'
OUTPUT_MD = ROOT / 'outputs' / 'daily_intelligence_latest.md'
OUTPUT_JSON = ROOT / 'outputs' / 'daily_intelligence_latest.json'
REPORTS_DIR = ROOT / 'reports' / 'intelligence'


def load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding='utf-8'))


def top_review_stats(review_rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    outcomes = Counter((row.get('outcome') or 'unknown') for row in review_rows)
    regime_outcomes = Counter()
    cluster_outcomes = Counter()
    for row in review_rows:
        regime_outcomes[(row.get('regime') or 'unknown', row.get('outcome') or 'unknown')] += 1
        cluster_outcomes[(row.get('cluster') or 'unknown', row.get('outcome') or 'unknown')] += 1
    return {
        'outcomes': dict(outcomes),
        'regime_outcomes': {f'{k[0]}::{k[1]}': v for k, v in regime_outcomes.items()},
        'cluster_outcomes': {f'{k[0]}::{k[1]}': v for k, v in cluster_outcomes.items()},
    }


def summarize_candidates(signals: List[Dict[str, Any]], config: Dict[str, Any]) -> List[Dict[str, Any]]:
    enriched = [enrich_signal(sig, config=config) for sig in signals]
    ranked = sorted(
        enriched,
        key=lambda s: (
            {'candidate': 0, 'research': 1, 'watch': 2, 'do_not_touch': 3}.get(s.get('execution_readiness'), 9),
            -float(s.get('evidence_score', 0) or 0),
            -float(s.get('confidence', 0) or 0),
        ),
    )
    return ranked


def build_report() -> Dict[str, Any]:
    config = load_json(CONFIG_FILE, {})
    signals = load_json(SIGNALS_FILE, [])
    alerts = load_json(ALERTS_FILE, [])
    review_rows = load_json(REVIEW_FILE, [])
    summary = load_json(SUMMARY_FILE, {})

    candidates = summarize_candidates(signals, config)
    alert_candidates = summarize_candidates(alerts, config)
    blocked = [c for c in candidates if c.get('execution_readiness') == 'do_not_touch'][:5]
    active = [c for c in candidates if c.get('execution_readiness') in ('candidate', 'research')][:8]
    watch = [c for c in candidates if c.get('execution_readiness') == 'watch'][:5]

    perf = summary.get('performance', {}) or {}
    gate = ((summary.get('discipline_v2') or {}).get('paper_to_micro_live_gate') or {})
    portfolio = (summary.get('portfolio') or {}).get('portfolio_health', {}) or {}

    return {
        'generated_at': datetime.now().isoformat(timespec='seconds'),
        'phase': config.get('mode'),
        'paper_gate_eligible': gate.get('eligible'),
        'portfolio_halt_reason': portfolio.get('halt_reason'),
        'headline': {
            'summary': '继续 paper-only，优先做情报筛选和噪音剔除。',
            'why': [
                f"paper gate eligible={gate.get('eligible')}",
                f"win_rate={perf.get('win_rate')}",
                f"flat_rate={perf.get('flat_rate')}",
                f"realized_pnl_like={perf.get('total_realized_pnl_like')}",
            ],
        },
        'active_candidates': active,
        'ready_alerts': alert_candidates[:6],
        'watchlist': watch,
        'do_not_touch': blocked,
        'review_stats': top_review_stats(review_rows),
        'regime_snapshot': summary.get('by_regime', {}),
        'cluster_snapshot': summary.get('by_cluster', {}),
        'paper_summary': {
            'realized_trade_count': perf.get('realized_trade_count'),
            'win_rate': perf.get('win_rate'),
            'flat_rate': perf.get('flat_rate'),
            'total_realized_pnl_like': perf.get('total_realized_pnl_like'),
        },
    }


def render_md(report: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append(f"# Polymarket Intelligence Brief - {report['generated_at'][:10]}")
    lines.append('')
    lines.append('## 今日结论')
    lines.append(f"- 阶段: {report.get('phase')}")
    lines.append(f"- 核心判断: {report['headline']['summary']}")
    for item in report['headline']['why']:
        lines.append(f"- {item}")
    lines.append('')

    lines.append('## 今日优先候选')
    if not report['active_candidates']:
        lines.append('- 当前无 candidate/research 级别信号。')
    else:
        for idx, sig in enumerate(report['active_candidates'], 1):
            lines.append(f"### {idx}. {sig.get('question')} [{sig.get('execution_readiness')}] ")
            lines.append(f"- 方向: {sig.get('direction')} | conf={float(sig.get('confidence', 0) or 0):.2f} | evidence={float(sig.get('evidence_score', 0) or 0):.2f}")
            lines.append(f"- regime/cluster: {sig.get('regime')} / {sig.get('cluster')}")
            lines.append(f"- thesis: {sig.get('thesis_summary')}")
            lines.append(f"- why_now: {sig.get('why_now')}")
            lines.append(f"- do_not_trade_if: {'; '.join(sig.get('do_not_trade_if', [])[:3])}")
            lines.append('')

    lines.append('## 可直接关注的 Ready Alerts')
    if not report['ready_alerts']:
        lines.append('- 当前无可直接关注 alert。')
    else:
        for sig in report['ready_alerts']:
            lines.append(f"- [{sig.get('execution_readiness')}] {sig.get('question')} | {sig.get('direction')} | conf={float(sig.get('confidence', 0) or 0):.2f} | catalyst={sig.get('catalyst_type')}")
    lines.append('')

    lines.append('## 观察名单')
    if not report['watchlist']:
        lines.append('- 当前无 watchlist。')
    else:
        for sig in report['watchlist']:
            lines.append(f"- {sig.get('question')} | cluster={sig.get('cluster')} | regime={sig.get('regime')} | why={sig.get('why_now')}")
    lines.append('')

    lines.append('## 今日避坑')
    if not report['do_not_touch']:
        lines.append('- 当前无新增 do_not_touch。')
    else:
        for sig in report['do_not_touch']:
            lines.append(f"- {sig.get('question')} | cluster={sig.get('cluster')} | regime={sig.get('regime')} | blocking={', '.join(sig.get('blocking_flags', [])[:3])}")
    lines.append('')

    lines.append('## 后验复盘快照')
    outcomes = report['review_stats'].get('outcomes', {})
    lines.append(f"- outcomes: {outcomes}")
    lines.append(f"- paper_summary: {report.get('paper_summary')}")
    lines.append('')

    lines.append('## Regime Snapshot')
    for regime, stats in (report.get('regime_snapshot') or {}).items():
        lines.append(f"- {regime}: closed={stats.get('closed')} win_rate={stats.get('win_rate')} flat_rate={stats.get('flat_rate')} pnl={stats.get('realized_pnl_like')}")
    lines.append('')

    lines.append('## Cluster Snapshot')
    for cluster, stats in (report.get('cluster_snapshot') or {}).items():
        lines.append(f"- {cluster}: closed={stats.get('closed')} win_rate={stats.get('win_rate')} flat_rate={stats.get('flat_rate')} pnl={stats.get('realized_pnl_like')}")
    lines.append('')

    lines.append('## 建议动作')
    lines.append('- 继续保持 paper-only，不推进 micro live。')
    lines.append('- 优先减少 flat-heavy cluster/regime 的注意力占用。')
    lines.append('- 只把 candidate/research 级别信号用于主观察池。')
    return '\n'.join(lines)


def main() -> None:
    report = build_report()
    OUTPUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    markdown = render_md(report)
    OUTPUT_MD.write_text(markdown, encoding='utf-8')
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    date_str = report['generated_at'][:10]
    (REPORTS_DIR / f'{date_str}.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    (REPORTS_DIR / f'{date_str}.md').write_text(markdown, encoding='utf-8')
    print(f'wrote {OUTPUT_MD} and {OUTPUT_JSON}')


if __name__ == '__main__':
    main()
