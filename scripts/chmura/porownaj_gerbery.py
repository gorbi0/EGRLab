"""Porównanie dwóch plików Gerber X2 z tolerancją położenia wierzchołków (chmura / Windows).

Najpierw porównanie dokładne z Plytki/P00-R3-review/src/gerber_equiv.py (multizbiór flash/stroke/region,
niezależny od numeracji apertur i kolejności obiektów). Obiekty, które nie mają dokładnej pary, są parowane
w obrębie tej samej klasy (rodzaj, apertura, polaryzacja): kontur regionu z konturem o największej liczbie
wspólnych wierzchołków, flash i odcinek po najbliższym położeniu. Para jest przyjęta, gdy odległość
Hausdorffa między zbiorami wierzchołków nie przekracza tolerancji.

Po co: KiCad 10.0.6 na Windows (MSVC) i na Linuksie (GCC) potrafi zaokrąglić pojedyncze wierzchołki
wypełnienia wylewki lub wielokąta pola o 1 nm (P04-R2.2: 3 kontury na warstwę miedzi). Produkcyjnie bez
znaczenia, ale porównanie dokładne zgłasza wtedy RÓŻNICĘ.

  python3 scripts/chmura/porownaj_gerbery.py A.gtl B.gtl [--tol-nm 10]
Kod wyjścia: 0 = identyczne semantycznie lub w tolerancji, 1 = różnica.
"""
import collections, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'Plytki' / 'P00-R3-review' / 'src'))
from gerber_equiv import normalize  # noqa: E402  (tylko odczyt modułu z zamkniętego pakietu)


def unit_nm(fmt):
    m = re.match(r'FSLAX(\d)(\d)Y(\d)(\d)', fmt or '')
    return 10 ** (6 - int(m[2])) if m else 1  # mm: 10^-dec mm; 1 nm = 10^-6 mm


def vertices(key):
    if key[0] == 'R':
        pts = set()
        for e in key[2]:
            for p in e:
                if isinstance(p, tuple) and len(p) == 2 and all(isinstance(v, int) for v in p):
                    pts.add(p)
        return pts
    if key[0] == 'F':
        return {key[3]}
    if key[0] == 'S':
        return set(key[3])
    return {p for p in key[3:5] if isinstance(p, tuple)}


def hausdorff(a, b):
    def d(p, S):
        return min(((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2) ** .5 for q in S)
    if not a or not b:
        return float('inf')
    return max(max(d(p, b) for p in a - b) if a - b else 0.0, max(d(p, a) for p in b - a) if b - a else 0.0)


def compare(a, b, tol_nm=10.0):
    fa, ia = normalize(a); fb, ib = normalize(b)
    res = {'format_equal': fa == fb, 'objects': (sum(ia.values()), sum(ib.values())), 'exact': fa == fb and ia == ib,
           'unmatched_exact': 0, 'paired_within_tol': 0, 'max_dev_nm': 0.0, 'unpaired': 0}
    if res['exact'] or not res['format_equal']:
        return res
    scale = unit_nm(fa)
    only_a, only_b = list((ia - ib).elements()), list((ib - ia).elements())
    res['unmatched_exact'] = len(only_a)
    cls = lambda k: (k[0], k[1] if k[0] != 'R' else None, k[2] if k[0] != 'R' else k[1])
    pool = collections.defaultdict(list)
    for k in only_b:
        pool[cls(k)].append(k)
    for k in only_a:
        cand = pool.get(cls(k), [])
        if not cand:
            res['unpaired'] += 1; continue
        va = vertices(k)
        best = max(cand, key=lambda y: (len(va & vertices(y)), -abs(len(vertices(y)) - len(va))))
        dev = hausdorff(va, vertices(best)) * scale
        if dev <= tol_nm:
            cand.remove(best); res['paired_within_tol'] += 1; res['max_dev_nm'] = max(res['max_dev_nm'], dev)
        else:
            res['unpaired'] += 1
    res['unpaired'] += sum(len(v) for v in pool.values())  # obiekty z B, które nie dostały pary
    return res


def verdict(res):
    if res['exact']:
        return 'EQUAL'
    if res['format_equal'] and res['unpaired'] == 0 and res['objects'][0] == res['objects'][1]:
        return 'EQUAL~'
    return 'DIFFERENT'


if __name__ == '__main__':
    tol = float(sys.argv[sys.argv.index('--tol-nm') + 1]) if '--tol-nm' in sys.argv else 10.0
    r = compare(sys.argv[1], sys.argv[2], tol)
    v = verdict(r)
    print(v, f"obiekty {r['objects'][0]}/{r['objects'][1]}",
          '' if r['exact'] else f"bez dokładnej pary {r['unmatched_exact']}, w tolerancji {r['paired_within_tol']}, "
                                f"maks. odchyłka {r['max_dev_nm']:.1f} nm, bez pary {r['unpaired']}")
    sys.exit(0 if v != 'DIFFERENT' else 1)
