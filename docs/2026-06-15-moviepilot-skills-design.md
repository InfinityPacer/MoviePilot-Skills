# MoviePilot Skills 设计

## 目标

建立独立仓库 `InfinityPacer/MoviePilot-Skills`，集中维护 MoviePilot 工作区的交付流程，
避免把 agent skill 附着在任一业务仓库。

## 结构

```text
MoviePilot-Skills/
├── skills/
│   ├── moviepilot-delivery/
│   ├── moviepilot-upstream-pr/
│   └── moviepilot-plugin-release/
└── tests/
    └── test_skills.py
```

`moviepilot-delivery` 根据当前子仓和“PR/发版”等自然语言请求选择专用 skill，但不承载
执行流程。`moviepilot-upstream-pr` 处理 `MoviePilot` 与 `MoviePilot-Frontend` fork 向
`jxxghp/*:v2` 提 PR；`moviepilot-plugin-release` 处理自有插件仓的 PR、Auto-merge
与 GitHub Release。两者不合并，防止目标仓库和终止条件混淆。

## 安装

同一事实源分别安装到：

- `~/.codex/skills/<skill-name>`
- `~/.claude/skills/<skill-name>`

安装副本必须与技能仓内容一致。更新 skill 时先修改技能仓，再同步安装。

## 业务仓清理

删除 `MoviePilot-Plugins/.agents/skills/moviepilot-plugin-release/`，避免双重事实源。
插件仓保留门禁实现；只有流程文档迁出。

## AGENTS.md

保留跨任务硬约束：代码规范、测试基线、隐私、commit/push 前确认。删除已经由 skill
承载的分支路由、PR 正文结构、协作来源判定和发布回查细节，只保留：

- 主程序后端或前端向上游提交 PR 时使用 `moviepilot-upstream-pr`；
- 插件发版时使用 `moviepilot-plugin-release`。

## 上游 PR 终止条件

Skill 创建并回读上游 PR，确认 CI/review 状态后结束。不得为 `jxxghp/*` PR 启用
Auto-merge 或代替上游维护者合并。前后端联动改动分别建立 PR，并在正文相互关联。
