# Findings

## 2026-04-27 当前检查
- `run_paper_cycle.sh` 已接入 `render_digest_page.py`，总流水线能自动刷新 `dist/digest_site`。
- `render_digest_page.py` 已能生成 latest、archive、manifest 与发布版入口。
- 发现一个关键问题：发布版内部仍混有指向 `../reports/short_digest_html/...`、`../../outputs/...`、`../../dist/digest_site/...` 的链接。
- 这意味着 `dist/digest_site` 目前不是完全自洽的独立静态站；如果直接部署到 GitHub Pages/Vercel，这些链接会失效。
- 当前下一步最值当的是：抽象“本地工作区链接”和“发布版链接”两套 href 规则，再补一个部署说明/配置文件。
- 当前仓库已经是 git 仓库，分支为 `main`，本机安装了 `gh` CLI，但还没有登录 GitHub（`gh auth status` 失败）。
- 因为当前未登录 GitHub，最稳妥方案是双轨：仓库内提供 GitHub Actions 自动部署工作流，同时提供本地 `scripts/publish_digest_site.sh` 导出脚本，便于手动推送到 `gh-pages`。
