# Progress

## 2026-04-27 Session
- 读取并检查 `render_digest_page.py` 当前发布逻辑。
- 确认 `run_paper_cycle.sh` 已接入 HTML 渲染。
- 发现发布版路径仍未完全独立，并完成修复：发布版 latest/archive 页面已改为只引用 `dist/digest_site` 内部相对路径。
- 新增部署辅助文件：`dist/digest_site/README.md`、`dist/digest_site/.nojekyll`、`dist/digest_site/vercel.json`。
- 重新运行 `python3 render_digest_page.py` 并验证发布入口、latest 页面、archive 页面导航正常。
- 检查 git / GitHub 环境：当前在 `main` 分支、已安装 `gh`，但尚未登录 GitHub。
- 新增 `.github/workflows/deploy-digest-site.yml`，用于 GitHub Pages 自动发布 `dist/digest_site`。
- 新增 `scripts/publish_digest_site.sh`，用于本地导出可推送到 `gh-pages` 分支的站点目录。
- 一次额外验证命令被环境拦截（用户未授权删除 `dist/gh-pages-export`），因此保留现状，不重复强推执行。
- 使用 PAT 成功完成 `gh` 登录，并确认账号为 `zzyy331234`。
- 将 `polymarket` 目录初始化为独立 git 仓库，新增 `.gitignore`，排除了嵌套仓库 `mcp_server/`，并完成首个 commit。
- 尝试用 `gh repo create polymarket-digest-site --private --source . --remote origin --push` 创建远端失败；REST API 建仓也失败，原因都是当前 PAT 无建仓权限。
- 结论：本地独立仓库与 GitHub Pages workflow 都已就绪，但还需要用户手动创建空仓库，或换一个有 `createRepository` 权限的 token，才能继续 push 和启用自动发布。
- 后续已换 classic token，成功 push 到 `origin/main`，并验证 workflow 被自动触发。
- 首次 Actions 失败是因为脚本使用了本机绝对路径 `/Users/mac/.openclaw/workspace/polymarket`；现已修复为 `Path(__file__).resolve().parent` 的相对路径写法，并再次 push。
- 第二次 Actions 构建与 artifact 上传都成功，最终失败点只剩 `Deploy to GitHub Pages` 返回 404，原因是仓库尚未在 Settings → Pages 中启用 Pages。
- 新增 `scripts/auto_publish_digest.sh`，把 digest 相关产物定向 `git add`、检测 staged diff、自动 commit + push 到当前分支。
- `run_paper_cycle.sh` 已接入自动发布脚本，且改成完全基于仓库相对路径执行，不再依赖本机绝对路径。
- 额外补了一层容错：若仓库缺少 `origin` 或当前分支不可识别，自动发布脚本会优雅跳过，不会把整条出刊流水线打死。
- 已本地执行自动发布脚本两次并验证：第一次成功推送 commit `6b35a35`，第二次成功推送 commit `4148df7`；当前工作树干净。
- 已检查 GitHub Actions 最近运行记录：`Deploy Digest Site` 对应 push 触发的 run `24981885021` 状态为 success，说明“本地提交/推送 → GitHub Actions 发布”链路已打通。
