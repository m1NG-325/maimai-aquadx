# 牌子曲库范围

三个选项独立保存于 `data/plate_catalogs.json`，快照日期为 2026-10-17。运行与查询无需联网。总览、未完成清单、图片分母和点击后的详情使用当前所选范围。原分析曲库作为基础输入之一；桌面查询、B50、曲库、推荐和牌子通过统一元数据层解析，不再各自维护展示曲库。

|选项|范围|
|---|---|
|私服曲库|日本官服现行普通谱面；按官方清单筛选，不混入国服保留曲、官服已删曲、暂缓收录曲或宴谱。|
|国服曲库|KarenBot-Resources 的国服 `music.json`、`plate.json`、`version.json`；牌子 requirements/remasters 与 bot 已载入曲目的交集。|
|私服曲库（含删除曲目）|日服现行清单加已核实的历史普通谱面，不受用户私服安装目录限制；包括公开历史档案补充的ブリキノダンス。|

国服的熊/華、爽/煌等牌子会按年度国服要求出现相同曲目集合，不照搬日服原版/PLUS各自的分组。国服版本截至 bot 的国服 version.json，不显示尚未支持的日服未来牌子。保留原版/PLUS牌子名称以对照 bot。

普通版本牌子不要求 Re:MASTER；舞按旧世代及 Re:MASTER计算。真合并初代/PLUS并排除ジングルベル，不支持真将。国服的 Re:MASTER 范围直接取 bot 的 remasters 清单，而不是“所有已知旧曲 Re:MASTER”。宴谱不计入上述普通牌子范围，包括恢复包把旧宴谱全世界共通リズム感テスト放入普通 ID 的情况。

## 数据与实现来源

- 日本现行收录/难度：[世嘉官方清单](https://maimai.sega.jp/data/maimai_songs.json)。本次核对覆盖其中全部1585个普通曲目类型条目（SD/DX分别计）、6492张难度谱面。
- 公开 ID、定数、版本参考：[SaltMeta](https://github.com/realtvop/SaltMeta)、[OTOGE DB](https://github.com/zvuc/otoge-db)。同名歌曲结合曲师识别，避免把两个 Link 或 Heartbeats/Heart Beats 合并。
- 最新9个DX曲目ID以官方曲绘和落雪公开曲绘交叉匹配：平滑缩放32×32，平均像素误差小于3，次优候选差距大于20；证据保存在快照 provenance.idMatches。
- 国服数据：[music.json](https://github.com/xszqxszq/KarenBot-Resources/blob/main/data/maimai/music.json)、[plate.json](https://github.com/xszqxszq/KarenBot-Resources/blob/main/data/maimai/plate.json)、[version.json](https://github.com/xszqxszq/KarenBot-Resources/blob/main/data/maimai/version.json)。保留资源哈希；牌子仅有要求而 bot 曲库未载入的 ID 不进入分母，遵循 bot 在载入曲库上筛选的行为。
- 国服功能参考：[KarenBot ComboQuery](https://github.com/xszqxszq/KarenBot/blob/da03d8cc3e19edd698482c1c6e750a04655dcbfa/maimai/src/main/kotlin/maimai/query/ComboQuery.kt)、MaimaiData 的本地数据加载。未运行或打包 bot 程序；上游 MIT 许可已附带。
- 历史曲目身份：[历史删曲表](https://gamerch.com/maimai/533442)、[OTOGE历史档案](https://github.com/zvuc/otoge-db/blob/main/maimai/data/music-ex-deleted.json)。恢复包只用于校对ID、谱面存在性和旧版本，不复制音频、视频、谱面文件或个人数据。已核实历史元数据内置供离线使用。
- `tools/build_plate_catalogs.py` 只读取单独下载的审计输入，生成已核实元数据快照；`app/plate_catalogs.py` 校验，`app/calculations.py` 的 plate_required/plate_progress 统一统计，`app/report_models.py` 复用同一要求生成图表。

## 特殊情况与限制

- Can Do：历史 ORANGE PLUS 与2026年MAGiCAL复活版保留各自版本记录。两版沿用相同成绩ID，旧私服成绩无法区分新版谱面完成情况，显示仅供参考。历史定数不覆盖复活版。[复活与谱面更新说明](https://info-maimai.sega.jp/9634/)
- ループザルーム：官方暂缓收录，因此不计入两个“日服谱面”范围；原私服查询元数据和原始成绩仍保留。[官方公告](https://info-maimai.sega.jp/9997/)
- 不能验证的精确定数为 null，显示待核实，不用显示等级冒充定数。历史本地定数标记为参考，不宣称与官服一致。
- 私服自定义占位、身份待核实曲目不进入日服历史牌子。实际授牌由游戏决定，快照不保证未来自动更新。
- 三种牌子范围不会改写玩家成绩或扩大落雪上传资格。统一元数据可能补齐估算 B50 的候选曲及参考 Rating；私服原始名单、顺序和原报总分保留。

真牌范围的进一步核对见 [TRUE_PLATE_AUDIT.md](TRUE_PLATE_AUDIT.md)：当前日服88首、含删曲106首。恢复包中的5首旧大陆版独占曲不进入日服范围；这些条目的身份已核实，不再归为疑似自制曲。
