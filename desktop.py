"""AquaSync native desktop entry point and reproducible packaged smoke test."""
import argparse
import json
import os
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data-dir', type=Path)
    parser.add_argument('--self-test', action='store_true')
    parser.add_argument('--audit-runtime', action='store_true', help='Self-test only: exercise packaged dependencies')
    parser.add_argument('--sample', type=Path)
    parser.add_argument('--screenshot', type=Path)
    parser.add_argument('--result', type=Path)
    parser.add_argument('--reports-dir', type=Path)
    parser.add_argument('--window-size', help='Self-test rendering size, such as 2560x1440')
    parser.add_argument('--preview-page', type=int, default=0)
    parser.add_argument('--preview-details', type=int, nargs='*', default=[], help='Self-test: open native song detail tabs')
    parser.add_argument('--preview-activity',choices=['course','bonus'],help='Self-test: open an embedded course or bonus detail tab')
    parser.add_argument('--preview-floating', action='store_true', help='Self-test: detach the last song detail')
    args = parser.parse_args()
    if args.self_test:
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    from PySide6.QtWidgets import QApplication
    from app.desktop_core import DesktopCore
    from app.desktop_ui import MainWindow
    app = QApplication(sys.argv[:1])
    app.setApplicationName('AquaSync')
    from app import __version__
    app.setApplicationVersion(__version__)
    from PySide6.QtGui import QIcon
    from app.desktop_core import ASSETS
    app.setWindowIcon(QIcon(str(ASSETS / 'data/report_assets/aquasync.ico')))
    if args.self_test:
        # Qt's offscreen test plugin does not discover Windows system fonts.
        from PySide6.QtGui import QFontDatabase
        for font in ['msyh.ttc', 'msyhbd.ttc', 'msgothic.ttc']:
            file = Path(os.getenv('WINDIR', 'C:/Windows'))/'Fonts'/font
            if file.exists():
                QFontDatabase.addApplicationFont(str(file))
    from app.desktop_bootstrap import milestone
    milestone('Loading data')
    core = DesktopCore(args.data_dir)
    if args.self_test and args.sample:
        core.import_file(args.sample, 'test')
    window = MainWindow(core)
    if args.self_test and args.window_size:
        width,height=map(int,args.window_size.lower().split('x'))
        window.resize(width,height)
    window.show()
    milestone('Main window shown')
    if args.self_test:
        window.show_page(args.preview_page)
        app.processEvents()
        if args.preview_activity:
            section='userCourseList' if args.preview_activity=='course' else 'userLoginBonusList'
            window.show_page(15);window.archives.progress_tabs.setCurrentIndex(3 if args.preview_activity=='course' else 5)
            if window.archives.progress_views[section].rows:window.archives.open_activity_detail(section,0)
        for mid in args.preview_details:window.song_detail(mid)
        app.processEvents()
        if args.preview_floating and window.detail_panels:window.detail_panels[-1].setFloating(True)
        app.processEvents()
        assert all(panel.isWindow()==panel.isFloating() for panel in window.detail_panels)
        window.calc_ds.setValue(14); window.calc_a.setValue(100.5); window.calculate()
        assert window.calc_label.text().startswith('315')
        window.render_library(True)
        assert window.library_table.rowCount() == 1
        window.new_game()
        assert hasattr(window, 'answer')
        report = {'ok': True, 'native': True, 'version':__version__, 'pages': window.pages.count(),
                  'activityDetails':sum(t.count() for t in window.archives.activity_detail_tabs.values()),
                  'archiveRows':len(window.archives.logs), 'archiveSections':len(window.archives.archive.get('present',[])),
                  'collectionNames':sum(len(v) for v in window.archives.names.values()),
                  'players': len(core.db.users()), 'charts': len(core.db.charts()),
                  'scoreRows': len(getattr(window,'score_rows',[])), 'scoreGridRows':window.scores.rowCount(), 'rating315': True,
                  'dataDirectory': str(core.directory), 'frozen': bool(getattr(sys, 'frozen', False)),
                  'detailPanels':len(window.detail_panels),
                  'floatingDetails':sum(panel.isFloating() for panel in window.detail_panels)}
        if window.data:
            source=window.data['b50Views']['source']
            report.update(knownTitles=window.data['privateCatalog']['known'],sourceB50MissingRating=source['uncalculated'],
                          calculatedRating=source['calculatedRating'],reportedRating=source['rating'])
        if args.screenshot:
            args.screenshot.parent.mkdir(parents=True, exist_ok=True)
            assert window.grab().save(str(args.screenshot), 'PNG')
        if args.audit_runtime:
            from app.runtime_audit import check
            report['runtimeAudit']=check(core,window,(args.result.parent if args.result else core.directory)/'runtime-audit')
        if args.result:
            args.result.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf8')
        if args.reports_dir and window.data:
            args.reports_dir.mkdir(parents=True,exist_ok=True)
            assert window.b50_canvas.export_image(args.reports_dir/'b50.png')
            assert window.plate_canvas.export_image(args.reports_dir/'plate.png')
        window.close()
        return 0
    return app.exec()


if __name__ == '__main__':
    from app.desktop_bootstrap import run
    raise SystemExit(run())
