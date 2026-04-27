#!/bin/bash
set -euo pipefail

cd /Users/mac/.openclaw/workspace/polymarket

echo "[$(date '+%F %T')] run v2 scan (read from DB)"
python3 /Users/mac/.openclaw/workspace/polymarket/run_v2_scan.py

echo "[$(date '+%F %T')] refresh scanner cache"
bash /Users/mac/.openclaw/workspace/polymarket/refresh_scanner.sh

echo "[$(date '+%F %T')] run review pipeline"
python3 /Users/mac/.openclaw/workspace/polymarket/review_pipeline.py

echo "[$(date '+%F %T')] run alert pipeline"
python3 /Users/mac/.openclaw/workspace/polymarket/alert_pipeline.py

echo "[$(date '+%F %T')] run paper trader"
python3 /Users/mac/.openclaw/workspace/polymarket/paper_trader.py

echo "[$(date '+%F %T')] build paper report + proposal"
python3 /Users/mac/.openclaw/workspace/polymarket/paper_report.py

echo "[$(date '+%F %T')] proposal files ready: /Users/mac/.openclaw/workspace/polymarket/outputs/proposed_config_patch.json /Users/mac/.openclaw/workspace/polymarket/outputs/proposed_config_patch.md"

echo "[$(date '+%F %T')] build daily report"
python3 /Users/mac/.openclaw/workspace/polymarket/daily_report.py

echo "[$(date '+%F %T')] daily report ready: /Users/mac/.openclaw/workspace/polymarket/outputs/daily_report_latest.md /Users/mac/.openclaw/workspace/polymarket/reports/daily"

echo "[$(date '+%F %T')] build intelligence brief"
python3 /Users/mac/.openclaw/workspace/polymarket/daily_intelligence_report.py

echo "[$(date '+%F %T')] intelligence brief ready: /Users/mac/.openclaw/workspace/polymarket/outputs/daily_intelligence_latest.md /Users/mac/.openclaw/workspace/polymarket/reports/intelligence"

echo "[$(date '+%F %T')] build weekly intelligence summary"
python3 /Users/mac/.openclaw/workspace/polymarket/weekly_intelligence_summary.py

echo "[$(date '+%F %T')] weekly intelligence summary ready: /Users/mac/.openclaw/workspace/polymarket/outputs/weekly_intelligence_summary.md /Users/mac/.openclaw/workspace/polymarket/reports/weekly_intelligence"

echo "[$(date '+%F %T')] build short intelligence digest"
python3 /Users/mac/.openclaw/workspace/polymarket/short_intelligence_digest.py

echo "[$(date '+%F %T')] render digest html site"
python3 /Users/mac/.openclaw/workspace/polymarket/render_digest_page.py

echo "[$(date '+%F %T')] short intelligence digest ready: /Users/mac/.openclaw/workspace/polymarket/outputs/short_intelligence_digest_latest.md /Users/mac/.openclaw/workspace/polymarket/reports/short_digest /Users/mac/.openclaw/workspace/polymarket/dist/digest_site"

echo "[$(date '+%F %T')] done"
