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
等事实；本 skill 不复制这些内容。执行前读取适用说明，确认当前仓库、目标文件和工作树。只有任务
需要识别权威基线、交付路由或处理已知基线漂移时才检查 remote；需要识别时按 URL 与仓库身份
判断角色，不按 `origin`、`upstream` 或 `fork` 等本地名称猜测。

## 开发边界

- 普通本地开发从当前 checkout、任务文件和工作树开始，不因本 skill 被调用就检查 remote、刷新
  base、计算 merge-base 或探测运行态。
- 只有任务涉及实例行为、现场诊断或实验室复现时，才按工作区规则确认问题主体并使用对应证据；
  纯源码、测试、文档和静态配置改动不把本机服务状态当作独立前置检查。
- 已知会进入评审时按 `product-development` 选择业务 topic branch。只有权威 base 是否漂移会影响当前实现
  或交付准备时，才按 remote URL 刷新 base，并核对 merge-base、base 到 HEAD 的提交范围和分支
  主题；不满足时保留有效工作并迁移。跨仓改动分别建立分支、提交和验证。
- 只有任务需要运行态诊断或验收、静态证据不足，或者端口/进程冲突影响当前下一步时，才探测并
  复用现有服务；现有运行态不是普通开发的独立证据门。
- 组合根、canonical package ownership 和依赖装配是任务相关的架构不变量。仅在改动触及模块归属、
  import 边界、依赖注入、启动或关闭生命周期时检查对应规则和架构测试，不对普通局部改动另做
  所有权审计。
- 保留当前任务改动；不混入、reset、stash 或覆盖无关改动。只有无法安全隔离时才使用用户授权的
  worktree 或询问必要问题。
- 按受影响路径和更近规则选择最小可信验证；不在 skill 中固化易漂移的命令副本。
- 本地 commit 服从 `product-development`、已批准计划或当前授权。本 skill 不 push、不创建 PR、不 merge、
  不发版。

## 完成

说明仓库与分支、改动范围、实际验证、未验证原因类别和工作树状态。需要外部交付时继续使用
`moviepilot-delivery`，不得把本地开发完成误报为 PR 或发布完成。
