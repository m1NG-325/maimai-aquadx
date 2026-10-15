"""Verified copy-and-switch migration; the original profile remains recoverable."""
import hashlib
import json
import os
import shutil
import sqlite3
import tempfile
import uuid
from contextlib import closing
from pathlib import Path


def default_settings_path():
    return Path(os.getenv('LOCALAPPDATA',Path.home()))/'AquaSync-desktop.json'


def configured_directory(settings):
    if not settings.exists():return None
    value=json.loads(settings.read_text(encoding='utf8')).get('dataDirectory')
    if not isinstance(value,str) or not Path(value).is_absolute():raise ValueError('数据目录配置无效：'+str(settings))
    return Path(value)


def save_directory(settings,directory):
    settings.parent.mkdir(parents=True,exist_ok=True)
    temp=settings.with_name(settings.name+'.'+uuid.uuid4().hex+'.tmp')
    try:
        temp.write_text(json.dumps({'schema':1,'dataDirectory':str(directory)},ensure_ascii=False,indent=2),encoding='utf8')
        os.replace(temp,settings)
    finally:
        if temp.exists():temp.unlink()


def digest_file(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.digest()


def copy_profile(source,target):
    source=source.resolve();target=target.expanduser().resolve()
    if source==target:return target
    if target.is_relative_to(source) or source.is_relative_to(target):raise ValueError('新旧数据目录不能互相包含，请选择独立空目录。')
    if target.exists() and (not target.is_dir() or any(target.iterdir())):raise ValueError('目标目录必须为空，现有文件不会被覆盖。')
    target.parent.mkdir(parents=True,exist_ok=True)
    stage=Path(tempfile.mkdtemp(prefix='.aquasync-migration-',dir=target.parent)).resolve()
    try:
        entries=[]
        for current,dirs,files in os.walk(source,followlinks=False):
            for name in dirs+files:
                p=Path(current)/name
                if p.is_symlink() or p.is_junction():raise ValueError('数据目录包含链接，无法安全自动迁移：'+str(p))
                entries.append(p)
        databases=set()
        for p in entries:
            if p.is_file() and p.suffix.lower() in ('.db','.sqlite','.sqlite3'):
                with p.open('rb') as f:header=f.read(16)
                if header==b'SQLite format 3\x00':databases.add(p)
        for p in entries:
            dest=stage/p.relative_to(source);dest.resolve().relative_to(stage)
            if p.is_dir():dest.mkdir(parents=True,exist_ok=True);continue
            if p.name.endswith(('-wal','-shm')) and p.with_name(p.name[:-4]) in databases:continue
            dest.parent.mkdir(parents=True,exist_ok=True)
            if p in databases:
                with closing(sqlite3.connect(p.as_uri()+'?mode=ro',uri=True)) as db,closing(sqlite3.connect(dest)) as out:
                    db.backup(out)
                    if out.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise ValueError('迁移数据库校验失败')
            else:
                shutil.copy2(p,dest)
                if digest_file(p)!=digest_file(dest):raise ValueError('迁移文件校验失败：'+str(p))
        if target.exists():target.rmdir()  # Only an empty, separately chosen destination.
        stage.replace(target);return target
    finally:
        if stage.exists():
            stage.relative_to(target.parent)
            if not stage.name.startswith('.aquasync-migration-'):raise ValueError('Unsafe migration cleanup')
            shutil.rmtree(stage)
