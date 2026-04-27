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
