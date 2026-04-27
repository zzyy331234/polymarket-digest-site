#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

CONFIG_FILE = Path('/Users/mac/.openclaw/workspace/polymarket/trading_config.json')
CYCLE_FILE = Path('/Users/mac/.openclaw/workspace/polymarket/outputs/paper_cycle_latest.json')
SUMMARY_FILE = Path('/Users/mac/.openclaw/workspace/polymarket/outputs/paper_summary.json')
PROPOSAL_FILE = Path('/Users/mac/.openclaw/workspace/polymarket/outputs/proposed_config_patch.json')
APPLY_LOG_FILE = Path('/Users/mac/.openclaw/workspace/polymarket/outputs/applied_config_patches.jsonl')


def load_json(path: Path, default=None):
    if default is None:
        default = {}
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding='utf-8'))


def load_jsonl_last(path: Path):
    if not path.exists():
        return None
    lines = [line for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]
    if not lines:
        return None
    return json.loads(lines[-1])


def top_recommendations(summary: Dict, limit: int = 5) -> List[Dict]:
    recs = summary.get('recommendations', []) or []
    priority_order = {'high': 0, 'medium': 1, 'low': 2}
    return sorted(recs, key=lambda x: (priority_order.get(x.get('priority', 'low'), 9), x.get('scope', ''), x.get('target', '')))[:limit]


def build_status() -> Dict[str, Any]:
    config = load_json(CONFIG_FILE, {})
    cycle = load_json(CYCLE_FILE, {})
    summary = load_json(SUMMARY_FILE, {})
    proposal = load_json(PROPOSAL_FILE, {})
    last_apply = load_jsonl_last(APPLY_LOG_FILE)

    discipline = config.get('discipline_v2') or {}
    execution = discipline.get('execution') or {}
    overrides = execution.get('overrides') or {}
    gate = ((summary.get('discipline_v2') or {}).get('paper_to_micro_live_gate') or {})
    perf = summary.get('performance') or {}
    portfolio = summary.get('portfolio') or {}

    status = {
        'mode': config.get('mode'),
        'discipline_version': discipline.get('version'),
        'bucket_thresholds': discipline.get('buckets', {}),
        'execution': {
            'trade_buckets': execution.get('trade_buckets', []),
            'observe_only_buckets': execution.get('observe_only_buckets', []),
            'blocked_buckets': execution.get('blocked_buckets', []),
            'overrides': {
                'blocked_clusters': overrides.get('blocked_clusters', []),
                'observe_only_clusters': overrides.get('observe_only_clusters', []),
                'blocked_regimes': overrides.get('blocked_regimes', []),
                'observe_only_regimes': overrides.get('observe_only_regimes', []),
            },
        },
        'latest_cycle': {
            'ran_at': cycle.get('ran_at'),
            'ready_count': cycle.get('ready_count'),
            'ready_buckets': cycle.get('ready_buckets', {}),
            'opened': cycle.get('opened'),
            'opened_buckets': cycle.get('opened_buckets', {}),
            'closed': cycle.get('closed'),
            'skipped': cycle.get('skipped'),
            'skipped_buckets': cycle.get('skipped_buckets', {}),
            'skip_reasons': cycle.get('skip_reasons', {}),
        },
        'paper_status': {
            'open_positions': portfolio.get('open_positions'),
            'closed_positions': portfolio.get('closed_positions'),
            'realized_trade_count': perf.get('realized_trade_count'),
            'win_rate': perf.get('win_rate'),
            'flat_rate': perf.get('flat_rate'),
            'total_realized_pnl_like': perf.get('total_realized_pnl_like'),
            'open_policy_counts': portfolio.get('open_policy_counts', {}),
            'closed_policy_counts': portfolio.get('closed_policy_counts', {}),
        },
        'gate': {
            'eligible': gate.get('eligible'),
            'actuals': gate.get('actuals', {}),
            'thresholds': gate.get('thresholds', {}),
        },
        'proposal': {
            'generated_at': proposal.get('generated_at'),
            'change_count': proposal.get('change_count', 0),
            'requires_manual_review': proposal.get('requires_manual_review'),
            'changes': proposal.get('changes', []),
        },
        'last_apply': last_apply or {},
        'top_recommendations': top_recommendations(summary),
    }
    return status


def print_human(status: Dict[str, Any]) -> None:
    print('=== Polymarket Status Overview ===')
    print(f"mode: {status.get('mode')}")
    print(f"discipline_version: {status.get('discipline_version')}")
    print(f"bucket_thresholds: {status.get('bucket_thresholds')}")
    print(f"trade_buckets: {status['execution'].get('trade_buckets')}")
    print(f"observe_only_buckets: {status['execution'].get('observe_only_buckets')}")
    print(f"blocked_buckets: {status['execution'].get('blocked_buckets')}")
    print(f"overrides: {status['execution'].get('overrides')}")
    print()

    cycle = status['latest_cycle']
    print('--- Latest Cycle ---')
    print(f"ran_at: {cycle.get('ran_at')}")
    print(f"ready_count: {cycle.get('ready_count')} ready_buckets={cycle.get('ready_buckets')}")
    print(f"opened={cycle.get('opened')} opened_buckets={cycle.get('opened_buckets')}")
    print(f"closed={cycle.get('closed')} skipped={cycle.get('skipped')} skipped_buckets={cycle.get('skipped_buckets')}")
    print(f"skip_reasons: {cycle.get('skip_reasons')}")
    print()

    paper = status['paper_status']
    print('--- Paper Status ---')
    print(f"open_positions={paper.get('open_positions')} closed_positions={paper.get('closed_positions')}")
    print(f"realized_trade_count={paper.get('realized_trade_count')} win_rate={paper.get('win_rate')} flat_rate={paper.get('flat_rate')}")
    print(f"total_realized_pnl_like={paper.get('total_realized_pnl_like')}")
    print(f"open_policy_counts={paper.get('open_policy_counts')}")
    print(f"closed_policy_counts={paper.get('closed_policy_counts')}")
    print()

    gate = status['gate']
    print('--- Gate (Paper -> Micro Live) ---')
    print(f"eligible={gate.get('eligible')}")
    print(f"actuals={gate.get('actuals')}")
    print(f"thresholds={gate.get('thresholds')}")
    print()

    proposal = status['proposal']
    print('--- Proposal ---')
    print(f"generated_at={proposal.get('generated_at')} change_count={proposal.get('change_count')} requires_manual_review={proposal.get('requires_manual_review')}")
    for change in proposal.get('changes', []):
        print(f"- {change}")
    if not proposal.get('changes'):
        print('- no pending proposed changes')
    print()

    print('--- Last Apply ---')
    if status['last_apply']:
        print(f"applied_at={status['last_apply'].get('applied_at')}")
        print(f"backup_file={status['last_apply'].get('backup_file')}")
        print(f"patch_file={status['last_apply'].get('patch_file')}")
    else:
        print('no apply history')
    print()

    print('--- Top Recommendations ---')
    recs = status.get('top_recommendations', [])
    if not recs:
        print('no recommendations')
    else:
        for rec in recs:
            print(f"- [{rec.get('priority')}] {rec.get('scope')}/{rec.get('target')} -> {rec.get('action')} | {rec.get('reason')}")


def main() -> None:
    parser = argparse.ArgumentParser(description='Show Polymarket trading system status overview')
    parser.add_argument('--json', action='store_true', help='Print JSON instead of human-readable text')
    args = parser.parse_args()

    status = build_status()
    if args.json:
        print(json.dumps(status, ensure_ascii=False, indent=2))
    else:
        print_human(status)


if __name__ == '__main__':
    main()
