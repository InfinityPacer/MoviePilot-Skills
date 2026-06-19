"""验证 MoviePilot 交付技能的结构、触发边界和关键安全约束。"""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = REPO_ROOT / "skills"


def _read_skill(name: str) -> str:
    """读取指定 skill，缺失时让 pytest 以明确路径失败。"""
    return (SKILLS_ROOT / name / "SKILL.md").read_text(encoding="utf-8")


def test_repository_contains_development_and_delivery_skills() -> None:
    """技能仓必须维护开发入口、交付入口和各仓库专用执行流程。"""
    names = {path.name for path in SKILLS_ROOT.iterdir() if path.is_dir()}

    assert names == {
        "moviepilot-delivery",
        "moviepilot-development",
        "moviepilot-main-development",
        "moviepilot-plugin-development",
        "moviepilot-official-plugin-pr",
        "moviepilot-upstream-pr",
        "moviepilot-plugin-release",
    }


def test_delivery_skill_routes_by_repository_without_duplicating_workflows() -> None:
    """模糊的“PR/发版”请求必须按当前仓库转交专用 skill。"""
    skill = _read_skill("moviepilot-delivery")

    assert "MoviePilot-Frontend" in skill
    assert "MoviePilot-Plugins" in skill
    assert "MoviePilot-Plugins-Official" in skill
    assert "moviepilot-upstream-pr" in skill
    assert "moviepilot-plugin-release" in skill
    assert "moviepilot-official-plugin-pr" in skill
    assert "先检查当前仓库" in skill
    assert "gh pr create" not in skill
    assert "check_plugin_versions.py" not in skill


def test_development_router_routes_without_duplicating_workflows() -> None:
    """开发路由只选择主程序/插件开发流程，不承载具体分支与测试命令。"""
    skill = _read_skill("moviepilot-development")

    assert "MoviePilot-Frontend" in skill
    assert "MoviePilot-Plugins" in skill
    assert "MoviePilot-Plugins-Official" in skill
    assert "moviepilot-main-development" in skill
    assert "moviepilot-plugin-development" in skill
    assert "先检查当前仓库" in skill
    assert "git checkout -b" not in skill
    assert "pytest" not in skill


def test_main_development_skill_separates_runtime_env_from_test_isolation() -> None:
    """主程序开发必须区分 Docker-style 运行态 env-file 与单测隔离环境。"""
    skill = _read_skill("moviepilot-main-development")

    assert "upstream/v2" in skill
    assert "MoviePilot-Frontend" in skill
    assert "Docker-style env-file" in skill
    assert "<workspace>/app.env" in skill
    assert "不得读取 env-file 内容" in skill
    assert "不得打印、提交、复制" in skill
    assert "当前 env-file 不应包含" not in skill
    assert "env -u CONFIG_DIR" in skill
    assert ".venv-test/bin/python tests/run.py" in skill
    assert "moviepilot-upstream-pr" in skill


def test_plugin_development_skill_handles_personal_and_official_repositories() -> None:
    """插件开发必须按 remote 分流个人插件仓和官方插件 fork。"""
    skill = _read_skill("moviepilot-plugin-development")

    assert "InfinityPacer/MoviePilot-Plugins" in skill
    assert "MoviePilot-Plugins-Official" in skill
    assert "jxxghp/MoviePilot-Plugins" in skill
    assert "origin/main" in skill
    assert "upstream/main" in skill
    assert "MOVIEPILOT_BACKEND_PATH=<workspace>/MoviePilot" in skill
    assert "env -u CONFIG_DIR" in skill
    assert "PLUGIN_LOCAL_REPO_PATHS" in skill
    assert "moviepilot-plugin-release" in skill
    assert "moviepilot-official-plugin-pr" in skill


def test_branch_names_match_task_type_and_reserve_release_prefix() -> None:
    """非发版流程必须使用任务类型命名，release 前缀只留给真实发版。"""
    generic_branch_skills = (
        "moviepilot-main-development",
        "moviepilot-plugin-development",
        "moviepilot-upstream-pr",
        "moviepilot-official-plugin-pr",
    )

    for name in generic_branch_skills:
        skill = _read_skill(name)

        assert "codex/<type>/<topic>" in skill
        assert "claude/<type>/<topic>" in skill
        assert "codex/release/" not in skill
        assert "claude/release/" not in skill

    delivery = _read_skill("moviepilot-delivery")
    assert "发版、发布插件、版本升级、插件 PR" not in delivery
    assert "非发版插件 PR" in delivery

    release = _read_skill("moviepilot-plugin-release")
    assert "preparing a pull request" not in release
    assert "普通维护、CI、文档或非版本发布 PR 不使用本 skill" in release
    assert "codex/release/<plugin>-<version>" in release
    assert "claude/release/<plugin>-<version>" in release


def test_official_plugin_pr_skill_targets_upstream_main_without_release_flow() -> None:
    """官方插件仓 PR 流程必须面向 jxxghp/main，且不得执行个人仓发版动作。"""
    skill = _read_skill("moviepilot-official-plugin-pr")

    assert "MoviePilot-Plugins-Official" in skill
    assert "jxxghp/MoviePilot-Plugins" in skill
    assert "upstream/main" in skill
    assert "origin" in skill
    assert "--base main" in skill
    assert "--head InfinityPacer:" in skill
    assert "Plugin release gate" in skill
    assert "不得启用 Auto-merge" in skill
    assert "不得运行个人仓自动合并或发布回查步骤" in skill
    for forbidden in ("--auto --squash", "gh pr merge", "--admin", "GitHub Release", "Plugin Release", "Release workflow"):
        assert forbidden not in skill


def test_upstream_skill_targets_forks_and_never_auto_merges() -> None:
    """主程序 skill 必须面向 jxxghp/v2，并将合并权留给上游维护者。"""
    skill = _read_skill("moviepilot-upstream-pr")

    assert "jxxghp/MoviePilot" in skill
    assert "jxxghp/MoviePilot-Frontend" in skill
    assert "upstream" in skill
    assert "v2" in skill
    assert "env -u CONFIG_DIR" in skill
    assert "不得启用 Auto-merge" in skill
    assert "commit、push 前" in skill


def test_plugin_skill_keeps_release_and_auto_merge_closure() -> None:
    """插件 skill 必须保留自有仓自动合并与 Release 回查闭环。"""
    skill = _read_skill("moviepilot-plugin-release")

    assert "InfinityPacer/MoviePilot-Plugins" in skill
    assert "env -u CONFIG_DIR" in skill
    assert "Plugin release gate" in skill
    assert "--auto --squash" in skill
    assert "--delete-branch" not in skill
    assert "GitHub Release" in skill
    assert "commit 或 push" in skill


def test_plugin_skill_syncs_local_main_after_merge_and_keeps_branch() -> None:
    """插件 PR 合并后必须同步本地 main，默认保留合并分支。"""
    skill = _read_skill("moviepilot-plugin-release")

    assert "git checkout main" in skill
    assert "git pull --ff-only origin main" in skill
    assert "默认保留本地和远程合并分支" in skill


def test_execution_skills_handle_issue_links_without_accidental_closure() -> None:
    """Issue 来源的改动必须正确关联，且不确定时不得擅自自动关闭。"""
    for name in ("moviepilot-upstream-pr", "moviepilot-plugin-release"):
        skill = _read_skill(name)

        assert "Fixes #<number>" in skill
        assert "Refs #<number>" in skill
        assert "完整 URL" in skill
        assert "默认使用 `Refs`" in skill
        assert "回读 PR" in skill


def test_delivery_router_does_not_duplicate_issue_link_policy() -> None:
    """路由 skill 只负责选流程，不维护 issue 关闭语义。"""
    skill = _read_skill("moviepilot-delivery")

    assert "Fixes #<number>" not in skill
    assert "Refs #<number>" not in skill


def test_upstream_skill_replies_to_issue_before_and_after_delivery() -> None:
    """上游 PR 无法自行完成合并，必须区分 PR 已提交与结果已完成。"""
    skill = _read_skill("moviepilot-upstream-pr")

    assert "PR 创建后回复 issue" in skill
    assert "已提交 PR" in skill
    assert "不得写“已完成”" in skill
    assert "合并或发布后" in skill
    assert "gh issue comment" in skill
    assert "--body-file" in skill
    assert "回读 issue" in skill
    assert "使用 `Refs`" in skill
    assert "不主动关闭" in skill


def test_plugin_release_replies_once_unless_delivery_is_blocked() -> None:
    """快速自动发布默认只回最终结果，阻塞或需介入时才先发进度。"""
    skill = _read_skill("moviepilot-plugin-release")

    assert "默认只在 PR 合并且 GitHub Release 成功后回复一次最终结果" in skill
    assert "Required Check、合并或 Release 被阻塞" in skill
    assert "需要维护者操作、补充信息或做出决定" in skill
    assert "用户明确要求在 PR 创建后立即同步" in skill
    assert "gh issue comment" in skill
    assert "--body-file" in skill
    assert "回读 issue" in skill
    assert "不主动关闭" in skill


def test_delivery_router_does_not_duplicate_issue_reply_workflow() -> None:
    """路由 skill 不承载 issue 回帖命令和交付状态措辞。"""
    skill = _read_skill("moviepilot-delivery")

    assert "gh issue comment" not in skill
    assert "PR 创建后回复 issue" not in skill


def test_every_skill_has_codex_metadata() -> None:
    """每个 skill 都必须提供 Codex UI 元数据。"""
    for name in (
        "moviepilot-delivery",
        "moviepilot-development",
        "moviepilot-main-development",
        "moviepilot-plugin-development",
        "moviepilot-official-plugin-pr",
        "moviepilot-upstream-pr",
        "moviepilot-plugin-release",
    ):
        metadata = SKILLS_ROOT / name / "agents/openai.yaml"
        assert metadata.is_file(), metadata
        assert f"${name}" in metadata.read_text(encoding="utf-8")
