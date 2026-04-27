#!/usr/bin/env python3
"""
数据查看器 - 查看已采集的 Polymarket 数据
"""

import sqlite3
import os
import sys
from datetime import datetime, timedelta

DB_FILE = os.path.expanduser("~/.openclaw/workspace/polymarket/collector/polymarket_data.db")

def get_db():
    if not os.path.exists(DB_FILE):
        print(f"数据库不存在: {DB_FILE}")
        print("运行 python3 collector.py start 先启动采集器")
        sys.exit(1)
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def show_summary():
    conn = get_db()
    c = conn.cursor()

    print(f"\n{'='*60}")
    print(f"Polymarket 数据采集 - 数据概览")
    print(f"{'='*60}")

    # 总览
    c.execute("SELECT COUNT(*) FROM markets")
    m_count = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM price_history")
    p_count = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM ta_snapshots")
    ta_count = c.fetchone()[0]

    print(f"\n📊 数据规模:")
    print(f"  市场数: {m_count}")
    print(f"  价格记录: {p_count:,} 条")
    print(f"  TA快照: {ta_count:,} 条")

    # 时间范围
    c.execute("SELECT MIN(timestamp), MAX(timestamp) FROM price_history")
    row = c.fetchone()
    print(f"\n⏱️  数据范围:")
    print(f"  开始: {row[0][:19] if row[0] else 'N/A'}")
    print(f"  结束: {row[1][:19] if row[1] else 'N/A'}")

    # 最新数据
    c.execute("""
        SELECT ph.*, m.question 
        FROM price_history ph 
        LEFT JOIN markets m ON ph.token_id = m.token_id 
        ORDER BY ph.timestamp DESC 
        LIMIT 10
    """)
    print(f"\n📈 最新价格数据 (Top 10):")
    print(f"{'-'*60}")
    for r in c.fetchall():
        q = (r['question'] or '')[:40]
        print(f"  {r['timestamp'][:19]} | YES:{r['yes_price']:.4f} NO:{r['no_price']:.4f} | {q}...")

    # BTC 15m 市场
    c.execute("""
        SELECT ph.*, m.question 
        FROM price_history ph 
        LEFT JOIN markets m ON ph.token_id = m.token_id 
        WHERE m.question LIKE '%btc%' OR m.question LIKE '%bitcoin%' OR m.slug LIKE '%btc%'
        ORDER BY ph.timestamp DESC 
        LIMIT 5
    """)
    btc_rows = c.fetchall()
    if btc_rows:
        print(f"\n₿  BTC 15m 市场最新:")
        print(f"{'-'*60}")
        for r in btc_rows:
            q = (r['question'] or '')[:50]
            print(f"  {r['timestamp'][:19]} | YES:{r['yes_price']:.4f} NO:{r['no_price']:.4f} | {q}")

    # TA 快照（最新）
    c.execute("""
        SELECT ta.*, m.question
        FROM ta_snapshots ta
        LEFT JOIN markets m ON ta.token_id = m.token_id
        ORDER BY ta.timestamp DESC
        LIMIT 5
    """)
    ta_rows = c.fetchall()
    if ta_rows:
        print(f"\n📉 技术指标快照 (最新):")
        print(f"{'-'*60}")
        for r in ta_rows:
            q = (r['question'] or '')[:30]
            print(f"  {r['timestamp'][:19]} | {q}...")
            print(f"    RSI(14):{r['rsi_14']:.1f} RSI(7):{r['rsi_7']:.1f if r['rsi_7'] else '-'} | "
                  f"MACD:{r['macd']:.4f} | BB:{r['bb_lower']:.4f}/{r['bb_middle']:.4f}/{r['bb_upper']:.4f} | "
                  f"Z:{r['zscore_20']:.2f}" if r['rsi_14'] else "  N/A")

    # 采集频率统计
    c.execute("""
        SELECT strftime('%Y-%m-%d %H:', timestamp) || substr('0'||(CAST(substr(timestamp,15,2) AS INTEGER) / 5 * 5), -2) || '00' as interval_5m,
               COUNT(*) as cnt
        FROM price_history
        GROUP BY interval_5m
        ORDER BY interval_5m DESC
        LIMIT 10
    """)
    print(f"\n⏰ 采集频率 (最近时段):")
    print(f"{'-'*60}")
    for r in c.fetchall():
        print(f"  {r[0]} - {r[1]:,} 条")

    print(f"\n{'='*60}\n")
    conn.close()

def show_market_detail(token_id: str = None):
    """查看特定市场的详细数据"""
    conn = get_db()
    c = conn.cursor()

    if not token_id:
        # 显示活跃市场列表
        c.execute("""
            SELECT DISTINCT ph.token_id, m.question, m.slug,
                   ph.yes_price, ph.no_price, ph.timestamp
            FROM price_history ph
            LEFT JOIN markets m ON ph.token_id = m.token_id
            ORDER BY ph.timestamp DESC
            LIMIT 20
        """)
        print(f"\n{'='*60}")
        print("最近活跃市场:")
        for r in c.fetchall():
            q = (r['question'] or r['slug'] or r['token_id'])[:50]
            print(f"  {r['token_id'][:20]}... | YES:{r['yes_price']:.4f} NO:{r['no_price']:.4f} | {q}")
        print(f"{'='*60}\n")
    else:
        # 特定市场的历史
        c.execute("""
            SELECT * FROM price_history WHERE token_id = ? ORDER BY timestamp DESC LIMIT 50
        """, (token_id,))
        print(f"\n价格历史 (token: {token_id}):")
        for r in c.fetchall():
            print(f"  {r['timestamp'][:19]} | YES:{r['yes_price']:.4f} NO:{r['no_price']:.4f} | vol:{r['volume']:.0f}")

    conn.close()

def show_ta(token_id: str = None, limit: int = 20):
    """查看 TA 指标"""
    conn = get_db()
    c = conn.cursor()

    if token_id:
        c.execute("""
            SELECT ta.*, m.question FROM ta_snapshots ta
            LEFT JOIN markets m ON ta.token_id = m.token_id
            WHERE ta.token_id = ?
            ORDER BY ta.timestamp DESC LIMIT ?
        """, (token_id, limit))
    else:
        c.execute("""
            SELECT ta.*, m.question FROM ta_snapshots ta
            LEFT JOIN markets m ON ta.token_id = m.token_id
            ORDER BY ta.timestamp DESC LIMIT ?
        """, (limit,))

    print(f"\n{'='*60}")
    print(f"技术指标 (最新 {limit} 条)")
    print(f"{'-'*60}")
    for r in c.fetchall():
        q = (r['question'] or '')[:40]
        print(f"\n  {r['timestamp'][:19]} | {q}...")
        print(f"    RSI(14): {r['rsi_14']:.1f if r['rsi_14'] else 'N/A':>6} | "
              f"RSI(7): {r['rsi_7']:.1f if r['rsi_7'] else 'N/A':>6}")
        print(f"    MACD: {r['macd']:.4f if r['macd'] else 'N/A':>10} | "
              f"Signal: {r['macd_signal']:.4f if r['macd_signal'] else 'N/A':>10} | "
              f"Hist: {r['macd_hist']:.4f if r['macd_hist'] else 'N/A':>8}")
        print(f"    BB: {r['bb_lower']:.4f if r['bb_lower'] else 'N/A':>8} / "
              f"{r['bb_middle']:.4f if r['bb_middle'] else 'N/A':>8} / "
              f"{r['bb_upper']:.4f if r['bb_upper'] else 'N/A':>8}")
        print(f"    EMA9: {r['ema_9']:.4f if r['ema_9'] else 'N/A':>10} | "
              f"EMA21: {r['ema_21']:.4f if r['ema_21'] else 'N/A':>10}")
        print(f"    Z-score(20): {r['zscore_20']:.2f if r['zscore_20'] else 'N/A':>8} | "
              f"1d变化: {r['yes_1d_change']:.2f}%" if r['yes_1d_change'] else "    1d变化: N/A")

    print(f"{'='*60}\n")
    conn.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="查看 Polymarket 采集数据")
    parser.add_argument("--summary", action="store_true", help="总览")
    parser.add_argument("--ta", action="store_true", help="技术指标")
    parser.add_argument("--market", type=str, help="特定市场 token_id")
    parser.add_argument("--limit", type=int, default=20, help="显示条数")
    args = parser.parse_args()

    if args.market:
        show_market_detail(args.market)
    elif args.ta:
        show_ta(limit=args.limit)
    else:
        show_summary()
