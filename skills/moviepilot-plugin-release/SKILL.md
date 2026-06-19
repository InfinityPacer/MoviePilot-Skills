---
name: moviepilot-plugin-release
description: Use when publishing, releasing, version-bumping, or preparing a release pull request for a v1 or v2 plugin in the InfinityPacer/MoviePilot-Plugins repository.
---

# MoviePilot 插件发版

## 核心原则

以插件仓源码、市场元数据和 GitHub Release 的实际结果形成闭环。不得把“本地改完”、
“PR 已创建”或“Action 已触发”当成发版完成。

只操作 `InfinityPacer/MoviePilot-Plugins`。发版统一走功能分支、PR Required Check、
Auto-merge 和 `main` Release workflow，不直接 push `main`。
普通维护、CI、文档或非版本发布 PR 不使用本 skill；先使用 `moviepilot-plugin-development`
确认任务类型和分支命名。

## 1. 确认范围

1. 运行 `git remote -v`，确认仓库是 `InfinityPacer/MoviePilot-Plugins`。
2. 运行 `git status --short --branch`，保留并避开用户已有改动。
3. v2 插件只修改 `plugins.v2/<plugin_id>/` 和 `package.v2.json`；除非用户明确要求，
   不修改 `plugins/`。
4. 运行 `git fetch origin main`，以 `origin/main` 作为发布基线。若当前不在 `main`，
   必须核对当前分支与 `origin/main` 的关系和提交范围：

   ```bash
   git merge-base --is-ancestor origin/main HEAD
   git log --oneline origin/main..HEAD
   git log --oneline HEAD..origin/main
   ```

   若分支不是基于最新 `origin/main`，或 `origin/main..HEAD` 包含旧版本发布、无关修复、
   其他插件改动等非本次发版提交，停止在原分支继续发版；从 `origin/main` 创建干净分支，
   仅 cherry-pick 或重做本次必要改动。不得为了“快速解决冲突”在旧发布分支上继续堆提交。
5. 从最新 `origin/main` 创建当前代理对应的发版协作分支。`release` 前缀只用于真实版本升级
   或 GitHub Release 闭环；普通维护、门禁、文档和 CI 修复按任务类型命名并转回开发或对应
   PR 流程。若目标分支名已存在且不能确认只包含本次发版提交，追加短后缀创建新分支，
   例如 `-clean` 或日期后缀：
   - Codex：`codex/release/<plugin>-<version>`
   - Claude Code：`claude/release/<plugin>-<version>`

## 2. 同步发布事实

按以下顺序核对，不要只搜索版本字符串：

1. 插件类的 `plugin_version`；
2. `package.json` 或 `package.v2.json` 对应条目的 `version`；
3. 对应 `history["v<version>"]` 的用户可读说明；
4. 若插件存在独立 README，其顶部“版本更新日志”必须有同版本、同语义条目；
5. 插件目录、package key、插件 ID 和 `plugin_version` 必须属于同一插件。

版本说明描述发布后的当前行为，不写 commit message 视角，不写源码行号或本机信息。

## 3. 启用本地门禁

先读取现有配置：

```bash
git config --get core.hooksPath
```

- 无输出：运行 `git config core.hooksPath .githooks`。
- 输出 `.githooks`：继续。
- 输出其他路径：停止并说明冲突，不得覆盖用户已有 Hook。

随后直接运行：

```bash
.githooks/pre-push
```

版本门禁不通过时先修复，不得使用 `--no-verify` 绕过。

## 4. 验证

使用工作区 `.venv-test`，插件仓测试必须显式指定后端：

```bash
env -u CONFIG_DIR MOVIEPILOT_BACKEND_PATH=<workspace>/MoviePilot \
  <workspace>/.venv-test/bin/python -m pytest tests/<v1|v2>/<plugin_id> -q
env -u CONFIG_DIR MOVIEPILOT_BACKEND_PATH=<workspace>/MoviePilot \
  <workspace>/.venv-test/bin/python tests/run.py -q
python .github/scripts/check_plugin_versions.py package.json package.v2.json
python -m json.tool package.v2.json >/dev/null
python -m compileall -q plugins.v2/<plugin_id>
git diff --check
```

`CONFIG_DIR` 不得从本地运行态环境泄漏进单测；外部服务必须 mock，全量测试不得真实出站。
任何失败都要修复或明确报告，不能带失败进入 PR。

## 5. 提交前确认

展示以下内容并取得维护者明确确认后，才能 commit 或 push：

- 分支名；
- 版本同步位置；
- 测试和门禁结果；
- `git diff --stat`；
- 拟用的单行英文 Conventional Commit subject。

确认一次可以覆盖紧接着执行的 commit 和 push；用户只确认 commit 时，不得推送。

## 6. 创建并自动合并 PR

commit、push 后，用真实换行的临时 Markdown 文件创建中文 PR：

创建 PR 前再次确认本地 `main` 信息已刷新，且 PR head 只包含本次发版提交：

```bash
git fetch origin main
git log --oneline origin/main..HEAD
git diff --name-only origin/main...HEAD
```

提交列表或文件列表出现旧版本发布、无关插件、无关仓库元数据时，停止创建 PR，改用干净
分支重做；不要依赖 GitHub 冲突提示后再补救。

```bash
gh pr create \
  --repo InfinityPacer/MoviePilot-Plugins \
  --base main \
  --head <branch> \
  --title "<中文标题>" \
  --body-file <body-file>
```

PR 必须包含变更说明、影响路径、验证结果和协作来源。纯 Codex 写
“本 PR 为 Codex 协作提交”，纯 Claude Code 写“本 PR 为 Claude Code 协作提交”；
两者都实际参与时写“本 PR 为 Claude Code & Codex 协作提交”。

Issue 关联按以下规则写入正文：

- 同仓 issue，修复已确认且 PR 合并后应自动关闭：`Fixes #<number>`；
- 同仓 issue，仅作背景、讨论或不应自动关闭：`Refs #<number>`；
- issue 与 PR 不在同一仓库：使用 issue 完整 URL，不依赖短编号；
- 无法确认是否应自动关闭时，默认使用 `Refs`，不得擅自关闭 issue。

回读 PR 正文确认渲染和隐私无误，并等待 `Plugin release gate` 至少出现一次。仓库首次
启用保护时，先创建要求该检查的 `main` Ruleset，再为 PR 启用 Auto-merge；不得在
Ruleset 生效前提前启用，否则 PR 可能在没有保护条件时直接合并。

回读 PR 时同时确认 issue 编号、所属仓库和 `Fixes` / `Refs` 语义正确。
回读 PR 时还必须确认 `baseRefName` 为 `main`、`headRefName` 为本次分支、提交列表和
changed files 与本次发版范围一致；不一致时关闭该 PR，创建干净分支后重新提 PR。

只对刚创建并核对过 URL/编号与 head SHA 的 PR 启用：

```bash
gh pr merge <pr-number> \
  --repo InfinityPacer/MoviePilot-Plugins \
  --auto --squash \
  --match-head-commit <head-sha>
```

不得扫描并批量启用其他 PR 的 Auto-merge，不得使用 `--admin` 绕过 Ruleset。默认保留本地和远程合并分支，除非维护者明确要求清理。

## 7. 回查发布

等待 PR 合并后依次确认：

1. PR 的 `mergedAt`、`mergeCommit` 和目标分支为 `main`；
2. `Plugin Release` workflow 对该 merge commit 成功；
3. tag 为 `<PluginId>_v<version>`；
4. Release 标题、说明和 zip 资产版本正确；
5. `main` 上 `package`、README 和 `plugin_version` 仍一致。

PR 合并并完成上述回查后，把远程 `main` 更新到本地 `main`，但不要清理刚合并的协作分支：

```bash
git fetch origin main
git checkout main
git pull --ff-only origin main
git status --short --branch
```

如果本地工作树不干净或切换 `main` 会覆盖用户改动，停止同步并说明阻塞原因；不要 stash、
reset 或删除分支来强行收尾。

若 workflow 失败，读取失败 step 和日志，修复后重新走分支 PR；不要直接改 `main`。

## 8. 回复来源 Issue

若改动来源于 issue，默认只在 PR 合并且 GitHub Release 成功后回复一次最终结果，避免
自动合并流程在短时间内连续发布“已提交 PR”和“已发布”两条近似评论。

只有出现以下任一情况时，才在 PR 创建后先回复进度：

- Required Check、合并或 Release 被阻塞，当前执行无法继续等待完成；
- 需要维护者操作、补充信息或做出决定；
- 用户明确要求在 PR 创建后立即同步。

进度评论必须明确写“已提交 PR”，附 PR URL，并说明当前阻塞或待确认事项；不得写
“已完成”“已修复”或宣称新版本已经发布。发布恢复后，再回复一次最终结果。

最终评论包含版本、PR URL、Release URL 与必要的验证结论。issue 与 PR 跨仓时写明
目标仓库并使用完整 URL，避免只贴短编号造成歧义。

使用真实换行的临时 Markdown 文件发布，并回读 issue 最后一条评论：

```bash
gh issue comment <issue-number> \
  --repo <issue-owner>/<issue-repo> \
  --body-file <body-file>
```

使用 `Fixes #<number>` 的同仓 issue 由合并自动关闭；使用 `Refs #<number>` 或完整
URL 关联时不主动关闭，除非维护者明确要求。每次发布评论后都要回读 issue，确认
Markdown、链接和公开信息无误。

## 常见错误

| 错误 | 处理 |
| --- | --- |
| 只改 package 版本 | 同步 `plugin_version`，有独立 README 时同步版本日志 |
| Required Check 一直缺失 | PR workflow 不得使用 `paths` 过滤 |
| 本地 Hook 没执行 | 检查 `core.hooksPath`，不要覆盖已有自定义路径 |
| PR 检查通过就宣称发布完成 | 继续回查合并、Release workflow、tag 和资产 |
| PR 合并后本地仍停在旧分支或旧 main | 快进本地 `main` 到 `origin/main`，保留合并分支不清理 |
| 自动合并流程中连续回复两次 issue | 正常情况下等待 Release 完成后只回复一次；仅在流程阻塞或需用户介入时先发进度评论 |
| 旧发布分支带入历史提交导致 PR 冲突 | 从最新 `origin/main` 创建干净分支，只带本次发版提交 |
| 为所有 PR 开启 Auto-merge | 只操作本次 skill 创建并核对过 head SHA 的 PR |
| 为赶发版使用 `--admin` 或 `--no-verify` | 修复门禁失败原因，不绕过保护 |
