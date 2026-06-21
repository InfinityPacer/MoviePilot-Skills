"""验证 MoviePilot skills 的当前 workflow 边界和可执行命令安全性。"""

from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = REPO_ROOT / "skills"

EXPECTED_SKILLS = {
    "moviepilot-delivery",
    "moviepilot-development",
    "moviepilot-main-development",
    "moviepilot-plugin-development",
    "moviepilot-official-plugin-pr",
    "moviepilot-upstream-pr",
    "moviepilot-plugin-delivery",
}

EXECUTION_SKILLS = {
    "moviepilot-main-development",
    "moviepilot-plugin-development",
    "moviepilot-official-plugin-pr",
    "moviepilot-upstream-pr",
    "moviepilot-plugin-delivery",
}

DELIVERY_SKILLS = {
    "moviepilot-official-plugin-pr",
    "moviepilot-upstream-pr",
    "moviepilot-plugin-delivery",
}


def _read_skill(name: str) -> str:
    return (SKILLS_ROOT / name / "SKILL.md").read_text(encoding="utf-8")


def _bash_blocks(skill: str) -> list[str]:
    return re.findall(r"```bash\n(.*?)```", skill, flags=re.DOTALL)


def _frontmatter_name(skill: str) -> str:
    match = re.search(r"^---\nname: ([a-z0-9-]+)\n", skill)
    assert match, "missing skill frontmatter name"
    return match.group(1)


def test_skill_set_and_metadata_match_current_public_workflows() -> None:
    """仓库只暴露当前 7 个 skill，目录名、frontmatter 和 UI metadata 必须一致。"""
    names = {path.name for path in SKILLS_ROOT.iterdir() if path.is_dir()}

    assert names == EXPECTED_SKILLS
    for name in EXPECTED_SKILLS:
        skill = _read_skill(name)
        assert _frontmatter_name(skill) == name
        metadata = SKILLS_ROOT / name / "agents/openai.yaml"
        assert metadata.is_file(), metadata
        assert f"${name}" in metadata.read_text(encoding="utf-8")


def test_router_skills_only_route_and_do_not_execute_delivery_work() -> None:
    """路由 skill 只做分流，不复制提交、PR、issue 或验证命令。"""
    delivery = _read_skill("moviepilot-delivery")
    development = _read_skill("moviepilot-development")

    assert "moviepilot-upstream-pr" in delivery
    assert "moviepilot-plugin-delivery" in delivery
    assert "moviepilot-official-plugin-pr" in delivery
    assert "moviepilot-plugin-development" not in delivery
    assert "MoviePilot-Plugins" in delivery
    assert "MoviePilot-Plugins-Official" in delivery

    assert "moviepilot-main-development" in development
    assert "moviepilot-plugin-development" in development

    forbidden = (
        "gh pr create",
        "gh issue comment",
        "pytest",
        "check_plugin_versions.py",
        "Fixes #<number>",
        "Refs #<number>",
    )
    for router in (delivery, development):
        for text in forbidden:
            assert text not in router


def test_development_skills_stop_before_commit_push_or_pr() -> None:
    """开发 skill 负责本地开发验证，最终全量门禁和交付交给 PR/release skill。"""
    main = _read_skill("moviepilot-main-development")
    plugin = _read_skill("moviepilot-plugin-development")

    for skill in (main, plugin):
        assert "本 skill 不 commit、不 push、不创建 PR" in skill
        assert "gh pr create" not in skill
        assert "gh pr merge" not in skill
        assert "gh issue comment" not in skill

    assert "最终全量门禁由 `moviepilot-upstream-pr` 执行" in main
    assert "最终全量门禁由 `moviepilot-plugin-delivery` 或 `moviepilot-official-plugin-pr` 执行" in plugin
    assert "moviepilot-plugin-delivery" in plugin
    assert "moviepilot-official-plugin-pr" in plugin


def test_personal_plugin_delivery_has_two_terminal_paths() -> None:
    """个人插件交付同时覆盖 PR-only 与发版，且两条路径终止条件不同。"""
    skill = _read_skill("moviepilot-plugin-delivery")

    assert "InfinityPacer/MoviePilot-Plugins" in skill
    assert "PR-only" in skill
    assert "发版路径" in skill
    assert "不做版本升级、tag、GitHub Release 或发布回查" in skill
    assert "Plugin Release" in skill
    assert "tag" in skill
    assert "zip" in skill
    assert "--auto --squash" in skill
    assert "--match-head-commit" in skill
    assert "--delete-branch" not in skill
    assert "不得使用 `--admin`" in skill


def test_delivery_skills_cover_commit_push_pr_tracking_and_issue_reply() -> None:
    """三个交付 skill 都必须覆盖提交确认、PR 回读、issue 关联和回复边界。"""
    for name in DELIVERY_SKILLS:
        skill = _read_skill(name)

        assert "commit、push 前" in skill or "commit 或 push" in skill
        assert 'git push -u origin "${BRANCH}"' in skill
        assert "gh pr create" in skill
        assert "gh pr view" in skill
        assert "Fixes #<number>" in skill
        assert "Refs #<number>" in skill
        assert "完整 URL" in skill
        assert "默认使用 `Refs`" in skill
        assert "回复来源 Issue" in skill
        assert "gh issue comment" in skill
        assert "回读 issue" in skill
        assert "不得写“已完成”" in skill


def test_official_and_upstream_prs_do_not_auto_merge() -> None:
    """向 jxxghp 提交的 PR 只跟踪状态，不代替上游维护者合并。"""
    for name in ("moviepilot-official-plugin-pr", "moviepilot-upstream-pr"):
        skill = _read_skill(name)

        assert "不得启用 Auto-merge" in skill
        assert "gh pr merge" not in skill
        assert "--auto --squash" not in skill
        assert "--admin" not in skill

    official = _read_skill("moviepilot-official-plugin-pr")
    assert "jxxghp/MoviePilot-Plugins" in official
    assert "--base main" in official
    assert "不得运行个人仓自动合并或发布回查步骤" in official

    upstream = _read_skill("moviepilot-upstream-pr")
    assert "jxxghp/MoviePilot" in upstream
    assert "jxxghp/MoviePilot-Frontend" in upstream
    assert "--base v2" in upstream


def test_workspace_env_file_is_loaded_safely_and_config_dir_is_cleared() -> None:
    """执行型 skill 可 source 工作区 app.env，但不能读取内容，单测必须清 CONFIG_DIR。"""
    for name in EXECUTION_SKILLS:
        skill = _read_skill(name)

        assert "<workspace>/app.env" in skill
        assert "set -a" in skill
        assert '. "${WORKSPACE}/app.env"' in skill
        assert "set +a" in skill
        assert "env -u CONFIG_DIR" in skill
        assert "不要把 env-file 内容拼进命令参数" in skill
        assert "不得读取" in skill
        assert "CONFIG_DIR" in skill
        assert "MOVIEPILOT_BACKEND_PATH=<workspace>/MoviePilot" not in skill


def test_plugin_test_commands_map_to_clear_scenarios() -> None:
    """插件测试命令按场景选择，并显式覆盖 base-ref、A 档覆盖率和 v1/v2 编译路径。"""
    for name in ("moviepilot-plugin-development", "moviepilot-plugin-delivery", "moviepilot-official-plugin-pr"):
        skill = _read_skill(name)

        assert "局部插件测试" in skill
        assert "全量回归" in skill
        assert "新增插件目录" in skill
        assert "基础文件检查" in skill
        assert "PLUGIN_KIND=v2" in skill
        assert 'PLUGIN_DIR="plugins.${PLUGIN_KIND}/${PLUGIN_ID}"' in skill
        assert 'PLUGIN_DIR="plugins/${PLUGIN_ID}"' in skill
        assert 'python -m compileall -q "${PLUGIN_DIR}"' in skill

    personal = _read_skill("moviepilot-plugin-delivery")
    assert "scripts/plugin_coverage.py --base-ref ${BASE_REF}" in personal
    assert "scripts/check_new_plugin_tests.py --base-ref origin/main" in personal
    basic_check_blocks = [
        block for block in _bash_blocks(personal) if "python -m json.tool package.json" in block
    ]
    assert basic_check_blocks
    assert all("check_new_plugin_tests.py" not in block for block in basic_check_blocks)
    assert "plugin_quality.json" in personal
    assert "新增插件只先进入最低测试目录门禁" in personal
    assert "不自动进入 A 档覆盖率门禁" in personal
    assert "不能替代 `tests/ci`、非 A 档插件测试或需要全量回归的" in personal


def test_executable_bash_blocks_are_copy_safe() -> None:
    """bash 代码块不得放危险占位符或绕过保护的参数。"""
    for skill_path in sorted(SKILLS_ROOT.glob("*/SKILL.md")):
        skill = skill_path.read_text(encoding="utf-8")
        for block in _bash_blocks(skill):
            assert "<" not in block, f"{skill_path} contains shell-unsafe placeholder in:\n{block}"
            assert "--admin" not in block, f"{skill_path} contains --admin in executable block:\n{block}"
            assert "--no-verify" not in block, f"{skill_path} contains --no-verify in executable block:\n{block}"


def test_readme_sync_is_idempotent_and_deletes_stale_installed_files() -> None:
    """README 的同步命令必须能重复执行并删除安装副本中的陈旧文件。"""
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    assert "rsync" in readme
    assert "--delete" in readme
    assert "cp -R" not in readme
