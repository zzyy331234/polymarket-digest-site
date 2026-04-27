# Findings

## 2026-04-27 当前检查
- `run_paper_cycle.sh` 已接入 `render_digest_page.py`，总流水线能自动刷新 `dist/digest_site`。
- `render_digest_page.py` 已能生成 latest、archive、manifest 与发布版入口。
- 发现一个关键问题：发布版内部仍混有指向 `../reports/short_digest_html/...`、`../../outputs/...`、`../../dist/digest_site/...` 的链接。
- 这意味着 `dist/digest_site` 目前不是完全自洽的独立静态站；如果直接部署到 GitHub Pages/Vercel，这些链接会失效。
- 当前下一步最值当的是：抽象“本地工作区链接”和“发布版链接”两套 href 规则，再补一个部署说明/配置文件。
- 当前仓库已经是 git 仓库，分支为 `main`，本机安装了 `gh` CLI，但还没有登录 GitHub（`gh auth status` 失败）。
- 因为当前未登录 GitHub，最稳妥方案是双轨：仓库内提供 GitHub Actions 自动部署工作流，同时提供本地 `scripts/publish_digest_site.sh` 导出脚本，便于手动推送到 `gh-pages`。
- 之后已用 PAT 成功登录 `gh`，并把 `polymarket` 目录重建为独立 git 仓库。
- 但当前 PAT 权限不足，无法创建 GitHub 仓库：`createRepository` / `POST /user/repos` 都返回 `Resource not accessible by personal access token`。
- 这说明自动发布配置已经就绪，但真正推远端还差一个具备建仓权限的 token，或者需要用户先手动在 GitHub 上创建空仓库。
- 后续已用 classic token 成功 push 到 `zzyy331234/polymarket-digest-site`，并修复了脚本里的硬编码绝对路径，改成仓库相对路径，GitHub Actions 构建已通过。
- 当前最后一个剩余动作不是代码修改，而是去仓库设置页手动启用 GitHub Pages；否则 `actions/deploy-pages@v4` 会返回 404（GitHub 明确要求先启用 Pages）。
- 自动发布脚本现在采用“白名单 add + staged diff 检测”的方式，只提交 digest 相关产物，不会因为无变化而报错。
- 自动发布脚本对缺失 `origin`、无法识别 branch 这类环境问题改成了 graceful skip，适合继续挂在总流水线末尾。
- 本地 `git rev-parse HEAD` 当前为 `4148df73efa676d183fb4fc8799ca1572a7f9ee0`，工作树干净；说明自动发布后没有遗留未提交改动。
- `gh run list` 已验证至少一条 push 触发的部署成功记录：run `24981885021`，title `Auto-publish digest 2026-04-27 15:21:39`，workflow `Deploy Digest Site`，结论为 success。
