#!/bin/bash
# 读取现有 crontab，追加 collector 任务
CRONTMP="/tmp/crontab_backup_$$"
/usr/bin/crontab -l > "$CRONTMP" 2>/dev/null
echo "# Polymarket 15m Data Collector - every 1 min" >> "$CRONTMP"
echo "* * * * * /Users/mac/.openclaw/workspace/polymarket/collector/run_collector.sh >> /Users/mac/.openclaw/workspace/polymarket/collector/cron.log 2>&1" >> "$CRONTMP"
/usr/bin/crontab "$CRONTMP"
rm -f "$CRONTMP"
echo "Done. New crontab:"
/usr/bin/crontab -l | grep -A1 "Polymarket 15m"
