# MoviePilot Skills

MoviePilot 工作区的代理交付流程事实源。

## Skills

- `moviepilot-delivery`：根据当前子仓和“PR/发版”等自然语言请求选择专用 skill。
- `moviepilot-upstream-pr`：将 `MoviePilot` 或 `MoviePilot-Frontend` fork 的改动提交到
  `jxxghp/*:v2`。
- `moviepilot-plugin-release`：通过插件仓 PR 门禁、Auto-merge 和 GitHub Release 完成发版。

## 验证

```bash
pytest
python <skill-creator>/scripts/quick_validate.py skills/moviepilot-upstream-pr
python <skill-creator>/scripts/quick_validate.py skills/moviepilot-plugin-release
```

## 安装

将 `skills/<skill-name>` 同步到 Codex 和 Claude Code 的个人技能目录：

```text
~/.codex/skills/<skill-name>
~/.claude/skills/<skill-name>
```

修改流程时先更新本仓，再同步安装副本；不要在业务仓维护第二份 skill。
