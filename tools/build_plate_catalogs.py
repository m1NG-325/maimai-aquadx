"""Build reviewed offline region snapshots from separately downloaded audit inputs.

No network access, player data, audio, or .ma2 files are copied to the output.
"""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import sys
import unicodedata

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.private_catalog import salt_charts
from app.report_models import PLATE_WORDS
from app.versions import canonical_version, OLD, DX


def normalize(title):
    return ''.join(unicodedata.normalize('NFKC', title).lower().split()).replace('’', "'")


def build(audit, inputs):
    read = lambda path: json.loads(path.read_text(encoding='utf-8'))
    official = read(audit/'official.json')
    otoge = read(audit/'otoge.json')
    local = read(audit/'local-merged.json')
    server = read(audit/'server-comparison.json')['serverCharts']
    salt = salt_charts(read(audit/'salt.json'))
    matches = read(inputs/'new-id-matches.json')
    ids = {(normalize(c['title']), c['type']): c['music_id'] for c in local}
    ids.update({(normalize(c['title']), 'DX' if c['id'] >= 10000 else 'SD'): c['id'] for c in server})
    ids.update({(normalize(c['title']), c['type']): c['music_id'] for c in salt})
    artist_ids = {(normalize(c['title']), c['type'], normalize(c.get('artist') or '')): c['music_id'] for c in local + salt if c.get('artist')}
    for m in matches:
        if m['error'] >= 3 or m['runnerUp'] - m['error'] <= 20:
            raise ValueError('unverified new ID')
        ids[(normalize(m['title']), 'DX')] = m['id'] + 10000
    references = {(c['music_id'], c['level_index']): c for c in local}
    references.update({(c['music_id'], c['level_index']): c for c in salt})
    extended = {normalize(s['title']): s for s in otoge}
    chronology = list(zip([10000,11000,12000,13000,14000,15000,16000,17000,18000,18500,19000,19500,19900,
                           20000,20500,21000,21500,22000,22500,23000,23500,24000,24500,25000,25500,26000,26500,27000,27500], OLD+DX))
    current = []
    for song in official:
        if song['catcode'] == '宴会場':
            continue
        for kind, prefix in [('SD',''),('DX','dx_')]:
            if not song.get(prefix+'lev_mas'):
                continue
            mid = artist_ids.get((normalize(song['title']),kind,normalize(song['artist']))) or ids.get((normalize(song['title']), kind))
            if mid is None:
                raise ValueError('official song has no verified ID: '+song['title']+' '+kind)
            ext = extended.get(normalize(song['title']), {})
            for difficulty, suffix in enumerate(('bas','adv','exp','mas','remas')):
                field = prefix+'lev_'+suffix
                if not song.get(field):
                    continue
                ref = references.get((mid,difficulty), {})
                version = ref.get('version') or canonical_version(next(v for code,v in reversed(chronology) if int(song['version']) >= code))
                ds = ref.get('ds')
                if ds is None and ext.get(field+'_i'):
                    ds = float(ext[field+'_i'])
                current.append(dict(music_id=mid,level_index=difficulty,title=song['title'],type=kind,
                    level=song[field],ds=ds,version=version,artist=song['artist'],bpm=ext.get('bpm'),
                    source='https://maimai.sega.jp/data/maimai_songs.json',reference_only=True))

    historical_titles = set(read(audit/'historical-wiki-title-keys.json'))
    # Only publicly cross-checked historical identities; exclude private/custom placeholders.
    historical = []
    for song in server:
        if normalize(song['title']) not in historical_titles or song['id'] == 854:  # Old utage, not a normal version-plate chart.
            continue
        c = song['chart']; ds = c['ds']
        level = str(int(ds)) + ('+' if ds % 1 >= .6 - 1e-8 else '')
        historical.append(dict(music_id=song['id'],level_index=c['difficulty'],title=song['title'],
            type='DX' if song['id']>=10000 else 'SD',level=level,ds=ds,version=canonical_version(song['version']),
            source='historical Music.xml; identity checked against https://gamerch.com/maimai/533442',
            reference_only=True,historical=True,constantStatus='Historical local reference; not verified official constant'))
    archived = read(audit/'deleted.json')
    historical_ids = {normalize(base64.b64decode(title).decode('utf-8')): int(mid) for mid,title in read(inputs/'songids.json').items()}
    known_historical = {(c['music_id'],c['level_index']) for c in historical + current}
    for song in archived:
        if song['title'] != 'ブリキノダンス':
            continue
        mid=historical_ids[normalize(song['title'])]
        version=canonical_version(next(v for code,v in reversed(chronology) if int(song['version']) >= code))
        for difficulty,suffix in enumerate(('bas','adv','exp','mas','remas')):
            field='lev_'+suffix
            if not song.get(field) or (mid,difficulty) in known_historical:
                continue
            historical.append(dict(music_id=mid,level_index=difficulty,title=song['title'],type='SD',
                level='12+' if difficulty==3 else song[field],ds=None,version=version,artist=song['artist'],bpm=song['bpm'],
                source='https://github.com/zvuc/otoge-db/blob/main/maimai/data/music-ex-deleted.json',
                reference_only=True,historical=True,constantStatus='Exact historical constant not verified'))
    # Keep the old and revived Can Do in their respective versions. Shared score IDs remain reference-only.
    merged = {(c['music_id'],c['level_index'],c['version']): c for c in historical}
    merged.update({(c['music_id'],c['level_index'],c['version']): c for c in current})

    music = read(inputs/'karen-res-music.json')
    plates = read(inputs/'karen-plate.json')
    cn = []
    for song in music:
        if song['id'] >= 100000 or song['type'] not in ('SD','DX'):
            continue
        for difficulty, c in enumerate(song['charts'][:5]):
            cn.append(dict(music_id=song['id'],level_index=difficulty,title=song['name'],type=song['type'],
                level=c['level'],ds=c.get('levelValue'),version=canonical_version(song['version']),
                artist=song.get('artist'),bpm=song.get('bpm'),notes=c.get('notes'),designer=c.get('notesDesigner'),
                source='https://github.com/xszqxszq/KarenBot-Resources/blob/main/data/maimai/music.json',reference_only=True))
    available = {(c['music_id'],c['level_index']) for c in cn}
    prefixes = {word:version for version,word in PLATE_WORDS.items()}
    prefixes['真']='真';prefixes['舞']='舞'
    requirements = {}
    omitted = set()
    cn_versions = read(inputs/'match-covers/karen-version.json')
    newest_cn = max(v['version'] for v in cn_versions)
    cn_words = {PLATE_WORDS.get(canonical_version(v)) for code,v in chronology if code <= newest_cn} | {'真','舞'}
    for plate in plates:
        for mark, suffix in [('将','将'),('极','極'),('神','神'),('舞舞','舞舞')]:
            word=plate['name'][:-len(suffix)] if plate['name'].endswith(suffix) else ''
            if word not in prefixes or word not in cn_words or not plate['requires']:
                continue
            keys={(mid,level) for mid in plate['requires'] for level in range(4)}
            keys.update((mid,4) for mid in plate['remasters'])
            omitted.update(mid for mid,level in keys if (mid,level) not in available)
            requirements.setdefault(prefixes[word],{})[mark]=sorted(keys & available)
    # Match KarenBot's filter over its loaded music.json, not unpublished plate-only IDs.
    requirements={v:marks for v,marks in requirements.items() if any(marks.values())}
    scopes={
        'jp':dict(charts=current,description='日服现行普通谱面；截至 2026-10-17，排除官方已删除、暂缓收录与宴谱。'),
        'cn':dict(charts=cn,requirements=requirements,description='可怜 bot 国服 music.json 与 plate.json 的要求交集；DX 年度分组合并规则沿用 bot。'),
        'jp_history':dict(charts=list(merged.values()),description='日服现行谱面加已核实历史谱面；不受这台私服安装范围限制。历史定数为参考，Can Do 保留旧版与复活版分组。')}
    return dict(schema=1,retrieved='2026-10-17',scopes=scopes,
        provenance=dict(official='https://maimai.sega.jp/data/maimai_songs.json',
            salt='https://github.com/realtvop/SaltMeta',otoge='https://github.com/zvuc/otoge-db',
            cnMusic='https://github.com/xszqxszq/KarenBot-Resources/blob/main/data/maimai/music.json',
            cnPlates='https://github.com/xszqxszq/KarenBot-Resources/blob/main/data/maimai/plate.json',
            historical='https://gamerch.com/maimai/533442',idMatches=matches,
            excludedHistoricalUtage=[854],
            sourceHashes={name:hashlib.sha256((inputs/name).read_bytes()).hexdigest() for name in ('karen-res-music.json','karen-plate.json','songids.json','match-covers/karen-version.json')},
            cnPlateIdsAbsentFromMusic=sorted(omitted)))


if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('audit',type=Path);parser.add_argument('inputs',type=Path);parser.add_argument('output',type=Path)
    args=parser.parse_args();value=build(args.audit,args.inputs)
    args.output.write_text(json.dumps(value,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    print({key:len(scope['charts']) for key,scope in value['scopes'].items()})
