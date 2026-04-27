#!/bin/bash
# Polymarket 15m 数据采集 - 单次轮询（供 cron 调用）
# crontab 设置: * * * * * /Users/mac/.openclaw/workspace/polymarket/collector/run_collector.sh

DIR="$HOME/.openclaw/workspace/polymarket/collector"
LOG="$DIR/collector.log"

cd "$DIR" || exit 1

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
echo "[$TIMESTAMP] Cron轮询开始" >> "$LOG"
python3 collector.py once 2>&1 | head -5 >> "$LOG"
echo "[$TIMESTAMP] Cron轮询完成" >> "$LOG"
