# 上游 Fork PR

## 适用边界

用于从 `InfinityPacer/*` fork 向对应 `jxxghp/*` MoviePilot 仓库提交 PR，包括官方插件 fork。
个人插件仓不使用本流程。目标仓、fork 和 base 以 remote URL、上游默认分支、工作区或更近仓库
说明为准，不凭惯例猜测私有或新目标。

## 准备与验证

- 确认 topic branch 基于最新上游 base，且 base 到 HEAD 只包含本次交付提交。
- 复用仍有效的开发验证；按目标仓说明、改动风险和已记录的维护者安排补齐适用检查，不复制固定
  命令清单。本地 anchor 与可合并状态分别报告，保存版本不代表验证完成。
- 本地 commit 使用单行英文 Conventional Commit subject。push/PR 已获授权后，只把 topic branch
  推到对应 fork；不直接 push 上游或默认分支。
- PR base 指向 `jxxghp/*` 上游，head 指向 `InfinityPacer/*` fork 分支。使用真实换行的 body file，
  并在创建后回读 URL、标题、正文、base、head、head SHA、changed files、checks 和 reviews。
- 跨仓联动分别创建 PR，并相互链接，说明兼容关系与必要合并顺序。
- 官方插件贡献使用上游 PR 路径，不进入个人插件发布流程；按目标仓当前说明和 workflow 完成适用门禁。

## 跟踪与合并

PR 创建不是默认终态。先回读 active Ruleset、branch protection、required checks/reviews、当前 head SHA
和 mergeability。只等待平台真正要求，或结果可能实质改变当前 PR 合并判断的 checks/review。

已证实与当前改动无关且未被其加重或重新触达的 base/上游既有问题、无关自动化/基础设施/配额故障，
或错误、不可达、低价值的 Review 反馈，按入口的维护者决定及证据记录处置；同一范围已获预授权时
不修复、不等待，也无需再次询问维护者；本轮已有 merge 授权且平台允许正常 merge 时继续交付。
平台允许正常 merge 且当前 HEAD 没有本次改动造成的未解决实质问题时，通过 GitHub PR 显式 merge，
并用 head SHA 防止合并陈旧版本。不要启用 Auto-merge，不用 `--admin` 绕过保护。若正常 merge 返回
明确权限拒绝，使该能力事实失效并查询一次；不要改成直接 push 上游。

复用工作区已确认的 PR 含 merge 授权。只有明确要求 PR 创建后停止、等待其他维护者，或更近规则
保留最终处置权且尚未授权时，PR 创建并回读才是终态。合并后回读 merged commit；工作树允许时再
fast-forward 本地 base，不 stash、reset 或覆盖用户改动来强行同步。

来源 issue 的最终回复附 PR URL、合并状态或 merge commit 与必要验证；进度和最终措辞遵循入口的
共同行为，避免同一正常交付连续回复两次。
