import os,json,hashlib
from pathlib import Path
os.environ['QT_QPA_PLATFORM']='offscreen'
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication
from app.desktop_ui import MainWindow,difficulty_background,crisp_pixmap
from tests.synthetic_sample import sample


def test_hd_status_assets_match_manifest_and_dpr():
    app=QApplication.instance() or QApplication([])
    root=Path(__file__).resolve().parents[1]/'data/report_assets'
    manifest=json.loads((root/'status_manifest.json').read_text())
    assert {a['file'] for a in manifest['assets']} >= {f'rating-icon_{s}.png' for s in ['fc','fcp','ap','app','fs','fsp','fsd','fsdp']}
    for asset in manifest['assets']:
        path=root/asset['file'];image=QImage(str(path))
        assert image.width()==image.height()==80 and image.hasAlphaChannel()
        assert hashlib.sha256(path.read_bytes()).hexdigest()==asset['sha256']
        pix=crisp_pixmap(path,30,30,2)
        assert pix.width()==60 and pix.devicePixelRatioF()==2


def test_difficulty_backgrounds_and_course_cover_identity(tmp_path):
    app=QApplication.instance() or QApplication([])
    core,_=sample(tmp_path);w=MainWindow(core)
    try:
        rows=[dict(music_id=772,title='Z',type='SD',difficulty='MASTER',level_index=3,ds=12.8,version='maimai',score=None),
              dict(music_id=11663,title='A',type='DX',difficulty='EXPERT',level_index=2,ds=13.8,version='maimai',score=None)]
        core.library=lambda *args,**kwargs:rows
        w.render_library();w.library_table.sortItems(0,Qt.SortOrder.AscendingOrder)
        for i in range(2):
            mid=w.library_table.item(i,0).data(Qt.ItemDataRole.UserRole)
            level=next(r['level_index'] for r in rows if r['music_id']==mid)
            for j in range(5):assert w.library_table.item(i,j).background().color()==difficulty_background(level)
        for k,c in enumerate(core.courses):
            w.course_choice.setCurrentIndex(k);w.render_course()
            for i,m in enumerate(c['musics']):
                assert w.course_table.item(i,0).data(Qt.ItemDataRole.UserRole)==m['id']
                assert w.course_table.item(i,0).background().color()==difficulty_background(m['difficulty'])
                assert (Path(__file__).resolve().parents[1]/'data/report_assets/covers'/f"{m['id']%10000}.png").exists()
        opened=[];w.song_detail=opened.append
        w.course_choice.setCurrentIndex(0);w.course_table.cellDoubleClicked.emit(0,1)
        assert opened==[core.courses[0]['musics'][0]['id']]
        for scope in ['private','cn']:
            w.data['recommendationScopes'][scope]['rows']=[dict(musicId=772,title='Z',difficulty='MASTER',level=3,ds=12.8,achievements=98,goal=99,targetRating=260,estimatedGain=10)]
        for k in range(2):
            w.recommend_scope.setCurrentIndex(k);w.render_recommend()
            for j in range(6):assert w.recommend.item(0,j).background().color()==difficulty_background(3)
    finally:w.close();app.processEvents()
