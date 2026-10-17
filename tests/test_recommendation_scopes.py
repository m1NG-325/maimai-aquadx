import copy
import json
import os
from app.parser import parse_aquadx
from app.recommendation_scopes import private_recommendations,cn_recommendations


def chart(mid,ds,version):
    return dict(music_id=mid,level_index=3,title=f'Song {mid}',type='SD',level='14',ds=ds,version=version,is_new=False)


def example():
    p=parse_aquadx({'userMusicDetailList':[dict(musicId=i,level=3,achievement=980000) for i in (1,2,3,4)]})
    p['ratingComposition']={'new':[dict(musicId=2,level=3)]}
    charts=[chart(1,14,'maimai GreeN'),chart(2,15,'maimai でらっくす PRiSM PLUS'),chart(3,15,'maimai でらっくす MAGiCAL')]
    cn={(i,'standard',3):dict(title=f'CN {i}',level='12',ds=12,version=24000 if i==1 else 25500,disabled=False) for i in (1,4)}
    return p,charts,cn


def test_two_pools_use_their_own_constants_and_versions_without_mutation():
    p,charts,cn=example();before=copy.deepcopy((p,charts,cn))
    private=private_recommendations(p,[],charts,[])
    public=cn_recommendations(p,cn,[dict(version=25500,title='舞萌DX2026')])
    assert private['currentVersion']=='maimai でらっくす PRiSM PLUS'
    assert {r['musicId'] for r in private['rows']}=={1,2}
    assert {r['musicId'] for r in public['rows']}=={1,4}
    assert private['unsupported']==2 and public['unsupported']==2
    assert next(r for r in private['rows'] if r['musicId']==1)['ds']==14
    assert next(r for r in public['rows'] if r['musicId']==1)['ds']==12
    assert private['rating']!=public['rating']
    assert all(r['is_new']==(r['musicId']==4) for r in public['rows'])
    assert '本地导入' in public['scoreSource'] and (p,charts,cn)==before
    manual=private_recommendations(p,[],charts,[],'maimai でらっくす MAGiCAL')
    assert {r['musicId'] for r in manual['rows']}=={1,2,3}
    assert all(r['is_new']==(r['musicId']==3) for r in manual['rows'])


def test_disabled_unknown_and_missing_constants_are_not_recommended():
    p,charts,cn=example();cn[(1,'standard',3)]['disabled']=True;cn[(4,'standard',3)]['ds']=None
    result=cn_recommendations(p,cn,[dict(version=25500,title='国服')])
    assert result['rows']==[] and result['missingConstants']==1 and result['unsupported']==3
    charts[0]['ds']=None;p['ratingComposition']={}
    result=private_recommendations(p,[],charts,[])
    assert '请核对' in result['basis'] and result['missingConstants']==1


def test_native_scope_switch_retains_sorting_and_version_choice(tmp_path):
    os.environ['QT_QPA_PLATFORM']='offscreen'
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt
    from app.desktop_core import DesktopCore
    from app.desktop_ui import MainWindow,PRIVATE_COLOR,LXNS_COLOR
    app=QApplication.instance() or QApplication([])
    core=DesktopCore(tmp_path/'profile',settings_path=tmp_path/'settings.json')
    source=tmp_path/'synthetic.json'
    source.write_text(json.dumps({'userMusicDetailList':[dict(musicId=772,level=2,achievement=980000)]}),encoding='utf-8')
    core.import_file(source,'example');before=core.db.player('example')
    w=MainWindow(core);w.nav.setCurrentRow(5);w.show();app.processEvents()
    try:
        assert w.recommend_scope.currentText()=='私服'
        assert not w.recommend_version.isHidden() and PRIVATE_COLOR in w.recommend_info.styleSheet()
        assert '私服' in w.recommend_info.text() and w.recommend.isSortingEnabled()
        w.recommend_scope.setCurrentIndex(1);app.processEvents()
        assert w.recommend_version.isHidden() and '国服' in w.recommend_info.text()
        assert LXNS_COLOR in w.recommend_info.styleSheet() and '非官服账号成绩' in w.recommend_info.text()
        assert w.recommend.isSortingEnabled()
        w.recommend_scope.setCurrentIndex(0);w.recommend_version.setCurrentText('maimai でらっくす PRiSM PLUS');app.processEvents()
        assert 'PRiSM PLUS' in w.recommend_info.text()
        assert core.db.player('example')==before
    finally:w.close();app.processEvents()
