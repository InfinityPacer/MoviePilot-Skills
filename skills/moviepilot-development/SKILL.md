---
name: moviepilot-development
description: Use for local development, diagnosis, reproduction, testing, runtime debugging, or topic-branch preparation in supported MoviePilot repositories before external delivery. Do not use for push, pull request, merge, or release-only requests.
---

# MoviePilot 开发

## 范围

处理 `MoviePilot`、`MoviePilot-Frontend`、`MoviePilot-Rust`、Wiki、Resources、Server、维护中的
私有 MoviePilot 上游目标、个人插件仓和官方插件 fork 的本地开发、调试、测试与运行态验证。私有
目标从全局私有 reference 与当前 remote 解析，不写入本公开 skill；未列入范围的仓库不因名称带有
`MoviePilot` 就自动套用本 skill。

工作区 `AGENTS.md` 和目标仓库更近的说明负责项目结构、环境、测试命令、运行态证据与 Rust ABI
等事实；本 skill 不复制这些内容。执行前读取适用说明，检查当前仓库、目标文件、工作树和 remote。
remote 角色按 URL 与仓库身份识别，不按 `origin`、`upstream` 或 `fork` 等本地名称猜测。

## 开发边界

- 先按工作区规则确认问题主体是本地实例、外部实例还是实验室复现，不用本机状态替代外部现场。
- 已知会进入评审时，按 remote URL 识别并刷新权威 base，核对 merge-base、base 到 HEAD 的提交范围
  和分支主题；不满足时保留有效工作并迁到合适的业务 topic branch。跨仓改动分别建立分支、提交
  和验证。
- 保留当前任务改动；不混入、reset、stash 或覆盖无关改动。只有无法安全隔离时才使用用户授权的
  worktree 或询问必要问题。
- 按受影响路径和更近规则选择最小可信验证；不在 skill 中固化易漂移的命令副本。
- 本地 commit 服从 `dev-workflow`、已批准计划或当前授权。本 skill 不 push、不创建 PR、不 merge、
  不发版。

## 完成

说明仓库与分支、改动范围、实际验证、未验证原因类别和工作树状态。需要外部交付时继续使用
`moviepilot-delivery`，不得把本地开发完成误报为 PR 或发布完成。
