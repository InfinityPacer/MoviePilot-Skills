---
name: moviepilot-plugin-delivery
description: Use when preparing, publishing, updating, or checking personal MoviePilot plugin pull requests, PR-only changes, version bumps, or releases in the InfinityPacer/MoviePilot-Plugins repository.
---

# MoviePilot 插件交付

## 核心原则

只操作 `InfinityPacer/MoviePilot-Plugins`。个人插件仓所有 commit、push、PR、Auto-merge、
PR-only 和发版闭环都走本 skill；不得直接 push `main`。

按任务选择终态：

| 任务 | 终态 |
| --- | --- |
| PR-only：普通维护、CI、文档或非版本发布 PR 使用本 skill 的 PR-only 路径 | PR、`Plugin release gate`、Auto-merge、本地 `main` 同步、按需回复 issue；不做版本升级、tag、GitHub Release 或发布回查 |
| 发版路径：发布插件、版本升级、更新 package/history/README 版本事实 | PR、`Plugin release gate`、Auto-merge、`Plugin Release` workflow、tag/Release 元数据回读、最终回复 issue |

不得把“本地改完”“PR 已创建”“Action 已触发”当成交付完成；必须到达所选终态。

## 1. 确认范围

运行：

```bash
git remote -v
git status --short --branch
git fetch origin main
git merge-base --is-ancestor origin/main HEAD
git log --oneline origin/main..HEAD
git log --oneline HEAD..origin/main
```

确认仓库为 `InfinityPacer/MoviePilot-Plugins`。若分支不是基于最新 `origin/main`，或
`origin/main..HEAD` 包含旧版本发布、无关修复、其他插件改动等非本次交付提交，停止在原分支
继续；从 `origin/main` 创建干净分支，仅 cherry-pick 或重做本次必要改动。

分支名必须先跟随本次交付的业务主题，而不是交付动作。当前已在工作分支时，先判断分支是否
干净、基于最新 `origin/main`、提交范围只包含本次改动，且分支名能表达业务主题；满足这些条件
就继续使用当前分支，不要仅因为进入发版闭环而改名。只有当前在 `main`/`master`、分支主题与
本次交付业务不一致、或提交范围不干净时，才从 `origin/main` 新建业务分支。

新建分支按任务类型和业务主题命名，例如：

```bash
TASK_TYPE=fix
PLUGIN_ID=subscribeassistantenhanced
BRANCH="codex/${TASK_TYPE}/${PLUGIN_ID}-topic"
git checkout -b "${BRANCH}" origin/main
```

Claude Code 对应使用 `claude/${TASK_TYPE}/${PLUGIN_ID}-topic`。

只有发布流程本身就是业务主题时，才使用 `release` 前缀；不要把普通 bugfix、docs、test 或
CI 修复分支仅因最后要发版而改成 `release`：

```bash
PLUGIN_ID=subscribeassistantenhanced
VERSION=0.3.0
BRANCH="codex/release/${PLUGIN_ID}-${VERSION}"
git checkout -b "${BRANCH}" origin/main
```

Claude Code 对应使用 `claude/release/${PLUGIN_ID}-${VERSION}`。若目标分支名已存在且不能确认
只包含本次交付提交，追加短后缀创建新分支，例如 `-clean` 或日期后缀。

## 2. 发版事实

仅发版路径需要同步发布事实。PR-only 路径不得为了“看起来完整”改版本。

发版路径按以下顺序核对，不要只搜索版本字符串：

1. 插件类的 `plugin_version`；
2. `package.json`、`package.v2.json` 或 `package.v3.json` 对应条目的 `version`；
3. 对应 `history["v版本"]` 的用户可读说明；
4. 若插件存在独立 README，其顶部“版本更新日志”必须有同版本、同语义条目；
5. 插件目录、package key、插件 ID 和 `plugin_version` 必须属于同一插件。

版本说明描述发布后的当前行为，不写 commit message 视角，不写源码行号或本机信息。

## 3. 本地门禁

先读取现有配置：

```bash
git config --get core.hooksPath
```

- 无输出：运行 `git config core.hooksPath .githooks`。
- 输出 `.githooks`：继续。
- 输出其他路径：停止并说明冲突，不得覆盖用户已有 Hook。

随后运行：

```bash
.githooks/pre-push
```

版本门禁不通过时先修复，不得使用 `--no-verify` 绕过。不要重复跑同一版本门禁：
`.githooks/pre-push` 已覆盖的版本一致性检查不再机械重复；若 hook 不可用，或 hook 后又修改
版本、package、history、README，再运行：

```bash
python .github/scripts/check_plugin_versions.py package.json package.v2.json package.v3.json
```

## 4. 验证

使用工作区 `.venv-test`。插件测试通过工作区 env-file 注入 `MOVIEPILOT_BACKEND_PATH` 等
运行所需变量，同时清理真实 `CONFIG_DIR`。`<workspace>/app.env` 是本机命令 env-file；命令中
使用 `WORKSPACE` 指向工作区根时，通过 source 工作区 env-file 注入变量。不得读取、打印、提交或
写进公开正文，不要把 env-file 内容拼进命令参数。

按场景选择：

| 场景 | 命令 |
| --- | --- |
| 局部插件测试：改动集中在单个插件，且需要快速复现或回归该插件行为 | `pytest tests/<v1\|v2\|v3>/<plugin_id> -q` |
| A 档覆盖率门禁：目标插件属于 `plugin_quality.json` A 档，或改动触及覆盖率门禁脚本/配置 | `scripts/plugin_coverage.py --base-ref ${BASE_REF}` |
| 全量回归：跨插件共享脚手架、测试基础设施、跨代兼容索引、多插件公共行为、局部结果不足，或 PR CI 无法可靠运行 | `tests/run.py -q` |
| 新增插件目录：PR 新增 `plugins/`、`plugins.v2/` 或 `plugins.v3/` 插件目录 | `scripts/check_new_plugin_tests.py --base-ref origin/main` |
| 基础文件检查：版本、索引、README、JSON、编译或空白敏感改动 | 版本门禁、`json.tool`、`compileall`、`git diff --check` |

常用变量：

```bash
WORKSPACE="${WORKSPACE:?set workspace root}"
BASE_REF=origin/main
PLUGIN_KIND=v3
PLUGIN_ID="${PLUGIN_ID:?set plugin id}"
TEST_TARGET="tests/${PLUGIN_KIND}/${PLUGIN_ID}"
PLUGIN_DIR="plugins.${PLUGIN_KIND}/${PLUGIN_ID}"
if [ "${PLUGIN_KIND}" = "v1" ]; then
  PLUGIN_DIR="plugins/${PLUGIN_ID}"
fi
```

局部插件测试：

```bash
(
  set -a
  . "${WORKSPACE}/app.env"
  set +a
  env -u CONFIG_DIR \
    "${WORKSPACE}/.venv-test/bin/python" -m pytest "${TEST_TARGET}" -q
)
```

A 档覆盖率门禁：

```bash
(
  set -a
  . "${WORKSPACE}/app.env"
  set +a
  env -u CONFIG_DIR \
    "${WORKSPACE}/.venv-test/bin/python" scripts/plugin_coverage.py --base-ref ${BASE_REF}
)
```

全量回归：

```bash
(
  set -a
  . "${WORKSPACE}/app.env"
  set +a
  env -u CONFIG_DIR \
    "${WORKSPACE}/.venv-test/bin/python" tests/run.py -q
)
```

基础文件检查：

```bash
python -m json.tool package.json >/dev/null
python -m json.tool package.v2.json >/dev/null
python -m json.tool package.v3.json >/dev/null
python -m compileall -q "${PLUGIN_DIR}"
git diff --check
```

新增插件目录检查仅在 PR 新增插件目录时运行：

```bash
python scripts/check_new_plugin_tests.py --base-ref origin/main
```

`CONFIG_DIR` 不得从本地运行态环境泄漏进单测；外部服务必须 mock，全量测试不得真实出站。
`scripts/plugin_coverage.py` 会运行 `plugin_quality.json` 中 A 档插件的测试并检查覆盖率；它可替代
这些插件的局部 pytest 重跑，但不能替代 `tests/ci`、非 A 档插件测试或需要全量回归的
`tests/run.py`。个人插件仓的 A 档覆盖率由 `plugin_quality.json` 显式声明；新增插件只先进入最低测试目录门禁，
不自动进入 A 档覆盖率门禁。

普通 PR 和发版 PR 的完整 Python 回归由 `Plugin test gate` CI 执行；本地默认保留受影响插件测试、
A 档覆盖率和版本、JSON、compile 等受影响门禁。共享边界或上述全量触发条件变化时再本地运行
`tests/run.py`。任何失败都要修复或明确报告，不能把局部结果冒充全量。验证证据仅在相关源码、
后端基线、依赖、测试脚手架或环境边界发生实质变化时失效；普通新 commit 或非重叠 rebase 不触发
机械全量，PR 更新后的 CI 负责重新运行完整门禁。

## 5. 提交与授权

commit、push 前核对：

- 分支名和交付路径：PR-only 或发版路径；
- 版本同步位置，PR-only 写明未改版本；
- 测试和门禁结果；
- `git diff --stat`；
- 拟用的单行英文 Conventional Commit subject。

本地 commit 服从当前 `dev-workflow`、已批准计划或本轮用户授权；已有授权时直接执行，不重复确认。
push、PR、Auto-merge 和 release 是独立的外部交付边界，只有当前指令或既有授权已覆盖时才能执行；
只授权 commit 时不得推送。

## 6. 创建并自动合并 PR

创建 PR 前再次确认本地 `main` 信息已刷新，且 PR head 只包含本次交付提交：

```bash
git fetch origin main
git log --oneline origin/main..HEAD
git diff --name-only origin/main...HEAD
```

提交列表或文件列表出现旧版本发布、无关插件、无关仓库元数据时，停止创建 PR，改用干净分支重做。

push/PR 已获授权后，先推送当前已核对分支，再使用真实换行的临时 Markdown 文件创建 PR：

```bash
BRANCH="$(git branch --show-current)"
PR_TITLE="fix(plugin): 修复插件行为"
BODY_FILE="/tmp/moviepilot-plugin-pr.md"
git push -u origin "${BRANCH}"
gh pr create \
  --repo InfinityPacer/MoviePilot-Plugins \
  --base main \
  --head "${BRANCH}" \
  --title "${PR_TITLE}" \
  --body-file "${BODY_FILE}"
```

PR 标题、正文和 issue 回复默认使用中文，commit subject 使用英文 Conventional Commit；仓库模板
或维护者另有要求时从其要求。同时应用 `dev-workflow` 的通用 PR 沟通与隐私契约，本 skill 不复制
固定章节模板。正文深度随改动风险调整，标题必须描述主要行为或维护结果，不能用测试或实现手段
掩盖生产行为变化，也不要重复自动生成的 PR 摘要。

MoviePilot 专项内容只补充个人插件仓、门禁、Auto-merge 与 release 终态。PR-only 不得声称已做
版本升级、tag 或 GitHub Release；无需为了模板主动列出这些“未做事项”，除非现有上下文会产生
交付路径歧义。发版路径正文应列出实际版本事实同步位置。Issue 仅在修复完整且合并后应自动关闭时
使用 `Fixes`；部分处理或背景关联使用 `Refs`，跨仓使用完整 URL。

回读 PR 正文确认其与改动规模匹配、无需本地讨论即可理解主要问题、行为变化、必要边界和验证结果，
并检查隐私后等待 `Plugin release gate` 至少出现一次。若 Required Check
或 Ruleset 缺失，将其作为仓库治理阻塞报告；常规交付中不要创建或修改 Ruleset，除非维护者明确
把仓库治理作为本次任务。

```bash
PR_NUMBER=123
gh pr view "${PR_NUMBER}" \
  --repo InfinityPacer/MoviePilot-Plugins \
  --json url,title,body,baseRefName,headRefName,headRefOid,state,mergeStateStatus,statusCheckRollup,reviews,files
```

回读 PR 时同时确认 issue 编号、所属仓库和 `Fixes` / `Refs` 语义正确，并确认 `baseRefName`
为 `main`、`headRefName` 为本次分支、head SHA 和 changed files 与本次交付范围一致。

只对刚创建并核对过 URL、编号与 head SHA 的 PR 启用：

```bash
PR_NUMBER=123
HEAD_SHA="$(git rev-parse HEAD)"
gh pr merge "${PR_NUMBER}" \
  --repo InfinityPacer/MoviePilot-Plugins \
  --auto --squash \
  --match-head-commit "${HEAD_SHA}"
```

不得扫描并批量启用其他 PR 的 Auto-merge，不得使用 `--admin` 绕过 Ruleset。默认保留本地和远程合并分支，
除非维护者明确要求清理。

## 7. 终态回查

PR 合并后，两条路径都要确认：

```bash
git fetch origin main
git checkout main
git pull --ff-only origin main
git status --short --branch
```

如果本地工作树不干净或切换 `main` 会覆盖用户改动，停止同步并说明阻塞原因；不要 stash、
reset 或删除分支来强行收尾。

PR-only 路径到这里结束：确认 PR 的 `mergedAt`、`mergeCommit`、目标分支为 `main`，本地 `main`
已快进到 `origin/main`；不做版本升级、tag、GitHub Release 或发布回查。

发版路径继续等待并确认：

1. `Plugin Release` workflow 对该 merge commit 成功；
2. tag 为 `PluginId_v版本`，且指向该 merge commit；
3. GitHub Release 的标题、说明和唯一 ZIP 资产元数据正确，默认不下载 ZIP；
4. `main` 上 package、README 和 `plugin_version` 仍一致。

若 workflow 失败，读取失败 step 和日志，修复后重新走分支 PR；不要直接改 `main`。

## 8. 回复来源 Issue

若改动来源于 issue，按终态回复：

- PR-only 路径：PR 合并后回复最终结果，附 PR URL、merge commit 或合并状态、必要验证结论；
- 发版路径：默认只在 PR 合并且 GitHub Release 成功后回复一次最终结果，附版本、PR URL、
  Release URL 与必要验证结论。

只有出现以下任一情况时，才在 PR 创建后先回复进度：

- Required Check、合并或 Release 被阻塞，当前执行无法继续等待完成；
- 需要维护者操作、补充信息或做出决定；
- 用户明确要求在 PR 创建后立即同步。

进度评论必须明确写“已提交 PR”，附 PR URL，并说明当前阻塞或待确认事项；不得写“已完成”
“已修复”或宣称新版本已经发布。发布恢复后，再回复一次最终结果。

issue 与 PR 跨仓时写明目标仓库并使用完整 URL，避免只贴短编号造成歧义。使用真实换行的临时
Markdown 文件发布，并回读 issue 最后一条评论：

```bash
ISSUE_NUMBER=123
ISSUE_REPO="InfinityPacer/MoviePilot-Plugins"
BODY_FILE="/tmp/moviepilot-plugin-issue-comment.md"
gh issue comment "${ISSUE_NUMBER}" \
  --repo "${ISSUE_REPO}" \
  --body-file "${BODY_FILE}"
```

使用 `Fixes #<number>` 的同仓 issue 由合并自动关闭；使用 `Refs #<number>` 或完整 URL
关联时不主动关闭，除非维护者明确要求。每次发布评论后都要回读 issue，确认 Markdown、链接
和公开信息无误。

## 常见错误

| 错误 | 处理 |
| --- | --- |
| 把 PR-only 当发版继续做 tag 或 Release 回查 | 停在已合并 PR、本地 main 同步和必要 issue 回复 |
| 只改 package 版本 | 发版路径同步 `plugin_version`，有独立 README 时同步版本日志 |
| Required Check 一直缺失 | 报告 Ruleset 或检查缺失为阻塞，不在常规交付里擅自改仓库治理 |
| PR 检查通过就宣称发布完成 | PR-only 等合并；发版路径继续回查 Release workflow、tag 和资产 |
| PR 合并后本地仍停在旧分支或旧 main | 快进本地 `main` 到 `origin/main`，保留合并分支不清理 |
| 自动合并流程中连续回复两次 issue | 正常情况下等待终态后只回复一次；仅在流程阻塞或需用户介入时先发进度评论 |
| 旧发布分支带入历史提交导致 PR 冲突 | 从最新 `origin/main` 创建干净分支，只带本次交付提交 |
| 为所有 PR 开启 Auto-merge | 只操作本次 skill 创建并核对过 head SHA 的 PR |
| 为赶发版使用 `--admin` 或 `--no-verify` | 修复门禁失败原因，不绕过保护 |
