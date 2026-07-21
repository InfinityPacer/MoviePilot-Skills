---
name: moviepilot-upstream-pr
description: Use when preparing, publishing, updating, or checking a pull request from the InfinityPacer MoviePilot or MoviePilot-Frontend fork to the jxxghp upstream v2 branch.
---

# MoviePilot 上游 PR

## 核心原则

只处理 `MoviePilot` 后端与 `MoviePilot-Frontend` 前端 fork。工作分支推到
`InfinityPacer/*`，PR 提交到对应 `jxxghp/*:v2`。上游维护者拥有最终合并权；不得启用
Auto-merge、不得使用管理员权限合并。

## 1. 确认仓库与分支

运行：

```bash
git status --short --branch
git remote -v
git fetch upstream v2
```

只接受以下映射：

| 本地仓库 | fork push 目标 | upstream PR 目标 |
| --- | --- | --- |
| `MoviePilot` | `InfinityPacer/MoviePilot` | `jxxghp/MoviePilot:v2` |
| `MoviePilot-Frontend` | `InfinityPacer/MoviePilot-Frontend` | `jxxghp/MoviePilot-Frontend:v2` |

若当前是 `v2`、`main` 或 `master`，从最新 `upstream/v2` 创建协作分支：

- Codex：`codex/<type>/<topic>`
- Claude Code：`claude/<type>/<topic>`

已有工作分支必须先核对 merge-base 和用户改动，不得为“保持干净”重置或覆盖。

## 2. 验证改动

### 后端 `MoviePilot`

在仓库根运行：

```bash
WORKSPACE="${WORKSPACE:?set workspace root}"
(
  set -a
  . "${WORKSPACE}/app.env"
  set +a
  env -u CONFIG_DIR "${WORKSPACE}/.venv-test/bin/python" tests/run.py
)
env -u CONFIG_DIR "${WORKSPACE}/.venv-test/bin/python" -m pylint app
git diff --check
```

`<workspace>/app.env` 是本机命令 env-file；不得读取、打印、提交或写进公开正文，不要把 env-file 内容拼进命令参数。
`CONFIG_DIR` 不得从本地运行态环境泄漏进单测；`tests/run.py` 必须零真实出站。若 `python -m pylint app`
存在与本次无关的基线失败，记录完整边界；不能把未运行写成通过，也不能用局部测试冒充全量测试。

### 前端 `MoviePilot-Frontend`

运行：

```bash
yarn typecheck
yarn lint
yarn build
git diff --check
```

涉及 UI、权限、路由、接口契约或用户流程时，还要复用或启动本地前后端，通过浏览器确认：

- 相关接口正常；
- 页面无明显控制台错误；
- 关键交互可完成；
- 响应式改动覆盖桌面与移动宽度；
- 截图已脱敏用户名、站点、token、路径及浏览器资料。

### 前后端联动

分别验证、提交和创建两个 PR。PR 正文相互链接，并说明合并顺序或兼容关系；不得把两个
仓库的改动混入一个提交或只创建其中一个 PR。

## 3. 提交前确认

commit、push 前向维护者展示：

- 仓库和分支名；
- `upstream/v2` 同步状态；
- 验证结果及未验证项；
- `git diff --stat`；
- 拟用的单行英文 Conventional Commit subject。

取得明确确认后才能 commit 或 push。只确认 commit 时不得 push；不得 force push，
除非维护者明确授权并已说明影响范围。

## 4. Push 与创建 PR

将协作分支推到 fork 的 `origin`。维护者确认 push 后，先推送当前已核对分支，再使用真实换行的
Markdown 文件创建中文 PR：

```bash
TARGET_REPO="jxxghp/MoviePilot"
BRANCH="$(git branch --show-current)"
PR_TITLE="fix: update moviepilot"
BODY_FILE="/tmp/moviepilot-upstream-pr.md"
git push -u origin "${BRANCH}"
gh pr create \
  --repo "${TARGET_REPO}" \
  --base v2 \
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

Issue 关联按以下规则写入正文：

- 同仓 issue，修复已确认且 PR 合并后应自动关闭：`Fixes #<number>`；
- 同仓 issue，仅作背景、讨论或不应自动关闭：`Refs #<number>`；
- issue 与 PR 不在同一仓库：使用 issue 完整 URL，不依赖短编号；
- 无法确认是否应自动关闭时，默认使用 `Refs`，不得擅自关闭 issue。

正文只能使用仓库相对路径、可复现命令或结果摘要，不得包含本机绝对路径、账号目录、
临时文件、凭据、Cookie、token、私有日志或本地端口映射。

## 5. 回读与跟踪

创建或更新 PR 后回读：

```bash
PR_NUMBER=123
TARGET_REPO="jxxghp/MoviePilot"
gh pr view "${PR_NUMBER}" \
  --repo "${TARGET_REPO}" \
  --json url,title,body,baseRefName,headRefName,headRefOid,state,mergeStateStatus,statusCheckRollup,reviews
```

确认：

1. base 为 `v2`，head 为 `InfinityPacer:<branch>`；
2. 正文真实分段，包含问题或目标、方案理由、影响与风险、验证结果，且没有隐私信息；
3. 回读 PR 后确认 issue 编号、仓库和 `Fixes` / `Refs` 语义正确；
4. CI 已出现，并区分等待、失败和成功；
5. review 或 requested changes 已如实报告；
6. 后续 push 后 head SHA 与 PR 一致。

不得启用 Auto-merge，不得代替上游维护者合并。用户只要求提交 PR 时，默认交付终态是
PR 创建并回读确认；若用户要求跟进 CI/review/合并，或上游已实际合并，则继续到对应结果明确为止。

## 6. 回复来源 Issue

若改动来源于 issue，PR 创建后回复 issue：

- 明确写“已提交 PR”，附 PR URL，并简述改动和验证结果；
- PR 尚未合并时不得写“已完成”“已修复”或承诺已进入正式版本；
- issue 与 PR 跨仓时，同时写明目标仓库，避免只贴短编号造成歧义。

默认交付终态是 PR 已创建并回读确认；只有用户要求跟进、PR 已实际合并或发布状态已经明确时，
才回写最终结果。

使用真实换行的临时 Markdown 文件发布，并回读 issue 最后一条评论：

```bash
ISSUE_NUMBER=123
ISSUE_REPO="jxxghp/MoviePilot"
BODY_FILE="/tmp/moviepilot-upstream-issue-comment.md"
gh issue comment "${ISSUE_NUMBER}" \
  --repo "${ISSUE_REPO}" \
  --body-file "${BODY_FILE}"
```

PR 合并后，若任务要求跟进结果，再回复合并状态与 PR/merge commit 链接。使用
`Fixes #<number>` 的同仓 issue 由合并自动关闭；使用 `Refs #<number>` 或完整 URL
关联时不主动关闭，除非维护者明确要求。每次发布评论后都要回读 issue，确认 Markdown、
链接和公开信息无误。

## 常见错误

| 错误 | 处理 |
| --- | --- |
| 从陈旧本地 `v2` 建分支 | 先 fetch，并以 `upstream/v2` 为基线 |
| 将分支推到 upstream | 只 push `origin`，PR head 使用 `InfinityPacer:<branch>` |
| 前端只跑 typecheck | 同时跑 lint/build；UI 改动补真实浏览器验证 |
| 后端局部测试代替全量 | push 前运行 `tests/run.py` |
| 多行正文使用字面量 `\n` | 使用 `--body-file`，创建后回读 |
| 为上游 PR 启用 Auto-merge | 停止；合并决定权属于 `jxxghp/*` 维护者 |
