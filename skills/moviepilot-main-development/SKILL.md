---
name: moviepilot-main-development
description: Use when developing, debugging, testing, or locally running MoviePilot backend or MoviePilot-Frontend before upstream PR delivery.
---

# MoviePilot 主程序开发

## 核心原则

只处理 `MoviePilot` 后端与 `MoviePilot-Frontend` 前端本地开发。开发完成后若要提交上游，
转 `moviepilot-upstream-pr`；本 skill 不 commit、不 push、不创建 PR。

## 1. 确认仓库与分支

运行：

```bash
git status --short --branch
git remote -v
git fetch upstream v2
```

只接受以下开发基线：

| 本地仓库 | 开发基线 |
| --- | --- |
| `MoviePilot` | `upstream/v2` |
| `MoviePilot-Frontend` | `upstream/v2` |

若当前是 `v2`、`main` 或 `master`，从最新 `upstream/v2` 创建协作分支：

- Codex：`codex/<type>/<topic>`
- Claude Code：`claude/<type>/<topic>`

已有工作分支必须先核对 merge-base、`upstream/v2..HEAD` 和用户改动；不要 reset、stash 或
覆盖用户已有改动。

## 2. 运行态环境

本地服务可以由 IDE、shell wrapper、compose 或等效命令加载工作区私有 Docker-style env-file，
例如 `<workspace>/app.env`。该文件会在进程启动前注入运行态环境变量，可能包含认证、
passkey、token、本地路径或插件市场配置。

不得读取 env-file 内容，不得打印、提交、复制该 env-file 内容到 PR、issue、review 回复或日志摘录；公开内容只写
`<workspace>/app.env` 这类占位路径。

运行态 env-file 与单测隔离环境分开。测试不得继承真实 `CONFIG_DIR`；无论 shell、IDE 或其他
运行态入口是否注入过环境变量，测试命令一律显式清理。

## 3. 后端开发

在 `MoviePilot/` 运行服务时使用工作区运行解释器：

```bash
<workspace>/.venv/bin/python -m app.main
```

若用户正在用 PyCharm debugger 或终端运行后端，不要抢占重启；通过 API、日志、浏览器网络请求
旁路验证。若进程停在断点，提示用户继续或单步。

后端测试使用单测环境：

```bash
env -u CONFIG_DIR <workspace>/.venv-test/bin/python -m pytest tests/<target> -q
env -u CONFIG_DIR <workspace>/.venv-test/bin/python tests/run.py
pylint app
git diff --check
```

外部服务必须 mock；不要把局部测试冒充全量测试。

## 4. 前端开发

在 `MoviePilot-Frontend/` 运行：

```bash
yarn dev
yarn typecheck
yarn lint
yarn build
git diff --check
```

涉及 UI、权限、路由、接口契约或用户流程时，复用或启动本地前后端，通过浏览器确认接口、控制台、
关键交互和响应式布局。截图和 PR 说明必须脱敏用户名、站点、token、路径和浏览器资料。

## 5. 完成开发

完成后汇总：

- 仓库、分支与基线；
- 改动范围；
- 运行过的测试、lint、浏览器验证；
- 未验证项和原因类别；
- `git diff --stat`。

需要提交上游 PR 时，转 `moviepilot-upstream-pr`。
