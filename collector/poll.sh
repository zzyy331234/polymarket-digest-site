#!/bin/bash
# Polymarket 数据采集 - cron 驱动
DIR="$HOME/.openclaw/workspace/polymarket/collector"
cd "$DIR" || exit 1
python3 collector.py run >> "${DIR}/collector_stdout.log" 2>&1
