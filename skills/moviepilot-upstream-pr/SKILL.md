---
name: moviepilot-upstream-pr
description: Use when preparing, publishing, updating, or checking a pull request from the InfinityPacer MoviePilot or MoviePilot-Frontend fork to the jxxghp upstream v3 branch.
---

# MoviePilot 上游 PR

## 核心原则

只处理 `MoviePilot` 后端与 `MoviePilot-Frontend` 前端 fork。工作分支推到
`InfinityPacer/*`，PR 提交到对应 `jxxghp/*:v3`。上游维护者拥有最终合并权；不得启用
Auto-merge、不得使用管理员权限合并。

## 1. 确认仓库与分支

运行：

```bash
git status --short --branch
git remote -v
git fetch upstream v3
```

只接受以下映射：

| 本地仓库 | fork push 目标 | upstream PR 目标 |
| --- | --- | --- |
| `MoviePilot` | `InfinityPacer/MoviePilot` | `jxxghp/MoviePilot:v3` |
| `MoviePilot-Frontend` | `InfinityPacer/MoviePilot-Frontend` | `jxxghp/MoviePilot-Frontend:v3` |

若当前是 `v3`、`main` 或 `master`，从最新 `upstream/v3` 创建协作分支：

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

## 3. 提交与授权

commit、push 前核对：

- 仓库和分支名；
- `upstream/v3` 同步状态；
- 验证结果及未验证项；
- `git diff --stat`；
- 拟用的单行英文 Conventional Commit subject。

本地 commit 服从当前 `dev-workflow`、已批准计划或本轮用户授权；已有授权时直接执行，不重复确认。
push 和 PR 是独立的外部交付边界，只有当前指令或既有授权已覆盖时才能执行；只授权 commit 时
不得 push。不得 force push，除非维护者明确授权并已说明影响范围。

## 4. Push 与创建 PR

将协作分支推到 fork 的 `origin`。push/PR 已获授权后，先推送当前已核对分支，再使用真实换行的
Markdown 文件创建 PR：

```bash
TARGET_REPO="jxxghp/MoviePilot"
BRANCH="$(git branch --show-current)"
PR_TITLE="fix: 修复 MoviePilot 行为"
BODY_FILE="/tmp/moviepilot-upstream-pr.md"
git push -u origin "${BRANCH}"
gh pr create \
  --repo "${TARGET_REPO}" \
  --base v3 \
  --head "InfinityPacer:${BRANCH}" \
  --title "${PR_TITLE}" \
  --body-file "${BODY_FILE}"
```

PR 标题、正文和 issue 回复默认使用中文，commit subject 使用英文 Conventional Commit；目标仓库
模板或维护者另有要求时从其要求。同时应用 `dev-workflow` 的通用 PR 沟通与隐私契约，本 skill
不复制固定章节模板。正文深度随改动风险调整，标题必须描述主要行为或维护结果，不能用测试或
实现手段掩盖生产行为变化，也不要重复自动生成的 PR 摘要。

MoviePilot 专项内容只补充实际存在的 fork/upstream 边界、`v3` 目标、验证结果、跨前后端 PR 的
兼容关系或合并顺序。Issue 仅在修复完整且合并后应自动关闭时使用 `Fixes`；部分处理或背景关联
使用 `Refs`，跨仓使用完整 URL。

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

1. base 为 `v3`，head 为 `InfinityPacer:<branch>`；
2. 正文与改动规模匹配，维护者无需本地讨论即可理解主要问题、行为变化、必要边界和验证结果；
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
| 从陈旧本地 `v3` 建分支 | 先 fetch，并以 `upstream/v3` 为基线 |
| 将分支推到 upstream | 只 push `origin`，PR head 使用 `InfinityPacer:<branch>` |
| 前端只跑 typecheck | 同时跑 lint/build；UI 改动补真实浏览器验证 |
| 后端局部测试代替全量 | push 前运行 `tests/run.py` |
| 多行正文使用字面量 `\n` | 使用 `--body-file`，创建后回读 |
| 为上游 PR 启用 Auto-merge | 停止；合并决定权属于 `jxxghp/*` 维护者 |
