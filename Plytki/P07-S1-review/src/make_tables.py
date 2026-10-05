"""P07-S1 tables from parts.py (single source): P12 contract docs/J_BP.csv, service strips docs/SERWIS.csv, wires docs/interfejsy.csv,
pin list, purchase list docs/zakupy.csv and source hashes. verify_s1.py compares J_BP.csv / SERWIS.csv with the EXPORTED netlist."""
from parts import *
import collections, hashlib
def table(name, fields, rows):
    with (P / 'docs' / name).open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f, delimiter=';'); w.writerow(fields); w.writerows(rows)
INFO = {('J_BP1', 2): ('in', 'P03 R6 (J_BP2.2)', 'zegar SPI; P12 wielopunktowo (P05, P06, P07); U7B, 100k R20 do GND'),
        ('J_BP1', 4): ('out', 'P03 R6 (J_BP2.4)', 'wspolne MISO: U7C trojstanowy (OE = CS_LOCAL_N) + R22 47R; P12 wielopunktowo (P05, P06, P07)'),
        ('J_BP1', 6): ('in', 'P03 R6 (J_BP1.4)', 'CS z dekodera P03 (U22); U7A, 100k R17 do 3V3A_P07 (start: nieaktywne)'),
        ('J_BP1', 8): ('in', 'P03 R6 (J_BP1.19)', 'MCP23017 GPA; U10A (Ioff), 100k R26 do GND'),
        ('J_BP1', 10): ('in', 'P03 R6 (J_BP1.20)', 'MCP23017 GPA; U10B (Ioff), 100k R27 do GND'),
        ('J_BP1', 12): ('out', 'P03 R6 (J_BP1.17)', 'IS galezi R: U17 Schmitt + R48 100R; H = prad >~2-3 A albo blad IS; 10k R28 do GND na P03'),
        ('J_BP1', 14): ('out', 'P03 R6 (J_BP1.18)', 'IS galezi L: U17 Schmitt + R49 100R; jw.; 10k R29 do GND na P03'),
        ('J_BP1', 16): ('gnd', 'P12 (wszystkie)', 'rezerwa GND'),
        ('J_BP2', 2): ('in', 'P04 R3 (J_BP2.2)', 'U5D push-pull na P04; U10C (Ioff), 100k R28 do GND'),
        ('J_BP2', 4): ('in', 'P04 R3 (J_BP2.4)', 'PWM & MOTOR_PERMIT z P04; U10D (Ioff), 100k R29 do GND'),
        ('J_BP2', 6): ('in', 'P04 R3 (J_BP2.6)', 'zbocze ARM (U2B HC14 na P04); zegar U15 (obie polowy), 100k R30 do GND'),
        ('J_BP2', 8): ('out', 'P04 R3 (J_BP2.8)', 'DRIVE_OK = RAILS_OK & NO_TRIP (U13B) + R32 100R; P04: U10A, 10k R20 do GND'),
        ('J_BP2', 10): ('pwr', 'P02 R4 (J_BP 2/4/6)', '5VA_P07 przez R50 10R, 5V_MOD przez F1 PTC (VCC modulu)'),
        ('J_BP2', 12): ('pwr', 'P02 R4 (J_BP 2/4/6)', 'drugi pin 5V_SYS (S1 5)'),
        ('J_BP2', 14): ('pwr', 'P02 R4 (J_BP 8/10)', 'zasilanie logiki P07 (U10-U15, U17), jak P04'),
        ('J_BP2', 16): ('in', 'P02 R4 (J_BP.16), P04 R3 (J_BP2.16)', 'wspolny wezel OC (podciaganie R4 10k na P04); P07 czyta (R31 1k -> U11 Schmitt) i sciaga Q2 przy OC; dla P12 nadajnik = P02 (jak P04 R3)')}
rows = []
for j in ('J_BP1', 'J_BP2'):
    for p in sorted(PARTS[j]['pins'], key=int):
        n = PARTS[j]['pins'][p]; k, tgt, uw = INFO.get((j, int(p)), ('gnd', 'P12 (wszystkie)', ''))
        rows.append([j, p, n, k, tgt, uw])
table('J_BP.csv', ['zlacze', 'pin', 'siec', 'kierunek', 'plytka_docelowa', 'uwagi'], rows)
rows = []
for j in ('J_SV1', 'J_SV2'):
    pins = PARTS[j]['pins']
    for p in range(1, max(map(int, pins)) + 1):
        n = pins[str(p)]
        if n == G: rows.append([j, p, G, '-', 'masa sondy'])
        else:
            jj, k, r, ohm, why = SERVICE[n[4:]]; v = PARTS[r]
            rows.append([j, p, n[4:], f"{r} {v['value']} / 1% 1206", why])
table('SERWIS.csv', ['zlacze', 'pin', 'siec', 'rezystor', 'cel_pomiaru'], rows)
W = [('W_VMOTOR', 'J1', 'P02 R4 J2 (GMSTBA 2,5/3-G-7,62; 1 VMOTOR, 2 GND)', 'P07', '250', '2 x 2,0 mm2 (czerwony / czarny)', 'GMSTB 2,5/3-ST-7,62 (wtyk do P02 J2)', '12', '1=VMOTOR;2=PGND'),
     ('W_MODPWR', 'J2', 'modul IBT-2: zaciski B+ / B-', 'P07', '300', '2 x 2,0 mm2 (czerwony / czarny)', 'tulejki 2,0 mm2 w zaciskach modulu', '12', '1=MOD_BP->B+;2=PGND->B-'),
     ('W_MODOUT', 'J3', 'modul IBT-2: zaciski M+ / M-', 'P07', '300', '2 x 2,0 mm2 (np. zolty / niebieski)', 'tulejki 2,0 mm2 w zaciskach modulu', '12', '1=M+->MOD_MP;2=M-->T_EGR_P3'),
     ('W_TEST', 'J4', 'P11 port TEST (piny zaworu 1 / 3)', 'P07', '200', '2 x 2,0 mm2', 'wg P11 R2 (port TEST)', '12', '1=T_EGR_P1;2=T_EGR_P3'),
     ('W_MOD_CTRL', 'J5', 'modul IBT-2: listwa 2x4 (1 RPWM, 3 R_EN, 5 R_IS, 7 VCC / 2 LPWM, 4 L_EN, 6 L_IS, 8 GND)', 'oba (IDC)', '300', 'tasma 8 zyl 1,27 mm AWG28', 'gniazdo IDC 2x4 zenskie na obu koncach (J5: obudowane IDC 2x4 katowe, kluczowane)', '-', '1..8 = 1..8 (numeracja jak listwa modulu, decyzja 5.10)')]
table('interfejsy.csv', ['ID', 'P07', 'drugi_koniec', 'ktory_koniec_lutowany', 'dlugosc_mm', 'przewod', 'wtyk_drugi_koniec', 'kotwa_mm', 'piny'], W)
table('netlist-pinowa.csv', ['ref', 'pin', 'net'], [[r, p, n] for r, v in PARTS.items() for p, n in v['pins'].items()])
g = collections.defaultdict(list)
for r, v in PARTS.items(): g[(v['zrodlo'], v['mpn'], v['display'], v['footprint'].split(':')[-1])].append(r)
table('zakupy.csv', ['zrodlo', 'nazwa', 'wartosc', 'ilosc_szt', 'referencje', 'obudowa'], [[z, m, d, len(rr), ', '.join(sorted(rr, key=lambda s: (re.sub(r'\d', '', s), int(re.sub(r'\D', '', s) or 0)))), f] for (z, m, d, f), rr in sorted(g.items())]
      + [[o['zrodlo'], o['mpn'], o['display'], o['qty'], o['ref'], 'wiazka (poza plytka)'] for o in OFFBOARD])
files = {f.relative_to(P / 'reference').as_posix(): hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted((P / 'reference').rglob('*')) if f.is_file() and f.name != 'snapshot-sha256.json'}
(P / 'reference/snapshot-sha256.json').write_text(json.dumps(files, indent=2))
print('J_BP.csv, SERWIS.csv, interfejsy.csv, zakupy.csv written.')
