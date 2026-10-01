# EGRLab P03-R6 — CORE w formacie S1 (schemat i PCB)

29.09.2026, sesja w chmurze, zadanie `Plytki/Format-S1/zadania/ZADANIE-P03-S1.md`. **Tylko schemat i kontrole, bez PCB.** Layout i trasowanie robi sesja lokalna (`docs/CHMURA.md`, zasada 6). Sprzęt NIE ZBADANO.

**30.09.2026 wieczorem: PCB gotowa do recenzji** (gałąź `p03-r6-pcb`, komputer 24/7 z Ubuntu, `docs/UBUNTU-24-7.md`): DRC 0 niepołączonych / 0 niezgodności ze schematem / 0 innych naruszeń (6 przyjętych `lib_footprint_mismatch` złączy z przyciętym nadrukiem), kontrole PCB 25/25, próby ujemne 16/16 z zerową, PDF `output/pdf/P03-R6-PCB.pdf`. Szczegóły w sekcji „PCB” niżej; przymiarka 1:1 i sprzęt: NIE ZBADANO.

**1.10.2026: poprawki po niezależnej recenzji PCB i decyzje użytkownika, nowe trasowanie.** R70 10 kΩ (gałąź serwisowa SUP_N_OUT), kolejność kołków listew według zasady szyn (szyna tylko obok GND, innej szyny albo linii za 10 kΩ), skrót ADC_RESET „ARS”, GND opisane na obu końcach J_SV2/J_SV3, legenda skrótów jako naklejka (`docs/NAKLEJKA-SERWIS.md`), tytuł z klasą i slotami. DRC 0 niepołączonych / 0 niezgodności / 0 innych naruszeń (6 przyjętych `lib_footprint_mismatch`), kontrole PCB **27/27**, próby ujemne **25/25** z zerową. Lista zmian: `STAN-PRAC.md` (sekcja 1.10).

P03-R6 to obwód P03-R5 przeniesiony do formatu S1 (`Plytki/Format-S1/SPECYFIKACJA-FORMATU-S1.md`, S1-2): klasa **L** (160 × 100 mm), **poziom 2**, sloty S1–S3. Funkcje i sieci R5 zostają bez zmian, zmieniają się złącza. Dochodzi wejście PFAIL_N z P02 R4 i trzy listwy serwisowe. Zamknięty pakiet `Plytki/P03-R5-review` nie był zmieniany.

**30.09.2026 (lokalnie, przed layoutem): poprawki z recenzji PR #6.** R43 10 kΩ → 100 kΩ (stan niski PFAIL_N w upale), trzecia żyła 5V_SYS na J_BP2.17 (PFAIL_N przeszedł z 18 na 16, ADC_RESET z 16 na 18), wszystkie rezystory i kondensatory 100 nF jako SMD 1206 (zakup). Szczegóły w sekcjach niżej, kontrole przeliczone.

## Zmiany R5 → R6

| Obszar | R5 | R6 | Dowód |
|---|---|---|---|
| Złącza do innych płytek | J1 DAQ B2B 2×8, J2–J8 IDC 2×3…2×8, J9 PANELCORE Mini-Fit 8p, J10 LV03 przewody lutowane | **J_BP1, J_BP2, J_BP3**: IDC 2×10 kątowe obudowane na krawędzi A, po jednym na slot, taśma ok. 30 mm do P12 | `docs/J_BP.csv`, C0–C5 w `verification/jbp-checks.json` |
| Zasilanie z P02 | J10: 5V_SYS, 3V3_IO | J_BP2.17, 19, 20 = 5V_SYS (trzy żyły od 30.09), J_BP3.5 = 3V3_IO (przez P12) | `function-checks.json`: „supply inputs…” |
| PFAIL_N (D-02) | brak | J_BP2.16 → R42 1 kΩ → **GPIO3** (J1-13); R43 100 kΩ do 3V3_CORE po stronie złącza | C6, C7 |
| Reset do P04 | U6 → R41 → J4.15, taśma 150 mm | bez zmian w obwodzie, SUP_N_OUT na J_BP3.12; droga 30 mm + P12 + 30 mm | `reset-budget.json` (`slew_estimate_R6`) |
| Punkty odbioru | TP1–TP8 (pady) | TP zostają; nowe **J_SV1–J_SV3**: goldpin 1×13 kątowy na krawędzi B, 33 punkty przez rezystory szeregowe R44–R76 | `docs/SERWIS.csv`, C8–C11 |
| Rezystory | THT DIN0207 leżące (R41 SMD) | wszystkie SMD 1206 (30.09: posiadane MF0207 10 kΩ i 4,7 kΩ zużywają P09 R2 i P10 R2, więc dla P03 to zakup) | `check_tables.py` (reguła montażu) |
| Kondensatory | K15 100 nF THT, 1206 przy SOT-23 | wszystkie SMD 1206; każde 100 nF z jednym kodem GRM31CR71H104KA01L, jak C12 i C15 w R5 (30.09: zapas K15 zużywają P09 R2 i P10 R2) | `check_tables.py`, BOM |
| U11–U14, U21–U23 | 74LVC125AD na adapterach Kamami SO14→DIP | lutowane wprost, footprint SOIC-14 | BOM |
| U3 TPS3808 | na adapterze PA0085 | lutowany wprost, SOT-23-6 | BOM |
| Arkusze | 5 × A3 | 6 × A3 (nowy SERWIS; LINKS = złącza krawędzi A) | `output/pdf/P03-R6-schemat.pdf` |

## Pinout krawędzi A (dla P12)

Pełna tabela z kierunkami i płytkami docelowymi: `docs/J_BP.csv`. Źródło: `src/jbp_pinout.py`. Kolejność żył w taśmie = numer pinu, więc sąsiedzi pinu n to n−1 i n+1.

| Złącze | Slot | Sygnały | GND | Wyjątki (nieparzyste ≠ GND) |
|---|---|---|---|---|
| J_BP1 | S1 | panel P11 (MARK, TEST_KEY, LOGGER_CLEAR, TEST_PRESENT, N_J_SCOPE_HOT), CAN P10, ILOG P06, SENSOR_HEALTHY P08, **P07: DIR i CS_ITEST_N** | 5 | 11, 13, 15, 17, 19 — blok sygnałów statycznych |
| J_BP2 | S2 | DAQ P05 (8 sygnałów, ADC_SCLK i ADC_DOUTA wielopunktowo do P05/P06/P07), **PFAIL_N**, 5V_SYS × 3 | 8 | 17, 19 — żyły 5V_SYS |
| J_BP3 | S3 | SAFE P04 (8), **TEMP P09 (5)**, 3V3_IO | 6 | 5 (3V3_IO), 9 SENSOR_ENABLE, 13 CORE_LINK, 17 HW_ARMED |

**Przesunięte grupy względem tabeli w zadaniu (sporne, do akceptacji):**
- TEMP: J_BP2 → J_BP3. P09 stoi w slocie S3 (poziom 3), więc J_BP3 jest bliżej niż J_BP2.
- PFAIL_N: J_BP3 → J_BP2, żeby na J_BP3 zmieścił się TEMP z GND przy każdym sygnale zboczowym.
- P07 (DIR i ITEST): J_BP3 → J_BP1. Cztery z pięciu sygnałów są statyczne, a CS_ITEST_N stoi obok bliźniaczego CS_ILOG_N z tego samego dekodera. P07 jest tylko w wariancie pełnym. Ścieżka na P12 wydłuża się o ok. 50–100 mm.

Uzasadnienie liczbowe: przy układzie z zadania J_BP2 i J_BP3 miałyby po 15 sygnałów i 5 GND. Pięć pinów GND nie wystarcza, żeby każdy zegar (ADC_SCLK, MEAS_EN, SPI3_SCLK) miał GND po obu stronach, a każdy inny sygnał zboczowy — co najmniej z jednej. Po przesunięciu reguły są spełnione na wszystkich trzech złączach (kontrole C3–C5). Na J_BP2, najszybszym łączu (AD7606B), wszystkie nieparzyste piny poza 17 i 19 (żyły 5V_SYS) to GND.

**Trzecia żyła 5V_SYS (30.09, sporne):** uwaga do PR #6 zmieniała tylko J_BP2.17 z GND na 5V_SYS, ale wtedy PFAIL_N na 18 stałby między dwiema żyłami 5V_SYS bez GND obok (C5), więc PFAIL_N przeszedł na 16 (GND na 15), a statyczny ADC_RESET na 18. MEAS_EN (14) nadal ma GND po obu stronach. P02 R4 wystawia 5V_SYS na trzech pinach swojego J_BP, więc droga P02 → P12 → P03 ma po trzy żyły z obu stron.

Klucz: złącza obudowane, więc bez usuwania pinów KEY jak w R5. Pin 1 od strony mniejszego x.

## PFAIL_N

- **GPIO3 (J1-13).** Formalnie to pin strapujący, ale ESP32-S3 czyta go tylko do wyboru źródła JTAG, gdy wypalony jest eFuse `EFUSE_STRAP_JTAG_SEL`; fabrycznie nie jest i firmware nie może go wypalać. Wszystkie inne wolne piny listwy są gorsze: GPIO35–37 to PSRAM oktalny, GPIO47/48 pracują w domenie 1,8 V, GPIO0/45/46 decydują o starcie, GPIO43/44 są podłączone do CH343P, a GPIO19/20 do USB1 (schemat Waveshare, `P03-R5-review/reference/datasheets/Waveshare-schematic.pdf`). Propozycja ze specyfikacji P02 R4 („np. J3-11”) to GPIO37, czyli PSRAM — odrzucona. Wybór sprawdza C7 (lista zakazanych pinów + próby ujemne GPIO37 i GPIO46).
- **Pull-up po stronie złącza, 100 kΩ (30.09; było 10 kΩ).** P02 R4 steruje linią z otwartego kolektora LM2903 (10 kΩ do swojego 3V3_IO, 1 kΩ szeregowo). Stan niski na GPIO = VOL + (3V3_CORE − VOL) × 1 kΩ / (1 kΩ + R43) = **0,43 V** przy VOL 0,4 V i **0,73 V** przy VOL 0,7 V (3V3_CORE 3,465 V); VIL ESP32-S3 = 0,25 × VDD = 0,825 V. Przy 10 kΩ wychodziło 0,68 V i 0,95 V, czyli w pełnym zakresie temperatur błąd.
- **Zapas.** Linia ciągnie ok. 0,36 mA (0,33 mA z podciągnięcia na P02, 0,03 mA z R43). Karta LM2903 podaje VOL 0,4 V maks. przy 4 mA i 25 °C oraz 0,7 V w pełnym zakresie temperatur (też przy 4 mA), więc zapas do VIL wynosi co najmniej 0,1 V także w upale. VOL i tak mierzymy w odbiorze (ODBIOR). Firmware: GPIO3 jako wejście bez wewnętrznego pull-down (ok. 45 kΩ wobec 100 kΩ dałoby L).
- **Stany:** bez P02 i bez P12 (J_BP2 niepodłączone) R43 daje **H = zasilanie OK**. P02 podłączony, ale bez zasilania (tylko USB na stole): 3V3_IO na P02 = 0 V, więc węzeł = 3,3 V × 11 kΩ / 111 kΩ ≈ **0,33 V, pewne L** (przy 10 kΩ było ok. 1,7 V, stan nieokreślony). Firmware w trybie tylko-USB ma PFAIL_N ignorować. CORE bez zasilania, P02 włączone: prąd do diod GPIO ograniczony przez podciągnięcie P02 i R42 1 kΩ (ok. 0,2 mA).

## Reset do P04 — nowa droga

Obwód U6 (SN74LVC1G17) → R41 220 Ω → SUP_N_OUT bez zmian, na J_BP3.12. Szacunek jak w R4 (idealne RC, najwolniejszy punkt okna 0,8–2,0 V): ns/V = R41 × C / 0,8 V. Obciążenie: taśmy 2 × 30 mm (6 pF), ścieżka P12 do 120 mm (12 pF), 4 styki IDC (4 pF), wejście 74LVC125A (5 pF), ścieżki lokalne (3 pF) = **30 pF → 8,3 ns/V** wobec limitu 10 ns/V (limit przy ok. 36 pF). R5 z taśmą 150 mm: 20 pF, 5,5 ns/V. Zapas jest więc mniejszy niż w R5 i zależy od P12. **Wymaganie dla P12:** SUP_N_OUT prowadzony nad ciągłą masą, bez odgałęzień, ≤ 120 mm, łącznie ≤ 30 pF. Szacunek nie jest gwarancją; rozstrzyga pomiar obu zboczy na P04 U9.5 (ODBIOR).

## Listwy serwisowe (krawędź B)

`docs/SERWIS.csv`. **Przydział według położenia węzłów (30.09, layout; wcześniej według funkcji):** pierwsze przebiegi routera miały 12 z 33 linii serwisowych przez całą płytkę (np. MOTOR_INA/INB z U1 w S1 do listwy w S3). Teraz J_SV1 (S1): MOTOR_INA/INB, 3V3_CORE, MEAS_BANK, SCOPE_TRIG, CS_ILOG_N/CS_ITEST_N, 3V3_IO, LOGGER_CURRENT_OK, I2C; J_SV2 (S2): 5V_SYS, CURRENT_CS_N, ADC_RESET, MEAS_EN, ADC_BUSY, ADC_CONVST, ADC_CS, PFAIL_N, SD_CS, SUP_RAW_N, 5V_M1; J_SV3 (S3): MCU_ARM, HEARTBEAT, PWM, CORE_LINK, SUP_N_OUT, SENSOR_ENABLE, TC2_CS, TC1_CS, INTERLOCK, HW_ARMED, SUP_N (= EN modułu J1-3 = RESET MCP23017). **30.09 wieczorem (decyzja użytkownika, zamiana bramek):** LOGGER_CURRENT_OK i SENSOR_HEALTHY buforuje U14 (wolne kanały 2 i 3) zamiast U12 (kanały 3 i 4, teraz wolne: A i OE na GND, wyjścia otwarte), bo oba końce tych sygnałów leżą w S1 (J_BP1.11/12 → bufor → U1), a U12 stoi przy M1 J3 w S2. Kołek LOGGER_CURRENT_OK przeszedł z J_SV3.12 na J_SV1.10 (węzeł przy R2), SUP_N z J_SV1.10 na J_SV3.12 (węzeł przy U6). Różnice wobec v6.1 i R1: 10 nowych, opisanych wpisów w `compare_v61.py` i `verify_function.py`. Te same 33 punkty i klasy rezystorów (od 1.10 numery kołków inne — niżej); odwołania w `docs/ODBIOR.md` poprawione. Rezystory: 1 kΩ dla szyn i logiki sterowanej, 10 kΩ dla węzłów wyznaczanych tylko przez podciągnięcie lub otwarty dren (SUP_RAW_N, SUP_N, PFAIL_N, I2C, CORE_LINK). Dzięki temu zsunięta sonda nie zresetuje CORE ani nie zdejmie CORE_LINK na P04. Zegarów SPI na listwach nie ma: mierzy się je na końcu łącza (P05, P09).

**1.10 (recenzja PCB, decyzja użytkownika):** w obrębie listwy szyna stoi tylko obok GND, innej szyny albo linii za 10 kΩ, żeby zsunięta sonda nie podała szyny na węzeł logiki przez 2 kΩ: J_SV1 — 3V3_IO / 3V3_CORE na kołkach 9–10 między I2C_SCL i I2C_SDA, LOGGER_CURRENT_OK na 12 przy GND (poślizg na GND daje „nie OK”), MOTOR_INB/INA na 2–3; J_SV2 — 5V_SYS na 2 i 5V_M1 na 12, przy GND i obok PFAIL_N / SUP_RAW_N (10 kΩ); J_SV3 bez zmian. Kolejność jest bliska trasowalnej z 30.09: wersja z szynami na kołkach 2–3 (4 próby routera) i wersja z najmniejszą liczbą przecięć linii (3 próby) nie domknęły trasowania. Sprawdza `verify_jbp.py` C12, odwołania w ODBIOR — C13. **R70 10 kΩ** (było 1 kΩ): gałąź SV_SUP_N_OUT do J_SV3.6 ma ok. 80 mm i za 1 kΩ spowalniała zbocze resetu do P04 do ok. 11,8 ns/V; przy 10 kΩ ograniczenie dla dowolnej długości gałęzi to 8,9 ns/V (`verify_reset.py`; wyjątek od S1 §6: węzeł logiki sterowanej, a 10 kΩ). Skróty na płytce: ADC_RESET „ARS” (było „RST”), GND przy kołkach 1 i 13; legenda skrótów to naklejka na ściankę serwisową (`docs/NAKLEJKA-SERWIS.md`, z `write_tables.py`).

## Części i montaż

- Rezystory: wszystkie SMD 1206 (`R_1206_3216Metric_Pad1.30x1.75mm_HandSolder`): 35 × 10 kΩ, 30 × 1 kΩ, 5 × 33 Ω, 2 × 4,7 kΩ, 2 × 220 Ω, 1 × 330 Ω, 1 × 100 kΩ.
- Kondensatory: wszystkie SMD 1206; 13 × 100 nF GRM31CR71H104KA01L (11 dawnych K15 oraz C12 i C15), C13 1 µF i C14 10 µF jak w R5.
- **Decyzja 30.09 (uwaga do PR #6):** posiadane MF0207 10 kΩ i 4,7 kΩ oraz K15 zużywają P09 R2 i P10 R2, więc wszystkie rezystory i kondensatory P03 to zakup, a nowe części są SMD (reguła użytkownika). Poprzednio 36 × 10 kΩ i 2 × 4,7 kΩ THT na stojąco i 11 × K15.
- SOIC-14 i SOT-23-6 lutowane wprost; adaptery Kamami 575068 i PA0085 zbędne. DIP28 i DIP16 w podstawkach (kupione).

## Wymagania dla layoutu (sesja lokalna)

- Klasa L, poziom 2, dystans 20 mm, elementy ≤ 16,5 mm nad płytką (M1 na listwach żeńskich ok. 13–14 mm — potwierdzić na module). 12 otworów M3 według S1 §4.
- J_BP1–3: środek x = 26,5 mm w swoim slocie, strona wtyku równo z krawędzią A, pin 1 od mniejszego x. J_SV1–3: x = 10–43 mm w slocie, kołki ok. 6 mm za krawędź B, nazwa sygnału przy każdym kołku czytelna od strony B.
- **Gniazdo USB modułu ESP32-S3 od strony krawędzi B**, dostępne przy złożonym stosie (programowanie bez rozbierania). Antena modułu od strony przeciwnej, z obszarem bez miedzi jak w R5 (+3 mm na boki, +8 mm za modułem).
- Rezystory serwisowe przy węźle (dopuszczalnie SMD od spodu, ≥ 1 mm od pól THT, poza strefami dystansów); R42 przy M1 J1-13, R43 przy J_BP2.16; U6/R41/C15 przy J_BP3.12; R36–R40 przy wyjściach buforów.
- Słot S1: panel i CAN; S2: DAQ (U21, U22 blisko J_BP2); S3: SAFE i TEMP (U23 blisko J_BP3).
- Nadruk: `P03 R6 S1-L`, znaczniki krawędzi A i B, pin 1 każdego złącza.

## Kontrole (30.09.2026, `src/run_release.py`, KiCad 10.0.6 lokalnie; 29.09 to samo w Dockerze przed poprawkami)

| Kontrola | Wynik | Raport |
|---|---|---|
| ERC | 0 naruszeń (6 arkuszy) | `verification/erc.json` |
| Netlista pin po pinie z `parts.py` | 122 części, 511/511 pinów, 0 różnic | `schematic-check.json` |
| Nazwy sieci wobec P09 R2 i P10 R2 (main, 29.09) | SPI3_*, TC1/2_CS, CAN_TX/RX, 5V_SYS, 3V3_IO zgodne z ich `docs/J_BP.csv` (porównanie ręczne) | — |
| Mapa v6.1 | 310 pinów, 18 udokumentowanych różnic (R2/R4 i zamiana bramek 30.09), 0 nieoczekiwanych; piny dawnych złączy sprawdzane po sieci na J_BP | `v61-compare.json` |
| Funkcje i stany domyślne (z R5, poprawione pod nowe złącza) | 53/53; mutacje 44/44 (nowa: utrata trzeciej żyły 5V_SYS) | `function-checks.json`, `function-mutations.json` |
| Budżet resetu + szacunek zbocza R6 | 8/8; mutacje 5/5 (1.10: gałąź serwisowa SUP_N_OUT za R70 10 kΩ, mutacja R70 = 1 kΩ) | `reset-budget.json` |
| J_BP, PFAIL_N, listwy serwisowe (C0–C13) | 14/14; próby ujemne 27/27 + zerowa (1.10: C12 sąsiedzi szyn na listwach, C13 odwołania J_SVn.p w ODBIOR) | `jbp-checks.json`, `jbp-negative-controls.json` |
| Tabele (BOM, zakupy, netlista, J_BP, SERWIS, STANY-DOMYSLNE, naklejka listew, reguła montażu: wszystkie R i C w 1206, jeden kod 100 nF) | PASS, 511 pinów, 114 części do zakupu, 26 stanów domyślnych z tabel `verify_function.py`, 39 kołków na naklejce | `table-checks.json` |

Nowe kontrole z zadania: każda sieć dawnego złącza dokładnie raz na J_BP (C1), nieparzyste = GND z listą wyjątków (C3), GND przy zegarach (C4), PFAIL_N z rezystorem szeregowym i podciągnięciem (C6), kołki serwisowe z rezystorami (C9), GND na końcach listew (C8). Każda kontrola ma co najmniej jedną próbę ujemną.

Nie przeniesiono kontroli R3 „złącza równe zamrożonym mapom sąsiadów” (P02-R3 J3, P04-R2.1 J2, P05-R1 J1): te mapy przestały obowiązywać, a nowe powstaną w rewizjach S1 sąsiadów i w P12. Do tego czasu jedynym kontraktem jest `docs/J_BP.csv`.

## PCB (1.10.2026, `src/run_release.py`, KiCad 10.0.6 w Dockerze; pierwsze wydanie 30.09 wieczorem)

| Kontrola | Wynik | Raport |
|---|---|---|
| DRC świeży, wszystkie poziomy | 0 niepołączonych, 0 niezgodności ze schematem, 0 innych naruszeń; 6 × `lib_footprint_mismatch` (J_BP1–3, J_SV1–3: nadruk przycięty przez `silkscreen.py`, przyjęte jawnie) | `verification/drc.json` |
| Kontrole PCB (`verify_pcb.py`) | 27/27 (1.10: pas zastrzeżony krawędzi A, bliskość oznaczeń) | `verification/pcb-checks.json`, `QA-PCB.md` |
| Próby ujemne PCB | 25/25 z zerową | `verification/negative-controls.json` |
| Tor 5 V (J_BP2 → Q1 → M1 J1-21, 1,5 mm) | 37,7 mΩ miedzi przy 20 °C (budżet 50 mΩ) | `pcb-checks.json` |
| Trasowanie | Freerouting 2.1.0 (30 przebiegów, 4 wątki, GND jako płaszczyzna B.Cu), 1.10 nowe trasowanie po zmianie kolejności kołków: pierwsza próba; planer dokańczania: 1 połączenie sygnałowe i 5 GND (niżej); 242 przelotki | `routing/completion-routes.json` (odtwarzanie bez `--new-route`) |

**Jak powstało trasowanie** (skrypty w `src/`, opis w nagłówkach): `fanout_gnd.py` przed routerem kładzie zablokowane belki GND pod każdym SOIC-14 (F.Cu pod korpusem, dwie przelotki) i grzebienie GND pod korpusami J_BP (piny nieparzystego rzędu przez szczeliny parzystego do szyny y = 8 mm); `prepare_routing.py` przekazuje GND routerowi jako płaszczyznę B.Cu, więc router sam dokłada przelotki GND przy polach SMD; po imporcie `cleanup.py --tidy` usuwa porzucone kawałki tras; `stitch.py` i planer `complete_routes.py` (raster 0,05 mm, przeszkody poszerzane geometrycznie, łączenie wysp GND z głównym klastrem) domykają resztę. Bez tych kroków router zostawiał 16–29 połączeń sygnałowych i kilkadziesiąt odciętych pól GND (7 wariantów, `STAN-PRAC.md`).

**Oględziny PDF (1.10, 5 stron, `output/previews/pcb-*.png`):** opis z liczbami z tego wydania; montaż 1:1 — skróty J_SV2/J_SV3 czytelne, GND przy obu końcach, napis przy kołku 1 nad znacznikiem pinu; F.Cu i B.Cu — wylewki GND, tor 5V_M1 1,5 mm po B.Cu, obszar bez miedzi pod anteną; przymiarka — kółka Ø7 przy otworach M3 i Ø6 przy SD1. Bez uwag blokujących.

**Trasy planera dokańczania (1.10, długości z `completion-routes.json`):** SV_ADC_RESET J_SV2.4 → R57.2 — 122 mm, 5 zmian warstwy (linia serwisowa za 1 kΩ: pojemność ok. 12 pF jest za rezystorem, węzeł ADC_RESET jej nie widzi; brzydka, ale bez skutku elektrycznego); GND: U4.3 → klaster 14 mm, M1.J3-1 → wylewka 61 mm i → klaster 46 mm, M1.J3-22 → wylewka 3,5 mm, U6.3 → klaster 34 mm (pin GND modułu M1 ma wiele innych pinów GND).

**Decyzje (sporne oznaczone):**
1. **Sporne:** USB-C M1 i karta SD1 ok. 6,2 mm przed krawędzią B — moduły (26 mm) są szersze niż przerwy między listwami serwisowymi (19,4 mm); dostęp przy zdjętej ściance B.
2. **Sporne:** U22 w S1 przy J_BP1 (README wymagało J_BP2) — jego wejścia idą z U1/U2, dwa wyjścia do J_BP1; `verify_pcb.py` sprawdza ≤ 30 mm od J_BP1.
3. **Sporne:** przydział kołków listew według położenia węzłów (zmiana względem schematu z PR #6), z zamianą J_SV1.10 ↔ J_SV3.12 (niżej).
4. **Sporne:** przy J_SV2 i J_SV3 skróty trzyliterowe (0,8 mm) zamiast pełnych nazw (nad listwami stoją moduły, zostaje 1,5 mm); od 1.10 legenda na naklejce, GND opisane przy kołkach 1 i 13 (napis przy kołku 1 o 0,45 mm wyżej, nad znacznikiem pinu 1).
5. 3V3_CORE 0,3 mm (0,5 mm nie mieści się między pinami w rastrze 2,54; spadek ok. 25 mV przy 100 mA).
6. **Decyzja użytkownika 30.09:** ścieżki sygnałowe 0,2 mm przy odstępie 0,25 mm, tylko na P03 R6 (odstępstwo od S1 §3: reguły jak P02-R3); zasilanie bez zmian.
7. **Decyzja użytkownika 30.09:** zamiana bramek LOGGER_CURRENT_OK / SENSOR_HEALTHY z U12 na wolne kanały U14 (opis w „Listwy serwisowe”).
8. Rozmieszczenie: S1 rozsunięte w dół (rząd SOIC y 28, U1 y 45, U2 y 66), U21 x = 54 (≤ 30 mm od J_BP2), C13 obrócony o 180° (pole 5V_SYS na górze, jak zakładał komentarz; wcześniej pole GND było zamknięte między J_BP2 a torem 5 V), węzły serwisowe bliżej listew (5V_SYS przy U5.1, ADC_BUSY przy U11.5, HEARTBEAT przy M1 J3-18, SUP_N przy U6.2).
9. **Sporne (lutowanie):** siedem pól GND z pełnym połączeniem z wylewką zamiast termicznego (1.10: J_BP2.5, 7, 9, 11, J_BP3.15, 19, U1.17 — szprychy odcięte przez ścieżki; `routing/solid-pads.json`); reguła P02 „pola złączy zostają z termikami” dotyczyła lutowanych przewodów, których na P03 nie ma. Przy lutowaniu tych pinów potrzeba więcej ciepła.

**Otwarte:** przymiarka wydruku 1:1 (strona 5 PDF), wysokość M1 na listwach (szacunek 13,8 mm), 16 oznaczeń ukrytych z braku miejsca (R2, R7, R9, R14, R27, R28, R41, R48, R50, R51, R65, R66, R70, R71, C13, U6; lista w `verification/QA-PCB.md`, na rysunku montażowym F.Fab są wszystkie; od 1.10 oznaczenie musi być wyraźnie bliżej własnej części niż innych i poza strefami Ø7, stąd więcej ukrytych niż 7 z 30.09), recenzja; paczka produkcyjna dopiero po „scal”.

## Otwarte punkty

1. Akceptacja przesunięć grup (TEMP, PFAIL_N, P07) i wyjątków od reguły „nieparzyste = GND”.
2. GPIO3 dla PFAIL_N (formalnie strap JTAG) — akceptacja albo inna decyzja.
3. VOL LM2903 przy ok. 0,36 mA — pomiar w odbiorze. Od 30.09 (R43 100 kΩ) zapas do VIL ≥ 0,1 V także przy 0,7 V z karty, a stan przy P02 bez zasilania to pewne L (ok. 0,33 V) zamiast 1,7 V.
4. Zbocze SUP_N_OUT: szacunek 8,3 ns/V przy 30 pF; wymaganie długości ścieżki dla P12 i pomiar na P04.
5. Rozstrzygnięte 30.09: wszystkie rezystory i kondensatory P03 jako SMD 1206 (zakup), jeden kod 100 nF.
6. Spadek 5V_SYS na drodze P02 → P12 → P03: przy dwóch żyłach na złącze szacowałem 40–60 mV przy 0,8 A; od 30.09 są trzy żyły po obu stronach, więc udział styków i taśmy spada do ok. 2/3. Do potwierdzenia pomiarem wobec wymagania 4,85 V na J_BP2.17, 19, 20.
7. Wysokość M1 na listwach i przymiarka modułów przed layoutem.
8. B2B P03–P05 z R5 przestaje być problemem (brak B2B w S1); `docs/B2B-STATUS.md` z R5 nie jest przenoszony.

## Pliki

- `eda/P03.kicad_sch` (+ 5 arkuszy podrzędnych), `eda/libraries/`, `eda/P03.kicad_pro` (reguły z `set_rules.py`), **`eda/P03.kicad_pcb`** (płytka z `run_release.py`).
- `output/pdf/P03-R6-schemat.pdf` (6 stron), podglądy `output/previews/sch-*.png`; **`output/pdf/P03-R6-PCB.pdf`** (5 stron: opis, montaż 1:1, F.Cu, B.Cu, przymiarka), `output/svg/`, `output/previews/pcb-*.png`, `top.png`, `isometric.png`.
- `docs/J_BP.csv` i `docs/SERWIS.csv` (dla P12), `docs/BOM.csv`, `docs/zakupy.csv`, `docs/netlist-pinowa.csv`, `docs/parts.json`, `docs/ODBIOR.md`, `docs/MECHANIKA.md`, `docs/ODTWARZANIE.md`; z R5 bez zmian treści: `STANY-DOMYSLNE.csv`, `ZRODLA.md`, `KONTRAKT-RESET.md` i `ZASILANIE-RESET.md` (z notą R6 na górze).
- `src/`: generator (`parts.py`, `jbp_pinout.py`, `serwis_pinout.py`, `build_schematic.py`, `write_tables.py`), kontrole (`verify_*.py`, `compare_v61.py`), layout (`placement.py`, `build_board.py`, `route_critical.py`, `fanout_gnd.py`, `prepare_routing.py`, `run_layout.py`, `import_routing.py`, `cleanup.py`, `stitch.py`, `complete_routes.py`, `silkscreen.py`, `negative_controls.py`, `export_views.py`, `make_pdf.py`), `run_release.py`.
- `routing/`: wynik routera `P03.ses` i trasy dokańczające `completion-routes.json` (odtwarzanie: `run_release.py` bez `--new-route`), raporty kroków; `verification/`: DRC, kontrole PCB, próby ujemne, `QA-PCB.md`, manifest SHA-256.
- `reference/`: netlisty R1 i R5, import v6.1, mapa części P04 do budżetu resetu, footprinty z P02.
