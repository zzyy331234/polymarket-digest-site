#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "not a git repository: $ROOT" >&2
  exit 1
fi

if ! git remote get-url origin >/dev/null 2>&1; then
  echo "missing git remote origin; skip auto publish"
  exit 0
fi

BRANCH="$(git branch --show-current)"
if [ -z "$BRANCH" ]; then
  echo "cannot detect current branch; skip auto publish"
  exit 0
fi

FILES=(
  ".github/workflows/deploy-digest-site.yml"
  "dist/digest_site"
  "outputs"
  "reports"
  "portfolio_state.json"
  "trade_log.jsonl"
  "trading_config.json"
  "run_paper_cycle.sh"
  "render_digest_page.py"
  "short_intelligence_digest.py"
  "daily_intelligence_report.py"
  "weekly_intelligence_summary.py"
  "scripts/publish_digest_site.sh"
  "scripts/auto_publish_digest.sh"
  "findings.md"
  "progress.md"
  "task_plan.md"
  "smart_money/history.jsonl"
  "smart_money/signals.json"
)

EXISTING=()
for path in "${FILES[@]}"; do
  if [ -e "$path" ]; then
    EXISTING+=("$path")
  fi
done

if [ ${#EXISTING[@]} -eq 0 ]; then
  echo "no tracked publish targets found; skip auto publish"
  exit 0
fi

git add "${EXISTING[@]}"

if git diff --cached --quiet; then
  echo "no digest changes to publish"
  exit 0
fi

STAMP="$(date '+%F %T')"
git commit -m "Auto-publish digest ${STAMP}"
git push origin "$BRANCH"

echo "auto-published digest to origin/${BRANCH}"
