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

插件测试必须显式指定后端，并清理真实 `CONFIG_DIR`：

```bash
env -u CONFIG_DIR MOVIEPILOT_BACKEND_PATH=<workspace>/MoviePilot \
  <workspace>/.venv-test/bin/python -m pytest tests/<v1|v2>/<plugin_id> -q
env -u CONFIG_DIR MOVIEPILOT_BACKEND_PATH=<workspace>/MoviePilot \
  <workspace>/.venv-test/bin/python tests/run.py
python .github/scripts/check_plugin_versions.py package.json package.v2.json
python -m json.tool package.json >/dev/null
python -m json.tool package.v2.json >/dev/null
git diff --check
```

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

将协作分支推到 fork 的 `origin`。使用真实换行的 Markdown 文件创建中文 PR：

```bash
gh pr create \
  --repo jxxghp/MoviePilot-Plugins \
  --base main \
  --head InfinityPacer:<branch> \
  --title "<Conventional Commit 风格标题>" \
  --body-file <body-file>
```

正文包括变更说明、影响路径、验证结果、关联 issue 或联动 PR、实际协作来源。正文只能使用仓库
相对路径、可复现命令或结果摘要，不得包含本机绝对路径、账号目录、临时文件、凭据、Cookie、
token、私有日志或本地端口映射。

Issue 关联按以下规则写入正文：

- 同仓 issue，修复已确认且 PR 合并后应自动关闭：`Fixes #<number>`；
- 同仓 issue，仅作背景、讨论或不应自动关闭：`Refs #<number>`；
- issue 与 PR 不在同一仓库：使用 issue 完整 URL，不依赖短编号；
- 无法确认是否应自动关闭时，默认使用 `Refs`，不得擅自关闭 issue。

## 5. 回读与跟踪

创建或更新 PR 后回读：

```bash
gh pr view <number> \
  --repo jxxghp/MoviePilot-Plugins \
  --json url,title,body,baseRefName,headRefName,headRefOid,state,mergeStateStatus,statusCheckRollup,reviews
```

确认：

1. base 为 `main`，head 为 `InfinityPacer:<branch>`；
2. 正文真实分段且没有隐私信息；
3. issue 编号、仓库和 `Fixes` / `Refs` 语义正确；
4. CI 或 `Plugin release gate` 已出现，并区分等待、失败和成功；
5. review 或 requested changes 已如实报告；
6. 后续 push 后 head SHA 与 PR 一致。

不得启用 Auto-merge，不得代替上游维护者合并，不得运行个人仓自动合并或发布回查步骤。
用户只要求提交 PR 时，PR 创建并回读后即可交付；若用户要求跟进 CI/review，则继续到
对应结果明确为止。

## 常见错误

| 错误 | 处理 |
| --- | --- |
| 从陈旧本地 `main` 建分支 | 先 fetch，并以 `upstream/main` 为基线 |
| 将分支推到 upstream | 只 push `origin`，PR head 使用 `InfinityPacer:<branch>` |
| 把官方仓改动带入个人仓发版 | 停止；官方仓只提交 `jxxghp/MoviePilot-Plugins:main` PR |
| PR 正文暴露本机 env 或路径 | 用 `<workspace>`、相对路径和结果摘要重写 |
| 为官方仓 PR 启用 Auto-merge | 停止；合并决定权属于上游维护者 |
