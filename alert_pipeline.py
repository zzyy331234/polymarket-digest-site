#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from pathlib import Path
from typing import Dict, List

INPUT = Path('/Users/mac/.openclaw/workspace/polymarket/outputs/signals_v2_alerts.json')
OUTPUT = Path('/Users/mac/.openclaw/workspace/polymarket/outputs/alerts_ready.json')
SUMMARY = Path('/Users/mac/.openclaw/workspace/polymarket/outputs/alerts_summary.md')

MAX_TOTAL = 6
MAX_PER_CLUSTER = 2
MIN_CONF = 0.58


def load_alerts() -> List[Dict]:
    if not INPUT.exists():
        return []
    with open(INPUT, 'r', encoding='utf-8') as f:
        return json.load(f)


def score(sig: Dict) -> float:
    conf = float(sig.get('confidence', 0) or 0)
    regime_bonus = {
        'trend': 0.03,
        'mean_revert': 0.02,
        'contrarian': 0.01,
        'carry_no': 0.00,
    }.get(sig.get('regime'), 0.0)
    advisory_penalty = 0.03 * len(sig.get('advisory_flags', []))
    return conf + regime_bonus - advisory_penalty


def build_url(sig: Dict) -> str:
    slug = sig.get('slug')
    return f'https://polymarket.com/question/{slug}' if slug else ''


def build_templates(sig: Dict) -> Dict[str, str]:
    question = sig.get('question', '')
    regime = sig.get('regime', '-')
    direction = sig.get('direction', '-')
    conf = float(sig.get('confidence', 0) or 0)
    pos = sig.get('position', '-')
    yes_p = float(sig.get('yes_price', 0) or 0)
    reasons = ', '.join(sig.get('reasons', [])[:2]) or '-'
    url = build_url(sig)
    short_text = f"[{regime}] {direction} conf={conf:.2f} | {question} | {url}".strip()
    detailed_text = f"[{regime}] {direction} | conf={conf:.2f} | pos={pos} | yes={yes_p:.4f}\n{question}\n原因: {reasons}\n{url}".strip()
    execution_text = f"执行候选：[{regime}] {direction}\n问题：{question}\n建议仓位：{pos}\n当前YES：{yes_p:.4f}\n置信度：{conf:.2f}\n理由：{reasons}\n链接：{url}".strip()
    return {
        'short': short_text,
        'detailed': detailed_text,
        'execution': execution_text,
    }


def select(alerts: List[Dict]) -> List[Dict]:
    ranked = [
        dict(a, pipeline_score=score(a), cluster=a.get('cluster', 'other'), market_url=build_url(a))
        for a in alerts
        if float(a.get('confidence', 0) or 0) >= MIN_CONF and not a.get('blocking_flags')
    ]
    ranked.sort(key=lambda x: x['pipeline_score'], reverse=True)

    picked = []
    cluster_counts = {}
    seen_questions = set()
    for sig in ranked:
        q = sig.get('question', '')
        cluster = sig.get('cluster', 'other')
        if q in seen_questions:
            continue
        if cluster_counts.get(cluster, 0) >= MAX_PER_CLUSTER:
            continue
        picked.append(sig)
        seen_questions.add(q)
        cluster_counts[cluster] = cluster_counts.get(cluster, 0) + 1
        if len(picked) >= MAX_TOTAL:
            break
    return picked


def save(selected: List[Dict]) -> None:
    for sig in selected:
        sig['templates'] = build_templates(sig)
        sig['alert_text'] = sig['templates']['detailed']
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(selected, f, ensure_ascii=False, indent=2)

    lines = ['# Polymarket Alert Pipeline Summary', '']
    if not selected:
        lines.append('- 当前无可推送 alert。')
    else:
        for i, sig in enumerate(selected, 1):
            lines.append(f"## {i}. [{sig.get('regime','-')}] {sig.get('direction','-')} conf={sig.get('confidence',0):.2f}")
            lines.append(f"- 问题: {sig.get('question','')}")
            lines.append(f"- Cluster: {sig.get('cluster','-')}")
            lines.append(f"- URL: {sig.get('market_url','')}")
            lines.append(f"- 原因: {', '.join(sig.get('reasons', [])[:3]) or '-'}")
            lines.append('')
    SUMMARY.write_text('\n'.join(lines), encoding='utf-8')


if __name__ == '__main__':
    alerts = load_alerts()
    selected = select(alerts)
    save(selected)
    print(f'alerts_in={len(alerts)} alerts_ready={len(selected)} output={OUTPUT}')
