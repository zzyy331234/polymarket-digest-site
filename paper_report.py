#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List

CONFIG_FILE = Path('/Users/mac/.openclaw/workspace/polymarket/trading_config.json')

PORTFOLIO_FILE = Path('/Users/mac/.openclaw/workspace/polymarket/portfolio_state.json')
TRADE_LOG = Path('/Users/mac/.openclaw/workspace/polymarket/trade_log.jsonl')
SUMMARY_JSON = Path('/Users/mac/.openclaw/workspace/polymarket/outputs/paper_summary.json')
SUMMARY_MD = Path('/Users/mac/.openclaw/workspace/polymarket/outputs/paper_summary.md')
PATCH_JSON = Path('/Users/mac/.openclaw/workspace/polymarket/outputs/proposed_config_patch.json')
PATCH_MD = Path('/Users/mac/.openclaw/workspace/polymarket/outputs/proposed_config_patch.md')
CYCLE_JSON = Path('/Users/mac/.openclaw/workspace/polymarket/outputs/paper_cycle_latest.json')


def load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding='utf-8'))


def load_events() -> List[Dict]:
    if not TRADE_LOG.exists():
        return []
    rows = []
    for line in TRADE_LOG.read_text(encoding='utf-8').splitlines():
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except Exception:
            continue
    return rows


def mean(nums: List[float]) -> float:
    return round(sum(nums) / len(nums), 6) if nums else 0.0


def realized_from_event(event: Dict):
    if event.get('realized_pnl_like') is not None:
        return float(event.get('realized_pnl_like') or 0)
    if event.get('pnl_like') is not None and event.get('size_usd') is not None:
        return float(event.get('pnl_like') or 0) * float(event.get('size_usd') or 0)
    try:
        entry = float(event.get('entry_yes_price', 0) or 0)
        exit_p = float(event.get('exit_yes_price', entry) or entry)
        move = exit_p - entry
        pnl_like = move if event.get('direction') == 'YES' else -move
        return pnl_like * float(event.get('size_usd', 0) or 0)
    except Exception:
        return None


def classify_bucket(confidence, config: Dict) -> str:
    buckets = (config.get('discipline_v2') or {}).get('buckets') or {}
    high_confidence_min = float(buckets.get('high_confidence_min', 0.65) or 0.65)
    main_pool_min = float(buckets.get('main_pool_min', 0.58) or 0.58)
    research_min = float(buckets.get('research_min', 0.50) or 0.50)
    conf = float(confidence or 0)
    if conf >= high_confidence_min:
        return 'high_confidence'
    if conf >= main_pool_min:
        return 'main_pool'
    if conf >= research_min:
        return 'research'
    return 'below_floor'


def bucket_execution_policy(bucket: str, config: Dict) -> str:
    execution = ((config.get('discipline_v2') or {}).get('execution') or {})
    trade_buckets = set(execution.get('trade_buckets', ['high_confidence', 'main_pool']))
    observe_only_buckets = set(execution.get('observe_only_buckets', ['research']))
    blocked_buckets = set(execution.get('blocked_buckets', ['below_floor']))
    if bucket in blocked_buckets:
        return 'blocked'
    if bucket in observe_only_buckets:
        return 'observe_only'
    if bucket in trade_buckets:
        return 'trade'
    return 'blocked'


def signal_execution_policy(signal: Dict, config: Dict) -> str:
    discipline = config.get('discipline_v2') or {}
    execution = discipline.get('execution') or {}
    overrides = execution.get('overrides') or {}
    cluster = signal.get('cluster', 'other')
    regime = signal.get('regime', 'other')
    bucket = classify_bucket(signal.get('confidence'), config)

    blocked_clusters = set(overrides.get('blocked_clusters', []))
    observe_only_clusters = set(overrides.get('observe_only_clusters', []))
    blocked_regimes = set(overrides.get('blocked_regimes', []))
    observe_only_regimes = set(overrides.get('observe_only_regimes', []))

    if cluster in blocked_clusters or regime in blocked_regimes:
        return 'blocked'
    if cluster in observe_only_clusters or regime in observe_only_regimes:
        return 'observe_only'
    return bucket_execution_policy(bucket, config)


def event_bucket(event: Dict, config: Dict) -> str:
    return event.get('signal_bucket') or classify_bucket(event.get('confidence'), config)


def event_execution_policy(event: Dict, config: Dict) -> str:
    return event.get('execution_policy') or signal_execution_policy(event, config)


def make_recommendation(scope: str, target: str, stats: Dict, *, min_samples: int = 3) -> Dict:
    closed = int(stats.get('closed', 0) or 0)
    win_rate = float(stats.get('win_rate', 0) or 0)
    flat_rate = float(stats.get('flat_rate', 0) or 0)
    pnl = float(stats.get('realized_pnl_like', 0) or 0)

    if closed < min_samples:
        return {
            'scope': scope,
            'target': target,
            'action': 'monitor',
            'priority': 'low',
            'reason': f'样本不足: closed={closed} < {min_samples}',
        }

    if scope == 'cluster':
        if flat_rate >= 0.90 and pnl <= 0:
            return {
                'scope': scope,
                'target': target,
                'action': 'block',
                'priority': 'high',
                'reason': f'flat_rate={flat_rate:.2%}, pnl={pnl:.4f}, closed={closed}',
            }
        if flat_rate >= 0.70 and win_rate == 0 and pnl <= 0:
            return {
                'scope': scope,
                'target': target,
                'action': 'observe_only',
                'priority': 'medium',
                'reason': f'win_rate={win_rate:.2%}, flat_rate={flat_rate:.2%}, pnl={pnl:.4f}',
            }
    elif scope == 'regime':
        if flat_rate >= 0.85 and pnl <= 0:
            return {
                'scope': scope,
                'target': target,
                'action': 'observe_only',
                'priority': 'high',
                'reason': f'flat_rate={flat_rate:.2%}, pnl={pnl:.4f}, closed={closed}',
            }
        if win_rate == 0 and pnl < 0 and closed >= max(4, min_samples):
            return {
                'scope': scope,
                'target': target,
                'action': 'downgrade',
                'priority': 'medium',
                'reason': f'win_rate={win_rate:.2%}, pnl={pnl:.4f}, closed={closed}',
            }
    elif scope == 'bucket':
        if flat_rate >= 0.70 and win_rate < 0.30 and pnl <= 0:
            return {
                'scope': scope,
                'target': target,
                'action': 'tighten_gate',
                'priority': 'high',
                'reason': f'win_rate={win_rate:.2%}, flat_rate={flat_rate:.2%}, pnl={pnl:.4f}',
            }

    return {
        'scope': scope,
        'target': target,
        'action': 'keep',
        'priority': 'low',
        'reason': f'closed={closed}, win_rate={win_rate:.2%}, flat_rate={flat_rate:.2%}, pnl={pnl:.4f}',
    }


def merge_unique_sorted(existing, additions):
    merged = list(existing or [])
    for item in additions or []:
        if item not in merged:
            merged.append(item)
    return sorted(merged)


def build_patch_proposal(config: Dict, summary: Dict) -> Dict:
    discipline = config.get('discipline_v2') or {}
    buckets = discipline.get('buckets') or {}
    execution = discipline.get('execution') or {}
    overrides = execution.get('overrides') or {}
    recommendations = summary.get('recommendations', [])

    blocked_clusters = list(overrides.get('blocked_clusters', []))
    observe_only_clusters = list(overrides.get('observe_only_clusters', []))
    blocked_regimes = list(overrides.get('blocked_regimes', []))
    observe_only_regimes = list(overrides.get('observe_only_regimes', []))
    high_confidence_min = float(buckets.get('high_confidence_min', 0.68) or 0.68)

    changes = []

    for rec in recommendations:
        scope = rec.get('scope')
        target = rec.get('target')
        action = rec.get('action')
        priority = rec.get('priority')
        reason = rec.get('reason')
        if priority not in ('high', 'medium'):
            continue

        if scope == 'cluster' and action == 'block':
            if target not in blocked_clusters:
                blocked_clusters.append(target)
                changes.append({
                    'path': 'discipline_v2.execution.overrides.blocked_clusters',
                    'action': 'add',
                    'value': target,
                    'reason': reason,
                })
        elif scope == 'cluster' and action == 'observe_only':
            if target not in observe_only_clusters:
                observe_only_clusters.append(target)
                changes.append({
                    'path': 'discipline_v2.execution.overrides.observe_only_clusters',
                    'action': 'add',
                    'value': target,
                    'reason': reason,
                })
        elif scope == 'regime' and action in ('observe_only', 'downgrade'):
            if target not in observe_only_regimes:
                observe_only_regimes.append(target)
                changes.append({
                    'path': 'discipline_v2.execution.overrides.observe_only_regimes',
                    'action': 'add',
                    'value': target,
                    'reason': reason,
                })
        elif scope == 'regime' and action == 'block':
            if target not in blocked_regimes:
                blocked_regimes.append(target)
                changes.append({
                    'path': 'discipline_v2.execution.overrides.blocked_regimes',
                    'action': 'add',
                    'value': target,
                    'reason': reason,
                })
        elif scope == 'bucket' and target == 'high_confidence' and action == 'tighten_gate':
            proposed = round(min(high_confidence_min + 0.02, 0.75), 2)
            if proposed > high_confidence_min:
                changes.append({
                    'path': 'discipline_v2.buckets.high_confidence_min',
                    'action': 'replace',
                    'from': high_confidence_min,
                    'to': proposed,
                    'reason': reason,
                })
                high_confidence_min = proposed

    proposed_config = json.loads(json.dumps(config))
    proposed_discipline = proposed_config.setdefault('discipline_v2', {})
    proposed_buckets = proposed_discipline.setdefault('buckets', {})
    proposed_execution = proposed_discipline.setdefault('execution', {})
    proposed_overrides = proposed_execution.setdefault('overrides', {})

    proposed_buckets['high_confidence_min'] = high_confidence_min
    proposed_overrides['blocked_clusters'] = merge_unique_sorted(proposed_overrides.get('blocked_clusters', []), blocked_clusters)
    proposed_overrides['observe_only_clusters'] = merge_unique_sorted(proposed_overrides.get('observe_only_clusters', []), observe_only_clusters)
    proposed_overrides['blocked_regimes'] = merge_unique_sorted(proposed_overrides.get('blocked_regimes', []), blocked_regimes)
    proposed_overrides['observe_only_regimes'] = merge_unique_sorted(proposed_overrides.get('observe_only_regimes', []), observe_only_regimes)

    return {
        'generated_at': datetime.now().isoformat(timespec='seconds'),
        'requires_manual_review': True,
        'summary_source': str(SUMMARY_JSON),
        'change_count': len(changes),
        'changes': changes,
        'proposed_config_excerpt': {
            'discipline_v2': proposed_config.get('discipline_v2', {})
        },
    }


def summarize() -> Dict:
    config = load_json(CONFIG_FILE, {})
    discipline = config.get('discipline_v2') or {}
    release_gate = (discipline.get('release_gates') or {}).get('paper_to_micro_live') or {}
    portfolio = load_json(PORTFOLIO_FILE, {'positions': [], 'portfolio_health': {}})
    cycle = load_json(CYCLE_JSON, {})
    events = load_events()

    opens = [e for e in events if e.get('type') == 'open']
    closes = [e for e in events if e.get('type') == 'close']
    skips = [e for e in events if e.get('type') == 'skip']
    halts = [e for e in events if e.get('type') == 'halt']

    realized = [x for x in (realized_from_event(e) for e in closes) if x is not None]
    wins = [x for x in realized if x > 0]
    losses = [x for x in realized if x < 0]

    close_reasons = Counter(e.get('close_reason', 'unknown') for e in closes)
    skip_reasons = Counter(e.get('reason', 'unknown') for e in skips)
    regime_stats = defaultdict(lambda: {'closed': 0, 'realized_pnl_like': 0.0, 'wins': 0, 'flat': 0})
    cluster_stats = defaultdict(lambda: {'closed': 0, 'realized_pnl_like': 0.0, 'wins': 0, 'flat': 0})
    bucket_stats = defaultdict(lambda: {'closed': 0, 'realized_pnl_like': 0.0, 'wins': 0, 'flat': 0})
    policy_stats = defaultdict(lambda: {'closed': 0, 'realized_pnl_like': 0.0, 'wins': 0, 'flat': 0})

    flat_threshold = 0.000001
    for e in closes:
        regime = e.get('regime', 'other')
        cluster = e.get('cluster', 'other')
        bucket = event_bucket(e, config)
        policy = event_execution_policy(e, config)
        pnl = float(realized_from_event(e) or 0)
        is_flat = abs(pnl) <= flat_threshold
        regime_stats[regime]['closed'] += 1
        regime_stats[regime]['realized_pnl_like'] += pnl
        regime_stats[regime]['wins'] += 1 if pnl > 0 else 0
        regime_stats[regime]['flat'] += 1 if is_flat else 0
        cluster_stats[cluster]['closed'] += 1
        cluster_stats[cluster]['realized_pnl_like'] += pnl
        cluster_stats[cluster]['wins'] += 1 if pnl > 0 else 0
        cluster_stats[cluster]['flat'] += 1 if is_flat else 0
        bucket_stats[bucket]['closed'] += 1
        bucket_stats[bucket]['realized_pnl_like'] += pnl
        bucket_stats[bucket]['wins'] += 1 if pnl > 0 else 0
        bucket_stats[bucket]['flat'] += 1 if is_flat else 0
        policy_stats[policy]['closed'] += 1
        policy_stats[policy]['realized_pnl_like'] += pnl
        policy_stats[policy]['wins'] += 1 if pnl > 0 else 0
        policy_stats[policy]['flat'] += 1 if is_flat else 0

    current_open = [p for p in portfolio.get('positions', []) if p.get('status') == 'open']
    current_closed = [p for p in portfolio.get('positions', []) if p.get('status') == 'closed']
    open_policy_counts = Counter(event_execution_policy(p, config) for p in current_open)
    closed_policy_counts = Counter(event_execution_policy(p, config) for p in current_closed)
    open_events_by_policy = Counter(event_execution_policy(e, config) for e in opens)
    skip_events_by_policy = Counter(event_execution_policy(e, config) for e in skips)

    avg_win_loss_ratio_like = None
    if wins and losses and abs(mean(losses)) > 0:
        avg_win_loss_ratio_like = round(abs(mean(wins) / mean(losses)), 4)
    flat_count = sum(1 for x in realized if abs(x) <= flat_threshold)
    flat_rate = round(flat_count / len(realized), 4) if realized else 0.0
    recent_consecutive_losses = int((portfolio.get('portfolio_health') or {}).get('recent_fail_count', 0) or 0)
    gate_checks = {
        'min_closed_trades': len(realized) >= int(release_gate.get('min_closed_trades', 30) or 30),
        'min_win_rate': (round(len(wins) / len(realized), 4) if realized else 0.0) >= float(release_gate.get('min_win_rate', 0.55) or 0.55),
        'min_avg_win_loss_ratio_like': (avg_win_loss_ratio_like or 0.0) >= float(release_gate.get('min_avg_win_loss_ratio_like', 1.3) or 1.3),
        'max_consecutive_losses': recent_consecutive_losses <= int(release_gate.get('max_consecutive_losses', 3) or 3),
        'max_flat_rate': flat_rate <= float(release_gate.get('max_flat_rate', 0.50) or 0.50),
    }
    regime_summary = {
        k: {
            'closed': v['closed'],
            'wins': v['wins'],
            'flat': v['flat'],
            'win_rate': round(v['wins'] / v['closed'], 4) if v['closed'] else 0.0,
            'flat_rate': round(v['flat'] / v['closed'], 4) if v['closed'] else 0.0,
            'realized_pnl_like': round(v['realized_pnl_like'], 6),
        }
        for k, v in regime_stats.items()
    }
    cluster_summary = {
        k: {
            'closed': v['closed'],
            'wins': v['wins'],
            'flat': v['flat'],
            'win_rate': round(v['wins'] / v['closed'], 4) if v['closed'] else 0.0,
            'flat_rate': round(v['flat'] / v['closed'], 4) if v['closed'] else 0.0,
            'realized_pnl_like': round(v['realized_pnl_like'], 6),
        }
        for k, v in cluster_stats.items()
    }
    bucket_summary = {
        k: {
            'closed': v['closed'],
            'wins': v['wins'],
            'flat': v['flat'],
            'win_rate': round(v['wins'] / v['closed'], 4) if v['closed'] else 0.0,
            'flat_rate': round(v['flat'] / v['closed'], 4) if v['closed'] else 0.0,
            'realized_pnl_like': round(v['realized_pnl_like'], 6),
        }
        for k, v in bucket_stats.items()
    }
    policy_summary = {
        k: {
            'closed': v['closed'],
            'wins': v['wins'],
            'flat': v['flat'],
            'win_rate': round(v['wins'] / v['closed'], 4) if v['closed'] else 0.0,
            'flat_rate': round(v['flat'] / v['closed'], 4) if v['closed'] else 0.0,
            'realized_pnl_like': round(v['realized_pnl_like'], 6),
        }
        for k, v in policy_stats.items()
    }
    recommendations = [
        {
            'scope': 'overall',
            'target': 'paper_to_micro_live',
            'action': 'stay_paper' if not all(gate_checks.values()) else 'micro_live_candidate',
            'priority': 'high' if not all(gate_checks.values()) else 'medium',
            'reason': f"eligible={all(gate_checks.values())}, closed={len(realized)}, win_rate={(round(len(wins) / len(realized), 4) if realized else 0.0):.2%}, flat_rate={flat_rate:.2%}",
        }
    ]
    recommendations.extend(make_recommendation('regime', k, v, min_samples=3) for k, v in regime_summary.items())
    recommendations.extend(make_recommendation('cluster', k, v, min_samples=3) for k, v in cluster_summary.items())
    recommendations.extend(make_recommendation('bucket', k, v, min_samples=3) for k, v in bucket_summary.items())
    recommendations = sorted(
        recommendations,
        key=lambda x: ({'high': 0, 'medium': 1, 'low': 2}.get(x.get('priority', 'low'), 9), x.get('scope', ''), x.get('target', ''))
    )
    summary = {
        'generated_at': datetime.now().isoformat(timespec='seconds'),
        'discipline_v2': {
            'version': discipline.get('version', 'v2'),
            'buckets': discipline.get('buckets', {}),
            'execution': discipline.get('execution', {}),
            'paper_to_micro_live_gate': {
                'thresholds': release_gate,
                'actuals': {
                    'closed_trades': len(realized),
                    'win_rate': round(len(wins) / len(realized), 4) if realized else 0.0,
                    'avg_win_loss_ratio_like': avg_win_loss_ratio_like,
                    'recent_consecutive_losses': recent_consecutive_losses,
                    'flat_rate': flat_rate,
                },
                'checks': gate_checks,
                'eligible': all(gate_checks.values()) if gate_checks else False,
            },
        },
        'events': {
            'open_count': len(opens),
            'close_count': len(closes),
            'skip_count': len(skips),
            'halt_count': len(halts),
        },
        'portfolio': {
            'open_positions': len(current_open),
            'closed_positions': len(current_closed),
            'open_policy_counts': dict(open_policy_counts),
            'closed_policy_counts': dict(closed_policy_counts),
            'portfolio_health': portfolio.get('portfolio_health', {}),
        },
        'performance': {
            'realized_trade_count': len(realized),
            'win_count': len(wins),
            'loss_count': len(losses),
            'flat_count': flat_count,
            'win_rate': round(len(wins) / len(realized), 4) if realized else 0.0,
            'flat_rate': flat_rate,
            'avg_realized_pnl_like': mean(realized),
            'avg_win': mean(wins),
            'avg_loss': mean(losses),
            'avg_win_loss_ratio_like': avg_win_loss_ratio_like,
            'profit_factor_like': round(sum(wins) / abs(sum(losses)), 4) if losses and sum(losses) != 0 else None,
            'total_realized_pnl_like': round(sum(realized), 6),
        },
        'reasons': {
            'close_reasons': dict(close_reasons),
            'skip_reasons': dict(skip_reasons),
        },
        'execution_scope': {
            'open_events_by_policy': dict(open_events_by_policy),
            'skip_events_by_policy': dict(skip_events_by_policy),
        },
        'by_regime': regime_summary,
        'by_cluster': cluster_summary,
        'by_bucket': bucket_summary,
        'by_execution_policy': policy_summary,
        'recommendations': recommendations,
        'latest_cycle': cycle,
    }
    return summary


def save(summary: Dict) -> None:
    SUMMARY_JSON.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_JSON.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')

    patch_proposal = build_patch_proposal(load_json(CONFIG_FILE, {}), summary)
    PATCH_JSON.write_text(json.dumps(patch_proposal, ensure_ascii=False, indent=2), encoding='utf-8')

    perf = summary['performance']
    evt = summary['events']
    health = summary['portfolio']['portfolio_health']
    gate = summary['discipline_v2']['paper_to_micro_live_gate']
    md = [
        '# Paper Trade Summary',
        '',
        f"- 生成时间: {summary['generated_at']}",
        f"- 纪律版本: {summary['discipline_v2']['version']}",
        f"- 执行桶: trade={summary['discipline_v2']['execution'].get('trade_buckets', [])} observe_only={summary['discipline_v2']['execution'].get('observe_only_buckets', [])} blocked={summary['discipline_v2']['execution'].get('blocked_buckets', [])}",
        f"- open / close / skip / halt: {evt['open_count']} / {evt['close_count']} / {evt['skip_count']} / {evt['halt_count']}",
        f"- 当前持仓: {summary['portfolio']['open_positions']} open / {summary['portfolio']['closed_positions']} closed",
        f"- 实现交易数: {perf['realized_trade_count']}",
        f"- 胜率: {perf['win_rate']:.2%}",
        f"- flat rate: {perf['flat_rate']:.2%}",
        f"- 平均单笔 realized_pnl_like: {perf['avg_realized_pnl_like']:.4f}",
        f"- 平均盈利 / 平均亏损: {perf['avg_win']:.4f} / {perf['avg_loss']:.4f}",
        f"- 平均盈亏比 like: {perf['avg_win_loss_ratio_like'] if perf['avg_win_loss_ratio_like'] is not None else 'N/A'}",
        f"- total realized_pnl_like: {perf['total_realized_pnl_like']:.4f}",
        f"- profit_factor_like: {perf['profit_factor_like'] if perf['profit_factor_like'] is not None else 'N/A'}",
        f"- 当前 halt: {health.get('halted')} ({health.get('halt_reason')})",
        '',
        '## Discipline v2 Gate (Paper → Micro Live)',
        f"- eligible: {gate['eligible']}",
        f"- closed_trades: {gate['actuals']['closed_trades']} / >= {gate['thresholds'].get('min_closed_trades', 30)}",
        f"- win_rate: {gate['actuals']['win_rate']:.2%} / >= {gate['thresholds'].get('min_win_rate', 0.55):.0%}",
        f"- avg_win_loss_ratio_like: {gate['actuals']['avg_win_loss_ratio_like'] if gate['actuals']['avg_win_loss_ratio_like'] is not None else 'N/A'} / >= {gate['thresholds'].get('min_avg_win_loss_ratio_like', 1.3)}",
        f"- recent_consecutive_losses: {gate['actuals']['recent_consecutive_losses']} / <= {gate['thresholds'].get('max_consecutive_losses', 3)}",
        f"- flat_rate: {gate['actuals']['flat_rate']:.2%} / <= {gate['thresholds'].get('max_flat_rate', 0.50):.0%}",
        '',
        '## Execution Scope Split',
        f"- 当前 open positions by policy: {summary['portfolio']['open_policy_counts']}",
        f"- 当前 closed positions by policy: {summary['portfolio']['closed_policy_counts']}",
        f"- 历史 open events by policy: {summary['execution_scope']['open_events_by_policy']}",
        f"- 历史 skip events by policy: {summary['execution_scope']['skip_events_by_policy']}",
        '',
        '## Auto Downgrade Suggestions',
    ]
    for rec in summary['recommendations']:
        md.append(f"- [{rec['priority']}] {rec['scope']}/{rec['target']} -> {rec['action']} | {rec['reason']}")

    md.extend(['', '## Close Reasons'])
    if summary['reasons']['close_reasons']:
        for k, v in summary['reasons']['close_reasons'].items():
            md.append(f'- {k}: {v}')
    else:
        md.append('- 暂无 close 记录')

    md.extend(['', '## Skip Reasons'])
    if summary['reasons']['skip_reasons']:
        for k, v in summary['reasons']['skip_reasons'].items():
            md.append(f'- {k}: {v}')
    else:
        md.append('- 暂无 skip 记录')

    md.extend(['', '## By Regime'])
    if summary['by_regime']:
        for k, v in summary['by_regime'].items():
            md.append(f"- {k}: closed={v['closed']} wins={v['wins']} win_rate={v['win_rate']:.2%} pnl={v['realized_pnl_like']:.4f}")
    else:
        md.append('- 暂无 regime 统计')

    md.extend(['', '## By Cluster'])
    if summary['by_cluster']:
        for k, v in summary['by_cluster'].items():
            md.append(f"- {k}: closed={v['closed']} wins={v['wins']} flat={v['flat']} win_rate={v['win_rate']:.2%} flat_rate={v['flat_rate']:.2%} pnl={v['realized_pnl_like']:.4f}")
    else:
        md.append('- 暂无 cluster 统计')

    md.extend(['', '## By Bucket'])
    if summary['by_bucket']:
        for k, v in summary['by_bucket'].items():
            md.append(f"- {k}: closed={v['closed']} wins={v['wins']} flat={v['flat']} win_rate={v['win_rate']:.2%} flat_rate={v['flat_rate']:.2%} pnl={v['realized_pnl_like']:.4f}")
    else:
        md.append('- 暂无 bucket 统计')

    md.extend(['', '## By Execution Policy'])
    if summary['by_execution_policy']:
        for k, v in summary['by_execution_policy'].items():
            md.append(f"- {k}: closed={v['closed']} wins={v['wins']} flat={v['flat']} win_rate={v['win_rate']:.2%} flat_rate={v['flat_rate']:.2%} pnl={v['realized_pnl_like']:.4f}")
    else:
        md.append('- 暂无 execution policy 统计')

    SUMMARY_MD.write_text('\n'.join(md) + '\n', encoding='utf-8')

    patch_md = [
        '# Proposed Config Patch',
        '',
        f"- 生成时间: {patch_proposal['generated_at']}",
        f"- requires_manual_review: {patch_proposal['requires_manual_review']}",
        f"- change_count: {patch_proposal['change_count']}",
        '',
        '## Proposed Changes',
    ]
    if patch_proposal['changes']:
        for change in patch_proposal['changes']:
            if change['action'] == 'replace':
                patch_md.append(
                    f"- {change['path']}: {change['from']} -> {change['to']} | {change['reason']}"
                )
            else:
                patch_md.append(
                    f"- {change['path']}: add {change['value']} | {change['reason']}"
                )
    else:
        patch_md.append('- 当前没有新的配置补丁建议')

    patch_md.extend(['', '## Proposed Config Excerpt', json.dumps(patch_proposal['proposed_config_excerpt'], ensure_ascii=False, indent=2)])
    PATCH_MD.write_text('\n'.join(patch_md) + '\n', encoding='utf-8')


if __name__ == '__main__':
    result = summarize()
    save(result)
    patch = build_patch_proposal(load_json(CONFIG_FILE, {}), result)
    print(
        f"summary={SUMMARY_JSON} patch={PATCH_JSON} realized={result['performance']['realized_trade_count']} "
        f"win_rate={result['performance']['win_rate']:.2%} open={result['portfolio']['open_positions']} changes={patch['change_count']}"
    )
