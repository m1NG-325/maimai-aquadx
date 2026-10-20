"""Read Lxns score CSV exports into local snapshots, without network access."""
import csv
import io
from decimal import Decimal, InvalidOperation
from app.parser import parse_aquadx, integer, FC, FS
from app.score_times import parse_play_time

REQUIRED = {'id', 'song_name', 'level_index', 'achievements', 'fc', 'fs', 'dx_score', 'song_type'}
NOTICE = '落雪 CSV 只包含成绩，不含玩家资料、原始 B50 分组、游玩日志或收藏档案；B50 按本地曲库估算。'


def parse_lxns_csv(text):
    reader = csv.DictReader(io.StringIO(text.lstrip('\ufeff'), newline=''), strict=True)
    headers = reader.fieldnames or []
    if len(headers) != len(set(headers)) or not REQUIRED.issubset(headers):
        raise ValueError('落雪 CSV 表头不正确，缺少字段：' + ', '.join(sorted(REQUIRED-set(headers))))
    records, originals = [], []
    try:
        for row in reader:
            if None in row or any(value is None for value in row.values()):
                raise ValueError(f'CSV 第 {reader.line_num} 行：列数不正确')
            row = {key: value.strip() for key, value in row.items()}
            try:
                mid = integer(row['id'], 'id', 1)
                if mid >= 10000:
                    raise ValueError('id 必须是不含 DX 偏移的落雪曲目 ID')
                kind = row['song_type'].lower()
                if kind not in ('standard', 'dx'):
                    raise ValueError('song_type 只支持 standard / dx 普通谱面')
                level = integer(row['level_index'], 'level_index')
                if level > 4:
                    raise ValueError('level_index 必须为 0..4')
                achievement = Decimal(row['achievements']) * 10000
                raw = integer(achievement, 'achievements')
                if raw > 1010000:
                    raise ValueError('achievements 必须为 0..101 且最多四位小数')
                fc, fs = row['fc'].lower(), row['fs'].lower()
                if fc not in FC.values() or fs not in FS.values():
                    raise ValueError('未知 FC / FS 标记')
                record = dict(musicId=mid+(10000 if kind == 'dx' else 0), level=level,
                              achievement=raw, deluxscoreMax=integer(row['dx_score'], 'dx_score'),
                              comboStatus=next(k for k,v in FC.items() if v == fc),
                              syncStatus=next(k for k,v in FS.items() if v == fs))
                if row.get('play_time'):
                    if not parse_play_time(row['play_time']):
                        raise ValueError('play_time 不是有效游玩时间')
                    record['lastPlayedAt'] = row['play_time']
                records.append(record)
                originals.append(row)
            except (ValueError, InvalidOperation) as exc:
                raise ValueError(f'CSV 第 {reader.line_num} 行：{exc}') from None
    except csv.Error as exc:
        raise ValueError(f'CSV 第 {reader.line_num} 行格式错误：{exc}') from None
    if not records:
        raise ValueError('落雪 CSV 没有成绩记录，未更新本地快照')
    payload = parse_aquadx({'userMusicDetailList': records})
    payload['source'] = 'Lxns CSV'
    payload['ratingComposition']['warnings'] = [NOTICE]
    payload['importInfo'] = {'format': 'lxns-csv', 'warnings': [NOTICE], 'rows': originals}
    return payload
