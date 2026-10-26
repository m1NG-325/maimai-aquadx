# AquaSync 2.2

[中文](README.md) · [English](readme_EN.md)

Windows 本地舞萌查分软件，支持导入 AquaDX 私服导出的 maimai2 JSON 和落雪查分器导出的成绩 CSV，查看成绩、B50、牌子进度和推分推荐

## 使用

1. 在本仓库 [Releases](https://github.com/m1NG-325/maimai-aquadx/releases) 下载 `AquaSync-2.2-Portable.zip`
2. 完整解压后运行 `AquaSync.exe`，请保留 `_internal` 文件夹，不要在压缩包内直接运行
3. 选择本地玩家 ID，点击「导入 AquaDX JSON」或「导入落雪 CSV」，选择自己的导出文件
4. 查看 B50、成绩、牌子进度和其他本地分析

支持 Windows 10/11 64 位，无需安装 Python。常用查询和分析功能可离线使用

软件免费提供，正式版本在本仓库 Releases 发布

## 功能

- **成绩查询**：B50、双 B50 对比、成绩排序、曲目详情及高清曲绘
- **统一曲库**：成绩、B50、曲库与推分推荐共用曲目元数据；牌子支持私服、国服及含删除曲目的参考范围
- **推分与计算**：私服/国服独立推荐、Rating 计算及彩色定数×达成率对照表
- **游玩历史**：逐局记录、游玩日历、每日游玩次数走势、筛选排序及 CSV 导出
- **判定分析**：音符判定、FAST/LATE 统计及 ACC 区间分析
- **成绩走势**：Rating 变化、单曲达成率走势及日期区间筛选
- **冒险与养成**：地图路线与奖励、角色、搭档亲密度、课程挑战、万华镜及登录奖励
- **个人档案与收藏**：个人资料、操作设置、当前装扮、收藏歌曲及物品预览
- **其他工具**：成绩统计、段位表、猜歌、开字母、分数线容错及自选 Best
- **备份与同步**：落雪成绩备份、差异选择同步，水鱼/落雪 JSON 导出
- **本地保存**：支持更改数据目录并迁移已有资料
- **检查更新**：在「功能与数据说明」中查看当前版本，手动检查 GitHub 最新正式版、查看更新日志并打开下载页

## 导入数据

- **AquaDX JSON**：建议使用完整导出，以查看文件实际提供的原始 B50、游玩日志和个人档案
- **落雪 CSV**：只包含成绩，不含完整玩家资料、原始 B50 分组、游玩日志和收藏档案。B50 按本地曲库估算，上传时间不会当作游玩时间
- 同名玩家再次导入会替换其本地快照，建议为落雪 CSV 使用独立的本地玩家 ID，避免替换已有完整 AquaDX 档案
- 导入只保存到本地，不会自动上传到落雪。同步前请核对目标账号和所选成绩
- 可查询内容取决于导出文件实际提供的数据，缺少的信息不会自动补造

## 数据保存与升级

- 个人数据默认保存在程序目录下的 `user-data`，配置为 `AquaSync-desktop.json`
- 升级前请关闭软件，保留数据目录和配置文件
- 解压新版后覆盖程序文件，请勿删除原有数据和配置；使用自定义数据目录时，继续保留该目录

公开参考定数可能与游戏实际版本不同，Rating 和牌子进度供参考

[详细使用说明](docs/DESKTOP.md) · [Releases 与更新日志](https://github.com/m1NG-325/maimai-aquadx/releases) · [算法与数据来源](docs/ALGORITHMS_AND_SOURCES.md)

## 来源与致谢

- [AquaDX](https://github.com/MewoLab/AquaDX)
- [KarenBot](https://github.com/xszqxszq/KarenBot)
- [落雪查分器](https://maimai.lxns.net/)
- [水鱼查分器](https://www.diving-fish.com/maimaidx/prober/)
- [Otoge DB](https://otoge-db.net/)
- [SaltMeta](https://github.com/reiwa/SaltyMeta)
- [mai-kit](https://github.com/mai-kit/mai-kit)
