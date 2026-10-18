# AquaSync 1.0 验证范围

- 功能版本全量自动测试：104 passed，1 条既有依赖弃用警告。
- 覆盖解析、SQLite、Rating 边界、B50、导出、模拟同步、报表、曲库自动筛选、列排序、详情、缩放平移和目录迁移。
- 本公开记录不包含个人测试样本、账号、成绩数值、统计结果、本机路径、截图或原始日志；个人回归数据不随公开源码发布。
- Windows 单文件软件提供独立启动自检；界面使用离屏渲染检查，不作为真人桌面操作验收。
- 发行内容通过白名单生成，公开 JSON 限于歌曲、谱面和段位元数据。


## 1.0.1 完整参考曲库牌子进度

- 专项测试 19 passed；最终全量测试 106 passed，54.27 秒，1 条既有依赖弃用警告。
- 牌子默认使用日服参考优先、分析库补缺的合并曲库，版本列表从 20 组补为 28 组（包含真、舞汇总项），涵盖已收录的各 DX PLUS、CiRCLE、CiRCLE PLUS、MAGiCAL。
- 提供原分析曲库切换；图鉴分母、总览、未完成列表与导出图使用同一选定范围，图片标明当前范围。
- 使用合成记录验证新版本完成状态和图片导出；回归测试确认 B50、原始导入和落雪上传资格不因牌子范围改变。
- 只列出有可核实谱面数据的版本，未收录的未来版本不编造空进度；参考完成表不代表官服授牌。
- 已检查原生离屏渲染，不代替真人桌面验收。发行包继续排除个人数据库、导出、原始样本、截图和日志。

修改文件：app/__init__.py、app/desktop_core.py、app/desktop_ui.py、app/report_models.py、app/report_view.py、app/credits.py、README.md、start-desktop.bat、docs/DESKTOP.md、docs/ALGORITHMS_AND_SOURCES.md、docs/TEST_RESULTS.md、tests/test_report_models.py；新增 tests/test_plate_catalog_scope.py。


## 2026-10-17 三个地区曲库范围

- 专项模块测试：21 passed；补齐历史档案及排除旧宴谱后，曲库专项4 passed。
- 最终全量回归：108 passed，58.59秒，1条既有 Starlette/httpx 弃用警告。
- 用合成成绩验证三个范围的统计、缺失筛选、全部版本/牌子分母、同名曲区分、历史曲详情、PNG导出，原始成绩/B50/落雪上传资格不变。
- 同一UNiVERSE极：日服现行268张、国服492张、含删除曲目304张；合成删曲记录仅在含删曲范围计入，结果分别0/268、0/492、1/304。
- 检查1400×900离屏窗口和整图导出。离屏截图不代替真人桌面操作验收。
- 日服官方现行1585个曲目类型条目（SD/DX分别计）、6492张难度谱面；国服按可怜bot快照及明确要求清单；含删曲范围7292张难度谱面。
- 新增176张可解码公开曲绘；历史ID444三个公开端点无可用图片，保留占位。

修改文件：app/calculations.py、app/report_models.py、app/desktop_core.py、app/desktop_ui.py、app/credits.py、AquaSync.spec、README.md、start-desktop.bat、docs/DESKTOP.md、docs/ALGORITHMS_AND_SOURCES.md、docs/TEST_RESULTS.md、tests/test_report_models.py、tests/test_plate_catalog_scope.py、data/report_assets/cover_manifest.json、data/report_assets/SOURCES.md、data/report_assets/covers/（176张新增）。新增：app/plate_catalogs.py、tools/build_plate_catalogs.py、data/plate_catalogs.json、docs/PLATE_CATALOGS.md。

- 单文件EXE从系统临时目录启动，隔离合成数据自检退出0；13个原生页面、Rating315检查和PNG导出通过。已核对内嵌三范围曲库与源JSON字节一致，未包含SQLite数据库或游戏.ma2文件。


## 1.1：版本名统一与真牌核对

- 专项测试21项通过；旧名称参数兼容测试16项通过；最终全量109 passed，62.61秒，1条既有依赖弃用警告。
- MiLK PLUS统一显示为maimai MiLK PLUS；旧数据库及旧参数兼容，数据库内原始参考快照不被改写。
- 含删除曲目真牌106首/424张；日本现行真牌88首/352张，88个ID与游戏真牌MusicGroup006101完全一致。18首历史曲已全部计入。
- 与恢复包初代标签相比剩余的5首已核实为旧大陆版独占曲，保持在日服口径之外。完整依据见TRUE_PLATE_AUDIT.md。
- 软件版本号与README更新为1.1，启动器优先dist/v1.1/AquaSync.exe。

本次修改：app/__init__.py、app/versions.py、app/calculations.py、app/database.py、app/plate_catalogs.py、tools/build_plate_catalogs.py、data/plate_catalogs.json、tests/test_plate_catalog_scope.py、tests/test_private_catalog.py、README.md、start-desktop.bat、docs/DESKTOP.md、docs/PLATE_CATALOGS.md、docs/TEST_RESULTS.md；新增docs/TRUE_PLATE_AUDIT.md。

### 1.1 EXE 最终验证

- `dist/v1.1/AquaSync.exe` 独立测试启动退出码 0；原生界面、13 个页面、B50 图片及牌子图片导出自检通过。使用独立数据目录与虚构成绩。
- 已检查 EXE 内版本为 `1.1`，MiLK PLUS 规范名称及内嵌牌子曲库与当前源码一致。
- EXE 未包含 SQLite 数据库、MA2 谱面文件或 JSONL 日志；SHA256 校验文件已生成。

## 2026-10-17 Rating 彩色对照表

- 专项测试18项通过；全量回归116 passed，68.31秒，1条既有 Starlette/httpx 弃用警告。
- 默认12.0～15.0定数、0.1间隔、14列；覆盖0.1～20.0全部定数，验证加1分门槛与前一个0.0001%刻度、临界点、无可达门槛、非法范围。
- 合成空白数据目录原生自检通过；检查1600×1000及1000×760离屏截图，窄窗口可横向滚动，保留下方计算器。离屏检查不代替真人桌面使用验收。
- 只改计算工具展示，不改原始Rating算法、成绩或数据库；未改README，未操作GitHub或Release。

修改文件：app/rating_table.py（新增）、app/desktop_ui.py、app/credits.py、tests/test_rating_table.py（新增）、start-desktop.bat、docs/DESKTOP.md、docs/ALGORITHMS_AND_SOURCES.md、docs/TEST_RESULTS.md。

- 最终 `dist/rating-table/AquaSync.exe` 从系统临时目录启动，自检退出0、frozen=true、players=0、Rating315校验通过；已检查内嵌表格模块和默认31行数据，未打包个人数据库、日志或MA2。校验文件为同目录SHA256SUMS.txt。

## 2026-10-17 私服与国服推分推荐分离

- 新推荐范围专项3项通过；既有推荐、计算、表格排序与设置专项18项通过。
- 最终全量119 passed，74.92秒，1条既有Starlette/httpx弃用警告。
- 验证相同导入成绩在不同地区使用不同定数和曲目池，私服版本识别、手动选择、未来曲排除、国服停用曲与缺定数排除、缺失数量、数值排序、切换颜色和原始成绩不变。
- 1400×900原生离屏渲染已检查私服和国服页面，仅使用虚构成绩；离屏检查不代替真人桌面验收。
- 兼容旧版推荐接口；仅桌面新增独立范围，两种模式明确标注本地导入成绩口径。README和GitHub发布内容未改动。

修改文件：app/recommendation_scopes.py（新增）、app/desktop_core.py、app/desktop_ui.py、app/credits.py、tests/test_recommendation_scopes.py（新增）、tests/test_desktop_settings.py、start-desktop.bat、docs/DESKTOP.md、docs/ALGORITHMS_AND_SOURCES.md、docs/TEST_RESULTS.md。

- 最终`dist/recommend-scopes/AquaSync.exe`从系统临时目录独立启动，隔离合成成绩自检退出0；13页、Rating315与frozen检查通过。已确认内嵌两地区推荐模块和Rating表格模块，未包含数据库、MA2或JSONL日志；SHA256校验文件已生成。

## 2026-10-17 统一桌面曲库

- 新跨页面专项3项通过；牌子、推荐、设置专项13项通过；完整功能回归122 passed，125.46秒，1条既有Starlette/httpx弃用警告。
- 私服统一展示7292张普通谱面，国服5502张；相对旧基础库与私服补充的并集新增849个ID+难度组合。牌子历史版本成员保留，重收录版本不压成单一历史记录。
- 合成新增曲验证：成绩查询、曲库、原始B50卡片、牌子元数据、推荐与详情均能识别同一曲名及定数；更新来源快照后再次查询全部同步，数据库原成绩与原参考快照不被合并写回。
- 另测地区定数隔离、同版本空字段不覆盖已知值、定数来源、历史重收录变体、返回值防外部改写、曲库地区切换。
- 原始B50名单、顺序、原报总分保留；估算B50和单曲Rating可以随完整资料重新计算。落雪上传资格仍以落雪真实收录为准。旧独立兼容API保留原基础库计算口径。
- 首轮旧断言期待新增曲无法计入Rating，现改为验证共享曲库已计入；清理旧import时发现缩进错误并已修复，最终完整回归通过。

修改文件：app/unified_catalog.py（新增）、app/desktop_core.py、app/desktop_ui.py、app/private_catalog.py、app/plate_catalogs.py、app/recommendation_scopes.py、app/credits.py、tests/test_unified_catalog.py（新增）、tests/test_plate_catalog_scope.py、start-desktop.bat、docs/DESKTOP.md、docs/PLATE_CATALOGS.md、docs/ALGORITHMS_AND_SOURCES.md、docs/TEST_RESULTS.md。

- 最终`dist/unified-catalog/AquaSync.exe`从系统临时目录独立启动，隔离合成新增曲自检退出0；新增曲Can Do BASIC在成绩页解析、B50计算（参考79分，合成原报123保持原值）及B50/牌子PNG导出通过。内嵌统一曲库、两地区推荐与Rating表格模块已确认，不含数据库、MA2或JSONL日志；SHA256文件已生成。

## 2026-10-17 成绩查询紧凑卡片

- 最终桌面与布局专项9 passed，36.24秒；针对本次视觉和交互范围验证，未重复全量算法/API测试。
- 保留一行两首、达成率顺序、搜索筛选、导出及双击详情；单卡选中替代同时选中整行。
- 全屏列宽大于等于568时行高112，相比原146减少约23%；窄窗口行高132，缩放时自动重新布局。
- 放大封面、曲名、达成率和Rating；超宽卡片将定数、DX分、次数放到中部，加入难度色条与评级/FC/FS图标、悬停和选中状态。
- 已检查2560×1440（与用户参考图相同尺寸）、1320×900、1000×760原生离屏渲染，仅使用合成成绩；离屏检查不代替真人桌面操作验收。
- 不改原始成绩和计算逻辑；README及GitHub发布内容未改动。

修改文件：app/desktop_ui.py、tests/test_score_card_layout.py（新增）、start-desktop.bat、docs/DESKTOP.md、docs/TEST_RESULTS.md。

- 最终`dist/score-cards/AquaSync.exe`从系统临时目录启动，2560×1440隔离合成数据自检退出0；32张成绩为16行、13页、Rating315与frozen检查通过。已验证包含统一曲库、分地区推荐和Rating表格模块，不含数据库、MA2或JSONL日志；SHA256已生成。

## 2026-10-17 难度底色、高清评级与成绩排序

- 时间与排序/高DPI素材专项14项通过；初步解析和布局专项15项通过。最终全量127 passed，139.26秒，1条既有Starlette/httpx弃用警告。
- 读取userMusicDetailList的已玩谱面Best快照；导出userPlaylogList按musicId+难度关联userPlayDate/playDate最近时间，日志不额外制造Best条目，不提取多人昵称、店铺或账号字段。只读原导出验证已通过，未在公开记录中保留实际日期、账号或成绩数值。
- 八种双向排序均已验证，未知时间/定数/Rating永远在末尾，独立FC/AP状态可排序；Best与最近游玩分离、时间格式/非法值、原数据不变和界面联动通过。旧快照需重新导入完整JSON，缺时间不猜测。
- 难度改为半透明卡片底色；14种评级替换为256×120原始透明PNG，固定mai-kit公开提交，来源/哈希/许可已保存，支持高DPI直接绘制。已检查2560×1440、1320×900、1000×760合成数据离屏图，包含最近时间显示，不代替真人桌面验收。
- 最终本地新文件为dist/v1.1/AquaSync-latest.exe，现有AquaSync.exe及已发布内容保留。README和GitHub Release未改动。

修改文件：app/parser.py、app/score_times.py（新增）、app/score_sorting.py（新增）、app/desktop_ui.py、app/credits.py、tests/test_score_ordering.py（新增）、AquaSync.spec、start-desktop.bat、data/report_assets/rating-rank_*.png（14种）、data/report_assets/rank_manifest.json（新增）、data/report_assets/SOURCES.md、docs/MaiKit-Assets-LICENSE.txt（新增）、docs/DESKTOP.md、docs/ALGORITHMS_AND_SOURCES.md、docs/TEST_RESULTS.md。

- 最终dist/v1.1/AquaSync-latest.exe从系统临时目录启动自检退出0；32张合成Best为16行，24张真实合成时间关联成功，13页、Rating315和B50/牌子导出通过。逐项检查包内14张评级素材256×120及SHA256与来源清单一致，许可证和新旧功能模块均在；无数据库、MA2或JSONL日志。新校验文件为SHA256SUMS-latest.txt，不覆盖旧版校验文件。


## 2026-10-17 高清状态、评级位置及难度表格

- 最终全量：129 passed，159.12秒，1条既有Starlette/httpx弃用警告。专项首轮16项通过；B50顶部留白回归修正后，详情/像素边界/高清状态/难度表格6项通过，再完成上述最终全量。
- FC/FC+/AP/AP+、FS/FS+/FSD/FSD+/SYNC/空状态共10张80×80原始透明PNG，逐项SHA256与来源清单一致；详情高DPI绘制通过。源素材和许可来自固定mai-kit公开提交。
- 曲库、私服/国服推分推荐及段位表均以难度作为半透明底色；修复Qt主题遮盖BackgroundRole问题，离屏渲染确认生效。排序后的颜色与musicId仍对应。全部30组段位配置所列曲目都有打包曲绘；双击打开详情的ID经过验证。
- 评级移到ACC后方，高度按ACC字号缩放，窄窗口按可用宽度缩小；B50白条评级从30×15增到40×18，顶部保留两像素间隔，状态不越过右边框。已查看2560×1440、1320×900、1000×760成绩页及曲库/推荐/段位/B50合成数据渲染，不代替用户实际操作验收。
- 最终dist/v1.1/AquaSync-latest.exe从系统临时目录启动自检退出0，native/frozen=true、13页、Rating315、32张虚构成绩显示16行，段位表截图曲绘和底色正确。包内10张状态图SHA256、模块、最新来源说明和许可均核对通过，无sqlite3/db/ma2/jsonl文件。校验值在SHA256SUMS-latest.txt。原始AquaSync.exe、个人资料、README、GitHub和Release保留不改。

修改文件：
- app/desktop_ui.py：评级紧随ACC、自适应字号、难度公共底色与表格绘制、段位曲绘/详情、状态图高DPI。
- app/report_view.py：B50评级放大与白条间隔。
- app/credits.py：软件内高清状态来源说明。
- tests/test_difficulty_tables.py（新增）：状态图原始尺寸/透明度/哈希/DPR、排序配色、全部段位曲绘身份、推荐地区配色。
- data/report_assets/rating-icon_{fc,fcp,ap,app,fs,fsp,fsd,fsdp,sync,none}.png（10张替换）。
- data/report_assets/status_manifest.json（新增）：逐文件公开来源、尺寸与哈希。
- data/report_assets/SOURCES.md、docs/ALGORITHMS_AND_SOURCES.md、docs/DESKTOP.md、docs/TEST_RESULTS.md。
- 本地构建输出：dist/v1.1/AquaSync-latest.exe、dist/v1.1/SHA256SUMS-latest.txt；隔离验证资料在.validation，临时打包配置在build/status-icons。


## 1.2 定版（2026-10-17）

- 统一版本号改为1.2，窗口标题/顶部版本及Qt应用版本共用app.__version__；启动器优先dist/v1.2/AquaSync.exe。既有1.1程序保留。
- 本次针对性回归16 passed，21.05秒（排序、高DPI素材/状态、Rating表格、统一曲库）；功能代码沿用上一轮129项全量通过的版本，本次只改版本定义与启动路径。
- 最终EXE内app模块确认版本1.2，所需五个新增功能模块、14种高清评级及10种状态图的SHA256均核验通过；许可证完整，未包含db/sqlite3/jsonl/ma2文件。
- 系统临时目录运行隔离虚构成绩自检退出0，native/frozen=true、13页、32张成绩/16行、Rating315通过。已查看1320×900的EXE截图，顶部显示AquaSync 1.2。
- 修改文件：app/__init__.py、start-desktop.bat、docs/CHANGELOG-1.2.md（新增）、docs/TEST_RESULTS.md、docs/DESKTOP.md。构建输出dist/v1.2/AquaSync.exe、SHA256SUMS.txt。
- README、用户原始资料、数据库和GitHub/Release未更改。完整对比见CHANGELOG-1.2.md。


## 2.0 完整本地档案（2026-10-17）

- 解析/时间排序旧模块14项通过；新档案数据层4项通过；新页面与档案专项6项通过；集成布局与迁移15项通过。
- 功能版本全量回归135 passed，187.70秒，1条既有Starlette/httpx弃用警告。之后完成窄窗口标签页调整及可选状态/收藏ID容错，最终档案/界面/布局/设置专项16 passed，76.41秒。
- 测试涵盖：字段隐私白名单、坏行跳过、区段缺失与空列表、缺字段不补零、UTC+8跨日、逐局与Best独立、判定覆盖、成对FAST/LATE比例、原始候选名单、全量分页排序、日期/难度/曲目筛选、单局详情、单曲曲线、旧档案清空、CSV公式防护、名称XML补丁优先级、用户名称资料与档案迁移。
- 用用户指定真实导出在私有隔离目录验证全部新页面与六类养成标签；不写现用资料，不改原JSON，不在公开记录中存账号、原始成绩或截图。源文件哈希不变，敏感字段排除检查通过。
- 查看1600×1000、1320×900、1000×760原生离屏渲染。修复窄窗口两图挤压，走势图与当局详细数据使用标签页；日历表头对比度已修正。离屏与自检不替代用户实际交互验收。
- 最终dist/v2.0/AquaSync.exe已分别从系统临时目录启动四个新页面，自检均ok/native/frozen=true、版本2.0、17页、Rating315检查通过；仅使用虚构外部JSON。内嵌公共名称索引12197项，与源码字节一致，五个档案模块及共享曲库/排序/Rating模块完整。
- 单曲选择另用隔离本地资料核实Qt元组键和真实匹配点数一致；并补强自动化断言。
- 包内没有db/sqlite3/jsonl/ma2、原始导出、测试或私有验证目录；用户数据不进入名称元数据。SHA256SUMS.txt已生成。原有版本、个人资料、README与GitHub/Release保留。

修改文件：
- 新增app/archive_data.py、app/archive_analysis.py、app/collection_metadata.py、app/archive_widgets.py、app/archive_ui.py。
- 修改app/parser.py、app/desktop_core.py、app/desktop_ui.py、app/credits.py、app/__init__.py、desktop.py、AquaSync.spec、start-desktop.bat。
- 新增data/collection_metadata.json（本地游戏XML公共名称/ID快照，无个人数据）。
- 新增tests/test_archive_data.py、tests/test_archive_ui.py；修改tests/test_desktop.py的页面数量断言。
- 新增docs/ARCHIVE-2.0.md、docs/CHANGELOG-2.0.md；修改docs/DESKTOP.md、docs/ALGORITHMS_AND_SOURCES.md、docs/TEST_RESULTS.md。
- 本地输出dist/v2.0/AquaSync.exe、dist/v2.0/SHA256SUMS.txt；合成测试记录在.validation，真实资料验证仅在.private-local。

## 2.0 历史页布局与状态修订（2026-10-18）

- 模块专项先通过5项，再通过新增分页/详情/底色测试6项；最终全量回归138 passed，223.42秒。1条既有Starlette/httpx弃用警告，无失败。
- 新增断言：10/20/50/100分页，先全量排序再分页，FC/AP仅四种已达成状态，定数列位置与来源，详情与当前页一致，切页清空旧详情，完整判定列宽与五行高度，窄窗口上下布局/宽窗口左右布局，以及五种难度选中后两个共享绘制器的实际像素色。
- 像素测试最初未计算半透明颜色与背景合成，修正测试预期后专项与最终完整回归通过；未为通过测试改变难度颜色。
- 使用虚构137局数据和私有隔离成绩快照，检查2560×1440、1320×900、1000×760原生离屏预览。详情分封面与曲名、达成率/评级、六项指标、时间地点、完整判定表；窄屏上下分区可拖动并滚动查看。离屏检查与启动自检不替代用户真实鼠标交互验收。
- dist/v2.0/AquaSync-latest.exe从系统临时目录启动，虚构数据自检退出0；ok/native/frozen=true、版本2.0、17页、137条历史、12197项名称、Rating315均通过。
- 包含最终HistorySplitter与档案模块；内嵌公共名称索引字节与源码相同；未发现个人数据库、原始导出、ma2、测试夹具和私有验证目录。SHA256SUMS-latest.txt已生成，SHA256为cf19c34a076824b155cd7b05236d73dfea62630a4f5d0c8074ca2dec9c65c4af。
- FAST/LATE包含/排除P开关未实施：导出缺少Perfect的快慢拆分，无法准确计算。原始计数保持原样；FS只从历史显示移除，原始字段与其他页面保留。
- 正在使用的旧EXE与原校验文件均保留，启动脚本优先使用AquaSync-latest.exe。未操作GitHub或Releases；README文件哈希前后一致。

本次修改文件：app/desktop_ui.py、app/archive_ui.py、app/archive_widgets.py；tests/test_archive_ui.py、tests/test_difficulty_tables.py；start-desktop.bat；docs/ARCHIVE-2.0.md、docs/CHANGELOG-2.0.md、docs/TEST_RESULTS.md。
本次输出：dist/v2.0/AquaSync-latest.exe、dist/v2.0/SHA256SUMS-latest.txt。合成验证日志仅在.validation，真实快照预览仅在.private-local，均不用于发布。

## 2.0 历史表居中与轴标题修正（2026-10-18）

- 历史记录除曲目外各列正文居中；曲目仍靠左。右侧音符判定表标题与数据居中，左上角改为“音符\判定”，数据方向仍为行音符、列判定。
- tests/test_archive_ui.py模块3 passed，20.08秒；断言覆盖每种分页大小下的居中、排序后保持、曲目靠左和轴标题。
- 已检查2560×1440原生离屏预览；本次为显示修正，未改数据与算法。
- 修改文件：app/archive_widgets.py、app/archive_ui.py、tests/test_archive_ui.py、docs/ARCHIVE-2.0.md、docs/TEST_RESULTS.md。README、GitHub与Releases未操作。
- 本次重新打包的AquaSync-latest.exe独立启动自检退出0，ok/native/frozen=true、版本2.0；包内容检查通过，SHA256SUMS-latest.txt已更新。新版SHA256：4388d4cf5cfefdfa84a26897b59718835d9cc565163aa013393169796b0143a9。

## 2.0 紧凑判定、日历跳转与ACC区间（2026-10-18）

- 模块首轮8项通过；新增日期/ACC测试后9项通过；最终档案数据、UI和难度绘制相关回归12 passed，35.49秒。
- 新测试覆盖日期表排序后双击跳转、三日每日记录数50/50/37、ACC含上下界、无ACC排除、反向区间提示、关闭筛选恢复、仅影响判定分析而不影响历史和日历，以及大小表初始完整表头/五行数据尺寸。
- 检查2560×1440、1320×900、1000×760的原生离屏预览；常规窗口完整显示表格，窄窗口保留滚动。单局判定外层大框已去掉，日历与次数折线并排，日期列表保留在下方。
- 本次修改：app/archive_ui.py、app/archive_widgets.py、app/archive_analysis.py、tests/test_archive_ui.py、docs/ARCHIVE-2.0.md、docs/TEST_RESULTS.md。个人资料、README、GitHub和Releases未修改。
- 最后收紧覆盖数表头后UI模块4 passed，25.77秒；EXE内最终ACC控件与表头代码核对通过，独立启动自检退出0、版本2.0、17页。包隐私检查通过，SHA256SUMS-latest.txt已更新；SHA256为55f5d105cfa8471b5c3f1aa8acf904b0479280aa0c1499974543f7e4c8c1a490。

## 2.0 日历上下布局、整数刻度与正式文件替换（2026-10-18）

- 每日次数使用整数边界与互不重复的整数刻度；Rating/ACC图保持原小数精度。折线独占上方，下方日历与日期列表并排，分隔条可拖动。
- 判定分析移除每页数量、上一页与下一页控件，保留筛选、全量排序、ACC区间与CSV。
- UI相关4 passed，25.50秒；新增断言覆盖多种范围整数刻度、其他图精度保持、上下/左右分区顺序与分页控件隐藏。检查2560×1440、1320×900、1000×760离屏预览。
- 新版先在隔离目录构建，包版本/代码/名称元数据/隐私检查通过，独立自检退出0，ok/native/frozen=true、版本2.0、17页。
- 按用户明确授权关闭现用旧版后替换dist/v2.0/AquaSync.exe。复制前后SHA256一致；v2.0仅剩AquaSync.exe与SHA256SUMS.txt，已删除旧latest包及对应校验文件。用户数据库、原始JSON与README未改，未操作GitHub或Release。
- 修改文件：app/archive_widgets.py、app/archive_ui.py、tests/test_archive_ui.py、start-desktop.bat、docs/ARCHIVE-2.0.md、docs/CHANGELOG-2.0.md、docs/TEST_RESULTS.md。
- 正式EXE SHA256：2d721d5db76b550344875fd1fe07575b5e229e6446f22afb5d0a86ac92298a8e。

## 2.0 Rating作用范围与单曲ACC区间（2026-10-18）

- UI首轮5 passed，28.22秒；最终档案UI、解析与共享难度绘制相关13 passed，42.45秒。
- 新断言覆盖账号/单曲控件作用范围、独立ACC区间含边界、区间与选曲交集、反向区间提示、关闭恢复、账号Rating不受单曲区间影响、单曲记录与图一致、标签切换关联表，以及同一横坐标不同纵坐标的数据点悬停定位与远离隐藏。
- 预览检查2560×1440、1320×900、1000×760；Rating轴整数，ACC轴4位小数，图表与记录表空间调整。保留原始零值与回落，未伪造连续增长。
- 修改文件：app/archive_ui.py、app/archive_widgets.py、tests/test_archive_ui.py、docs/ARCHIVE-2.0.md、docs/TEST_RESULTS.md。README与GitHub/Release未改，个人资料未改。
- 新版包内最终模块与隐私检查通过，Rating页面独立启动自检退出0，ok/native/frozen=true、2.0、17页。正式AquaSync.exe已覆盖，复制校验一致；v2.0仍只有EXE和SHA256SUMS.txt。SHA256：d0673384a0f464c24119931871c3068253c548ebd6af6b0b1f6e4f40e84325d7。

## 2.0 走势跳转、日期区间与档案图片（2026-10-18）
- 档案 UI、数据解析与难度表相关 15 项测试通过（48.29 秒）。新增覆盖排序翻页后双击定位曲目与难度、日期闭区间、反向区间提示、默认 ACC 97%、图片清单路径安全和角色图标实际加载。
- 检查 1320×900 离屏界面截图；不能替代用户实际操作体验确认。
- 本地资源通过 UnityPy 解码，图片映射：角色 1404、搭档 27、地图底图 35、课程曲绘组合 301、登录奖励 24。万华镜门图标与未匹配项目暂缺，不伪造替代。
- 包内代码、图片清单和私密文件排除检查通过；隔离目录 EXE 自检退出 0，native/frozen/ok=true，2.0，17 页、137 条合成日志。
- 已覆盖 dist/v2.0/AquaSync.exe，复制前后 SHA256 一致：927fbfa8dd1aa02ac4257b1253c231ad41d39e301c0ba40712969f8a6a9620bd。
- 修改文件：app/archive_ui.py、app/archive_widgets.py、app/collection_metadata.py、tools/build_archive_images.py、tests/test_archive_ui.py、data/report_assets/archive/*、docs/ARCHIVE-2.0.md、docs/TEST_RESULTS.md。用户数据、README、GitHub 与 Releases 未更改。

## Studio 独立视觉版本（2026-10-18）
- 新增 app/studio_theme.py、desktop_studio.py、AquaSync-Studio.spec、data/report_assets/studio/*.svg、docs/STUDIO-2.0.md；没有替换标准入口及原版 EXE。
- 17 页在 1000×760、1320×900、2560×1440 离屏切换通过，检查主要页面截图；验证单曲双击跳转及档案图片加载。实际显示体验仍以用户运行结果为准。
- 既有档案 UI/数据/难度表 15 项回归通过，50.85 秒。Studio EXE 使用隔离合成数据独立启动自检通过。
- 包含独立 Studio 样式与 SVG 控件资源，未包含数据库或私密导出。
- 标准 EXE SHA256 仍为 927fbfa8dd1aa02ac4257b1253c231ad41d39e301c0ba40712969f8a6a9620bd。
- 独立交付目录 dist/v2.0-studio，校验文件 SHA256SUMS.txt。README、GitHub 和 Releases 未更改。

## 中文 DX／标准图标（2026-10-18）
- 采用用户提供的 Topaz Wonder 透明 PNG，均为 232×84，文件像素与 alpha 不作修改。原始低清来源与 SHA256 见 data/report_assets/type_manifest.json。
- app/report_view.py 的 B50 和牌子完成表共用等比绘制，双 B50、屏幕缩放与 PNG 导出沿用同一代码路径；不再使用手绘替代标识。
- tests/test_report_models.py 与 tests/test_difficulty_tables.py：10 项通过，39.53 秒。新增像素对照验证 SD/DX、28/32/96 像素宽度、透明通道及等比绘制；既有 B50/牌子导出与交互回归通过。
- 检查实际 B50 卡片渲染，预览 .validation/chinese-types/b50-icons.png。离屏渲染不能代替用户实际显示体验。
- 修改 app/report_view.py、app/credits.py、tests/test_report_models.py、data/report_assets/rating-type_DX.png、rating-type_SD.png、type_manifest.json、SOURCES.md、docs/ALGORITHMS_AND_SOURCES.md、docs/TEST_RESULTS.md。
- 新包另存 dist/v2.0-cn-icons；原 dist/v2.0 和 dist/v2.0-studio 保留。未更改用户数据、README 或 GitHub/Release。
- 新普通版与 Studio 包内图标逐字节等于用户提供文件；两份包的私密文件排除检查通过；原普通版和 Studio EXE SHA256 均未改变。
- EXE 独立启动自检未通过：启动没有返回结果；同时 Python 启动发生“执行页内操作时的错误”。Windows System 日志 2026-10-18 11:55:34 记录多条 disk / Event ID 153、磁盘 2 的 I/O 重试。停止进一步反复启动，运行验证不能标为通过。未执行磁盘修复或删除用户文件。

## Studio 覆盖正式 2.0（2026-10-18）
- 按用户授权，将带中文超分 DX／标准图标的 dist/v2.0-cn-icons/AquaSync-Studio.exe 覆盖至 dist/v2.0/AquaSync.exe。版本仍为 2.0；启动脚本原本指向该路径，无须修改。
- 先复制临时文件并核对 SHA256，再替换正式 EXE；源文件、临时文件和最终文件三者校验一致：83a4b6a97f31c7194f99f5d490ff512e42e9fbf9b96ffbc1404ce3926d54d45f。
- 未关闭用户正在运行的独立旧 Studio 程序，未更改用户数据、README、GitHub 或 Releases。此前的启动自检限制仍保留，复制校验不能替代实际启动验证。

## 2.0 成绩统计布局（2026-10-18）
- 新增 app/stats_dashboard.py，替换 app/desktop_ui.py 原有两列表格；顶部四张指标卡，下方评级、FC/AP、难度表现及谱面类型四个面板。累计次数、FS 标记保留。
- 统计来自 privateCatalog.rows 的最佳成绩快照；达成率按有效值计算平均数，未知及特殊难度保留；不将已玩谱面占比描述为全曲库完成率。累计次数继续使用既有 statistics.chartPlayCount。
- 新增 tests/test_stats_dashboard.py：评级阈值含边界、无效值、特殊谱面、标记合计、空数据与响应式布局。统计与档案 UI 共 9 项通过（78.42 秒）；列宽调整后统计测试 2 项再通过（25.94 秒）。
- 使用合成 419 张谱面数据，检查 2560×1440、1320×900、1000×760 的 Studio 离屏预览；不代表真实用户成绩或现场显示确认。
- 修改文件：app/stats_dashboard.py、app/desktop_ui.py、tests/test_stats_dashboard.py、docs/STUDIO-2.0.md、docs/TEST_RESULTS.md。版本仍为 2.0，用户数据、README、GitHub/Release 未更改。
- 最终包检查统计模块、版本 2.0、中文图标字节一致、私密文件排除通过；隔离 EXE 启动自检退出 0，ok/native/frozen=true，17 页。已覆盖正式 dist/v2.0/AquaSync.exe，源/临时/最终 SHA256 一致：2e88ddbeac71c101d6f048e2e0a8aed3e4aeda273040eef86df20921e6a78e29。此前磁盘故障导致的启动限制不适用于这次已完成的启动自检。

## 2.0 段位定数、导航及地图详情（2026-10-18）
- 段位表在难度后增加统一参考定数，按 ID 和难度查找，缺失值待核实。导航说明项移到最后，内部页面 ID 保持稳定；show_page 与 CLI 预览按稳定 ID 定位。
- 角色表除角色名外各列居中。地图详情在冒险页内以标签页打开、去重、多开和关闭，不阻塞软件；切换用户/刷新后清空旧详情。
- 地图参考数据 226 张，其中 205 张拥有最终名牌板奖励，对应原始 Sprite 全部匹配；21 张无该奖励，显示无图。奖励类型、节点距离、条件原值和当前状态分开显示，不推断实际领取。
- 首轮地图/档案UI/难度表/档案数据 17 项通过（79.00 秒）；补充静态地图映射校验与目录迁移等 8 项通过（35.22 秒）。检查 2560×1440、1320×900、1000×760 离屏界面，名牌板完整显示、奖励表优先展示距离和名称；离屏结果不等于用户实际操作确认。
- 修改 app/desktop_ui.py、app/desktop_core.py、app/archive_ui.py、app/credits.py、app/map_metadata.py、app/map_details_ui.py、desktop.py、tools/build_map_details.py、tools/build_archive_images.py、tests/test_archive_ui.py、tests/test_map_details.py、AquaSync.spec、AquaSync-Studio.spec、data/map_details.json、data/report_assets/archive、素材来源与 Studio/测试文档。未改用户数据库、README、GitHub 或 Releases。
- 最终包已检查地图模块、2.0 版本、地图元数据及 205 张名牌板图片逐字节一致，私密文件排除通过。EXE 隔离自检退出 0，ok/native/frozen=true、17 页。已关闭旧程序并覆盖正式 dist/v2.0/AquaSync.exe，源/临时/最终 SHA256 一致：b79559572e87a65fa12cd93887677ec0a004bd6d5c2b581801319b1b61d7738f。

## 2.0 地图奖励图片与推荐布局（2026-10-18）
- 地图奖励 / 解禁要素列显示角色、名牌板、背景框、头像图片，任务与解禁曲目显示曲绘。挑战曲目通过 Challenge.xml Music/id 显式关联。
- 扫描 226 张参考地图，相关 2625 个节点均匹配图片；688 组名牌板/背景框/头像引用均有原图。称号和数值礼物等无独立图片的类型保持文字，不作伪造补图。
- 图片绘制支持 ArchiveTable 指定名称列，不挤占距离列；排序后图片、名称与距离绑定同一条记录。曲绘优先用户本地缓存，其次内置曲绘。
- 推分推荐新增独立难度列，除曲目外各列居中；曲目列加宽且可调整，保留私服/国服颜色、难度底色和各列排序。
- 地图详情、推荐口径、难度绘制与设置相关 16 项测试通过（68.95 秒）；列宽调整后推荐相关 5 项通过（18.64 秒）。已检查地图奖励图标与推分推荐离屏预览；不替代用户实际操作确认。
- 修改 app/map_details_ui.py、app/map_metadata.py、app/archive_widgets.py、app/desktop_ui.py、app/credits.py、tools/build_map_details.py、tools/build_archive_images.py、tests/test_map_details.py、tests/test_recommendation_scopes.py、tests/test_desktop_settings.py、tests/test_difficulty_tables.py、data/map_details.json、data/report_assets/archive、素材来源与 Studio/测试文档。README、用户数据与 GitHub/Release 未更改。
- 最终包的 688 组奖励图原始字节、地图数据、2.0 版本及私密文件排除检查通过。EXE 隔离启动自检退出 0，ok/native/frozen=true。已关闭旧程序并覆盖正式 dist/v2.0/AquaSync.exe；源/临时/最终 SHA256 一致：f4752915c78bf40b80cc0f1dfa816beb3cf6a6a69329803888ba8412abab6aa9。

## 2.0 课程挑战与登录奖励修复（2026-10-18）
- 新增 app/activity_metadata.py、app/activity_details_ui.py、data/activity_details.json 与 tools/build_activity_details.py。按 Course.xml、LoginBonus.xml、Ticket.xml 明确 ID 关联；当前状态来自导出，配置为参考，未推断领奖。
- 324 个课程中 239 个固定课程共 956 个曲目位置都有曲绘；85 个随机课程不显示占位曲目作为实际选曲。固定课程列表显示曲绘组合，详情显示各谱面曲绘/难度/参考定数/最佳成绩，课程配置与统计分开。
- 72 种登录奖励全部匹配图片，包括搭档、曲目、背景框、名牌板、头像、1.5 倍票券。票券依据 Ticket.xml filename=UI_CMN_Tix_Icon_Free 精确匹配本地游戏 Sprite。
- 两页双击均打开软件内部标签，支持多开/去重/关闭；刷新或切换用户清空旧详情。登录列表新增奖励类型与所需点数。
- 首轮档案 UI 7 项通过（50.03 秒）；完整活动/档案/地图/目录设置相关 19 项通过（84.18 秒），最终布局活动测试 3 项通过（6.46 秒）。检查三种尺寸离屏预览；不等于用户实际操作确认。
- 修改 app/activity_metadata.py、app/activity_details_ui.py、app/archive_ui.py、app/archive_widgets.py、app/desktop_core.py、app/credits.py、desktop.py（增加隔离自检详情开关）、tools/build_activity_details.py、tools/build_archive_images.py、tests/test_activity_details.py、AquaSync.spec、AquaSync-Studio.spec、data/activity_details.json、data/report_assets/archive、来源/Studio/测试文档。版本仍为2.0，未改用户数据、README、GitHub/Release。
- 最终包中活动模块、2.0 版本、活动元数据与奖励图片原始字节一致；私密文件排除检查通过。分别执行课程和奖励详情的 EXE 隔离自检，均退出 0、详情标签数 1，已检查实际打包后离屏截图。正式 dist/v2.0/AquaSync.exe 已覆盖；源/临时/最终 SHA256 一致：efd088aa64491f7bdaed4d9c7a2b79389615143e9d5fa65a36de0528a86a50c9。

## 2026-10-18 — AquaSync 2.0 icon and startup diagnostics
- Added original minimal cyan eight-key ring icon (PNG + seven-size ICO); window icon and both PyInstaller specifications use it. Prompt and provenance: APP_ICON.md.
- Studio and standard launchers share early exception reporting, bounded local startup logs, native fatal-error diagnostics and exit status. Offscreen mode is selected before Studio imports Qt.
- Bootstrap tests: 2 passed. Source native self-test: passed, 17 pages.
- Final packaged EXE: frozen self-test passed in an isolated C-drive temporary profile (10.49 seconds); version 2.0, 17 pages. PE icon resources present; embedded ICO matches source; no bundled sqlite3/jsonl private stores.
- Normal entry (without --self-test) reached the main-window milestone and both packaged processes remained responsive. This was a hidden-window smoke test, not manual visible-window acceptance. MainWindowHandle is unavailable for this hidden launch, so readiness evidence uses the application milestone and process state.
- Windows Application Error reports show prior 0xc0000006 / storage access failures. Fresh disk event 153 I/O retries repeatedly occurred during this run, including 14:05. Original EXE eventually passed its isolated self-test after 145.36 seconds. Software diagnostics cannot repair the F-drive/storage-link failure; no disk repair or user-data reset was attempted.
- README, GitHub and Releases were not changed.

- Delivery limitation: repeated F-drive hash reads stalled; replacement was cancelled before the atomic move. Canonical dist/v2.0/AquaSync.exe remains the previous 809765147-byte binary. The tested new EXE is in the system TEMP/AquaSync-icon-startup-validation/AquaSync.exe. An unverified AquaSync.verified staging file could not be removed because a pending disk read retained its handle; it must not be launched or treated as a verified release. No GitHub/Release update occurred.

## 2026-10-18 — F-drive storage and fixed-course startup repair
- Reproduced user startup failure from local traceback: course thumbnails accessed owner.archives before MainWindow assigned it. Initial refresh now passes its already-created chart list explicitly. Added a fixed-course first-construction regression test.
- 11 related tests passed; source and final installed frozen self-tests also passed with an existing non-empty personal profile, all 17 pages.
- Added AquaSync-Portable.spec (onedir). Final EXE and _internal run directly from dist/v2.0 without one-file extraction on C. Logs and settings are beside the EXE; data is in its user-data folder.
- C-drive legacy profile was copied into F-drive data and additionally into .private-local/legacy-c-profile-20261018. SQLite dumps were compared and migration files verified. Personal backup and configurations are ignored by Git and excluded from build inputs.
- Final EXE SHA256: 23aa026a6019b776eaa28de8e6f617e98ae0abb65b68806ad0b2b56eb7357d3a. Keep _internal with the EXE. Version remains 2.0.
- Auto-review rejected deletion of the original C-drive personal profile and temporary directory because explicit deletion authorization was missing. Those C-drive originals remain pending confirmation; the installed F-drive program no longer uses them. README, GitHub and Releases unchanged.

- User explicitly authorized C-drive cleanup. Fresh F-drive backup verified using SQLite dump comparison; removed only the two explicitly authorized legacy C-drive directories. Current F-drive data and prior backups preserved.

## 2026-10-18 — GitHub upload folder
- Created dist/GitHub-2.0 with AquaSync-2.0-Windows-x64-Portable.zip and SHA256SUMS.txt only. No GitHub upload, README edit or Release change performed.
- tools/package_release.py uses an allowlist of AquaSync.exe + _internal, rejects unexpected private runtime files and local machine paths in bundled text, and adds a short Chinese usage guide inside the archive.
- 3 packaging/privacy regression tests passed. ZIP integrity check passed (4495 files). Extracted the finished ZIP on F and ran its frozen native self-test: version 2.0, 17 pages, zero imported players, default data directory beside the extracted EXE on F.
- ZIP bytes: 811557128. SHA256: eb42bf76a74340582d31ca575224491a2afdc7abe9dead6688246930bdf470b1.
- Release excludes installed user-data, logs, AquaSync-desktop.json, private backups and personal databases. Keep the complete extracted folder, including _internal.

## 2026-10-18 — Personal profile and collections layout
- Added compact profile identity/metric cards, current equipment image/name cards and responsive layout. Missing or absent fields stay unknown; raw setting encodings are not guessed.
- Default details hide the raw field-name column with an explicit toggle. Existing data filtering, sorting and CSV columns remain available. Short detail tables no longer show redundant page-size controls.
- Collection rows now resolve bundled thumbnails, center non-name columns, show a selection preview and disable irrelevant filters by mode. Narrow windows prioritize the collection table. Rankings use side-by-side panels.
- 13 archive/profile/activity tests passed, including missing-data semantics, plain-text names, raw-field toggle, filtering, selection identity and preservation of imported player data.
- Synthetic native previews checked at 1000x800, 1320x900 and 2560x1440. Frozen staged and installed EXEs passed startup checks (17 pages). Final clean ZIP extracted on F also passed startup with zero imported players.
- Version remains 2.0. Installed EXE SHA256: 3e160131f8924faa49ab7f1f7d4064ff81aabc57aa78318e399b847af42a8da6. Updated dist/GitHub-2.0 ZIP SHA256: 4afd42de1585e1605c87d3d7b87dd49b2f527a24cacb67627358416fbdafc1ca (811571414 bytes).
- Personal data/configuration/backups preserved and excluded from the public upload ZIP. README, remote GitHub repository and Releases unchanged.

## 2026-10-18 — Collection artwork completeness
- Added explicit icon/plate/frame manifest entries from original AssetBundle Sprite IDs: 1643 icons, 539 nameplates, 575 frames. Plate.xml is mapped to ui_plate assets. Existing full-size map reward extractions are preserved.
- All 27 Ticket.xml references match their exact shared sprites. All 4302 Title.xml entries have a preview rendered from original Shougou rarity backgrounds plus original XML text; manifest marks these as renderedText, not standalone game textures. Added 12 missing jacket images (10 Sprite, 2 exact-name Texture2D); all 1706 local jacket references now resolve. Map Title reward previews resolve for all 110 reference nodes.
- Legacy nameplateId=0 no longer creates an empty equipment card; raw value stays visible. Unknown inventory types remain explicit and do not receive guessed images. A local-only personal-profile audit confirmed coverage of all supported inventory/equipment records; an unrecognized item type remains unsupported. Audit details are in .private-local and excluded from release inputs.
- 12 targeted collection/profile/map/activity tests passed. Checked synthetic profile previews and frozen native startup. Final installed EXE with existing personal data and final extracted public ZIP with zero imported players both passed self-tests (17 pages, version 2.0). ZIP manifest image paths, integrity and privacy checks passed.
- Installed runtime: 11580 files, 7089 updated; EXE SHA256 a7c6e3f4c01b81c08375f94f19d671bb02fdde308553f50039f954a8c87c299e.
- Updated dist/GitHub-2.0 archive: 11582 entries, 1104075850 bytes, SHA256 0932295d2295049a98bc74deb123552a20637d0abd512b0cbb2c136b38d5fd27. Personal data/config/backups preserved and not bundled. README, GitHub and Releases unchanged. All application output stays on F.

## 2026-10-18 — Guessing game and advanced tools layout
- Added app/tool_pages.py native card layouts. Guessing separates the puzzle, controls, opened characters and hint/feedback; Enter submits; completed rounds preserve their answer until a new round. User-controlled titles remain plain text.
- Advanced utilities use four tabs with labeled inputs and independent keyword fields for completion and Best queries. Results show cover art, difficulty colors, centered metadata and explicit empty states. Existing score-line formulas and selection rules are preserved.
- Course table keeps the song column left aligned and centers every other column on each render, including course switches.
- 9 targeted tests passed (test_tool_pages.py, test_desktop.py, test_difficulty_tables.py). Source previews checked at 1000x800 and 1320x900; all three frozen pages passed startup/render self-tests. Installed EXE passed with existing F-drive data. Final ZIP extracted on F passed startup with zero imported players, 17 pages, version 2.0.
- Installed EXE SHA256: c9f0cccb34d312a1d688d051d0c8dc8884b7b8c675eaece93976acd1e3fc87f7. Clean upload ZIP: 11582 entries, 1104081397 bytes, SHA256 30b767684833c317d414fbdc1fc8cf9cafb014fbe4fcbc49ffb489a55175aadd.
- Personal data/configuration/backups preserved. No README edits, remote GitHub writes or Release changes. All application and validation output remains on F.

## 2026-10-18 — Setup and portable distribution
- Added tools/installer/AquaSync.iss and pinned ChineseSimplified.isl from the official Inno Setup is-6_7_3 source tag. Official compiler download passed Windows Authenticode validation (Pyrsys B.V.) and was unpacked in portable mode on F. Compiler and installer temp/log paths were explicitly set on F.
- Built a Chinese non-admin x64 Windows 10+ installer with an editable destination, preference for a fixed non-system drive, current-user desktop shortcut, installed icon and uninstaller. Only privacy-checked AquaSync.exe and _internal files are included. No wildcard uninstall deletion of the installation directory.
- Real unattended install into an isolated F directory succeeded. All 11581 payload files matched the clean runtime SHA256 hashes. Shortcut target and working directory were checked using a redirected test shortcut folder. Installed frozen application self-test passed: 2.0, 17 pages, zero players, data beside the EXE on F.
- Reinstalled the identical package over the test installation, then uninstalled it. Every test profile/configuration file retained its hash after both operations; program and test shortcut were removed on uninstall. Test application registration was removed by the uninstaller. Installer wizard was not manually clicked through.
- Renamed the already integrity/privacy/startup-verified portable archive to AquaSync-2.0-Portable.zip; content/hash unchanged. Updated package_release.py and its filename test: 3 packaging tests passed.
- dist/GitHub-2.0 contains AquaSync-2.0-Setup.exe (1092031709 bytes; SHA256 5aaef5be7cbc7092b6fba7f502269a2aef41674b7153de119ae33cfab14b03d4), AquaSync-2.0-Portable.zip (1104081397 bytes; SHA256 30b767684833c317d414fbdc1fc8cf9cafb014fbe4fcbc49ffb489a55175aadd), and SHA256SUMS.txt for both files.
- Added docs/PACKAGING-2.0.md. Existing personal data, installed canonical program, README and GitHub/Releases unchanged.

## 2026-10-18 — Lossless size reduction and startup optimization
- Added tools/compact_assets.py and app/image_assets.py. Original source PNGs remain untouched. 10785 unique offline images were converted to exact lossless WebP with dimensions, alpha and every RGBA byte verified; 488 byte-identical duplicates use local aliases. Artwork decreased from 1026662370 to 689124259 bytes. No images are downloaded on demand, resized or lossily encoded.
- Qt decode microbenchmark of 12 sampled jackets: WebP medians were faster than PNG in each sample (roughly 1.3–3.1 ms versus 1.5–3.3 ms). PIL decode timings were not used to infer Qt performance. Original/new frozen B50 screenshots were byte-identical at 1320x900.
- Catalog snapshots are reused only inside a synchronous UI initialization/refresh session, then discarded; nested sessions and exception cleanup are tested. Immutable chart scalar fields avoid generic deepcopy dispatch, while nested containers remain isolated. Archive manifest entries resolve files on demand rather than stat/resolve every asset at startup. Fresh catalog/region/eligibility semantics are unchanged.
- Full regression suite: 167 passed, one existing Starlette/httpx deprecation warning. After adding build-cache invalidation coverage, all 3 optimization tests passed. Earlier targeted run surfaced a pre-existing cover manifest file count that omitted 12 recently added jackets; count now matches all 1714 source files.
- Source window initialization with cProfile dropped from 15.93 to 7.36 seconds before the final scalar-copy optimization. Final unprofiled source runs took 2.24/2.32/2.18 seconds. These differently instrumented numbers are not directly comparable.
- Alternating frozen full startup self-tests used the same synthetic archive. Old runs: 31.49/7.57/7.63 s; new: 4.68/3.74/3.75 s. First-run disk-cache effects and concurrent packaging affect timing; repeated medians are approximately 7.63 versus 3.75 seconds. These include self-test work and are not a guaranteed first-window cold-start latency.
- Frozen history, progress and profile pages passed, as did the extracted clean ZIP (zero imported players) and actual installed program. Existing player payload hashes remained unchanged. Runtime now occupies 865434675 bytes versus 1216484976 bytes previously, excluding EXE and personal data.
- Chinese installer fresh install, shortcut, startup and uninstall/data preservation passed. Upgrading from the earlier full-size installer also passed: only old bundled archive/cover PNGs and obsolete PIL runtime are retired; user-data is preserved. Updated installer was tested unattended, not by manually clicking the wizard.
- AquaSync-2.0-Setup.exe: 750530341 bytes; SHA256 dfa0303208de1ce671b5154b1cf11e4461b592049bfe80b283c796a8f0d7b117.
- AquaSync-2.0-Portable.zip: 761027998 bytes; SHA256 79a34d8bbb72c1beca0201fb95a3611b896e22d6be3beb75eeeab3693098853b.
- Canonical EXE SHA256: 717d4174809f32cb9daf2e0cc840ad56e355eeef4058c682b841bca2ac858999. Version remains 2.0. README, GitHub and Releases unchanged. Cleanup details are retained locally in .validation/slim-audit/cleanup.json.
- Cleanup completed: 39035474972.0 bytes removed across 270 generated targets. Historical Git checkouts, original source artwork, private backups, user data and user-provided artifacts were preserved; compiler retained in .tools/InnoSetup. Installed self-test and public package SHA256 checks passed after cleanup.
