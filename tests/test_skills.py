"""验证 MoviePilot skills 的当前 workflow 边界和可执行命令安全性。"""

from __future__ import annotations

import re
import subprocess
import tempfile
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


def test_no_stale_plugin_release_skill_references() -> None:
    """MoviePilot skill source must use the current plugin delivery skill name."""
    # Keep the stale name split so repository-wide stale-name scans stay signal-bearing.
    stale_skill = "moviepilot-plugin-" "release"
    current_skill = "moviepilot-plugin-delivery"
    checked_files = [
        REPO_ROOT / "README.md",
        *sorted(SKILLS_ROOT.glob("*/SKILL.md")),
        *sorted(SKILLS_ROOT.glob("*/agents/openai.yaml")),
    ]

    for path in checked_files:
        text = path.read_text(encoding="utf-8")
        assert stale_skill not in text, path

    routing_files = {
        REPO_ROOT / "README.md",
        SKILLS_ROOT / "moviepilot-delivery" / "SKILL.md",
        SKILLS_ROOT / "moviepilot-plugin-development" / "SKILL.md",
        SKILLS_ROOT / "moviepilot-plugin-delivery" / "SKILL.md",
    }
    for path in routing_files:
        assert current_skill in path.read_text(encoding="utf-8"), path


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


def test_development_skills_allow_authorized_local_commits_but_stop_before_delivery() -> None:
    """开发 skill 可按通用 workflow 本地提交，但外部交付仍转 delivery skill。"""
    main = _read_skill("moviepilot-main-development")
    plugin = _read_skill("moviepilot-plugin-development")

    for skill in (main, plugin):
        assert "本地 commit 服从当前 `dev-workflow`、已批准计划或用户授权" in skill
        assert "不 push、不创建 PR" in skill
        assert "gh pr create" not in skill
        assert "gh pr merge" not in skill
        assert "gh issue comment" not in skill

    assert "最终全量门禁由 `moviepilot-upstream-pr` 执行" in main
    assert "最终全量门禁由 `moviepilot-plugin-delivery` 或 `moviepilot-official-plugin-pr` 执行" in plugin
    assert "moviepilot-plugin-delivery" in plugin
    assert "moviepilot-official-plugin-pr" in plugin


def test_development_skills_classify_existing_changes_and_use_business_branches() -> None:
    """开发 skill 先判断已有改动归属，只有无法安全隔离时才询问。"""
    for name in ("moviepilot-main-development", "moviepilot-plugin-development"):
        skill = _read_skill(name)

        assert "开始任务前先判断工作区状态和改动归属" in skill
        assert "当前任务改动继续保留" in skill
        assert "无关改动不得混入、reset、stash" in skill
        assert "只有归属不明、修改范围重叠或无法" in skill
        assert "安全隔离时才询问用户" in skill
        assert "根据用户目标和业务语义创建或选择分支" in skill
        assert "分支名与业务语义不一致" in skill
        assert "创建" in skill
        assert "新的业务分支" in skill


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


def test_personal_plugin_delivery_branch_names_follow_business_semantics() -> None:
    """插件交付分支名必须表达业务主题，不因发版闭环强制改成 release。"""
    skill = _read_skill("moviepilot-plugin-delivery")

    assert "分支名必须先跟随本次交付的业务主题" in skill
    assert "不要仅因为进入发版闭环而改名" in skill
    assert "只有当前在 `main`/`master`、分支主题与" in skill
    assert "本次交付业务不一致、或提交范围不干净时" in skill
    assert "只有发布流程本身就是业务主题时，才使用 `release` 前缀" in skill
    assert "不要把普通 bugfix、docs、test 或" in skill
    assert "CI 修复分支仅因最后要发版而改成 `release`" in skill
    assert 'BRANCH="codex/${TASK_TYPE}/${PLUGIN_ID}-topic"' in skill
    assert "claude/${TASK_TYPE}/${PLUGIN_ID}-topic" in skill
    assert 'BRANCH="codex/release/${PLUGIN_ID}-${VERSION}"' in skill


def test_delivery_skills_cover_commit_push_pr_tracking_and_issue_reply() -> None:
    """三个交付 skill 都必须覆盖提交确认、PR 回读、issue 关联和回复边界。"""
    for name in DELIVERY_SKILLS:
        skill = _read_skill(name)

        assert "本地 commit 服从当前 `dev-workflow`、已批准计划或本轮用户授权" in skill
        assert "已有授权时直接执行，不重复确认" in skill
        assert "独立的外部交付边界" in skill
        assert 'git push -u origin "${BRANCH}"' in skill
        assert "gh pr create" in skill
        assert "gh pr view" in skill
        assert "Fixes #<number>" in skill
        assert "Refs #<number>" in skill
        assert "完整 URL" in skill
        assert "部分处理或背景关联" in skill
        assert "回复来源 Issue" in skill
        assert "gh issue comment" in skill
        assert "回读 issue" in skill
        assert "不得写“已完成”" in skill


def test_delivery_skills_require_maintainer_facing_pr_context() -> None:
    """三个交付 skill 组合通用契约，只保留 MoviePilot 专项正文边界。"""
    for name in DELIVERY_SKILLS:
        skill = _read_skill(name)

        assert "PR 标题、正文和 issue 回复默认使用中文" in skill
        assert "commit subject 使用英文 Conventional Commit" in skill
        assert "应用 `dev-workflow` 的通用 PR 沟通与隐私契约" in skill
        assert "不复制" in skill
        assert "固定章节模板" in skill
        assert "正文深度随改动风险调整" in skill
        assert "不能用测试或" in skill
        assert "掩盖生产行为变化" in skill
        assert "不要重复自动生成的 PR 摘要" in skill
        assert "## 问题与背景" not in skill
        assert "## 影响与风险" not in skill

    upstream = _read_skill("moviepilot-upstream-pr")
    official = _read_skill("moviepilot-official-plugin-pr")
    personal = _read_skill("moviepilot-plugin-delivery")
    assert "fork/upstream 边界、`v3` 目标" in upstream
    assert "官方插件 fork、`upstream/main`" in official
    assert "个人插件仓、门禁、Auto-merge 与 release 终态" in personal
    assert "无需为了模板主动列出这些“未做事项”" in personal


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
    assert "--base v3" in upstream


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


def test_upstream_backend_pylint_uses_workspace_test_venv() -> None:
    """后端 PR 门禁的 Pylint 必须使用工作区测试环境，避免依赖外部 PATH。"""
    skill = _read_skill("moviepilot-upstream-pr")

    assert 'env -u CONFIG_DIR "${WORKSPACE}/.venv-test/bin/python" -m pylint app' in skill
    assert "\npylint app\n" not in skill


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


def test_workspace_instruction_source_is_versioned_and_documents_the_runtime_link() -> None:
    """MoviePilot 工作区规则必须由本仓事实源和工作区软链接加载。"""
    source = REPO_ROOT / "instructions/moviepilot-workspace.md"
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    assert source.is_file()
    text = source.read_text(encoding="utf-8")
    assert "MoviePilot 面向中文社区" in text
    assert "PR 标题、PR 正文、issue/review 回复默认使用中文" in text
    assert "Commit message 默认只写 subject" in text
    assert "使用英文撰写" in text
    assert "Goal 或已批准 plan 边界" in text
    assert "ledger 或 plan" not in text
    assert "instructions/moviepilot-workspace.md" in readme
    assert "../AGENTS.md" in readme
    assert "相对软链接" in readme
    assert "MoviePilot-Skills/instructions/moviepilot-workspace.md" in readme
    assert "readlink ../AGENTS.md" in readme
    assert "test -L ../AGENTS.md || ln -s " in readme
    assert "ln -sfn" not in readme
    assert "普通文件" in readme
    assert "拒绝覆盖" in readme
    assert "没有更近的仓库或目录级 `AGENTS.md` 时" in text
    assert "插件仓自身无 `AGENTS.md`" not in text
    assert "## Delivery Hygiene" not in text
    tracked = subprocess.run(
        ["git", "ls-files", "--error-unmatch", "instructions/moviepilot-workspace.md"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert tracked.returncode == 0, "workspace instruction source must be tracked by git"


def test_workspace_link_command_refuses_to_replace_a_regular_file() -> None:
    """恢复工作区入口时不得覆盖已有本地规则文件。"""
    with tempfile.TemporaryDirectory() as temp_dir:
        workspace = Path(temp_dir)
        skill_repo = workspace / "MoviePilot-Skills"
        skill_repo.mkdir()
        target = workspace / "AGENTS.md"
        target.write_text("local rules\n", encoding="utf-8")

        result = subprocess.run(
            [
                "sh",
                "-c",
                "test -L ../AGENTS.md || "
                "ln -s MoviePilot-Skills/instructions/moviepilot-workspace.md ../AGENTS.md",
            ],
            cwd=skill_repo,
            check=False,
            capture_output=True,
            text=True,
        )

        assert result.returncode != 0
        assert not target.is_symlink()
        assert target.read_text(encoding="utf-8") == "local rules\n"
