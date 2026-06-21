# MoviePilot Skills

MoviePilot 工作区的 Codex / Claude Code skill 事实源。先改本仓，通过验证后再同步安装副本。

## Skills

| Skill | 用途 |
| --- | --- |
| `moviepilot-development` | 开发、调试、跑测试请求的仓库路由 |
| `moviepilot-main-development` | `MoviePilot` 后端与 `MoviePilot-Frontend` 前端本地开发 |
| `moviepilot-plugin-development` | 个人插件仓与官方插件 fork 的本地开发、测试和热加载调试 |
| `moviepilot-delivery` | PR、发版、发布请求的仓库路由 |
| `moviepilot-upstream-pr` | `InfinityPacer/MoviePilot*` fork 到 `jxxghp/*:v2` 的上游 PR |
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
