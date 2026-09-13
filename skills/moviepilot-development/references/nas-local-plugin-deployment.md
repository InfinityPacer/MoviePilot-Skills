# NAS 本地插件部署

适用于 MoviePilot 使用 `PLUGIN_LOCAL_REPO_PATHS` 和 `PLUGIN_AUTO_RELOAD` 监测本地插件仓库的部署场景。

## 更新方式

保持被 MoviePilot 监测的本地插件仓库目录本身不变，只在原目录内更新插件内容。可以先在该仓库目录内准备临时插件子目录，再把目标插件文件复制或替换到原有插件目录中。

不要整体原子替换仓库目录。目录路径虽然相同，但整体替换会改变目录 inode，MoviePilot 的文件监测器可能继续监听旧目录对象，导致新目录中的文件变化不再触发同步和热重载。

部署后应从 MoviePilot 日志确认以下链路：

1. 检测到本地插件文件变化
2. 已同步本地插件
3. 准备重载插件
4. 插件路由重新注册

如果因故必须整体替换仓库目录，替换后必须通过 MoviePilot 的管理路径重建插件文件监测器，并重新验证上述日志链路；不能只比较仓库文件哈希就宣称热更新已生效。

## 自动部署脚本

重复部署本地插件时，使用 `scripts/deploy_local_plugin.py`。脚本通过 `secure-access` 上传一个不携带 macOS 扩展属性的临时 tar 包，再在 MoviePilot 容器中覆盖**原插件目录内的文件**，并在覆盖前后清理 `._*`、`.__*` 和 `.DS_Store`。它不会替换被监测仓库目录本身，因此不会丢失文件监测器绑定的 inode。

```bash
python3 skills/moviepilot-development/scripts/deploy_local_plugin.py \
  /path/to/MoviePilot-Plugins/plugins.v3/archivemanager \
  --container-repo /config/local_plugins/plugins.v3/archivemanager
```

脚本结束时会回读容器健康状态、AppleDouble 残留数量、目标插件关键标记和 MoviePilot 最近的插件加载日志。出现插件加载失败时应先处理输出中的残留文件或日志错误，不要只依据文件已上传就判断热加载成功。
