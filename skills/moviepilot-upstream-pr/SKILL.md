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
<workspace>/.venv-test/bin/python tests/run.py
pylint app
git diff --check
```

`tests/run.py` 必须零真实出站。若 `pylint app` 存在与本次无关的基线失败，记录完整边界；
不能把未运行写成通过，也不能用局部测试冒充全量测试。

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

将协作分支推到 fork 的 `origin`。使用真实换行的 Markdown 文件创建中文 PR：

```bash
gh pr create \
  --repo jxxghp/<MoviePilot-or-MoviePilot-Frontend> \
  --base v2 \
  --head InfinityPacer:<branch> \
  --title "<Conventional Commit 风格标题>" \
  --body-file <body-file>
```

正文包括：

- 变更说明；
- 影响路径；
- 复现或验证结果；
- 关联 issue 或联动 PR；
- 实际协作来源。

协作来源固定写在末尾：

- 仅 Codex：`本 PR 为 Codex 协作提交`
- 仅 Claude Code：`本 PR 为 Claude Code 协作提交`
- 两者实际参与：`本 PR 为 Claude Code & Codex 协作提交`

正文只能使用仓库相对路径、可复现命令或结果摘要，不得包含本机绝对路径、账号目录、
临时文件、凭据、Cookie、token、私有日志或本地端口映射。

## 5. 回读与跟踪

创建或更新 PR 后回读：

```bash
gh pr view <number> \
  --repo jxxghp/<repo> \
  --json url,title,body,baseRefName,headRefName,headRefOid,state,mergeStateStatus,statusCheckRollup,reviews
```

确认：

1. base 为 `v2`，head 为 `InfinityPacer:<branch>`；
2. 正文真实分段且没有隐私信息；
3. CI 已出现，并区分等待、失败和成功；
4. review 或 requested changes 已如实报告；
5. 后续 push 后 head SHA 与 PR 一致。

不得启用 Auto-merge，不得代替上游维护者合并。用户只要求提交 PR 时，PR 创建并回读后
即可交付；若用户要求跟进 CI/review，则继续到对应结果明确为止。

## 常见错误

| 错误 | 处理 |
| --- | --- |
| 从陈旧本地 `v2` 建分支 | 先 fetch，并以 `upstream/v2` 为基线 |
| 将分支推到 upstream | 只 push `origin`，PR head 使用 `InfinityPacer:<branch>` |
| 前端只跑 typecheck | 同时跑 lint/build；UI 改动补真实浏览器验证 |
| 后端局部测试代替全量 | push 前运行 `tests/run.py` |
| 多行正文使用字面量 `\n` | 使用 `--body-file`，创建后回读 |
| 为上游 PR 启用 Auto-merge | 停止；合并决定权属于 `jxxghp/*` 维护者 |
