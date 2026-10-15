"""Recover bundled report assets for source rebuilds without duplicating the ZIP."""
import argparse
from pathlib import Path,PureWindowsPath
from PyInstaller.archive.readers import CArchiveReader

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('exe',type=Path)
    parser.add_argument('output',type=Path)
    args=parser.parse_args();root=args.output.resolve();archive=CArchiveReader(str(args.exe))
    count=0
    for name in archive.toc:
        parts=PureWindowsPath(name).parts
        if parts[:2]!=('data','report_assets'):continue
        relative=Path(*parts[2:])
        if '..' in relative.parts or relative.is_absolute():raise ValueError('unsafe asset path')
        destination=(root/relative).resolve();destination.relative_to(root)
        destination.parent.mkdir(parents=True,exist_ok=True)
        destination.write_bytes(archive.extract(name));count+=1
    print(f'Extracted {count} assets to {root}')
