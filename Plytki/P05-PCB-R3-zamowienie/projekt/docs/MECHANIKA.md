# Mechanika, złącza i montaż P05-R3 (format S1)

*R3 (1.10.2026): obrys R1/R2 160 × 120 mm, para B2B P03/P05 (TSW-108-08-G-D-NA / SSW-108-02-G-D-RA) i tabela matingu znikają. Obowiązuje `Plytki/Format-S1/SPECYFIKACJA-FORMATU-S1.md` (S1-3). Od 1.10 layout jest w pakiecie (sesja lokalna, README sekcja „PCB”); poniżej wymagania, według których powstał.*

## Płytka

Klasa 2/3: 106,5 × 100,0 mm, sloty S1–S2 poziomu 3, narożniki R 1 mm, FR-4 1,6 mm, 2 warstwy, miedź 35 µm, JLCPCB. Osiem otworów M3 Ø 3,2 mm w x = 4,0 / 49,0 / 57,5 / 102,5 i y = 14,0 / 86,0, strefa Ø 7 mm bez miedzi innych sieci i bez elementów. Dystanse 20 mm: elementy od góry ≤ 16,5 mm (najwyższe C1 Ø 6,3 × 11,2 mm — 220 µF od 1.10 — i SW1 ok. 11,4 mm), od spodu tylko SMD ≤ 1,5 mm, bez SOIC, ≥ 1 mm od pól THT; wyprowadzenia THT przycięte do ≤ 1,5 mm.

Reguły jak w P02-R3 (minimalny prześwit 0,15 mm przy LQFP/VSSOP, pierścień PTH i przelotek ≥ 0,25 mm). Płaszczyzna masy pod rdzeniem ADC, referencją i końcowym rozprowadzeniem wejść jak w R2: bez podziału GND na wyspy łączone mostkiem.

## Krawędź A (y = 0) — złącza do P12

| Złącze | Slot | Środek x | Typ | Uwagi |
|---|---|---:|---|---|
| J_BP1 | S1 | 26,5 mm | IDC 2×5 kątowe obudowane, Au | 5V_SYS × 2, DAQ_OK, VBAT_SENSE; nieparzyste GND |
| J_BP2 | S2 | 80,0 mm | IDC 2×10 kątowe obudowane, Au | DAQ na tych samych pinach co P03 R6 J_BP2 (tory P12 pionowo) |

Strona wtyku równo z krawędzią, pin 1 od strony mniejszego x, pas y = 0–10 mm zastrzeżony tylko na długości złącza (x = 10–43 mm w slocie). Taśma IDC ok. 30 mm do P12.

## Krawędź B (y = 100) — listwy serwisowe

J_SV1 (1 × 13) w slocie S1 (x = 10–43 mm), J_SV2 (1 × 13) w slocie S2 (x = 63,5–96,5 mm); goldpin kątowy, kołki ok. 6 mm za krawędzią. GND na pierwszym i ostatnim pinie, na J_SV1 także na 3 i 7 (1.10: szyny obok GND i siebie, VBAT_SENSE między GND). Rezystory szeregowe (1206 albo MF0207 na stojąco) **przy węźle**, nie przy listwie — tor od rezystora do kołka może być długi, bo po stronie kołka nie płynie prąd. Nadruk: nazwa sieci przy każdym kołku, czytelna od strony B. Pin 1 kątowej listwy widziany z góry leży przy większym x; layout może przestawić kołki według położenia węzłów — w `src/parts.py` (listy SV1/SV2, `SV1_PIN`), potem `run_schematic.py`; zasadę sąsiedztwa szyn sprawdza `verify_s1.py`.

## Strona panelu (x = 0)

J4 (TAPS, 5 par AWG24 z P11), J6 (AUX, RG174 do BNC na panelu) i SW1 stoją przy brzegu x = 0 — TAPS najkrótszą drogą (S1 §7). Pigtaile lutowane w PTH: otwory 1,1 mm, pady 2,2 mm, dwa otwory kotwy 3,2 mm 11,5 mm od pierwszego rzędu, opaska 2,5 mm na izolacji. Ekran AUX łączy się z GND na J6 (bez izolacji galwanicznej).

SW1 — **E-Switch 100 DPDT ON-ON w wersji kątowej M6** (decyzja 1.10; footprint `P05:ESW_100DP_M6` z rysunku M6-DP, karta s. 11: 2 × 3 otwory Ø1,85 w rastrze 4,70 × 3,81 i dwie nóżki wspornika 12,70 mm przed biegunem A). Obudowa ok. 11,4 mm nad płytką, tuleja i dźwignia równolegle do płytki w stronę x = 0 — przez otwór w panelu. Wersja z chmury (do 1.10): **C&K JS202011AQN** (suwak DPDT ON-ON, kątowy, footprint KiCad `SW_CK_JS202011AQN_DPDT_Angled` z rysunku C&K JS): suwak wystaje za krawędź płytki. Dostęp przez otwór w panelu przy x = 0 albo od strony B rozstrzyga layout i makieta obudowy. Pozycje sprawdzić omomierzem (ODBIOR krok 13): HI = 2–1 + 5–4 (bocznik R35 do GND), LO = 2–3 + 5–6 (pin 6 wolny) — jak w netliście i BOM (1.10: tu wcześniej zamienione 5–4 / 5–6).

## Elementy wymagające szczególnej kontroli

- U1 AD7606BBSTZ LQFP64, pitch 0,5 mm; odsprzęganie według wzoru `Plytki/P05-R2-review/wip-layout-obrys-R1/` (opisy „Cx przy U1.nn” w arkuszu ADC), przy czym kondensatory są teraz 1206 zamiast 0603/0805 — korpusy większe, wzór trzeba dopasować; dozwolone od spodu pod U1 (S1-2). DOUT nie pod U1 po B.Cu (P5-01).
- U3 TLV1702 VSSOP-8 pitch 0,65 mm, U2 i U8–U11 SOIC — tylko od góry (poziom 3).
- U6/U7 MCP120 bondout D: 1 RESET, 2 VDD, 3 GND; U12 MCP1700: 1 GND, 2 VIN, 3 VOUT.
- R1 KNP01U-1R 1 W leżący (footprint DIN0411, 15,24 mm). Rezystory posiadane (R13 47k, R43 4,7k) na stojąco, raster 5,08 mm.
- Kondensatory posiadane THT: MKT B32529 (C16–C18, C25, C26) raster 5 mm, WIMA MKS2 1 µF 7,2 × 7,2 mm (C2, C23), KEMET C320 1 nF (C32, raster do sprawdzenia na wydruku 1:1).
- C12/C13 22 µF 1210 X7R przy U1.42 i U1.44/45.
- K1–K3 G6K-2P-Y DC5 THT.

Nad płytką zostawić miejsce na sondę przy TP1–TP5 (krok 11 ODBIOR, przed skręceniem stosu).
