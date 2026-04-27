#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

echo "[$(date '+%F %T')] run v2 scan (read from DB)"
python3 "$ROOT/run_v2_scan.py"

echo "[$(date '+%F %T')] refresh scanner cache"
bash "$ROOT/refresh_scanner.sh"

echo "[$(date '+%F %T')] run review pipeline"
python3 "$ROOT/review_pipeline.py"

echo "[$(date '+%F %T')] run alert pipeline"
python3 "$ROOT/alert_pipeline.py"

echo "[$(date '+%F %T')] run paper trader"
python3 "$ROOT/paper_trader.py"

echo "[$(date '+%F %T')] build paper report + proposal"
python3 "$ROOT/paper_report.py"

echo "[$(date '+%F %T')] proposal files ready: $ROOT/outputs/proposed_config_patch.json $ROOT/outputs/proposed_config_patch.md"

echo "[$(date '+%F %T')] build daily report"
python3 "$ROOT/daily_report.py"

echo "[$(date '+%F %T')] daily report ready: $ROOT/outputs/daily_report_latest.md $ROOT/reports/daily"

echo "[$(date '+%F %T')] build intelligence brief"
python3 "$ROOT/daily_intelligence_report.py"

echo "[$(date '+%F %T')] intelligence brief ready: $ROOT/outputs/daily_intelligence_latest.md $ROOT/reports/intelligence"

echo "[$(date '+%F %T')] build weekly intelligence summary"
python3 "$ROOT/weekly_intelligence_summary.py"

echo "[$(date '+%F %T')] weekly intelligence summary ready: $ROOT/outputs/weekly_intelligence_summary.md $ROOT/reports/weekly_intelligence"

echo "[$(date '+%F %T')] build short intelligence digest"
python3 "$ROOT/short_intelligence_digest.py"

echo "[$(date '+%F %T')] render digest html site"
python3 "$ROOT/render_digest_page.py"

echo "[$(date '+%F %T')] auto publish digest repo"
bash "$ROOT/scripts/auto_publish_digest.sh"

echo "[$(date '+%F %T')] short intelligence digest ready: $ROOT/outputs/short_intelligence_digest_latest.md $ROOT/reports/short_digest $ROOT/dist/digest_site"

echo "[$(date '+%F %T')] done"
