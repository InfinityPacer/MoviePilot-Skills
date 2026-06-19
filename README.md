# MoviePilot Skills

MoviePilot 工作区的代理开发与交付流程事实源。

## Skills

- `moviepilot-development`：根据当前子仓和“开发/调试/跑测试”等自然语言请求选择专用开发 skill。
- `moviepilot-main-development`：处理 `MoviePilot` 后端与 `MoviePilot-Frontend` 前端的本地开发、测试和运行态调试。
- `moviepilot-plugin-development`：处理个人插件仓与官方插件仓 fork 的本地开发、测试、分支和热加载调试。
- `moviepilot-delivery`：根据当前子仓和“PR/发版”等自然语言请求选择专用交付 skill。
- `moviepilot-upstream-pr`：将 `MoviePilot` 或 `MoviePilot-Frontend` fork 的改动提交到
  `jxxghp/*:v2`。
- `moviepilot-official-plugin-pr`：将 `MoviePilot-Plugins-Official` fork 的改动提交到
  `jxxghp/MoviePilot-Plugins:main`。
- `moviepilot-plugin-release`：通过插件仓 PR 门禁、Auto-merge 和 GitHub Release 完成发版。

## 验证

```bash
pytest
python <skill-creator>/scripts/quick_validate.py skills/moviepilot-development
python <skill-creator>/scripts/quick_validate.py skills/moviepilot-main-development
python <skill-creator>/scripts/quick_validate.py skills/moviepilot-plugin-development
python <skill-creator>/scripts/quick_validate.py skills/moviepilot-delivery
python <skill-creator>/scripts/quick_validate.py skills/moviepilot-upstream-pr
python <skill-creator>/scripts/quick_validate.py skills/moviepilot-official-plugin-pr
python <skill-creator>/scripts/quick_validate.py skills/moviepilot-plugin-release
```

## 安装

将 `skills/<skill-name>` 同步到 Codex 和 Claude Code 的个人技能目录：

```text
~/.codex/skills/<skill-name>
~/.claude/skills/<skill-name>
```

修改流程时先更新本仓，再同步安装副本；不要在业务仓维护第二份 skill。
