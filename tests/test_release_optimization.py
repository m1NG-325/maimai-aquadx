import json
from pathlib import Path
from PIL import Image
from app.image_assets import image_path,aliases
from app.collection_metadata import entity_image,_entity_image_index
from tools.compact_assets import compact,ensure_compact


def test_lossless_compact_assets_aliases_and_original_priority(tmp_path):
    source=tmp_path/'source';output=tmp_path/'compact';folder=source/'archive';folder.mkdir(parents=True)
    image=Image.new('RGBA',(40,40),(12,38,55,0));image.putpixel((1,1),(123,201,19,127))
    image.save(folder/'one.png');(folder/'two.png').write_bytes((folder/'one.png').read_bytes())
    (folder/'manifest.json').write_text(json.dumps({'entries':{'icon:1':{'file':'one.png'},'icon:2':{'file':'two.png'},'icon:3':{'file':'../bad.png'}}}))
    result=compact(source,output,2)
    assert result['pixelChecks']==1 and result['duplicateImages']==1
    a=image_path(output/'archive/one.png');b=image_path(output/'archive/two.png');assert a==b and a.suffix=='.webp'
    assert Image.open(a).convert('RGBA').tobytes()==image.tobytes()
    assert entity_image(output/'archive','icon',1)==str(a.resolve())
    assert entity_image(output/'archive','icon',3) is None
    image.save(output/'archive/one.png');assert image_path(output/'archive/one.png').suffix=='.png'


def test_compact_build_cache_tracks_source_changes(tmp_path):
    source=tmp_path/'source';source.mkdir();(source/'covers').mkdir();output=tmp_path/'out'
    Image.new('RGBA',(8,8),'red').save(source/'covers/1.png')
    first=ensure_compact(source,output);assert first['pixelChecks']==1
    before=(output/'covers/1.webp').stat().st_mtime_ns
    assert ensure_compact(source,output)==first and (output/'covers/1.webp').stat().st_mtime_ns==before
    Image.new('RGBA',(8,8),'green').save(source/'covers/1.png')
    ensure_compact(source,output)
    assert Image.open(output/'covers/1.webp').convert('RGBA').getpixel((0,0))==(0,128,0,255)


def test_catalog_session_is_nested_and_does_not_persist(tmp_path):
    from tests.test_archive_ui import core_with_archive
    core=core_with_archive(tmp_path)
    with core.catalog_session():
        first=core.shared_catalog()
        with core.catalog_session():assert core.shared_catalog() is first
        assert core.shared_catalog() is first
        rows=core.catalog('private');rows[0]['title']='mutated return value'
        assert core.catalog('private')[0]['title']!='mutated return value'
    assert core._session_catalog is None
    assert core.shared_catalog() is not first
    try:
        with core.catalog_session():raise ValueError('abort refresh')
    except ValueError:pass
    assert core._catalog_depth==0 and core._session_catalog is None
