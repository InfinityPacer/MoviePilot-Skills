# 个人插件交付

## 适用边界

只操作 `InfinityPacer/MoviePilot-Plugins`，不得直接 push `main`。先区分终态：

| 路径 | 终态 |
| --- | --- |
| PR-only | PR 门禁通过并合并，本地 `main` 在工作树允许时同步；不升级版本，不创建 tag 或 Release |
| 发版 | PR 合并后，当前发布 workflow、预期 tag、GitHub Release 和发布资产均回读正确 |

普通维护、CI、文档或未要求发布的改动走 PR-only；明确发布、版本升级或同步发布事实才走发版。

## 分支、事实与验证

- topic branch 基于按 remote URL 识别的自有仓最新默认分支，只包含本次业务改动；分支名表达业务
  主题，不因最终发版机械改成 `release`。只有发布流程本身就是主题时才使用 release 前缀。
- 发版时按目标仓当前版本门禁保持源码版本、市场 metadata 和发布说明一致；PR-only 不改版本。
- 遵循目标仓当前 hook、测试、版本和发布门禁，复用同一 HEAD 上仍有效的结果；不覆盖用户自定义
  hook，不绕过门禁。Required Check 未出现时作为治理阻塞报告，不在普通交付中创建或修改 Ruleset，
  除非当前任务明确包含仓库治理。
- PR 正文说明实际路径与验证。创建后回读 base、head SHA、changed files、checks、reviews 和 issue
  关联，避免旧发布提交或其他插件改动混入；发版正文列出实际版本事实同步位置。

## 合并与发布

当前授权覆盖 merge 时，先回读默认分支的 active Ruleset、仓库 merge/Auto-merge 设置和当前 PR head
SHA，只对本次已核对 PR 使用 Ruleset 允许的 merge 方法；检查尚未完成且 Auto-merge 可用时，优先
使用带 head SHA 约束的 Auto-merge。不得扫描其他 PR，不用 `--admin`，不绕过保护，默认不删除
本地或远程分支。

PR-only 在 merged commit 和目标 `main` 回读正确后结束。发版继续确认：

1. 当前发布 workflow 对该 merged commit 成功；
2. 预期 tag 指向该 merged commit；
3. Release 与发布资产的标题、说明、名称和版本等 metadata 符合当前 workflow，默认不下载资产；
4. 默认分支上的发布事实保持一致。

workflow 失败时从新的 topic branch 修复并走 PR，不直接修改 `main`。来源 issue 默认在所选终态后
回复一次：PR-only 附 PR URL、合并状态或 merge commit，发版附版本、PR URL 和 Release URL；
进度和最终措辞遵循入口的共同行为。
