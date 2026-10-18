# 2.0 发布文件

上传 `dist/GitHub-2.0` 中的两个程序包即可。`SHA256SUMS.txt` 是可选的下载校验附件。

| 文件 | 使用方式 |
| --- | --- |
| AquaSync-2.0-Setup.exe | 中文向导安装，可选择安装盘，自动创建当前用户桌面快捷方式 |
| AquaSync-2.0-Portable.zip | 完整解压，双击 AquaSync.exe；保留同目录的 _internal |

两者均为 Windows 10/11 x64 版，无需 Python，内容相同。首次使用点击“导入 AquaDX JSON”，选择自己的完整导出文件。

程序默认在所选位置保存 `user-data`、`AquaSync-desktop.json` 和 `logs`。安装包优先推荐非系统盘，不要求管理员权限。请选择当前用户可写的独立文件夹。更新前关闭程序，保留数据与配置；卸载只移除安装的程序文件及快捷方式，不主动删除个人资料。

## 构建

开发与打包环境安装 `requirements-dev.txt`，其中包含桌面依赖、PyInstaller、pytest 和无损图片处理所需的 Pillow。

便携包由 `tools/package_release.py` 的白名单生成。安装包必须使用同一份通过隐私检查的干净运行目录，不能直接把含个人资料的 `dist/v2.0` 整目录加入安装包。

安装脚本：`tools/installer/AquaSync.iss`。编译工具使用官方 Inno Setup 6.7.3，官网下载文件的 Authenticode 签名验证通过。简体中文翻译来自对应 `is-6_7_3` 标签的 `Files/Languages/Unofficial/ChineseSimplified.isl`，保留原始来源与译者说明。

`AquaSync-Portable.spec` 默认通过 `tools/compact_assets.py` 生成紧凑资源目录；源文件变化时自动重建缓存。图片采用逐像素核对的无损 WebP，完全重复的图片使用本地别名复用；尺寸、透明度和原始 PNG 源素材保留，不需要联网补图。`AQUASYNC_RELEASE_ASSETS` 可显式指定已验证的资源目录。

公开源码中的新增收藏图片也可直接使用已经验证的 WebP 和 `image_aliases.json`，避免重复收录体积更大的 PNG。图片解析兼容原始 PNG 与无损 WebP；从公开源码打包时，已经压缩的图片会直接复制，不再次编码。

从较早的安装包覆盖更新时，仅清除程序自带的旧 PNG 资源及已经不再使用的 PIL 目录，避免新旧图片重复占用空间；`user-data` 中的自定义封面、成绩和设置不在清理范围。

示例（将路径替换为实际的干净目录、工具位置及输出位置）：

```powershell
python tools/package_release.py --source CLEAN_RUNTIME --output PORTABLE_OUTPUT --version 2.0
ISCC.exe /DSourceDir=CLEAN_RUNTIME /DOutputDir=SETUP_OUTPUT tools/installer/AquaSync.iss
```

安装包不联网下载运行依赖，不自动导入玩家资料，不发布到 GitHub。安装、覆盖安装和卸载测试使用隔离的 F 盘目录；快捷方式测试使用 `/SHORTCUTDIR=` 重定向到测试目录，默认目的地为当前用户桌面。测试不覆盖既有桌面快捷方式。

工具来源：<https://jrsoftware.org/isdl.php>；便携编译器模式说明：<https://jrsoftware.org/ishelp/topic_technotes.htm>。
