# Polymarket 情报样刊站点继续推进计划

## Goal
把当前 digest 站点从“本地可看”推进到“可交付、可部署、可复用”的状态，优先补齐部署文件与发布版内部路径问题。

## Phases
- [x] Phase 1 — 检查当前发布结构与现有流水线接入情况
- [x] Phase 2 — 修正发布版内部链接路径，使 dist/digest_site 成为真正独立站点
- [x] Phase 3 — 补充一键部署文件（优先 GitHub Pages / 通用静态托管）
- [x] Phase 4 — 重新生成并验证发布站点导航与部署文件
- [x] Phase 5 — 检查 git / GitHub 环境并确定自动发布接入方式
- [x] Phase 6 — 新增 GitHub Pages 一键发布脚本与 Actions 工作流
- [x] Phase 7 — 验证发布文件并补项目说明

## Decisions
- 继续沿用 dist/digest_site 作为最终交付目录
- 先做通用静态托管友好的发布结构，再考虑平台专属自动部署
- 优先修正当前发布版里仍指向 reports/ 和 outputs/ 的坏链接

## Errors Encountered
- 暂无
