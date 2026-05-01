#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

from risk_manager import can_open, should_close

READY_FILE = Path('/Users/mac/.openclaw/workspace/polymarket/outputs/alerts_ready.json')
LATEST_FILE = Path('/Users/mac/.openclaw/workspace/polymarket/outputs/signals_v2_latest.json')
PORTFOLIO_FILE = Path('/Users/mac/.openclaw/workspace/polymarket/portfolio_state.json')
TRADE_LOG = Path('/Users/mac/.openclaw/workspace/polymarket/trade_log.jsonl')
CONFIG_FILE = Path('/Users/mac/.openclaw/workspace/polymarket/trading_config.json')
CYCLE_SUMMARY_FILE = Path('/Users/mac/.openclaw/workspace/polymarket/outputs/paper_cycle_latest.json')


def now_iso() -> str:
    return datetime.now().isoformat(timespec='seconds')


def load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding='utf-8'))


def load_portfolio() -> Dict:
    return load_json(PORTFOLIO_FILE, {'positions': [], 'cash': 20.0, 'updated_at': now_iso()})


def load_config() -> Dict:
    return load_json(CONFIG_FILE, {
        'mode': 'paper_trade',
        'daily_budget_usd': 12.0,
        'max_total_exposure_usd': 6.0,
        'max_single_size_usd': 3.0,
        'auto_trade_enabled': True,
        'live_trade_enabled': False,
        'emergency_stop': False,
        'max_daily_loss_like': -0.12,
        'paper_review_only': False,
        'consecutive_fail_halt': 3,
        'allowed_modes': ['analysis_only', 'paper_review_only', 'paper_trade', 'live_disabled'],
        'discipline_v2': {
            'version': 'v2',
            'buckets': {
                'high_confidence_min': 0.65,
                'main_pool_min': 0.58,
                'research_min': 0.50,
            },
            'release_gates': {
                'paper_to_micro_live': {
                    'min_closed_trades': 30,
                    'min_win_rate': 0.55,
                    'min_avg_win_loss_ratio_like': 1.3,
                    'max_consecutive_losses': 3,
                    'max_flat_rate': 0.50,
                }
            }
        }
    })


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


def signal_bucket_counts(signals: List[Dict], config: Dict) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for sig in signals:
        bucket = classify_bucket(sig.get('confidence'), config)
        counts[bucket] = counts.get(bucket, 0) + 1
    return counts


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
    strategy_vnext = config.get('strategy_vnext') or {}
    tradability_gate = strategy_vnext.get('tradability_gate') or {}
    signal_rules = strategy_vnext.get('signal_rules') or {}

    cluster = signal.get('cluster', 'other')
    regime = signal.get('regime', 'other')
    bucket = classify_bucket(signal.get('confidence'), config)

    blocked_clusters = set(overrides.get('blocked_clusters', []))
    observe_only_clusters = set(overrides.get('observe_only_clusters', []))
    blocked_regimes = set(overrides.get('blocked_regimes', []))
    observe_only_regimes = set(overrides.get('observe_only_regimes', []))

    vnext_blocked_clusters = set(tradability_gate.get('blocked_clusters', []) or [])
    vnext_allowed_clusters = set(tradability_gate.get('allowed_clusters', []) or [])
    vnext_trade_regimes = set(signal_rules.get('trade_regimes', []) or [])
    vnext_observe_regimes = set(signal_rules.get('observe_only_regimes', []) or [])
    vnext_blocked_regimes = set(signal_rules.get('blocked_regimes', []) or [])

    if cluster in blocked_clusters or cluster in vnext_blocked_clusters:
        return 'blocked'
    if regime in blocked_regimes or regime in vnext_blocked_regimes:
        return 'blocked'
    if vnext_allowed_clusters and cluster not in vnext_allowed_clusters:
        return 'blocked'
    if cluster in observe_only_clusters or regime in observe_only_regimes or regime in vnext_observe_regimes:
        return 'observe_only'
    if vnext_trade_regimes:
        if regime in vnext_trade_regimes:
            return bucket_execution_policy(bucket, config)
        return 'observe_only'
    return bucket_execution_policy(bucket, config)


def position_bucket_counts(positions: List[Dict], config: Dict) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for pos in positions:
        bucket = pos.get('signal_bucket') or classify_bucket(pos.get('confidence'), config)
        counts[bucket] = counts.get(bucket, 0) + 1
    return counts


def save_portfolio(portfolio: Dict) -> None:
    portfolio['updated_at'] = now_iso()
    PORTFOLIO_FILE.write_text(json.dumps(portfolio, ensure_ascii=False, indent=2), encoding='utf-8')


def save_cycle_summary(summary: Dict) -> None:
    CYCLE_SUMMARY_FILE.parent.mkdir(parents=True, exist_ok=True)
    CYCLE_SUMMARY_FILE.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')


def append_trade(event: Dict) -> None:
    TRADE_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(TRADE_LOG, 'a', encoding='utf-8') as f:
        f.write(json.dumps(event, ensure_ascii=False) + '\n')


def iter_trade_events() -> List[Dict]:
    events: List[Dict] = []
    if not TRADE_LOG.exists():
        return events
    for line in TRADE_LOG.read_text(encoding='utf-8').splitlines():
        if not line.strip():
            continue
        try:
            events.append(json.loads(line))
        except Exception:
            continue
    return events


def latest_map(latest: List[Dict]) -> Dict[str, Dict]:
    out = {}
    for item in latest:
        key = item.get('token_id') or item.get('slug') or item.get('question')
        if key:
            out[key] = item
    return out


def used_budget_today() -> float:
    today = datetime.now().date().isoformat()
    total = 0.0
    for event in iter_trade_events():
        if event.get('type') != 'open':
            continue
        if not str(event.get('opened_at', '')).startswith(today):
            continue
        total += float(event.get('size_usd', 0) or 0)
    return total


def _event_realized_pnl(event: Dict):
    realized = event.get('realized_pnl_like')
    if realized is not None:
        return float(realized)
    pnl_like = event.get('pnl_like')
    size_usd = event.get('size_usd')
    if pnl_like is None or size_usd is None:
        return None
    return float(pnl_like) * float(size_usd)


def recent_fail_count(limit: int = 20) -> int:
    fails = 0
    rows = iter_trade_events()
    for event in reversed(rows[-limit:]):
        if event.get('type') != 'close':
            continue
        realized = _event_realized_pnl(event)
        if realized is None:
            break
        if float(realized) < 0:
            fails += 1
        else:
            break
    return fails


def opened_today_count() -> int:
    today = datetime.now().date().isoformat()
    count = 0
    for event in iter_trade_events():
        if event.get('type') != 'open':
            continue
        if str(event.get('opened_at', '')).startswith(today):
            count += 1
    return count


def open_position(signal: Dict, size: float, config: Dict) -> Dict:
    signal_bucket = classify_bucket(signal.get('confidence'), config)
    return {
        'status': 'open',
        'opened_at': now_iso(),
        'question': signal.get('question'),
        'slug': signal.get('slug'),
        'token_id': signal.get('token_id'),
        'cluster': signal.get('cluster'),
        'regime': signal.get('regime'),
        'direction': signal.get('direction'),
        'confidence': signal.get('confidence'),
        'signal_bucket': signal_bucket,
        'execution_policy': signal_execution_policy(signal, config),
        'entry_yes_price': signal.get('yes_price'),
        'size_usd': size,
        'noise_score': signal.get('noise_score'),
        'hours_to_event': signal.get('hours_to_event'),
        'liquidity': signal.get('liquidity'),
        'thesis': ', '.join(signal.get('reasons', [])[:3]),
    }


def mark_positions(portfolio: Dict, latest_by_key: Dict[str, Dict]) -> None:
    now = datetime.now()
    for pos in portfolio.get('positions', []):
        if pos.get('status') != 'open':
            continue
        key = pos.get('token_id') or pos.get('slug') or pos.get('question')
        latest = latest_by_key.get(key)
        if not latest:
            continue
        pos['current_yes_price'] = latest.get('yes_price')
        move = float(latest.get('yes_price', 0) or 0) - float(pos.get('entry_yes_price', 0) or 0)
        pos['pnl_like'] = round(move if pos.get('direction') == 'YES' else -move, 6)
        try:
            opened_at = datetime.fromisoformat(pos.get('opened_at'))
            pos['hold_hours'] = round((now - opened_at).total_seconds() / 3600.0, 2)
        except Exception:
            pos['hold_hours'] = None
        pos['latest_regime'] = latest.get('regime')
        pos['latest_direction'] = latest.get('direction')
        pos['latest_confidence'] = latest.get('confidence')
        pos['health'] = 'healthy'
        if latest.get('direction') and latest.get('direction') != pos.get('direction'):
            pos['health'] = 'thesis_risk'
        elif float(latest.get('confidence', 0) or 0) < 0.45:
            pos['health'] = 'confidence_weak'
        elif 'event_near' in latest.get('blocking_flags', []):
            pos['health'] = 'event_risk'


def close_position(pos: Dict, latest_sig: Dict, reason: str) -> Tuple[Dict, Dict]:
    exit_yes_price = float(
        latest_sig.get('yes_price', pos.get('current_yes_price', pos.get('entry_yes_price', 0))) or 0
    )
    entry_yes_price = float(pos.get('entry_yes_price', 0) or 0)
    size_usd = float(pos.get('size_usd', 0) or 0)
    move = exit_yes_price - entry_yes_price
    pnl_like = move if pos.get('direction') == 'YES' else -move
    realized_pnl_like = pnl_like * size_usd

    pos['status'] = 'closed'
    pos['closed_at'] = now_iso()
    pos['close_reason'] = reason
    pos['exit_yes_price'] = round(exit_yes_price, 6)
    pos['current_yes_price'] = round(exit_yes_price, 6)
    pos['pnl_like'] = round(pnl_like, 6)
    pos['realized_pnl_like'] = round(realized_pnl_like, 6)
    pos['latest_confidence'] = latest_sig.get('confidence', pos.get('latest_confidence'))

    event = {
        'type': 'close',
        **pos,
    }
    return pos, event


def add_reason(counter: Dict[str, int], reason: str) -> None:
    counter[reason] = counter.get(reason, 0) + 1


def vnext_precheck(signal: Dict, config: Dict) -> Tuple[bool, str]:
    strategy_vnext = config.get('strategy_vnext') or {}
    tradability_gate = strategy_vnext.get('tradability_gate') or {}
    signal_rules = strategy_vnext.get('signal_rules') or {}

    cluster = signal.get('cluster', 'other')
    regime = signal.get('regime', 'other')
    liquidity = float(signal.get('liquidity', 0) or 0)
    noise = signal.get('noise_score')
    hours_to_event = signal.get('hours_to_event')
    yes_price = float(signal.get('yes_price', 0) or 0)
    confidence = float(signal.get('confidence', 0) or 0)

    blocked_clusters = set(tradability_gate.get('blocked_clusters', []) or [])
    allowed_clusters = set(tradability_gate.get('allowed_clusters', []) or [])
    trade_regimes = set(signal_rules.get('trade_regimes', []) or [])
    blocked_regimes = set(signal_rules.get('blocked_regimes', []) or [])
    whitelist_keywords = [str(x).lower() for x in (tradability_gate.get('question_whitelist_keywords', []) or [])]
    observe_keywords = [str(x).lower() for x in (tradability_gate.get('question_observe_keywords', []) or [])]
    blocklist_keywords = [str(x).lower() for x in (tradability_gate.get('question_blocklist_keywords', []) or [])]
    question_text = f"{signal.get('question') or ''} {signal.get('slug') or ''}".lower()

    if cluster in blocked_clusters:
        return False, f'vnext blocked cluster={cluster}'
    if allowed_clusters and cluster not in allowed_clusters:
        return False, f'vnext cluster not allowed={cluster}'
    if blocklist_keywords and any(k in question_text for k in blocklist_keywords):
        return False, 'vnext question blocklisted'
    if observe_keywords and any(k in question_text for k in observe_keywords):
        return False, 'vnext question observe-only'
    if whitelist_keywords and not any(k in question_text for k in whitelist_keywords):
        return False, 'vnext question not whitelisted'
    if regime in blocked_regimes:
        return False, f'vnext blocked regime={regime}'
    if trade_regimes and regime not in trade_regimes:
        return False, f'vnext regime not tradable={regime}'
    min_liquidity = tradability_gate.get('min_liquidity')
    if min_liquidity is not None and liquidity < float(min_liquidity):
        return False, 'vnext liquidity too low'
    max_noise = tradability_gate.get('max_noise_score')
    if noise is not None and max_noise is not None and float(noise) > float(max_noise):
        return False, 'vnext noise too high'
    min_hours = tradability_gate.get('min_hours_to_event')
    max_hours = tradability_gate.get('max_hours_to_event')
    if hours_to_event is not None and min_hours is not None and float(hours_to_event) < float(min_hours):
        return False, 'vnext event too near'
    if hours_to_event is not None and max_hours is not None and float(hours_to_event) > float(max_hours):
        return False, 'vnext event too far'
    low = tradability_gate.get('yes_price_low')
    high = tradability_gate.get('yes_price_high')
    if low is not None and yes_price <= float(low):
        return False, 'vnext yes price too low'
    if high is not None and yes_price >= float(high):
        return False, 'vnext yes price too high'

    mr_rules = (signal_rules.get('mean_revert') or {}) if regime == 'mean_revert' else {}
    min_conf = mr_rules.get('min_confidence')
    if min_conf is not None and confidence < float(min_conf):
        return False, 'vnext confidence below min'
    return True, 'ok'


def main() -> None:
    ready = load_json(READY_FILE, [])
    latest = load_json(LATEST_FILE, [])
    latest_by_key = latest_map(latest)
    portfolio = load_portfolio()
    config = load_config()
    portfolio['trading_mode'] = config.get('mode', 'paper_trade')
    mark_positions(portfolio, latest_by_key)

    cycle_summary = {
        'ran_at': now_iso(),
        'mode': config.get('mode', 'paper_trade'),
        'discipline_version': ((config.get('discipline_v2') or {}).get('version') or 'v2'),
        'discipline_buckets': (config.get('discipline_v2') or {}).get('buckets', {}),
        'discipline_execution': (config.get('discipline_v2') or {}).get('execution', {}),
        'ready_count': len(ready),
        'ready_buckets': signal_bucket_counts(ready, config),
        'latest_count': len(latest),
        'opened': 0,
        'opened_buckets': {},
        'closed': 0,
        'skipped': 0,
        'skipped_buckets': {},
        'skip_reasons': {},
        'closed_reasons': {},
        'halted': False,
        'halt_reason': None,
    }

    opened_today = opened_today_count()
    used_budget = used_budget_today()

    # exits first
    for pos in portfolio.get('positions', []):
        if pos.get('status') != 'open':
            continue
        close, reason = should_close(pos, latest_by_key)
        if close:
            key = pos.get('token_id') or pos.get('slug') or pos.get('question')
            latest_sig = latest_by_key.get(key, {})
            _, close_event = close_position(pos, latest_sig, reason)
            append_trade(close_event)
            cycle_summary['closed'] += 1
            add_reason(cycle_summary['closed_reasons'], reason)

    # opens
    allowed_modes = set(config.get('allowed_modes', []))
    mode = config.get('mode', 'paper_trade')
    portfolio_health = portfolio.get('portfolio_health', {})
    total_pnl_like = float(portfolio_health.get('total_pnl_like', 0) or 0)
    fail_count = recent_fail_count()
    halt_reason = None
    if mode not in allowed_modes:
        halt_reason = f'illegal mode={mode}'
    elif config.get('live_trade_enabled'):
        halt_reason = 'live trading blocked by safety gate'
    elif config.get('emergency_stop'):
        halt_reason = 'emergency_stop'
    elif not config.get('auto_trade_enabled', True):
        halt_reason = 'auto_trade_disabled'
    elif config.get('paper_review_only') or mode in ('analysis_only', 'paper_review_only', 'live_disabled'):
        halt_reason = f'mode={mode}'
    elif total_pnl_like <= float(config.get('max_daily_loss_like', -0.12) or -0.12):
        halt_reason = 'daily_loss_halt'
    elif fail_count >= int(config.get('consecutive_fail_halt', 3) or 3):
        halt_reason = 'consecutive_fail_halt'

    if halt_reason:
        cycle_summary['halted'] = True
        cycle_summary['halt_reason'] = halt_reason
        append_trade({'type': 'halt', 'time': now_iso(), 'reason': halt_reason})
    else:
        daily_budget = float(config.get('daily_budget_usd', 12.0) or 12.0)
        for sig in ready:
            key = sig.get('token_id') or sig.get('slug') or sig.get('question')
            bucket = classify_bucket(sig.get('confidence'), config)
            policy = signal_execution_policy(sig, config)
            already_open = any(
                (p.get('token_id') or p.get('slug') or p.get('question')) == key and p.get('status') == 'open'
                for p in portfolio.get('positions', [])
            )
            if already_open:
                continue
            if policy != 'trade':
                reason = f'bucket={bucket} policy={policy}'
                append_trade({
                    'type': 'skip',
                    'time': now_iso(),
                    'question': sig.get('question'),
                    'reason': reason,
                    'signal_bucket': bucket,
                    'execution_policy': policy,
                })
                cycle_summary['skipped'] += 1
                add_reason(cycle_summary['skip_reasons'], reason)
                add_reason(cycle_summary['skipped_buckets'], bucket)
                continue
            vnext_ok, vnext_reason = vnext_precheck(sig, config)
            if not vnext_ok:
                append_trade({
                    'type': 'skip',
                    'time': now_iso(),
                    'question': sig.get('question'),
                    'reason': vnext_reason,
                    'signal_bucket': bucket,
                    'execution_policy': policy,
                })
                cycle_summary['skipped'] += 1
                add_reason(cycle_summary['skip_reasons'], vnext_reason)
                add_reason(cycle_summary['skipped_buckets'], bucket)
                continue
            if used_budget >= daily_budget:
                reason = 'daily budget reached'
                append_trade({
                    'type': 'skip',
                    'time': now_iso(),
                    'question': sig.get('question'),
                    'reason': reason,
                    'signal_bucket': bucket,
                    'execution_policy': policy,
                })
                cycle_summary['skipped'] += 1
                add_reason(cycle_summary['skip_reasons'], reason)
                add_reason(cycle_summary['skipped_buckets'], bucket)
                continue
            min_confidence = float(
                (((config.get('discipline_v2') or {}).get('buckets') or {}).get('main_pool_min', 0.58) or 0.58)
            )
            ok, reason, size = can_open(sig, portfolio, opened_today, min_confidence=min_confidence)
            vnext_risk = (config.get('strategy_vnext') or {}).get('risk') or {}
            size = min(size, float(config.get('max_single_size_usd', 3.0) or 3.0))
            size = min(size, float(vnext_risk.get('max_single_size_usd', size) or size))
            if not ok:
                append_trade({
                    'type': 'skip',
                    'time': now_iso(),
                    'question': sig.get('question'),
                    'reason': reason,
                    'signal_bucket': bucket,
                    'execution_policy': policy,
                })
                cycle_summary['skipped'] += 1
                add_reason(cycle_summary['skip_reasons'], reason)
                add_reason(cycle_summary['skipped_buckets'], bucket)
                continue
            if used_budget + size > daily_budget:
                reason = 'daily budget would be exceeded'
                append_trade({
                    'type': 'skip',
                    'time': now_iso(),
                    'question': sig.get('question'),
                    'reason': reason,
                    'signal_bucket': bucket,
                    'execution_policy': policy,
                })
                cycle_summary['skipped'] += 1
                add_reason(cycle_summary['skip_reasons'], reason)
                add_reason(cycle_summary['skipped_buckets'], bucket)
                continue
            pos = open_position(sig, size, config)
            portfolio['positions'].append(pos)
            append_trade({'type': 'open', **pos})
            cycle_summary['opened'] += 1
            add_reason(cycle_summary['opened_buckets'], pos.get('signal_bucket', bucket))
            opened_today += 1
            used_budget += size

    open_positions_list = [p for p in portfolio.get('positions', []) if p.get('status') == 'open']
    closed_positions_list = [p for p in portfolio.get('positions', []) if p.get('status') == 'closed']
    total_pnl_like = sum(float(p.get('pnl_like', 0) or 0) * float(p.get('size_usd', 0) or 0) for p in open_positions_list)
    realized_pnl_like = 0.0
    for p in closed_positions_list:
        try:
            if p.get('realized_pnl_like') is None:
                entry = float(p.get('entry_yes_price', 0) or 0)
                exit_p = float(p.get('exit_yes_price', entry) or entry)
                move = exit_p - entry
                pnl = move if p.get('direction') == 'YES' else -move
                p['pnl_like'] = round(pnl, 6)
                p['realized_pnl_like'] = round(pnl * float(p.get('size_usd', 0) or 0), 6)
            realized_pnl_like += float(p.get('realized_pnl_like', 0) or 0)
        except Exception:
            pass

    regime_pnl = {}
    cluster_pnl = {}
    for p in open_positions_list + closed_positions_list:
        key_regime = p.get('regime', 'other')
        key_cluster = p.get('cluster', 'other')
        if p.get('status') == 'open':
            pnl_val = float(p.get('pnl_like', 0) or 0) * float(p.get('size_usd', 0) or 0)
        else:
            pnl_val = float(p.get('realized_pnl_like', 0) or 0)
        regime_pnl[key_regime] = round(regime_pnl.get(key_regime, 0.0) + pnl_val, 4)
        cluster_pnl[key_cluster] = round(cluster_pnl.get(key_cluster, 0.0) + pnl_val, 4)

    portfolio['portfolio_health'] = {
        'mode': config.get('mode', 'paper_trade'),
        'discipline_version': ((config.get('discipline_v2') or {}).get('version') or 'v2'),
        'halted': bool(halt_reason),
        'halt_reason': halt_reason,
        'recent_fail_count': fail_count,
        'auto_trade_enabled': config.get('auto_trade_enabled', True),
        'emergency_stop': config.get('emergency_stop', False),
        'used_budget_today': round(used_budget, 2),
        'daily_budget_usd': float(config.get('daily_budget_usd', 12.0) or 12.0),
        'open_positions': len(open_positions_list),
        'closed_positions': len(closed_positions_list),
        'open_bucket_counts': position_bucket_counts(open_positions_list, config),
        'closed_bucket_counts': position_bucket_counts(closed_positions_list, config),
        'total_open_exposure': sum(float(p.get('size_usd', 0) or 0) for p in open_positions_list),
        'open_pnl_like': round(total_pnl_like, 4),
        'realized_pnl_like': round(realized_pnl_like, 4),
        'total_pnl_like': round(total_pnl_like + realized_pnl_like, 4),
        'thesis_risk_positions': sum(1 for p in open_positions_list if p.get('health') == 'thesis_risk'),
        'regime_pnl': regime_pnl,
        'cluster_pnl': cluster_pnl,
    }
    save_portfolio(portfolio)

    cycle_summary['portfolio_health'] = portfolio['portfolio_health']
    cycle_summary['open_positions'] = len(open_positions_list)
    cycle_summary['closed_positions'] = len(closed_positions_list)
    cycle_summary['used_budget_today'] = round(used_budget, 2)
    save_cycle_summary(cycle_summary)

    print(
        f"ready={len(ready)} opened={cycle_summary['opened']} closed={cycle_summary['closed']} "
        f"skipped={cycle_summary['skipped']} open_positions={len(open_positions_list)} "
        f"closed_positions={len(closed_positions_list)} portfolio={PORTFOLIO_FILE}"
    )


if __name__ == '__main__':
    main()
