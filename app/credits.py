"""In-app attribution: distinguish reused resources, references and local algorithms."""

KAREN='https://github.com/xszqxszq/KarenBot/blob/da03d8cc3e19edd698482c1c6e750a04655dcbfa/maimai/src/main/kotlin/maimai/'

CREDITS_HTML='''
<h2>现有功能</h2>
<p>原始与估算 B50、双 B50 对比、旧版 B40 估算、成绩与单曲查询、曲库筛选、随机选曲、牌子完成表、推分推荐、Rating 计算、成绩统计、文字猜歌与开字母、分数线容错、今日舞萌、条件完成表、自选 Best、段位配置、落雪同步与备份。</p>
<h2>算法与计算口径</h2>
<p><b>AquaDX 解析与 Best：</b>沿用 AquaSync 初版解析框架，Python 实现在 app/parser.py。achievement ÷ 10000 得百分比，优先读取 deluxscoreMax；同 ID / 难度分别保留达成率、DX 分、FC/AP、FS 的最佳值，次数取导出快照最大值，不把不同游玩的最佳字段伪装成一次成绩。字段对照 <a href="https://github.com/MewoLab/AquaDX/blob/master/src/main/java/icu/samnyan/aqua/sega/maimai2/model/userdata/UserEntities.kt">AquaDX UserEntities.kt</a>；未打包其服务端代码。</p>
<p><b>DX Rating / 评级：</b>app/calculations.py 的完整分段系数表，Decimal 计算 floor(定数 × min(达成率,100.5) × 系数 ÷ 100)。高分段、边界补偿与封顶参考 <a href="KARENmusic/Rating.kt">KarenBot Rating.calc</a>；低分段以本地 COEFFICIENTS 为准，Python 实现为本项目重写。</p>
<p><b>B50 / B40：</b>原始 B50 从 recent_rating / recent_rating_new 读取 B35 / B15 顺序，保留私服原报总分；卡片单曲 Rating 用公开参考定数计算，另列计算合计及差值。估算 B50 按参考库新旧分区分别取前 35 / 15；同分按定数、达成率、ID、难度排序。B40 使用前 25 / 15 和旧系数，参考 <a href="KARENmusic/Rating.kt">Rating.calcOld</a>，不是当前 B50。实现：app/b50_views.py、app/calculations.py、app/desktop_tools.py。</p>
<p><b>推分推荐：</b>本项目 app/local_tools.py：目标达成率依次为 97、98、99、99.5、100、100.5%；用目标 Rating − max(当前单曲 Rating, 对应 B35/B15 门槛) 估算收益，优先较小提升幅度。同一张谱面只给出第一个有效目标，单曲收益不能直接相加。表头按文本或真实数值排序，不按数字字符串排序。</p>
<p><b>牌子 / 条件完成 / 统计：</b>本地 app/calculations.py、app/desktop_tools.py：将 ≥100%，极 ≥FC，神 ≥AP，舞舞 ≥FSD；普通版本排除 Re:MASTER，真合并 maimai / PLUS 并排除 ID 70，不设真将；舞包含旧世代及 Re:MASTER。FC/AP、FS 和累计次数按 Best 快照统计。桌面提供私服曲库（日服现行）、国服曲库（KarenBot 国服曲目与牌子要求交集）、私服曲库（含删除曲目）三个独立快照；统计、未完成清单与图鉴使用同一分母，不据此宣称获得游戏授牌。国服不再沿用日服逐版本分组推算，而是使用 bot 的 requires/remasters 清单；自选 Best 按条件筛选再按 Rating 排序。功能参考 <a href="KARENquery/ComboQuery.kt">KarenBot ComboQuery</a>，筛选与计算逻辑由本项目实现。</p>
<p><b>分数线容错：</b>参考并重写 <a href="KARENcontroller/CalcController.kt">KarenBot CalcController</a>。TAP/TOUCH=500、HOLD=1000、SLIDE=1500、BREAK=2500；TAP GREAT 损失百分比=10000/加权总分，允许数量=总分×(101−目标达成率)/10000，BREAK 50 落按 0.25/BREAK 数量估算。物量缺失时不计算。实现：app/desktop_tools.py。</p>
<p><b>今日舞萌 / 随机 / 猜歌：</b>本项目算法：SHA256(玩家 ID|本地日期) 生成随机种子，使当天娱乐推荐可复现；随机选曲和文字猜歌使用 Python random.choice；开字母按 Unicode casefold 匹配。并非 KarenBot 服务端的同一随机结果。</p>
<p><b>双 B50 / 同步差异：</b>本项目 app/b50_views.py、app/score_diff.py、app/lxns.py：按 musicId / 谱面类型 / 难度对齐，比较达成率、DX 分、FC/FS；使用规范化 JSON 的 SHA256 指纹防止误用旧预览；读取备份、人工选择提交、回读核对。协议参考 <a href="https://maimai.lxns.net/docs/api/maimai">落雪 API</a>。密钥仅在进程内暂存，不写入数据目录。</p>
<p><b>版本 / 曲库合并 / 曲绘 ID：</b>本项目 app/unified_catalog.py、app/versions.py、app/private_catalog.py；按显式版本表排序、按 ID + 难度合并参考元数据。曲绘资源 ID = musicId % 10000，参考 <a href="KARENmusic/MusicInfo.kt">MusicInfo.resourceId</a>。新曲补充通过公开曲绘匹配（平均像素误差 &lt;3、第二候选差距 &gt;20）交叉核对；映射依据和来源存于 data/private_music_data.json。名称或精确定数无法核实则保持待核实，显示等级不代替精确定数。牌子三范围快照与公开曲绘ID匹配证据存于 data/plate_catalogs.json；详见 docs/PLATE_CATALOGS.md。</p>
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
<li><a href="https://github.com/xszqxszq/KarenBot-Resources/tree/main/data/maimai/templates">KarenBot-Resources templates</a>：复用背景、难度卡片底图、评级、FC/FS、等级徽章等 PNG，并参考 <a href="KARENcomponent/image/templates/RatingTemplate.kt">RatingTemplate</a> / <a href="KARENcomponent/image/templates/LevelTemplate.kt">LevelTemplate</a> 的图鉴形式。本项目用 Qt 重绘，未运行上游 HTML/Kotlin 渲染器；DX/标准小标识已改成本项目矢量绘制。游戏曲绘及标识归各自权利人。</li>
</ul>
<p>Rating 彩色对照表由本项目 app/rating_table.py 实现，调用现有 Decimal Rating 公式；同评级加 1 分门槛向上舍入至 0.0001%。布局参考用户提供的表格图片，未复制图片数值或素材。</p>
<p>推分推荐由 app/recommendation_scopes.py 分离私服参考与落雪国服定数、版本及候选池，再使用既有 recommendations 算法分别计算 B35/B15 替换收益；两种模式均基于本地导入成绩。数据来源沿用上方曲库说明。</p>
<p>统一曲库：成绩查询、B50、曲库、详情、推荐和牌子共享 UnifiedCatalog 元数据入口，保留各地区及版本变体。空字段不覆盖已核实值，定数来源单独记录；历史重收录版本、牌子要求清单与落雪上传资格分别保留。资料补齐可能改变估算Rating，私服原报数据不被改写。</p>
<p>成绩时间与排序：app/score_times.py、app/score_sorting.py为本项目实现，仅从导出的谱面时间或userPlaylogList读取真实最近记录，旧快照需重导，无时间保持未知。八种双向排序不写回成绩。</p>
<p>高清评级：<a href="https://github.com/mai-kit/mai-kit/tree/32572f7ffc5ae8fa3cc18dab6eff590fc4d17f4d/packages/assets/assets/rank">mai-kit原始D～SSS+透明PNG</a>，固定提交32572f7ffc5ae8fa3cc18dab6eff590fc4d17f4d，评级 256×120、状态 80×80；FC/AP/FS 状态原图来自同一提交的 assets/bonus；逐文件来源和SHA256见 rank_manifest.json 和 status_manifest.json。MIT声明保存在licenses/MaiKit-Assets-LICENSE.txt；游戏图形归SEGA等相应权利人。未复制上游程序代码。</p>
<h2>参考源码与依赖</h2>
<p>KarenBot 参考提交 <b>da03d8cc3e19edd698482c1c6e750a04655dcbfa</b>，上方已逐项列出参考算法及复用素材。KarenBot 与 KarenBot-Resources 的上游 MIT 许可已随软件附在 licenses 目录（源码包 docs/KarenBot-LICENSE.txt、KarenBot-Resources-LICENSE.txt）。AquaSync 的 Python、Qt 界面、SQLite、迁移与同步模块为本项目实现；没有运行 QQ bot 服务。</p>
<p>运行与构建依赖：<a href="https://www.python.org/">Python</a>（Decimal、hashlib、random、sqlite3、文件操作等标准库），<a href="https://doc.qt.io/qtforpython-6/">PySide6 / Qt for Python</a>（原生界面与绘制），<a href="https://sqlite.org/">SQLite</a>（本地数据库），<a href="https://www.python-httpx.org/">HTTPX</a>（网络请求），<a href="https://fastapi.tiangolo.com/">FastAPI</a>（兼容 API 模块，桌面版不启动服务），<a href="https://docs.pydantic.dev/">Pydantic</a> / <a href="https://www.starlette.io/">Starlette</a>（FastAPI 依赖），<a href="https://pyinstaller.org/">PyInstaller</a>（Windows 打包）。源码 requirements.txt / requirements-desktop.txt 记录固定版本；uvicorn 仅保留给兼容 API 启动，未用于桌面运行。</p>
'''.replace('KAREN',KAREN).replace('MewoLab/AquaDX/blob/master/','MewoLab/AquaDX/blob/4a0254ec198fe0448a2682eba82f8222a233605a/')
