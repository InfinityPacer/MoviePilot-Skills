---
name: moviepilot-main-development
description: Use when developing, debugging, testing, or locally running MoviePilot backend or MoviePilot-Frontend before upstream PR delivery.
---

# MoviePilot 主程序开发

## 核心原则

只处理 `MoviePilot` 后端与 `MoviePilot-Frontend` 前端本地开发。开发完成后若要提交上游，
转 `moviepilot-upstream-pr`。本地 commit 服从当前 `dev-workflow`、已批准计划或用户授权；本 skill
不 push、不创建 PR。
普通开发默认在当前仓库 checkout 中创建或切换业务分支；不要因保持基线干净、执行实现计划或
准备 PR 而自动创建 Git linked worktree。只有用户明确要求隔离工作区时才创建 worktree。

## 1. 确认仓库与分支

运行：

```bash
git status --short --branch
git remote -v
git fetch upstream v3
```

只接受以下开发基线：

| 本地仓库 | 开发基线 |
| --- | --- |
| `MoviePilot` | `upstream/v3` |
| `MoviePilot-Frontend` | `upstream/v3` |

若当前是 `v3`、`main` 或 `master`，从最新 `upstream/v3` 创建协作分支：

- Codex：`codex/<type>/<topic>`
- Claude Code：`claude/<type>/<topic>`

开始任务前先判断工作区状态和改动归属。若 `git status --short` 有未提交改动，先核对它们是否属于
当前任务、另一条已知工作线或来源不明。当前任务改动继续保留；无关改动不得混入、reset、stash
或覆盖，能安全隔离时使用独立分支或用户已授权的 worktree。只有归属不明、修改范围重叠或无法
安全隔离时才询问用户。

工作区干净后，根据用户目标和业务语义创建或选择分支。当前已在工作分支时，先判断分支是否
基于 `upstream/v3`、提交范围只包含本次任务，且分支名能表达业务主题；满足这些条件就继续使用
当前分支。若当前在 `v3`、`main`、`master`，分支名与业务语义不一致，或提交范围不干净，应从
最新 `upstream/v3` 创建新的业务分支。已有工作分支必须先核对 merge-base、`upstream/v3..HEAD`
和用户改动。

## 2. 运行态环境

本地服务可以由 IDE、shell wrapper、compose 或等效命令加载工作区私有 Docker-style env-file，
例如 `<workspace>/app.env`。该文件会在进程启动前注入运行态环境变量，可能包含认证、
passkey、token、本地路径或插件市场配置。

不得读取 env-file 内容，不得打印、提交、复制该 env-file 内容到 PR、issue、review 回复或日志摘录；公开内容只写
`<workspace>/app.env` 这类占位路径。不要把 env-file 内容拼进命令参数。

需要在命令中显式加载 env-file 时，用子 shell 限定作用域；测试命令一律清理真实
`CONFIG_DIR`：

```bash
WORKSPACE="${WORKSPACE:?set workspace root}"
(
  set -a
  . "${WORKSPACE}/app.env"
  set +a
  env -u CONFIG_DIR "${WORKSPACE}/.venv-test/bin/python" -m pytest tests
)
```

## 3. 后端开发

在 `MoviePilot/` 运行服务时使用工作区运行解释器：

```bash
WORKSPACE="${WORKSPACE:?set workspace root}"
(
  set -a
  . "${WORKSPACE}/app.env"
  set +a
  "${WORKSPACE}/.venv/bin/python" -m app.main
)
```

若用户正在用 PyCharm debugger 或终端运行后端，不要抢占重启；通过 API、日志、浏览器网络请求
旁路验证。若进程停在断点，提示用户继续或单步。

后端测试使用单测环境：

```bash
WORKSPACE="${WORKSPACE:?set workspace root}"
if [ -n "${TEST_TARGET:-}" ]; then
  (
    set -a
    . "${WORKSPACE}/app.env"
    set +a
    env -u CONFIG_DIR "${WORKSPACE}/.venv-test/bin/python" -m pytest "${TEST_TARGET}" -q
  )
fi
```

首次使用共享环境、依赖锁变化或环境缺少锁定工具时，在 `MoviePilot/` 中把工作区根运行环境与测试环境
同步到当前 `pyproject.toml` 和 `uv.lock`：

```bash
UV_PROJECT_ENVIRONMENT="${WORKSPACE}/.venv" uv sync --locked
UV_PROJECT_ENVIRONMENT="${WORKSPACE}/.venv-test" uv sync --locked
```

只有确认目标环境已同步后才使用 `uv run --locked --no-sync`。不得让该命令在后端仓库或隔离 worktree
中隐式创建 `MoviePilot/.venv`；缺少 Ruff、Pylint 等开发工具时应同步共享环境，而不是把空环境当成
项目依赖缺失。

有 Python 文件改动时，默认对改动文件同时运行 Pylint 与 Ruff：

```bash
PYTHON_TARGETS="${PYTHON_TARGETS:-}"
if [ -n "${PYTHON_TARGETS}" ]; then
  env -u CONFIG_DIR "${WORKSPACE}/.venv-test/bin/python" -m pylint ${PYTHON_TARGETS}
  env -u CONFIG_DIR "${WORKSPACE}/.venv-test/bin/python" -m ruff check ${PYTHON_TARGETS}
fi
```

触及 Ruff 架构治理脚本、baseline，或 CI 报告新增 Ruff 诊断时，补跑全仓只降不增门禁：

```bash
env -u CONFIG_DIR "${WORKSPACE}/.venv-test/bin/python" scripts/architecture/ruff_ratchet.py
```

新增诊断应修复；不得通过 `--write` 放宽 baseline。只有实际清理存量诊断且需要固化更低水位时，才更新
baseline 并审计对应 diff。

默认按改动选择 focused 测试。依赖或锁文件、共享测试脚手架、数据库、启动链、跨模块生命周期、
兼容层、大范围行为改动，或用户明确要求本地全量时，才在 `MoviePilot/` 运行
`${WORKSPACE}/.venv-test/bin/python tests/run.py`；只有断点、顺序污染或覆盖率采集需要单进程时才显式
追加 `--serial`。外部服务必须 mock；不要把局部测试冒充全量测试。

最终全量门禁由 `moviepilot-upstream-pr` 交付流程触发并由上游 CI 执行；本地全量不是每次开发或 PR 的
重复门禁。在有效源码、依赖锁、测试脚手架和环境边界未改变时复用已有结果；后续改动或非重叠 rebase
只重跑被具体变化失效的证据，不因 HEAD 变化机械重跑全部检查。

## 4. 前端开发

在 `MoviePilot-Frontend/` 运行：

```bash
yarn dev
```

涉及 UI、权限、路由、接口契约或用户流程时，复用或启动本地前后端，通过浏览器确认接口、控制台、
关键交互和响应式布局。截图和 PR 说明必须脱敏用户名、站点、token、路径和浏览器资料。

## 5. 完成开发

完成后汇总：

- 仓库、分支与基线；
- 改动范围；
- 运行过的测试或浏览器验证；
- 未验证项和原因类别；
- `git diff --stat`。

需要提交上游 PR 时，转 `moviepilot-upstream-pr`。
