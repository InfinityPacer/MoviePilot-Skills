# 容器实例与本地插件部署验证

在 NAS 或远程容器实例上验证插件改动前，先检查容器环境与日志是否实际启用了 `PLUGIN_LOCAL_REPO_PATHS`，区分市场安装实例与本地监测仓库两种形态，不要未经核实就向 `/config/local_plugins` 写入文件。

## 形态一 未启用本地插件仓的市场安装实例（常见生产容器）

当容器未配置 `PLUGIN_LOCAL_REPO_PATHS`（或日志显示获取到 0 个本地插件）时，已安装插件运行在 `/app/app/plugins/<plugin_id>`，写入 `/config/local_plugins` 不会触发加载。

1. **备份并更新运行副本** 在覆盖 `/app/app/plugins/<plugin_id>` 前先保留原目录备份，验证通过后正式上线仍走仓库 PR 与插件市场更新。在 macOS 上用 `tar` 打包插件目录或镜像构建上下文传往容器主机时，必须设置 `COPYFILE_DISABLE=1` 并清理 `._*`、`.__*` 与 `.DS_Store`，防止 AppleDouble 二进制文件混入目录或被当作容器启动控制脚本导致循环重启。
2. **热重载与作业状态确认** 启用 `PLUGIN_AUTO_RELOAD` 的实例在运行副本更新后会触发插件重载，从日志确认重新加载与路由注册成功；注意热重载会将该插件正在运行的后台作业标记为 `stopped`，重载完成后需重新提交运行。
3. **通过插件自身运行入口验收** 直接调用插件自身的运行接口（例如 `/api/v1/plugin/<PluginId>/run`）触发真实任务链路观察结果，不要在容器内单独直接执行插件内部模块脚本做旁路测试。通过接口读写插件配置时，`GET /api/v1/plugin/<plugin_id>` 返回的是 `{"success", "message", "data"}` 包装结构，而 `PUT /api/v1/plugin/<plugin_id>` 请求体只接收 `data` 内的原始配置字典本身，写回后须回读确认启用状态与任务数未丢失。
4. **在线进程探针有界原则** 严禁向正在运行的生产进程注入逐对象 `gc.get_referrers` 等深层堆遍历（在主线程事件循环持有 GIL 会导致服务卡死数分钟），重型内存归因应在 `docker commit --pause=false` 导出的离线无网络副本容器中执行。

## 形态二 已启用 `PLUGIN_LOCAL_REPO_PATHS` 的本地监测仓库

当容器已明确配置 `PLUGIN_LOCAL_REPO_PATHS` 与 `PLUGIN_AUTO_RELOAD` 监测本地仓库目录时，保持被监测目录本身不变，只在原目录内更新插件文件，不要整体原子替换仓库目录（替换目录会改变 inode，导致文件监测器继续监听旧目录而漏掉后续变更；若已整体替换，须重建监测器并从日志核对“检测到本地插件文件变化 -> 已同步本地插件 -> 准备重载插件 -> 插件路由重新注册”完整链路）。

重复向容器内目标插件目录同步（无论目标是本地监测目录还是已确认的插件目录）时，可使用 `scripts/deploy_local_plugin.py` 上传不含 macOS 扩展属性的归档并覆盖原目录内文件

```bash
python3 skills/moviepilot-development/scripts/deploy_local_plugin.py \
  /path/to/MoviePilot-Plugins/plugins.v3/archivemanager \
  --container-repo /app/app/plugins/archivemanager
```

脚本结束时会回读容器健康状态、AppleDouble 残留数量与最近的插件加载日志，出现加载报错时先排清残留文件或异常日志，不单凭文件上传成功判定生效。
