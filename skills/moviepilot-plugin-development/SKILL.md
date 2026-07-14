---
name: moviepilot-plugin-development
description: Use when developing, debugging, testing, hot-reloading, or preparing topic branches for personal or official MoviePilot plugin repositories before release or PR delivery.
---

# MoviePilot 插件开发

## 核心原则

只处理插件仓本地开发、调试和必要验证。个人插件仓提交 PR、PR-only 或发版转
`moviepilot-plugin-delivery`；官方插件仓提交上游转 `moviepilot-official-plugin-pr`。
本 skill 不 commit、不 push、不创建 PR、不发版。
普通开发默认在当前仓库 checkout 中创建或切换业务分支；不要因保持基线干净、执行实现计划或
准备 PR 而自动创建 Git linked worktree。只有用户明确要求隔离工作区时才创建 worktree。

## 1. 确认仓库类型

运行：

```bash
git status --short --branch
git remote -v
```

按 remote 分流：

| 本地仓库 | 远端特征 | 开发基线 | 完成后转交 |
| --- | --- | --- | --- |
| `MoviePilot-Plugins` | `origin` 为 `InfinityPacer/MoviePilot-Plugins` | `origin/main` | `moviepilot-plugin-delivery` |
| `MoviePilot-Plugins-Official` | `upstream` 为 `jxxghp/MoviePilot-Plugins` | `upstream/main` | `moviepilot-official-plugin-pr` |

分支创建前只 fetch 当前仓库对应基线。个人插件仓：

```bash
git fetch origin main
```

官方插件 fork：

```bash
git fetch upstream main
```

若当前已在工作分支，核对 merge-base、基线到 HEAD 的提交范围和用户改动；不要 reset、stash
或覆盖用户已有改动。

## 2. 分支策略

开始任务前先判断工作区是否干净。若 `git status --short` 有未提交改动，先停止并询问用户
如何处理这些改动；不要擅自 reset、stash、覆盖、带入新任务或代替用户判断归属。

工作区干净后，根据用户目标和业务语义创建或选择分支。当前已在工作分支时，先判断分支是否
基于对应基线、提交范围只包含本次任务，且分支名能表达业务主题；满足这些条件就继续使用当前
分支。若当前在 `main`/`master`、分支名与业务语义不一致，或提交范围不干净，应从对应基线创建
新的业务分支。

新建分支模式仍是 `codex/<type>/<topic>` 或 `claude/<type>/<topic>`，命令中用变量展开：

```bash
BASE_REF=origin/main
TASK_TYPE=fix
TOPIC=plugin-topic
BRANCH="codex/${TASK_TYPE}/${TOPIC}"
git checkout -b "${BRANCH}" "${BASE_REF}"
```

`BASE_REF` 为个人仓 `origin/main` 或官方仓 `upstream/main`。`TASK_TYPE` 按任务类型选择
`feat`、`fix`、`chore`、`docs`、`test` 或 `ci`；普通开发、PR 门禁、文档和 CI 修复不要使用
`release` 前缀，真实发版才转 `moviepilot-plugin-delivery`。

## 3. 测试环境

插件单测通过工作区 env-file 注入 `MOVIEPILOT_BACKEND_PATH` 等运行所需变量，同时清理真实
`CONFIG_DIR`。按场景选择命令：

| 场景 | 命令 |
| --- | --- |
| 局部插件测试：改动集中在单个插件，且需要快速复现或回归该插件行为 | `pytest tests/<v1\|v2>/<plugin_id> -q` |
| A 档覆盖率门禁：个人插件仓改动触及 `plugin_quality.json` 声明的 A 档插件，或需要检查新增行覆盖率 | `scripts/plugin_coverage.py` |
| 全量回归：跨插件共享脚手架变更、测试基础设施变更、或局部结果不足以覆盖开发风险 | `tests/run.py` |
| 新增插件目录：PR 新增 `plugins/` 或 `plugins.v2/` 插件目录 | `scripts/check_new_plugin_tests.py --base-ref ${BASE_REF}` |
| 基础文件检查：索引、metadata、版本、JSON、编译或空白敏感改动 | 对应的版本门禁、`json.tool`、`compileall`、`git diff --check` |

常用命令：

```bash
WORKSPACE="${WORKSPACE:?set workspace root}"
BASE_REF=origin/main
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
    "${WORKSPACE}/.venv-test/bin/python" scripts/plugin_coverage.py
)
(
  set -a
  . "${WORKSPACE}/app.env"
  set +a
  env -u CONFIG_DIR \
    "${WORKSPACE}/.venv-test/bin/python" tests/run.py
)
```

`<workspace>/app.env` 是本机命令 env-file；不得读取、打印、提交或写进公开正文，不要把 env-file 内容拼进命令参数。
`CONFIG_DIR` 不得从运行态环境泄漏进单测。外部服务必须 mock。
`scripts/plugin_coverage.py` 会运行 `plugin_quality.json` 中 A 档插件的测试并检查覆盖率；它可替代
这些插件的局部 pytest 重跑，但不能替代 `tests/ci`、非 A 档插件测试或需要全量回归的
`tests/run.py`。

新增插件目录检查：

```bash
python scripts/check_new_plugin_tests.py --base-ref ${BASE_REF}
```

基础文件检查：

```bash
python .github/scripts/check_plugin_versions.py package.json package.v2.json
python -m json.tool package.json >/dev/null
python -m json.tool package.v2.json >/dev/null
python -m compileall -q "${PLUGIN_DIR}"
git diff --check
```

个人插件仓的 A 档覆盖率由 `plugin_quality.json` 显式声明；新增插件不会自动进入 A 档。
PR 新增插件目录时，必须至少提交对应 `tests/<v1|v2>/<plugin_id>/test_*.py` 并运行新增插件目录检查。
README、索引说明或 metadata 变更按“基础文件检查”处理；代码、运行态或发布相关变更按上表扩大验证。
最终全量门禁由 `moviepilot-plugin-delivery` 或 `moviepilot-official-plugin-pr` 执行；同一 HEAD
已在开发阶段跑过的全量结果可在交付 skill 中复用，后续有任何改动则重新跑。

## 4. 本地运行与热加载

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

个人插件仓需要提交 PR、PR-only 或发版时转 `moviepilot-plugin-delivery`；官方插件仓需要提交
上游时转 `moviepilot-official-plugin-pr`。
