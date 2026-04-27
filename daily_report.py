#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
from datetime import datetime
from pathlib import Path

from status_overview import build_status

REPORT_DIR = Path('/Users/mac/.openclaw/workspace/polymarket/reports/daily')
LATEST_MD = Path('/Users/mac/.openclaw/workspace/polymarket/outputs/daily_report_latest.md')
LATEST_JSON = Path('/Users/mac/.openclaw/workspace/polymarket/outputs/daily_report_latest.json')


def fmt_pct(value):
    if value is None:
        return 'N/A'
    return f'{float(value):.2%}'


def fmt_num(value, digits=4):
    if value is None:
        return 'N/A'
    return f'{float(value):.{digits}f}'


def build_report(date_str: str):
    status = build_status()
    cycle = status.get('latest_cycle', {})
    paper = status.get('paper_status', {})
    gate = status.get('gate', {})
    proposal = status.get('proposal', {})
    recs = status.get('top_recommendations', [])
    execution = status.get('execution', {})

    lines = [
        f'# Polymarket 日报 - {date_str}',
        '',
        '## 今日结论',
        f"- 当前阶段：{status.get('mode')} / discipline {status.get('discipline_version')}",
        f"- Paper → Micro Live 放行：{'可考虑' if gate.get('eligible') else '未达标，继续 paper'}",
        f"- 最新 paper：realized_trade_count={paper.get('realized_trade_count')} / win_rate={fmt_pct(paper.get('win_rate'))} / flat_rate={fmt_pct(paper.get('flat_rate'))} / total_realized_pnl_like={fmt_num(paper.get('total_realized_pnl_like'))}",
        f"- 最新 proposal：change_count={proposal.get('change_count', 0)} / requires_manual_review={proposal.get('requires_manual_review')}",
        '',
        '## 当前配置与执行口径',
        f"- bucket_thresholds: {status.get('bucket_thresholds')}",
        f"- trade_buckets: {execution.get('trade_buckets', [])}",
        f"- observe_only_buckets: {execution.get('observe_only_buckets', [])}",
        f"- blocked_buckets: {execution.get('blocked_buckets', [])}",
        f"- overrides: {execution.get('overrides', {})}",
        '',
        '## 最新周期',
        f"- ran_at: {cycle.get('ran_at')}",
        f"- ready_count: {cycle.get('ready_count')} / ready_buckets: {cycle.get('ready_buckets', {})}",
        f"- opened: {cycle.get('opened')} / opened_buckets: {cycle.get('opened_buckets', {})}",
        f"- closed: {cycle.get('closed')} / skipped: {cycle.get('skipped')} / skipped_buckets: {cycle.get('skipped_buckets', {})}",
        f"- skip_reasons: {cycle.get('skip_reasons', {})}",
        '',
        '## Paper 表现',
        f"- open_positions: {paper.get('open_positions')} / closed_positions: {paper.get('closed_positions')}",
        f"- open_policy_counts: {paper.get('open_policy_counts', {})}",
        f"- closed_policy_counts: {paper.get('closed_policy_counts', {})}",
        '',
        '## Gate 检查（Paper → Micro Live）',
        f"- eligible: {gate.get('eligible')}",
        f"- actuals: {gate.get('actuals', {})}",
        f"- thresholds: {gate.get('thresholds', {})}",
        '',
        '## Proposal',
        f"- generated_at: {proposal.get('generated_at')}",
        f"- change_count: {proposal.get('change_count', 0)}",
        f"- requires_manual_review: {proposal.get('requires_manual_review')}",
    ]

    changes = proposal.get('changes', []) or []
    if changes:
        for change in changes:
            if change.get('action') == 'replace':
                lines.append(f"- {change.get('path')}: {change.get('from')} -> {change.get('to')} | {change.get('reason')}")
            else:
                lines.append(f"- {change.get('path')}: add {change.get('value')} | {change.get('reason')}")
    else:
        lines.append('- 今日无新的 proposal 变更')

    lines.extend(['', '## Top Recommendations'])
    if recs:
        for rec in recs:
            lines.append(f"- [{rec.get('priority')}] {rec.get('scope')}/{rec.get('target')} -> {rec.get('action')} | {rec.get('reason')}")
    else:
        lines.append('- 今日无推荐动作')

    lines.extend(['', '## 建议动作'])
    if not gate.get('eligible'):
        lines.append('- 继续保持 paper，不进入 micro live。')
    if changes:
        lines.append('- 审核 proposed_config_patch，确认是否应用。')
    if any(rec.get('action') == 'tighten_gate' for rec in recs):
        lines.append('- 继续关注 high_confidence 桶是否还需要进一步收紧。')
    if any(rec.get('action') in ('block', 'observe_only') for rec in recs):
        lines.append('- 持续观察被 block / observe_only 的 cluster 与 regime 是否仍然合理。')

    report = {
        'date': date_str,
        'generated_at': datetime.now().isoformat(timespec='seconds'),
        'status': status,
        'markdown': '\n'.join(lines) + '\n',
    }
    return report


def main():
    parser = argparse.ArgumentParser(description='Generate daily report for Polymarket system')
    parser.add_argument('--date', default=datetime.now().date().isoformat(), help='Report date, e.g. 2026-04-19')
    parser.add_argument('--stdout', action='store_true', help='Print markdown to stdout')
    args = parser.parse_args()

    report = build_report(args.date)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    md_path = REPORT_DIR / f'{args.date}.md'
    json_path = REPORT_DIR / f'{args.date}.json'

    md_path.write_text(report['markdown'], encoding='utf-8')
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    LATEST_MD.write_text(report['markdown'], encoding='utf-8')
    LATEST_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    print(f'report_md={md_path} report_json={json_path}')
    if args.stdout:
        print('---')
        print(report['markdown'])


if __name__ == '__main__':
    main()
