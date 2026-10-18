# AquaSync 应用图标

原创图标通过内置 ImageGen 生成，使用深蓝底色与青色八键圆环，去除彩色灯光、音符和装饰。
源图：`data/report_assets/aquasync.png`；Windows 图标：`data/report_assets/aquasync.ico`。
ICO 包含 16、24、32、48、64、128、256 像素尺寸；PNG 转 ICO 仅作文件编码与尺寸适配。

最终生成提示词：

> One ultra-minimal original Windows app icon for AquaSync, a maimai rhythm game score viewer. Flat clean vector-like symbol, only two solid colors: dark navy #152333 and soft cyan #64DDD9. Eight simple short rounded rectangular keys arranged evenly around a perfectly circular ring, evoking a circular eight-button rhythm game controller. Center is completely empty dark navy negative space. Cyan keys and a thin cyan inner circle on a navy rounded-square tile. Absolutely no notes, no stars, no water drops, no gradients, no lighting, no bevel, no texture, no outlines around keys, no text, no small details, no extra decoration. Calm premium restrained software icon, crisp symmetry, readable at 16 pixels. Large centered mark with generous consistent margins, square canvas, genuinely transparent exterior outside the rounded-square navy tile. Deliver only one finished icon.

启动日志保存在 EXE 同目录的 `logs/startup.log`，超过 2 MiB 时轮转一份；默认数据在同目录 `user-data`，配置在同目录 `AquaSync-desktop.json`。Portable 为目录版，不会向 C 盘解包运行库；请保留 `_internal` 文件夹。程序入口执行前的 Windows 加载器、磁盘读取故障可能来不及写入该日志，需要结合 Windows 事件查看器排查。
