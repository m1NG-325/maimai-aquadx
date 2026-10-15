"""Official update_records / scores request bodies; no network submission."""


class ExportError(ValueError):
    def __init__(self, rejected):
        self.rejected = rejected
        super().__init__(f'{len(rejected)} chart(s) cannot be exported; see rejected list')


def export_scores(summary, target, allow_partial=False):
    if target not in ('diving-fish', 'lxns'):
        raise ValueError('target must be diving-fish or lxns')
    scores, rejected = [], []
    for r in summary['best']:
        reason = None
        if r['musicId'] >= 100000 or r['level'] >= 5:
            reason = 'utage/unsupported chart requires an explicit target mapping'
        elif not r['catalogMatched']:
            reason = 'chart missing from target catalog'
        if reason:
            rejected.append({'musicId': r['musicId'], 'level': r['level'], 'reason': reason})
            continue
        common = {'achievements': r['achievements'], 'level_index': r['level'], 'fc': r['fc'], 'fs': r['fs']}
        if target == 'diving-fish':
            scores.append(dict(common, song_id=r['musicId'], type=r['type'], dxScore=r['dxScore']))
        else:
            scores.append(dict(common, id=r['musicId'] % 10000,
                               type='dx' if r['type'] == 'DX' else 'standard',
                               dx_score=r['dxScore'], fc=r['fc'] or None, fs=r['fs'] or None))
    if rejected and not allow_partial:
        raise ExportError(rejected)
    return (scores if target == 'diving-fish' else {'scores': scores}), rejected
