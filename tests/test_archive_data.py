import copy,json
from pathlib import Path
from app.parser import parse_aquadx
from app.archive_analysis import enrich_logs,filter_logs,log_statistics,rating_candidates,favorite_music_ids
from app.collection_metadata import read_xml_names,load_names,entity_name


def export():
 return {'userData':{'userName':'Example','accessCode':'SECRET_ACCESS','friendCode':'SECRET_FRIEND','highestRating':15000},
  'userMusicDetailList':[{'musicId':1,'level':2,'achievement':990000}],
  'userPlaylogList':[{'musicId':1,'level':2,'achievement':990000,'userPlayDate':'2026-01-01T18:00:00+00:00','beforeDeluxRating':100,'afterDeluxRating':105,'tapGreat':3,'fastCount':2,'lateCount':1,'vsUserName':'OTHER_PERSON','playedUserId1':999,'comboStatus':3},
    {'musicId':1,'level':2,'achievement':980000,'userPlayDate':'invalid','lateCount':50},None,{'musicId':'bad','level':2}],
  'userOption':{'noteSpeed':10,'unknownSecret':'DROP'},'userMapList':[{'mapId':1,'distance':250,'isClear':False}],
  'userCharacterList':[{'characterId':101,'level':12}], 'userFavoriteList':[{'userId':123,'itemKind':9,'itemIdList':[101]}],
  'userPrintDetailList':[{'serialId':'SERIAL','clientId':'CLIENT','printNumber':1}],
  'userFavoriteMusicList':[{'id':1}],
  'userGeneralDataList':[{'propertyKey':'recent_rating_next','propertyValue':'1:2:26000:995000,broken'},{'propertyKey':'favorite_music','propertyValue':'1,2'},{'propertyKey':'credential','propertyValue':'DROP'}]}


def test_archive_allowlist_missing_and_partial_data_do_not_change_best():
 raw=export();before=copy.deepcopy(raw);p=parse_aquadx(raw);a=p['archive'];text=json.dumps(a)
 assert raw==before and len(p['best'])==1 and len(a['sections']['userPlaylogList'])==2
 assert all(secret not in text for secret in ['SECRET_ACCESS','SECRET_FRIEND','OTHER_PERSON','SERIAL','CLIENT','credential','unknownSecret','userId'])
 assert len(a['warnings'])==1 and 'userOption' in a['present']
 assert 'fastCount' not in a['sections']['userPlaylogList'][1]
 assert not parse_aquadx({'userMusicDetailList':[]})['archive']['available']
 raw['userMapList']={};assert any('userMapList 格式异常' in w for w in parse_aquadx(raw)['archive']['warnings'])


def test_retained_history_calendar_judgement_coverage_and_no_guessed_time():
 a=parse_aquadx(export())['archive'];charts=[dict(music_id=1,level_index=2,title='Song',ds=12,version='maimai')]
 rows=enrich_logs(a,charts);s=log_statistics(rows)
 assert rows[0]['day']=='2026-01-02' and rows[0]['ratingDelta']==5 and rows[1]['day']==''
 assert s['days']=={'2026-01-02':1} and s['undated']==1
 assert s['judgements']['tapGreat']==3 and s['judgements']['tapMiss'] is None
 assert s['coverage']['tapGreat']==1 and s['late']==51 and s['fast']==2
 assert s['fastPercent']==100*2/3 and s['pairedTimingLogs']==1
 assert len(filter_logs(rows,start='2026-01-02',end='2026-01-02'))==1
 assert len(filter_logs(rows,query='1',difficulty=2))==2
 assert filter_logs(rows,new_only=True)==[] and len(rating_candidates(a,charts))==1
 assert favorite_music_ids(a)=={1,2}
 assert log_statistics([])['averageAchievement'] is None


def test_names_xml_patch_priority_no_personal_paths_and_unknown_ids(tmp_path):
 for part,name in [('StreamingAssets/A000','Base'),('A021','Patched')]:
  p=tmp_path/part/'Chara.xml';p.parent.mkdir(parents=True,exist_ok=True)
  p.write_text(f'<CharaData><name><id>101</id><str>{name}</str></name></CharaData>',encoding='utf-8')
 bad=tmp_path/'A021/Map.xml';bad.write_text('<!DOCTYPE a><MapData/>')
 names=read_xml_names(tmp_path)
 assert names['entries']['chara']['101']['name']=='Patched' and names['skipped']==1
 assert str(tmp_path) not in json.dumps(names)
 bundle=tmp_path/'bundle.json';bundle.write_text(json.dumps(names));local=tmp_path/'local.json'
 local.write_text(json.dumps({'entries':{'chara':{'102':{'name':'Extra'}}}}))
 all_names=load_names(bundle,local)
 assert entity_name(all_names,'chara',101)=='Patched' and entity_name(all_names,'chara',102)=='Extra'
 assert '名称未收录' in entity_name(all_names,'map',999)


def test_archive_persistence_and_migration_preserve_data(tmp_path):
 from app.desktop_core import DesktopCore
 core=DesktopCore(tmp_path/'profile',settings_path=tmp_path/'settings.json')
 names=tmp_path/'names';names.mkdir();(names/'Chara.xml').write_text('<CharaData><name><id>101</id><str>Synthetic Override</str></name></CharaData>')
 core.import_collection_names(names)
 source=tmp_path/'synthetic.json';source.write_text(json.dumps(export()),encoding='utf-8');core.import_file(source,'example')
 before=core.db.player('example');assert core.archive_logs('example')[0]['musicId']==1
 moved=core.migrate_directory(tmp_path/'moved');assert moved.db.player('example')==before
 assert moved.collection_names()['chara']['101']['name']=='Synthetic Override'
 legacy=dict(before);legacy.pop('archive');core.db.save_player('legacy',legacy)
 assert not core.archive('legacy')['available'] and core.archive_logs('legacy')==[]


def test_malformed_optional_status_and_favorite_ids_are_not_fake_unlocks():
 raw=export();raw['userPlaylogList'][0].update(comboStatus=[1],syncStatus=True)
 raw['userFavoriteList']=[dict(itemKind=[],itemIdList=None),dict(itemKind=9,itemIdList=[True,101,{},'private-string'])]
 a=parse_aquadx(raw)['archive'];row=a['sections']['userPlaylogList'][0]
 assert row['comboStatus'] is None and row['syncStatus'] is None
 assert a['sections']['userFavoriteList']==[dict(itemKind=None,itemIdList=[]),dict(itemKind=9,itemIdList=[101])]
