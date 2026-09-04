# MoviePilot Skills

MoviePilot 工作区的 Codex skill 与工作区指令事实源。先改本仓，通过验证后再同步安装副本。

## Workspace Instructions

`instructions/moviepilot-workspace.md` 由工作区根 `../AGENTS.md` 通过相对软链接加载。修改
MoviePilot 工作区规则时编辑本仓事实源，并验证软链接仍可读；不要在工作区根维护独立副本。
从本仓根目录恢复并校验入口：

```bash
test -L ../AGENTS.md || ln -s MoviePilot-Skills/instructions/moviepilot-workspace.md ../AGENTS.md
test "$(readlink ../AGENTS.md)" = "MoviePilot-Skills/instructions/moviepilot-workspace.md"
test -r ../AGENTS.md
```

若目标已是普通文件，`ln -s` 会拒绝覆盖；先人工核对并迁移其中仍有效的规则，不要强制替换。

## Skills

| Skill | 用途 |
| --- | --- |
| `moviepilot-development` | 后端、前端、Rust 与插件仓的本地开发、调试和测试边界 |
| `moviepilot-delivery` | fork-first 上游 PR、合并与个人插件 PR-only/发版终态 |

工作区指令负责通用产品生命周期和可见界面或交互验证。本仓两个 skill 只补充 MoviePilot 仓库、
运行态与交付路由，不重定义 Project、Goal、Task、授权、质量或完成语义。

稳定项目事实和测试命令由工作区或目标仓库 `AGENTS.md` 维护；skill 只保留触发、授权、路由和
非显然状态转换，避免复制易漂移的命令说明。

## 验证

```bash
pytest -q
git diff --check
SKILL_CREATOR_DIR="${SKILL_CREATOR_DIR:?set skill-creator skill directory}"
python "${SKILL_CREATOR_DIR}/scripts/quick_validate.py" skills/moviepilot-development
python "${SKILL_CREATOR_DIR}/scripts/quick_validate.py" skills/moviepilot-delivery
```

## 同步

`skill-catalog.json` 是本仓的同步事实源。使用个人 skill 仓库提供的通用同步工具，并显式传入本仓
catalog 和 source root。Codex 安装到工作区 `../.agents/skills`；两个 MoviePilot workflow skill
不进入用户级全局 skill 目录，也不再同步 Claude 副本。

```bash
SKILL_SYNC_TOOL="${SKILL_SYNC_TOOL:?set path to personal-agent-skills/tools/sync_skills.py}"
python3 "$SKILL_SYNC_TOOL" --catalog skill-catalog.json --source-root skills --target codex
python3 "$SKILL_SYNC_TOOL" --catalog skill-catalog.json --source-root skills --target codex --check
```

首次迁移到工作区 scope 时，将两个当前 skill 和五个退休名称的用户级全局目录移到 Trash，再
确认它们只在 MoviePilot 工作区暴露：

```bash
for skill in \
  moviepilot-development \
  moviepilot-delivery \
  moviepilot-main-development \
  moviepilot-plugin-development \
  moviepilot-upstream-pr \
  moviepilot-official-plugin-pr \
  moviepilot-plugin-delivery
do
  for root in "${HOME}/.codex/skills" "${HOME}/.claude/skills"
  do
    if [ -e "${root}/${skill}" ]; then
      /usr/bin/trash "${root}/${skill}"
    fi
  done
done
```

先完成工作区同步和 parity 检查再清理；该迁移可从 Trash 恢复。
