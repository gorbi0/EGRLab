"""P12 R2 (wariant pełny): kontrakt pinowy płytki połączeń z pinoutów płytek stosu (jedno źródło dla schematu, PCB i kontroli).

Czyta te same pliki co Plytki/P12-przygotowanie/src/kontrakty.py (lista w P12-przygotowanie/zrodla.json). Pliki z gałęzi bieżącej
(P02..P11) są czytane z drzewa roboczego, a pinouty płytek wariantu pełnego z ich gałęzi (`git show ref:plik`, ref z zrodla.json:
P04 R3 origin/p04-r3-pcb, P07 S1 origin/p07-s1-pcb, P08 R2 origin/p08-r2-pcb). Każdy plik musi mieć ten sam blob git co wpis
w P12-przygotowanie/wyniki/kontrakty.json (raport kontraktów 5.10: 0 błędów, 56 sieci OK, 0 czeka). Dla każdego złącza krawędzi A
(P02, P03, P05, P09, P06, P10, P08, P07, P04) i dla J_P12 płyty P11 zapisuje pin -> sieć (GND jawnie), położenie środka złącza na P12
i typ IDC.

Geometria (README, „Geometria”): P12 stoi pionowo przed krawędzią A, stroną złączy do stosu. Układ płytki P12: x = x stosu
(0 = strona panelu), z = wysokość nad dnem obudowy. Środek złącza: x = x_stos (zlacza-P12.csv), z = z_spodu_plytki + 1,6 +
H_OSI, gdzie H_OSI = 4,45 mm to oś rzędów kątowego IDC nad płytką (korpus 8,9 mm, rzędy symetrycznie w korpusie; tolerancję
pokrywa taśma).

Sieci: łączone WYŁĄCZNIE po nazwie sieci, nigdy pin w pin. W R2 wszystkie płytki są obecne: każda sieć poza GND ma co najmniej
dwa końce i jest łączona; sieć z jednym końcem albo w stanie innym niż OK to błąd (R1 zostawiał piny P04 / P07 / P08 wolne).
Wynik: docs/kontrakt-P12.json, docs/GEOMETRIA.csv, docs/NIEPODLACZONE.csv (w R2 pusta: tylko nagłówek). Kod 1 przy niezgodności.
"""
import csv, io, json, subprocess, sys
from pathlib import Path

P = Path(__file__).resolve().parents[1]; REPO = P.parents[1]
PRZ = REPO / 'Plytki/P12-przygotowanie'
CFG = json.loads((PRZ / 'zrodla.json').read_text(encoding='utf-8'))
KON = json.loads((PRZ / 'wyniki/kontrakty.json').read_text(encoding='utf-8'))
H_OSI = 4.45          # oś kątowego IDC nad górną powierzchnią płytki stosu (korpus 8,9 mm / 2)
GRUBOSC = CFG['grubosc_plytki_mm']
# kolejność i oznaczenia złączy na P12 (ref P12, płytka, złącze płytki)
ZLACZA = [('J1', 'P02 R4', 'J_BP'), ('J2', 'P03 R6', 'J_BP1'), ('J3', 'P03 R6', 'J_BP2'), ('J4', 'P03 R6', 'J_BP3'),
          ('J5', 'P05 R3', 'J_BP1'), ('J6', 'P05 R3', 'J_BP2'), ('J7', 'P09 R2', 'J1'), ('J8', 'P06 R2', 'J_BP'),
          ('J9', 'P10 R2', 'J1'), ('J10', 'P11 R2', 'J_P12'),
          # R2 (wariant pełny): poziom 5 (P08 S1, P07 S2/S3) i poziom 6 (P04 S1..S3); J1..J10 bez zmian wobec R1
          ('J11', 'P08 R2', 'J_BP'), ('J12', 'P07 S1', 'J_BP1'), ('J13', 'P07 S1', 'J_BP2'),
          ('J14', 'P04 R3', 'J_BP1'), ('J15', 'P04 R3', 'J_BP2'), ('J16', 'P04 R3', 'J_BP3')]
# J_P12 (P11 leży poziomo na dnie strefy panelu, x < 0): przy lewej krawędzi P12, nisko, w miejscu slotu S1 poziomu 1
# (P02 ma tam pustą krawędź; jedyne złącze poziomu 1 jest w S3). Piny 10 i 13-16 stoją wtedy pod tymi samymi pinami P03 J_BP1.
P11_X, P11_Z = 26.5, round(CFG['dno_mm'] + GRUBOSC + H_OSI, 2)
WARIANT_PELNY = ('P04', 'P07', 'P08')   # R2: wszystkie obecne, NIEPODLACZONE ma być puste


def git(*a):
    return subprocess.run(['git', '-C', str(REPO), *a], capture_output=True, text=True).stdout.strip()


def z_galezi(z):
    """Plik z innej gałęzi (ref origin/...) czytany przez git show; ref 'main' = drzewo robocze (pliki tej gałęzi, jak w R1)."""
    return z['ref'].startswith('origin/')


def blob(z):
    if z_galezi(z):
        return git('rev-parse', f"{z['ref']}:{z['plik']}")
    return git('hash-object', str(REPO / z['plik']))


def tekst_(z):
    if z_galezi(z):
        r = subprocess.run(['git', '-C', str(REPO), 'show', f"{z['ref']}:{z['plik']}"], capture_output=True)
        if r.returncode:
            raise SystemExit(f"brak {z['ref']}:{z['plik']} (git fetch origin?)")
        return r.stdout.decode('utf-8-sig')
    return (REPO / z['plik']).read_text(encoding='utf-8-sig')


def wczytaj(pl):
    z = pl['zrodlo']; tekst = tekst_(z); piny = []
    if z['typ'] == 'csv':
        for r in csv.DictReader(io.StringIO(tekst), delimiter=';'):
            piny.append({'zlacze': r.get('zlacze') or z['zlacze'], 'pin': int(r['pin']), 'siec': r['siec'].strip(),
                         'kierunek': (r.get('kierunek') or '').strip(), 'cel': (r.get('plytka_docelowa') or '').strip()})
    elif z['typ'] == 'parts':
        parts = json.loads(tekst)
        for zl in pl['zlacza']:
            for n, net in parts[zl]['pins'].items():
                net = net.split('/')[-1]
                piny.append({'zlacze': zl, 'pin': int(n), 'siec': net, 'kierunek': 'gnd' if net == 'GND' else pl['kierunki'].get(net, '?'),
                             'cel': 'wszystkie' if net == 'GND' else pl['cele'].get(net, '')})
    else:
        raise SystemExit(f"{pl['plytka']}: nieznany typ źródła {z['typ']}")
    return piny


def main():
    bledy = []; plytki = {pl['plytka']: pl for pl in CFG['plytki'] if pl.get('zrodlo')}
    zl_kon = {(z['plytka'], z['zlacze']): z for z in KON['zlacza']}
    zrodla = {}; dane = {}
    for nazwa, pl in plytki.items():
        rel = pl['zrodlo']['plik']; b = blob(pl['zrodlo']); wpis = KON['zrodla'].get(nazwa, '')
        zgodny = bool(b) and f'blob {b[:10]}' in wpis
        if not zgodny:
            bledy.append(f'{nazwa}: plik {rel} (blob {b[:10]}) inny niż w kontrakty.json ({wpis})')
        zrodla[nazwa] = {'plik': rel, 'ref': pl['zrodlo']['ref'] if z_galezi(pl['zrodlo']) else 'drzewo robocze', 'blob': b, 'kontrakty_json': wpis, 'zgodny': zgodny}
        for q in wczytaj(pl):
            dane.setdefault((nazwa, q['zlacze']), []).append(q)
    zlacza = []
    for ref, pl, zl in ZLACZA:
        piny = sorted(dane[(pl, zl)], key=lambda q: q['pin']); n = len(piny)
        if [q['pin'] for q in piny] != list(range(1, n + 1)) or n not in (10, 16, 20):
            bledy.append(f'{pl} {zl}: numeracja pinów {[q["pin"] for q in piny]}')
        k = zl_kon[(pl, zl)]
        if k['typ'] != f'IDC 2×{n // 2}':
            bledy.append(f'{pl} {zl}: {n} pinów, typ w kontrakty.json {k["typ"]}')
        if pl.startswith('P11'):
            x, zs, zo = P11_X, None, P11_Z
        else:
            x, zs = k['x_stos_mm'], k['z_spodu_plytki_mm']; zo = round(zs + GRUBOSC + H_OSI, 2)
        zlacza.append({'ref': ref, 'plytka': pl, 'zlacze': zl, 'typ': k['typ'], 'n': n, 'poziom': k['poziom'], 'slot': k['slot'],
                       'x_mm': x, 'z_spodu_plytki_mm': zs, 'z_osi_mm': zo,
                       'footprint': f'Connector_IDC:IDC-Header_2x{n // 2:02d}_P2.54mm_Vertical',
                       'piny': {str(q['pin']): q['siec'] for q in piny},
                       'kierunki': {str(q['pin']): q['kierunek'] for q in piny}, 'cele': {str(q['pin']): q['cel'] for q in piny}})
    # sieci P12: nazwa -> lista 'Jx.n'
    sieci = {}
    for z in zlacza:
        for n, s in z['piny'].items():
            sieci.setdefault(s, []).append(f"{z['ref']}.{n}")
    # zgodność z kontrakty.json: końce każdej sieci (bez GND) = końce w raporcie kontraktów
    ref_of = {(z['plytka'], z['zlacze']): z['ref'] for z in zlacza}
    for s, v in KON['sieci'].items():
        want = set()
        for e in v['konce']:   # 'P03 R6 J_BP2.4 IN'
            plyt, rest = ' '.join(e.split()[:2]), e.split()[2]; zl, pin = rest.split('.')
            want.add(f'{ref_of[(plyt, zl)]}.{pin}')
        got = set(sieci.get(s, []))
        if got != want:
            bledy.append(f'sieć {s}: P12 {sorted(got)}, kontrakty.json {sorted(want)}')
    extra = sorted(set(sieci) - set(KON['sieci']) - {'GND'})
    if extra:
        bledy.append(f'sieci spoza kontrakty.json: {extra}')
    niepodl = []
    for s, konce in sorted(sieci.items()):
        if s != 'GND' and len(konce) < 2:   # R2: każda sieć ma oba końce (wszystkie płytki wariantu pełnego obecne)
            v = KON['sieci'][s]
            bledy.append(f'sieć {s}: jeden koniec ({konce[0]}), stan {v["stan"]} / czeka na {v["czeka_na"]} — w R2 niedopuszczalne')
            niepodl.append({'siec': s, 'pin': konce[0], 'czeka_na': v['czeka_na']})
    nie_ok = sorted(s for s, v in KON['sieci'].items() if v['stan'] != 'OK')
    if nie_ok:
        bledy.append(f'kontrakty.json: sieci w stanie innym niż OK: {nie_ok}')
    laczone_czeka = sorted(s for s, k in sieci.items() if s != 'GND' and len(k) >= 2 and KON['sieci'][s]['stan'] == 'czeka')
    ok = sorted(s for s, v in KON['sieci'].items() if v['stan'] == 'OK')
    wynik = {'opis': 'Kontrakt pinowy P12 R2 (wariant pełny); generowany przez src/kontrakt.py — nie edytować ręcznie.',
             'h_osi_mm': H_OSI, 'grubosc_plytki_mm': GRUBOSC, 'zrodla': zrodla, 'zlacza': zlacza, 'sieci': sieci,
             'sieci_OK_w_kontraktach': ok, 'laczone_mimo_czeka': laczone_czeka, 'niepodlaczone': niepodl,
             'kontrakty_json': {'bledy': KON['bledy'], 'uwagi': KON['uwagi']}, 'bledy': bledy}
    (P / 'docs').mkdir(exist_ok=True)
    (P / 'docs/kontrakt-P12.json').write_text(json.dumps(wynik, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    with (P / 'docs/GEOMETRIA.csv').open('w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f, delimiter=';')
        w.writerow(['ref_P12', 'plytka', 'zlacze', 'typ', 'poziom', 'slot', 'x_mm', 'z_spodu_plytki_mm', 'z_osi_mm', 'footprint'])
        for z in zlacza:
            w.writerow([z['ref'], z['plytka'], z['zlacze'], z['typ'], z['poziom'], z['slot'], z['x_mm'], z['z_spodu_plytki_mm'] if z['z_spodu_plytki_mm'] is not None else '',
                        z['z_osi_mm'], z['footprint']])
    with (P / 'docs/NIEPODLACZONE.csv').open('w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f, delimiter=';'); w.writerow(['siec', 'pin_P12', 'zlacze_plytki', 'czeka_na'])
        nz = {z['ref']: f"{z['plytka']} {z['zlacze']}" for z in zlacza}
        for q in niepodl:
            r, n = q['pin'].split('.'); w.writerow([q['siec'], q['pin'], f'{nz[r]}.{n}', ', '.join(q['czeka_na'])])
    print(f"kontrakt P12: {len(zlacza)} złączy, {sum(z['n'] for z in zlacza)} pinów, {len(sieci)} sieci "
          f"(łączone {sum(1 for s, k in sieci.items() if len(k) > 1)}, niepodłączone {len(niepodl)}, łączone mimo „czeka”: {laczone_czeka}); błędy: {len(bledy)}")
    for e in bledy:
        print('  BŁĄD', e)
    return 1 if bledy else 0


if __name__ == '__main__':
    sys.exit(main())
