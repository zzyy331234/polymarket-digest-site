#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

from .indicators import (
    compute_rsi,
    compute_slope,
    compute_volatility,
    nearest_price_at_or_before,
    pct_change,
    rolling_percentile,
    simple_noise_score,
)

DB_PATH = "/Users/mac/.openclaw/workspace/polymarket/collector/polymarket_data.db"


class DataAdapter:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True, timeout=30.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA busy_timeout = 30000")
        return conn

    def load_feature_markets(self, min_liquidity: float = 20000.0) -> List[Dict]:
        last_error = None
        for _ in range(3):
            conn = None
            try:
                conn = self._connect()
                cur = conn.cursor()

                cur.execute(
                    """
                    SELECT m.token_id, m.question, m.slug, m.liquidity, m.volume,
                           COALESCE(m.event_time, m.close_time, m.end_date_iso) AS event_time,
                           MAX(ph.timestamp) AS latest_ts
                    FROM markets m
                    JOIN price_history ph ON ph.token_id = m.token_id
                    WHERE m.liquidity >= ?
                    GROUP BY m.token_id, m.question, m.slug, m.liquidity, m.volume
                    ORDER BY m.liquidity DESC
                    """,
                    (min_liquidity,),
                )
                rows = cur.fetchall()
                markets = []
                for row in rows:
                    history = self._load_history(cur, row["token_id"])
                    if len(history) < 5:
                        continue
                    feature = self._build_feature(row, history)
                    if feature:
                        markets.append(feature)
                conn.close()
                return markets
            except sqlite3.OperationalError as exc:
                last_error = exc
                if conn is not None:
                    conn.close()
                if "locked" not in str(exc).lower():
                    raise
                time.sleep(1.0)
        raise last_error

    def _load_history(self, cur, token_id: str) -> List[Dict]:
        cur.execute(
            """
            SELECT timestamp, yes_price, no_price, liquidity, volume
            FROM price_history
            WHERE token_id = ?
            ORDER BY timestamp ASC
            """,
            (token_id,),
        )
        return [dict(r) for r in cur.fetchall()]

    def _build_feature(self, row, history: List[Dict]) -> Optional[Dict]:
        latest = history[-1]
        latest_price = latest.get("yes_price")
        if latest_price is None or latest_price <= 0 or latest_price >= 1:
            return None

        timestamps = [h["timestamp"] for h in history]
        prices = [h.get("yes_price") for h in history]
        latest_ts = timestamps[-1]
        dt_latest = datetime.fromisoformat(latest_ts)

        refs = {
            "1h": (dt_latest - timedelta(hours=1)).isoformat(),
            "4h": (dt_latest - timedelta(hours=4)).isoformat(),
            "24h": (dt_latest - timedelta(hours=24)).isoformat(),
            "7d": (dt_latest - timedelta(days=7)).isoformat(),
        }
        points = [(h["timestamp"], h.get("yes_price")) for h in history if h.get("yes_price") is not None]

        ref_1h = nearest_price_at_or_before(points, refs["1h"])
        ref_4h = nearest_price_at_or_before(points, refs["4h"])
        ref_24h = nearest_price_at_or_before(points, refs["24h"])
        ref_7d = nearest_price_at_or_before(points, refs["7d"])

        changes_for_vol = []
        for i in range(1, len(prices)):
            prev = prices[i - 1]
            cur = prices[i]
            chg = pct_change(cur, prev)
            if chg is not None:
                changes_for_vol.append(chg)

        recent_4h_prices = [p for ts, p in points if ts >= refs["4h"]]
        recent_24h_prices = [p for ts, p in points if ts >= refs["24h"]]
        recent_7d_prices = [p for ts, p in points if ts >= refs["7d"]]

        pct_rank_7d = rolling_percentile(latest_price, recent_7d_prices or prices)
        pct_rank_30d = rolling_percentile(latest_price, prices)

        event_time = row["event_time"]
        hours_to_event = None
        if event_time:
            try:
                event_dt = datetime.fromisoformat(str(event_time).replace("Z", "+00:00"))
                if event_dt.tzinfo is None:
                    event_dt = event_dt.replace(tzinfo=timezone.utc)
                hours_to_event = (event_dt - dt_latest.replace(tzinfo=timezone.utc)).total_seconds() / 3600.0
            except Exception:
                hours_to_event = None

        return {
            "token_id": row["token_id"],
            "question": row["question"],
            "slug": row["slug"],
            "yes_price": float(latest_price),
            "no_price": float(latest.get("no_price") or (1.0 - latest_price)),
            "liquidity": float(row["liquidity"] or 0.0),
            "volume": float(row["volume"] or 0.0),
            "latest_ts": latest_ts,
            "history_points": len(history),
            "chg_1h": pct_change(latest_price, ref_1h),
            "chg_4h": pct_change(latest_price, ref_4h),
            "chg_24h": pct_change(latest_price, ref_24h),
            "chg_7d": pct_change(latest_price, ref_7d),
            "rsi_14": compute_rsi(prices, 14),
            "volatility": compute_volatility(changes_for_vol[-96:]),
            "trend_slope_4h": compute_slope(recent_4h_prices),
            "trend_slope_24h": compute_slope(recent_24h_prices),
            "pct_rank_7d": pct_rank_7d,
            "pct_rank_30d": pct_rank_30d,
            "noise_score": simple_noise_score(changes_for_vol[-48:]),
            "hours_to_event": hours_to_event,
            "event_time": event_time,
            "spread": None,
        }
