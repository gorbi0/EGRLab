"""Zbiorcza mapa kontraktów krawędzi A (J_BP, format S1) — przygotowanie płytki połączeń P12 (1.10.2026; 5.10: wariant pełny).

Czyta pinouty płytek (docs/J_BP.csv, parts.json albo plan z zadania) z gałęzi git podanych w zrodla.json, położenia złączy
z raportów PCB (verification/pcb-checks.json) i sprawdza:
- złącza: wielkość IDC, piny nieparzyste = GND (wyjątki z uwagami), położenie środka w slocie (S1 §5) i na stosie;
- sieci: drugi koniec na płytce wskazanej w kolumnie plytka_docelowa (brak na płytce, która już ma pinout = BŁĄD,
  brak na płytce bez pinoutu = czeka), jeden nadajnik na sieć (wyjątki: magistrale i pętle z zrodla.json), cele w obie strony,
  zbliżone nazwy (np. DAQ_OK / DAQOK);
- zasilanie: piny 5V_SYS / 3V3_IO na płytkach, prądy z dokumentów płytek wobec styków IDC i zasilacza P02 R4;
- opisy położeń w specyfikacji S1 wobec zmierzonych płytek.
Wynik: wyniki/KONTRAKTY.md, wyniki/kontrakty.json, wyniki/zlacza-P12.csv.
Uruchomienie (z dowolnego katalogu; potrzebny git z gałęziami z zrodla.json, najpierw `git fetch origin`):
  python3 Plytki/P12-przygotowanie/src/kontrakty.py [konfiguracja.json] [katalog_wynikow]
Wychodzi z kodem 1, gdy jest choć jeden BŁĄD.
"""
import csv, io, json, re, subprocess, sys
from pathlib import Path

P = Path(__file__).resolve().parents[1]; REPO = P.parents[1]
CFG = json.loads(Path(sys.argv[1] if len(sys.argv) > 1 else P / 'zrodla.json').read_text(encoding='utf-8'))   # inna konfiguracja: próby ujemne
SLOTY = CFG['sloty']; STEP = CFG['rozstaw_slotow_mm']; X0 = CFG['srodek_x_w_slocie_mm']; IMAX = CFG['prad_na_styk_A']
MAGISTRALE = CFG['magistrale']; ZASILANIE = ('5V_SYS', '3V3_IO')


def git(*a):
    return subprocess.run(['git', '-C', str(REPO), *a], capture_output=True)


def show(ref, path):
    r = git('show', f'{ref}:{path}')
    if r.returncode:
        raise SystemExit(f'Brak {ref}:{path} — {r.stderr.decode().strip()} (git fetch origin?)')
    return r.stdout


def wersja(ref, path):
    c = git('rev-parse', '--short=7', ref).stdout.decode().strip()
    b = git('rev-parse', '--short=10', f'{ref}:{path}').stdout.decode().strip()
    return f'{ref} @ {c}, blob {b}'


def baza(nazwa):                       # 'P03 R6' -> 'P03'
    return nazwa.split()[0]


def plytki_w(tekst):                   # 'P05, P06, P07' -> {'P05', 'P06', 'P07'}; 'wszystkie (P12)' -> {'*'}
    s = set(re.findall(r'P\d\d', tekst or '')) - {'P12'}
    if not s and re.search(r'wszystk|P12', tekst or '', re.I):
        return {'*'}
    return s


def kier(s):
    s = (s or '').strip().lower()
    for k, pref in (('GND', ('gnd', 'masa')), ('ZRODLO', ('zrodlo', 'źródło')), ('PWR', ('pwr', 'zasil')), ('PETLA', ('petla', 'pętla')),
                    ('OUT', ('out', 'wyj')), ('IN', ('in', 'wej'))):
        if s.startswith(pref):
            return k
    return '?'


def wczytaj(pl):
    z = pl.get('zrodlo') or {}; typ = z.get('typ'); piny = []
    if typ == 'csv':
        for r in csv.DictReader(io.StringIO(show(z['ref'], z['plik']).decode('utf-8-sig')), delimiter=';'):
            piny.append({'zlacze': r.get('zlacze') or z['zlacze'], 'pin': int(r['pin']), 'siec': r['siec'].strip(), 'kier': kier(r.get('kierunek')),
                         'cele': plytki_w(r.get('plytka_docelowa')), 'uwagi': (r.get('uwagi') or '').strip()})
    elif typ == 'parts':
        parts = json.loads(show(z['ref'], z['plik']))
        for zl in pl['zlacza']:
            for n, net in sorted(parts[zl]['pins'].items(), key=lambda q: int(q[0])):
                net = net.split('/')[-1]
                piny.append({'zlacze': zl, 'pin': int(n), 'siec': net, 'kier': 'GND' if net == 'GND' else kier(pl['kierunki'].get(net)),
                             'cele': {'*'} if net == 'GND' else plytki_w(pl['cele'].get(net)), 'uwagi': ''})
    elif typ == 'plan':
        for zl, rows in z['piny'].items():
            for n, (net, k, cel) in rows.items():
                piny.append({'zlacze': zl, 'pin': int(n), 'siec': net, 'kier': kier(k), 'cele': plytki_w(cel), 'uwagi': 'plan z zadania'})
    return piny


def zmierzone(pl):
    """Środki złączy w układzie płytki z raportu PCB (verify_pcb.py każdej płytki): {złącze: x_mm}."""
    z = pl.get('zrodlo') or {}
    if not z.get('pcb_checks'):
        return {}
    out = {}
    for k, v in json.loads(show(z['ref'], z['pcb_checks']))['details'].items():
        if not isinstance(v, dict):
            continue
        if 'centre_x' in v and (k.startswith('J_BP') or k.startswith('J1 = J_BP')):
            out[next(iter(pl['zlacza']))] = v['centre_x']
        elif k.startswith('J_BP'):
            out.update({zl: q['centre_x'] for zl, q in v.items() if isinstance(q, dict) and 'centre_x' in q})
    return out


def pl_(v):
    return '—' if v is None else (f'{v:g}' if isinstance(v, (int, float)) else str(v)).replace('.', ',')


def piny_(n):
    return f'{n} pin' if n == 1 else f'{n} piny' if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14 else f'{n} pinów'


def z_poziomu(poziom):
    z = CFG['dno_mm']
    for k in range(1, int(poziom)):
        z += CFG['grubosc_plytki_mm'] + CFG['dystans_nad_poziomem_mm'][str(k)]
    return round(z, 1)


plytki = CFG['plytki']; dane = {}; bledy = []; uwagi = []; zlacza = []
for pl in plytki:
    piny = wczytaj(pl); pl['_piny'] = piny
    plan = (pl.get('zrodlo') or {}).get('plan_piny')   # 1.10: schemat z chmury (csv) wobec tabel z zadania
    if plan and piny:
        jest = {(p['zlacze'], p['pin']): p['siec'] for p in piny}; chce = {(zl, int(n)): v[0] for zl, rows in plan.items() for n, v in rows.items()}
        for k in sorted(set(jest) | set(chce)):
            if jest.get(k) != chce.get(k):
                bledy.append(f"{pl['plytka']} {k[0]}.{k[1]}: schemat {jest.get(k)}, plan z zadania {chce.get(k)}")
    if not piny:
        continue
    dane[baza(pl['plytka'])] = pl
    pl['_wersja'] = wersja(pl['zrodlo']['ref'], pl['zrodlo']['plik']); pl['_zmierzone'] = zmierzone(pl)
    if not pl.get('sloty'):    # 4.10: P11 (panel) — poza stosem, złącze bez slotu; położenie na P12 ustala projekt P12
        for zl in pl['zlacza']:
            n = sum(1 for q in piny if q['zlacze'] == zl)
            zlacza.append({'poziom': pl['poziom'], 'slot': '—', 'x_stos_mm': None, 'z_spodu_plytki_mm': None, 'plytka': pl['plytka'], 'zlacze': zl,
                           'typ': f'IDC 2×{n // 2}', 'x_lokalnie_mm': None, 'zmierzone_x_mm': None, 'stan': pl['stan'], 'nieparzyste_nie_GND': []})
        continue
    pierwszy = SLOTY.index(pl['sloty'][0])
    for zl, slot in pl['zlacza'].items():
        p_ = sorted((q for q in piny if q['zlacze'] == zl), key=lambda q: q['pin'])
        n = len(p_); nr = [q['pin'] for q in p_]
        if nr != list(range(1, n + 1)) or n not in (10, 16, 20):
            bledy.append(f"{pl['plytka']} {zl}: piny {nr[:3]}…{nr[-2:]} — nie IDC 2×5/2×8/2×10 albo dziury w numeracji")
        wyj = [f"{q['pin']} {q['siec']}" + (f" ({q['uwagi']})" if q['uwagi'] else '') for q in p_ if q['pin'] % 2 and q['siec'] != 'GND']
        k = SLOTY.index(slot); x_lok = X0 + STEP * (k - pierwszy); x_stos = X0 + STEP * k; zm = pl['_zmierzone'].get(zl)
        if zm is not None and abs(zm - x_lok) > .05:
            bledy.append(f"{pl['plytka']} {zl}: środek zmierzony x = {zm} mm, slot {slot} wymaga {x_lok} mm (S1 §5)")
        zlacza.append({'poziom': pl['poziom'], 'slot': slot, 'x_stos_mm': x_stos, 'z_spodu_plytki_mm': z_poziomu(pl['poziom']), 'plytka': pl['plytka'],
                       'zlacze': zl, 'typ': f'IDC 2×{n // 2}', 'x_lokalnie_mm': x_lok, 'zmierzone_x_mm': zm, 'stan': pl['stan'],
                       'nieparzyste_nie_GND': wyj})
for pl in plytki:          # złącza płytek bez pinoutu, ale z miejscem w stosie (P12 musi je przewidzieć)
    if not pl['_piny'] and isinstance(pl.get('poziom'), int) and pl.get('sloty'):
        zlacza.append({'poziom': pl['poziom'], 'slot': '/'.join(pl['sloty']), 'x_stos_mm': None, 'z_spodu_plytki_mm': z_poziomu(pl['poziom']),
                       'plytka': pl['plytka'], 'zlacze': '?', 'typ': '?', 'x_lokalnie_mm': None, 'zmierzone_x_mm': None, 'stan': pl['stan'],
                       'nieparzyste_nie_GND': []})

# ---- sieci ----
sieci = {}
for b, pl in dane.items():
    for q in pl['_piny']:
        if q['siec'] != 'GND':
            sieci.setdefault(q['siec'], []).append(dict(q, plytka=pl['plytka'], baza=b))
oczekujace = {baza(pl['plytka']): pl['stan'] for pl in plytki if not pl['_piny']}
wynik_sieci = {}
for s, ep in sorted(sieci.items()):
    na = {e['baza'] for e in ep}; cele = set().union(*(e['cele'] for e in ep)) - {'*'} - na
    brak_jest = sorted(c for c in cele if c in dane); brak_czeka = sorted(c for c in cele if c not in dane)
    nad = [e for e in ep if e['kier'] in ('OUT', 'ZRODLO')]; petla = any(e['kier'] == 'PETLA' for e in ep)
    problemy = []; stan = 'OK'
    for c in brak_jest:
        problemy.append(f'brak na {c}, choć {c} ma już pinout'); stan = 'BŁĄD'
    nad_pl = sorted({e['plytka'] for e in nad})   # kilka pinów jednej płytki (np. 5V_SYS na trzech) to jeden nadajnik
    if len(nad_pl) > 1 and s not in MAGISTRALE:
        problemy.append('więcej niż jeden nadajnik: ' + ', '.join(nad_pl)); stan = 'BŁĄD'
    if not nad and not petla and not brak_czeka and len(na) > 1:
        problemy.append('brak nadajnika (same wejścia)'); stan = 'BŁĄD'
    for e in ep:            # cele w obie strony
        for c in e['cele'] - {'*'}:
            if c in dane and c in na:
                drugi = [f for f in ep if f['baza'] == c]
                if drugi and not any(e['baza'] in f['cele'] or '*' in f['cele'] for f in drugi):
                    problemy.append(f"{c} nie wskazuje {e['baza']} jako drugiej strony"); stan = 'BŁĄD' if stan == 'BŁĄD' else 'UWAGA'
    if stan != 'BŁĄD' and brak_czeka:
        stan = 'czeka'
    if len(na) == 1 and not cele:
        problemy.append('jeden koniec i brak celu'); stan = 'BŁĄD'
    wynik_sieci[s] = {'stan': stan, 'konce': [f"{e['plytka']} {e['zlacze']}.{e['pin']} {e['kier']}" for e in ep], 'czeka_na': brak_czeka,
                      'problemy': problemy, 'magistrala': MAGISTRALE.get(s)}
    if stan == 'BŁĄD':
        bledy += [f'{s}: {x}' for x in problemy]
    elif stan == 'UWAGA':
        uwagi += [f'{s}: {x}' for x in problemy]
grupy = {}
for s in sieci:
    grupy.setdefault(re.sub(r'[^A-Z0-9]', '', s.upper()), set()).add(s)
for g, ns in grupy.items():
    if len(ns) > 1:
        uwagi.append('zbliżone nazwy sieci: ' + ', '.join(sorted(ns)))

# ---- zasilanie ----
zas = {}
for s in ZASILANIE:
    rows = []
    for b, pl in dane.items():
        n = sum(1 for q in pl['_piny'] if q['siec'] == s)
        if n:
            src = any(q['kier'] == 'ZRODLO' for q in pl['_piny'] if q['siec'] == s)
            rows.append({'plytka': pl['plytka'], 'piny': n, 'zrodlo': src, 'max_A': n * IMAX})
    zas[s] = rows
logger = [pl for pl in plytki if pl.get('wariant') == 'LOGGER' and pl.get('prad_5V_mA')]
suma = sum(pl['prad_5V_mA'] for pl in logger)
src5 = next((r for r in zas['5V_SYS'] if r['zrodlo']), None)
for pl in logger:
    n = sum(1 for q in pl['_piny'] if q['siec'] == '5V_SYS')
    if pl['_piny'] and n * IMAX * 1000 < pl['prad_5V_mA']:
        bledy.append(f"{pl['plytka']}: {pl['prad_5V_mA']} mA z 5V_SYS na {n} pinach (≤ {IMAX} A/styk)")
if src5 and suma > src5['max_A'] * 1000:
    bledy.append(f'suma budżetów 5V_SYS {suma} mA > styki źródła {src5["max_A"]} A')
# 5.10: wariant pełny (P04 R3, P07 S1, P08 R2) — budżet całego stosu wobec styków źródła i przetwornicy 2 A (rezerwa 10 %: 1,8 A)
pelny = [pl for pl in plytki if pl.get('wariant') == 'pełny' and 'prad_5V_mA' in pl]
suma_pelny = suma + sum(pl['prad_5V_mA'] for pl in pelny); LIMIT_5V_mA = CFG.get('limit_5V_mA', 1800)
for pl in pelny:
    n = sum(1 for q in pl['_piny'] if q['siec'] == '5V_SYS')
    if pl['_piny'] and n * IMAX * 1000 < pl['prad_5V_mA']:
        bledy.append(f"{pl['plytka']}: {pl['prad_5V_mA']} mA z 5V_SYS na {n} pinach (≤ {IMAX} A/styk)")
if pelny and src5 and suma_pelny > src5['max_A'] * 1000:
    bledy.append(f'suma budżetów 5V_SYS wariantu pełnego {suma_pelny} mA > styki źródła {src5["max_A"]} A')
if pelny and suma_pelny > LIMIT_5V_mA:
    uwagi.append(f'ryzyko: suma budżetów 5V_SYS wariantu pełnego {suma_pelny} mA > {LIMIT_5V_mA} mA (90 % przetwornicy 2 A)')

# ---- pojemność na szynach 5 V (obciążenie pojemnościowe TSR 2-2450) ----
def farad(v):                          # '4u7' -> 4.7e-6, '22u / 16V' -> 22e-6, '100nF / X7R' -> 1e-7
    m = re.match(r'\s*(\d+(?:[.,]\d+)?)\s*([pnuµm])(\d*)', v or '')
    if not m:
        return None
    x = float(m.group(1).replace(',', '.') + ('.' + m.group(3) if m.group(3) and '.' not in m.group(1) else ''))
    return x * {'p': 1e-12, 'n': 1e-9, 'u': 1e-6, 'µ': 1e-6, 'm': 1e-3}[m.group(2)]


poj = CFG.get('pojemnosc_5V'); pojemnosc = []
if poj:
    for z in poj['plytki']:
        parts = json.loads(show(z['ref'], z['plik'])); rows = []
        for r, q in parts.items():
            nets = [n.split('/')[-1] for n in q.get('pins', {}).values()]
            if r.startswith('C') and q.get('on_board', True) and 'GND' in nets and any(n in poj['sieci'] for n in nets):
                c = farad(z.get('zamiany', {}).get(r, q.get('value')))   # 1.10: wartość według decyzji przed rewizją płytki (np. P06 C3)
                rows.append({'ref': r, 'wartosc': z.get('zamiany', {}).get(r, q.get('value')), 'siec': next(n for n in nets if n in poj['sieci']), 'uF': round(c * 1e6, 3) if c else None})
        pojemnosc.append({'plytka': z['plytka'], 'wersja': wersja(z['ref'], z['plik']), 'uF': round(sum(x['uF'] or 0 for x in rows), 1),
                          'najwieksze': sorted(rows, key=lambda x: -(x['uF'] or 0))[:3], 'bez_wartosci': [x['ref'] for x in rows if x['uF'] is None]})
    suma_uF = round(sum(x['uF'] for x in pojemnosc), 1)
    if suma_uF > poj['limit_uF']:
        bledy.append(f"pojemność na szynach 5 V razem {suma_uF} µF > {poj['limit_uF']} µF dopuszczalnych dla TSR 2-2450 (" +
                     ', '.join(f"{x['plytka']} {x['uF']} µF" for x in pojemnosc) + ')')

# ---- opisy w specyfikacji ----
opisy = []
for o in CFG.get('opisy_w_specyfikacji', []):
    tekst = (REPO / o['plik']).read_text(encoding='utf-8'); m = re.search(o['wzor'], tekst)
    pl = next(p_ for p_ in plytki if p_['plytka'] == o['plytka']); zm = pl.get('_zmierzone', {}).get(o['zlacze'])
    if not m:
        opisy.append({'plik': o['plik'], 'stan': 'nie znaleziono wzorca'}); continue
    slot, x = m.group(1), float(m.group(2).replace(',', '.')); x_slotu = X0 + STEP * SLOTY.index(slot)
    ok = abs(x - x_slotu) < .05 and (zm is None or abs(zm - x) < .05) and pl['zlacza'].get(o['zlacze']) == slot
    opisy.append({'plik': o['plik'], 'opis': m.group(0), 'slot_w_opisie': slot, 'x_w_opisie': x, 'x_slotu': x_slotu, 'zmierzone_x': zm, 'stan': 'OK' if ok else 'BŁĄD'})
    if not ok:
        bledy.append(f"{o['plik']}: „{m.group(0)}” — slot {slot} ma środek {x_slotu} mm, płytka zmierzona {zm} mm")

# ---- wyniki ----
W = Path(sys.argv[2]) if len(sys.argv) > 2 else P / 'wyniki'; W.mkdir(parents=True, exist_ok=True)
with open(W / 'zlacza-P12.csv', 'w', encoding='utf-8', newline='') as fh:
    w = csv.writer(fh, delimiter=';')
    w.writerow(['poziom', 'slot', 'x_stos_mm', 'z_spodu_plytki_mm', 'plytka', 'zlacze', 'typ', 'zmierzone_x_lokalnie_mm', 'stan'])
    for z in sorted(zlacza, key=lambda z: (str(z['poziom']), z['slot'])):
        w.writerow([z['poziom'], z['slot'], z['x_stos_mm'], z['z_spodu_plytki_mm'], z['plytka'], z['zlacze'], z['typ'], z['zmierzone_x_mm'], z['stan']])
res = {'zrodla': {pl['plytka']: pl.get('_wersja') for pl in plytki if pl['_piny']}, 'zlacza': zlacza, 'sieci': wynik_sieci, 'zasilanie': zas,
       'budzet_5V_mA': {pl['plytka']: pl['prad_5V_mA'] for pl in logger + pelny}, 'suma_5V_mA': suma, 'suma_5V_pelny_mA': suma_pelny,
       'budzet_3V3_mA': {pl['plytka']: pl['prad_3V3_mA'] for pl in plytki if 'prad_3V3_mA' in pl}, 'pojemnosc_5V': pojemnosc, 'opisy_w_specyfikacji': opisy, 'bledy': bledy, 'uwagi': uwagi}
(W / 'kontrakty.json').write_text(json.dumps(res, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')

L = ['# Kontrakty krawędzi A (J_BP) — mapa dla P12', '', '*Plik generowany przez `src/kontrakty.py` z `zrodla.json`; nie edytować ręcznie.*', '',
     f"**Wynik:** {len(bledy)} błędów, {len(uwagi)} uwag; sieci: " + ', '.join(f"{k} {sum(1 for v in wynik_sieci.values() if v['stan'] == k)}"
                                                                      for k in ('OK', 'czeka', 'UWAGA', 'BŁĄD')) + '.', '']
if bledy:
    L += ['## Błędy', ''] + [f'- {b}' for b in bledy] + ['']
if uwagi:
    L += ['## Uwagi', ''] + [f'- {u}' for u in uwagi] + ['']
L += ['## Źródła', '', '| Płytka | Stan | Pinout |', '|---|---|---|']
L += [f"| {pl['plytka']} | {pl['stan']} | {pl.get('_wersja') or '—'} |" for pl in plytki]
L += ['', '## Złącza na krawędzi A (miejsca dla P12)', '',
      'x — środek złącza w układzie stosu (x = 0 od strony panelu); z — spód płytki nad dnem obudowy (dno 8 mm, płytki 1,6 mm, dystanse z S1 §7).', '',
      '| Poziom | Slot | x stosu [mm] | z spodu [mm] | Płytka | Złącze | Typ | x zmierzone w układzie płytki [mm] | Piny nieparzyste ≠ GND |', '|---|---|---|---|---|---|---|---|---|']
for z in sorted(zlacza, key=lambda z: (str(z['poziom']), z['slot'])):
    L.append(f"| {z['poziom']} | {z['slot']} | {pl_(z['x_stos_mm'])} | {pl_(z['z_spodu_plytki_mm'])} | {z['plytka']} | {z['zlacze']} | {z['typ']} | "
             f"{pl_(z['zmierzone_x_mm'])} | {'; '.join(z['nieparzyste_nie_GND']) or '—'} |")
L += ['', '## Sieci (bez GND)', '', '| Sieć | Stan | Końce | Czeka na | Uwagi |', '|---|---|---|---|---|']
kol = {'BŁĄD': 0, 'UWAGA': 1, 'czeka': 2, 'OK': 3}
for s, v in sorted(wynik_sieci.items(), key=lambda q: (kol[q[1]['stan']], q[0])):
    L.append(f"| {s} | {v['stan']} | {'; '.join(v['konce'])} | {', '.join(v['czeka_na']) or '—'} | {'; '.join(v['problemy'] + ([v['magistrala']] if v['magistrala'] else [])) or '—'} |")
L += ['', '## Zasilanie przez P12', '', f'Styki IDC: ok. {pl_(IMAX)} A na styk (S1 §5).', '']
for s, rows in zas.items():
    L.append(f"- **{s}:** " + '; '.join(f"{r['plytka']} {piny_(r['piny'])}{' (źródło)' if r['zrodlo'] else ''}, styki do {pl_(r['max_A'])} A" for r in rows))
pl02 = next(pl for pl in plytki if baza(pl['plytka']) == 'P02')
L += ['', f"Budżety 5V_SYS z dokumentów płytek (LOGGER): " + ', '.join(f"{pl['plytka']} {pl['prad_5V_mA']} mA" for pl in logger)
      + f" — **razem {suma} mA**. Źródło: {pl02['zasilacz']['5V_SYS']}; styki J_BP P02 R4: {pl_(src5['max_A'])} A. Budżetów 3V3_IO płytki nie podają." if src5 else '', '']
L += [f"- {pl['plytka']}: {pl['prad_zrodlo']}" for pl in logger] + ['']
if pelny:
    L += [f"**Wariant pełny** dodatkowo: " + ', '.join(f"{pl['plytka']} {pl['prad_5V_mA']} mA" for pl in pelny) + f" — **razem cały stos {suma_pelny} mA** "
          f"wobec {LIMIT_5V_mA} mA (90 % przetwornicy 2 A){' — RYZYKO' if suma_pelny > LIMIT_5V_mA else ''}. 3V3_IO (płytki, które podają budżet): "
          + ', '.join(f"{pl['plytka']} {pl['prad_3V3_mA']} mA" for pl in plytki if 'prad_3V3_mA' in pl) + '.', '']
    L += [f"- {pl['plytka']}: {pl['prad_zrodlo']}" for pl in pelny] + ['']
if pojemnosc:
    L += ['## Pojemność na szynach 5 V', '', f"Sieci: " + ', '.join(f'{k} ({v})' for k, v in poj['sieci'].items()) + f". Limit: {poj['limit_uF']} µF ({poj['limit_zrodlo']}).", '',
          '| Płytka | µF | Największe | Źródło |', '|---|---|---|---|']
    for x in pojemnosc:
        duze = ', '.join('{} {} ({})'.format(y['ref'], y['wartosc'], y['siec']) for y in x['najwieksze'])
        L.append(f"| {x['plytka']} | {pl_(x['uF'])} | {duze} | {x['wersja']} |")
    L += ['', f"**Razem {pl_(round(sum(x['uF'] for x in pojemnosc), 1))} µF.**", '']
if opisy:
    L += ['## Opisy położeń w specyfikacji S1', ''] + [f"- {o.get('plik')}: „{o.get('opis', '')}” — {o['stan']}" + (f" (slot ma środek {pl_(o['x_slotu'])} mm, płytka {pl_(o['zmierzone_x'])} mm)" if o.get('x_slotu') is not None else '') for o in opisy] + ['']
(W / 'KONTRAKTY.md').write_text('\n'.join(L) + '\n', encoding='utf-8')
print(f"{len(bledy)} błędów, {len(uwagi)} uwag; " + ', '.join(f"{k} {sum(1 for v in wynik_sieci.values() if v['stan'] == k)}" for k in ('OK', 'czeka', 'UWAGA', 'BŁĄD')))
for b in bledy:
    print('BŁĄD', b)
for u in uwagi:
    print('UWAGA', u)
sys.exit(1 if bledy else 0)
