# P04 SAFE — R3, schemat w formacie S1

*5.10.2026. Pakiet na kopii łańcucha schematu `P04-R2.2-review/src` według `Plytki/Format-S1/zadania/ZADANIE-P04-S1.md` (decyzja użytkownika 5.10.2026: wariant pełny, P04 na 6. poziomie, klasa L). Zamknięty pakiet R2.2 bez zmian.*

**Status (5.10.2026): schemat R3 i PCB (sesja lokalna, gałąź `p04-r3-pcb`) do recenzji; paczka zamówieniowa `Plytki/P04-PCB-R3-zamowienie`.** Sekcja „PCB” niżej. Sprzętu nie zmontowano ani nie zmierzono.

Obwód R2.2 zostaje: watchdog CD74HC123 (U1), zatrzask ARM 74HC74 (U3), regeneracja SAFE_N przez 74HC14 (U2), bramki 74HC08 (U4–U7), bufory 74LVC125AD z Ioff i podwójnymi pulldownami (U8–U10), nadzorca MCP100-300 (U11), otwarte kolektory Q1–Q3 na SAFE_N, druga droga watchdoga SAFE_WD, R17 10 kΩ pod reset z P03. Zmieniają się złącza do innych płytek, punkty pomiarowe, typy części i wymiar. `verify_s1.py` sprawdza na eksportowanej netliście, że poza złączami J1–J8 i polami TP każdy pin ma tę samą sieć i wartość co w R2.2 (`reference/P04-R2.2.xml`), z dwiema jawnymi zmianami nazw.

## Zmiany R2.2 → R3

| Punkt | R2.2 | R3 |
|---|---|---|
| Płytka | 160 × 120 mm, 4 otwory, samodzielna | klasa L 160 × 100 mm, poziom 6 (sloty S1–S3), 12 otworów M3, dystanse 20 mm |
| Złącza | J1 LV04 i J2 SAFE (pigtaile z kotwami), J3–J6 IDC, J7 PG i J8 PANELSAFE (Mini-Fit) | **J_BP1** IDC 2×8 (S1, x = 26,5), **J_BP2** i **J_BP3** IDC 2×10 (S2 x = 80,0, S3 x = 133,5), kątowe obudowane, wszystkie nieparzyste GND, przez P12 |
| Nazwy sieci | SUP_N (J2.15), PG_3V3 (J7.1) | **SUP_N_OUT**, **P04_3V3** — nazwy z P12 (P03 R6 J_BP3.12, P02 R4 J_BP.15) |
| Drugi koniec PG/SAFE_N | P01 J5 | P02 R4 (Q7, zwora PG) przez P12; P07 łączy się z SAFE_N po nazwie |
| Punkty pomiarowe | TP1–TP15 | **J_SV1** 1×13, **J_SV2** 1×7, **J_SV3** 1×7 na krawędzi B; 19 kołków przez R43–R61 przy węzłach (mapa w `docs/ODBIOR.md`) |
| Rezystory | MFR-25 THT leżące | nowe **SMD 1206** RC1206FR-07… (rejestr nie ma zapasu tych wartości) |
| Kondensatory | K104K15 100 n THT, K102J15 1 n, EEUFR1H100, 2 × MKS2 63 V | 100 n **X7R 1206**; posiadane: C1 MKS2 1 µF / 100 V, C3 EEU-EB1J100SH, C18 C320C102J1G5TA; C2 nowy MKS2 jak w R2.2 |
| U8–U10 | SO14 na adapterach Kamami, C15–C17 na adapterach | **SOIC-14 lutowane wprost** (S1 §9); C15–C17 na płytce jako druga 100 n przy U8–U10 |
| Arkusze | 6 (w tym `CON`) | 7: `CON` → **`ZLACZA`** (nazwa zarezerwowana w Windows, `docs/CHMURA.md`), nowy **`SERWIS`** |

## Pinout J_BP (pełny: `docs/J_BP.csv`, kierunki widziane z P04)

| Pin | J_BP1 (S1) | J_BP2 (S2) | J_BP3 (S3) |
|---|---|---|---|
| 2 | PANEL_3V3 → P11 | MOTOR_PERMIT → P07 | SENSOR_ENABLE ← P03 |
| 4 | MECH_OK ← P11 | PWM_OUT → P07 | CORE_LINK ← P03 |
| 6 | STOP_NC_OUT ← P11 | ARM_CLK → P07 | HW_ARMED → P03 |
| 8 | ARM_CONTACT ← P11 | DRIVE_OK ← P07 | 5V_SYS (tylko kołek) |
| 10 | SENSOR_PERMIT → P08 | 3V3_IO (zasilanie) | 3V3_IO (zasilanie) |
| 12 | SENSOR_OK ← P08 | PSU_OK ← P02 | SUP_N_OUT ← P03 |
| 14 | TEST_KEY ← P11 | P04_3V3 → P02 | PWM ← P03 |
| 16 | DAQ_OK ← P05 | SAFE_N (węzeł OC) | HEARTBEAT ← P03 |
| 18 | — | PG_LINK (pętla P02) | MCU_ARM ← P03 |
| 20 | — | PG_SEND (pętla P02) | INTERLOCK → P03 |

Nieparzyste: GND. Te same numery pinów co u partnera tam, gdzie się dało: J_BP1 2/4/6/8/14 = P11 J_P12, J_BP2 12/16/18 = P02 R4 J_BP, J_BP3 12–20 = P03 R6 J_BP3 — taśmy na P12 idą wtedy prosto. Sieci do P07 (DRIVE) i P08 (SENSOR) mają nazwy z R2.2 J3/J4 (i z P08 R1 W2); **P07 jeszcze nie istnieje — te sieci czekają na P07**.

## Kontrole

`python src/run_schematic.py` (w chmurze `scripts/egrlab-docker python3 src/run_schematic.py`, ok. 20 s): schemat, tabele, ERC, netlista, cztery zestawy kontroli, PDF, `verification/QA.md`, manifest.

- ERC **0** na 7 arkuszach; netlista **397/397** pinów zgodnych z `parts.py`, 100 części, 95 sieci.
- `verify_electrical.py` (kontrole R2.2 z pinami przeniesionymi na J_BP): **22/22**, mutacje **16/16** — m.in. pełne tabele prawdy INTERLOCK / SAFE_N / HW_ARMED / MOTOR_PERMIT / PWM_OUT / SENSOR_PERMIT (131 072 wierszy), druga droga watchdoga bez Q1, sekwencje ARM bez samoczynnego uzbrojenia, SAFE_N tylko z jednym podciąganiem i kolektorami (rezystor kołka serwisowego pominięty jawnie), 3V3 wychodzi z płytki tylko przez R38/R39/R40.
- `verify_values.py`: **10/10**, mutacje **24/24** (wartości i MPN S1, rogi rezystorów panelu i SAFE_N).
- `verify_reset.py` z mapą części **P03 R6**: **7/7**, mutacje **4/4** (R17 10 kΩ, VIL/VIH na U9.5, SUP_N_OUT na J_BP3.12 po obu stronach).
- `verify_s1.py` (kontrakt S1 i P12, niezależny od generatora): **34/34**, mutacje **42/42** wykryte przez kontrolę docelową, próba zerowa czysta. Sprawdza m.in.: pinout i footprint każdego J_BP; nieparzyste GND; każda sieć dawnych J1–J8 na J_BP dokładnie raz (3V3_IO dwa razy); te same piny co partner; **każda z 19 sieci „czeka na P04” w `reference/P12-kontrakty.json` kończy się na P04 dokładnie raz i po dołączeniu P04 ma jeden nadajnik (albo pętlę)**; brak obcych nazw; nazwy DRIVE/SENSOR jak w R2.2 i P08 R1; zgodność `J_BP.csv` i `SERWIS.csv` z netlistą; listwy ≤ 13 kołków z GND na końcach, rezystor przy węźle w swojej klasie, SAFE_N i ARM_BUTTON_N tylko obok GND, szyny tylko obok GND lub szyn; pokrycie TP1–TP15 z R2.2; obudowy S1; obwód R2.2 bez zmian.
- kicad-cli wypisuje „schemat posiada błędy numeracji” — oznaczenia `J_BP1…3`, `J_SV1…3` (nazwy formatu S1); ERC tego nie zgłasza.

## Decyzje (sporne oznaczone)

1. **Trzy J_BP zamiast dwóch z budżetu S1 §8:** 25 sygnałów (19 czekających na P04 w P12 + 6 do P07/P08) i zasilanie nie mieszczą się w 2 × 10 parzystych pinach bez wyjątków od GND na nieparzystych; klasa L ma trzy sloty. J_BP1 jako 2×8 (osiem sygnałów).
2. **Sporne — SAFE_N w `J_BP.csv` jako `in`:** P04 ma podciąganie R4 i własne kolektory Q1–Q3, ale dla kontraktu P12 nadajnikiem jest P02 R4 (`out`); dwa `out` kontrola P12 uznałaby za konflikt. Uwaga w kolumnie `uwagi`.
3. **Sporne — U8–U10 SOIC wprost, bez adapterów:** S1 §9 dopuszcza adaptery tylko tam, gdzie jest miejsce; SOIC na płytce z fabryki jest prostszy i niższy (tak samo P06 R2). Adaptery z przydziału P04 zostają w rejestrze. C15–C17 przeniesione na płytkę, żeby obwód był identyczny z R2.2 — mogą zostać DNP.
4. **5V_SYS na jednym pinie (J_BP3.8), tylko do kołka J_SV3.2** — jak J1.1 → TP13 w R2.2; P04 nie pobiera 5 V, więc reguła „5V_SYS na ≥ 2 pinach” (S1 §5, dla zasilania) nie ma tu zastosowania.
5. **3V3_IO na dwóch pinach (J_BP2.10, J_BP3.10):** pobór kilka–kilkanaście mA, ale drugi pin daje zapas styku i masę obok.
6. **Klasy rezystorów kołków:** 1 kΩ szyny i węzły napędzane bramką; 10 kΩ węzły pasywne SAFE_N (R4 10k / R5 100k) i ARM_BUTTON_N (R2 10k). **Wyjątek Q1_B 1 kΩ:** próba E21 zwiera kołek do GND i musi zatkać Q1 (z 10 kΩ baza zostaje na ok. 1,57 V, z 1 kΩ ok. 0,30 V). **SAFE_N i ARM_BUTTON_N stoją tylko między kołkami GND:** zsunięta sonda zwierająca je z szyną podniosłaby SAFE_N mimo otwartego STOP albo dała zbocze ARM.
7. **Posiadane ostatnie sztuki z rejestru:** C1 MKS2 1 µF / 100 V (5 %), C3 EEU-EB1J100SH, C18 C320C102J1G5TA — bilans w `docs/ZAKUPY.md`. C2 zostaje foliowy (nowy, jak w R2.2), bo filtr ARM i tak wymaga kwalifikacji przycisku.

## PCB (5.10.2026, sesja lokalna; `src/run_release.py`, KiCad 10.0.6 w Dockerze)

| Kontrola | Wynik | Raport |
|---|---|---|
| DRC świeży, wszystkie poziomy, z parity | 0 niepołączonych, 0 niezgodności ze schematem, 0 innych naruszeń; 6 × `lib_footprint_mismatch` (J_BP1–3, J_SV1–3: nadruk przycięty przez `silkscreen.py`, pola równe bibliotece — przyjęte jawnie) | `verification/drc.json` |
| Kontrole PCB (`verify_pcb.py`) | 31/31 | `verification/pcb-checks.json`, `QA-PCB.md` |
| Próby ujemne PCB | 33/33 z próbą zerową | `verification/negative-controls.json` |
| Otwory M3 i strefy Ø7 | 12 NPTH 3,2 mm w punktach S1, bez miedzi i części w Ø7 | `pcb-checks.json` |
| J_BP1–J_BP3 | IDC 2×8 / 2×10 / 2×10 kątowe, środki x = 26,5 / 80 / 133,5, wtyk w y = 0, pin 1 od mniejszego x, nieparzyste GND, pinout = `docs/J_BP.csv` | `pcb-checks.json` |
| J_SV1–J_SV3 | 1×13 / 1×7 / 1×7 w x 10–43 slotu, pin 1 przy większym x, GND na końcach, rezystor przy węźle ≤ 10 mm (R57 5V_SYS: od przelotki wyjścia), etykiety węzłów ≤ 7 znaków | `pcb-checks.json` |
| Części od spodu / wysokości | od spodu żadnych (wszystko od góry, U8–U10 SOIC też); najwyższy C1 13,0 mm ≤ 16,5 mm | `src/heights.py` |
| Zasilanie ≥ 0,4 mm | 3V3_IO (456 mm), P04_3V3 (29,8 mm), PANEL_3V3 (15,2 mm), 5V_SYS (25,1 mm): każda ścieżka 0,4 mm (klasa PWR) | `pcb-checks.json` |
| SUP_N_OUT | J_BP3.12 → U9.5 12,8 mm miedzi, 1 przelotka, R17 3,6 mm od U9.5; obok GND J_BP3.11 / .13; masa (wylewka, grzebień, pola) na drugiej warstwie pod 73 % długości | `pcb-checks.json` |
| Watchdog | WD_RC 9,9 mm, WD_C 6,6 mm, zablokowane, F.Cu, bez przelotek; C1 na U1.15 / U1.14 | `pcb-checks.json` |
| SAFE_N | C18 3,3 mm i R5 3,7 mm od U2.11; R40 / R41 / R42 / R3 przy J_BP1, R38 / R39 przy J_BP2 | `pcb-checks.json` |
| Odsprzęganie | 100 nF przy każdym układzie: pole 3V3_IO 2,5–3,9 mm miedzi od pinu VCC; masa: kondensator → pin GND układu 3,8–21,4 mm przez miedź GND (limit 1,3 × prosta + 3 mm, `gndpath.py`) | `pcb-checks.json` |
| Nadruk | wszystkie napisy ≥ 1,0 mm / 0,15 mm, pin 1 każdego złącza, „P04 R3 S1-L S1-S3”, KRAWEDZ A / B; 23 oznaczenia ukryte z braku miejsca (na rysunku montażowym z F.Fab) | `routing/silkscreen.json` |
| Trasowanie | Freerouting 2.1.0 (GND jako płaszczyzna B.Cu), dziewiąty przebieg łańcucha, pierwsza próba; planer dokańczania 2 trasy (DAQ_OK, PSU_OK); 204 przelotki; ścieżki sygnałowe 2741 mm F.Cu / 3127 mm B.Cu | `routing/attempts.json`, `completion-routes.json` |

**Jak powstało** (łańcuch P05 R3 / P03 R6, wartości płytki w `src/board.py`): `placement.py` (złącza z S1; DIP w rzędzie y 34: S1 U5 / U4 / U3, S2 U7 / U2 / U6, S3 U1; U10 pod J_BP2, U9 z pinem 5 pod J_BP3.12, U8 obok; 100 nF DIP nad korpusem, pozostałe przy pinie VCC; bierne przy swoich pinach) → `route_critical.py` (miedź zablokowana przed routerem: wyjścia zasilania 0,4 mm, SUP_N_OUT, RC watchdoga, łącza 3V3_IO do 100 nF, grzbiety GND pod DIP) → `fanout_gnd.py` (belki GND pod SOIC, przelotki 100 nF SOIC z łączem do belki, grzebienie GND pod J_BP) → `prepare_routing.py` (strefy routera bez pinów wokół SUP_N_OUT) → Freerouting → import, `cleanup.py --tidy`, `stitch.py`, planer `complete_routes.py` (+ `--ties`), `stitch.py --targeted`, `cleanup.py`, `trim_stubs.py` (też nieużyte przelotki wyjść) → `silkscreen.py`. Odtworzenie: `scripts/egrlab-docker python3 src/run_release.py` (odtwarza `routing/P04.ses` i `completion-routes.json`); nowe trasowanie `--new-route`.

**Decyzje (sporne oznaczone):**
1. **Sporne — wyjścia zasilania pod korpusem J_BP:** piny 3V3_IO / P04_3V3 / 5V_SYS są w parzystym rzędzie IDC (bliżej krawędzi A), a między polami GND rzędu nieparzystego (0,84 mm) mieści się ścieżka 0,3 mm, nie 0,4 mm. Wymaganie 0,4 mm spełnione bez przewężeń: po B.Cu w stronę krawędzi A (pasy y 5,0–6,5 mm pod korpusem złącza), do końca złącza i w górę; 25–36 mm zamiast kilku. Skutek: R39 (P04_3V3) stoi 13 mm od J_BP2.14 (kontrola: ≤ 15 mm), R57 przy przelotce wyjścia 5V_SYS. Alternatywa: przewężenie 0,3 mm na ok. 1,5 mm między polami GND (wyjątek od 0,4 mm).
2. **Wszystkie części od góry** (S1-2 dopuszcza SMD ≤ 1,5 mm od spodu): płytka ma miejsce, montaż jednostronny; w zamówieniu bez nadruku od spodu.
3. **SUP_N_OUT z jedną przelotką:** pod J_BP3 F.Cu zajmuje grzebień GND, więc wyjście z J_BP3.12 idzie po B.Cu między pinami GND 9 / 11, przelotka 3 mm przed U9; pod odcinkiem F.Cu strefa routera bez innych ścieżek na B.Cu (przebieg 5: INTERLOCK przeciął tam masę, odniesienie 50 %).
4. **Masa odsprzęgania DIP:** VCC i GND są w przeciwnych narożnikach (pin 14 / 7, U1 16 / 8); w przebiegach 3–4 droga masy przez pociętą płaszczyznę B.Cu miała 35–130 mm. Teraz grzbiet GND 0,4 mm po B.Cu wzdłuż osi korpusu (20–23 mm, pod podstawką), kondensator nad korpusem. SOIC: przelotka 100 nF połączona po B.Cu z przelotką belki GND przy pinie 7.
5. **Etykiety listew** pełnymi nazwami węzłów, skrócone do 7 znaków (`ARM_BTN`, `LSUP_N`, `INTRLCK`, `MOT_PRM`, `SEN_PRM`, `PNL_3V3`); ODBIOR i SERWIS.csv mają pełne nazwy.
6. 23 oznaczenia ukryte z braku miejsca przy SOIC i rezystorach domyślnych (lista w `routing/silkscreen.json`, na rysunku montażowym F.Fab są wszystkie).

**Oględziny PDF (5.10, 5 stron, `output/previews/pcb-*.png`):** opis z liczbami z wydania; montaż 1:1 — etykiety listew czytelne, pin 1 złączy, nazwa płytki; B.Cu — wyjścia zasilania pod J_BP2 / J_BP3, reszta głównie masa. Bez uwag blokujących.

## Dokumenty

`docs/J_BP.csv` (kontrakt dla P12), `docs/SERWIS.csv`, `docs/ODBIOR.md` (formularz R2.2 z mapą TP → kołki i zmienionymi E04/E18/E21/E22), `docs/MECHANIKA.md` (wymagania dla layoutu), `docs/PROJEKT.md` i `docs/KONTRAKT-RESET.md` (R2.2 z notą R3), `docs/ZAKUPY.md` i `docs/zakupy.csv`, `docs/BOM.csv`, `docs/parts.json`, `docs/netlist-pinowa.csv`. Schemat: `output/pdf/P04-R3-schemat.pdf`. PCB: `eda/P04.kicad_pcb`, `output/pdf/P04-R3-PCB.pdf` (5 stron: opis, montaż 1:1, F.Cu, B.Cu, przymiarka), `routing/` (wynik routera, trasy dokańczające, raporty kroków), `verification/QA-PCB.md`.

## Pytania ze schematu — decyzje użytkownika (5.10.2026, przyjęte rekomendacje)

1. **5V_SYS na J_BP3.8 zostaje** (kołek J_SV3.2 pokazuje obecność 5 V z P12).
2. **U8–U10 SOIC lutowane wprost, C15–C17 zostają na płytce** (druga 100 nF przy każdym buforze, obsadzone).
3. **Limit wysokości nad poziomem 6: 16,5 mm**; C1 MKS2 ok. 13 mm — w limicie (sprawdzić przy przymiarce).

## Otwarte (poza tym zadaniem)

1. **Przejściówka P00 → J_BP1–J_BP3** do odbioru pojedynczej P04 R3 na P00 (wiązka P00 R3 jest pod złącza R2.2) — osobne zadanie.
2. **Ostatnie posiadane C1 / C3 / C18** przydzielone P04 — czy P08 R2 (równolegle) ich nie bierze? (pytanie 3 ze schematu, bez decyzji w tym zadaniu).
3. **Zbocze SUP_N_OUT na U9.5** (≤ 10 ns/V) przy drodze taśma–P12–taśma — tylko pomiarem przy odbiorze P04/P12.
