# Repository Guidelines

## Project Structure & Scope Boundary
本工作区是多仓协作容器，严格区分上游开源公共规范与本机维护者执行环境
- 上游开源仓（`MoviePilot/` FastAPI 后端、`MoviePilot-Frontend/` Vue3 前端、`MoviePilot-Rust/` PyO3 原生扩展、`MoviePilot-Plugins-Official/` 官方插件、以及 `MoviePilot-Wiki/`、`MoviePilot-Resources/`、`MoviePilot-Server/`、`MoviePilot-OCR/`）各自的 `AGENTS.md` 与文档面向全体社区贡献者（contributor default），不得把维护者个人的本地环境路径或个人工作偏好写入上游仓库规则。
- 个人插件仓 `MoviePilot-Plugins/` 存放自有插件（目录在 `plugins/`、`plugins.v2/` 与 `plugins.v3/`，索引在 `package.json`、`package.v2.json`、`package.v3.json`）。
- `MoviePilot-Skills/` 是工作区根指令与专属 skill 的公开事实源，本仓不适用 `moviepilot-development` 或 `moviepilot-delivery`。

## Build, Test, and Development Commands
后端与本地 Python 环境（`MoviePilot/`）
- 在工作区根执行 `UV_PROJECT_ENVIRONMENT="${PWD}/.venv" uv sync --locked --directory MoviePilot`，按 `pyproject.toml` 与 `uv.lock` 安装运行环境（Python 3.14+），环境路径须用绝对路径以免落入后端仓内，不要使用 `MoviePilot/.venv/bin/python`（PyCharm 解释器同样指向工作区根 `.venv/bin/python`，工作目录保持 `<workspace>/MoviePilot`）。
- 本地启动后端必须在子进程中加载工作区根 `app.env`，命令为 `env -i ... /bin/zsh -lc 'set -a; source <workspace>/app.env; set +a; cd <workspace>/MoviePilot; exec <workspace>/.venv/bin/python -m app.main'`（默认 API 端口 `3001`），不得直接运行未加载该文件的后端进程。
- `pylint app` 仅在高风险改动或明确要求全量时运行，普通改动按受影响的 Python 文件运行。
- `MoviePilot-Rust/.venv` 作为 Rust 子仓独立开发环境（当前 V3 基线 Python 3.14），执行 `maturin develop` 前核对实际 Python 版本并通过目标环境的 `python -m maturin` 调用，`cp311`、`cp314` 与 `cp314t` 的 ABI 专项验证必须分别用匹配解释器显式执行 `maturin build -i <python>` 并装入隔离环境验收。

前端（`MoviePilot-Frontend/`）
- `yarn && yarn dev` 启动开发服务，`yarn build` 在依赖、构建配置、路由、资源或高风险 UI 改动时构建产物。
- `yarn typecheck && yarn lint && yarn format:check` 为前端代码改动的默认本地检查（`format:check` 对比 `v3` 基线变更文件）。修改前端生产 `JS/TS/Vue` 文件时按 `MoviePilot-Frontend/docs/code-quality.md` 同步清理该文件可安全修复的 ESLint 存量并运行 `yarn lint:suppressions:prune`，不扩改未触及文件或新增 suppression。

## Maintainer Execution & Git Boundaries
- MoviePilot 项目规则由本文件和目标仓库更近说明共同定义，本文件不创建独立 Goal、Checkpoint、Review 或 CI 控制面。
- 公共仓库 `AGENTS.md` 的业务架构、兼容性、正确性、测试隔离和真实报告是共同工程合同；提交准备与 checklist 是 contributor default。当前用户已确认为上游主要维护者，本工作区按维护者执行语境协作，授权来自当前用户或项目已确认语境，不以 GitHub `WRITE` 或 contributor 自称身份证明。
- 维护者可依据已有证据明确调整适用检查的范围、时机和交付顺序，包括先保存本地 anchor 再补验证并记录未验证项与后续安排（anchor 不代表验收通过），当前明确的不 commit/push/sync 等限制优先。
- 已知改动将用于评审或 PR 时，在修改前创建或切换业务 topic branch（若交付意图后置明确，核对 diff 后保留有效工作并迁移），只读排查或一次性本地诊断不强制建分支。
- 默认使用当前仓库 checkout，不自动创建 Git linked worktree，仅在用户明确要求隔离或已有无关脏改动无法在同一 checkout 安全分离时才使用 worktree。

## Coding Style & Comments
- Python 使用 4 空格缩进、`snake_case` 函数模块与 `PascalCase` 类；Vue/TS/SCSS 使用 2 空格、单引号、无分号，组件 `PascalCase.vue`，组合式函数 `useXxx.ts`。
- 稳定的仓内结构（ORM/model/schema/DTO/VO、插件配置模型、主程序明确返回对象、内部生命周期属性及契约测试替身）直接属性访问如 `obj.field`，禁止为求稳妥滥用 `getattr`/`hasattr`（仅在第三方 SDK、跨版本可选字段、动态事件 payload 或插件热加载等真实动态边界使用并明确默认值语义）。
- 面向中文开发者协作，跨栈（Python、TS/Vue、脚本与插件）的业务结构、公开或契约字段（实体、Schema、DTO、VO、配置与请求响应模型、插件 metadata、前端 `interface`/`type`/`enum`/`props`/`store`）及影响正确性判断的实现（插件生命周期、热重载、本地同步、缓存、异步链路、兼容分支、环境变量覆盖）默认补充中文说明（Python 用 docstring，TS/Vue 用 JSDoc 或行上注释，字段用行内注释），评审时缺失应有中文注释按缺陷处理；注释只描述当前契约与约束，不写具体插件下线或谁仍在调用等历史变更来由（背景归入 PR 说明）。
- 新增插件保持目录名与插件 ID 稳定并同步更新索引文件。新增或重写 `plugins.v2/` 或 `plugins.v3/` 插件 `README.md` 时，个人插件仓遵循根 `TEMPLATE_README.md` 顶部 HTML 注释契约，官方插件仓无模板文件时同样回读源码使配置项中文名、form-default 默认值及枚举项与 `get_form` 严格一致，不在正文暴露源码行号或 `get_form`/`init_plugin` 等元信息，高频配置项用 `<a id="cfg-<config_key>"></a>` 锚点展开，仓库根 `README.md` 首页标题须链向插件实际代际目录。

## Testing Guidelines
- 后端测试放在 `MoviePilot/tests/test_*.py`，外部服务一律 mock 保证零真实出站（见 `MoviePilot/docs/testing.md`）。
- 后端与插件单测优先使用专用环境 `<workspace>/.venv-test/bin/python`（与运行环境 `.venv` 分离，测试不加载运行用 `app.env`，隔离临时 `CONFIG_DIR`）。后端公共文档的 `uv run --locked --no-sync <command>` 在本工作区映射为 `UV_PROJECT_ENVIRONMENT="<workspace>/.venv-test" uv run --locked --no-sync <command>`（`--no-sync` 不会校验已安装依赖一致性）。主程序与插件单测由 `app.testing.bootstrap` 安装站点最小垫片而不加载源码内本机 `.so`/`.pyd`；重建测试环境在工作区根执行 `WORKSPACE="$(pwd -P)" && uv venv --python 3.14 --clear "${WORKSPACE}/.venv-test" && (cd "${WORKSPACE}/MoviePilot" && uv export --locked --no-default-groups --group dev --group runtime-standard --format requirements.txt | uv pip sync --python "${WORKSPACE}/.venv-test/bin/python" -)`。
- 插件仓单测放在各插件仓根 `tests/<gen>/<plugin_id>/test_*.py`（严禁放插件目录内以免随 `copytree` 带入运行时副本），`pytest.ini` 配置 `addopts = --import-mode=importlib`，统一使用 pytest 风格与 `assert`（不新增 `unittest.TestCase` runner，改到旧 `TestCase` 文件时整文件迁移为 pytest），经 `tests/_bootstrap.py` 复用主程序 `app.testing`（`stub_modules` 等）共享脚手架，显式传入 `MOVIEPILOT_BACKEND_PATH=<workspace>/MoviePilot`，不同代同名插件包分独立 pytest 会话运行。
- 按改动选择最小可信验证并复用源码、锁文件、脚手架未变的有效证据；仅在触及依赖锁、共享测试脚手架、数据库、启动链、跨模块生命周期、兼容层、大范围行为改动或用户明确要求时跑对应仓全量 `tests/run.py`。PR 仅受平台真实 required checks/Ruleset 与本次改动引入的实质问题阻断，optional check 或 pending 自动化不自动成为门禁；前端改动至少验证 `typecheck`、`lint`、`format:check`，视觉行为验证实际渲染面。

## Instance Boundaries & Runtime Verification
- 诊断前先区分目标现场事实与本机实验室复现。外部或远程用户反馈以目标实例证据为准，不得用本机日志、数据库或配置确认或否定外部现场；本机等价复现须记录版本与环境差异并标明实验室证据。
- 本地运行态验证（仅限本机实例或声明边界的复现）涉及前后端联动、插件 UI 或可见交互时，先探活端口、进程与日志优先复用现有服务完成真实浏览器验证（桌面与移动宽度、控制台与网络无异常）。若探测到 PyCharm debugger 或终端正在运行服务，不抢占重启（断点处提示用户操作，前端 stdout 不可读时通过浏览器控制台、Vite overlay 与网络面板诊断）。
- 本地开发实例调试插件优先通过 `PLUGIN_LOCAL_REPO_PATHS` 与 `PLUGIN_AUTO_RELOAD=true`（需停定时任务时加 `DEV=true`）更新 `MoviePilot/app/plugins/<plugin>/`，插件 UI 或模块联邦改动须同时核对运行时副本与远程组件加载，并查看 `MoviePilot/config/logs/moviepilot.log` 与 `plugins/` 日志确认加载与路由注册；注意环境变量覆盖 WebUI 配置的情况，普通接口走登录态/JWT，仅源码明确标注 `API_TOKEN` 的 `*2` 诊断接口（如 `/api/v1/dashboard/schedule2`）才传 `?token=<API_TOKEN>` 且严禁在任何公开或聊天文本输出 token 原文。本地与远程登录及 SSH 凭据统一走全局 `secure-access` 技能。

## Commit & Delivery Routing
- Commit message 默认只写单行英文 Conventional Commits subject，不附正文（允许末尾附加 `Co-Authored-By` trailer，squash 合并同样保留）；PR 标题采用英文前缀加中文摘要（`type(scope): 中文摘要`），PR 正文与 issue/review 回复默认使用中文并在公开交付前做隐私检查。
- 本工作区已确认的维护者决定允许在 merge 已获授权且平台允许正常合并时，继续交付已证实与改动无关且未被加重或重新触达的 base 失败、无关基础设施/配额故障及不可操作的 Review 反馈（同一范围的预授权，每次记录具体失败与无关依据，不绕过真实保护或放行本次改动的实质缺陷）。
- `commit`、`push`、创建 PR、`merge` 与 `release` 按当前请求、已批准计划或任务明确授权的终态执行；仅要求提交 PR 而未明确授权合并或发版时，在创建 PR 并回读检查后交维护者确认放行，已明确授权合并时按 `moviepilot-delivery` 跟踪合并，不由 PR 授权推断发版。
- 上述产品与插件代码仓的本地开发、调试和测试使用 `moviepilot-development` skill，push、PR、merge 和发版使用 `moviepilot-delivery` skill，`MoviePilot-Skills` 明确排除。当前只维护 v3，后端、前端与 Rust PR 目标为上游 `v3`，插件仓发布目标为 `main`（插件 V3 改动进 `plugins.v3/`）。
