"""Normalize downloaded SaltMeta next data; keep provenance and content hash."""
import argparse
import hashlib
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.private_catalog import salt_charts

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    raw = args.input.read_bytes()
    charts = salt_charts(json.loads(raw))
    args.output.write_text(json.dumps({'schema': 1, 'source': 'https://github.com/realtvop/SaltMeta',
                                     'sha256': hashlib.sha256(raw).hexdigest(),
                                     'retrieved': '2026-10-14', 'charts': charts}, ensure_ascii=False), encoding='utf-8')
    print(f'{len(charts)} JP reference charts')
