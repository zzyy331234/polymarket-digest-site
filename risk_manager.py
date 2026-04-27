#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime, timezone
from typing import Dict, List, Tuple

MAX_POSITIONS = 5
MAX_DAILY_TRADES = 6
MAX_CLUSTER_EXPOSURE = 2
MAX_SINGLE_SIZE = 3.0
DEFAULT_SIZE = 1.5
MIN_CONFIDENCE = 0.60
MAX_TOTAL_EXPOSURE = 6.0
MAX_CONSECUTIVE_LOSSES = 2


def recent_consecutive_losses(portfolio: Dict) -> int:
    losses = 0
    closed = [p for p in portfolio.get('positions', []) if p.get('status') == 'closed']
    for pos in reversed(closed):
        pnl = pos.get('pnl_like')
        if pnl is None:
            break
        if float(pnl) < 0:
            losses += 1
        else:
            break
    return losses


def can_open(signal: Dict, portfolio: Dict, opened_today: int, min_confidence: float = MIN_CONFIDENCE) -> Tuple[bool, str, float]:
    if opened_today >= MAX_DAILY_TRADES:
        return False, 'daily trade limit reached', 0.0

    open_positions = [p for p in portfolio.get('positions', []) if p.get('status') == 'open']
    if len(open_positions) >= MAX_POSITIONS:
        return False, 'max positions reached', 0.0
    if float(signal.get('confidence', 0) or 0) < float(min_confidence):
        return False, 'confidence too low', 0.0
    if signal.get('blocking_flags'):
        return False, 'blocking flags present', 0.0
    if recent_consecutive_losses(portfolio) >= MAX_CONSECUTIVE_LOSSES:
        return False, 'cooldown after consecutive losses', 0.0

    cluster = signal.get('cluster', 'other')
    cluster_open = sum(1 for p in open_positions if p.get('cluster') == cluster)
    if cluster_open >= MAX_CLUSTER_EXPOSURE:
        return False, f'cluster exposure limit for {cluster}', 0.0

    current_exposure = sum(float(p.get('size_usd', 0) or 0) for p in open_positions)
    if current_exposure >= MAX_TOTAL_EXPOSURE:
        return False, 'total exposure limit reached', 0.0

    size = min(MAX_SINGLE_SIZE, DEFAULT_SIZE, MAX_TOTAL_EXPOSURE - current_exposure)
    if size <= 0:
        return False, 'no exposure budget left', 0.0
    return True, 'ok', size


def _parse_dt(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    except Exception:
        return None


def should_close(position: Dict, latest_map: Dict[str, Dict]) -> Tuple[bool, str]:
    key = position.get('token_id') or position.get('slug') or position.get('question')
    latest = latest_map.get(key)
    if not latest:
        return False, 'no latest snapshot'

    entry_yes = float(position.get('entry_yes_price', 0) or 0)
    current_yes = float(latest.get('yes_price', 0) or 0)
    direction = position.get('direction')
    risk_flags = latest.get('blocking_flags', [])

    move = current_yes - entry_yes
    pnl_like = move if direction == 'YES' else -move

    opened_at = _parse_dt(position.get('opened_at'))
    latest_ts = _parse_dt(latest.get('latest_ts'))
    confidence = float(latest.get('confidence', 0) or 0)
    latest_direction = latest.get('direction')

    if pnl_like >= 0.04:
        return True, 'take_profit'
    if pnl_like <= -0.03:
        return True, 'stop_loss'
    if 'low_tradability' in risk_flags:
        return True, 'low_tradability_exit'
    if 'stale_carry_no' in risk_flags:
        return True, 'stale_carry_no_exit'
    if 'deep_tail_world_cup' in risk_flags:
        return True, 'deep_tail_world_cup_exit'
    if 'event_near' in risk_flags:
        return True, 'event_near_exit'
    if opened_at and latest_ts:
        hold_hours = (latest_ts - opened_at).total_seconds() / 3600.0
        if hold_hours >= 24 and abs(pnl_like) < 0.01:
            return True, 'time_stop_24h'
        if hold_hours >= 48:
            return True, 'time_stop_48h'
    if latest_direction and latest_direction != direction and confidence >= 0.60:
        return True, 'thesis_invalidated'
    if confidence < 0.45:
        return True, 'confidence_decay'
    return False, 'hold'
