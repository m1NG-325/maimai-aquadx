"""Build pixel-identical offline assets; never modify original source artwork."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import io
import json
from pathlib import Path
import shutil
from PIL import Image


def ensure_compact(source,output):
    source=Path(source).resolve();output=Path(output).resolve()
    marker=output.with_name(output.name+'.build.json')
    signature=[[p.relative_to(source).as_posix(),p.stat().st_size,p.stat().st_mtime_ns]
               for p in sorted(source.rglob('*')) if p.is_file()]
    if output.is_dir() and marker.is_file():
        try:
            previous=json.loads(marker.read_text(encoding='utf-8'))
            if previous['inputs']==signature:return previous['result']
        except (OSError,ValueError,KeyError):pass
    result=compact(source,output)
    marker.write_text(json.dumps(dict(inputs=signature,result=result)),encoding='utf-8')
    return result


def compact(source,output,workers=6):
    source=Path(source).resolve();output=Path(output).resolve()
    if source==output or output.is_relative_to(source) or source.is_relative_to(output):
        raise ValueError('Use a separate output directory')
    output.mkdir(parents=True,exist_ok=True)
    files=sorted(p for p in source.rglob('*') if p.is_file())
    jobs=[];aliases={};seen={};original=0;retained=[]
    for path in files:
        rel=path.relative_to(source);original+=path.stat().st_size
        if rel.parts[0] in ('archive','covers') and path.suffix.lower()=='.png':
            digest=hashlib.sha256(path.read_bytes()).hexdigest();key=(rel.parent,digest)
            if key in seen:
                aliases.setdefault(rel.parent,{})[path.name]=seen[key];continue
            name=path.with_suffix('.webp').name;seen[key]=name
            aliases.setdefault(rel.parent,{})[path.name]=name;jobs.append((path,output/rel.with_suffix('.webp')))
        else:
            target=output/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,target);retained.append(rel.as_posix())

    def encode(job):
        path,target=job;target.parent.mkdir(parents=True,exist_ok=True)
        with Image.open(path) as image:
            rgba=image.convert('RGBA');stream=io.BytesIO()
            options={key:image.info[key] for key in ('icc_profile','exif') if key in image.info}
            rgba.save(stream,format='WEBP',lossless=True,exact=True,method=4,**options)
            blob=stream.getvalue()
            with Image.open(io.BytesIO(blob)) as check:
                if check.size!=rgba.size or check.convert('RGBA').tobytes()!=rgba.tobytes():raise ValueError(f'Pixel mismatch: {path.name}')
            target.write_bytes(blob)
            return {'file':target.relative_to(output).as_posix(),'width':rgba.width,'height':rgba.height,
                    'rgbaSha256':hashlib.sha256(rgba.tobytes()).hexdigest()}
    with ThreadPoolExecutor(max_workers=workers) as pool:
        records=list(pool.map(encode,jobs))
    for folder,values in aliases.items():
        (output/folder/'image_aliases.json').write_text(json.dumps(values,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    expected=set(retained)|{r['file'] for r in records}|{(p/'image_aliases.json').as_posix() for p in aliases}
    # A stale generated asset must not re-enter a future release.
    for path in output.rglob('*'):
        if path.is_file() and path.relative_to(output).as_posix() not in expected:path.unlink()
    size=sum(p.stat().st_size for p in output.rglob('*') if p.is_file())
    return dict(originalBytes=original,compactBytes=size,uniqueImages=len(records),
                duplicateImages=sum(len(v) for v in aliases.values())-len(records),pixelChecks=len(records))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True);parser.add_argument('--workers',type=int,default=6)
    args=parser.parse_args();print(json.dumps(compact(args.source,args.output,args.workers),indent=2))
