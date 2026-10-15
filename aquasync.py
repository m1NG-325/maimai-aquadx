#!/usr/bin/env python3
# AquaSync v0.2
# AquaDX 导出成绩转换器（保留 v0.1 命令行入口）
# 功能：
# 1. 读取 AquaDX maimai2 export JSON
# 2. 提取玩家信息和成绩列表
# 3. 输出统一 JSON，供后续接水鱼/落雪转换

import json
import argparse
from pathlib import Path
from app.parser import parse_aquadx
from app.database import Database
from app.calculations import summarize
from app.exporters import export_scores, ExportError


ROOT = Path(__file__).resolve().parent


def write_json(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')


def convert(src, dst, target='unified', db_path=None, current_version=None, allow_partial=False, user_id=None):
    parsed = parse_aquadx(json.loads(Path(src).read_text(encoding='utf-8-sig')))
    db = Database(db_path or ROOT / 'data/aquasync.sqlite3')
    if not db.charts():
        db.import_catalog(json.loads((ROOT / 'data/music_data.json').read_text(encoding='utf-8')), 'bundled diving-fish catalog')
    report = summarize(parsed, db.charts(), current_version)
    report['calculation']['catalogSource'] = db.catalog_source()
    if target == 'unified':
        output = report
    else:
        output, rejected = export_scores(report, target, allow_partial)
        write_json(str(dst) + '.rejected.json', rejected)
    write_json(dst, output)
    if user_id is not None:
        db.save_player(user_id, parsed)
    print(f"完成: {len(parsed['records'])} 条成绩，{len(parsed['best'])} 张最佳谱面；计算 Rating={report['rating']}")
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description='AquaSync AquaDX 成绩转换工具')
    parser.add_argument('src', nargs='?', help='AquaDX 导出 JSON')
    parser.add_argument('dst', nargs='?', help='输出 JSON')
    parser.add_argument('--format', choices=['unified', 'diving-fish', 'lxns'], default='unified')
    parser.add_argument('--db', default=str(ROOT / 'data/aquasync.sqlite3'))
    parser.add_argument('--user-id', help='保存玩家快照供 API 查询')
    parser.add_argument('--current-version', help='明确指定曲库中的新曲版本名称')
    parser.add_argument('--allow-partial', action='store_true', help='允许跳过无法映射谱面，并输出拒绝清单')
    parser.add_argument('--catalog', help='导入水鱼 music_data 格式曲库，原子替换当前曲库')
    parser.add_argument('--refresh-catalog', action='store_true', help='下载公开曲库并更新 SQLite')
    args = parser.parse_args(argv)
    try:
        if args.catalog or args.refresh_catalog:
            if args.refresh_catalog:
                import urllib.request
                url = 'https://www.diving-fish.com/api/maimaidxprober/music_data'
                with urllib.request.urlopen(url, timeout=30) as response:
                    songs = json.loads(response.read().decode('utf-8'))
                source = url
            else:
                songs = json.loads(Path(args.catalog).read_text(encoding='utf-8-sig'))
                source = str(Path(args.catalog).resolve())
            print(f'曲库已更新: {Database(args.db).import_catalog(songs, source)} 张谱面')
        if args.src or args.dst:
            if not args.src or not args.dst:
                parser.error('输入和输出路径必须同时提供')
            convert(args.src, args.dst, args.format, args.db, args.current_version, args.allow_partial, args.user_id)
        elif not (args.catalog or args.refresh_catalog):
            parser.error('请提供输入和输出 JSON 路径，或使用 --catalog / --refresh-catalog')
    except ExportError as e:
        if args.dst:
            write_json(str(args.dst) + '.rejected.json', e.rejected)
        parser.exit(2, f'导出未完成: {e}\n')
    except (ValueError, OSError, KeyError, TypeError) as e:
        parser.exit(2, f'处理失败: {e}\n')


if __name__ == "__main__":
    main()
