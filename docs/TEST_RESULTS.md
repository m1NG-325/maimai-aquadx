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


## 1.2

- 本地功能全量回归129项通过，1条既有Starlette/httpx依赖弃用警告；定版时针对性回归16项通过。
- 完成统一曲库、分地区推荐、Rating对照表、成绩排序与布局、高清评级和状态图、段位曲绘的验证。
- 单文件EXE独立启动自检通过，验证内嵌版本为1.2；高清素材的来源哈希、许可及功能模块完整。
- 公开源码排除原始成绩夹具、数据库、备份、截图、日志、本机绝对路径和个人成绩统计。公开测试只采用代码生成的合成记录；涉及私有样本的测试留在本地。
- README与GitHub Releases保持原样，1.2完整更新内容见CHANGELOG-1.2.md。
