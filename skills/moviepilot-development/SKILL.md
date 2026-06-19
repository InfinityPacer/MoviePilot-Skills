---
name: moviepilot-development
description: Use when starting local development, debugging, reproducing issues, running tests, preparing topic branches, or launching runtime services in the MoviePilot workspace before commit or PR work.
---

# MoviePilot 开发路由

## 作用

只判断当前 MoviePilot 工作区开发任务应使用哪个开发 skill。不要复制、概括或自行执行具体
分支、测试、运行态调试、PR 或发版命令。

## 路由

先检查当前仓库、目标文件和 `git remote -v`，再选择：

| 当前工作范围 | 用户常见说法 | 必须转交 |
| --- | --- | --- |
| `MoviePilot` | 后端开发、修 bug、跑后端单测、启动后端、调试接口 | `moviepilot-main-development` |
| `MoviePilot-Frontend` | 前端开发、页面调试、跑前端检查、启动 Vite | `moviepilot-main-development` |
| `MoviePilot-Plugins` | 个人插件开发、插件单测、本地热加载、插件分支 | `moviepilot-plugin-development` |
| `MoviePilot-Plugins-Official` | 官方插件仓开发、官方插件 PR 前准备、官方仓门禁 | `moviepilot-plugin-development` |

跨后端、前端、插件联动时，分别使用对应开发 skill；不要把多个仓库改动混入一个开发分支。

## 模糊请求

- 用户只说“开发/调试/复现/跑测试”：先检查当前仓库；当前目录是工作区根时按本次目标文件判断。
- 用户只说“插件”：先区分 `MoviePilot-Plugins` 与 `MoviePilot-Plugins-Official`，再转插件开发流程。
- 用户说“PR/发版/提交上游”：改用 `moviepilot-delivery`，不要在开发路由里处理交付。
- 仓库、remote 或目标仍无法确定：只问一个必要澄清问题，不凭空选择。

## 强制边界

选定后必须加载并完整遵循对应开发 skill。路由 skill 到此结束，不得把“已完成路由”误报为
已经完成开发、测试、commit、push、PR 或发版。
