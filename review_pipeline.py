#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sqlite3
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from core.portfolio_manager import classify_cluster

HISTORY_FILE = Path('/Users/mac/.openclaw/workspace/polymarket/outputs/signals_v2_history.jsonl')
LATEST_FILE = Path('/Users/mac/.openclaw/workspace/polymarket/outputs/signals_v2_latest.json')
OUTPUT = Path('/Users/mac/.openclaw/workspace/polymarket/outputs/review_status.json')
DB_PATH = '/Users/mac/.openclaw/workspace/polymarket/collector/polymarket_data.db'


def connect_db() -> sqlite3.Connection:
    conn = sqlite3.connect(f'file:{DB_PATH}?mode=ro', uri=True, timeout=30.0)
    conn.execute('PRAGMA busy_timeout = 30000')
    return conn


def parse_dt(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    except Exception:
        return None


def load_json(path: Path):
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding='utf-8'))


def load_history(path: Path) -> List[Dict]:
    rows = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except Exception:
            pass
    return rows


def build_latest_map(latest: List[Dict]) -> Dict[str, Dict]:
    out = {}
    for item in latest:
        key = item.get('token_id') or item.get('slug') or item.get('question')
        if key:
            out[key] = item
    return out


def _window_threshold(hours: int) -> float:
    if hours <= 6:
        return 0.01
    if hours <= 24:
        return 0.015
    return 0.02


def _judge_window(direction: str, move: Optional[float], mfe: Optional[float], mae: Optional[float], hours: int) -> Tuple[str, List[str]]:
    notes: List[str] = []
    if direction not in ('YES', 'NO'):
        return 'pending', notes
    thr = _window_threshold(hours)
    if move is None and mfe is None and mae is None:
        return 'pending', notes

    if direction == 'YES':
        if move is not None and move >= thr:
            return 'hit', [f'{hours}h close reached +{thr:.3f}']
        if mfe is not None and mfe >= thr and (mae is None or mae > -thr):
            return 'hit', [f'{hours}h favorable excursion reached +{thr:.3f}']
        if move is not None and move <= -thr:
            return 'miss', [f'{hours}h close reached -{thr:.3f}']
        if mae is not None and mae <= -thr:
            return 'miss', [f'{hours}h adverse excursion reached -{thr:.3f}']
    else:
        if move is not None and move <= -thr:
            return 'hit', [f'{hours}h close reached -{thr:.3f}']
        if mae is not None and mae <= -thr and (mfe is None or mfe < thr):
            return 'hit', [f'{hours}h favorable excursion reached -{thr:.3f}']
        if move is not None and move >= thr:
            return 'miss', [f'{hours}h close reached +{thr:.3f}']
        if mfe is not None and mfe >= thr:
            return 'miss', [f'{hours}h adverse excursion reached +{thr:.3f}']

    flat_reasons: List[str] = []
    if move is not None:
        flat_reasons.append(f'{hours}h close stayed within ±{thr:.3f}')
    elif mfe is not None or mae is not None:
        flat_reasons.append(f'{hours}h window stayed within ±{thr:.3f}')
    return 'flat', flat_reasons


def get_price_windows(conn, token_id: str, saved_at_dt):
    if not token_id or not saved_at_dt:
        return {}
    out = {}
    base_ts = saved_at_dt.strftime('%Y-%m-%dT%H:%M:%S')
    cur = conn.cursor()
    cur.execute(
        """
        SELECT yes_price, timestamp FROM price_history
        WHERE token_id = ? AND timestamp >= ?
        ORDER BY timestamp ASC
        LIMIT 1
        """,
        (token_id, base_ts),
    )
    row0 = cur.fetchone()
    if not row0:
        return out
    base_price = float(row0[0])
    out['base_yes_price'] = base_price
    out['base_ts'] = row0[1]
    for hours in (6, 24, 48):
        target_dt = saved_at_dt.replace(tzinfo=None) if saved_at_dt.tzinfo else saved_at_dt
        target_dt = target_dt + timedelta(hours=hours)
        target_ts = target_dt.strftime('%Y-%m-%dT%H:%M:%S')
        out[f'window_{hours}h_ready'] = False

        cur.execute(
            """
            SELECT yes_price, timestamp FROM price_history
            WHERE token_id = ? AND timestamp >= ?
            ORDER BY timestamp ASC
            LIMIT 1
            """,
            (token_id, target_ts),
        )
        row = cur.fetchone()
        if row:
            try:
                sampled_ts = parse_dt(row[1])
                out[f'window_{hours}h_ready'] = sampled_ts is not None and sampled_ts >= target_dt
                out[f'post_move_{hours}h'] = float(row[0]) - base_price
                out[f'window_{hours}h_ts'] = row[1]
            except Exception:
                pass

        cur.execute(
            """
            SELECT MIN(yes_price), MAX(yes_price) FROM price_history
            WHERE token_id = ? AND timestamp >= ? AND timestamp <= ?
            """,
            (token_id, base_ts, target_ts),
        )
        mm = cur.fetchone()
        if mm and mm[0] is not None and mm[1] is not None:
            out[f'mae_{hours}h'] = float(mm[0]) - base_price
            out[f'mfe_{hours}h'] = float(mm[1]) - base_price
    return out


def select_review_history(history: List[Dict], limit: int = 200) -> List[Dict]:
    now = datetime.now(timezone.utc)
    buckets = {
        'mature_48h': [],
        'mature_24h': [],
        'mature_6h': [],
        'fresh': [],
    }
    seen = set()

    for item in reversed(history):
        saved_at = parse_dt(item.get('saved_at'))
        if not saved_at:
            continue
        key = item.get('token_id') or item.get('slug') or item.get('question')
        if not key:
            continue
        age_hours = (now - saved_at.astimezone(timezone.utc)).total_seconds() / 3600.0
        bucket = 'fresh'
        if age_hours >= 48:
            bucket = 'mature_48h'
        elif age_hours >= 24:
            bucket = 'mature_24h'
        elif age_hours >= 6:
            bucket = 'mature_6h'
        dedupe_key = (bucket, key)
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        buckets[bucket].append(item)

    selected: List[Dict] = []
    for name in ('mature_48h', 'mature_24h', 'mature_6h', 'fresh'):
        for item in buckets[name]:
            selected.append(item)
            if len(selected) >= limit:
                return list(reversed(selected))
    return list(reversed(selected))


def classify(item: Dict, latest_map: Dict[str, Dict], conn) -> Dict:
    key = item.get('token_id') or item.get('slug') or item.get('question')
    latest = latest_map.get(key, {})
    now = datetime.now(timezone.utc)

    event_time = parse_dt(item.get('event_time') or latest.get('event_time') or item.get('end_date_iso') or latest.get('end_date_iso'))
    saved_at = parse_dt(item.get('saved_at'))
    latest_ts = parse_dt(latest.get('latest_ts'))

    status = 'unresolved'
    expired = False
    resolved = False
    notes = []

    if event_time and event_time <= now:
        status = 'expired'
        expired = True
        notes.append('event_time passed')
    elif latest:
        status = 'still_open'
        notes.append('market still visible in latest candidate set')

    window_moves = get_price_windows(conn, item.get('token_id'), saved_at) if saved_at else {}
    entry_yes_price = item.get('yes_price')
    if entry_yes_price is None:
        entry_yes_price = window_moves.get('base_yes_price')

    if saved_at and latest_ts and latest.get('yes_price') is not None and entry_yes_price is not None:
        try:
            post_move = float(latest.get('yes_price')) - float(entry_yes_price)
        except Exception:
            post_move = None
    else:
        post_move = None

    hours_elapsed = None
    if saved_at and latest_ts:
        hours_elapsed = round((latest_ts - saved_at).total_seconds() / 3600.0, 2)

    outcome = 'pending'
    direction = item.get('direction')
    judged_hours = None
    for hours in (48, 24, 6):
        if not window_moves.get(f'window_{hours}h_ready'):
            continue
        outcome, judge_notes = _judge_window(
            direction,
            window_moves.get(f'post_move_{hours}h'),
            window_moves.get(f'mfe_{hours}h'),
            window_moves.get(f'mae_{hours}h'),
            hours,
        )
        judged_hours = hours
        notes.append(f'judge_on_{hours}h_window')
        notes.extend(judge_notes)
        break

    if judged_hours is None and post_move is not None:
        if abs(post_move) >= 0.03:
            resolved = True
            notes.append(f'post_move significant {post_move:+.4f}')
        fallback_hours = None
        if (hours_elapsed or 0) >= 48:
            fallback_hours = 48
        elif (hours_elapsed or 0) >= 24:
            fallback_hours = 24
        elif (hours_elapsed or 0) >= 6:
            fallback_hours = 6
        if fallback_hours is not None:
            outcome, judge_notes = _judge_window(direction, post_move, None, None, fallback_hours)
            if outcome != 'pending':
                notes.append(f'judge_on_live_{fallback_hours}h_proxy')
                notes.extend(judge_notes)

    return {
        'saved_at': item.get('saved_at'),
        'question': item.get('question'),
        'slug': item.get('slug'),
        'cluster': item.get('cluster') or latest.get('cluster') or classify_cluster(item.get('question') or latest.get('question') or ''),
        'regime': item.get('regime'),
        'direction': item.get('direction'),
        'confidence': item.get('confidence'),
        'entry_yes_price': entry_yes_price,
        'event_time': item.get('event_time') or latest.get('event_time') or item.get('end_date_iso') or latest.get('end_date_iso'),
        'latest_ts': latest.get('latest_ts'),
        'review_status': status,
        'expired': expired,
        'resolved': resolved,
        'hours_elapsed': hours_elapsed,
        'post_move_abs': post_move,
        'post_move_6h': window_moves.get('post_move_6h'),
        'post_move_24h': window_moves.get('post_move_24h'),
        'post_move_48h': window_moves.get('post_move_48h'),
        'window_6h_ready': window_moves.get('window_6h_ready', False),
        'window_24h_ready': window_moves.get('window_24h_ready', False),
        'window_48h_ready': window_moves.get('window_48h_ready', False),
        'mfe_6h': window_moves.get('mfe_6h'),
        'mae_6h': window_moves.get('mae_6h'),
        'mfe_24h': window_moves.get('mfe_24h'),
        'mae_24h': window_moves.get('mae_24h'),
        'mfe_48h': window_moves.get('mfe_48h'),
        'mae_48h': window_moves.get('mae_48h'),
        'outcome': outcome,
        'notes': notes,
    }


if __name__ == '__main__':
    history = load_history(HISTORY_FILE)
    selected_history = select_review_history(history, limit=200)
    latest = load_json(LATEST_FILE)
    latest_map = build_latest_map(latest)

    last_error = None
    reviews = []
    for _ in range(3):
        conn = None
        try:
            conn = connect_db()
            reviews = [classify(item, latest_map, conn) for item in selected_history]
            conn.close()
            last_error = None
            break
        except sqlite3.OperationalError as exc:
            last_error = exc
            if conn is not None:
                conn.close()
            if 'locked' not in str(exc).lower():
                raise
            time.sleep(1.0)
    if last_error is not None:
        raise last_error

    OUTPUT.write_text(json.dumps(reviews, ensure_ascii=False, indent=2), encoding='utf-8')
    unresolved = sum(1 for r in reviews if r['review_status'] == 'unresolved')
    still_open = sum(1 for r in reviews if r['review_status'] == 'still_open')
    expired = sum(1 for r in reviews if r['review_status'] == 'expired')
    hit = sum(1 for r in reviews if r.get('outcome') == 'hit')
    miss = sum(1 for r in reviews if r.get('outcome') == 'miss')
    flat = sum(1 for r in reviews if r.get('outcome') == 'flat')
    print(f'reviews={len(reviews)} still_open={still_open} unresolved={unresolved} expired={expired} hit={hit} miss={miss} flat={flat} output={OUTPUT}')
