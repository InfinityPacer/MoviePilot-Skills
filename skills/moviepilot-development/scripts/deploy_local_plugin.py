#!/usr/bin/env python3
"""通过 secure-access 将 MoviePilot 本地插件更新到 NAS 容器的原目录。"""

from __future__ import annotations

import argparse
import hashlib
import shlex
import subprocess
import sys
import tarfile
import tempfile
import uuid
from pathlib import Path


def build_archive(plugin_dir: Path, output: Path) -> tuple[int, str]:
    root = plugin_dir.parent
    included = 0
    with tarfile.open(output, "w:gz", format=tarfile.PAX_FORMAT) as archive:
        for path in sorted(plugin_dir.rglob("*")):
            relative = path.relative_to(root)
            if any(part in {".git", "node_modules", "__pycache__"} for part in relative.parts):
                continue
            if any(part.startswith("._") or part == ".DS_Store" for part in relative.parts):
                continue
            archive.add(path, arcname=relative, recursive=False)
            included += 1
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    return included, digest


def run_controller(args: list[str], *, input_data: bytes | str | None = None) -> None:
    command = [sys.executable, *args]
    payload = input_data.encode() if isinstance(input_data, str) else input_data
    subprocess.run(command, input=payload, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="部署 MoviePilot 本地插件并验证热加载")
    parser.add_argument("plugin_dir", type=Path, help="本地插件目录，例如 MoviePilot-Plugins/plugins.v3/archivemanager")
    parser.add_argument("--container", default="moviepilot-v3", help="MoviePilot 容器名")
    parser.add_argument("--container-repo", required=True, help="容器内被监测的插件目录")
    parser.add_argument("--profile", default="nas-ssh", help="secure-access SSH profile")
    parser.add_argument(
        "--controller",
        type=Path,
        default=Path.home() / ".codex/skills/secure-access/scripts/access-controller.py",
        help="secure-access controller 脚本路径",
    )
    parser.add_argument("--timeout", type=int, default=60, help="每次远程操作超时时间（秒）")
    parsed = parser.parse_args()

    plugin_dir = parsed.plugin_dir.resolve()
    if not plugin_dir.is_dir():
        parser.error(f"插件目录不存在：{plugin_dir}")
    if not (plugin_dir / "__init__.py").is_file():
        parser.error(f"不是可部署的 MoviePilot 插件目录：{plugin_dir}")
    if not parsed.container_repo.startswith("/") or ".." in Path(parsed.container_repo).parts:
        parser.error("--container-repo 必须是容器内绝对路径且不能包含 ..")

    controller = parsed.controller.expanduser().resolve()
    if not controller.is_file():
        parser.error(f"secure-access controller 不存在：{controller}")
    remote_name = f"moviepilot-plugin-{uuid.uuid4().hex}.tar.gz"
    remote_path = f"/tmp/{remote_name}"
    with tempfile.TemporaryDirectory(prefix="moviepilot-plugin-") as temporary:
        archive_path = Path(temporary) / remote_name
        count, digest = build_archive(plugin_dir, archive_path)
        size = archive_path.stat().st_size
        print(f"打包 {plugin_dir.name}：{count} 个条目，{size} 字节，sha256={digest}")
        run_controller(
            [
                controller,
                "upload-file",
                "--profile",
                parsed.profile,
                "--fallback",
                "fail",
                "--timeout",
                str(parsed.timeout),
                "--destination",
                remote_path,
                "--size",
                str(size),
                "--sha256",
                digest,
            ],
            input_data=archive_path.read_bytes(),
        )

        container = shlex.quote(parsed.container)
        repo = shlex.quote(parsed.container_repo)
        remote_file = shlex.quote(remote_path)
        plugin_name = shlex.quote(plugin_dir.name)
        script = f"""set -eux
container={container}
repo={repo}
package={remote_file}
name={plugin_name}
parent=$(dirname "$repo")
docker exec "$container" sh -c "test -d '$repo'"
test "$(basename "$repo")" = "$name"
docker cp "$package" "$container:/tmp/{remote_name}"
docker exec "$container" sh -c "find '$repo' -depth -name '._*' -exec rm -rf {{}} +"
docker exec "$container" sh -c "tar -xzf /tmp/{remote_name} -C '$parent' && find '$repo' -depth -name '._*' -exec rm -rf {{}} + && touch '$repo/__init__.py' && rm -f /tmp/{remote_name}"
rm -f "$package"
printf '%s\\n' '--- deployment verification ---'
printf 'container='; docker inspect -f '{{{{.Name}}}} {{{{.State.Status}}}} {{{{.State.Health.Status}}}}' "$container"
printf 'appledouble='; docker exec "$container" sh -c "find '$repo' -name '._*' -o -name '.__*' | wc -l"
printf 'plugin_markers=\\n'; docker exec "$container" sh -c "grep -n '_staging_tasks\\|copyTask\\|staging_count' '$repo/__init__.py' '$repo/frontend/src/components/Config.vue' '$repo/frontend/src/config/api.ts' 2>/dev/null | head -20" || true
printf '%s\\n' '--- recent MoviePilot plugin logs ---'
docker exec "$container" sh -c "tail -n 300 /config/logs/moviepilot.log 2>/dev/null | grep -E 'ArchiveManager|同步本地插件|检测到本地插件|加载插件：ArchiveManager|插件加载失败' | tail -60" || true
"""
        run_controller(
            [
                controller,
                "run-script",
                "--profile",
                parsed.profile,
                "--fallback",
                "fail",
                "--timeout",
                str(parsed.timeout),
            ],
            input_data=script,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
