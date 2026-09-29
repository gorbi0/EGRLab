"""Próby ujemne kontroli CAM: każda kopia pakietu dostaje jedną celową usterkę w plikach
produkcyjnych, a sumy w kopii pokwitowania eksportu są przeliczone — tak, żeby usterkę mogła
wykryć wyłącznie kontrola geometryczna, nie porównanie bajtów. Próba zerowa (bez usterki) musi przejść.
Uruchomienie: python src/cam_negative_controls.py   (oryginalnych plików nie zmienia)
"""
from pathlib import Path
import hashlib, json, re, shutil, subprocess, sys, tempfile

R = Path(__file__).resolve().parents[1]
CFG = json.loads((R/'src'/'config.json').read_text(encoding='utf-8'))
N = CFG['name']
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def first(pattern, text, flags=0):
    m = re.search(pattern, text, flags)
    assert m, pattern
    return m


def drop_pad_flash(t):  # usuń pierwsze pole oznaczone atrybutem .P (flash D03)
    m = first(r'%TO\.P,[^%]*\*%\n(?:%TO\.[^%]*\*%\n)*X-?\d+Y-?\d+D03\*\n', t)
    return t[:m.start()] + t[m.end():]


def shift_drill(t):  # przesuń pierwszy otwór o 0,1 mm w X
    m = first(r'\nX(-?[\d.]+)Y(-?[\d.]+)\n', t)
    return t[:m.start()] + f'\nX{float(m.group(1)) + 0.1:.3f}Y{m.group(2)}\n' + t[m.end():]


def resize_tool(t):  # zmień średnicę drugiego narzędzia o 0,05 mm
    tools = re.findall(r'^T(\d+)C([\d.]+)$', t, re.M)
    n, d = tools[1] if len(tools) > 1 else tools[0]
    return re.sub(rf'^T{n}C{re.escape(d)}$', f'T{n}C{float(d) + 0.05:.3f}', t, count=1, flags=re.M)


def drop_mask_opening(t):  # usuń pierwsze otwarcie maski (flash lub region) należące do pola
    m = re.search(r'X-?\d+Y-?\d+D03\*\n', t)
    if m:
        return t[:m.start()] + t[m.end():]
    m = first(r'G36\*\n(?:.*\n)*?G37\*\n', t)
    return t[:m.start()] + t[m.end():]


def move_outline(t):  # przesuń prawy bok obrysu o 0,5 mm
    w = int(CFG['board_mm'][0] * 1_000_000)
    return t.replace(f'X{w}Y', f'X{w + 500000}Y')


def swap_net(t):  # zmień nazwę sieci w pierwszym atrybucie .N przy polu
    m = first(r'%TO\.N,([^*%]+)\*%', t)
    return t[:m.start()] + '%TO.N,ZLA_SIEC*%' + t[m.end():]


def drop_zone(t):  # usuń pierwszy region wylewki: G36..G37 bez aktywnego atrybutu .P (śledzonego jak w parserze)
    lines = t.splitlines(keepends=True)
    has_p, start = False, None
    for i, ln in enumerate(lines):
        s = ln.strip()
        if s.startswith('%TO.P,'):
            has_p = True
        elif s == '%TD*%' or s.startswith('%TD.P'):
            has_p = False
        elif s == 'G36*' and not has_p:
            start = i
        elif s == 'G37*' and start is not None:
            return ''.join(lines[:start] + lines[i + 1:])
    raise AssertionError('brak regionu wylewki')


CASES = [
    ('zero', None, None, None),
    ('usunięte pole w miedzi górnej', f'{N}-F_Cu.gtl', drop_pad_flash, 'Miedź góra'),
    ('przesunięty otwór PTH', f'{N}-PTH.drl', shift_drill, 'PTH: każdy otwór'),
    ('zmieniona średnica wiertła', f'{N}-PTH.drl', resize_tool, 'PTH: każdy otwór'),
    ('brak otwarcia maski', f'{N}-F_Mask.gts', drop_mask_opening, 'Maska góra'),
    ('zmieniony obrys', f'{N}-Edge_Cuts.gm1', move_outline, 'obrys'),
    ('zła sieć na polu', f'{N}-B_Cu.gbl', swap_net, 'Miedź dół'),
    ('usunięta wylewka', f'{N}-B_Cu.gbl', drop_zone, 'wylewek'),
]
results = []
for label, fname, mutate, expect in CASES:
    with tempfile.TemporaryDirectory() as td:
        T = Path(td)/'pkg'
        for sub in ('src', 'gerber', 'verification'):
            shutil.copytree(R/sub, T/sub)
        (T/'podglad').mkdir()
        if mutate:
            f = T/'gerber'/fname
            before = f.read_text(encoding='ascii')
            after = mutate(before)
            assert after != before, label
            f.write_text(after, encoding='ascii')
        rec = json.loads((T/'verification'/'export-receipt.json').read_text(encoding='utf-8'))
        rec['files'] = {f.name: sha(f) for f in sorted((T/'gerber').iterdir())}
        (T/'verification'/'export-receipt.json').write_text(json.dumps(rec, indent=2), encoding='utf-8')
        r = subprocess.run([sys.executable, str(T/'src'/'check_cam.py')], capture_output=True, text=True)
        rep = json.loads((T/'verification'/'cam-checks.json').read_text(encoding='utf-8')) if (T/'verification'/'cam-checks.json').exists() else {'checks': []}
        failed = [c['name'] for c in rep['checks'] if not c['pass']]
        if mutate is None:
            ok = r.returncode == 0 and not failed
        else:
            ok = r.returncode != 0 and bool(failed) and (expect is None or any(expect in n for n in failed))
        results.append({'próba': label, 'plik': fname, 'ok': ok, 'znaczenie_ok': 'usterka wykryta' if mutate else 'czysta kopia przeszła', 'nieudane_kontrole': failed})
        print(('OK  ' if ok else 'BŁĄD') + f' {label}: {failed}')
(R/'verification'/'cam-negative-controls.json').write_text(json.dumps(results, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
if not all(x['ok'] for x in results):
    raise SystemExit(1)
