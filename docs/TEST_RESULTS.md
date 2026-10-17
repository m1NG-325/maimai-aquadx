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
