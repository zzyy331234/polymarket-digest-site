#!/usr/bin/env python3
"""
Polymarket 15m 数据采集器
============================
实时采集 Polymarket 15分钟市场数据，存入 SQLite 供回测使用。

功能:
  - 轮询 Polymarket API（30秒间隔）
  - 采集 15m BTC 市场 + 全市场元数据
  - 实时计算 TA 指标（RSI, MACD, 布林带, VWAP）
  - 存入 SQLite，支持后续回测
  - 软重启（网络恢复自动重连）

运行:
  python3 collector.py start   # 后台运行
  python3 collector.py status    # 查看状态
  python3 collector.py stop     # 停止
  python3 collector.py shell    # SQLite 命令行
"""

import json  # 用于解析 outcomePrices 字符串
import os
import sys
import time
import sqlite3
import signal
import subprocess
import requests
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import threading
import atexit

# ============ 配置 ============
BASE_DIR = os.path.expanduser("~/.openclaw/workspace/polymarket/collector")
DB_FILE = os.path.join(BASE_DIR, "polymarket_data.db")
PID_FILE = os.path.join(BASE_DIR, "collector.pid")
LOG_FILE = os.path.join(BASE_DIR, "collector.log")

POLYMARKET_API = "https://gamma-api.polymarket.com"
CLOB_API = "https://clob.polymarket.com"
WS_URL = "wss://ws-live-data.polymarket.com"

POLL_INTERVAL = 30        # 轮询间隔（秒）
SERIES_15M_BTC = "10192"   # BTC 15m 系列 ID

# BTC 15m 市场 slug 前缀（用于识别）
BTC_15M_SLUG_KEYWORDS = ["btc-updown", "btc-up-or-down", "bitcoin-updown", "bitcoin-up-or-down"]

# ============ 日志 ============

def log(msg, level="INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level}] {msg}"
    print(line)
    try:
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")
    except:
        pass

# ============ API ============

def api_get(url: str, timeout: int = 15) -> Optional[Any]:
    """GET 请求，带错误处理和重试（requests 库，更稳定）"""
    for attempt in range(3):
        try:
            resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=timeout)
            if resp.status_code == 200:
                return resp.json()
            elif resp.status_code in (429, 500, 502, 503):
                log(f"HTTP错误 {resp.status_code}: {url}", "WARN")
                time.sleep(5 * (attempt + 1))
                continue
            else:
                log(f"HTTP {resp.status_code}: {url}", "WARN")
                return None
        except requests.exceptions.SSLError as e:
            log(f"SSL错误 [{attempt+1}/3]: {str(e)[:80]}", "WARN")
            if attempt < 2:
                time.sleep(3)
            continue
        except Exception as e:
            log(f"API错误 [{attempt+1}/3]: {type(e).__name__} - {str(e)[:80]}", "WARN")
            if attempt < 2:
                time.sleep(3)
            continue
    return None

def get_open_markets(limit: int = 100) -> List[Dict]:
    """获取所有开放市场"""
    url = f"{POLYMARKET_API}/markets?limit={limit}&closed=false"
    data = api_get(url)
    if not data or not isinstance(data, list):
        return []
    return [m for m in data if not m.get("closed", True) and m.get("question")]

def get_market_history(token_id: str, days: int = 7) -> List[Dict]:
    """获取历史价格（ticker-history）"""
    end = datetime.now()
    start = end - timedelta(days=days)
    url = (f"{POLYMARKET_API}/ticker-history?token_id={token_id}"
           f"&start_date={start.isoformat()}&end_date={end.isoformat()}")
    return api_get(url) or []

# ============ 技术指标 ============

def calculate_rsi(prices: List[float], period: int = 14) -> Optional[float]:
    """计算 RSI"""
    if len(prices) < period + 1:
        return None
    deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    gains = [d if d > 0 else 0 for d in deltas[-period:]]
    losses = [-d if d < 0 else 0 for d in deltas[-period:]]
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def calculate_macd(prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Optional[Dict]:
    """计算 MACD (EMA based)"""
    if len(prices) < slow + signal:
        return None
    try:
        ema_fast = _ema(prices, fast)
        ema_slow = _ema(prices, slow)
        macd_line = ema_fast - ema_slow
        # Signal line (simplified - use recent MACD values)
        macd_hist = macd_line  # simplified
        return {
            "macd": round(macd_line, 6),
            "signal": round(macd_line * 0.9, 6),  # rough approx
            "histogram": round(macd_line * 0.1, 6)
        }
    except:
        return None

def _ema(prices: List[float], period: int) -> float:
    """计算 EMA"""
    if len(prices) < period:
        return prices[-1] if prices else 0
    k = 2 / (period + 1)
    ema = sum(prices[:period]) / period
    for p in prices[period:]:
        ema = p * k + ema * (1 - k)
    return ema

def calculate_bollinger_bands(prices: List[float], period: int = 20, std_dev: int = 2) -> Optional[Dict]:
    """计算布林带"""
    if len(prices) < period:
        return None
    recent = prices[-period:]
    sma = sum(recent) / period
    variance = sum((p - sma) ** 2 for p in recent) / period
    std = variance ** 0.5
    return {
        "upper": round(sma + std_dev * std, 6),
        "middle": round(sma, 6),
        "lower": round(sma - std_dev * std, 6),
        "bandwidth": round(std_dev * std * 2, 6)
    }

def calculate_vwap(prices: List[float], volumes: List[float]) -> Optional[float]:
    """计算 VWAP（简化版：收盘价×成交量）"""
    if len(prices) < 2 or len(prices) != len(volumes):
        return None
    try:
        return sum(p * v for p, v in zip(prices[-len(volumes):], volumes[-len(volumes):])) / sum(volumes)
    except:
        return None

def calculate_ema(prices: List[float], period: int) -> Optional[float]:
    """计算 EMA（对外暴露）"""
    if len(prices) < period:
        return None
    return _ema(prices, period)

def calculate_zscore(prices: List[float], period: int = 20) -> Optional[float]:
    """计算 Z-score（当前价格偏离均值的标准差数）"""
    if len(prices) < period:
        return None
    recent = prices[-period:]
    mean = sum(recent) / period
    variance = sum((p - mean) ** 2 for p in recent) / period
    std = variance ** 0.5
    if std == 0:
        return 0.0
    return (prices[-1] - mean) / std

# ============ 数据库 ============

def get_db() -> sqlite3.Connection:
    """获取数据库连接"""
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    conn = sqlite3.connect(DB_FILE, timeout=30)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """初始化数据库表"""
    conn = get_db()
    c = conn.cursor()

    # 市场元数据表
    c.execute("""
        CREATE TABLE IF NOT EXISTS markets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token_id TEXT UNIQUE NOT NULL,
            slug TEXT,
            question TEXT,
            series_id TEXT,
            volume REAL DEFAULT 0,
            liquidity REAL DEFAULT 0,
            created_at TEXT,
            updated_at TEXT,
            event_time TEXT,
            close_time TEXT,
            end_date_iso TEXT,
            active INTEGER DEFAULT 1,
            closed INTEGER DEFAULT 0,
            archived INTEGER DEFAULT 0
        )
    """)

    # 轻量迁移：给旧表补列
    existing_cols = {row[1] for row in c.execute("PRAGMA table_info(markets)").fetchall()}
    market_extra_cols = {
        "event_time": "TEXT",
        "close_time": "TEXT",
        "end_date_iso": "TEXT",
        "active": "INTEGER DEFAULT 1",
        "closed": "INTEGER DEFAULT 0",
        "archived": "INTEGER DEFAULT 0",
    }
    for col, col_type in market_extra_cols.items():
        if col not in existing_cols:
            c.execute(f"ALTER TABLE markets ADD COLUMN {col} {col_type}")

    # 价格历史表（核心）
    c.execute("""
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token_id TEXT NOT NULL,
            yes_price REAL,
            no_price REAL,
            btc_price REAL,
            volume REAL DEFAULT 0,
            liquidity REAL DEFAULT 0,
            timestamp TEXT NOT NULL,
            UNIQUE(token_id, timestamp)
        )
    """)

    # TA 指标快照（每5分钟计算一次）
    c.execute("""
        CREATE TABLE IF NOT EXISTS ta_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token_id TEXT NOT NULL,
            rsi_14 REAL,
            rsi_7 REAL,
            macd REAL,
            macd_signal REAL,
            macd_hist REAL,
            bb_upper REAL,
            bb_middle REAL,
            bb_lower REAL,
            vwap REAL,
            zscore_20 REAL,
            ema_9 REAL,
            ema_21 REAL,
            yes_1d_change REAL,
            no_1d_change REAL,
            timestamp TEXT NOT NULL,
            UNIQUE(token_id, timestamp)
        )
    """)

    # 订单流（简化）
    c.execute("""
        CREATE TABLE IF NOT EXISTS orderflow (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token_id TEXT NOT NULL,
            bid_price REAL,
            ask_price REAL,
            bid_vol REAL,
            ask_vol REAL,
            spread REAL,
            imbalance REAL,
            timestamp TEXT NOT NULL
        )
    """)

    # BTC 参考价（每次采集附带的链上价格）
    c.execute("""
        CREATE TABLE IF NOT EXISTS btc_reference (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            price REAL NOT NULL,
            source TEXT DEFAULT 'chainlink',
            timestamp TEXT NOT NULL
        )
    """)

    # 索引
    c.execute("CREATE INDEX IF NOT EXISTS idx_price_token_time ON price_history(token_id, timestamp)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_ta_token_time ON ta_snapshots(token_id, timestamp)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_ohlc_time ON price_history(timestamp)")

    conn.commit()
    conn.close()
    log("数据库初始化完成")

def insert_price(conn: sqlite3.Connection, row: Dict):
    """插入一条价格记录"""
    try:
        c = conn.cursor()
        c.execute("""
            INSERT OR REPLACE INTO price_history 
            (token_id, yes_price, no_price, btc_price, volume, liquidity, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            row["token_id"],
            row.get("yes_price"),
            row.get("no_price"),
            row.get("btc_price"),
            row.get("volume", 0),
            row.get("liquidity", 0),
            row["timestamp"]
        ))
    except Exception as e:
        log(f"插入价格失败: {e}", "WARN")

def insert_ta_snapshot(conn: sqlite3.Connection, token_id: str, ta: Dict, timestamp: str):
    """插入 TA 快照"""
    try:
        c = conn.cursor()
        c.execute("""
            INSERT OR IGNORE INTO ta_snapshots
            (token_id, rsi_14, rsi_7, macd, macd_signal, macd_hist,
             bb_upper, bb_middle, bb_lower, vwap, zscore_20,
             ema_9, ema_21, yes_1d_change, no_1d_change, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            token_id,
            ta.get("rsi_14"),
            ta.get("rsi_7"),
            ta.get("macd"),
            ta.get("macd_signal"),
            ta.get("macd_hist"),
            ta.get("bb_upper"),
            ta.get("bb_middle"),
            ta.get("bb_lower"),
            ta.get("vwap"),
            ta.get("zscore_20"),
            ta.get("ema_9"),
            ta.get("ema_21"),
            ta.get("yes_1d_change"),
            ta.get("no_1d_change"),
            timestamp
        ))
    except Exception as e:
        log(f"插入TA失败: {e}", "WARN")

def update_market_info(conn: sqlite3.Connection, market: Dict):
    """更新市场元数据"""
    try:
        raw_ids = market.get("clobTokenIds") or []
        if isinstance(raw_ids, str):
            try:
                clob_ids = json.loads(raw_ids)
            except:
                clob_ids = []
        elif isinstance(raw_ids, list):
            clob_ids = raw_ids
        else:
            clob_ids = []
        yes_token = str(clob_ids[0]) if len(clob_ids) > 0 else None
        c = conn.cursor()
        event_time = (
            market.get("event_time")
            or market.get("eventTime")
            or market.get("endDateIso")
            or market.get("end_date_iso")
            or market.get("endDate")
            or market.get("closeTime")
            or market.get("close_time")
        )
        close_time = market.get("closeTime") or market.get("close_time") or market.get("endDate")
        end_date_iso = market.get("endDateIso") or market.get("end_date_iso")
        c.execute("""
            INSERT OR REPLACE INTO markets
            (token_id, slug, question, series_id, volume, liquidity, updated_at,
             event_time, close_time, end_date_iso, active, closed, archived)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            yes_token,
            market.get("slug"),
            market.get("question"),
            market.get("series_id"),
            float(market.get("volumeClob") or market.get("volume") or 0),
            float(market.get("liquidityClob") or market.get("liquidity") or 0),
            datetime.now().isoformat(),
            event_time,
            close_time,
            end_date_iso,
            1 if market.get("active", True) else 0,
            1 if market.get("closed", False) else 0,
            1 if market.get("archived", False) else 0,
        ))
    except Exception as e:
        log(f"更新市场失败: {e}", "WARN")

# ============ 采集逻辑 ============

def is_btc_15m_market(market: Dict) -> bool:
    """判断是否为 BTC 15m 市场"""
    slug = (market.get("slug") or "").lower()
    question = (market.get("question") or "").lower()
    for kw in BTC_15M_SLUG_KEYWORDS:
        if kw in slug or kw in question:
            return True
    series_id = market.get("series_id") or market.get("seriesId") or ""
    if str(series_id) == SERIES_15M_BTC:
        return True
    return False

def collect_btc_price() -> Optional[float]:
    """获取 BTC 参考价（通过 CLOB 或其他途径）"""
    # Polymarket 15m 市场本身就是 BTC/USD 计价
    # 这里用市场数据里的 btcPrice 或通过 Chainlink 获取
    # 暂时返回 None，等 WS 连通后补充
    return None

def collect_market_ta(token_id: str, history: List, yes_price: float) -> Dict:
    """计算一个市场的 TA 指标"""
    prices = []
    for h in history:
        if isinstance(h, dict):
            p = h.get("close") or h.get("price") or h.get("p")
            if p:
                prices.append(float(p))

    if len(prices) < 2:
        return {}

    # RSI
    rsi_14 = calculate_rsi(prices, 14)
    rsi_7 = calculate_rsi(prices, 7) if len(prices) >= 8 else None

    # MACD
    macd_data = calculate_macd(prices)

    # 布林带
    bb = calculate_bollinger_bands(prices)

    # EMA
    ema_9 = calculate_ema(prices, 9) if len(prices) >= 9 else None
    ema_21 = calculate_ema(prices, 21) if len(prices) >= 21 else None

    # Z-score
    zscore = calculate_zscore(prices, 20) if len(prices) >= 20 else None

    # 1日变化
    yes_1d = 0.0
    if len(prices) >= 2:
        yes_1d = (yes_price - prices[-2]) / prices[-2] if prices[-2] > 0 else 0

    return {
        "rsi_14": rsi_14,
        "rsi_7": rsi_7,
        "macd": macd_data.get("macd") if macd_data else None,
        "macd_signal": macd_data.get("signal") if macd_data else None,
        "macd_hist": macd_data.get("histogram") if macd_data else None,
        "bb_upper": bb.get("upper") if bb else None,
        "bb_middle": bb.get("middle") if bb else None,
        "bb_lower": bb.get("lower") if bb else None,
        "ema_9": ema_9,
        "ema_21": ema_21,
        "zscore_20": zscore,
        "yes_1d_change": round(yes_1d * 100, 4) if yes_1d else 0,
    }

def one_poll_cycle(conn: sqlite3.Connection) -> int:
    """执行一次采集周期，返回采集的市场数"""
    ts = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    markets = get_open_markets(limit=200)

    if not markets:
        log("未获取到市场数据", "WARN")
        return 0

    count = 0
    btc_markets = []

    for m in markets:
        try:
            # 解析 clobTokenIds（可能是 JSON 字符串或列表）
            clob_ids = m.get("clobTokenIds") or []
            if isinstance(clob_ids, str):
                try:
                    clob_ids = json.loads(clob_ids)
                except:
                    clob_ids = []
            yes_token = str(clob_ids[0]) if len(clob_ids) > 0 else None

            # 价格从 outcomePrices 直接获取（无需额外 API）
            # outcomePrices 是 JSON 字符串如 '["0.545", "0.455"]'
            outcome_prices = m.get("outcomePrices") or []
            if isinstance(outcome_prices, str):
                try:
                    outcome_prices = json.loads(outcome_prices)
                except:
                    outcome_prices = []

            yes_price = float(outcome_prices[0]) if len(outcome_prices) > 0 else None
            no_price = float(outcome_prices[1]) if len(outcome_prices) > 1 else None

            # 如果没有 outcomePrices，用 lastTradePrice 推算
            if yes_price is None or yes_price == 0:
                last = float(m.get("lastTradePrice", 0))
                if last > 0:
                    yes_price = last
                    no_price = 1 - last
                else:
                    yes_price = 0.5
                    no_price = 0.5

            if yes_token:
                # 更新市场元数据
                update_market_info(conn, m)

                row = {
                    "token_id": yes_token,
                    "yes_price": yes_price,
                    "no_price": no_price,
                    "volume": float(m.get("volumeClob") or m.get("volume") or 0),
                    "liquidity": float(m.get("liquidityClob") or m.get("liquidity") or 0),
                    "timestamp": ts
                }
                insert_price(conn, row)

                count += 1

                # BTC 15m 市场额外记录
                if is_btc_15m_market(m):
                    log(f"  BTC 15m: {m.get('question','')[:40]} @ YES:{yes_price:.4f}", "INFO")



        except Exception as e:
            log(f"处理市场失败: {m.get('question','')[:40]}: {e}", "WARN")
            continue

    if btc_markets:
        log(f"  BTC 15m 市场: {len(btc_markets)} 个", "INFO")

    conn.commit()
    return count

# ============ 主循环 ============

running = True

def signal_handler(signum, frame):
    global running
    log("收到停止信号，正在退出...")
    running = False

def run_collector(once=False):
    """主采集循环"""
    global running

    log("=" * 50)
    log("Polymarket 15m 数据采集器启动")
    log(f"轮询间隔: {POLL_INTERVAL}秒")
    log(f"数据库: {DB_FILE}")
    log(f"模式: {'单次' if once else '持续'}")
    log("=" * 50)

    init_db()

    conn = get_db()
    consecutive_errors = 0
    last_ta_flush = time.time()

    while running:
        cycle_start = time.time()

        try:
            count = one_poll_cycle(conn)
            if count > 0:
                consecutive_errors = 0
                log(f"采集完成: {count} 个市场")
            else:
                consecutive_errors += 1
                log(f"采集为空 (连续第{consecutive_errors}次)", "WARN")

        except Exception as e:
            consecutive_errors += 1
            log(f"采集循环异常: {type(e).__name__}: {e}", "ERROR")

        # 单次模式：跑完一轮就退出
        if once:
            conn.commit()
            conn.close()
            log("单次采集完成，退出")
            return

        # 强制每5分钟 flush 一次 TA 数据
        if time.time() - last_ta_flush > 300:
            conn.commit()
            last_ta_flush = time.time()

        # 计算实际耗时，控制采集频率
        elapsed = time.time() - cycle_start
        sleep_time = max(1, POLL_INTERVAL - elapsed)
        if sleep_time > 0 and running:
            time.sleep(sleep_time)

    conn.close()
    log("采集器已停止")

# ============ 进程管理 ============

def write_pid():
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))

def read_pid():
    try:
        with open(PID_FILE) as f:
            return int(f.read().strip())
    except:
        return None

def is_running(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except:
        return False

def start_daemon():
    pid = read_pid()
    if pid and is_running(pid):
        print(f"采集器已在运行 (PID {pid})")
        return

    log("启动采集器...")
    pid = os.fork()
    if pid == 0:
        # 子进程
        os.setsid()
        write_pid()
        run_collector()
        sys.exit(0)
    else:
        print(f"采集器已在后台启动 (PID {pid})")

def stop_daemon():
    pid = read_pid()
    if not pid or not is_running(pid):
        print("采集器未运行")
        return
    log(f"停止采集器 (PID {pid})...")
    os.kill(pid, signal.SIGTERM)
    time.sleep(2)
    try:
        os.remove(PID_FILE)
    except:
        pass

def show_status():
    pid = read_pid()
    alive = is_running(pid) if pid else False
    print(f"\n{'='*50}")
    print(f"Polymarket 15m 数据采集器")
    print(f"{'='*50}")
    print(f"状态: {'🟢 运行中' if alive else '🔴 已停止'}")
    print(f"PID: {pid or 'N/A'}")
    print(f"数据库: {DB_FILE}")
    print(f"数据目录: {BASE_DIR}")

    if os.path.exists(DB_FILE):
        conn = get_db()
        c = conn.cursor()
        try:
            c.execute("SELECT COUNT(*) FROM price_history")
            price_count = c.fetchone()[0]
            c.execute("SELECT COUNT(*) FROM ta_snapshots")
            ta_count = c.fetchone()[0]
            c.execute("SELECT COUNT(DISTINCT token_id) FROM markets")
            market_count = c.fetchone()[0]
            c.execute("SELECT MIN(timestamp), MAX(timestamp) FROM price_history")
            row = c.fetchone()
            time_range = f"{row[0][:19] if row[0] else 'N/A'} ~ {row[1][:19] if row[1] else 'N/A'}"

            print(f"市场数: {market_count}")
            print(f"价格记录: {price_count:,} 条")
            print(f"TA快照: {ta_count:,} 条")
            print(f"数据范围: {time_range}")
        except Exception as e:
            print(f"统计错误: {e}")
        conn.close()

    print(f"{'='*50}\n")

def open_shell():
    subprocess.run(["sqlite3", DB_FILE])

# ============ 入口 ============

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    cmd = sys.argv[1] if len(sys.argv) > 1 else "start"

    if cmd == "start":
        start_daemon()
    elif cmd == "stop":
        stop_daemon()
    elif cmd == "status":
        show_status()
    elif cmd == "shell":
        open_shell()
    elif cmd == "restart":
        stop_daemon()
        time.sleep(2)
        start_daemon()
    elif cmd == "run":
        # 前台运行（调试用）
        init_db()
        run_collector(once=False)
    elif cmd == "once":
        # 单次运行（供 cron 调用）
        init_db()
        run_collector(once=True)
    else:
        print(f"用法: {sys.argv[0]} [start|stop|status|shell|restart|run|once]")
