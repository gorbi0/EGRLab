# P06 I-LOGGER — R2, schemat w formacie S1

*1.10.2026. Pakiet na kopii łańcucha `P06-R1-review/src` według `Plytki/Format-S1/zadania/ZADANIE-P06-S1.md` (decyzje użytkownika 1.10.2026: klasa 2/3, bocznik 2512 Kelvin, BYPASS na panelu, C3 220 µF). Zamknięty pakiet R1 bez zmian.*

**Status: schemat R2 po przeglądzie lokalnym, PCB R2 po recenzji niezależnej i poprawkach (2.10)** — sekcja „PCB” niżej. Sprzętu nie zmontowano ani nie zmierzono.

Obwód R1 zostaje: INA240A2 z filtrem R1/R2 10 Ω, dzielnik R3/R4 1:2, MCP6022, MCP3201, nadzorcy MCP120, bufory 74LVC125 z Ioff, logika LOGGER_CURRENT_OK, R21 (prąd zwilżania styku statusu BYPASS). Zmieniają się złącza do innych płytek, bocznik, punkty pomiarowe i typy części. `verify_s1.py` sprawdza na eksportowanej netliście, że poza J1/J2, bocznikiem i polami testowymi każdy pin obwodu R1 ma tę samą sieć co w R1 (`reference/P06-R1.xml`).

## Zmiany R1 → R2

| Punkt | R1 | R2 |
|---|---|---|
| Płytka | 120 × 100 mm, 2 × 70 µm, samodzielnie mocowana | klasa 2/3, 106,5 × 100 mm, sloty S1–S2 poziomu 4, dystanse 20 mm, 35 µm |
| Zasilanie i ILOG | J1 LV06 (Mini-Fit 4p, 200 mm) i J2 ILOG (taśma 8 żył do P03) | **J_BP** IDC 2×8 kątowe, slot S2 (x = 80,0 mm): ADC_SCLK 2, ADC_DOUTA 4 (jak J_BP2 płytek P03 R6 i P05 R3), CS_ILOG_N 6, LOGGER_CURRENT_OK 8, 5V_SYS 10 i 12, 3V3_IO 14, nieparzyste i 16 GND |
| Przewody | 5 wiązek | zostają J3 ISERIES, J4 BYPASS (tor mocy), J5 status BYPASS — przy brzegu x = 0 |
| Bocznik RSH1 | PBV-R005-F1-0.5 THT, 3 W | **SMD 2512 Kelvin 5 mΩ 1 %**, Vishay **WSK25125L000FEA**, footprint lokalny `P06:R_Shunt_Vishay_WSK2512_T1.19mm_SenseE1.70` (pady 1/4 prądowe, 2/3 pomiarowe; przegląd 1.10) |
| SW1 BYPASS | NKK S6A | ogólny **DPDT ON-ON ≥ 10 A DC** z oczkami, na panelu; MPN do potwierdzenia |
| Punkty pomiarowe | TP1–TP15 | **J_SV1** 1×7 (S1: węzły analogowe przez 10 kΩ) i **J_SV2** 1×13 (S2: szyny i logika); 14 kołków przez rezystory przy węźle R25–R38 |
| R3/R4 | 5,1 kΩ 0,1 % THT | **5,11 kΩ 0,1 % 1206, 25 ppm/K** (zamiana 1:1 z listy 2); dzielnik 1:2 bez zmian, obciążenie INA240 10,22 kΩ |
| C3 | 470 µF / 16 V D8 | **220 µF / 16 V** D6,3 (decyzja 1.10); impuls ładowania przez R6 ok. 3,0 mJ (było 6,5 mJ) |
| C1 | 470 nF PET | 470 nF X7R 1206 (τ nominalnie 1,201 ms, 132,5 Hz; z tolerancją X7R 0,92–1,39 ms) |
| C4/C5 | 4,7 µF elektrolit D5 | 4,7 µF X7R 1206 25 V (MCP1525: CL 1–10 µF; MCP1702: ceramika X7R) |
| R i C | THT DIN0207, 0805 | nowe **SMD 1206**; R11 47 kΩ z rejestru (MF0207 na stojąco) — `docs/ZAKUPY.md` |
| Arkusze | 6 | 7 (CONNECT: J_BP; nowy SERWIS: listwy) |

**Wyjątki od „nowe = SMD 1206” (S1 §1/§9):**
- **RSH1** 2512 z czterema polami — tor 5–6 A i pomiar Kelvina (decyzja 28.09/1.10).
- **R6** 1 Ω / 1 W KNP01U-1R leżący (DIN0411) — rezystor mocy jak R1 w P05 R3; impuls ładowania C3 ok. 3 mJ, a posiadany MF0207 1R ma 0,6 W.
- **R21** 39 Ω PR02 2 W leżący (footprint `R_PR02_P17.78` z P02 R4). Wydziela 0,64 W przy 5,00 V i 0,71 W przy 5,25 V. W 2512 1 W pracowałby na ok. 70 % mocy z gorącym punktem na laminacie obok toru analogowego; PR02 ma 36 % obciążenia i stoi 3–5 mm nad płytką. 2512 2 W to część specjalna. **Decyzja użytkownika 1.10: zostaje THT (PR02).**
- **C3** elektrolit radialny 220 µF.
- **D1** 1N5819 (DO-41) i **D2** BAT85 (DO-35), układy scalone — obudowy jak w R1 (SOIC tylko od góry).

## Kontrole

`python src/run_schematic.py` (Python KiCada; w chmurze `scripts/egrlab-docker python3 src/run_schematic.py`, ok. 17 s): schemat, tabele, ERC, netlista, trzy zestawy kontroli, PDF, `verification/QA.md`, manifest.

- ERC **0** na 7 arkuszach; netlista **243/243** pinów zgodnych z `parts.py`, 74 części, 54 sieci (1.10 po przeglądzie lokalnym: J3 bez pustych pól 3/4) (R1: 6 arkuszy, 70 części).
- `verify_electrical.py` (kontrole R1 dostosowane): **33/33**, mutacje **30/30** — m.in. J_BP i dojście każdego sygnału do tego samego elementu co w R1, dzielnik 5,11 kΩ 0,1 %, C5/C4 z obniżeniem X7R (C5 efektywnie 2,5–5,9 µF w oknie 1–10 µF), C3 220 µF, R6 1 W, R21 2 W ≥ 2 × moc, 3V3_IO tylko do J_BP i kołka, tabela prawdy READY z eksportu.
- `verify_s1.py` (kontrakt S1, niezależny od generatora): **27/27**, mutacje **37/37** wykryte przez kontrolę docelową, próba zerowa czysta. Pinout J_BP dokładnie jak w zadaniu; ADC_SCLK/ADC_DOUTA na pinach 2/4 jak J_BP2 w `reference/P03-R6-J_BP.csv` (gałąź `p03-r6-pcb`, b094fa7) i `reference/P05-R3-J_BP.csv`; kierunki w `J_BP.csv` przeciwne do P03 R6; każda sieć dawnych J1/J2 na J_BP dokładnie raz (5V_SYS dwa razy); nieparzyste piny GND; J3/J4/J5 i Kelvin poza J_BP; listwy ≤ 13 kołków, GND na końcach, rezystor przy węźle w klasie z S1 §6, zasada sąsiedztwa szyn, pokrycie TP1–TP15 z R1; `J_BP.csv`/`SERWIS.csv` zgodne z netlistą; RSH1: 4 pola, pola prądowe (dwa największe) ECU_P1/EGR_P1, pomiarowe K_PLUS/K_MINUS po tej samej stronie — z geometrii footprintu; C3 220 µF; źródła i obudowy części; obwód R1 bez zmian.
- kicad-cli wypisuje „schemat posiada błędy numeracji” — dotyczy oznaczenia `J_BP` bez numeru (nazwa z zadania, jak w P02 R4); ERC tego nie zgłasza.

## Listwy serwisowe (krawędź B)

| J_SV1 (S1, x = 10–43) | Sieć | Rezystor | J_SV2 (S2, x = 63,5–96,5) | Sieć | Rezystor |
|---|---|---|---|---|---|
| 1 | GND | — | 1 | GND | — |
| 2 | I_L_OUT | R25 10k | 2 | 5V_SYS | R29 1k |
| 3 | ADC_AIN | R26 10k | 3 | 5VA_P06 | R30 1k |
| 4 | GND | — | 4 | 3V3_P06 | R31 1k |
| 5 | REF_BUF | R27 10k | 5 | GND | — |
| 6 | REF25 | R28 10k | 6 | 3V3_IO | R32 1k |
| 7 | GND | — | 7 | SUP3_N | R33 10k |
| | | | 8 | SUP5_N | R34 10k |
| | | | 9 | SHUNT_ENABLED | R35 1k |
| | | | 10 | LOGGER_CURRENT_OK | R36 1k |
| | | | 11 | CS_LOCAL_N | R37 1k |
| | | | 12 | CLK_LOCAL | R38 1k |
| | | | 13 | GND | — |

Szyny stoją tylko obok GND, innej szyny albo linii za 10 kΩ, która nie jest węzłem analogowym (3V3_IO obok SUP3_N). Węzły analogowe są na osobnej listwie, poza sąsiedztwem szyn. I_L_OUT ma 10 kΩ, choć zadanie wymienia go tylko na liście węzłów: to wyjście INA240, a 10 kΩ odcina pojemność toru do kołka od wyjścia wzmacniacza (multimetr 10 MΩ: błąd 0,1 %). SUP5_N ma 10 kΩ według zadania, choć na P06 jest wyjściem bufora U6A (w P05 R3 analogiczny P05_SUP5_N ma 1 kΩ) — 10 kΩ nic nie psuje. Kolejność w listwie może zmienić layout: `src/parts.py` (listy SV1/SV2), potem `run_schematic.py`.

## Wymagania dla layoutu (sesja lokalna)

- **Strona panelu (x = 0):** J3 ISERIES, J4 BYPASS i J5 status BYPASS przy brzegu x = 0 (S1 §7: ISERIES najkrótszą drogą), pola PTH J3 i J4 tuż przy RSH1. Pigtaile jak w R1: otwory 2,4 mm / pady 4,5 mm dla 2,5 mm², 1,1 / 2,2 mm dla AWG22, dwa otwory kotwy 3,2 mm 12 mm od rzędu.
- **Tor 5–6 A na miedzi 35 µm (S1 §3):** od J3 przez pola prądowe RSH1 do J4 jako pola ≥ 4 mm szerokości na obu warstwach, zszyte przelotkami, możliwie krótko (R1: 6 mm / 70 µm). Bez przelotek w samym polu RSH1 i bez innych sieci pod bocznikiem.
- **Kelvin:** ścieżki od pól pomiarowych 2/3 RSH1 do R1/R2 i dalej do U1.8/U1.1 osobno, parą, z dala od toru mocy i R21; R1/R2 i U1 blisko bocznika. Żadnego złącza między Kelvinem a INA240.
- **J_BP** w slocie S2, środek x = 80,0 mm, pin 1 od strony mniejszego x, strona wtyku równo z krawędzią A; pas y = 0–10 mm tylko na długości złącza.
- **J_SV1** w x = 10–43 mm, **J_SV2** w x = 63,5–96,5 mm, kątowe, kołki ok. 6 mm za krawędzią B; rezystory R25–R38 **przy węzłach** (SMD, mogą być od spodu). Nadruk: nazwa sieci przy każdym kołku, czytelna od strony B.
- **Poziom 4:** od góry ≤ 16,5 mm (najwyższe: C3 ok. 11,2 mm, U2/U3 w podstawkach ok. 8 mm, R21 leżący ok. 9 mm z odstępem); **od spodu tylko SMD ≤ 1,5 mm, bez SOIC** (U1, U5, U6 od góry); wyprowadzenia THT przycięte do ≤ 1,5 mm. Osiem otworów M3 (x = 4,0 / 49,0 / 57,5 / 102,5; y = 14,0 / 86,0), strefa Ø 7 mm.
- **R21** odsunięty od RSH1, U1 i U10 (gorący element); nad nim nie prowadzić taśmy.
- Szczegóły: `docs/MECHANIKA.md`.

## PCB (1.10.2026, poprawki po recenzji 2.10.2026; `src/run_release.py`, KiCad 10.0.6 w Dockerze)

| Kontrola | Wynik | Raport |
|---|---|---|
| DRC świeży, wszystkie poziomy | 0 niepołączonych, 0 niezgodności ze schematem, 0 innych naruszeń; 3 × lib_footprint_mismatch (J_BP, J_SV1, J_SV2 — nadruk przycięty przez `silkscreen.py`, przyjęte w `verify_pcb.py`) | `verification/drc.json` |
| Kontrole PCB (`verify_pcb.py`) | **34/34** | `verification/pcb-checks.json`, `verification/QA-PCB.md` |
| Próby ujemne PCB | **37/37** z zerową | `verification/negative-controls.json` |
| Tor prądu silnika | ECU_P1 / EGR_P1 na F.Cu i B.Cu (F.Cu 435,6 / 230,0 mm²), ≥ 4 mm na całej drodze J3–J4 (wypełnienie zwężone o 2 mm zostaje jednym kawałkiem), przelotki zszywające 15 / 12, pola J3 / J4 na szprychach 4 × 2 mm (2.10), pola RSH1 pełne | `pcb-checks.json` |
| Para Kelvina | K_PLUS 10,0 mm, K_MINUS 4,18 mm do R1 / R2, dalej 4,491 / 4,491 mm do U1.8 / U1.1; tylko F.Cu, bez przelotek; linie najwyżej 4,2 mm od siebie | `pcb-checks.json` |
| R21 i U10 | R21 ≥ 40,88 mm od RSH1, U1, U2, U3, U10; C5 3,76 mm od U10.2 (karta: ≤ 5 mm) | `pcb-checks.json` |
| Blok analogowy (recenzja 2.10, F2 / F3) | między rzędami nóżek U2 / U3 (obie warstwy) i między nimi oraz pod dolnymi pinami U2 (B.Cu) tylko masa — strefy routera `board.ANALOG_KEEPOUT` | `pcb-checks.json` |
| Powrót masy odsprzęgania (nowa kontrola, `src/gndpath.py`) | droga po miedzi GND od padu masy kondensatora do pinu GND jego układu ≤ 1,3 × odległość w linii prostej + 3 mm, dla 15 kondensatorów: 3,2–17,6 mm (przed recenzją C15 43, C2 43, C16 40, C12 58 mm); wyjątek jawny: C6 → U1.2 13,2 mm (limit 14) | `pcb-checks.json` |
| Nadruk | wszystkie napisy ≥ 1,0 mm, linia ≥ 0,15 mm (minimum JLCPCB; DRC pilnuje) | `pcb-checks.json` |
| Trasowanie | Freerouting 2.1.0, próba 1 z 1, 144 przelotki; jeden tor masy z planera (C12 → U7.7, `routing/return-ties.json`) | `routing/attempts.json` |

**Jak powstało** (łańcuch P05 R3 z dodatkami dla toru mocy; opisy w nagłówkach skryptów): `placement.py` (końcówki J3 / J4 / J5 w jednej kolumnie przy x = 0, RSH1 tuż przy J3, R1 / R2 i U1 na przedłużeniu pary Kelvina, tor analogowy U2 / U3 / U10 w prawo, bufory U5 pod J_BP, logika READY i zasilanie po prawej, R21 w lewym dolnym rogu, rezystory listew od spodu przy węzłach) → `route_critical.py` (wylewki ECU_P1 / EGR_P1 na obu warstwach z 27 przelotkami, para Kelvina, strefa zakazana pod bocznikiem na B.Cu) → `fanout_gnd.py` → `prepare_routing.py` (wylewki mocy jako strefy routera, sieci prądowe i Kelvina poza listą routera, strefy routera przy boczniku i między liniami Kelvina — tylko z pinami sieci zablokowanych) → Freerouting → import (GND na F.Cu z otworem nad bocznikiem), `cleanup.py --tidy`, `check_intrusion.py` (próba odpada, gdy obca miedź routera wchodzi w obrys RSH1 albo między linie Kelvina) → `stitch.py` → planer `complete_routes.py` → `trim_stubs.py` → `silkscreen.py`.

**Decyzje (sporne oznaczone):**
1. **Sporne — J3 2 pola, J4 raster 7,62 mm (przegląd lokalny 1.10):** z wymiarami R1 (J3 4 pola, J4 17,78 mm) trzy końcówki zajmują 81 mm krawędzi x = 0, a między strefami M3 jest 65 mm. Puste pola 3/4 J3 usunięte, J4 ma raster J3. Wiązki W3 / W4 bez zmian, zmienia się tylko rozstaw lutów na P06.
2. **J3 numerowany od drugiego końca:** w kolumnie przy x = 0 od góry J3.1 ECU, J3.2 EGR, J4.2 EGR, J4.1 ECU. EGR_P1 jest jednym blokiem w środku, ECU_P1 obu złączy łączy pas 5 mm między kotwami opasek a polami (pod przewodami, na masce). Inaczej jedna z sieci prądowych musiałaby objąć bocznik i przeciąć parę Kelvina.
3. **Bocznik i Kelvin:** RSH1 obrócony o 270° (pole prądowe ECU u góry, EGR u dołu, pola pomiarowe na przekątnej). K_PLUS biegnie z pola pomiarowego w dół i pod korpusem, w szczelinie 3,7 mm między polami prądowymi, w prawo; K_MINUS wprost w prawo. Linie idą równolegle w odstępie 3,3 mm, do 4,2 mm przy U1 (położenie pól pomiarowych WSK2512 i dwa rezystory 1206 jeden nad drugim). Pod bocznikiem na F.Cu jest tylko jego własna sieć K_PLUS, na B.Cu nic (strefa zakazana); GND na F.Cu ma otwór nad obrysem RSH1.
4. **Wylewki mocy:** pola RSH1 z pełnym połączeniem; pola przewodów J3 / J4 od 2.10 na czterech szprychach 2 mm na każdej warstwie (decyzja użytkownika po uwadze F5 recenzji: przewód 2,5 mm² lutuje się bez podgrzewania 830 mm² wylewki; szprychy razem 16 mm miedzi na dwóch warstwach). Pod J4.1 wylewka ECU_P1 przedłużona o 2,45 mm, żeby zmieściła się czwarta szprycha. Najwęższe miejsce toru to samo pole prądowe bocznika (2,03 mm).
5. **5V_SYS, 5VA_P06 i SW_RAW w klasie PWR 0,6 mm** (do 180 mA; 130 mA styku statusu przez R21).
6. **Od spodu: C8 (100 nF nad U3), C2 (470 pF pod U3, 3 mm od IN+ / IN−) i R10 (pod U5)** — uwaga w BOM przy C2 i C8: grubość ≤ 1,5 mm (S1-2).
7. **R21** w lewym dolnym rogu przy J5, z dala od części analogowych; nadruk ECU / EGR i 5VA / SW / GND przy polach końcówek.

**Recenzja niezależna 2.10 i poprawki** (raport poza repozytorium, ustalenia tutaj):
- **F1 (MAJOR) nadruk 0,8 / 0,12 mm** poniżej minimum JLCPCB → wszystkie napisy 1,0 / 0,15 mm (`silkscreen.py`), minimum w regułach DRC (`set_rules.py`), kontrola i próba ujemna.
- **F2 (MINOR) wyspy masy pod U2 / U3, C15 → U10.1 ok. 30 mm** → wnętrza U2 / U3 i pas między nimi bez obcej miedzi, kondensatory odsprzęgające rozmieszczane według sumy odległości pad zasilania → pin i pad masy → pin GND (`placement.py`, `place_dec`), C2 pod U3 przy IN+ / IN−, D1 niżej (miejsce na C4 / C9 przy pinie GND U4), przelotki GND przy każdym kondensatorze po planerze (`stitch.py --targeted`), tor masy z planera tam, gdzie droga po wylewkach przekracza limit (`complete_routes.py --ties`).
- **F3 (MINOR) ścieżki serwisowe przez blok analogowy** → strefy routera j.w.; R30 (SRV_5VA_P06) przy U9.2 zamiast przy INA240. SW_SENSE nadal długi (ok. 160 mm, od J5 przy x = 0 do U6): próba „tylko F.Cu” odcięła U6.5, sieć statyczna 1k / 100k biegnie poza blokiem analogowym.
- **Przy okazji:** R10 od spodu pod U5 (blokował wyprowadzenie U5.10 w 5 z 6 prób trasowania), próba trasowania z kolizjami miedzi odpada (`run_layout.py`; raz 11 kolizji I_L_OUT / 5VA przy U1).
- **Uwagi (NOTE) bez zmian w projekcie:** F4 izolacja spodu WSK2512 pod K_PLUS — do sprawdzenia w karcie / przy zakupie; F6 kotwy przy x = 0 (1,4 mm laminatu do krawędzi, kotwa J3 0,98 mm od strefy M3) — przy przymiarce; F7 odstęp wylewek mocy od GND 0,30 mm (pod maską przy 12 V wystarcza), 5VA do J5 — od 2.10 C17 100 nF przy J5.1 (decyzja użytkownika); F8 kosmetyka wylewek.
- **2.10 (decyzje użytkownika „P06 – ok”):** szprychy 4 × 2 mm na polach J3 / J4 (F5); C17 100 nF 1206 na 5VA_P06 przy J5.1, GND przy J5.3 (F7, zmiana schematu, C17 w `R1-CIRCUIT-KEPT` jako nowa część); C1 zostaje X7R 1206 (budżet τ już obejmuje rozrzut X7R, C0G 470 nF w 1206 słabo dostępny); kod przełącznika BYPASS — wybór przy zakupie według `docs/ZAKUPY.md`. Trasowanie zatwierdzonej wersji odtworzone, planer dołożył połączenia C17.

**Oględziny PDF (1.10; 2.10 po poprawkach strony 2 i 4 obejrzane ponownie: montaż z C2 / R10 od spodu, B.Cu bez cięć pod blokiem analogowym):** strony 1–5 obejrzane po wydaniu. 1: opis i render. 2: montaż — opisy ECU / EGR przy polach J3 / J4 i 5VA / SW / GND przy J5, etykiety obu listew, cztery ukryte oznaczenia z warstwy F.Fab, oznaczenia krawędzi A / B i nazwa płytki. 3: F.Cu — wylewki ECU_P1 / EGR_P1, K_PLUS z pola pomiarowego w dół i pod korpusem do R1, K_MINUS wprost do R2, bez miedzi przy otworach M3 i kotwach. 4: B.Cu — masa, druga warstwa wylewek, pusto pod bocznikiem. 5: przymiarka — obrysy, kotwy przy x = 0, otwory. Bez uwag blokujących.

**Otwarte:** przymiarka 1:1 (końcówki przewodów przy x = 0 z opaskami, R21 leżący 3–5 mm nad płytką), kod przełącznika BYPASS i C1 przy zakupie, decyzje z uwag F5 / F7 recenzji; 3 oznaczenia ukryte z braku miejsca (R11, R12, U10; na rysunku montażowym z warstwy F.Fab); paczka produkcyjna dopiero po „scal”.

## Otwarte punkty

- **MPN bocznika (sprawdzone lokalnie 1.10):** kod **WSK25125L000FEA** (karta 30108: poniżej 0,01 Ω wartość z literą L, więc „R0050” z pierwszej wersji nie jest kodem); 1,0 W przy 70 °C, TCR ±35 ppm/K. Pola pomiarowe według tabeli karty 1,70 mm (biblioteka KiCada 1,40 mm) — footprint lokalny. Bourns CSS2H-2512K-5L00F ma inny układ pól: przy zamianie nowy footprint (kontrola `RSH1-KELVIN-2512` czyta geometrię).
- **MPN przełącznika BYPASS:** wymagania w `docs/ZAKUPY.md`; wybór kodu przy zakupie (dostępność). Numery oczek sprawdzić omomierzem (ODBIOR E03).
- **R21:** PR02 2 W leżący — decyzja użytkownika 1.10 (THT zostaje).
- **C1 (rozstrzygnięte 2.10):** X7R 1206 zostaje (budżet τ obejmuje rozrzut X7R).
- **Zapas z rejestru:** bilans w `docs/ZAKUPY.md`; z posiadanych THT P06 bierze tylko R11 47 kΩ (ostatnią sztukę po P02 R4 i P05 R3). Adaptery Kamami SO14/SOIC8 z przydziału P06 niepotrzebne (SOIC lutowane wprost).
- **3V3_IO** jest na J_BP.14 bez odbiorcy (jak w R1). Pin można zwolnić na GND, jeśli P12 nie potrzebuje tej szyny przy P06 — pytanie w PR. Przegląd lokalny 1.10: zostawić — kołek J_SV2.6 pokazuje wtedy obecność 3V3_IO z P12 na tej płytce.
- **Pojemność 5V_SYS:** P06 220,3 µF + P05 R3 ok. 265,7 µF ≈ 486 µF wobec 600 µF dla TSR 2-2450; start kompletu zmierzyć na stole.

## Pliki

- `eda/` — schemat KiCad 10 (7 arkuszy A3), PCB `P06.kicad_pcb` (layout lokalny 1.10, poprawki po recenzji 2.10) i biblioteki.
- `output/pdf/P06-R2-schemat.pdf`, `output/previews/sch-*.png`; `output/pdf/P06-R2-PCB.pdf` (PDF do recenzji, 5 stron 1:1), `output/previews/pcb-*.png`, `output/svg/`.
- `src/` — generatory schematu oraz łańcuch layoutu (`board.py`, `placement.py`, `route_critical.py`, `run_layout.py`, `verify_pcb.py`, `negative_controls.py`, `run_release.py`, `gndpath.py` — droga po miedzi GND, 2.10 — i skrypty wspólne z P05 R3).
- `routing/` — DSN, SES (`P06.ses`, próby `attempt-*.ses`), `critical.json`, `attempts.json`, `return-ties.json` (tory masy z planera, 2.10), `stitching.json`, raporty DRC pośrednie, `silkscreen.json`.
- `docs/` — `J_BP.csv` i `SERWIS.csv` (kontrakty dla P12 i listew), `BOM.csv`, `parts.json`, `ZAKUPY.md`, `zakupy.csv`, `interfejsy.csv`, `WIAZKI.md`, `ODBIOR.md` R2, `MECHANIKA.md`, `PROJEKT.md`, `FIRMWARE.md`, `netlist-pinowa.csv`.
- `verification/` — ERC, netlista, `schematic-check.json`, `electrical-checks.json`, `s1-checks.json`, `QA.md`; PCB: `drc.json`, `pcb-checks.json`, `negative-controls.json`, `QA-PCB.md`; logi, manifest.
- `reference/` — `P06-R1.xml` (eksport R1 do porównania), `P03-R6-J_BP.csv`, `P05-R3-J_BP.csv`, wyciągi tekstowe kart z R1 (`datasheets/*.txt`).
