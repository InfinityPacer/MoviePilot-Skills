# Repository Guidelines

## Project Structure & Module Organization
本工作区是多仓协作：
- `MoviePilot/`：后端（FastAPI），核心代码在 `app/`，迁移在 `database/versions/`，测试在 `tests/`。
- `MoviePilot-Frontend/`：前端（Vue3 + Vite），主代码在 `src/`，静态资源在 `public/`。
- `MoviePilot-Plugins/`：插件集合，插件目录在 `plugins/`、`plugins.v2/` 与 `plugins.v3/`，索引在 `package.json`、`package.v2.json`、`package.v3.json`。
- `MoviePilot-Rust/`：PyO3 原生扩展，本地开发环境与主程序运行环境独立。
- `MoviePilot-Skills/`：工作区指令与专属 skill 的事实源；本仓不适用 `moviepilot-development` 或 `moviepilot-delivery`。

## Build, Test, and Development Commands
后端（`MoviePilot/`）：
- `UV_PROJECT_ENVIRONMENT=.venv uv sync --locked --directory MoviePilot`：按 `pyproject.toml` 与 `uv.lock` 安装依赖（Python 3.14+）。
- `<workspace>/.venv/bin/python -m app.main`：本地启动后端（默认 API `3001`），工作目录为 `MoviePilot/`。
- 后端与插件单测命令统一见「Testing Guidelines」，不要在本段维护第二套测试入口。
- `pylint app`：后端全量静态检查，仅在高风险改动或明确要求本地全量时运行；普通改动按受影响的 Python 文件运行。

本地 Python 环境：
- 优先使用工作区根目录解释器 `<workspace>/.venv/bin/python`（Python 3.14+），并以 `MoviePilot/` 作为后端工作目录运行脚本。
- 不要使用 `MoviePilot/.venv/bin/python`；后端仓库内不保留独立运行环境，统一使用工作区根 `.venv`，避免解释器版本和依赖状态分叉。
- PyCharm 运行配置中，解释器应指向工作区根目录 `.venv/bin/python`，工作目录保持 `<workspace>/MoviePilot`。
- `MoviePilot-Rust/.venv` 可作为 Rust 子仓的独立本地开发环境；当前 V3 开发基线使用 Python 3.14。执行 `maturin develop` 前必须核对该环境的实际 Python 版本，并通过目标环境的 `python -m maturin` 调用，不根据已存在的 `.venv` 推断目标 ABI。
- cp311、cp314 和 cp314t 的 ABI 专项验证必须分别使用匹配解释器显式执行 `maturin build -i <python>`，并将 wheel 安装到对应的隔离环境中验证；不得用单个 `maturin develop` 环境代替多 ABI 验收。

前端（`MoviePilot-Frontend/`）：
- `yarn && yarn dev`：启动开发服务。
- `yarn build`：在依赖、构建配置、路由、资源、产物或高风险 UI 改动时构建产物。
- `yarn typecheck && yarn lint`：前端代码改动的默认本地检查。
- 前端生产 `JS/TS/Vue` 文件遵循 `MoviePilot-Frontend/docs/code-quality.md` 的渐进治理：业务 PR 修改到某个生产文件时，同时审计并修复该文件可安全处理的 ESLint 存量，运行 `yarn lint:suppressions:prune` 裁剪已失效 baseline；不要因此扩改未触及文件或新增 suppression。

## Task Completion Defaults
- MoviePilot 项目规则叠加在全局 `product-development` 生命周期之上；可见前端或交互结果变化时同时使用 `frontend-development`。本文件不创建独立 Goal、Checkpoint、Review 或 CI 控制面。
- 先完成用户指定的 MoviePilot 目标，再按改动类型选择最小但可信的验证闭环。不要为了覆盖所有可能检查而扩大到无关仓库、无关插件或无关运行态。
- 后端、前端、插件、文档或交付流程分别按本文件对应章节验证；若服务、凭据、外部依赖或登录态不可用，说明阻塞类别、已完成的本地证据和剩余风险。
- 涉及发布、PR、issue 回复、公开截图或日志摘录时，最终交付前做一次隐私审查，确保公开内容只包含维护者可复现或可判断的信息。
- 已知改动将用于评审或 PR 时，在修改前创建或切换业务 topic branch；若交付意图在修改后才明确，核对当前 diff 后保留有效工作并迁移到合适分支。只读排查、一次性本地诊断或明确不交付的工作不为流程形式强制建分支。
- 默认使用当前仓库 checkout，不因保持基线干净、执行计划或准备 PR 自动创建 Git linked worktree；只有用户明确要求隔离，或已存在的无关改动无法在同一 checkout 安全分离时才使用 worktree。

## Coding Style & Naming Conventions
- Python：4 空格缩进，`snake_case`（函数/模块）+ `PascalCase`（类）。
- 稳定的仓内结构（ORM/model/schema/DTO/VO、插件配置模型、主程序明确返回对象、测试替身中按契约构造的对象）字段应直接属性访问，例如 `obj.field`；不要为了“保险”滥用 `getattr`/`hasattr`。只有动态边界才使用 `getattr`/`hasattr`，例如第三方 SDK 对象、跨版本可选字段、事件 payload 兼容、dict/object 混合适配、插件热加载或外部协议返回值不稳定等场景；使用时应让默认值语义明确，必要时补一句说明为什么这里是动态对象。
- 类定义或构造函数建立的内部生命周期状态、资源句柄和私有属性同样属于稳定仓内结构，应直接访问。不得使用 `getattr`/`hasattr` 容忍绕过构造函数的测试对象或理论上的半初始化状态；测试替身应主动补齐被测路径所需的对象契约。
- Vue/TS/SCSS：2 空格、单引号、无分号（遵循 Prettier/ESLint 配置）。
- 组件命名 `PascalCase.vue`；组合式函数命名 `useXxx.ts`。
- 新增插件时，目录名与插件 ID 保持稳定，并同步更新插件索引文件。
- 插件 README 规范：新增或重写 `plugins.v2/` 或 `plugins.v3/` 下任一插件的 `README.md` 时，以仓库根 `TEMPLATE_README.md` 为基础——配置项中文名必须与 `get_form` 里该字段的 `label` 字符串完全一致（包括括号注解如"（实验性功能）"），不要按"功能描述"自己拟名；默认值以 `get_form` 返回的 form-default 字典为准；可选枚举与 `get_form` 的 `items` 一一对齐；禁止只翻译表单 hint；禁止在正文出现"源码 line N / `get_form` 返回 / `init_plugin` 默认值"等元信息；高频翻车配置项放到「深入说明」展开，并按 `<a id="cfg-<config_key>"></a>` 显式锚点从配置表跳转。详细写作约定见 `TEMPLATE_README.md` 顶部 HTML 注释。
- 插件市场首页链接：插件仓库根 `README.md` 的"插件说明"小节，存在独立 README 的插件标题须链接到实际代际目录（`plugins.v3/`、`plugins.v2/` 或 `plugins/`），不得把 V3 插件链接回旧代目录。

## Code Comments
- 默认继承全局注释规范；本节只补充 MoviePilot 工作区的 repo-specific 要求，避免重复维护两套通用规则。
- 当前工作区面向中文开发者协作，业务结构和对外契约默认补充中文说明；字段说明可以很短，但公开或 contract-like 字段应能说明用途、来源或约束。范围包括但不限于后端实体类、ORM model、Schema、DTO、VO、配置模型、API 请求/响应模型、插件 metadata、注册对象，以及前端 interface、type、enum、props、store state 和返回值映射结构。
- MoviePilot 是多语言全栈工作区，注释要求不限于 Python 和 TS/Vue；后端、前端、脚本和插件相关代码都按同一标准执行，并优先采用各语言原生的注释形式。
- Python 优先使用 docstring；TS/Vue 优先使用 JSDoc 或行上注释；字段说明优先 inline comment；其他语言遵循各自惯例，但默认保持中文说明。
- 对会影响 reviewer 判断正确性的实现，默认补充 review-oriented 注释，重点覆盖插件生命周期、热重载、本地插件同步、缓存、副作用、异步链路、兼容分支、能力位/模式字段、环境变量覆盖和前后端契约。
- Reviewer 在评审 MoviePilot 工作区改动时，应把业务结构、对外契约、跨模块方法或非显然逻辑缺少应有中文注释视为缺陷，而不是风格建议；明确落入例外范围时放行。

## Testing Guidelines
- 后端测试统一放在 `MoviePilot/tests/`，文件名使用 `test_*.py`。
- 涉及外部服务（TMDB、下载器、媒体服务器、LLM 目录、MP 服务器、任意外链）优先 mock，保证 focused 测试与 CI 全量测试都可重复且零真实出站。详见 `MoviePilot/docs/testing.md`。
- 后端单测优先使用单测专用环境 `<workspace>/.venv-test/bin/python`：该环境按 `MoviePilot/pyproject.toml` 与 `uv.lock` 安装依赖，不依赖本地生成的站点扩展资源，能复现 CI / 全新环境，避免本地编译产物和额外包掩盖问题。
- 普通主程序及插件单测由 `MoviePilot/tests/conftest.py` 复用的 `app.testing.bootstrap` 强制安装 `app.application.site.sites` 最小垫片，不加载源码目录中的本机 `.so` / `.pyd`；真实制品只在资源与 ABI 专项验收中加载。重建时在工作区根目录执行：`WORKSPACE="$(pwd -P)" && uv venv --python 3.14 --clear "${WORKSPACE}/.venv-test" && (cd "${WORKSPACE}/MoviePilot" && uv export --locked --no-default-groups --group dev --group runtime-standard --format requirements.txt | uv pip sync --python "${WORKSPACE}/.venv-test/bin/python" -)`。
- 插件仓单测放在各插件仓库根 `tests/` 下（**不放插件目录内**：插件按整目录 `copytree` 下发，目录内测试会被带进运行时副本），按目标仓库实际支持的代际目录分组（通常为 `v3/`、`v2/`、`v1/`）；每个插件按 ID 建独立子目录，例如 `tests/v3/<plugin_id>/`，不要把用例文件直接平铺在代际目录下；插件独立目录内的测试文件名使用 `test_*.py`，不再重复插件名前缀。各仓脚手架以目标仓库现有实现为准，不要求跨仓机械相同。没有更近的仓库或目录级 `AGENTS.md` 时，以本基线为准。
- 插件仓 `pytest.ini` 应配置 `addopts = --import-mode=importlib`，避免不同插件独立目录内复用 `test_plugin.py` 等同名测试文件时触发 pytest 默认导入模式的模块名冲突。
- 插件单测统一使用 pytest 风格：普通测试函数或测试类均可，断言使用 `assert`；不要新增 `unittest.TestCase`、`unittest.main()` 或 `if __name__ == "__main__"` 测试入口。`unittest.mock` 可继续作为 mock 工具使用，“不用 unittest”指测试组织与执行入口不使用 unittest runner。
- 插件单测经 `tests/_bootstrap.py` 定位同级 `MoviePilot` 后端并注入 `sys.path`、隔离临时 `CONFIG_DIR` 并建表；`app/testing`（`stub_modules` 等）是主程序与插件仓**共享**的 stub harness，bootstrap 后可 `from app.testing import ...` 复用。不同代可能存在同名包，必须分独立 pytest 会话运行。
- 插件仓单测必须显式设置 `MOVIEPILOT_BACKEND_PATH=<workspace>/MoviePilot`，并使用 `<workspace>/.venv-test/bin/python` 运行，避免依赖当前目录层级推导后端路径。
- 默认按改动选择最小但可信的本地验证：后端运行受影响测试或 focused pytest，插件仓运行受影响代际/插件测试，前端代码改动运行 `typecheck`、`lint` 和仓库已有的 focused 测试，并执行 `git diff --check`。依赖或锁文件、共享测试脚手架、数据库、启动链、跨模块生命周期、兼容层、大范围行为改动，或用户明确要求本地全量时，才扩大到对应仓库全量：主程序在 `MoviePilot/` 跑 `<workspace>/.venv-test/bin/python tests/run.py`，插件仓跑 `MOVIEPILOT_BACKEND_PATH=<workspace>/MoviePilot <workspace>/.venv-test/bin/python tests/run.py`，由各仓 runner 按 V3、兼容 V2 和历史代际分组执行。PR 是否阻断交付由目标仓库的 required checks/Ruleset、平台真实限制和本次改动拥有的实质问题决定；普通 full regression、optional check 或 pending 自动化不自动成为门禁，本地全量也不是每次交付的重复门禁。
- 在有效源码、依赖锁、测试脚手架和环境边界未改变时复用已有验证；后续改动或非重叠 rebase 只重跑被具体变化失效的证据，不因 HEAD 变化机械重跑全部检查。纯文档、说明文本或局部 metadata 变更继续按实际风险使用更小的可复现检查。
- 前端改动至少验证 `typecheck`、`lint`；视觉行为按 `frontend-development` 验证实际渲染面。UI PR 不默认生成或附带截图，只有用户明确要求时才处理。

## External User Reports & Instance Boundaries
- 诊断前先标明被判断的实例、部署、镜像或版本以及相关时间窗口，并区分源码可达性、目标现场事实和实验室复现结果。
- 问题主体确认是当前本地实例且版本与时间窗口匹配时，本机日志、数据库、配置和运行态是合格证据，应按问题范围使用。
- 用户反馈来自外部或远程实例时，以用户时序和目标实例证据为现场事实；本工作区的日志、数据库、配置、备份、安装状态和运行时副本默认只描述本机。不要仅因本机材料可访问就先行检查，也不能用其存在、缺失、成功或失败确认或否定用户现场。
- 本地环境可用于明确设计的等价复现或源码假设验证，但必须记录版本、部署、挂载、配置、输入等价条件、已知差异和结论边界；结果应标记为实验室证据，不得改写成用户现场证据。
- 缺少必要目标证据时，保留未知或索取能解决当前判断的最小证据；源码和测试可以证明契约、兼容性和可达路径，不能单独证明用户实例实际发生过某事件。

## Full-Stack Runtime Verification
- 以下本地运行态规则只适用于当前本地实例或已声明边界的实验室复现；外部用户现场遵循上一节的证据归属规则。
- 涉及前后端联动、页面行为、插件 UI、登录态、接口契约或用户可见流程的任务，不要只停在静态检查；优先复用或启动可用服务，完成一次真实浏览器验证。
- 开始运行态验证前，先探测端口、进程、关键接口和日志，判断现有后端/前端服务是否可复用。后端通常在 `MoviePilot/` 中运行，启动命令为 `<workspace>/.venv/bin/python -m app.main`；前端通常在 `MoviePilot-Frontend/` 中运行 `yarn dev`。
- 如果探测到用户正在用 PyCharm debugger 或 PyCharm 终端运行服务，不要抢占重启；通过 API、日志、浏览器控制台、网络请求和 DOM/snapshot 做旁路验证。若后端停在断点，提示用户在 PyCharm 中继续/单步。
- PyCharm 终端中的 `yarn dev` stdout 通常不能直接读取；前端问题优先通过浏览器控制台、Vite 页面 overlay、网络请求、DOM/snapshot、`yarn typecheck`/`lint` 复现。若需要长期共享终端日志，建议将命令改为 `yarn dev 2>&1 | tee /tmp/moviepilot-frontend-dev.log` 或启用 PyCharm console output 保存到文件。
- 浏览器调试优先使用当前环境可用的 Browser / Chrome / CDP 工具连接本地页面或已有 Chrome：先列出页面，再导航、截屏、读取 DOM 或 accessibility snapshot、检查控制台/网络状态；必要时结合接口请求和后端日志定位问题。首次连接页面可能需要用户在 Chrome 上允许调试。
- 对 UI 修复的最低验证闭环：相关接口返回正常、页面无明显控制台错误、关键交互可完成，实际渲染状态与交互结果可复核。涉及响应式或布局的改动至少检查桌面与移动宽度。
- 对插件 UI 或模块联邦改动，还要验证远程组件加载、插件运行时副本、插件日志和前端网络请求，避免只改源码但运行时仍加载旧副本。

## Local Plugin Development & Debugging
- 以下市场、安装、同步、配置和日志检查只适用于当前本地实例或已声明边界的实验室复现，不是外部用户现场的默认取证顺序。
- 插件开发以 `MoviePilot-Plugins/plugins.v3/<plugin>/`、`MoviePilot-Plugins/plugins.v2/<plugin>/` 或 `MoviePilot-Plugins/plugins/<plugin>/` 为源码事实源；部分兼容历史版本的插件仍保留在旧代目录。优先通过 `PLUGIN_LOCAL_REPO_PATHS` 指向一个或多个本地插件仓库，让主项目按市场来源读取 package 索引并同步到运行时副本。
- 本地插件调试优先启用 `PLUGIN_AUTO_RELOAD=true`，需要暂停定时任务时再启用 `DEV=true`；修改本地仓库源码后，预期由本地插件同步机制更新 `MoviePilot/app/plugins/<plugin>/` 并触发热加载，不再把手动复制运行时副本作为默认步骤。
- 调试插件问题时，先确认本地插件是否在市场列表中出现、是否已安装、是否触发本地同步与热加载、配置是否已被插件读取，再判断业务逻辑本身；避免把本地仓库路径配置错误、运行时副本不同步、模块缓存未刷新误判为代码问题。
- 涉及插件配置时，确认配置是否被环境变量或旧配置字段影响；若主项目提示某配置已由环境变量设置，WebUI 修改可能不会改变实际运行行为。
- 服务列表或运行状态问题优先用后端接口验证实际状态，而不是只看前端表现。普通 WebUI 接口应复用浏览器登录态或 JWT 认证；只有源码明确标注 `API_TOKEN` 的诊断接口（如 `/api/v1/dashboard/schedule2` 这类 `*2` 接口）才使用 `?token=<API_TOKEN>` 访问，并且不得在聊天、PR、issue、日志摘录或截图中输出 token 原文。检查服务状态时重点核对 `id`、`name`、`provider`、`status` 是否重复或来源错误。
- 调试日志优先查看主日志 `MoviePilot/config/logs/moviepilot.log` 和插件日志目录 `MoviePilot/config/logs/plugins/`；过滤插件 ID/插件名、`plugin.py`、相关模块名、目标 job id 和关键中文服务名，确认加载、热加载、配置读取、注册、移除、执行、异常是否按预期发生。
- 插件代码或运行态改动的验证优先包括：`python -m py_compile` 对源码和运行时副本编译、`python -m json.tool` 校验本次涉及的 `package*.json`、`git diff --check`、旧配置字段/旧文案 `rg` 清理检查，以及一次本地同步、热加载日志或运行时接口验证。纯 README、索引说明、文案或 package metadata 改动按影响面选择 `json.tool`、链接/文本检查、`git diff --check` 等更小闭环即可。

## Local Secret and Operations Credential Contract
- `<workspace>/app.env` 可能包含运行凭据和私有配置；命令确需加载时只在受限子进程中 source，
  不得为了诊断读取或打印内容，不得提交、写入公共文本或拼进命令参数。测试必须继续隔离真实
  `CONFIG_DIR`。
- 本地浏览器登录和 SSH 登录统一使用 `$secure-access`；每个 profile 指定一个 1Password item 和明确字段，地址、用户名、密码或私钥在一次 item 读取中解析到内存。
- 浏览器 profile 使用本地 MoviePilot 登录 item 的 `username`/`password` 字段；SSH profile 使用主机、用户名和认证字段；NAS profile 的地址明确来自 item 顶层 `website` URL，并启用 `sudo`。`notesPlain` 不作为隐式地址或凭据兜底。
- `.ops/moviepilot/.login` 和 `.ops/moviepilot-server/.ssh` 是已退役的明文凭据位置，不得重新创建、提交、打印、截图或写入日志。新自动化不得支持 file provider、`usr`/`pwd` 历史键名或其他明文 fallback。
- 1Password secret value 只能由 `$secure-access` 在内存中读取；禁止通过命令行参数、环境变量、临时文件、shell trace 或日志传递 secret value。`op://...` item 引用属于非敏感配置，可以出现在本地 profile 和 agent 指令中。
- `$secure-access` 默认使用已安装的 machine provider，不要求当前终端预先完成 `op` app-integration 授权。只有用户明确要求显式授权，或 machine provider 失败且确认用户在场后，才在当前交互 PTY 以 `--provider interactive` 发起一次独立请求；不得自动弹出授权、循环重试或回退到本地凭据文件。

## Commit & Pull Request Guidelines
- 推荐 Conventional Commits：`feat(scope): ...`、`fix(scope): ...`、`chore: ...`、`refactor: ...`。
- Commit message 默认只写 subject（单行标题），使用英文撰写，不附 body/description；改动的"为什么、风险、回归点"放到 PR 描述里，不放进 commit message。
- MoviePilot 面向中文社区；PR 标题、PR 正文、issue/review 回复默认使用中文。仓库模板、目标上游或维护者对某次交付另有明确要求时，按该要求执行。
- PR 正文应用 `product-development` 的通用沟通契约并随风险调整深度：让不了解本地讨论的维护者直接看懂问题或目标、主要行为变化与验证；兼容、迁移、安全、跨仓依赖或剩余风险只在实际存在时展开，不固定六章节，不重复自动摘要或本地执行流水。
- 单次提交聚焦单一子仓/单一主题，避免混入无关改动。
- 已被 `.gitignore` 或仓库 ignore 规则显式忽略的文件视为本地或派生产物，默认不纳入 git，也不需要反复询问是否提交；只有维护者明确要求 version/force-add 时才处理。
- GitHub 操作默认先直接使用 `gh`
- commit、push、PR、release 权限以 `product-development`、适用的 `moviepilot-delivery` 路由、本轮用户明确授权、Goal/Task 或已批准 plan 边界为准；这些事实源已授权时不要二次确认，未授权时在对应外部动作前获得维护者确认。
- 上述 MoviePilot 产品代码仓本地开发、调试和测试使用 `moviepilot-development` skill；push、PR、merge 和发版使用 `moviepilot-delivery` skill。`MoviePilot-Skills` 明确排除。
- 插件 V3 专用改动进入 `plugins.v3/`，V1/V2 仅在明确要求兼容或维护历史实现时修改对应目录。
- 当前只维护 v3：主程序后端、前端与 Rust PR 目标为上游 `v3`，插件仓发布目标为 `main`。

## Official Wiki Alignment (Important)
以下约束以官方 Wiki 为准（`wiki.movie-pilot.org`）：
- 部署优先推荐 Docker；`/media` 挂载需与下载器/媒体服务器路径体系一致（硬链接场景必须同盘同根）。
- 配置优先级：环境变量 > `app.env`/WebUI；若已设置环境变量，WebUI 修改不会生效。
- `SUPERUSER`、`SUPERUSER_PASSWORD` 仅首次安装生效；V2 的 `API_TOKEN` 需至少 16 位复杂字符串。
- 本地插件开发可配置 `PLUGIN_LOCAL_REPO_PATHS` 指向本地插件仓库，并启用 `PLUGIN_AUTO_RELOAD=true`；仅开发调试时启用 `DEV=true`（会暂停定时任务）。
- `PLUGIN_MARKET` 仅支持 GitHub `main` 分支仓库，多个地址用逗号分隔。
