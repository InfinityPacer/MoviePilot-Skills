---
name: moviepilot-plugin-development
description: Use when developing, debugging, testing, hot-reloading, or preparing topic branches for personal or official MoviePilot plugin repositories before release or PR delivery.
---

# MoviePilot 插件开发

## 核心原则

只处理插件仓本地开发、调试和必要验证。个人插件仓提交 PR、PR-only 或发版转
`moviepilot-plugin-delivery`；官方插件仓提交上游转 `moviepilot-official-plugin-pr`。
本地 commit 服从当前 `dev-workflow`、已批准计划或用户授权；本 skill 不 push、不创建 PR、不发版。
普通开发默认在当前仓库 checkout 中创建或切换业务分支；不要因保持基线干净、执行实现计划或
准备 PR 而自动创建 Git linked worktree。只有用户明确要求隔离工作区时才创建 worktree。

## 0. 证据实例边界

执行前先确认问题主体是当前本地实例、外部用户实例，还是明确构造的实验室复现。外部用户反馈
优先依据用户时序、目标实例证据、宿主与插件版本以及源码和部署契约；本机日志、数据库、配置、
备份、安装状态和运行时副本默认只描述本机，不能确认或否定外部现场，也不应仅因可访问就先行检查。

问题主体确认是当前本地实例且宿主、插件版本与时间窗口匹配时，本机运行态是合格证据，应按问题
范围使用。
本地环境可以用于复现或验证源码假设，但必须说明宿主/插件版本、部署、挂载、配置和输入的等价
条件、已知差异及结论边界。缺少必要现场证据时保留未知或索取最小证据，不用本机状态替代。只有
目标确为当前本地实例，或已经声明实验室复现边界时，本地同步、热加载和日志步骤才适用。

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

开始任务前先判断工作区状态和改动归属。若 `git status --short` 有未提交改动，先核对它们是否属于
当前任务、另一条已知工作线或来源不明。当前任务改动继续保留；无关改动不得混入、reset、stash
或覆盖，能安全隔离时使用独立分支或用户已授权的 worktree。只有归属不明、修改范围重叠或无法
安全隔离时才询问用户。

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
| 局部插件测试：改动集中在单个插件，且需要快速复现或回归该插件行为 | `pytest tests/<v1\|v2\|v3>/<plugin_id> -q` |
| A 档覆盖率门禁：个人插件仓改动触及 `plugin_quality.json` 声明的 A 档插件，或需要检查新增行覆盖率 | `scripts/plugin_coverage.py` |
| 全量回归：跨插件共享脚手架、测试基础设施、跨代兼容索引、多插件公共行为、局部结果不足，或 PR CI 无法可靠运行 | `tests/run.py` |
| 新增插件目录：PR 新增 `plugins/`、`plugins.v2/` 或 `plugins.v3/` 插件目录 | `scripts/check_new_plugin_tests.py --base-ref ${BASE_REF}` |
| 基础文件检查：索引、metadata、版本、JSON、编译或空白敏感改动 | 对应的版本门禁、`json.tool`、`compileall`、`git diff --check` |

常用命令：

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
python .github/scripts/check_plugin_versions.py package.json package.v2.json package.v3.json
python -m json.tool package.json >/dev/null
python -m json.tool package.v2.json >/dev/null
python -m json.tool package.v3.json >/dev/null
python -m compileall -q "${PLUGIN_DIR}"
git diff --check
```

个人插件仓的 A 档覆盖率由 `plugin_quality.json` 显式声明；新增插件不会自动进入 A 档。
PR 新增插件目录时，必须至少提交对应 `tests/<v1|v2>/<plugin_id>/test_*.py` 并运行新增插件目录检查。
README、索引说明或 metadata 变更按“基础文件检查”处理；代码、运行态或发布相关变更按上表扩大验证。
普通 PR 的完整回归由目标仓 `Plugin Gate` CI 执行；`moviepilot-plugin-delivery` 或
`moviepilot-official-plugin-pr` 负责评估尚未完成的交付与发布门禁。在有效源码、后端基线、依赖、
测试脚手架和环境边界未改变时复用已有结果；后续改动或非重叠 rebase 只重跑被具体变化失效的证据。

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
