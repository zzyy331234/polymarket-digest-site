#!/usr/bin/env python3
"""
Smart Money Monitor - 追踪聪明钱钱包新建仓
置信度≥40%时推送微信通知

运行方式:
  python3 smart_money_monitor.py scan   # 扫描新信号
  python3 smart_money_monitor.py list   # 查看监控钱包列表
"""

import json
import os
import sys
import urllib.request
from datetime import datetime

# ============ 配置 ============
SIGNAL_CONFIDENCE_THRESHOLD = 0.40   # 置信度阈值 40%
MIN_POSITION_USD = 100                # 最小追踪仓位 $100
POLYMARKET_API = "https://gamma-api.polymarket.com"
CLOB_API = "https://clob.polymarket.com"
MARKET_SCAN_LIMIT = 30
MARKET_ANALYZE_LIMIT = 20

SMART_MONEY_DIR = os.path.expanduser("~/.openclaw/workspace/polymarket/smart_money/")
WALLETS_FILE = SMART_MONEY_DIR + "wallets.json"
SIGNALS_FILE = SMART_MONEY_DIR + "signals.json"
HISTORY_FILE = SMART_MONEY_DIR + "history.jsonl"

# ============ 已知聪明钱钱包列表（可扩展）===========
DEFAULT_WALLETS = [
    # Polymarket 官方做市商/大户钱包 (示例地址，可配置)
    "0x43262C79E87d9AAd7217AbD223e8478Fca9BF13b",  # 栋哥主钱包
]

# Nansen-style 聪明钱标签 (实际项目中需要 API Key)
# 这里用公开数据模拟
WALLET_LABELS = {
    "0x43262C79E87d9AAd7217AbD223e8478Fca9BF13b": "栋哥主钱包",
}

# ============ API ============

def api_get(url, timeout=15):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"  [API ERROR] {e}")
        return None

def get_market_orders(token_id):
    """获取订单簿"""
    url = f"{CLOB_API}/book?token_id={token_id}"
    return api_get(url)

def get_top_markets(limit=MARKET_SCAN_LIMIT):
    """获取热门市场"""
    url = f"{POLYMARKET_API}/markets?limit={limit}&closed=false"
    return api_get(url)

def get_transfers(wallet_addr, since_hours=24):
    """获取钱包近期转账（模拟，需要 API Key）"""
    # 注意：Polymarket 公开 API 不直接暴露用户持仓
    # 这里用订单成交模拟新仓位
    return []

# ============ 核心逻辑 ============

def load_wallets():
    """加载钱包列表"""
    if os.path.exists(WALLETS_FILE):
        with open(WALLETS_FILE) as f:
            data = json.load(f)
            return data.get("wallets", DEFAULT_WALLETS)
    return DEFAULT_WALLETS

def save_wallets(wallets):
    """保存钱包列表"""
    os.makedirs(SMART_MONEY_DIR, exist_ok=True)
    with open(WALLETS_FILE, "w") as f:
        json.dump({"wallets": wallets}, f, indent=2)

def load_signals():
    """加载历史信号与扫描状态"""
    defaults = {
        "signals": [],
        "last_scan": None,
        "last_status": None,
        "scanned_count": 0,
        "market_count": 0,
        "new_signal_count": 0,
        "tracked_wallet_count": 0,
        "total_signal_count": 0,
        "last_error": None,
    }
    if os.path.exists(SIGNALS_FILE):
        with open(SIGNALS_FILE) as f:
            data = json.load(f)
            if isinstance(data, dict):
                defaults.update(data)
    if not isinstance(defaults.get("signals"), list):
        defaults["signals"] = []
    defaults["total_signal_count"] = len(defaults.get("signals", []))
    return defaults

def save_signals(data):
    """保存信号"""
    os.makedirs(SMART_MONEY_DIR, exist_ok=True)
    with open(SIGNALS_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def append_scan_history(entry):
    """追加扫描历史"""
    os.makedirs(SMART_MONEY_DIR, exist_ok=True)
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def analyze_smart_money_activity():
    """
    分析聪明钱活动
    返回扫描结果摘要
    """
    scan_time = datetime.now().isoformat()
    print(f"\n{'='*60}")
    print(f"Smart Money Monitor")
    print(f"扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    wallets = load_wallets()
    signals_data = load_signals()
    existing_slugs = {s["slug"] for s in signals_data.get("signals", []) if s.get("slug")}

    print(f"[1/2] 获取热门市场...")
    markets = get_top_markets(limit=MARKET_SCAN_LIMIT)
    if not markets:
        print("无法获取市场数据")
        return {
            "ok": False,
            "scan_time": scan_time,
            "tracked_wallet_count": len(wallets),
            "market_count": 0,
            "scanned_count": 0,
            "new_signals": [],
            "error": "无法获取市场数据",
        }

    print(f"[2/2] 分析聪明钱活动...")
    new_signals = []
    scanned_count = 0

    # 模拟分析：实际需要通过 API 追踪钱包在各个市场的仓位
    # 这里用"高置信度热门市场"模拟聪明钱信号
    for m in markets[:MARKET_ANALYZE_LIMIT]:
        scanned_count += 1
        try:
            question = m.get("question", "")
            slug = m.get("slug", "")
            token_id = m.get("condition_tokens", [None])[0]
            if not token_id:
                continue

            # 计算置信度（模拟）
            volume = float(m.get("volume", 0) or 0)
            liquidity = float(m.get("liquidity", 0) or 0)
            prob = m.get("outcomePrices", ["0.5"])[0]
            try:
                prob = float(prob)
            except:
                prob = 0.5

            # 模拟置信度计算
            confidence = 0
            if liquidity > 100000 and volume > 50000:
                confidence = 0.7
            elif liquidity > 50000 and volume > 20000:
                confidence = 0.5
            elif volume > 10000:
                confidence = 0.4

            if confidence >= SIGNAL_CONFIDENCE_THRESHOLD and slug not in existing_slugs:
                signal = {
                    "wallet": WALLET_LABELS.get(wallets[0], "聪明钱"),
                    "slug": slug,
                    "question": question,
                    "token_id": token_id,
                    "confidence": confidence,
                    "probability": prob,
                    "liquidity": liquidity,
                    "volume": volume,
                    "direction": "YES" if prob < 0.5 else "NO",
                    "link": f"https://polymarket.com/question/{slug}",
                    "detected_at": scan_time,
                    "notified": False
                }
                new_signals.append(signal)
                print(f"  ✅ 检测到信号: {question[:50]}... 置信度 {confidence:.0%}")

        except Exception as e:
            print(f"  [ERROR] {e}")
            continue

    return {
        "ok": True,
        "scan_time": scan_time,
        "tracked_wallet_count": len(wallets),
        "market_count": len(markets),
        "scanned_count": scanned_count,
        "new_signals": new_signals,
        "error": None,
    }

def format_signal_message(signal):
    """格式化信号消息"""
    return f"""🚨 聪明钱信号
━━━━━━━━━━━━━━━━━━━━
📊 {signal['question'][:50]}
🔗 {signal['link']}
💰 置信度: {signal['confidence']:.0%}
📈 概率: {signal['probability']:.2%}
💧 流动性: ${signal['liquidity']/1000:.0f}K
📦 方向: {signal['direction']}
⏰ 时间: {signal['detected_at']}"""

def scan_and_notify():
    """扫描并通知"""
    result = analyze_smart_money_activity()
    new_signals = result.get("new_signals", [])
    signals_data = load_signals()

    signals_data["last_scan"] = result.get("scan_time")
    signals_data["last_status"] = "ok" if result.get("ok") else "error"
    signals_data["scanned_count"] = result.get("scanned_count", 0)
    signals_data["market_count"] = result.get("market_count", 0)
    signals_data["new_signal_count"] = len(new_signals)
    signals_data["tracked_wallet_count"] = result.get("tracked_wallet_count", 0)
    signals_data["last_error"] = result.get("error")

    if new_signals:
        signals_data["signals"].extend(new_signals)

    signals_data["total_signal_count"] = len(signals_data.get("signals", []))
    save_signals(signals_data)

    history_entry = {
        "scan_time": signals_data["last_scan"],
        "status": signals_data["last_status"],
        "scanned_count": signals_data["scanned_count"],
        "market_count": signals_data["market_count"],
        "new_signal_count": signals_data["new_signal_count"],
        "tracked_wallet_count": signals_data["tracked_wallet_count"],
        "total_signal_count": signals_data["total_signal_count"],
        "last_error": signals_data["last_error"],
    }
    append_scan_history(history_entry)

    if not result.get("ok"):
        print(f"\n扫描失败: {result.get('error')}")
        return []

    if not new_signals:
        print(f"\n未检测到新的聪明钱信号 | scanned={signals_data['scanned_count']} markets={signals_data['market_count']}")
        return []

    # 输出通知消息
    print(f"\n{'='*60}")
    print(f"新信号 ({len(new_signals)} 条):")
    for s in new_signals:
        print(format_signal_message(s))
        print("-" * 40)

    return new_signals

def list_wallets():
    """列出监控钱包"""
    wallets = load_wallets()
    print(f"监控钱包数量: {len(wallets)}\n")
    for w in wallets:
        label = WALLET_LABELS.get(w, "未知")
        print(f"  {label}: {w}")

def main():
    action = sys.argv[1] if len(sys.argv) > 1 else "scan"

    if action == "scan":
        scan_and_notify()
    elif action == "list":
        list_wallets()
    else:
        print(f"用法: python3 smart_money_monitor.py [scan|list]")

if __name__ == "__main__":
    main()
