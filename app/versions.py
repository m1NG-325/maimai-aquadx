"""Canonical chronology shared by public and private reference catalogs."""
OLD = ['maimai', 'maimai PLUS', 'GreeN', 'GreeN PLUS', 'ORANGE', 'ORANGE PLUS',
       'PiNK', 'PiNK PLUS', 'MURASAKi', 'MURASAKi PLUS', 'MiLK', 'MiLK PLUS', 'FiNALE']
DX = ['maimaiでらっくす', 'maimaiでらっくす PLUS', 'Splash', 'Splash PLUS',
      'UNiVERSE', 'UNiVERSE PLUS', 'FESTiVAL', 'FESTiVAL PLUS', 'BUDDiES',
      'BUDDiES PLUS', 'PRiSM', 'PRiSM PLUS', 'CiRCLE', 'CiRCLE PLUS', 'MAGiCAL', 'MAGiCAL PLUS']


def canonical_version(value):
    compact = value.replace('maimai でらっくす', 'maimaiでらっくす')
    if compact.startswith('maimaiでらっくす'):
        suffix = compact[len('maimaiでらっくす'):].strip()
        return 'maimai でらっくす' + (' ' + suffix if suffix else '')
    short = compact.removeprefix('maimai ')
    if short in OLD[2:]:
        return 'maimai ' + short
    if short in DX[2:]:
        return 'maimai でらっくす ' + short
    return value


ORDER = {canonical_version(v): i for i, v in enumerate(OLD + DX)}


def version_order(value):
    # Aggregate 真 starts the old era; aggregate 舞 closes it.
    if value == '真':
        return (-1, '')
    if value == '舞':
        return (len(OLD) - .5, '')
    return (ORDER.get(canonical_version(value), 999), value)
