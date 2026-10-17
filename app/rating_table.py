"""Rating reference values generated from the shared DX formula, never from an image."""
from decimal import Decimal, ROUND_CEILING
from app.calculations import rating, COEFFICIENTS

# label, achievement, mode; step columns show the first extra point in that band.
COLUMNS = (
    ('SSS+', '100.5000', 'fixed'), ('SSS', '100.4999', 'fixed'),
    ('SSS +1', '100.0000', 'step'), ('SSS', '100.0000', 'fixed'),
    ('SS+', '99.9999', 'fixed'), ('SS+ +1', '99.5000', 'step'),
    ('SS+', '99.5000', 'fixed'), ('SS +1', '99.0000', 'step'),
    ('SS', '99.0000', 'fixed'), ('S+', '98.9999', 'fixed'),
    ('S+ +1', '98.0000', 'step'), ('S+', '98.0000', 'fixed'),
    ('S +1', '97.0000', 'step'), ('S', '97.0000', 'fixed'),
)
BAND_END = {'100.0000': '100.4999', '99.5000': '99.9999',
            '99.0000': '99.5000', '98.0000': '98.9999', '97.0000': '98.0000'}


def first_extra_point(ds, base):
    """Smallest 0.0001% achievement gaining one point before the next coefficient."""
    constant, low = Decimal(str(ds)), Decimal(base)
    start, _ = rating(constant, low)
    coefficient = next(Decimal(str(c)) for a, c, _ in reversed(COEFFICIENTS) if low >= Decimal(str(a)))
    target = (Decimal(start + 1) * 100 / (constant * coefficient)).quantize(Decimal('.0001'), rounding=ROUND_CEILING)
    return target if target < Decimal(BAND_END[base]) else None


def reference_rows(minimum=12, maximum=15):
    low, high = Decimal(str(minimum)), Decimal(str(maximum))
    if not low.is_finite() or not high.is_finite() or not Decimal('.1') <= low <= high <= 20:
        raise ValueError('定数范围应为 0.1～20.0，最低定数不能大于最高定数')
    if low * 10 != int(low * 10) or high * 10 != int(high * 10):
        raise ValueError('定数间隔为 0.1')
    rows = []
    for tenth in range(int(high * 10), int(low * 10) - 1, -1):
        ds = Decimal(tenth) / 10
        cells = []
        for label, base, mode in COLUMNS:
            achievement = first_extra_point(ds, base) if mode == 'step' else Decimal(base)
            value, rank = rating(ds, achievement) if achievement is not None else (None, None)
            cells.append(dict(label=label, ra=value, rank=rank,
                              achievement=float(achievement) if achievement is not None else None, mode=mode))
        rows.append(dict(ds=float(ds), cells=cells))
    return rows
