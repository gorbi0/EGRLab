# P05 DAQ — R3, schemat w formacie S1

*1.10.2026. Pakiet na kopii łańcucha `P05-R2-review/src` według `Plytki/Format-S1/zadania/ZADANIE-P05-S1.md` (decyzja użytkownika 1.10.2026: dwa złącza J_BP, wariant B). Zamknięty pakiet R2 bez zmian.*

**1.10.2026 (lokalnie): poprawki po recenzji PR #7** — listwa J_SV1 13 kołków (szyny obok GND i siebie, VBAT_SENSE między GND), bilans posiadanych części z P02 R4 (kondensatory foliowe jako nowe 1206), punkt otwarty o pojemności 5V_SYS, pomiar REF_2V5 w ODBIOR, kontrola kolumny rezystorów w `SERWIS.csv`, poprawki dokumentów. Decyzje użytkownika 1.10: **SW1 = E-Switch 100 kątowy (M6)** i **C1 = 220 µF**.

**Status (1.10.2026 wieczorem): schemat R3 i PCB gotowe do recenzji** (gałąź `p05-r3-pcb`, sesja lokalna na komputerze 24/7): DRC 0 niepołączonych / 0 niezgodności / 0 innych naruszeń (4 przyjęte `lib_footprint_mismatch`), kontrole PCB 30/30, próby ujemne 31/31, PDF `output/pdf/P05-R3-PCB.pdf`; sekcja „PCB” niżej. Sprzętu nie zmontowano ani nie zmierzono.

Obwód R2 zostaje: okno DAQ_OK z REF5025IDR (R5 6,04 kΩ, R7 5,11 kΩ), R13 47 kΩ, CH7 = VBAT_SENSE, przekaźniki K1–K3, tor AUX. Zmieniają się złącza do innych płytek, punkty pomiarowe i typy części. `verify_s1.py` sprawdza na eksportowanej netliście, że poza wymienionymi złączami każdy pin obwodu R2 ma tę samą sieć co w R2 (`reference/P05-R2.xml`); od 1.10 także SW1 (E-Switch M6 ma układ styków jak C&K 7201 z R2 — wersja z chmury lustrzyła biegun B pod suwak JS).

## Zmiany R2 → R3

| Punkt | R2 | R3 |
|---|---|---|
| Płytka | obrys R1 160 × 120 mm (layout niedokończony) | klasa 2/3, 106,5 × 100 mm, sloty S1–S2 poziomu 3, dystanse 20 mm |
| DAQ do P03 | J1 B2B TSW-108-08-G-D-NA (P05 obok P03) | **J_BP2** IDC 2×10 kątowe, slot S2 (x = 80,0 mm); DAQ na tych samych pinach co P03 R6 J_BP2; 16 i 20 GND (rezerwa) |
| Zasilanie, DAQ_OK, VBAT | J2 LV05 (Mini-Fit 4p), J3 DAQOK (IDC 6p), J5 VSENSE (Mini-Fit 14p) | **J_BP1** IDC 2×5 kątowe, slot S1 (x = 26,5 mm): 5V_SYS na 2 i 4, DAQ_OK na 6, GND na 8 (rezerwa), VBAT_SENSE na 10 |
| 3V3_IO | LV05.3 → TP5 (tylko punkt kontrolny) | **nie wchodzi na P05**; wyjątek od S1 §5 („3V3_IO na ≥ 1 pinie”): logika P05 ma własne 3V3_DAQ z U12, więc zewnętrzne 3V3 nie miałoby odbiornika |
| Przewody | 5 wiązek + B2B | zostają J4 TAPS i J6 AUX (S1 §5), przy brzegu x = 0 |
| Punkty pomiarowe | TP1–TP16 | **J_SV1** 1×13 (S1: VBAT między GND, zasilania obok siebie i GND, okno, U4.18; GND na 1, 3, 7, 13) i **J_SV2** 1×13 (S2: sygnały DAQ i nadzór) — 20 kołków przez rezystory przy węźle R36–R55; TP1–TP5 tylko przy U1 (GND, ADC_REF, REGCAP_A/D, REFCAP) |
| R i C | THT MBB0207/metal film, 0603/0805/1210 | nowe **SMD 1206**; posiadane THT z rejestru tam, gdzie zostaje zapas (`docs/ZAKUPY.md`) |
| Rezystory precyzyjne R3–R8 | MBB0207 0,1 %, 25 ppm/K | **1206 0,1 %, 10 ppm/K** (propozycja Yageo RT1206BRB07…) — patrz „Okno DAQ_OK” |
| Rezystory precyzyjne R28, R29, R31–R35 | MBB0207 0,1 % | 1206 0,1 %, 25 ppm/K (RT1206BRD07…) |
| SW1 | C&K 7201SYCBE (dźwignia), HI = 2-1 + 5-4 | **E-Switch 100 DPDT ON-ON, kątowy M6** (decyzja 1.10; kod np. 100DP1T1B4M6RE do potwierdzenia), footprint z rysunku M6-DP (karta s. 11); styki jak w R2: HI = 2-1 + 5-4, LO = 2-3 + 5-6 (pin 6 wolny). Wersja z chmury: suwak C&K JS202011AQN |
| C1 | 470 µF / 16 V, D8 | **220 µF / 16 V** (decyzja 1.10: razem z P06 C3 ok. 486 µF na 5 V wobec 600 µF dla TSR 2-2450) |
| Arkusze | 8 | 9 (nowy `SERWIS`: listwy) |

**Wyjątki od „nowe = SMD 1206”:** R1 1 Ω (KNP01U-1R, 1 W leżący — udar ładowania C1 ok. 2,8 mJ przy 220 µF, posiadane MF0207 1R mają 0,6 W); C1 220 µF elektrolit radialny; C12/C13 22 µF w 1210 (1206 22 µF przy 4,4 V nie daje pewnie Ceff ≥ 10 µF z kroku 11 ODBIOR); diody i układy scalone bez zmian obudów.

**Posiadane części THT w P05:** R13 47k i R43 4,7k (MF0207 na stojąco), C32 KEMET C0G 1 n, D1–D3 1N4148, U5–U11 z przydziału. 10 k i 100 k MF0207 oraz K104K15 100 n nie mają zapasu po P02 R4, P09 R2 i P10 R2; kondensatorów foliowych (MKT 10 n / 100 n, WIMA 1 µF) P02 R4 zostawia po jednej sztuce, więc C2, C23, C16–C18, C25 i C26 są nowe 1206 (1.10; pierwsza wersja liczyła tylko P09/P10) — bilans w `docs/ZAKUPY.md`.

## Okno DAQ_OK — dlaczego 10 ppm/K

R2 liczyło okno dla MBB0207 (0,1 % + 25 ppm/K × 100 K) bez dodatku na lutowanie i starzenie rezystorów; dolny narożnik wychodził 4,7524 V przy regule 4,75 V, czyli **2,4 mV zapasu**. Rezystory cienkowarstwowe SMD przesuwają się przy lutowaniu i z czasem; karty Yageo RT nie dało się pobrać w chmurze (proxy), więc `verify_electrical.py` dolicza założone **0,1 % na rezystor** i klasę TCR z MPN w eksporcie:

| Rezystory okna R3–R8 | Dodatek | Dolny narożnik | Górny narożnik | 4,75–5,25 V |
|---|---|---:|---:|---|
| 25 ppm/K (podstawa R2) | 0 | 4,7524 V | 5,2344 V | tak |
| 25 ppm/K | 0,1 % | **4,7445 V** | 5,2425 V | **nie** (próba ujemna) |
| **10 ppm/K (R3)** | **0,1 %** | **4,7564 V** | **5,2304 V** | **tak** |

Zapas 5VA do narożników przy TSR 2-2450 (`electrical-checks.json`, `window.tsr_margin`): −2 %/25 °C +35,5 mV; −2 %/60 °C **+0,5 mV**; +2 %/25 °C +53,4 mV; +2 %/60 °C +18,4 mV. Przypadek −2 % w upale nadal jest na granicy, więc kryterium odbioru 5V_SYS 4,93–5,07 V przy 23 °C zostaje. Przy 10 ppm/K także REF5025AIDR (klasa standardowa) mieściłby się w regule — z zapasem 1,6 mV; U2 zostaje REF5025ID(R) według decyzji z 29.09.

## Kontrole

`python src/run_schematic.py` (Python KiCada; w chmurze `scripts/egrlab-docker python3 src/run_schematic.py`): schemat, tabele, ERC, netlista, trzy zestawy kontroli, PDF, `verification/QA.md`, manifest.

- ERC **0** na 9 arkuszach; netlista **466/466** pinów zgodnych z `parts.py`, 119 części, 111 sieci (R2: 421/421, 110 części).
- `verify_electrical.py` (obwód R2 dostosowany do S1): **21/21**, mutacje **12/12** — m.in. brak 3V3_IO, VBAT_SENSE na J_BP1.10, SW1 sprawdzany z geometrii footprintu (dźwignia łączy wspólne obu biegunów z polami na tym samym końcu), okno z klasą TCR z MPN.
- `verify_s1.py` (kontrakt S1, niezależny od generatora): **26/26**, mutacje **33/33** wykryte przez kontrolę docelową, próba zerowa czysta. Pinout J_BP1/J_BP2 dokładnie jak w zadaniu; DAQ na pinach P03 R6 J_BP2 (`reference/P03-R6-J_BP.csv` z gałęzi `p03-r6-pcb`, b094fa7); każda sieć dawnych J1/J2/J3/J5 na J_BP dokładnie raz (5V_SYS dwa razy, 3V3_IO wcale); nieparzyste piny GND; GND po obu stronach ADC_SCLK i MEAS_EN w taśmie; TAPS i AUX poza J_BP; listwy ≤ 13 kołków, GND na końcach (wewnątrz dozwolone), szyny tylko obok GND albo innej szyny i VBAT_SENSE tylko obok GND (1.10), rezystor przy węźle w klasie z S1 §6, pokrycie listy z ODBIOR; `J_BP.csv`/`SERWIS.csv` zgodne z netlistą; źródła i obudowy części; obwód R2 bez zmian.

## PCB (1.10.2026, `src/run_release.py`, KiCad 10.0.6 w Dockerze)

| Kontrola | Wynik | Raport |
|---|---|---|
| DRC świeży, wszystkie poziomy | 0 niepołączonych, 0 niezgodności ze schematem, 0 innych naruszeń; 4 × `lib_footprint_mismatch` (J_BP1, J_BP2, J_SV1, J_SV2: nadruk przycięty przez `silkscreen.py`, przyjęte jawnie) | `verification/drc.json` |
| Kontrole PCB (`verify_pcb.py`) | 30/30 | `verification/pcb-checks.json`, `QA-PCB.md` |
| Próby ujemne PCB | 31/31 z zerową | `verification/negative-controls.json` |
| Odsprzęganie U1 (droga po miedzi od pinu do pola) | wszystkie w limitach, mm (pin→kondensator droga/limit): 1→C4 2,28/3,0; 48→C7 2,73/3,0; 37→C5 2,74/3,0; 38→C5 2,74/3,0; 23→C8 2,74/4,0; 36→C9 2,62/3,0; 39→C10 2,06/3,0; 42→C11 2,68/3,0; 42→C12 3,15/6,0; 44→C13 5,29/6,0; 45→C13 4,79/6,0 | `pcb-checks.json` |
| Trasowanie | Freerouting 2.1.0 (40 przebiegów, 4 wątki, GND jako płaszczyzna B.Cu), piąta próba; planer dokańczania: 2 połączenia 3V3_DAQ (29,1 i 17,6 mm) i 6 GND; nieużyte końce zablokowanych wyprowadzeń przycięte (`trim_stubs.py`); pełne połączenie z wylewką: C32.2, J_BP1.9, U4.3, U4.6, U6.3, U7.3 (szprychy odcięte); 183 przelotki | `routing/attempts.json`, `completion-routes.json` |

**Jak powstało** (łańcuch P03 R6 przez P09 / P10 R2; opisy w nagłówkach skryptów): `placement.py` (U1 i jego kondensatory jawnie, kolumna filtrów C27–C34 w rastrze 2,65 mm, bufory U9 / U11 tuż przy U1, reszta przy swoich pinach, rezystory listew od spodu przy węzłach) → `route_critical.py` (miedź przy U1 i U3 przed routerem: odsprzęganie, wyprowadzenia sygnałów, wachlarz wejść, przelotki do wnętrza U1, wylewka GND wewnątrz pierścienia z 4 przelotkami, mostki 3V3 / 5VA po B.Cu) → `fanout_gnd.py` → `prepare_routing.py` (piny GND U1 poza listą routera; strefa routera tylko we wnętrzu pierścienia U1) → Freerouting → import, `cleanup.py --tidy`, `check_intrusion.py` (próba odpada, gdy miedź routera innej sieci wchodzi w obrys U1 albo jakakolwiek do wnętrza pierścienia) → `stitch.py` → planer `complete_routes.py` (próba odpada od razu przy > 12 przerwach; strefy planera: obrys U1 i U3, B.Cu pod częścią analogową; start z końca wyprowadzenia) → `silkscreen.py`.

**Decyzje (sporne oznaczone):**
1. **Sporne — reguła drobnego rastra:** odstęp 0,15 mm i tor 0,2 mm tylko między elementami, które oba dotykają obrysu U1 (LQFP-64, raster 0,5 mm) albo U3 (VSSOP-8, 0,65 mm); poza nimi S1 §3 (0,25 / 0,3 jak P02-R3). S1 dopuszcza LQFP, a przy 0,25 mm szczeliny między polami samych footprintów (0,2 / 0,15 mm) są naruszeniem DRC. JLCPCB: 0,1 / 0,1 mm. Reguły w `eda/P05.kicad_dru` (z `set_rules.py`), kontrola treści w `verify_pcb.py`.
2. **5V_SYS jako sygnał 0,3 mm** (ok. 150 mA: cewki 3 × 30 mA, R1 ok. 60 mA; spadek ok. 25 mV na 100 mm); klasa PWR 0,6 mm tylko dla 5VA_P05 — tor 0,6 mm nie wchodzi w raster 0,65 mm U3.8.
3. **Odsprzęganie U1** (tabela dróg w `pcb-checks.json`): 1 µF (REGCAP) i 22 µF (REFIN / REFCAP) od góry, bez przelotek; 100 nF od spodu pod korpusem, każdy przez własną przelotkę wewnątrz pierścienia (grubość ≤ 1,5 mm w BOM); REFCAP biegnie 0,2 mm wzdłuż końców pól pod C12 do C13; TP2–TP5 na odgałęzieniach 0,3 mm poza drogą odsprzęgania. AVCC pinu 1 łączy się z resztą po B.Cu (przelotka V1 przy pinie).
4. **Masa U1:** piny GND do wylewki F.Cu wewnątrz pierścienia (pełne połączenie), 4 przelotki do B.Cu; DOUT po F.Cu w prawo (P5-01).
5. **Bufory U9 / U11 przy U1** (wcześniej przy J_BP2): linie lokalne 4–15 mm, odgałęzienia magistrali J_BP2 ok. 35 mm — przy szybkościach SPI P05 dużo poniżej długości krytycznej.
6. **Kondensatory od spodu:** C5, C7, C8, C11 (100 nF) i C26 (10 nF) — uwaga w BOM: grubość ≤ 1,5 mm.
7. SW1 (E-Switch M6): tuleja i dźwignia za krawędzią x = 0; J4 / J6 z kotwami opasek przy krawędzi.

**Jak doszło do trasowania (1.10, 9 przebiegów):** strefy zakazane w DSN, w których leżą piny (obrys U1 / U3, B.Cu z kondensatorami 100 nF), zostawiały w routerze 20–105 przerw (3V3_DAQ prawie nietrasowane); bez stref router przechodził, ale skracał drogę przez wnętrze pierścienia U1. Obecnie: strefy routera tylko tam, gdzie nie ma pinów (wnętrze pierścienia na F.Cu, pasy B.Cu wokół U1), strefy planera osobno, a kontrola `check_intrusion.py` odrzuca próbę z obcą siecią w obrysie U1.

**Oględziny PDF (1.10, 5 stron, `output/previews/pcb-*.png`):** opis z liczbami z wydania; montaż 1:1 — napisy listew do 7 znaków, czytelne; F.Cu — wachlarz wejść, REFCAP pod C12, odgałęzienia TP; B.Cu — masa z mostkami 5VA / 3V3 pod U1; przymiarka — kółka Ø7. Bez uwag blokujących.

**Otwarte:** przymiarka 1:1 (SW1 w panelu, przewody TAPS / AUX), kod SW1 i C1 przy zakupie, recenzja lokalna; 11 oznaczeń ukrytych z braku miejsca (C10, C12, C14, C20, C25, C28, R5, R7, R11, R18, R33; na rysunku montażowym F.Fab są wszystkie); paczka produkcyjna dopiero po „scal”.

## Wymagania dla layoutu (sesja lokalna)

- J4 (TAPS), J6 (AUX) i SW1 od strony x = 0; dźwignia SW1 (E-Switch M6, tuleja i dźwignia równolegle do płytki) przez otwór w panelu przy x = 0 — położenie tak, by tuleja sięgała ścianki (makieta).
- J_BP1 w slocie S1 (środek x = 26,5 mm), J_BP2 w slocie S2 (x = 80,0 mm), pin 1 od strony mniejszego x. J_SV1 w x = 10–43 mm, J_SV2 w x = 63,5–96,5 mm; rezystory R36–R55 przy węzłach (SMD mogą być od spodu; R43 to posiadany MF0207 na stojąco — od góry). Przestawienie kołków: `src/parts.py` (listy SV1/SV2, `SV1_PIN`), potem `run_schematic.py` — `SERWIS.csv`, kontrole i odwołania w ODBIOR idą za nim.
- Odsprzęganie U1 według `Plytki/P05-R2-review/wip-layout-obrys-R1/` (opisy „Cx przy U1.nn” w arkuszu ADC zostają); kondensatory są teraz 1206 — wzór trzeba dopasować, dozwolone od spodu pod U1 tylko do 1,5 mm (100 n 1206; nie C12/C13 1210 o grubości 2,5 mm ani 1–2,2 µF 1206 o grubości do 1,6 mm). DOUT nie pod U1 po B.Cu (P5-01).
- Od spodu tylko SMD ≤ 1,5 mm, bez SOIC; najwyższe: SW1 ok. 11,4 mm (obudowa M6) i C1 ok. 11,2 mm — w limicie 16,5 mm.
- Szczegóły: `docs/MECHANIKA.md`.

## Otwarte punkty

- **SW1 (rozstrzygnięte 1.10):** E-Switch 100 w wersji kątowej M6 zamiast pionowego 100DP1T1B1M2REH (ok. 28 mm, ponad 16,5 mm poziomu 3; karta `reference/E-Switch-100-series.pdf`, s. 2, 6, 8, 11). Do potwierdzenia przy zakupie: dokładny kod (tuleja B4 bez gwintu — standard dla M6, albo B3 z gwintem i nakrętką na panel) i dostępność; footprint z rysunku M6-DP sprawdzić na wydruku 1:1 z próbką.
- **Pojemność 5V_SYS (rozstrzygnięte 1.10):** C1 = 220 µF (P06 C3 też 220 µF w rewizji S1) — razem ok. 486 µF wobec 600 µF dla TSR 2-2450; start kompletu i tak mierzyć na stole. MPN C1 (EEUFR1C221, D6,3 × 11,2 mm) do potwierdzenia. Budżet w `docs/INTEGRACJA.md` (ok. 538 µF) jest sprzed P02 R4 i decyzji.
- **Zapas z rejestru:** bilans w `docs/ZAKUPY.md` (1.10: z P02 R4); 10 k i 100 k MF0207 oraz K104 zużywają P02 R4, P09 R2 i P10 R2, P05 bierze je jako nowe 1206. Budżet dzielników kanałów (0,1 %, 25 ppm/K): `electrical-checks.json`, `channels.*.divider_budget`.
- R1 KNP01U-1R: odporność na impuls ok. 2,8 mJ (C1 220 µF) z karty.

## Pliki

- `eda/` — schemat KiCad 10 (9 arkuszy A3), biblioteki i **PCB** `P05.kicad_pcb` z regułami `P05.kicad_dru` (drobny raster U1 / U3).
- `output/pdf/P05-R3-PCB.pdf` (5 stron: opis, montaż 1:1, F.Cu, B.Cu, przymiarka), `output/svg/`, `output/previews/pcb-*.png`.
- `routing/` — wynik routera `P05.ses` i trasy dokańczające `completion-routes.json` (odtwarzanie: `run_release.py` bez `--new-route`), miedź krytyczna `critical.json`, raporty kroków.
- `output/pdf/P05-R3-schemat.pdf`, `output/previews/sch-*.png`.
- `docs/` — `J_BP.csv` i `SERWIS.csv` (kontrakty dla P12 i listew), BOM, `ZAKUPY.md`, `zakupy.csv`, `pinout.csv`, `interfejsy.csv`/`wiazki-BOM.csv` (TAPS, AUX), ODBIOR R3, MECHANIKA R3, INTEGRACJA, PROJEKT.
- `verification/` — ERC, netlista, `schematic-check.json`, `electrical-checks.json`, `s1-checks.json`, `QA.md`; PCB: `drc.json`, `pcb-checks.json`, `negative-controls.json`, `QA-PCB.md`; logi, manifest.
- `reference/` — `P05-R2.xml` (eksport R2 do porównania), `P03-R6-J_BP.csv`, `baseline.json`, karty.
