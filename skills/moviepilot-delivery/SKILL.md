---
name: moviepilot-delivery
description: Use when the user says PR, pull request, 提 PR, 提交上游, 发版, 发布, release, version bump, or asks to commit and publish work anywhere in the MoviePilot workspace without explicitly naming a delivery skill.
---

# MoviePilot 交付路由

## 作用

只判断当前 MoviePilot 仓库应使用哪个交付 skill。不要复制、概括或自行执行子 skill 的
提交、验证、PR、Auto-merge、发版命令。

## 路由

先检查当前仓库、目标文件和 `git remote -v`，再选择：

| 当前工作范围 | 用户常见说法 | 必须转交 |
| --- | --- | --- |
| `MoviePilot` | PR、提 PR、提交上游、push 后开 PR | `moviepilot-upstream-pr` |
| `MoviePilot-Frontend` | 前端 PR、提上游、发布前端改动 | `moviepilot-upstream-pr` |
| `MoviePilot-Plugins` | 发版、发布插件、版本升级、插件 PR | `moviepilot-plugin-release` |

前后端联动时，对两个业务仓分别使用 `moviepilot-upstream-pr`，不得转到插件发版流程。

## 模糊请求

- 用户只说“PR”：先检查当前仓库；主程序前后端走 `moviepilot-upstream-pr`，插件仓走
  `moviepilot-plugin-release`。
- 用户只说“发版/发布”：先检查当前仓库；插件仓走 `moviepilot-plugin-release`。主程序
  前后端没有对应发布流程时，确认用户是要提交上游 PR，还是另有发布目标。
- 当前目录是工作区根：根据本次改动所在子仓路由；跨多个子仓时逐仓处理。
- 仓库、remote 或目标仍无法确定：只问一个必要的澄清问题，不凭空选择。

## 强制边界

选定后必须加载并完整遵循对应子 skill。路由 skill 到此结束，不得把“已完成路由”误报为
已经完成 commit、push、PR 或发版。
