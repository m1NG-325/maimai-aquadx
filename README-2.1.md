# AquaSync 2.1

[中文](README-2.1.md) · [English](readme_EN-2.1.md)

Windows 本地舞萌查分软件，支持导入 AquaDX 私服导出的 maimai2 JSON 和落雪查分器导出的成绩 CSV，查看成绩、B50、牌子进度和推分推荐。

> 2.1 为待发布候选版本，安装包与便携包已在本地准备，GitHub Release 将在确认后发布。

## 使用

1. 发布后，在本仓库 **[Releases](https://github.com/m1NG-325/maimai-aquadx/releases)** 下载以下任意一种：
   - **安装版** `AquaSync-2.1-Setup.exe`：双击安装，可选择安装位置，自动创建桌面快捷方式。
   - **便携版** `AquaSync-2.1-Portable.zip`：完整解压后运行 `AquaSync.exe`，请保留 `_internal` 文件夹。
2. 选择本地玩家 ID，点击「导入 AquaDX JSON」或「导入落雪 CSV」，选择自己的导出文件。
3. 查看 B50、成绩、牌子进度和其他本地分析。

支持 Windows 10/11 64 位，无需安装 Python。常用查询和分析功能可离线使用。

## 2.1 更新

- 新增落雪 CSV 成绩导入，保留达成率、DX 分、FC/FS 和文件提供的游玩时间。
- 落雪 CSV 导入后默认显示落雪 B50 估算，可继续查询成绩和牌子进度。
- 落雪同步表格的表头和文字居中，「选择」列按内容收窄。
- 精简未使用的运行依赖：安装包从 750.5 MB 减至 724.7 MB，便携包从 761.0 MB 减至 730.8 MB（按十进制计算）。
- 图片素材与 2.0 保持一致，没有重新压缩画质、缩小分辨率或改为联网下载。

## 功能

- **成绩查询**：B50、双 B50 对比、成绩排序、曲目详情和曲绘。
- **统一曲库**：成绩、B50、曲库与推分推荐共用曲目元数据；牌子支持私服、国服和历史参考范围。
- **推分与计算**：私服/国服独立推荐、Rating 计算和彩色定数×达成率对照表。
- **游玩历史与判定**：逐局记录、游玩日历、每日次数走势、FAST/LATE、判定分析及 CSV 导出。
- **成绩走势**：Rating 与单曲达成率走势，支持日期范围筛选。
- **冒险与养成**：地图路线与奖励、角色、搭档亲密度、课程挑战、万华镜和登录奖励。
- **个人档案与收藏**：个人资料、操作设置、当前装扮、收藏歌曲及物品预览。
- **其他工具**：成绩统计、段位表、猜歌、开字母、分数线容错和自选 Best。
- **备份与同步**：落雪成绩备份、差异选择同步，水鱼/落雪 JSON 导出。
- **本地保存**：支持更改数据目录并迁移已有资料。

## 导入与数据

- **AquaDX JSON**：建议使用完整导出，以查看文件实际提供的原始 B50、游玩日志和个人档案。
- **落雪 CSV**：只包含成绩，不含完整玩家资料、原始 B50 分组、游玩日志和收藏档案。B50 按本地曲库估算，上传时间不会当作游玩时间。
- 同名玩家再次导入会替换其本地快照。建议为落雪 CSV 使用独立的本地玩家 ID，避免替换已有完整 AquaDX 档案。
- 导入只保存到本地，不会自动上传到落雪。同步前请核对目标账号和所选成绩。
- 可查询内容取决于导出文件实际提供的数据；缺少的信息不会自动补造。

## 数据与更新

- 个人数据默认保存在程序目录下的 `user-data`，配置为 `AquaSync-desktop.json`。
- 更新前请关闭软件，保留数据目录和配置文件。
- 安装版可覆盖更新，卸载时保留个人资料；便携版请覆盖程序文件，不要删除原有数据和配置。
- 新旧版本兼容本地成绩数据库。完整档案功能仍需要导入包含相关记录的 AquaDX JSON。

公开参考定数可能与游戏实际版本不同，Rating 和牌子进度供参考。

[详细使用说明](docs/DESKTOP.md) · [Releases 与更新日志](https://github.com/m1NG-325/maimai-aquadx/releases) · [算法与数据来源](docs/ALGORITHMS_AND_SOURCES.md)

## 来源与致谢

- [AquaDX](https://github.com/MewoLab/AquaDX)
- [KarenBot](https://github.com/xszqxszq/KarenBot)
- [落雪查分器](https://maimai.lxns.net/)
- [水鱼查分器](https://www.diving-fish.com/maimaidx/prober/)
- [Otoge DB](https://otoge-db.net/)
- [SaltMeta](https://github.com/reiwa/SaltyMeta)
- [mai-kit](https://github.com/mai-kit/mai-kit)
