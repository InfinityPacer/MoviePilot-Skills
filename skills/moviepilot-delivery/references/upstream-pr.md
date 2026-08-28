# 上游 Fork PR

## 适用边界

用于从 `InfinityPacer/*` fork 向对应 `jxxghp/*` MoviePilot 仓库提交 PR，包括官方插件 fork。
个人插件仓不使用本流程。目标仓、fork 和 base 以 remote URL、上游默认分支、工作区或更近仓库
说明为准，不凭惯例猜测私有或新目标。

## 准备与验证

- 确认 topic branch 基于最新上游 base，且 base 到 HEAD 只包含本次交付提交。
- 复用仍有效的开发验证；按目标仓说明和改动风险补齐缺失门禁，不复制另一套固定命令清单。
- 本地 commit 使用单行英文 Conventional Commit subject。push/PR 已获授权后，只把 topic branch
  推到对应 fork；不直接 push 上游或默认分支。
- PR base 指向 `jxxghp/*` 上游，head 指向 `InfinityPacer/*` fork 分支。使用真实换行的 body file，
  并在创建后回读 URL、标题、正文、base、head、head SHA、changed files、checks 和 reviews。
- 跨仓联动分别创建 PR，并相互链接，说明兼容关系与必要合并顺序。
- 官方插件贡献使用上游 PR 路径，不进入个人插件发布流程；按目标仓当前说明和 workflow 完成适用门禁。

## 跟踪与合并

PR 创建不是默认终态。跟踪 required checks、review 和 mergeability；pending 或 failed checks、required
review、冲突和 merge method 限制是交付状态，不是权限事实失效。

门禁满足后，本轮授权允许合并且全局维护者 reference 已记录该账号对精确目标具有正向能力时，
通过 GitHub PR 显式 merge，并用 head SHA 防止合并陈旧版本。不要启用 Auto-merge，不用 `--admin`
绕过保护。若正常 merge 返回明确权限拒绝，使该能力事实失效并查询一次；不要改成直接 push 上游。

只有本轮明确要求 PR 创建后停止、等待其他维护者，或更近规则保留最终处置权时，PR 创建并回读才是
终态。合并后回读 merged commit；工作树允许时再 fast-forward 本地 base，不 stash、reset 或覆盖用户
改动来强行同步。

来源 issue 的最终回复附 PR URL、合并状态或 merge commit 与必要验证；进度和最终措辞遵循入口的
共同行为，避免同一正常交付连续回复两次。
