"""P06-R2 review tables from parts.py (single source): P12 contract docs/J_BP.csv, service strips docs/SERWIS.csv, the wires that stay
(ISERIES, BYPASS), purchase list docs/ZAKUPY.md with the register balance, and source snapshot hashes.
verify_s1.py compares J_BP.csv and SERWIS.csv with the EXPORTED netlist, not with this generator."""
from parts import *
import collections, hashlib
def table(name, fields, rows):
    with (P / 'docs' / name).open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f, delimiter=';'); w.writerow(fields); w.writerows(rows)
# --- J_BP (edge A, slot S2) ---
INFO = {2: ('in', 'P03 R6 (J_BP2.2)', 'zegar SPI; GND po obu stronach; P12 wielopunktowo (P05, P06, P07); U5B, 100k R10 do GND'),
        4: ('out', 'P03 R6 (J_BP2.4)', 'wspolne MISO: U5C trojstanowy (OE = CS_LOCAL_N) + R12 47R; P12 wielopunktowo (P05, P06, P07)'),
        6: ('in', 'P03 R6 (J_BP1.2)', 'CS z dekodera P03 (U22 Y0); U5A, 100k R8 do 3V3_P06 (start: nieaktywne)'),
        8: ('out', 'P03 R6 (J_BP1.11)', 'READY: U6C + R19 100R, 10k R20 do GND; statyczny'),
        10: ('pwr', 'P02 R4 (J_BP 2/4/6)', 'zasilanie P06: R6 1R -> 5VA_P06 (budzet 180 mA w MEASURE)'),
        12: ('pwr', 'P02 R4 (J_BP 2/4/6)', 'drugi pin 5V_SYS (S1 5: IDC ok. 1 A na styk)'),
        14: ('pwr', 'P02 R4 (J_BP 8/10)', 'bez odbiorcy na P06 (jak LV06.3 -> TP4 w R1); tylko kolek J_SV2.6 przez 1k'),
        16: ('gnd', 'P12 (wszystkie)', 'rezerwa GND')}
rows = []
for p in sorted(PARTS['J_BP']['pins'], key=int):
    n = PARTS['J_BP']['pins'][p]; k, tgt, uw = INFO.get(int(p), ('gnd', 'P12 (wszystkie)', ''))
    rows.append(['J_BP', p, n, k, tgt, uw])
table('J_BP.csv', ['zlacze', 'pin', 'siec', 'kierunek', 'plytka_docelowa', 'uwagi'], rows)
# --- service strips (edge B) ---
rows = []
for j in ('J_SV1', 'J_SV2'):
    pins = PARTS[j]['pins']
    for p in range(1, max(map(int, pins)) + 1):
        n = pins[str(p)]
        if n == G: rows.append([j, p, G, '-', 'masa sondy'])
        else:
            jj, k, r, ohm, why = SERVICE[n[4:]]; v = PARTS[r]
            rows.append([j, p, n[4:], f"{r} {v['value']} / {'1% MF0207 na stojaco' if v['zrodlo'] == REG else '1% 1206'}", why])
table('SERWIS.csv', ['zlacze', 'pin', 'siec', 'rezystor', 'cel_pomiaru'], rows)
# --- wires that stay (S1 5): ISERIES and BYPASS, soldered in PTH at the x = 0 edge ---
W = [('W3/ISERIES', 'J3', 'P11/J_ISERIESA (do zatwierdzenia z P11 S1)', 'P06', '150', '2x2.5mm2', 'MSTB 2.5/4-ST-5.08 >=12A (P11)', '12', '1=ECU_P1;2=EGR_P1;3/4=NC'),
     ('W4/SW1-A', 'J4', 'SW1.2/3 (panel)', 'oba', '100', '2x2.5mm2', 'brak - oczka lutownicze SW1', '12', '1->SW1.2;2->SW1.3'),
     ('W5/SW1-B', 'J5', 'SW1.4/5/6 (panel)', 'oba', '150', '3xAWG22', 'brak - oczka lutownicze SW1', '12', '1->SW1.4;2->SW1.5;3->SW1.6')]
table('interfejsy.csv', ['ID', 'P06', 'drugi_koniec', 'ktory_koniec_lutowany', 'dlugosc_mm', 'przewod', 'wtyk_drugi_koniec', 'kotwa_mm', 'piny'], W)
table('netlist-pinowa.csv', ['ref', 'pin', 'net'], [[r, p, n] for r, v in PARTS.items() for p, n in v['pins'].items()])
# --- purchases: one board, grouped by source/MPN/footprint ---
g = collections.defaultdict(list)
for r, v in PARTS.items(): g[(v['zrodlo'], v['mpn'], v['display'], v['footprint'].split(':')[-1])].append(r)
table('zakupy.csv', ['zrodlo', 'nazwa', 'wartosc', 'ilosc_szt', 'referencje', 'obudowa'], [[z, m, d, len(rr), ', '.join(rr), f] for (z, m, d, f), rr in sorted(g.items())])
cnt = collections.Counter(v['value'] for v in PARTS.values() if v['ref'][0] == 'R' and v['zrodlo'] == NEW and v['footprint'] == R1206)
L = ['# Zakupy P06-R2 — ilości na jedną płytkę (S1)', '',
     '*Plik generowany przez `src/make_tables.py` z `src/parts.py`.* Źródło: **rejestr** = pozycja z `Zamowione/zamowione.csv` (posiadane, przydział P06); **nowe** = do kupienia (lista zakupowa 3, po akceptacji). Płytka z JLCPCB (klasa 2/3, 106,5 × 100 mm); w tym pakiecie tylko schemat.', '',
     '| Źródło | Nazwa (MPN) | Wartość | Ilość | Referencje / obudowa |', '|---|---|---|---:|---|']
for (z, m, d, f), rr in sorted(g.items()): L.append(f'| {z} | {m} | {d} | {len(rr)} | {", ".join(rr)} / {f} |')
L += ['', '## Bilans posiadanych części (rejestr 24.09; P01 zbędna po decyzji o pakiecie 18650)', '',
      'Zużycie innych płytek z ich BOM-ów (kolumna `zrodlo`): P02 R4 (`main`, zamówiona — pierwszeństwo), P05 R3 (`main`), P09 R2 i P10 R2 (`main`); zestawienie zbiorcze `Plytki/Zakupy-3-szkic`.', '',
      '| Część z rejestru | Rejestr | P02 R4 | P05 R3 | P09 R2 | P10 R2 | Zostaje | P06 R2 bierze | Uwagi |', '|---|---:|---:|---:|---:|---:|---:|---:|---|',
      f"| MF0207FTE-10K | 7 | 7 | 0 | 6 | 3 | −9 | 0 | brak zapasu; {cnt['10K']} × 10 k w P06 jako nowe 1206 |",
      f"| MF0207FTE-100K | 7 | 6 | 0 | 7 | 0 | −6 | 0 | brak zapasu; {cnt['100K']} × 100 k jako nowe 1206 |",
      '| K104K15X7RF5TH5 100 n | 5 | 6 | 0 | 3 | 3 | −7 | 0 | brak zapasu; odsprzęganie 100 n jako nowe 1206 |',
      "| MF0207FTE-47K | 6 | 4 | 1 | 0 | 0 | 1 | 1 | R11 (podciąganie ADC_DOUT) na stojąco — ostatnia sztuka |",
      '| MF0207FTE-4K7 | 6 | 3 | 1 | 0 | 0 | 2 | 0 | brak 4,7 k w P06 |',
      '| MF0207FTE-1R 0,6 W | 2 | 1 | 0 | 0 | 0 | 1 | 0 | R6 wymaga 1 W (impuls ładowania C3 ok. 3 mJ) — KNP01U-1R jak w P05 R3 |',
      '| MF0207FTE-2K2, -820R, -470K, MF0204 6k8 | 2 | po 1 | 0 | 0 | 0 | po 1 | 0 | brak takich wartości w P06 |',
      '| B32529 MKT 10 n / 100 n, WIMA MKS2 1 µ | 2 / 3 / 2 | 1 / 2 / 1 | 0 | 0 | 0 | po 1 | 0 | zapas (jak w P05 R3); w P06 brak tych wartości poza odsprzęganiem 100 n — tam 1206 |',
      '| C320C102J1G5TA C0G 1 n | 2 | 0 | 1 | 0 | 0 | 1 | 0 | brak 1 n w P06 (C2 to 470 p) |',
      '| EEU-FR1H220 / FR1H470 / EB1J100 | 2 / 2 / 2 | 2 / 2 / 1 | 0 | 0 | 0 | 0 / 0 / 1 | 0 | inne wartości niż C3 220 µF / 16 V |',
      '| PR02000201009JA100 (10 Ω 2 W) | 2 | 1 | 0 | 0 | 0 | 1 | 0 | R21 to 39 Ω — nowy PR02 |',
      '| INA240A2EDRQ1, MCP3201-BI/P | 2 / 2 (P06, P07) | — | — | — | — | — | 1 / 1 | U1, U3 — przydział P06 |',
      '| MCP6022-I/P, MCP1525-I/TO, MCP1702-3302E/TO | po 1 (P06) | — | — | — | — | — | po 1 | U2, U10, U4 |',
      '| MCP120-300DI/TO | 4 (P02, P05, P06, P08) | 1 | 1 | — | — | 2 | 1 | U8 |',
      '| MCP120-450DI/TO | 2 TME + 3 Mouser | 2 | 1 | — | — | 2 | 1 | U9 |',
      '| SN74HC08N + podstawka DIP14 (Kamami 648) | 8 / 10 | 1 | 1 | — | — | — | 1 | U7 (P04 bierze 4, P08 1) |',
      '| 74LVC125AD,118 (Nexperia) | 25 (P06: 2) | 1 | 4 | 2 | 1 | — | 2 | U5, U6 lutowane wprost (adaptery Kamami 575068/575072 z przydziału P06 niepotrzebne) |',
      '| podstawka DIP8 złocona (Kamami 1207058) | 2 (P06) | — | — | — | — | — | 2 | U2, U3 (opcjonalnie; wysokość z podstawką ok. 8 mm) |', '',
      '## Uwagi do zakupów', '',
      '- **RSH1:** bocznik SMD 2512 z czterema wyprowadzeniami (Kelvin), 5 mΩ, ≤ 1 %, ≥ 1 W. Propozycja: **Vishay WSK2512R0050FEA** — footprint KiCad `R_Shunt_Vishay_WSK2512_6332Metric_T1.19mm` (opis: zakres 5–200 mΩ). Karta Vishay jest w chmurze zablokowana: moc, TCR i wymiary pól sprawdzić lokalnie przed layoutem. Alternatywa Bourns CSS2H-2512K-5L00F ma inny układ pól — przy zmianie potrzebny nowy footprint i sprawdzenie numeracji pól (kontrola `RSH1-KELVIN` w `verify_s1.py` czyta geometrię).',
      '- **SW1 BYPASS (panel, poza PCB):** DPDT ON-ON, ≥ 10 A przy 12–30 V DC (obciążenie rezystancyjne/indukcyjne silnika EGR do 6 A), oczka lutownicze, montaż w panelu (tuleja z nakrętką). Styki wspólne w środku (2 i 5 w numeracji schematu: BYPASS 2-3 + 5-6, MEASURE 2-1 + 5-4). MPN do potwierdzenia, zakup po akceptacji; NKK S6A nie kupować. Biegun B obciąża R21 (ok. 0,13 A), więc styki srebrne są w porządku.',
      '- **R21:** Vishay PR02 39 Ω 2 W (kod do potwierdzenia, np. PR02000203909JA100), leżący 3–5 mm nad laminatem.',
      '- **R6:** KNP01U-1R (1 W, drutowy, jak R1 w P05 R3); próba impulsowa z karty (ok. 3 mJ przy ładowaniu C3 220 µF) niepotwierdzona.',
      '- **C3:** 220 µF / 16 V, Panasonic EEUFR1C221 (D6,3 × 11,2 mm, raster 2,5 mm) — ta sama pozycja co C1 w P05 R3.',
      '- **R1–R4 (0,1 %, 25 ppm/K):** Yageo RT1206BRD0710RL (10 Ω — sprawdzić, czy seria RT ma 10 Ω w 0,1 %; zamiennik Panasonic ERA-8AEB100V) i RT1206BRD075K11L (5,11 kΩ, zamiana 1:1 z listy 2).',
      '- **C1 470 n:** X7R 1206 50 V 10 % zamiast PET (S1: nowe = 1206). Rozrzut τ rośnie z 1,07–1,33 ms do ok. 0,92–1,39 ms (tolerancja + temperatura); kalibracja i tak w firmware. Pytanie w PR: C0G/film SMD zamiast X7R.',
      '- **C4/C5 4,7 µF X7R 1206 25 V** zamiast elektrolitów EEUFR1H4R7 (MCP1525: CL 1–10 µF; MCP1702: wyjście ceramiczne X7R dozwolone).',
      '- **J_BP:** obudowane kątowe IDC 2×8, raster 2,54 mm, styki Au; taśma IDC 2×8 ok. 30 mm do P12 (dwa gniazda zaciskowe).',
      '- **J_SV1 / J_SV2:** goldpin **kątowy** 1×7 i 1×13 (posiadana listwa 1×40 Kamami jest prosta).',
      '- Z wersji R1 znikają: PBV-R005-F1-0.5, NKK S6A, wiązki W1 LV06 (Mini-Fit 4p) i W2 ILOG (IDC 2×4), MKS2C034701C00KSSD, EEUFR1C471, EEUFR1H4R7, rezystory osiowe DIN0207 (zastąpione 1206).',
      '- Nowe 1206: rezystory Yageo RC1206FR-07…, kondensatory X7R 50 V (4,7 µF: 25 V; 470 p: C0G 50 V).']
(P / 'docs/ZAKUPY.md').write_text('\n'.join(L) + '\n', encoding='utf-8')
files = {f.relative_to(P / 'reference').as_posix(): hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted((P / 'reference').rglob('*')) if f.is_file() and f.name != 'snapshot-sha256.json'}
(P / 'reference/snapshot-sha256.json').write_text(json.dumps(files, indent=2))
print('J_BP.csv, SERWIS.csv, interfaces, ZAKUPY.md and reference hashes written.')
