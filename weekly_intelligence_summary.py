#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path('/Users/mac/.openclaw/workspace/polymarket')
REVIEW_FILE = ROOT / 'outputs' / 'review_status.json'
SUMMARY_FILE = ROOT / 'outputs' / 'paper_summary.json'
OUT_JSON = ROOT / 'outputs' / 'weekly_intelligence_summary.json'
OUT_MD = ROOT / 'outputs' / 'weekly_intelligence_summary.md'
REPORTS_DIR = ROOT / 'reports' / 'weekly_intelligence'


def load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding='utf-8'))


def parse_dt(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    except Exception:
        return None


def recent_rows(rows: List[Dict[str, Any]], days: int = 7) -> List[Dict[str, Any]]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    out = []
    for row in rows:
        saved_at = parse_dt(row.get('saved_at'))
        if saved_at and saved_at.astimezone(timezone.utc) >= cutoff:
            out.append(row)
    return out


def group_stats(rows: List[Dict[str, Any]], key_name: str) -> Dict[str, Dict[str, Any]]:
    groups: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
        'total': 0,
        'hit': 0,
        'miss': 0,
        'flat': 0,
        'unresolved': 0,
        'avg_confidence': 0.0,
        'sum_confidence': 0.0,
    })
    for row in rows:
        key = row.get(key_name) or 'unknown'
        g = groups[key]
        g['total'] += 1
        outcome = row.get('outcome') or 'unresolved'
        if outcome in g:
            g[outcome] += 1
        else:
            g['unresolved'] += 1
        g['sum_confidence'] += float(row.get('confidence', 0) or 0)
    for g in groups.values():
        if g['total']:
            g['avg_confidence'] = round(g['sum_confidence'] / g['total'], 4)
        g.pop('sum_confidence', None)
    return dict(groups)


def rank_groups(stats: Dict[str, Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    rows = []
    for name, item in stats.items():
        total = item.get('total', 0) or 1
        hit_rate = item.get('hit', 0) / total
        flat_rate = item.get('flat', 0) / total
        unresolved_rate = item.get('unresolved', 0) / total
        score = hit_rate - flat_rate * 0.5 - unresolved_rate * 0.2
        rows.append({
            'name': name,
            'score': round(score, 4),
            **item,
        })
    best = sorted(rows, key=lambda x: (x['score'], x['hit'], -x['flat']), reverse=True)[:5]
    worst = sorted(rows, key=lambda x: (x['score'], x['hit'], -x['flat']))[:5]
    return {'best': best, 'worst': worst}


def build_summary() -> Dict[str, Any]:
    review_rows = load_json(REVIEW_FILE, [])
    paper_summary = load_json(SUMMARY_FILE, {})
    recent = recent_rows(review_rows, days=7)
    regime_stats = group_stats(recent, 'regime')
    cluster_stats = group_stats(recent, 'cluster')
    return {
        'generated_at': datetime.now().isoformat(timespec='seconds'),
        'window_days': 7,
        'review_count': len(recent),
        'regime_stats': regime_stats,
        'cluster_stats': cluster_stats,
        'ranked_regimes': rank_groups(regime_stats),
        'ranked_clusters': rank_groups(cluster_stats),
        'paper_performance': paper_summary.get('performance', {}),
        'paper_gate': ((paper_summary.get('discipline_v2') or {}).get('paper_to_micro_live_gate') or {}),
    }


def render_md(summary: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append(f"# Weekly Intelligence Summary - {summary['generated_at'][:10]}")
    lines.append('')
    lines.append('## 周度结论')
    lines.append(f"- window_days: {summary.get('window_days')}")
    lines.append(f"- review_count: {summary.get('review_count')}")
    perf = summary.get('paper_performance', {})
    lines.append(f"- paper win_rate={perf.get('win_rate')} flat_rate={perf.get('flat_rate')} pnl={perf.get('total_realized_pnl_like')}")
    gate = summary.get('paper_gate', {})
    lines.append(f"- paper_to_micro_live eligible={gate.get('eligible')}")
    lines.append('')

    lines.append('## Best Regimes')
    for row in summary['ranked_regimes']['best']:
        lines.append(f"- {row['name']}: score={row['score']} total={row['total']} hit={row['hit']} flat={row['flat']} unresolved={row['unresolved']} avg_conf={row['avg_confidence']}")
    lines.append('')

    lines.append('## Worst Regimes')
    for row in summary['ranked_regimes']['worst']:
        lines.append(f"- {row['name']}: score={row['score']} total={row['total']} hit={row['hit']} flat={row['flat']} unresolved={row['unresolved']} avg_conf={row['avg_confidence']}")
    lines.append('')

    lines.append('## Best Clusters')
    for row in summary['ranked_clusters']['best']:
        lines.append(f"- {row['name']}: score={row['score']} total={row['total']} hit={row['hit']} flat={row['flat']} unresolved={row['unresolved']} avg_conf={row['avg_confidence']}")
    lines.append('')

    lines.append('## Worst Clusters')
    for row in summary['ranked_clusters']['worst']:
        lines.append(f"- {row['name']}: score={row['score']} total={row['total']} hit={row['hit']} flat={row['flat']} unresolved={row['unresolved']} avg_conf={row['avg_confidence']}")
    lines.append('')

    lines.append('## 建议动作')
    lines.append('- 把 high-flat 的 regime/cluster 降低注意力权重。')
    lines.append('- 优先保留 hit rate / score 更好的方向进入样刊主栏。')
    lines.append('- 继续以周报验证情报质量，而不是直接推进自动真钱。')
    return '\n'.join(lines)


def main() -> None:
    summary = build_summary()
    OUT_JSON.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    markdown = render_md(summary)
    OUT_MD.write_text(markdown, encoding='utf-8')
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    date_str = summary['generated_at'][:10]
    (REPORTS_DIR / f'{date_str}.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    (REPORTS_DIR / f'{date_str}.md').write_text(markdown, encoding='utf-8')
    print(f'wrote {OUT_MD} and {OUT_JSON}')


if __name__ == '__main__':
    main()
