import json,os
from pathlib import Path
os.environ['QT_QPA_PLATFORM']='offscreen'
from PySide6.QtWidgets import QApplication
from app.collection_metadata import entity_image
from app.profile_dashboard import profile_image


def test_collection_manifest_files_and_accurate_title_provenance():
    assets=Path(__file__).resolve().parents[1]/'data/report_assets/archive'
    manifest=json.loads((assets/'manifest.json').read_text(encoding='utf8'))
    assert manifest['missingCollectionImages']==[]
    for kind,count in manifest['collectionImageCounts'].items():
        rows=[(key,row) for key,row in manifest['entries'].items() if key.startswith(kind+':')]
        assert len(rows)>=count>0
        for key,row in rows:
            assert entity_image(assets,kind,key.split(':')[1]),key
            if kind=='title':assert row['renderedText'] and row['rarity'] and 'Qt text preview' in row['source']
    for kind,identifier in [('icon',1),('plate',1),('frame',1),('title',1),('ticket',2)]:
        assert profile_image(assets,kind,identifier)
    assert profile_image(assets,'nameplate',0) is None
    assert (assets.parent/'covers/9919.png').is_file()
    from app.map_details_ui import reward_image
    assert reward_image(assets,{'kind':'Title','elementId':'1'})


def test_collection_ui_images_and_unused_legacy_equipment(tmp_path):
    from tests.test_archive_ui import core_with_archive
    from app.desktop_ui import MainWindow
    app=QApplication.instance() or QApplication([]);core=core_with_archive(tmp_path)
    payload=core.db.player('example');sections=payload['archive']['sections']
    sections['userData'].update(iconId=1,plateId=1,titleId=1,frameId=1,nameplateId=0)
    sections['userItemList']=[dict(itemKind=kind,itemId=identifier,stock=1,isValid=True) for kind,identifier in [(1,1),(2,1),(3,1),(11,1),(12,2),(6,19919)]]
    core.db.save_player('example',payload);before=core.db.player('example');w=MainWindow(core)
    try:
        a=w.archives
        assert all(row.get('_imagePath') for row in a.collection_table.rows)
        for key,kind,image,label,card in a.profile_equipment.cards:
            if key=='nameplateId':assert card.isHidden()
            elif key in ('iconId','plateId','titleId','frameId'):assert image.pixmap() and not image.pixmap().isNull()
        assert any(row.get('_imageNote') for row in a.collection_table.rows if row['kind']=='称号')
        assert core.db.player('example')==before
    finally:w.close();app.processEvents()
