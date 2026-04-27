#!/bin/bash
# Smart Money Monitor Cron Runner
LOG_FILE="/Users/mac/.openclaw/workspace/memory/smartmoney_scan.log"
ERROR_FILE="/Users/mac/.openclaw/workspace/memory/smartmoney_scan.error"

cd /Users/mac/.openclaw/workspace/polymarket
python3 smart_money_monitor.py scan >> "$LOG_FILE" 2>> "$ERROR_FILE"
echo "---EOF---" >> "$LOG_FILE"
