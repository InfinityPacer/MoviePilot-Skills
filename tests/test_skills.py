"""验证 MoviePilot skill 的精简结构、交付边界和安装迁移契约。"""

from __future__ import annotations

import json
import re
import subprocess
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = REPO_ROOT / "skills"
EXPECTED_SKILLS = {"moviepilot-development", "moviepilot-delivery"}
RETIRED_SKILLS = {
    "moviepilot-main-development",
    "moviepilot-plugin-development",
    "moviepilot-upstream-pr",
    "moviepilot-official-plugin-pr",
    "moviepilot-plugin-delivery",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _skill(name: str) -> str:
    return _read(SKILLS_ROOT / name / "SKILL.md")


def _bash_blocks(text: str) -> list[str]:
    return re.findall(r"```bash\n(.*?)```", text, flags=re.DOTALL)


def test_source_exposes_only_two_complete_entrypoints() -> None:
    names = {path.name for path in SKILLS_ROOT.iterdir() if path.is_dir()}

    assert names == EXPECTED_SKILLS
    for name in EXPECTED_SKILLS:
        skill = _skill(name)
        assert re.search(rf"^---\nname: {name}\n", skill)
        metadata = SKILLS_ROOT / name / "agents/openai.yaml"
        assert metadata.is_file()
        assert f"${name}" in _read(metadata)


def test_skill_surface_uses_progressive_disclosure() -> None:
    markdown = sorted(SKILLS_ROOT.glob("**/*.md"))
    entrypoints = sorted(SKILLS_ROOT.glob("*/SKILL.md"))
    references = sorted(SKILLS_ROOT.glob("*/references/*.md"))

    assert {path.name for path in references} == {
        "personal-plugin.md",
        "upstream-pr.md",
    }
    assert len(entrypoints) == 2
    assert set(markdown) == {*entrypoints, *references}
    assert all(not _read(path).startswith("---\n") for path in references)

    delivery = _skill("moviepilot-delivery")
    for path in references:
        relative = path.relative_to(SKILLS_ROOT / "moviepilot-delivery")
        assert f"]({relative.as_posix()})" in delivery


def test_development_routes_workspace_evidence_only_when_relevant() -> None:
    development = _skill("moviepilot-development")

    for repository in (
        "`MoviePilot`",
        "`MoviePilot-Frontend`",
        "`MoviePilot-Rust`",
        "Wiki、Resources、Server",
        "维护中的\n私有 MoviePilot 上游目标",
        "个人插件仓",
        "官方插件 fork",
    ):
        assert repository in development
    assert "工作区 `AGENTS.md`" in development
    assert "本 skill 不复制" in development
    assert "确认当前仓库、目标文件和工作树" in development
    assert "只有任务\n需要识别权威基线、交付路由或处理已知基线漂移时才检查 remote" in development
    assert "不因本 skill 被调用就检查 remote、刷新\n  base、计算 merge-base 或探测运行态" in development
    assert "纯源码、测试、文档和静态配置改动不把本机服务状态当作独立前置检查" in development
    assert "只有权威 base 是否漂移会影响当前实现\n  或交付准备时" in development
    assert "才按 remote URL 刷新 base" in development
    assert "只有任务需要运行态诊断或验收、静态证据不足，或者端口/进程冲突影响当前下一步时" in development
    assert "现有运行态不是普通开发的独立证据门" in development
    assert "组合根、canonical package ownership 和依赖装配是任务相关的架构不变量" in development
    assert "不对普通局部改动另做\n  所有权审计" in development
    assert "保留有效工作并迁移" in development
    assert "本 skill 不 push、不创建 PR、不 merge" in development
    assert "moviepilot-delivery" in development
    assert not _bash_blocks(development)


def test_delivery_reuses_stable_capability_but_keeps_authorization_separate() -> None:
    delivery = _skill("moviepilot-delivery")

    assert "账户能力不构成当前任务授权" in delivery
    assert "github-maintainer-context.md" in delivery
    assert "直接复用" in delivery
    assert "不在每个 PR 前查询 `viewerPermission`" in delivery
    assert "重查遵循 `dev-workflow`" in delivery
    assert "fork-first" in delivery
    assert "不允许直接 push 默认分支" in delivery
    assert "force push 只有维护者明确授权" in delivery
    assert "以下判断只适用于 `jxxghp/*` 上游路由" in delivery
    assert "个人插件路径服从 `personal-plugin.md` 的独立门禁" in delivery
    assert "普通 CI 和 Review 状态只是交付信号" in delivery
    assert "不因名称、颜色或来源自动成为门禁" in delivery
    assert "未被其加重或重新触达的 base/上游既有问题" in delivery
    assert "不可操作的 Review 反馈" in delivery
    assert "无需再次询问维护者" in delivery
    assert "平台实际阻止正常 merge" in delivery


def test_upstream_pr_is_fork_first_and_explicitly_merged_after_signal_triage() -> None:
    upstream = _read(
        SKILLS_ROOT / "moviepilot-delivery/references/upstream-pr.md"
    )

    assert "`InfinityPacer/*` fork" in upstream
    assert "`jxxghp/*`" in upstream
    assert "topic branch" in upstream
    assert "active Ruleset、branch protection、required checks/reviews" in upstream
    assert "只等待平台真正要求" in upstream
    assert "可能实质改变当前 PR 合并判断" in upstream
    assert "未被其加重或重新触达的 base/上游既有问题" in upstream
    assert "不修复、不等待" in upstream
    assert "无需再次询问维护者" in upstream
    assert "平台允许正常 merge" in upstream
    assert "本次改动造成的未解决实质问题" in upstream
    assert "显式 merge" in upstream
    assert "head SHA" in upstream
    assert "不要启用 Auto-merge" in upstream
    assert "不用 `--admin`" in upstream
    assert "明确权限拒绝" in upstream
    assert "PR 创建并回读才是" in upstream
    assert "相互链接，说明兼容关系与必要合并顺序" in upstream
    assert "不进入个人插件发布流程" in upstream


def test_personal_plugin_preserves_pr_only_and_release_terminal_states() -> None:
    personal = _read(
        SKILLS_ROOT / "moviepilot-delivery/references/personal-plugin.md"
    )
    compact_personal = personal.replace("\n", "")

    assert "`InfinityPacer/MoviePilot-Plugins`" in personal
    assert "PR-only" in personal
    assert "不升级版本，不创建 tag 或 Release" in personal
    assert "当前发布 workflow" in personal
    assert "预期 tag 指向该 merged commit" in personal
    assert "Release 与发布资产" in personal
    assert "按 remote URL 识别的自有仓最新默认分支" in personal
    assert "源码版本、市场 metadata 和发布说明一致" in personal
    assert "active Ruleset、仓库 merge/Auto-merge 设置" in personal
    assert "只对本次已核对 PR 使用 Ruleset 允许的 merge 方法" in personal
    assert "带 head SHA 约束的 Auto-merge" in personal
    assert "不得扫描其他 PR" in personal
    assert "不用 `--admin`" in personal
    assert "不覆盖用户自定义\n  hook" in personal
    assert "不绕过门禁" in personal
    assert "Required Check 未出现时作为治理阻塞" in personal
    assert "不在普通交付中创建或修改 Ruleset" in compact_personal

    delivery = _skill("moviepilot-delivery")
    assert "个人插件路径服从 `personal-plugin.md` 的独立门禁" in delivery


def test_issue_linkage_progress_and_final_reply_contract_is_preserved() -> None:
    delivery = _skill("moviepilot-delivery")
    compact_delivery = delivery.replace("\n", "")
    upstream = _read(
        SKILLS_ROOT / "moviepilot-delivery/references/upstream-pr.md"
    )
    personal = _read(
        SKILLS_ROOT / "moviepilot-delivery/references/personal-plugin.md"
    )

    assert "使用 `Fixes`" in delivery
    assert "使用 `Refs`" in delivery
    assert "跨仓使用完整 URL" in compact_delivery
    assert "是否应关闭尚不确定时使用 `Refs`" in compact_delivery
    assert "`Refs` 和完整 URL 不主动关闭 issue" in delivery
    assert "使用 body file" in delivery
    assert "真实换行" in delivery
    assert "不发布\n字面量 `\\n`" in delivery
    assert "回读实际 Markdown、链接和隐私" in delivery
    assert "默认在所选交付终态后回复一次" in delivery
    assert "PR 创建本身就是终态、流程阻塞、需要维护者操作" in delivery
    assert "已提交 PR" in delivery
    assert "附 PR URL 与阻塞或待操作事项" in delivery
    assert "回读 issue 编号、仓库与关联语义" in delivery
    assert "授权包含下述一次相关来源\nissue 回复" in delivery
    assert "无关 issue、review 或公共评论仍需单独授权" in delivery
    for premature_claim in ("已完成", "已修复", "已发布"):
        assert premature_claim in delivery
    assert "PR URL、合并状态或 merge commit" in upstream
    assert "避免同一正常交付连续回复两次" in upstream
    assert "PR-only 附 PR URL、合并状态或 merge commit" in personal
    assert "发版附版本、PR URL 和 Release URL" in personal


def test_public_skill_source_does_not_disclose_private_repository_names() -> None:
    public_source = "\n".join(
        _read(path)
        for path in [
            REPO_ROOT / "README.md",
            REPO_ROOT / "instructions/moviepilot-workspace.md",
            *sorted(SKILLS_ROOT.glob("**/*.*")),
        ]
        if path.is_file()
    )

    assert "jxxghp/MoviePilot-Build" not in public_source
    assert "msm9527/" not in public_source
    assert "私有目标只从全局私有" in public_source


def test_workspace_owns_moviepilot_env_secret_and_test_isolation() -> None:
    workspace = _read(REPO_ROOT / "instructions/moviepilot-workspace.md")
    compact_workspace = re.sub(r"\s+", "", workspace)

    assert "`<workspace>/app.env` 可能包含运行凭据和私有配置" in workspace
    assert "不得为了诊断读取或打印内容" in workspace
    assert "不得提交、写入公共文本或拼进命令参数" in workspace
    assert "隔离真实`CONFIG_DIR`" in compact_workspace


def test_retired_skill_names_are_absent_from_active_instruction_surfaces() -> None:
    active = "\n".join(
        _read(path)
        for path in [
            REPO_ROOT / "instructions/moviepilot-workspace.md",
            *sorted(SKILLS_ROOT.glob("**/*.*")),
        ]
        if path.is_file()
    )

    for name in RETIRED_SKILLS:
        assert name not in active


def test_all_skill_markdown_bash_blocks_are_copy_safe() -> None:
    for path in sorted(SKILLS_ROOT.glob("**/*.md")):
        for block in _bash_blocks(_read(path)):
            assert "<" not in block, f"{path} contains an unsafe placeholder"
            assert "--admin" not in block, f"{path} contains --admin"
            assert "--no-verify" not in block, f"{path} contains --no-verify"


def test_readme_syncs_two_skills_and_retires_old_installs_via_trash() -> None:
    readme = _read(REPO_ROOT / "README.md")

    catalog = json.loads(_read(REPO_ROOT / "skill-catalog.json"))
    assert catalog["install_targets"] == {"codex": "../.agents/skills"}
    active = {
        entry["name"] for entry in catalog["skills"] if entry["status"] == "active"
    }
    retired = {
        entry["name"] for entry in catalog["skills"] if entry["status"] == "retired"
    }
    assert active == EXPECTED_SKILLS
    assert retired == RETIRED_SKILLS
    assert all(entry["install_targets"] == ["codex"] for entry in catalog["skills"])
    assert "skill-catalog.json" in readme
    assert "--catalog skill-catalog.json --source-root skills" in readme
    assert "--target codex --check" in readme
    assert "--target claude" not in readme
    assert "不进入用户级全局 skill 目录" in readme
    assert "/usr/bin/trash" in readme
    assert "可从 Trash 恢复" in readme
    for name in RETIRED_SKILLS:
        assert name in readme
    for name in EXPECTED_SKILLS:
        assert name in readme


def test_workspace_instruction_source_and_runtime_link_are_documented() -> None:
    source = REPO_ROOT / "instructions/moviepilot-workspace.md"
    workspace = _read(source)
    readme = _read(REPO_ROOT / "README.md")

    assert "moviepilot-development" in workspace
    assert "moviepilot-delivery" in workspace
    assert "push、PR、merge 和发版" in workspace
    assert "MoviePilot-Skills` 明确排除" in workspace
    assert "本仓不适用 `moviepilot-development` 或 `moviepilot-delivery`" in workspace
    assert "后端、前端与 Rust PR 目标为上游 `v3`" in workspace
    assert "instructions/moviepilot-workspace.md" in readme
    assert "MoviePilot-Skills/instructions/moviepilot-workspace.md" in readme
    assert "readlink ../AGENTS.md" in readme
    assert "test -L ../AGENTS.md || ln -s " in readme
    assert "ln -sfn" not in readme

    tracked = subprocess.run(
        ["git", "ls-files", "--error-unmatch", str(source.relative_to(REPO_ROOT))],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert tracked.returncode == 0


def test_workspace_link_command_refuses_to_replace_a_regular_file() -> None:
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
