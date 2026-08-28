---
name: moviepilot-delivery
description: Use for commit-and-publish, push, pull request creation or follow-up, merge, version bump, plugin release, or issue delivery in supported MoviePilot repositories. Uses fork-based upstream contribution rules for jxxghp targets.
---

# MoviePilot 交付

## 范围与授权

先建立用户要求的终态：本地 commit、上游 PR 创建、PR 跟踪并合并、个人插件 PR-only，或个人插件
发版。commit、push、PR、merge、release 和公开回复分别服从 `dev-workflow`、已批准计划、Goal 或
当前用户授权；账户能力不构成当前任务授权。

检查当前仓库、remote、分支、base、提交范围、验证证据和工作树。remote 角色按 URL 与仓库身份
识别，不按本地名称猜测。跨仓改动分别交付，不混成一个 PR。

## 稳定能力与 Fork

权限路径不明时，先读取全局 Codex 指令链接的私有 `github-maintainer-context.md`。对其中同一账号
和精确目标仓已记录的正向能力直接复用，不在每个 PR 前查询 `viewerPermission`；能力失效、权限
拒绝和未知能力的重查遵循 `dev-workflow`。

所有面向 `jxxghp/*` 的 MoviePilot 贡献固定使用 `InfinityPacer/*` fork topic branch 和 Pull
Request，即使上游具有 `WRITE`。权限只决定门禁通过后能否显式 merge，不改变 fork-first 拓扑，
也不允许直接 push 默认分支或绕过 Ruleset。force push 只有维护者明确授权且影响范围已说明时才可
执行，不能从一般 push/PR 授权推断。

## 路由

- 面向 `jxxghp/*` 的主程序、前端、Rust、Wiki、资源、服务端、私有 MoviePilot 上游目标和官方
  插件贡献：读取 [references/upstream-pr.md](references/upstream-pr.md)。私有目标只从全局私有
  reference、当前 remote 和更近说明解析，不复制到本公开 skill。
- `InfinityPacer/MoviePilot-Plugins` 的个人插件 PR-only 或发版：读取
  [references/personal-plugin.md](references/personal-plugin.md)。
- 未列入支持范围的仓库不自动套用本 skill；用户只说“发布”而当前仓没有对应 release 流程时，
  先确认目标，不推断新的外部副作用。

## 公共文本与完成

PR 标题、正文和 issue/review 回复默认使用中文，commit subject 使用简洁英文 Conventional
Commit。应用 `dev-workflow` 的隐私与 PR 沟通契约；私有仓名和维护者 capability reference 只用于
内部判断，不写入无关公共文本。

多行 PR、issue 和 review/comment 正文使用 body file 或其他能保留真实换行的结构化输入，不发布
字面量 `\n`。每次创建或更新公共文本后回读实际 Markdown、链接和隐私。

来源 issue 仅在同仓问题会被完整解决时使用 `Fixes`；部分处理、背景关联或是否应关闭尚不确定时
使用 `Refs`，跨仓使用完整 URL。`Refs` 和完整 URL 不主动关闭 issue，除非维护者明确要求。发布
PR 后回读 issue 编号、仓库与关联语义。

当前任务明确来源于某个 issue 且已授权对应 PR 或 Release 交付时，该授权包含下述一次相关来源
issue 回复；无关 issue、review 或公共评论仍需单独授权。

默认在所选交付终态后回复一次；只有 PR 创建本身就是终态、流程阻塞、需要维护者操作或用户明确
要求时才先发“已提交 PR”的进度回复，并附 PR URL 与阻塞或待操作事项。合并或 Release 尚未完成
时不得写“已完成”、“已修复”或“已发布”。

按所选 reference 到达实际终态。不得把 push、PR 创建、Action 已触发或权限已知误报为完成。
