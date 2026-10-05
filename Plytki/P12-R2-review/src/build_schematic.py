"""P12 R2 (wariant pełny): jeden arkusz A3. Złącza ułożone jak na płytce (widok od strony stosu: poziom 6 u góry, slot S1 po lewej); każdy pin ma
etykietę sieci z kontraktu (docs/kontrakt-P12.json), więc połączenia wynikają wyłącznie z nazw sieci, nigdy z położenia pinów."""
from parts import *
import cadlib
S = Sheet('P12', 'Plytka polaczen krawedzi A (wariant pelny)', 1, None)
KOL = {'S1': 30, 'S2': 82, 'S3': 134}                  # x arkusza (jednostki 2,54 mm) dla slotu
WIERSZ = {6: 16, 5: 31, 4: 46, 3: 61, 2: 76, 1: 91, 'panel': 91}    # y arkusza dla poziomu (P11 w wierszu poziomu 1, kolumna S1)


def put(r, x, y, a=0):
    pp = copy.copy(PARTS[r]); pp['display'] = pp['display'].split(' / ')[0]
    if r.startswith('J'):
        pp['text_at'] = (-4, -8 if PARTS[r]['typ'] != 'IDC 2×5' else -6)
    if r.startswith('TP'):
        pp['text_at'] = (1, -3)
    S.place(pp, x, y, a)


import copy
for z in K12['zlacza']:
    put(z['ref'], KOL['S1' if z['poziom'] == 'panel' else z['slot']], WIERSZ[z['poziom']])
for k in range(1, 5):
    put(f'TP{k}', 70 + 8 * k, 89)
S.text('Kazdy podlaczony pin ma etykiete sieci z kontraktu (docs/kontrakt-P12.json, z pinoutow plytek). Laczenie WYLACZNIE po nazwie sieci, nigdy pin w pin: '
       'np. P03 J_BP2 16/17/19/20 = PFAIL_N / 5V_SYS, a P05 J_BP2 16/17/19/20 = GND.', 8, 101, 1.3)
S.text('Wariant pelny: wszystkie plytki obecne, kazda siec ma co najmniej dwa konce (brak pinow NC). '
       'PG_SEND (P02 J_BP.17 - P04 J_BP2.20) i PG_LINK (P02 J_BP.18 - P04 J_BP2.18) osobno: zwora R34 0R jest na P02 R4, P12 jej nie powtarza.', 8, 104, 1.3)
S.text('Uklad arkusza jak na plytce widzianej od strony stosu: wiersze = poziomy 6 / 5 / 4 / 3 / 2 / 1, kolumny = sloty S1 / S2 / S3; J10 = tasma z P11 (panel).', 8, 107, 1.3)
S.text(f'P12-R2 / 01   PLYTKA POLACZEN KRAWEDZI A (WARIANT PELNY)', 8, 6, 2)
cadlib.CROSS = {n for p_ in PARTS.values() for n in p_['pins'].values() if n != 'NC'}   # global labels: net names without the '/' sheet prefix (PCB classes, GND pour)
S.finish()
for k_, (part, pins) in S.parts.items():   # opis pinów NC: nazwa sieci z kontraktu i płytka, na którą czeka
    for n, net in part.get('nc_nets', {}).items():
        x, y, a = pins[n]; ex = -5.6 if a == 0 else 5.6
        S.items.append(f'(text {q(net + " (NC)")} (at {round(x + ex, 3)} {y} 0) (effects (font (size 1 1)) (justify {"right" if a == 0 else "left"})) '
                       f'(uuid {uid("nctxt" + k_ + n)}))')
S.save()
write_tables(); (P / 'verification').mkdir(exist_ok=True)
(P / 'verification/sheet-parts.json').write_text(json.dumps({'P12': list(S.parts)}, indent=2)); print(len(PARTS), 'parts; one sheet')
