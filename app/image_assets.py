"""Read original PNGs or pixel-identical compact release assets."""
import json
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=16)
def aliases(directory):
    try:
        value=json.loads((Path(directory)/'image_aliases.json').read_text(encoding='utf-8'))
        return {key:name for key,name in value.items()
                if isinstance(name,str) and Path(name).name==name and name not in ('.','..')}
    except (OSError,ValueError,AttributeError):return {}


def image_path(path):
    path=Path(path)
    if path.is_file():return path
    name=aliases(str(path.parent)).get(path.name)
    if name:return path.parent/name
    alternative=path.with_suffix('.webp')
    return alternative if path.suffix.lower()=='.png' and alternative.is_file() else path
