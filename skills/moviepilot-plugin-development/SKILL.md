---
name: moviepilot-plugin-development
description: Use when developing, debugging, testing, hot-reloading, or preparing topic branches for personal or official MoviePilot plugin repositories before release or PR delivery.
---

# MoviePilot 插件开发

## 核心原则

只处理插件仓本地开发与验证。个人插件仓发布转 `moviepilot-plugin-release`；官方插件仓提交上游转
`moviepilot-official-plugin-pr`。本 skill 不 commit、不 push、不创建 PR、不发版。

## 1. 确认仓库类型

运行：

```bash
git status --short --branch
git remote -v
```

按 remote 分流：

| 本地仓库 | 远端特征 | 开发基线 | 完成后转交 |
| --- | --- | --- | --- |
| `MoviePilot-Plugins` | `origin` 为 `InfinityPacer/MoviePilot-Plugins` | `origin/main` | `moviepilot-plugin-release` |
| `MoviePilot-Plugins-Official` | `upstream` 为 `jxxghp/MoviePilot-Plugins` | `upstream/main` | `moviepilot-official-plugin-pr` |

分支创建前先 fetch 对应基线：

```bash
git fetch origin main
git fetch upstream main
```

只运行当前仓库需要的 fetch。若当前已在工作分支，核对 merge-base、基线到 HEAD 的提交范围和
用户改动；不要 reset、stash 或覆盖用户已有改动。

## 2. 分支策略

在当前插件仓内从对应基线创建协作分支：

```bash
git checkout -b codex/<type>/<topic> <base>
git checkout -b claude/<type>/<topic> <base>
```

`<base>` 为个人仓 `origin/main` 或官方仓 `upstream/main`。`<type>` 按任务类型选择
`feat`、`fix`、`chore`、`docs`、`test` 或 `ci`；普通开发、PR 门禁、文档和 CI 修复不要使用
`release` 前缀，真实发版才转 `moviepilot-plugin-release`。

## 3. 测试环境

插件单测必须显式定位主程序源码，同时清理真实 `CONFIG_DIR`。按改动面选择最小可信闭环：

```bash
env -u CONFIG_DIR MOVIEPILOT_BACKEND_PATH=<workspace>/MoviePilot \
  <workspace>/.venv-test/bin/python -m pytest tests/<v1|v2>/<plugin_id> -q
env -u CONFIG_DIR MOVIEPILOT_BACKEND_PATH=<workspace>/MoviePilot \
  <workspace>/.venv-test/bin/python scripts/plugin_coverage.py
env -u CONFIG_DIR MOVIEPILOT_BACKEND_PATH=<workspace>/MoviePilot \
  <workspace>/.venv-test/bin/python tests/run.py
```

`MOVIEPILOT_BACKEND_PATH=<workspace>/MoviePilot` 只用于定位后端源码，可以保留在本地
Docker-style env-file 中；`CONFIG_DIR` 不得从运行态环境泄漏进单测。外部服务必须 mock。
`scripts/plugin_coverage.py` 会运行 `plugin_quality.json` 中 A 档插件的测试并检查覆盖率；它可替代
这些插件的局部 pytest 重跑，但不能替代 `tests/ci`、非 A 档插件测试或需要全量回归的
`tests/run.py`。

个人插件仓的 A 档覆盖率由 `plugin_quality.json` 显式声明；新增插件不会自动进入 A 档。
PR 新增 `plugins/` 或 `plugins.v2/` 插件目录时，至少要提交对应
`tests/<v1|v2>/<plugin_id>/test_*.py`，并本地运行：

```bash
python scripts/check_new_plugin_tests.py --base-ref <base>
```

基础检查按影响面选择：

```bash
python .github/scripts/check_plugin_versions.py package.json package.v2.json
python -m json.tool package.json >/dev/null
python -m json.tool package.v2.json >/dev/null
python -m compileall -q plugins.v2/<plugin_id>
git diff --check
```

README、索引说明或 metadata 变更可使用更小闭环；代码、运行态或发布相关变更必须扩大验证。

## 4. 本地运行与热加载

本地服务可以加载工作区私有 Docker-style env-file，例如 `<workspace>/app.env`。该文件可能包含认证、
passkey、token、本地插件路径和市场配置；不得读取、打印、提交或写进公开正文。

插件源码事实源是本地插件仓。运行态调试优先通过：

- `PLUGIN_LOCAL_REPO_PATHS` 指向一个或多个本地插件仓；
- `PLUGIN_AUTO_RELOAD=true` 触发同步和热加载；
- 仅需要暂停定时任务时启用 `DEV=true`。

修改源码后，先确认市场列表、安装状态、本地同步、运行时副本、插件日志和热加载日志，再判断业务逻辑。
不要把手动复制运行时副本作为默认调试方式。

## 5. 完成开发

完成后汇总：

- 仓库类型、分支和基线；
- 改动路径；
- 单测、版本门禁、JSON、compile、运行态验证；
- 未验证项和原因类别；
- `git diff --stat`。

个人插件仓需要发版时转 `moviepilot-plugin-release`；官方插件仓需要提交上游时转
`moviepilot-official-plugin-pr`。
