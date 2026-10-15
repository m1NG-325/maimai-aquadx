# 已有舞萌功能与参考来源

本页仅记录已提供的桌面功能。完整算法、数据、素材与参考源码归属见 [ALGORITHMS_AND_SOURCES.md](ALGORITHMS_AND_SOURCES.md)，软件内「功能与数据说明」同步展示。

| 功能 | 当前提供的交互 |
|---|---|
| B50 / B40 | 原始 B35+B15、参考估算 B50、旧系数 25+15 估算 |
| 单曲与成绩 | 双列成绩卡片、详情页签与可拖出浮窗 |
| 曲库 | 类型 / 难度 / 定数自动筛选，曲名与 ID 搜索，随机一张 |
| 牌子与条件完成 | 图鉴、总览和未完成列表，可调分区、缩放和平移 |
| 推分 | 单曲目标与替换收益估算，各列独立升降序 |
| 自选 Best | 按现有条件筛选后排序 |
| 分数线 | 物量支持时计算 TAP GREAT / BREAK 50 落容错 |
| 段位 | 30 项配置与单曲最佳成绩展示 |
| 今日舞萌 | 玩家 ID + 本地日期确定的娱乐推荐 |
| 猜歌 / 开字母 | 本地单人文字提示及曲名作答 |
| 导入与同步 | AquaDX JSON、本地玩家、落雪个人 API、备份与所选差异提交 |
| 数据管理 | 可选数据目录、校验迁移与下次启动自动使用 |

参考项目：https://github.com/xszqxszq/KarenBot ，核对提交 da03d8cc3e19edd698482c1c6e750a04655dcbfa。Rating.kt、CalcController.kt、MusicInfo.kt 等具体参考位置已在软件及来源文档逐项列明；Python / Qt 界面和本地服务由本项目实现。

复用资源：https://github.com/xszqxszq/KarenBot-Resources ，包括 course.json 和图鉴背景、卡片、评级、FC/FS、等级等 PNG；许可见 KarenBot-LICENSE.txt 与 KarenBot-Resources-LICENSE.txt。未执行上游 bot 或 Kotlin / HTML 渲染器。
