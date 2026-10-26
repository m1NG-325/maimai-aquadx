# AquaSync 2.1 发布文件

| 文件 | 大小 | 使用方式 |
| --- | --- | --- |
| AquaSync-2.1-Setup.exe | 724,693,600 字节 | 中文安装向导，可选择位置并创建桌面快捷方式 |
| AquaSync-2.1-Portable.zip | 730,844,303 字节 | 完整解压后运行 AquaSync.exe，保留 _internal 文件夹 |

Windows 10/11 x64，无需安装 Python。当前程序包已在本地生成，2.1 Release 需确认后发布。

## 构建与隐私

与 2.0 一样使用 PyInstaller 目录版、Inno Setup 安装器和白名单便携 ZIP。发行包只包含程序与公开资源，不包含玩家数据库、原始导出、API 密钥、本机配置、日志、测试样本或截图。

- PyInstaller 配置：`AquaSync-Portable.spec`。
- 运行依赖裁剪：`tools/runtime_pruning.py`；保留软件 OpenGL 后备库、HTTPS、SQLite 和常用图片解码。
- 安装器配置：`tools/installer/AquaSync.iss`。
- 便携打包：`tools/package_release.py --source CLEAN_RUNTIME --output RELEASE_OUTPUT --version 2.1`。
- 打包 EXE 自检：`AquaSync.exe --self-test --audit-runtime --data-dir TEST_PROFILE --result RESULT_JSON`。

本次沿用 2.0 已验证的素材文件，10834 个资源文件逐文件 SHA-256 相同，没有重编码或修改图片尺寸、透明度和画质。运行依赖与资源目录减少约 65.7 MiB；这不是压缩包下载体积的减少量。

## 升级

更新前关闭软件，保留 `user-data`、自定义数据目录和 `AquaSync-desktop.json`。安装版清理范围仅限 `_internal` 中已淘汰的程序资源和依赖，不递归清理整个安装目录。卸载保留个人数据、配置和日志。

安装包相比 2.0 的 750,530,341 字节减少 25,836,741 字节（约 3.44%）；便携包相比 761,027,998 字节减少 30,183,695 字节（约 3.97%）。上述 65.7 MiB 为解压后目录的减少量，不能作为下载包的减少量。

本文件记录 2.1 的历史构建方式。当前使用说明见仓库首页，更新日志只保留在 GitHub Releases 正文中。
