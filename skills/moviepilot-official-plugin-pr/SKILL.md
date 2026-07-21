---
name: moviepilot-official-plugin-pr
description: Use when preparing, publishing, updating, or checking a pull request from the InfinityPacer MoviePilot-Plugins-Official fork to jxxghp/MoviePilot-Plugins main.
---

# MoviePilot 官方插件 PR

## 核心原则

只处理 `MoviePilot-Plugins-Official` fork。工作分支推到 `InfinityPacer/MoviePilot-Plugins-Official`，
PR 提交到 `jxxghp/MoviePilot-Plugins:main`。上游维护者拥有最终合并权；不得启用 Auto-merge，
不得执行个人插件仓发布流程。

## 1. 确认仓库与分支

运行：

```bash
git status --short --branch
git remote -v
git fetch upstream main
```

只接受以下映射：

| 本地仓库 | fork push 目标 | upstream PR 目标 |
| --- | --- | --- |
| `MoviePilot-Plugins-Official` | `InfinityPacer/MoviePilot-Plugins-Official` | `jxxghp/MoviePilot-Plugins:main` |

若当前是 `main` 或 `master`，从最新 `upstream/main` 创建协作分支：

- Codex：`codex/<type>/<topic>`
- Claude Code：`claude/<type>/<topic>`

已有工作分支必须先核对 merge-base、`upstream/main..HEAD` 和用户改动，不得 reset、stash 或
覆盖用户已有改动。

## 2. 验证改动

插件测试通过 `<workspace>/app.env` 注入 `MOVIEPILOT_BACKEND_PATH` 等运行所需变量，同时清理真实
`CONFIG_DIR`。按场景选择命令：

| 场景 | 命令 |
| --- | --- |
| 局部插件测试：改动集中在单个插件，且需要快速复现或回归该插件行为 | `pytest tests/<v1\|v2>/<plugin_id> -q` |
| 全量回归：准备提交官方仓 PR、跨插件共享脚手架变更、测试基础设施变更、或局部结果不足以覆盖风险 | `tests/run.py` |
| 新增插件目录：PR 新增 `plugins/` 或 `plugins.v2/` 插件目录 | 若仓库存在脚本，运行 `scripts/check_new_plugin_tests.py --base-ref upstream/main`；否则确认对应 `tests/<v1\|v2>/<plugin_id>/test_*.py` 已存在并运行局部/全量测试 |
| 基础文件检查：索引、metadata、版本、JSON、编译或空白敏感改动 | 版本门禁、`json.tool`、`compileall`、`git diff --check` |

常用命令：

```bash
WORKSPACE="${WORKSPACE:?set workspace root}"
PLUGIN_KIND=v2
PLUGIN_ID="${PLUGIN_ID:?set plugin id}"
TEST_TARGET="tests/${PLUGIN_KIND}/${PLUGIN_ID}"
PLUGIN_DIR="plugins.${PLUGIN_KIND}/${PLUGIN_ID}"
if [ "${PLUGIN_KIND}" = "v1" ]; then
  PLUGIN_DIR="plugins/${PLUGIN_ID}"
fi
```

```bash
(
  set -a
  . "${WORKSPACE}/app.env"
  set +a
  env -u CONFIG_DIR \
    "${WORKSPACE}/.venv-test/bin/python" -m pytest "${TEST_TARGET}" -q
)
(
  set -a
  . "${WORKSPACE}/app.env"
  set +a
  env -u CONFIG_DIR \
    "${WORKSPACE}/.venv-test/bin/python" tests/run.py
)
python .github/scripts/check_plugin_versions.py package.json package.v2.json
python -m json.tool package.json >/dev/null
python -m json.tool package.v2.json >/dev/null
python -m compileall -q "${PLUGIN_DIR}"
git diff --check
```

仓库存在新增插件目录门禁脚本时运行：

```bash
python scripts/check_new_plugin_tests.py --base-ref upstream/main
```

`<workspace>/app.env` 是本机命令 env-file；不得读取、打印、提交或写进公开正文，不要把 env-file 内容拼进命令参数。
若仓库不存在某个脚本，记录缺失边界并使用同场景的测试目录检查、局部测试或全量测试兜底。
若仓库存在 `Plugin release gate` 或同等 PR 检查，本地必须先跑对应脚本。外部服务必须 mock；
不能用个人插件仓 Release 验证替代官方仓 PR 验证。

## 3. 提交前确认

commit、push 前向维护者展示：

- 仓库和分支名；
- `upstream/main` 同步状态；
- 验证结果及未验证项；
- `git diff --stat`；
- 拟用的单行英文 Conventional Commit subject。

取得明确确认后才能 commit 或 push。只确认 commit 时不得 push；不得 force push，除非维护者
明确授权并已说明影响范围。

## 4. Push 与创建 PR

将协作分支推到 fork 的 `origin`。维护者确认 push 后，先推送当前已核对分支，再使用真实换行的
Markdown 文件创建中文 PR：

```bash
BRANCH="$(git branch --show-current)"
PR_TITLE="fix(plugin): update official plugin"
BODY_FILE="/tmp/moviepilot-official-plugin-pr.md"
git push -u origin "${BRANCH}"
gh pr create \
  --repo jxxghp/MoviePilot-Plugins \
  --base main \
  --head "InfinityPacer:${BRANCH}" \
  --title "${PR_TITLE}" \
  --body-file "${BODY_FILE}"
```

PR 正文必须为维护者提供判断改动是否成立所需的上下文，不能只列文件或实现动作。除确实不适用的
章节外，按以下顺序使用中文 Markdown 标题：

1. `## 问题与背景`：说明用户可感知的问题、预期与实际行为，或非缺陷类改动的维护目标；
2. `## 原因分析`：说明已确认的直接原因、触发条件和边界；原因尚未完全确认时明确证据与未知项，
   不把推测写成事实；
3. `## 解决方案`：说明改了什么以及为什么选择该方案；存在有意义的替代方案或兼容取舍时简述
   未采用原因；
4. `## 影响与风险`：说明受影响路径、用户行为、兼容性、配置/数据迁移要求和剩余风险；经核实无
   特殊迁移或兼容影响时也要明确写出结论；
5. `## 验证`：列出可复现命令或结果摘要，并如实写明未验证项及原因类别；
6. `## 关联`：列出 issue、联动 PR、合并顺序或兼容关系；没有关联项时可省略。

纯文档、工作流或机械维护可以把“问题与背景”和“原因分析”合并为 `## 背景与目标`，但仍须说明
为什么需要改、为什么采用当前方案、影响边界和验证结果，不能退化为 diff 摘要或本地执行流水账。
正文只能使用仓库相对路径、可复现命令或结果摘要，不得包含本机绝对路径、账号目录、临时文件、
凭据、Cookie、token、私有日志或本地端口映射。

Issue 关联按以下规则写入正文：

- 同仓 issue，修复已确认且 PR 合并后应自动关闭：`Fixes #<number>`；
- 同仓 issue，仅作背景、讨论或不应自动关闭：`Refs #<number>`；
- issue 与 PR 不在同一仓库：使用 issue 完整 URL，不依赖短编号；
- 无法确认是否应自动关闭时，默认使用 `Refs`，不得擅自关闭 issue。

## 5. 回读与跟踪

创建或更新 PR 后回读。回读 PR 时确认：

```bash
PR_NUMBER=123
gh pr view "${PR_NUMBER}" \
  --repo jxxghp/MoviePilot-Plugins \
  --json url,title,body,baseRefName,headRefName,headRefOid,state,mergeStateStatus,statusCheckRollup,reviews
```

1. base 为 `main`，head 为 `InfinityPacer:<branch>`；
2. 正文真实分段，包含问题或目标、方案理由、影响与风险、验证结果，且没有隐私信息；
3. issue 编号、仓库和 `Fixes` / `Refs` 语义正确；
4. CI 或 `Plugin release gate` 已出现，并区分等待、失败和成功；
5. review 或 requested changes 已如实报告；
6. 后续 push 后 head SHA 与 PR 一致。

不得启用 Auto-merge，不得代替上游维护者合并，不得运行个人仓自动合并或发布回查步骤。
用户只要求提交 PR 时，默认交付终态是 PR 创建并回读确认；若用户要求跟进 CI/review/合并，
或上游已实际合并，则继续到对应结果明确为止。

## 6. 回复来源 Issue

若改动来源于 issue，PR 创建后回复 issue：

- 明确写“已提交 PR”，附 PR URL，并简述改动和验证结果；
- PR 尚未合并时不得写“已完成”“已修复”或承诺已进入正式版本；
- issue 与 PR 跨仓时，同时写明目标仓库，避免只贴短编号造成歧义。

默认交付终态是 PR 已创建并回读确认；只有用户要求跟进或 PR 已实际合并时，才回写最终结果。

使用真实换行的临时 Markdown 文件发布，并回读 issue 最后一条评论：

```bash
ISSUE_NUMBER=123
ISSUE_REPO="jxxghp/MoviePilot-Plugins"
BODY_FILE="/tmp/moviepilot-official-plugin-issue-comment.md"
gh issue comment "${ISSUE_NUMBER}" \
  --repo "${ISSUE_REPO}" \
  --body-file "${BODY_FILE}"
```

使用 `Fixes #<number>` 的同仓 issue 由合并自动关闭；使用 `Refs #<number>` 或完整 URL
关联时不主动关闭，除非维护者明确要求。每次发布评论后都要回读 issue，确认 Markdown、
链接和公开信息无误。

## 常见错误

| 错误 | 处理 |
| --- | --- |
| 从陈旧本地 `main` 建分支 | 先 fetch，并以 `upstream/main` 为基线 |
| 将分支推到 upstream | 只 push `origin`，PR head 使用 `InfinityPacer:<branch>` |
| 把官方仓改动带入个人仓发版 | 停止；官方仓只提交 `jxxghp/MoviePilot-Plugins:main` PR |
| PR 正文暴露本机 env 或路径 | 用 `<workspace>`、相对路径和结果摘要重写 |
| 为官方仓 PR 启用 Auto-merge | 停止；合并决定权属于上游维护者 |
