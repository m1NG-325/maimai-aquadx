# 算法、公开数据与参考源码


<h2>现有功能</h2>
<p>原始与估算 B50、双 B50 对比、旧版 B40 估算、成绩与单曲查询、曲库筛选、随机选曲、牌子完成表、推分推荐、Rating 计算、成绩统计、文字猜歌与开字母、分数线容错、今日舞萌、条件完成表、自选 Best、段位配置、落雪同步与备份。</p>
<h2>算法与计算口径</h2>
<p><b>AquaDX 解析与 Best：</b>沿用 AquaSync 初版解析框架，Python 实现在 app/parser.py。achievement ÷ 10000 得百分比，优先读取 deluxscoreMax；同 ID / 难度分别保留达成率、DX 分、FC/AP、FS 的最佳值，次数取导出快照最大值，不把不同游玩的最佳字段伪装成一次成绩。字段对照 <a href="https://github.com/MewoLab/AquaDX/blob/4a0254ec198fe0448a2682eba82f8222a233605a/src/main/java/icu/samnyan/aqua/sega/maimai2/model/userdata/UserEntities.kt">AquaDX UserEntities.kt</a>；未打包其服务端代码。</p>
<p><b>DX Rating / 评级：</b>app/calculations.py 的完整分段系数表，Decimal 计算 floor(定数 × min(达成率,100.5) × 系数 ÷ 100)。高分段、边界补偿与封顶参考 <a href="https://github.com/xszqxszq/KarenBot/blob/da03d8cc3e19edd698482c1c6e750a04655dcbfa/maimai/src/main/kotlin/maimai/music/Rating.kt">KarenBot Rating.calc</a>；低分段以本地 COEFFICIENTS 为准，Python 实现为本项目重写。</p>
<p><b>B50 / B40：</b>原始 B50 从 recent_rating / recent_rating_new 读取 B35 / B15 顺序，保留私服原报总分；卡片单曲 Rating 用公开参考定数计算，另列计算合计及差值。估算 B50 按参考库新旧分区分别取前 35 / 15；同分按定数、达成率、ID、难度排序。B40 使用前 25 / 15 和旧系数，参考 <a href="https://github.com/xszqxszq/KarenBot/blob/da03d8cc3e19edd698482c1c6e750a04655dcbfa/maimai/src/main/kotlin/maimai/music/Rating.kt">Rating.calcOld</a>，不是当前 B50。实现：app/b50_views.py、app/calculations.py、app/desktop_tools.py。</p>
<p><b>推分推荐：</b>本项目 app/local_tools.py：目标达成率依次为 97、98、99、99.5、100、100.5%；用目标 Rating − max(当前单曲 Rating, 对应 B35/B15 门槛) 估算收益，优先较小提升幅度。同一张谱面只给出第一个有效目标，单曲收益不能直接相加。表头按文本或真实数值排序，不按数字字符串排序。</p>
<p><b>牌子 / 条件完成 / 统计：</b>本地 app/calculations.py、app/desktop_tools.py：将 ≥100%，极 ≥FC，神 ≥AP，舞舞 ≥FSD；普通版本排除 Re:MASTER，真合并 maimai / PLUS 并排除 ID 70，不设真将；舞包含旧世代及 Re:MASTER。FC/AP、FS 和累计次数按 Best 快照统计。桌面提供私服曲库（日服现行）、国服曲库（KarenBot 国服曲目与牌子要求交集）、私服曲库（含删除曲目）三个独立快照；统计、未完成清单与图鉴使用同一分母，不据此宣称获得游戏授牌。国服不再沿用日服逐版本分组推算，而是使用 bot 的 requires/remasters 清单；自选 Best 按条件筛选再按 Rating 排序。功能参考 <a href="https://github.com/xszqxszq/KarenBot/blob/da03d8cc3e19edd698482c1c6e750a04655dcbfa/maimai/src/main/kotlin/maimai/query/ComboQuery.kt">KarenBot ComboQuery</a>，筛选与计算逻辑由本项目实现。</p>
<p><b>分数线容错：</b>参考并重写 <a href="https://github.com/xszqxszq/KarenBot/blob/da03d8cc3e19edd698482c1c6e750a04655dcbfa/maimai/src/main/kotlin/maimai/controller/CalcController.kt">KarenBot CalcController</a>。TAP/TOUCH=500、HOLD=1000、SLIDE=1500、BREAK=2500；TAP GREAT 损失百分比=10000/加权总分，允许数量=总分×(101−目标达成率)/10000，BREAK 50 落按 0.25/BREAK 数量估算。物量缺失时不计算。实现：app/desktop_tools.py。</p>
<p><b>今日舞萌 / 随机 / 猜歌：</b>本项目算法：SHA256(玩家 ID|本地日期) 生成随机种子，使当天娱乐推荐可复现；随机选曲和文字猜歌使用 Python random.choice；开字母按 Unicode casefold 匹配。并非 KarenBot 服务端的同一随机结果。</p>
<p><b>双 B50 / 同步差异：</b>本项目 app/b50_views.py、app/score_diff.py、app/lxns.py：按 musicId / 谱面类型 / 难度对齐，比较达成率、DX 分、FC/FS；使用规范化 JSON 的 SHA256 指纹防止误用旧预览；读取备份、人工选择提交、回读核对。协议参考 <a href="https://maimai.lxns.net/docs/api/maimai">落雪 API</a>。密钥仅在进程内暂存，不写入数据目录。</p>
<p><b>版本 / 曲库合并 / 曲绘 ID：</b>本项目 app/versions.py、app/private_catalog.py；按显式版本表排序、按 ID + 难度合并参考元数据。曲绘资源 ID = musicId % 10000，参考 <a href="https://github.com/xszqxszq/KarenBot/blob/da03d8cc3e19edd698482c1c6e750a04655dcbfa/maimai/src/main/kotlin/maimai/music/MusicInfo.kt">MusicInfo.resourceId</a>。新曲补充通过公开曲绘匹配（平均像素误差 &lt;3、第二候选差距 &gt;20）交叉核对；映射依据和来源存于 data/private_music_data.json。名称或精确定数无法核实则保持待核实，显示等级不代替精确定数。牌子三范围快照与公开曲绘ID匹配证据存于 data/plate_catalogs.json；详见 docs/PLATE_CATALOGS.md。</p>
<p><b>界面 / 导出 / 迁移：</b>原生 Qt 控件、QPainter 图鉴、可见行封面缓存、缩放平移、卡片、分隔条、页签拖出和数值排序为本项目实现。缩放以鼠标位置为锚点，导出使用固定完整画布。目录迁移用 <a href="https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection.backup">SQLite backup</a> 生成一致快照、integrity_check 校验数据库、SHA256 校验普通文件，暂存后切换并原子保存设置；失败不改原目录配置，旧目录保留。</p>
<h2>曲库、配置与素材来源</h2>
<ul>
<li><a href="https://www.diving-fish.com/api/maimaidxprober/music_data">水鱼 music_data</a>：公共分析曲库、定数、版本及新旧标志，data/music_data.json，快照 2026-10-14。</li>
<li><a href="https://maimai.lxns.net/api/v0/maimai/song/list">落雪 song/list</a>：目标网站曲库、ID、谱面类型与版本，data/lxns_song_list.json；初始快照 2026-10-14，用户可主动更新。私服参考曲库不扩大上传资格。</li>
<li><a href="https://github.com/realtvop/SaltMeta">SaltMeta</a>：日服分区域谱面、曲名、定数、版本、BPM、谱师、物量及曲绘。参考曲库独立存储，来源标记 reference_only。</li>
<li><a href="https://otoge-db.net/maimai/data/music-ex.json">OTOGE DB music-ex</a> / <a href="https://github.com/zvuc/otoge-db">源码与数据说明</a>：CiRCLE / MAGiCAL 等补充参考元数据，2026-10-15 核对；并非私服实机定数的证明。</li>
<li><a href="https://git.fragrance.moe/mokurin000/maimaiDX-Api/src/commit/89e096bac6cd8cab40c403a2a89cea8db6789101/Data/musicDB.json">历史 musicDB</a>：删曲 ID → 名称对照（PERFECT HUMAN、目覚めRETURNER）。<a href="https://adxdls.saop.cc/en/charts?q=SAWTOWNE">ADX 目录</a>：ループザルーム名称与显示等级的补充参考，精确定数仍待核实；未打包其音频或谱面文件。</li>
<li><a href="https://github.com/xszqxszq/KarenBot-Resources/blob/main/data/maimai/course.json">KarenBot-Resources course.json</a>：30 项段位配置，2026-10-14 快照；展示配置与最佳成绩，不判断实际段位合格。</li>
<li><a href="https://github.com/realtvop/SaltMeta/tree/main/covers">SaltMeta 曲绘</a> 与 <a href="https://assets2.lxns.net/maimai/jacket/772.png">落雪公开曲绘端点示例</a>：内置 1702 张 PNG；三个牌子范围新增曲绘176张，历史曲绘ID444暂无可核实图片，保留占位。未核实曲绘显示占位图。详情见 data/report_assets/cover_manifest.json 和 SOURCES.md。</li>
<li><a href="https://github.com/xszqxszq/KarenBot-Resources/tree/main/data/maimai/templates">KarenBot-Resources templates</a>：复用背景、难度卡片底图、评级、FC/FS、等级徽章等 PNG，并参考 <a href="https://github.com/xszqxszq/KarenBot/blob/da03d8cc3e19edd698482c1c6e750a04655dcbfa/maimai/src/main/kotlin/maimai/component/image/templates/RatingTemplate.kt">RatingTemplate</a> / <a href="https://github.com/xszqxszq/KarenBot/blob/da03d8cc3e19edd698482c1c6e750a04655dcbfa/maimai/src/main/kotlin/maimai/component/image/templates/LevelTemplate.kt">LevelTemplate</a> 的图鉴形式。本项目用 Qt 重绘，未运行上游 HTML/Kotlin 渲染器；DX/标准小标识已改成本项目矢量绘制。游戏曲绘及标识归各自权利人。</li>
</ul>
<h2>参考源码与依赖</h2>
<p>KarenBot 参考提交 <b>da03d8cc3e19edd698482c1c6e750a04655dcbfa</b>，上方已逐项列出参考算法及复用素材。KarenBot 与 KarenBot-Resources 的上游 MIT 许可已随软件附在 licenses 目录（源码包 docs/KarenBot-LICENSE.txt、KarenBot-Resources-LICENSE.txt）。AquaSync 的 Python、Qt 界面、SQLite、迁移与同步模块为本项目实现；没有运行 QQ bot 服务。</p>
<p>运行与构建依赖：<a href="https://www.python.org/">Python</a>（Decimal、hashlib、random、sqlite3、文件操作等标准库），<a href="https://doc.qt.io/qtforpython-6/">PySide6 / Qt for Python</a>（原生界面与绘制），<a href="https://sqlite.org/">SQLite</a>（本地数据库），<a href="https://www.python-httpx.org/">HTTPX</a>（网络请求），<a href="https://fastapi.tiangolo.com/">FastAPI</a>（兼容 API 模块，桌面版不启动服务），<a href="https://docs.pydantic.dev/">Pydantic</a> / <a href="https://www.starlette.io/">Starlette</a>（FastAPI 依赖），<a href="https://pyinstaller.org/">PyInstaller</a>（Windows 打包）。源码 requirements.txt / requirements-desktop.txt 记录固定版本；uvicorn 仅保留给兼容 API 启动，未用于桌面运行。</p>

## Rating 彩色对照表

- `app/rating_table.py` 使用本项目现有 `app/calculations.py::rating` 和系数表动态生成，未从参考图片抄录数值或素材。评级系数来源沿用上文的 KarenBot Rating 参考。
- 默认定数范围 12.0～15.0，每行 0.1，可调整为 0.1～20.0。列包含 S～SSS+ 达成率及临界点。
- 加 1 分门槛先求 `(起点Rating + 1) × 100 / (定数 × 当前系数)`，向上舍入到 0.0001%；在下一个系数区间前无法达到时显示 —。
- 表格点击填入原计算器，不写入成绩或改变 B50；颜色仅用于区分 Rating 数值。

## 分地区推分推荐

`app/recommendation_scopes.py` 将两套定数、分组与候选池分开，再调用既有 `app/local_tools.py::recommendations` 算法。私服参考合并基础曲库、日服含删曲快照与私服补充元数据；排除比所选版本更晚的曲目。私服导出新曲组能唯一对应参考版本时自动选择，否则默认最新参考版本并提示手动核对。国服采用落雪曲库的普通谱面、定数与当前年度版本分组，排除停用或版本未知谱面。

两个模式都只使用本地导入成绩；未收录、特殊谱面和缺定数不参与推荐。B35/B15门槛分别由各自已计算成绩建立；未满组时门槛为0。收益为目标Rating减去当前Rating与组门槛的较大值，仅表示单谱替换收益，不可相加。原始成绩、上传资格及旧版兼容推荐接口不变。

## 统一桌面曲库

`app/unified_catalog.py::UnifiedCatalog` 是桌面共享元数据入口，按 musicId、难度、地区、版本保存变体；没有把不同地区定数压成同一个值。私服优先级从低至高为基础库、私服补充、日服历史快照、日服现行快照；国服为KarenBot国服参考加落雪国服缓存。相同版本优先用高优先级非空字段，未知值不覆盖已核实值，并单独保留定数来源。重收录曲目的历史版本仍保留在牌子分母中。全部曲库以私服参考为同谱面默认展示，国服变体可单独查询。

共享层每次由当前数据源构造，不向成绩表写入合并结果；新版本元数据可自动用于已有玩家。成绩、原始B50补名和参考单曲Rating、估算B50、查询/随机、推荐、详情和其他桌面工具统一读取。B50新旧分组识别沿用推荐中的导出新曲版本识别规则；估算与私服原报分开。牌子成员资格仍受原范围要求清单控制；落雪导出/上传资格依旧只使用落雪已确认收录的曲库，统一展示不增加远端资格。旧版独立兼容API的基础曲库计算保持其协议口径。

## 最近游玩与成绩排序

`app/score_times.py` 仅从谱面记录明确的lastPlayedAt/lastPlayDate等字段及导出userPlaylogList中的userPlayDate/playDate解析真实日期，按musicId+难度选最大时间；不使用登录时间、排列位置或Rating猜测。ISO日期（含时区）、紧凑日历日期及Unix秒/毫秒可解析，无时区按UTC+8处理，非法/零时间忽略。只存最近时间及字段来源，不保留日志中的多人昵称、店铺信息等无关字段；逐局日志不会额外制造最佳成绩条目。

`app/score_sorting.py` 实现八种双向排序，缺定数、缺Rating与缺时间永远在末尾，平手按达成率降序、ID、难度稳定排列。FC排序为AP+、AP、FC+、FC、无；AP排序为AP+、AP、其它。排序不写回成绩。

## 高清评级素材

14种D～SSS+原始透明PNG来源：[mai-kit rank目录](https://github.com/mai-kit/mai-kit/tree/32572f7ffc5ae8fa3cc18dab6eff590fc4d17f4d/packages/assets/assets/rank)，固定提交32572f7ffc5ae8fa3cc18dab6eff590fc4d17f4d，每张256×120，未修改像素。逐文件URL与SHA256见data/report_assets/rank_manifest.json，MIT声明保留在docs/MaiKit-Assets-LICENSE.txt。游戏图形与商标归SEGA等相应权利人；未复制上游程序代码。Qt直接从原图绘制，详情根据设备像素比生成显示缓存。


2026-10-17：FC/FC+/AP/AP+、FS/FS+/FSD/FSD+/SYNC 和空状态图标采用 mai-kit/mai-kit 固定提交 32572f7ffc5ae8fa3cc18dab6eff590fc4d17f4d 的 packages/assets/assets/bonus 原始 80×80 透明 PNG；未放大伪造源分辨率。逐文件来源和 SHA256 见 data/report_assets/status_manifest.json；许可见 docs/MaiKit-Assets-LICENSE.txt。游戏素材权利归 SEGA 及相应权利人。
