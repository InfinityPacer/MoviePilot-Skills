# MoviePilot Skills Implementation Plan

## Goal

创建独立技能仓，维护一个路由 skill 以及 upstream PR、plugin release 两个执行 skill，
完成双代理安装、旧事实源清理和工作区规则精简。

## Tasks

1. 先写结构与关键行为测试并确认失败。
2. 用 skill-creator 初始化两个 skill。
3. 迁移插件发版流程，编写前后端上游 PR 流程。
4. 运行仓库测试和 `quick_validate.py`。
5. 安装到 Codex 与 Claude Code，比较安装副本。
6. 删除插件仓旧 skill，精简工作区 `AGENTS.md`。
7. 展示三个落点的 diff，取得 commit、建仓和 push 确认。
