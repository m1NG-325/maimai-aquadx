"""Generated test scores only; no exported player data."""
import json
from app.desktop_core import DesktopCore


def sample(tmp_path):
    core=DesktopCore(tmp_path)
    charts=core.catalog('private')[:6]
    raw={'userMusicDetailList':[dict(musicId=c['music_id'],level=c['level_index'],achievement=990000+i*500,deluxscoreMax=100+i*10,comboStatus=i%5,playCount=i+1) for i,c in enumerate(charts)]}
    path=tmp_path/'synthetic.json';path.write_text(json.dumps(raw),encoding='utf-8')
    core.import_file(path,'example')
    return core,core.overview('example')
