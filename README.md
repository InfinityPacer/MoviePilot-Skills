# MoviePilot Skills

MoviePilot 工作区的 Codex / Claude Code skill 与工作区指令事实源。先改本仓，通过验证后再同步安装副本。

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
| `moviepilot-development` | 开发、调试、跑测试请求的仓库路由 |
| `moviepilot-main-development` | `MoviePilot` 后端与 `MoviePilot-Frontend` 前端本地开发 |
| `moviepilot-plugin-development` | 个人插件仓与官方插件 fork 的本地开发、测试和热加载调试 |
| `moviepilot-delivery` | PR、发版、发布请求的仓库路由 |
| `moviepilot-upstream-pr` | `InfinityPacer/MoviePilot*` fork 到 `jxxghp/*:v3` 的上游 PR |
| `moviepilot-official-plugin-pr` | `MoviePilot-Plugins-Official` fork 到 `jxxghp/MoviePilot-Plugins:main` 的官方插件 PR |
| `moviepilot-plugin-delivery` | 个人插件仓 PR-only、发版、Auto-merge 和必要回查 |

## 验证

```bash
pytest -q
git diff --check
SKILL_CREATOR_DIR="${SKILL_CREATOR_DIR:?set skill-creator skill directory}"
python "${SKILL_CREATOR_DIR}/scripts/quick_validate.py" skills/moviepilot-development
python "${SKILL_CREATOR_DIR}/scripts/quick_validate.py" skills/moviepilot-main-development
python "${SKILL_CREATOR_DIR}/scripts/quick_validate.py" skills/moviepilot-plugin-development
python "${SKILL_CREATOR_DIR}/scripts/quick_validate.py" skills/moviepilot-delivery
python "${SKILL_CREATOR_DIR}/scripts/quick_validate.py" skills/moviepilot-upstream-pr
python "${SKILL_CREATOR_DIR}/scripts/quick_validate.py" skills/moviepilot-official-plugin-pr
python "${SKILL_CREATOR_DIR}/scripts/quick_validate.py" skills/moviepilot-plugin-delivery
```

## 同步

```bash
for skill in \
  moviepilot-development \
  moviepilot-main-development \
  moviepilot-plugin-development \
  moviepilot-delivery \
  moviepilot-upstream-pr \
  moviepilot-official-plugin-pr \
  moviepilot-plugin-delivery
do
  rsync -a --delete "skills/${skill}/" "${HOME}/.codex/skills/${skill}/"
  rsync -a --delete "skills/${skill}/" "${HOME}/.claude/skills/${skill}/"
  diff -qr "skills/${skill}" "${HOME}/.codex/skills/${skill}"
  diff -qr "skills/${skill}" "${HOME}/.claude/skills/${skill}"
done
```
