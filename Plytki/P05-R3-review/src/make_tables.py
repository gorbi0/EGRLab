"""P05-R3 review tables from parts.py (single source): P12 contract docs/J_BP.csv, service strips docs/SERWIS.csv, the remaining
wires (TAPS, AUX), pinout, BOM groups, net purchase list docs/ZAKUPY.md with the register balance, and source snapshot hashes.
verify_s1.py compares J_BP.csv and SERWIS.csv with the EXPORTED netlist, not with this generator."""
from parts import *
import collections, hashlib
def table(name, fields, rows):
    with (P / 'docs' / name).open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f, delimiter=';'); w.writerow(fields); w.writerows(rows)
# --- J_BP (edge A) ---
INFO = {('J_BP1', 2): ('pwr', 'P02 R4 (J_BP 2/4/6)', 'zasilanie P05: R1 -> 5VA_P05, U2, U3, U7, COM U4 i cewki K1-K3'),
        ('J_BP1', 4): ('pwr', 'P02 R4 (J_BP 2/4/6)', 'drugi pin 5V_SYS (S1 5: IDC ok. 1 A na styk)'),
        ('J_BP1', 6): ('out', 'P04 (wariant pelny)', 'U5C, 10k R12 do GND; w LOGGER bez odbiorcy, linia zostaje'),
        ('J_BP1', 8): ('gnd', 'P12 (wszystkie)', 'rezerwa GND oddzielajaca VBAT_SENSE od DAQ_OK'),
        ('J_BP1', 10): ('in', 'P02 R4 (J_BP.20)', 'akumulator auta (10k + P6KE24CA na P02 R4); dzielnik R31/R32 -> CH7'),
        ('J_BP2', 2): ('in', 'P03 R6 (J_BP2.2)', 'zegar; GND po obu stronach; P12 wielopunktowo (P05, P06, P07)'),
        ('J_BP2', 4): ('out', 'P03 R6 (J_BP2.4)', 'wspolne MISO: U11A trojstanowy (OE = CS) + R26 33R'),
        ('J_BP2', 6): ('in', 'P03 R6 (J_BP2.6)', 'U9A, 10k R15 do GND'),
        ('J_BP2', 8): ('in', 'P03 R6 (J_BP2.8)', 'U9C, 47k R13 do 3V3_DAQ (start: nieaktywne)'),
        ('J_BP2', 10): ('in', 'P03 R6 (J_BP2.10)', 'U9D, 10k R16 do GND'),
        ('J_BP2', 12): ('out', 'P03 R6 (J_BP2.12)', 'U11B + R27 33R'),
        ('J_BP2', 14): ('in', 'P03 R6 (J_BP2.14)', 'U10B, 10k R18 do GND; GND po obu stronach'),
        ('J_BP2', 16): ('gnd', 'P12 (wszystkie)', 'rezerwa GND; na P03 R6 J_BP2.16 jest PFAIL_N - P12 nie laczy'),
        ('J_BP2', 18): ('in', 'P03 R6 (J_BP2.18)', 'U10A, 10k R17 do GND; statyczny'),
        ('J_BP2', 20): ('gnd', 'P12 (wszystkie)', 'rezerwa GND; na P03 R6 J_BP2.20 jest 5V_SYS - P12 nie laczy')}
rows = []
for j in ('J_BP1', 'J_BP2'):
    for p in sorted(PARTS[j]['pins'], key=int):
        n = PARTS[j]['pins'][p]; k, tgt, uw = INFO.get((j, int(p)), ('gnd', 'P12 (wszystkie)', ''))
        rows.append([j, p, n, k, tgt, uw])
table('J_BP.csv', ['zlacze', 'pin', 'siec', 'kierunek', 'plytka_docelowa', 'uwagi'], rows)
# --- service strips (edge B) ---
rows = []
for j in ('J_SV1', 'J_SV2'):
    pins = PARTS[j]['pins']; last = max(map(int, pins))
    for p in range(1, last + 1):
        n = pins[str(p)]
        if n == G: rows.append([j, p, G, '-', 'masa sondy'])
        else:
            jj, k, r, ohm, why = SERVICE[n[4:]]; v = PARTS[r]
            rows.append([j, p, n[4:], f"{r} {v['value']} / {'1% MF0207 na stojaco' if v['zrodlo'] == REG else '1% 1206'}", why])
table('SERWIS.csv', ['zlacze', 'pin', 'siec', 'rezystor', 'cel_pomiaru'], rows)
# --- wires that stay (S1 5): TAPS and AUX ---
h = [('TAPS', 'J4', 'P11/TAPS', '50', '5 par AWG24 sygnal/GND', 'Mini-Fit Jr female 12p Au, 11/12 NC', 'P05/J4 (PTH przy brzegu x = 0)', ''),
     ('AUX', 'J6', 'BNC panel', '50', 'RG174', 'BNC izolowany od panelu; ekran do GND', 'P05/J6 (PTH przy brzegu x = 0)', '')]
fields = ['interfejs', 'P05', 'drugi_koniec', 'dlugosc_mm', 'przewod', 'wtyk', 'koniec_lutowany', 'klucz']
table('interfejsy.csv', fields, h)
table('wiazki-BOM.csv', ['ref', 'nazwa', 'ilosc', 'dlugosc_mm', 'przewod', 'wtyk'], [['H_' + a, 'Wiazka ' + a, 1, l, w, c] for a, j, peer, l, w, c, s, k in h])
rows = [[a, j, p, n, l, s] for a, j, peer, l, w, c, s, k in h for p, n in PARTS[j]['pins'].items()]
rows += [['P12', j, p, n, '30 (tasma IDC)', 'nie'] for j in ('J_BP1', 'J_BP2') for p, n in PARTS[j]['pins'].items()]
rows += [['SERWIS', j, p, n, '-', 'nie'] for j in ('J_SV1', 'J_SV2') for p, n in PARTS[j]['pins'].items()]
table('pinout.csv', ['interface', 'connector', 'pin', 'net', 'length_mm', 'soldered_end'], rows)
table('netlist-pinowa.csv', ['ref', 'pin', 'net'], [[r, p, n] for r, v in PARTS.items() for p, n in v['pins'].items()])
# --- purchases: one board, grouped by source/MPN/footprint ---
g = collections.defaultdict(list)
for r, v in PARTS.items():
    if not r.startswith('TP'): g[(v['zrodlo'], v['mpn'], v['display'], v['footprint'].split(':')[-1])].append(r)
table('zakupy.csv', ['zrodlo', 'nazwa', 'wartosc', 'ilosc_szt', 'referencje', 'obudowa'], [[z, m, d, len(rr), ', '.join(rr), f] for (z, m, d, f), rr in sorted(g.items())])
use = collections.Counter(v['mpn'].split(' ')[0] for v in PARTS.values() if v['zrodlo'] == REG)
L = ['# Zakupy P05-R3 — ilości na jedną płytkę (S1)', '',
     '*Plik generowany przez `src/make_tables.py` z `src/parts.py`.* Źródło: **rejestr** = pozycja z `Zamowione/zamowione.csv` (posiadane); **nowe** = do kupienia (lista zakupowa 2 do przeliczenia po decyzjach S1). Płytka z JLCPCB (klasa 2/3, 106,5 × 100 mm); tu tylko schemat.', '',
     '| Źródło | Nazwa (MPN) | Wartość | Ilość | Referencje / obudowa |', '|---|---|---|---:|---|']
for (z, m, d, f), rr in sorted(g.items()): L.append(f'| {z} | {m} | {d} | {len(rr)} | {", ".join(rr)} / {f} |')
L += ['', '## Bilans posiadanych części (rejestr 24.09, P01 zbędna po decyzji o pakiecie 18650)', '',
      'Zużycie innych płytek z ich BOM-ów (kolumna `zrodlo`): P02 R4 (`main`, zamówiona), P09 R2 i P10 R2 (gałęzie `p09-r2-pcb`, `p10-r2-pcb`). '
      '1.10 (recenzja lokalna): pierwszy bilans pomijał P02 R4 — zadanie wymieniało tylko P09/P10.', '',
      '| Część z rejestru | Rejestr | P02 R4 | P09 R2 | P10 R2 | Zostaje | P05 R3 bierze | Uwagi |', '|---|---:|---:|---:|---:|---:|---:|---|',
      f"| MF0207FTE-10K | 7 | 7 | 6 | 3 | −9 | 0 | brak zapasu; {sum(1 for v in PARTS.values() if v['value'] == '10K')} × 10 k w P05 jako nowe 1206 |",
      '| MF0207FTE-100K | 7 | 6 | 7 | 0 | −6 | 0 | brak zapasu; dzielniki 100 k i tak 0,1 % |',
      '| K104K15X7RF5TH5 100 n | 5 | 6 | 3 | 3 | −7 | 0 | brak zapasu (lista zakupowa 3 liczy całość) |',
      f"| MF0207FTE-47K | 6 | 4 | 0 | 0 | 2 | {use['MF0207FTE-47K']} | R13 (podciąganie CS, P5-05) |",
      f"| MF0207FTE-4K7 | 6 | 3 | 0 | 0 | 3 | {use['MF0207FTE-4K7']} | R43, kołek VBAT_SENSE (S1 §6: 4,7 kΩ) |",
      f"| B32529C1103J289 MKT 10 n/100 V | 2 | 1 | 0 | 0 | 1 | {use['B32529C1103J289']} | za mało na parę C25/C26 (filtry progów okna) — obie nowe 1206 |",
      f"| B32529C1104J000 MKT 100 n/100 V | 3 | 2 | 0 | 0 | 1 | {use['B32529C1104J000']} | za mało na C16–C18 — nowe 1206 |",
      f"| MKS2D041001K00JO00 WIMA 1 µ/100 V | 2 | 1 | 0 | 0 | 1 | {use['MKS2D041001K00JO00']} | za mało na C2 i C23 — nowe 1206 |",
      f"| C320C102J1G5TA C0G 1 n | 2 | 0 | 0 | 0 | 2 | {use['C320C102J1G5TA']} | C32 (CH6); raster nóżek sprawdzić na wydruku 1:1 |",
      '| MF0207FTE-1R 0,6 W | 2 | 1 | 0 | 0 | 1 | 0 | R1 wymaga 1 W (udar ładowania C1 ok. 6 mJ) |',
      '| MF0207FTE-2K2, -820R, -470K, MF0204 6k8 | 2 | po 1 | 0 | 0 | po 1 | 0 | brak takich wartości w P05 |',
      f"| 74LVC125AD,118 | 25 (P05: 4) | — | 2 | 1 | — | {use['74LVC125AD,118']} | U8–U11, przydział z zamówienia |",
      f"| MCP120-300DI/TO, MCP120-450DI/TO | przydział P05 | — | — | — | — | {use['MCP120-300DI/TO'] + use['MCP120-450DI/TO']} | U6, U7 |",
      f"| SN74HC08N + podstawka DIP14 (Kamami 648) | przydział P05 | — | — | — | — | {use['SN74HC08N']} | U5 |",
      f"| 1N4148 (Kamami 1187768) | 10 | 0 | 0 | 0 | 10 | {use['1N4148']} | D1–D3 (P08 bierze 1) |", '',
      'Kondensatory foliowe zostają po jednej sztuce każdego typu (zapas). P03 R6 nie używa posiadanych THT (wszystko 1206); MF0207 10 k i 100 k zużywa P02 R4 z P09 R2.', '',
      '## Uwagi do zakupów', '',
      '- **Rezystory precyzyjne 1206 0,1 % (propozycja MPN, do potwierdzenia w TME i karcie Yageo RT):** okno DAQ_OK R3–R8 w klasie **10 ppm/K** (RT1206BRB07…), dzielniki kanałów R28, R29, R31–R35 w klasie 25 ppm/K (RT1206BRD07…). Uzasadnienie i budżet: README, „Okno DAQ_OK”. Zamiennik serii: Panasonic ERA-8AR (10 ppm/K) / ERA-8AE (25 ppm/K), 0,1 %.',
      '- U2: **REF5025ID** (Mouser 595-REF5025ID, tuba; klasa wysoka jak REF5025IDR — decyzja 29.09). U3: lista 2 ma TLV1702AIDGKR (wersja przemysłowa, ten sam pinout) zamiast TLV1702AQDGKRQ1.',
      '- R1: KNP01U-1R (1 W, drutowy, z listy 2); próba impulsowa (ok. 6 mJ przy ładowaniu C1) z karty niepotwierdzona.',
      '- C12/C13: 22 µF/25 V X7R **1210**, TDK C3225X7R1E226M250AB (BOM; lista 2 miała Samsung CL32B226KAJNNNE — zamiennik po sprawdzeniu DC-bias); 1206 22 µF przy 4,4 V nie daje pewnie Ceff ≥ 10 µF (krok 11 ODBIOR). Grubość 2,5 mm: tylko od góry.',
      '- SW1: **do decyzji użytkownika** (1.10). Wybrany 29.09 E-Switch 100DP1T1B1M2REH to wersja pionowa (M2): obudowa z tuleją ok. 17,8 mm, z dźwignią ok. 28 mm — ponad 16,5 mm poziomu 3. Warianty: E-Switch kątowy M6 (np. 100DP1T1B3M6REH, ok. 11,5 mm nad płytką, dźwignia przez ściankę przy x = 0) albo C&K JS202011AQN (suwak kątowy, obecnie w schemacie). Karta E-Switch: `reference/E-Switch-100-series.pdf`. Nie kupować przed decyzją.',
      '- J_BP1/J_BP2: obudowane kątowe IDC 2×5 i 2×10, raster 2,54 mm, styki Au; taśmy IDC do P12 (po dwa gniazda zaciskowe).',
      '- J_SV1/J_SV2: goldpin **kątowy** 2 × 1×13 (posiadana listwa 1×40 z Kamami jest prosta).',
      '- Z listy 2 znikają: TSW-108-08-G-D-NA (B2B), wtyki Mini-Fit 4p (LV05) i 14p (VSENSE), IDC 6p (DAQOK) z przewodami; zostają TAPS (Mini-Fit 12p, AWG24) i AUX (BNC-056, RG174).',
      '- Nowe 1206: rezystory Yageo RC1206FR-07…, kondensatory X7R 25 V (220 p: C0G 50 V).']
(P / 'docs/ZAKUPY.md').write_text('\n'.join(L) + '\n', encoding='utf-8')
files = {f.relative_to(P / 'reference').as_posix(): hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted((P / 'reference').rglob('*')) if f.is_file() and f.name != 'snapshot-sha256.json'}
(P / 'reference/snapshot-sha256.json').write_text(json.dumps(files, indent=2))
print('J_BP.csv, SERWIS.csv, interfaces, pinout, ZAKUPY.md and reference hashes written.')
