"""One metadata registry, with region/version variants and independent eligibility rules."""
from copy import deepcopy
from app.versions import canonical_version, version_order

ATOMIC_TYPES=(str,int,float,bool,bytes,type(None))


def copy_chart(chart):
    # JSON scalar values are immutable. Clone containers, without routing every
    # title/number through deepcopy's generic dispatch on each UI refresh.
    return {key:value if type(value) in ATOMIC_TYPES else deepcopy(value) for key,value in chart.items()}


def merge_fields(previous, incoming):
    result=dict(previous)
    for key,value in incoming.items():
        if value is not None and value!='':
            result[key]=value if type(value) in ATOMIC_TYPES else deepcopy(value)
            if key=='ds':result['constantSource']=incoming.get('constantSource') or incoming.get('source','本地曲库')
        elif key not in result:result[key]=value
    return result


class UnifiedCatalog:
    def __init__(self,base,private,plate_catalogs,cn_index,cn_versions):
        self.snapshots=plate_catalogs
        self.cn_index=deepcopy(cn_index)
        self.cn_versions=deepcopy(cn_versions)
        self.variants={'private':{},'cn':{}}
        for rows in [base,private,plate_catalogs['scopes']['jp_history']['charts'],plate_catalogs['scopes']['jp']['charts']]:
            self.add('private',rows)
        self.add('cn',plate_catalogs['scopes']['cn']['charts'])
        codes=sorted((v for v in cn_versions if isinstance(v.get('version'),int)),key=lambda v:v['version'])
        current=codes[-1]['version'] if codes else max((c['version']//1000*1000 for c in cn_index.values() if isinstance(c.get('version'),int)),default=0)
        cn_rows=[]
        for (mid,kind,level),chart in cn_index.items():
            code=chart.get('version');title=next((v['title'] for v in reversed(codes) if isinstance(code,int) and code>=v['version']),str(code))
            cn_rows.append(dict(music_id=mid+(10000 if kind=='dx' else 0),level_index=level,
                                title=chart['title'],ds=chart.get('ds'),level=chart['level'],type='DX' if kind=='dx' else 'SD',
                                version=title,is_new=isinstance(code,int) and code>=current,disabled=chart.get('disabled',False),
                                version_code=code,source='落雪国服曲库',reference_only=True))
        self.add('cn',cn_rows)
        for c in self.variants['cn'].values():
            code=c.get('version_code')
            if not isinstance(code,int):
                code=next((v['version'] for v in codes if canonical_version(v['title'])==c['version']),None)
            c['is_new']=isinstance(code,int) and code>=current
        self.regions={key:self.latest(values) for key,values in self.variants.items()}
        # Country-only songs can still be found; JP constants for shared songs stay JP.
        all_rows=dict(self.regions['cn']);all_rows.update(self.regions['private']);self.regions['all']=all_rows

    def add(self,region,rows):
        target=self.variants[region]
        for row in rows:
            if not 0<row['music_id']<100000 or row['level_index'] not in range(5):continue
            c=dict(row,version=canonical_version(row['version']),metadataRegion=region)
            identity=(c['music_id'],c['level_index'],c['version'])
            target[identity]=merge_fields(target.get(identity,{}),c)

    @staticmethod
    def latest(variants):
        result={}
        for _,c in sorted(variants.items(),key=lambda pair:version_order(pair[0][2])):
            result[(c['music_id'],c['level_index'])]=c
        return result

    def charts(self,scope='private'):
        if scope in ('jp','jp_history'):
            return self.plate_scopes()[scope]['charts']
        if scope not in self.regions:raise ValueError('未知曲库范围')
        return [copy_chart(c) for _,c in sorted(self.regions[scope].items())]

    def plate_scopes(self):
        result=deepcopy(self.snapshots['scopes'])
        for scope in ('jp','cn','jp_history'):
            region='cn' if scope=='cn' else 'private'
            for i,c in enumerate(result[scope]['charts']):
                key=(c['music_id'],c['level_index'],c['version'])
                variant=self.variants[region].get(key)
                if variant:
                    result[scope]['charts'][i]=merge_fields(c,variant)
        return result
