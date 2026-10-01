"""Szkic listy zakupowej 3 (1.10.2026): zapotrzebowanie płytek S1 z gotowym BOM-em (P02 R4, P03 R6, P09 R2, P10 R2)
wobec rejestru `Zamowione/zamowione.csv`, z cenami TME z listy 2 (28.09) tam, gdzie pozycja się nie zmieniła.

To nie jest zamówienie ani lista wiążąca: BOM-y P03/P09/P10 czekają na recenzję PR, P05/P06/P11 na rewizje S1,
a ceny i stany TME trzeba sprawdzić w przeglądarce (Cloudflare, `docs/pamiec-claude/tme-mouser-lookup.md`).
Pozycje grupowane po numerze części, a rezystory i kondensatory 1206 oraz posiadane THT — po wartości.
uruchomienie (z katalogu repozytorium, po `git fetch origin`): python3 Plytki/Zakupy-3-szkic/src/szkic.py
Wynik: Plytki/Zakupy-3-szkic/ZAKUPY-3-SZKIC.md i zakupy-3-szkic.csv.
"""
import csv, io, re, subprocess, sys
from collections import defaultdict
from pathlib import Path

P = Path(__file__).resolve().parents[1]; REPO = P.parents[1]
ZRODLA = [  # płytka, gałąź, plik, format
    ('P02 R4', 'origin/main', 'Plytki/P02-R4-review/docs/BOM.csv', 'bom'),
    ('P03 R6', 'origin/p03-r6-pcb', 'Plytki/P03-R6-review/docs/zakupy.csv', 'zakupy'),
    ('P09 R2', 'origin/p09-r2-pcb', 'Plytki/P09-R2-review/docs/BOM.csv', 'bom'),
    ('P10 R2', 'origin/p10-r2-pcb', 'Plytki/P10-R2-review/docs/BOM.csv', 'bom'),
]
PLYTKI = [z[0] for z in ZRODLA]
DO_WYBORU = {  # klucz -> co wybrać (S1: typ nieustalony w BOM)
    'IDC 2X10 KĄTOWE': 'typ do wyboru: kątowe obudowane IDC 2×10, złocone (TME nie prowadzi Würtha; w liście 2 były proste Amphenol T821)',
    'IDC 2X8 KĄTOWE': 'typ do wyboru: kątowe obudowane IDC 2×8, złocone',
    'IDC 2X5 KĄTOWE': 'typ do wyboru: kątowe obudowane IDC 2×5, złocone',
    'GOLDPIN 1X13 KĄTOWY': 'typ do wyboru: kątowy goldpin 1×13 (posiadany 1×40 jest prosty); można ciąć z kątowego 1×40',
    'GOLDPIN 1X9 KĄTOWY': 'typ do wyboru: kątowy goldpin 1×9 (jak wyżej)',
}


def git_show(ref, path):
    r = subprocess.run(['git', '-C', str(REPO), 'show', f'{ref}:{path}'], capture_output=True)
    if r.returncode:
        raise SystemExit(f'Brak {ref}:{path} (git fetch origin?)')
    return r.stdout.decode('utf-8-sig')


def wartosc_r(s):          # '10KL' / '10K' / '4K7' / '100R' / '1K' -> '10K', '4K7', '100R', '1K'
    s = s.upper().rstrip('L')
    return s[:-1] + 'R' if s.endswith('RR') else s


KOD_C = {'103': '10n', '104': '100n', '105': '1u', '475': '4u7', '106': '10u', '226': '22u'}


def klucz(mpn, display, fp):
    """Klucz grupy i opis. Rezystory/kondensatory 1206 i posiadane THT po wartości, reszta po numerze części."""
    m = (mpn or '').strip(); u = m.upper(); f = (fp or '').upper(); d = (display or '').strip()
    if re.match(r'RC1206FR-07', u):
        v = wartosc_r(u.split('-07')[1]); return f'R1206 {v}', f'rezystor 1206 1 % {v}'
    if u.startswith('SMD 1206') and ('W ' in u or u.endswith('W')) or (u.startswith('SMD 1206 1%')):
        v = wartosc_r(u.split()[-1]); return f'R1206 {v}', f'rezystor 1206 1 % {v}'
    if u.startswith('SMD 1206 X7R') or u.startswith('GRM31') or u.startswith('C1206C') or u.startswith('C3216'):
        if u.startswith('SMD'):
            v = u.split()[-1].replace('U', 'u').replace('N', 'n')
        else:
            kod = re.search(r'(\d{3})[KMJ]', u[4:] if u.startswith('GRM31') else u)
            v = KOD_C.get(kod.group(1), kod.group(1)) if kod else d
        return f'C1206 {v}', f'kondensator 1206 X7R {v}'
    if re.match(r'MF0207', u):
        v = re.search(r'(\d+[RK]\d*|\d+R\d*|\d+K)', u.replace('FTE52-', ' ').replace('FTE-', ' ').split(' ', 1)[1] if ' ' in u else u)
        v = wartosc_r(v.group(1)) if v else d.upper()
        return f'MF0207 {v}', f'rezystor THT MF0207 {v} (na stojąco)'
    if u.startswith('K104K15X7RF5TH5'):
        return 'K104K15X7RF5TH5', 'kondensator 100n X7R 50 V radialny 5 mm (K104)'
    if 'IDC' in u and ('2X10' in u or '2X10' in f) and ('ANGLE' in u or 'ANGLED' in u or 'HORIZONTAL' in f):
        return 'IDC 2X10 KĄTOWE', 'złącze IDC 2×10 kątowe obudowane, Au (J_BP)'
    if 'IDC' in u and '2X8' in u:
        return 'IDC 2X8 KĄTOWE', 'złącze IDC 2×8 kątowe obudowane, Au (J_BP)'
    if 'IDC' in u and '2X5' in u:
        return 'IDC 2X5 KĄTOWE', 'złącze IDC 2×5 kątowe obudowane, Au (J_BP)'
    if ('1X13' in u or '1X13' in f) and ('ANGLE' in u or 'HORIZONTAL' in f):
        return 'GOLDPIN 1X13 KĄTOWY', 'listwa goldpin 1×13 kątowa (listwa serwisowa)'
    if ('1X9' in u or '1X09' in f) and ('ANGLE' in u or 'HORIZONTAL' in f) and 'GOLDPIN' in u.replace('PIN HEADER', 'GOLDPIN'):
        return 'GOLDPIN 1X9 KĄTOWY', 'listwa goldpin 1×9 kątowa (listwa serwisowa)'
    if u.startswith('SOCKET 1X9'):
        return 'GNIAZDO 1X9 + MODUŁ', 'gniazdo 1×9 + posiadany moduł MAX31856 (gniazdo: pozycja ZL262-9SG niżej)'
    if u.startswith('ADAFRUIT 4682'):
        return 'ADAFRUIT 4682', 'Adafruit 4682 microSD (gniazdo 1×9 i dystanse — pozycje niżej)'
    if u.startswith('HEADER 1X3'):
        return 'GOLDPIN 1X3 PROSTY', 'goldpin 1×3 prosty (JP1/JP2; zworki — pozycja JUMPER-KPL)'
    k = re.sub(r'\s+', '', m.split(' (')[0].split(' or ')[0]).upper().split(',')[0]
    return k, m


def wczytaj():
    pozycje = defaultdict(lambda: {'opis': '', 'ilosc': defaultdict(int), 'oznaczenia': defaultdict(list), 'zrodlo': set()})
    for plytka, ref, plik, fmt in ZRODLA:
        tekst = git_show(ref, plik)
        for r in csv.DictReader(io.StringIO(tekst), delimiter=';'):
            if fmt == 'bom':
                if str(r.get('on_board', 'True')).lower() in ('false', '0', 'no'):
                    continue
                k, opis = klucz(r['mpn'], r.get('display'), r.get('footprint'))
                n = int(r.get('qty') or 1); oz = [r['ref']]; zr = (r.get('zrodlo') or '').strip()
            else:   # zakupy.csv P03: nazwa;ilosc_szt;oznaczenia
                k, opis = klucz(r['nazwa'], '', ''); n = int(r['ilosc_szt']); oz = [x.strip() for x in r['oznaczenia'].split(',')]; zr = ''
            p = pozycje[k]; p['opis'] = p['opis'] or opis; p['ilosc'][plytka] += n; p['oznaczenia'][plytka] += oz
            if zr:
                p['zrodlo'].add(zr)
    for plytka, sym, opis, n, oz in DODATKI:
        k, _ = klucz(sym, '', ''); p = pozycje[k]; p['opis'] = p['opis'] or f'{sym} — {opis}'; p['ilosc'][plytka] += n; p['oznaczenia'][plytka] += oz
    return pozycje


ALIAS = {'2N5551G': '2N5551TA'}   # ta sama część, inne opakowanie (BOM P02 R4 wobec rejestru)


DODATKI = [  # części ukryte w opisach BOM (gniazda, dystanse, zworki) — jak w liście 2 (Zakupy-2/src/items2.py, tme.py)
    ('P03 R6', 'ZL262-40SG', 'gniazdo żeńskie 1×40 złocone, ciąć na 1×22 (M1 na dwóch rzędach)', 2, ['M1']),
    ('P03 R6', 'ZL262-9SG', 'gniazdo żeńskie 1×9 złocone', 1, ['SD1']),
    ('P03 R6', 'TFF-M2.5X12/DR182', 'dystans poliamidowy M2,5 12 mm', 2, ['SD1']),
    ('P09 R2', 'ZL262-9SG', 'gniazdo żeńskie 1×9 złocone', 2, ['J3', 'J4']),
    ('P09 R2', 'TFF-M2.5X12/DR182', 'dystans poliamidowy M2,5 12 mm (podparcie modułów, wysokość do przymiarki)', 4, ['J3', 'J4']),
    ('P09 R2', 'JUMPER-KPL', 'zworka 2,54 (JP1/JP2; początkowo bez zwory)', 2, ['JP1', 'JP2']),
]
UWAGI = {  # pozycje z rejestru albo posiadane, których BOM nie nazywa wprost
    'GOLDPIN 1X3 PROSTY': 'z posiadanej prostej listwy 1×40 (rejestr: Kamami 1207864, przydział z adapterami)',
    'GNIAZDO 1X9 + MODUŁ': 'moduły MAX31856 posiadane; gniazda liczone w pozycji ZL262-9SG',
}
CENY_INNE = {'ADAFRUIT 4682': 'Mouser 485-4682: 13,24 zł (lista 2)'}


def rejestr():
    """Każdy wiersz rejestru pod kluczami z obu pól (symbol dostawcy i MPN producenta); dopasowanie sumuje wiersze bez dublowania."""
    wiersze_r = []; indeks = defaultdict(set)
    with open(REPO / 'Zamowione/zamowione.csv', encoding='utf-8-sig') as fh:
        for i, r in enumerate(csv.DictReader(fh, delimiter=';')):
            wiersze_r.append(r)
            for pole in (r['symbol_dostawcy'], r['mpn_producent'], r['symbol_dostawcy'].split('-', 1)[-1]):
                if pole:
                    k, _ = klucz(pole, '', '')
                    if not re.fullmatch(r'(MF0207|MF0204|PR02|R1206|C1206) ?', k):   # „MF0207 (Yageo)” bez wartości nic nie mówi
                        indeks[k].add(i)
    out = {}
    for k, ids in indeks.items():
        out[k] = {'ilosc': sum(int(wiersze_r[i]['ilosc'] or 0) for i in ids),
                  'moduly': {m.strip() for i in ids for m in wiersze_r[i]['modul'].split(',')}}
    return out


def ceny():
    sys.path.insert(0, str(REPO / 'Plytki/Zakupy-2/src'))
    from tme import TME   # (symbol, ilość, cena netto zł/szt, stan, płytki, uwaga) z 28.09
    out = {}
    for sym, _, cena, stan, _, _ in TME:
        k, _ = klucz(sym, '', ''); out.setdefault(k, (sym, cena, stan))
    return out


poz = wczytaj(); rej = rejestr(); cen = ceny()
wiersze = []
for k, p in poz.items():
    razem = sum(p['ilosc'].values()); r = rej.get(ALIAS.get(k, k)); c = cen.get(k)
    if re.match(r'(PCBTERMINATION|SOLDERED|TINNEDCOPPER)', k):
        wniosek = 'przewód lub zakończenie lutowane — poza listą części (wiązki, `docs/` płytki)'
    elif k in UWAGI:
        wniosek = UWAGI[k]
    elif 'OWNED' in k:
        wniosek = 'posiadane (opis w BOM)'
    elif k in DO_WYBORU:
        wniosek = 'kupić ' + str(razem) + ' — ' + DO_WYBORU[k]
    elif r and r['ilosc'] >= razem:
        wniosek = f"z rejestru ({r['ilosc']} szt., kupione dla: {', '.join(sorted(r['moduly']))}) — sprawdzić przydział z innymi płytkami"
    elif r:
        wniosek = f"rejestr {r['ilosc']} szt. ({', '.join(sorted(r['moduly']))}); dokupić co najmniej {razem - r['ilosc']}"
    else:
        wniosek = f'kupić {razem}'
    if p['zrodlo'] == {'rejestr'} and not r:
        wniosek += ' (BOM płytki wskazuje rejestr, w rejestrze brak dopasowania — sprawdzić)'
    wiersze.append({'klucz': k, 'opis': p['opis'], **{pl: p['ilosc'].get(pl, 0) for pl in PLYTKI}, 'razem': razem, 'wniosek': wniosek,
                    'tme_28_09': f'{c[0]}: {c[1]:.4f} zł (stan {c[2]})' if c else CENY_INNE.get(k, ''), 'oznaczenia': '; '.join(f"{pl}: {', '.join(v)}" for pl, v in p['oznaczenia'].items())})
grupa = lambda w: (0 if w['klucz'] in DO_WYBORU else 1 if w['wniosek'].startswith('kupić') else 2 if 'dokupić' in w['wniosek'] else 3 if w['wniosek'].startswith('z rejestru') else 4, w['klucz'])
wiersze.sort(key=grupa)
with open(P / 'zakupy-3-szkic.csv', 'w', encoding='utf-8', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=list(wiersze[0]), delimiter=';'); w.writeheader(); w.writerows(wiersze)
koszt = sum(float(w['tme_28_09'].split(': ')[1].split(' zł')[0].replace(',', '.')) * w['razem'] for w in wiersze if w['tme_28_09'] and (w['wniosek'].startswith('kupić') or 'dokupić' in w['wniosek']))
L = ['# Lista zakupowa 3 — SZKIC (płytki S1: P02 R4, P03 R6, P09 R2, P10 R2)', '',
     '*1.10.2026, plik generowany przez `src/szkic.py`. Nie zamawiać: BOM-y P03/P09/P10 czekają na recenzję PR, P05/P06/P11 na rewizje S1, '
     'ceny i stany TME są z listy 2 (28.09) i trzeba je sprawdzić w przeglądarce.*', '',
     f"Pozycji: {len(wiersze)}; do wyboru typu: {sum(1 for w in wiersze if w['klucz'] in DO_WYBORU)}; do kupienia: "
     f"{sum(1 for w in wiersze if w['wniosek'].startswith('kupić'))}; częściowo z rejestru: {sum(1 for w in wiersze if 'dokupić' in w['wniosek'])}; "
     f"z rejestru: {sum(1 for w in wiersze if w['wniosek'].startswith('z rejestru'))}. "
     f"Cena z 28.09 jest tylko dla {sum(1 for w in wiersze if w['tme_28_09'] and (w['wniosek'].startswith('kupić') or 'dokupić' in w['wniosek']))} "
     f"pozycji do kupienia (razem {koszt:.2f} zł netto, bez minimów i wysyłki) — reszta to nowe części S1 bez ceny.", '',
     '| Pozycja | ' + ' | '.join(PLYTKI) + ' | Razem | Wniosek | TME 28.09 | Oznaczenia |', '|---|' + '---:|' * (len(PLYTKI) + 1) + '---|---|---|']
for w in wiersze:
    L.append(f"| {w['opis']} | " + ' | '.join(str(w[pl] or '') for pl in PLYTKI) + f" | {w['razem']} | {w['wniosek']} | {w['tme_28_09']} | {w['oznaczenia']} |")
L += ['', '## Uwagi', '',
      '- „z rejestru” znaczy tylko, że w rejestrze jest tyle sztuk tej części. Część z nich mogła być przewidziana dla płytek spoza szkicu '
      '(P04, P05, P06, P08 — kolumna „kupione dla”); przydział ustalić przy liście wiążącej.',
      '- Rezystory i kondensatory 1206 bez MPN w BOM (P09/P10: „SMD 1206 …”) zgrupowane z tymi samymi wartościami P02/P03 (Yageo RC1206FR-07…, Murata GRM31).',
      '- Poza szkicem: P00 R3 i P04 R2.2 (bez zmian względem listy 2), P05 R3 (schemat w toku), P06, P08, P11 (rewizje S1), przewody i drobne mechaniczne.']
(P / 'ZAKUPY-3-SZKIC.md').write_text('\n'.join(L) + '\n', encoding='utf-8')
print(f'{len(wiersze)} pozycji; koszt orientacyjny {koszt:.2f} zł')
