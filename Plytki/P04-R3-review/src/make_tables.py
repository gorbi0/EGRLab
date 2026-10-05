"""P04-R3 review tables from parts.py (single source): P12 contract docs/J_BP.csv, service strips docs/SERWIS.csv, pin list,
purchase list docs/ZAKUPY.md with the register balance, and source snapshot hashes.
verify_s1.py compares J_BP.csv and SERWIS.csv with the EXPORTED netlist and with the P12 contracts, not with this generator."""
from parts import *
import collections, hashlib
def table(name, fields, rows):
    with (P / 'docs' / name).open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f, delimiter=';'); w.writerow(fields); w.writerows(rows)
# --- J_BP1..J_BP3 (edge A). Directions seen from P04, words as in the other boards' J_BP.csv (P12 kontrakty.py).
INFO = {
 'PANEL_3V3': ('zrodlo', 'P11 R2 (J_P12.2)', '3V3_IO przez R40 100R do stykow panelu (STOP, KEY, MECH); przy obsadzonej P04 R1 na P11 = DNP'),
 'MECH_OK': ('in', 'P11 R2 (J_P12.4)', 'petla MECH z panelu; R42 1k + R24 10k do GND po stronie bramki'),
 'STOP_NC_OUT': ('in', 'P11 R2 (J_P12.6)', 'STOP NC: podciaganie SAFE_N przez R4 10k'),
 'ARM_CONTACT': ('in', 'P11 R2 (J_P12.8)', 'ARM NO do GND; R3 1k, R2 10k do 3V3_IO, C2 1u'),
 'SENSOR_PERMIT': ('out', 'P08 (SENSOR; czeka na P08 R2)', 'nazwa jak J4.1 R2.2 / W2 P08 R1; U5B push-pull'),
 'SENSOR_OK': ('in', 'P08 (SENSOR; czeka na P08 R2)', 'nazwa jak J4.3 R2.2 / W2 P08 R1; U10B, 10k R21 do GND'),
 'TEST_KEY': ('in', 'P11 R2 (J_P12.14)', 'ten sam pin co na P11 i P03 R6 (J_BP1.14); R41 1k + R23 10k do GND'),
 'DAQ_OK': ('in', 'P05 R3 (J_BP1.6)', 'U9D, 10k R19 do GND; statyczny'),
 'MOTOR_PERMIT': ('out', 'P07 (DRIVE; czeka na P07)', 'nazwa jak J3.1 R2.2; U5D push-pull'),
 'PWM_OUT': ('out', 'P07 (DRIVE; czeka na P07)', 'nazwa jak J3.3 R2.2; U4C = PWM & MOTOR_PERMIT; GND po obu stronach'),
 'ARM_CLK': ('out', 'P07 (DRIVE; czeka na P07)', 'nazwa jak J3.5 R2.2; U2B'),
 'DRIVE_OK': ('in', 'P07 (DRIVE; czeka na P07)', 'nazwa jak J3.7 R2.2; U10A, 10k R20 do GND'),
 '3V3_IO': ('pwr', 'P02 R4 (J_BP 8/10)', 'zasilanie P04 (rezerwa 30 mA); dwa piny: J_BP2.10 i J_BP3.10'),
 'PSU_OK': ('in', 'P02 R4 (J_BP.12)', 'U9C, 10k R18 do GND; statyczny'),
 'P04_3V3': ('zrodlo', 'P02 R4 (J_BP.15)', '3V3_IO przez R39 1k do Q7 P02 (w R2.2: PG_3V3 do P01 J5)'),
 'SAFE_N': ('in', 'P02 R4 (J_BP.16), P07 (czeka)', 'wspolny wezel OC: podciaganie R4 10k i kolektory Q1-Q3 na P04, Q7 na P02, P07 moze dolozyc OC; dla P12 nadajnik = P02'),
 'PG_LINK': ('petla', 'P02 R4 (J_BP.18)', 'powrot petli PG (zwora 0R na P02); U10C, 10k R22 do GND'),
 'PG_SEND': ('petla', 'P02 R4 (J_BP.17)', '3V3_IO przez R38 1k do petli PG'),
 'SENSOR_ENABLE': ('in', 'P03 R6 (J_BP3.9)', 'U8D, 10k R15 / 100k R28; statyczny'),
 'CORE_LINK': ('in', 'P03 R6 (J_BP3.13)', '3V3_CORE przez R14 1k na P03; U9A, 10k R16 do GND'),
 'HW_ARMED': ('out', 'P03 R6 (J_BP3.17)', 'zatrzask U3A push-pull, czyta CORE'),
 '5V_SYS': ('pwr', 'P02 R4 (J_BP 2/4/6)', 'bez odbiorcy na P04 (jak J1.1 -> TP13 w R2.2); tylko kolek J_SV3.2 przez 1k'),
 'SUP_N_OUT': ('in', 'P03 R6 (J_BP3.12)', 'reset CORE przez U6 i R41 220R na P03; R17 10k do GND, U9B (KONTRAKT-RESET)'),
 'PWM': ('in', 'P03 R6 (J_BP3.14)', 'GPIO1; U8A, 10k R12 do GND; GND po obu stronach'),
 'HEARTBEAT': ('in', 'P03 R6 (J_BP3.16)', 'GPIO21; U8B, 10k R13 / 47k R26'),
 'MCU_ARM': ('in', 'P03 R6 (J_BP3.18)', 'U8C, 10k R14 / 47k R27; statyczny'),
 'INTERLOCK': ('out', 'P03 R6 (J_BP3.20)', 'U7B push-pull, 10k R36 do GND'),
}
rows = []
for j in ('J_BP1', 'J_BP2', 'J_BP3'):
    pins = PARTS[j]['pins']
    for p in sorted(pins, key=int):
        n = pins[p]
        k, tgt, uw = ('gnd', 'P12 (wszystkie)', '') if n == G else INFO[n]
        rows.append([j, p, n, k, tgt, uw])
table('J_BP.csv', ['zlacze', 'pin', 'siec', 'kierunek', 'plytka_docelowa', 'uwagi'], rows)
# --- service strips (edge B) ---
rows = []
for j in ('J_SV1', 'J_SV2', 'J_SV3'):
    pins = PARTS[j]['pins']
    for p in range(1, max(map(int, pins)) + 1):
        n = pins[str(p)]
        if n == G: rows.append([j, p, G, '-', 'masa sondy'])
        else:
            jj, k, r, ohm, why = SERVICE[n[4:]]; v = PARTS[r]
            rows.append([j, p, n[4:], f"{r} {v['value']} 1206", why])
table('SERWIS.csv', ['zlacze', 'pin', 'siec', 'rezystor', 'cel_pomiaru'], rows)
table('netlist-pinowa.csv', ['ref', 'pin', 'net'], [[r, p, n] for r, v in PARTS.items() for p, n in v['pins'].items()])
# --- purchases: one board, grouped by source/MPN/footprint ---
g = collections.defaultdict(list)
for r, v in PARTS.items(): g[(v['zrodlo'], v['mpn'], v['display'], v['footprint'].split(':')[-1])].append(r)
table('zakupy.csv', ['zrodlo', 'nazwa', 'wartosc', 'ilosc_szt', 'referencje', 'obudowa'], [[z, m, d, len(rr), ', '.join(rr), f] for (z, m, d, f), rr in sorted(g.items())])
L = ['# Zakupy P04-R3 — ilości na jedną płytkę (S1)', '',
     '*Plik generowany przez `src/make_tables.py` z `src/parts.py`.* Źródło: **rejestr** = pozycja z `Zamowione/zamowione.csv` (posiadane); **nowe** = do kupienia (po akceptacji, wspólne zamówienie wariantu pełnego). Płytka z JLCPCB (klasa L, 160 × 100 mm); w tym pakiecie tylko schemat.', '',
     '| Źródło | Nazwa (MPN) | Wartość | Ilość | Referencje / obudowa |', '|---|---|---|---:|---|']
for (z, m, d, f), rr in sorted(g.items()): L.append(f'| {z} | {m} | {d} | {len(rr)} | {", ".join(rr)} / {f} |')
L += ['', '## Bilans posiadanych części (rejestr 24.09)', '',
      'Zużycie innych płytek policzone z ich `docs/parts.json` na gałęzi `pelny-s1` (P02 R4, P03 R6, P05 R3, P06 R2, P09 R2, P10 R2). P08 R2 powstaje równolegle — jeśli sięgnie po te same pozycje, trzeba rozstrzygnąć przydział (pytanie w PR).', '',
      '| Część z rejestru | Rejestr | Zużyte przez inne płytki | Zostaje | P04 R3 bierze | Uwagi |', '|---|---:|---|---:|---:|---|',
      '| 74LVC125AD,118 (Nexperia) | 25 | P02 1, P03 7, P05 4, P06 2, P09 2, P10 1 | 8 | 3 | U8–U10 lutowane wprost; zostaje 5 (P08 R1: 2, P07: do ustalenia) |',
      '| SN74HC08N + podstawka DIP14 (Kamami 648) | 8 / 10 | P02 1, P05 1, P06 1 | 5 | 4 | U4–U7 w podstawkach (przydział P04 z 24.09); zostaje 1 (P08) |',
      '| podstawka DIP16 (Kamami 649) | 2 | P03 1 | 1 | 1 | U1 CD74HC123E (układ nowy) |',
      '| adapter SO14→DIP14 (Kamami 575068) | 18 (P04: 3) | — | 3 | 0 | niepotrzebne: SOIC lutowane wprost (S1 §9); do dyspozycji P07/P08 |',
      '| WIMA MKS2 1 µF / 100 V 5 % (MKS2D041001K00JO00) | 2 | P02 R4 C6 | 1 | 1 | C1 (watchdog, PET) — ostatnia sztuka; korpus 7,2 × 7,2 mm (footprint z P02 R4) |',
      '| KEMET C320C102J1G5TA C0G 1 nF | 2 | P05 R3 C32 | 1 | 1 | C18 (filtr SAFE_N) — ostatnia sztuka; raster sprawdzić na wydruku 1:1 |',
      '| Panasonic EEU-EB1J100SH 10 µF / 63 V | 2 | P02 R4 C1 | 1 | 1 | C3 (bulk 3V3_IO) — ostatnia sztuka; w R2.2 EEUFR1H100 10 µF / 50 V, ten sam D5 P2 |',
      '| Kingbright L-934GD | 2 | P02 R4, P03 R6 | 0 | 0 | LED1 jako nowa |',
      '| MF0207 (10K, 100K, 47K, 220K, 1K, 100R) | — | — | 0 | 0 | brak zapasu tych wartości (bilans w P06 R2 `docs/ZAKUPY.md`); wszystkie rezystory P04 jako nowe 1206 |', '',
      '## Uwagi do zakupów', '',
      '- **Rezystory:** wszystkie nowe Yageo RC1206FR-07…L (1 %, 1206), także 21 rezystorów listew serwisowych.',
      '- **C2:** WIMA MKS2 1 µF / 63 V (MKS2C041001F00KSSD) jak w R2.2 — filtr ARM; foliowy THT, bo 1 µF X7R zmienia pojemność z napięciem i temperaturą, a S1 §9 mówi o nowych ceramicznych.',
      '- **C4–C17:** 100 nF X7R 1206 50 V; C15–C17 to druga para 100 nF przy U8–U10 (w R2.2 na adapterach) — do decyzji przy recenzji, czy zostają.',
      '- **U1 CD74HC123E, U2 SN74HC14N, U3 SN74HC74N, Q1–Q3 2N3904BU, U11 MCP100-300DI/TO:** nowe, obudowy jak w R2.2 (DIP, TO-92). Podstawki DIP14 pod U2/U3 opcjonalne (nowe).',
      '- **J_BP1:** obudowane kątowe IDC 2×8; **J_BP2, J_BP3:** 2×10; styki Au. Taśmy IDC ok. 30 mm do P12 (po dwa gniazda zaciskowe) — z zamówieniem P12 dla wariantu pełnego.',
      '- **J_SV1:** goldpin kątowy 1×13, **J_SV2 i J_SV3:** 1×7 (posiadana listwa 1×40 Kamami jest prosta).',
      '- Z R2.2 znikają: Mini-Fit J7/J8 (39-29-9069, 39-29-9109) i ich wiązki, IDC J3–J6 (Würth 612…), pigtaile J1/J2 z kotwami, adaptery SO14 (zostają w rejestrze), K104K15X7RF53H5, K102J15C0GF53H5 (zastąpiony posiadanym C320), EEUFR1H100, MFR-25 (zastąpione 1206), pola TP1–TP15.']
(P / 'docs/ZAKUPY.md').write_text('\n'.join(L) + '\n', encoding='utf-8')
files = {f.relative_to(P / 'reference').as_posix(): hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted((P / 'reference').rglob('*')) if f.is_file() and f.name != 'snapshot-sha256.json'}
(P / 'reference/snapshot-sha256.json').write_text(json.dumps(files, indent=2))
print('J_BP.csv, SERWIS.csv, pin list, ZAKUPY.md and reference hashes written.')
