#!/bin/bash
set -euo pipefail

ROOT="/Users/mac/.openclaw/workspace/polymarket"
SITE_DIR="$ROOT/dist/digest_site"
PUBLISH_BRANCH="${1:-gh-pages}"
EXPORT_DIR="${2:-$ROOT/dist/gh-pages-export}"

cd "$ROOT"

echo "[$(date '+%F %T')] rebuild digest site"
python3 "$ROOT/short_intelligence_digest.py"
python3 "$ROOT/render_digest_page.py"

if [ ! -f "$SITE_DIR/index.html" ]; then
  echo "digest site missing: $SITE_DIR/index.html" >&2
  exit 1
fi

rm -rf "$EXPORT_DIR"
mkdir -p "$EXPORT_DIR"
cp -R "$SITE_DIR"/. "$EXPORT_DIR"/

cat > "$EXPORT_DIR/.gitignore" <<'EOF'
.DS_Store
EOF

cd "$EXPORT_DIR"
git init -b "$PUBLISH_BRANCH" >/dev/null 2>&1 || git init >/dev/null
git checkout -B "$PUBLISH_BRANCH" >/dev/null 2>&1 || true
git add .
if git diff --cached --quiet; then
  echo "no site changes to commit"
else
  git commit -m "Publish digest site $(date '+%F %T')" >/dev/null
fi

echo
printf '站点已导出到：%s\n' "$EXPORT_DIR"
printf '下一步手动发布：\n'
printf '1) cd %s\n' "$EXPORT_DIR"
printf '2) git remote add origin <你的仓库地址>   # 如果还没配\n'
printf '3) git push -f origin %s\n' "$PUBLISH_BRANCH"
printf '\n注意：当前环境未登录 GitHub，脚本只负责生成可推送的 gh-pages 内容。\n'
