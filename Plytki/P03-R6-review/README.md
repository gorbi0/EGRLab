# EGRLab P03-R6 — CORE w formacie S1 (schemat)

29.09.2026, sesja w chmurze, zadanie `Plytki/Format-S1/zadania/ZADANIE-P03-S1.md`. **Tylko schemat i kontrole, bez PCB.** Layout i trasowanie robi sesja lokalna (`docs/CHMURA.md`, zasada 6). Sprzęt NIE ZBADANO.

P03-R6 to obwód P03-R5 przeniesiony do formatu S1 (`Plytki/Format-S1/SPECYFIKACJA-FORMATU-S1.md`, S1-2): klasa **L** (160 × 100 mm), **poziom 2**, sloty S1–S3. Funkcje i sieci R5 zostają bez zmian, zmieniają się złącza. Dochodzi wejście PFAIL_N z P02 R4 i trzy listwy serwisowe. Zamknięty pakiet `Plytki/P03-R5-review` nie był zmieniany.

## Zmiany R5 → R6

| Obszar | R5 | R6 | Dowód |
|---|---|---|---|
| Złącza do innych płytek | J1 DAQ B2B 2×8, J2–J8 IDC 2×3…2×8, J9 PANELCORE Mini-Fit 8p, J10 LV03 przewody lutowane | **J_BP1, J_BP2, J_BP3**: IDC 2×10 kątowe obudowane na krawędzi A, po jednym na slot, taśma ok. 30 mm do P12 | `docs/J_BP.csv`, C0–C5 w `verification/jbp-checks.json` |
| Zasilanie z P02 | J10: 5V_SYS, 3V3_IO | J_BP2.19–20 = 5V_SYS, J_BP3.5 = 3V3_IO (przez P12) | `function-checks.json`: „supply inputs…” |
| PFAIL_N (D-02) | brak | J_BP2.18 → R42 1 kΩ → **GPIO3** (J1-13); R43 10 kΩ do 3V3_CORE po stronie złącza | C6, C7 |
| Reset do P04 | U6 → R41 → J4.15, taśma 150 mm | bez zmian w obwodzie, SUP_N_OUT na J_BP3.12; droga 30 mm + P12 + 30 mm | `reset-budget.json` (`slew_estimate_R6`) |
| Punkty odbioru | TP1–TP8 (pady) | TP zostają; nowe **J_SV1–J_SV3**: goldpin 1×13 kątowy na krawędzi B, 33 punkty przez rezystory szeregowe R44–R76 | `docs/SERWIS.csv`, C8–C11 |
| Rezystory | THT DIN0207 leżące (R41 SMD) | 10 kΩ i 4,7 kΩ (posiadane wartości MF0207) THT **na stojąco**; 1 kΩ, 330 Ω, 220 Ω, 33 Ω SMD 1206 | `check_tables.py` (reguła montażu) |
| Kondensatory | K15 100 nF THT, 1206 przy SOT-23 | bez zmian; MPN K15 zmieniony na posiadany kod K104K15X7RF5TH5 (ta sama część) | BOM |
| U11–U14, U21–U23 | 74LVC125AD na adapterach Kamami SO14→DIP | lutowane wprost, footprint SOIC-14 | BOM |
| U3 TPS3808 | na adapterze PA0085 | lutowany wprost, SOT-23-6 | BOM |
| Arkusze | 5 × A3 | 6 × A3 (nowy SERWIS; LINKS = złącza krawędzi A) | `output/pdf/P03-R6-schemat.pdf` |

## Pinout krawędzi A (dla P12)

Pełna tabela z kierunkami i płytkami docelowymi: `docs/J_BP.csv`. Źródło: `src/jbp_pinout.py`. Kolejność żył w taśmie = numer pinu, więc sąsiedzi pinu n to n−1 i n+1.

| Złącze | Slot | Sygnały | GND | Wyjątki (nieparzyste ≠ GND) |
|---|---|---|---|---|
| J_BP1 | S1 | panel P11 (MARK, TEST_KEY, LOGGER_CLEAR, TEST_PRESENT, N_J_SCOPE_HOT), CAN P10, ILOG P06, SENSOR_HEALTHY P08, **P07: DIR i CS_ITEST_N** | 5 | 11, 13, 15, 17, 19 — blok sygnałów statycznych |
| J_BP2 | S2 | DAQ P05 (8 sygnałów, ADC_SCLK i ADC_DOUTA wielopunktowo do P05/P06/P07), **PFAIL_N**, 5V_SYS × 2 | 9 | 19 — druga żyła 5V_SYS |
| J_BP3 | S3 | SAFE P04 (8), **TEMP P09 (5)**, 3V3_IO | 6 | 5 (3V3_IO), 9 SENSOR_ENABLE, 13 CORE_LINK, 17 HW_ARMED |

**Przesunięte grupy względem tabeli w zadaniu (sporne, do akceptacji):**
- TEMP: J_BP2 → J_BP3. P09 stoi w slocie S3 (poziom 3), więc J_BP3 jest bliżej niż J_BP2.
- PFAIL_N: J_BP3 → J_BP2, żeby na J_BP3 zmieścił się TEMP z GND przy każdym sygnale zboczowym.
- P07 (DIR i ITEST): J_BP3 → J_BP1. Cztery z pięciu sygnałów są statyczne, a CS_ITEST_N stoi obok bliźniaczego CS_ILOG_N z tego samego dekodera. P07 jest tylko w wariancie pełnym. Ścieżka na P12 wydłuża się o ok. 50–100 mm.

Uzasadnienie liczbowe: przy układzie z zadania J_BP2 i J_BP3 miałyby po 15 sygnałów i 5 GND. Pięć pinów GND nie wystarcza, żeby każdy zegar (ADC_SCLK, MEAS_EN, SPI3_SCLK) miał GND po obu stronach, a każdy inny sygnał zboczowy — co najmniej z jednej. Po przesunięciu reguły są spełnione na wszystkich trzech złączach (kontrole C3–C5). Na J_BP2, najszybszym łączu (AD7606B), wszystkie nieparzyste piny poza 19 to GND.

Klucz: złącza obudowane, więc bez usuwania pinów KEY jak w R5. Pin 1 od strony mniejszego x.

## PFAIL_N

- **GPIO3 (J1-13).** Formalnie to pin strapujący, ale ESP32-S3 czyta go tylko do wyboru źródła JTAG, gdy wypalony jest eFuse `EFUSE_STRAP_JTAG_SEL`; fabrycznie nie jest i firmware nie może go wypalać. Wszystkie inne wolne piny listwy są gorsze: GPIO35–37 to PSRAM oktalny, GPIO47/48 pracują w domenie 1,8 V, GPIO0/45/46 decydują o starcie, GPIO43/44 są podłączone do CH343P, a GPIO19/20 do USB1 (schemat Waveshare, `P03-R5-review/reference/datasheets/Waveshare-schematic.pdf`). Propozycja ze specyfikacji P02 R4 („np. J3-11”) to GPIO37, czyli PSRAM — odrzucona. Wybór sprawdza C7 (lista zakazanych pinów + próby ujemne GPIO37 i GPIO46).
- **Pull-up po stronie złącza.** P02 R4 steruje linią z otwartego kolektora LM2903 (10 kΩ do swojego 3V3_IO, 1 kΩ szeregowo). Stan niski na GPIO = VOL + (3V3_CORE − VOL) × 1 kΩ / 11 kΩ = **0,68 V** przy VOL 0,4 V i 3,465 V; VIL ESP32-S3 = 0,25 × VDD = 0,825 V. Ten sam 10 kΩ po stronie GPIO dałby 0,91 V, czyli błąd — stąd R43 przy złączu.
- **Zapas zależy od VOL LM2903 przy małym prądzie.** Linia ciągnie ok. 0,6 mA. Karta podaje 0,4 V maks. przy 4 mA i 25 °C, ale 0,7 V w pełnym zakresie temperatur (też przy 4 mA). Przy 0,7 V wyszłoby 0,95 V > VIL. Przy 0,6 mA spodziewam się ok. 0,1 V, ale to trzeba zmierzyć (ODBIOR).
- **Stany:** bez P02 i bez P12 (J_BP2 niepodłączone) R43 daje **H = zasilanie OK**. P02 podłączony, ale bez zasilania (tylko USB na stole): węzeł ok. 1,7 V, czyli stan nieokreślony — firmware ma w tym trybie ignorować PFAIL_N. CORE bez zasilania, P02 włączone: prąd do diod GPIO ograniczony przez R42 1 kΩ (ok. 0,2 mA).

## Reset do P04 — nowa droga

Obwód U6 (SN74LVC1G17) → R41 220 Ω → SUP_N_OUT bez zmian, na J_BP3.12. Szacunek jak w R4 (idealne RC, najwolniejszy punkt okna 0,8–2,0 V): ns/V = R41 × C / 0,8 V. Obciążenie: taśmy 2 × 30 mm (6 pF), ścieżka P12 do 120 mm (12 pF), 4 styki IDC (4 pF), wejście 74LVC125A (5 pF), ścieżki lokalne (3 pF) = **30 pF → 8,3 ns/V** wobec limitu 10 ns/V (limit przy ok. 36 pF). R5 z taśmą 150 mm: 20 pF, 5,5 ns/V. Zapas jest więc mniejszy niż w R5 i zależy od P12. **Wymaganie dla P12:** SUP_N_OUT prowadzony nad ciągłą masą, bez odgałęzień, ≤ 120 mm, łącznie ≤ 30 pF. Szacunek nie jest gwarancją; rozstrzyga pomiar obu zboczy na P04 U9.5 (ODBIOR).

## Listwy serwisowe (krawędź B)

`docs/SERWIS.csv`. J_SV1 (S1): szyny 5V_SYS, 5V_M1, 3V3_CORE, 3V3_IO, reset SUP_RAW_N, SUP_N (= EN modułu J1-3 = RESET MCP23017), SUP_N_OUT, PFAIL_N, I2C, SCOPE_TRIG. J_SV2 (S2): stany startowe DAQ i wszystkie linie CS. J_SV3 (S3): TC2_CS, SAFE, MOTOR_INA/INB, LOGGER_CURRENT_OK. Rezystory: 1 kΩ dla szyn i logiki sterowanej, 10 kΩ dla węzłów wyznaczanych tylko przez podciągnięcie lub otwarty dren (SUP_RAW_N, SUP_N, PFAIL_N, I2C, CORE_LINK). Dzięki temu zsunięta sonda nie zresetuje CORE ani nie zdejmie CORE_LINK na P04. „EN modułu” i SUP_N to ta sama sieć, więc zajmują jeden kołek. Zegarów SPI na listwach nie ma: mierzy się je na końcu łącza (P05, P09).

## Części i montaż

- Rezystory: wartości posiadane w `Zamowione/zamowione.csv` jako MF0207 (10 kΩ, 4,7 kΩ) są THT na stojąco (`R_Axial_DIN0207_L6.3mm_D2.5mm_P5.08mm_Vertical`). Pozostałe to SMD 1206: 30 × 1 kΩ, 2 × 220 Ω, 1 × 330 Ω, 5 × 33 Ω.
- Kondensatory: 100 nF K15 THT jak w R5; C12–C15 zostają 1206 przy SOT-23 (lokalne odsprzęganie, decyzja R2/R4).
- **Ilości wobec posiadanych (pytanie w PR):** reguła „wartość i typ są w rejestrze” daje 36 × 10 kΩ THT i 11 × K15, a posiadane są 7 × 10 kΩ i 5 × K15 (P01 wstrzymane, więc cały zapas wolny). Reszta to zakup, np. z listy 2.
- SOIC-14 i SOT-23-6 lutowane wprost; adaptery Kamami 575068 i PA0085 zbędne. DIP28 i DIP16 w podstawkach (kupione).

## Wymagania dla layoutu (sesja lokalna)

- Klasa L, poziom 2, dystans 20 mm, elementy ≤ 16,5 mm nad płytką (M1 na listwach żeńskich ok. 13–14 mm — potwierdzić na module). 12 otworów M3 według S1 §4.
- J_BP1–3: środek x = 26,5 mm w swoim slocie, strona wtyku równo z krawędzią A, pin 1 od mniejszego x. J_SV1–3: x = 10–43 mm w slocie, kołki ok. 6 mm za krawędź B, nazwa sygnału przy każdym kołku czytelna od strony B.
- **Gniazdo USB modułu ESP32-S3 od strony krawędzi B**, dostępne przy złożonym stosie (programowanie bez rozbierania). Antena modułu od strony przeciwnej, z obszarem bez miedzi jak w R5 (+3 mm na boki, +8 mm za modułem).
- Rezystory serwisowe przy węźle (dopuszczalnie SMD od spodu, ≥ 1 mm od pól THT, poza strefami dystansów); R42 przy M1 J1-13, R43 przy J_BP2.18; U6/R41/C15 przy J_BP3.12; R36–R40 przy wyjściach buforów.
- Słot S1: panel i CAN; S2: DAQ (U21, U22 blisko J_BP2); S3: SAFE i TEMP (U23 blisko J_BP3).
- Nadruk: `P03 R6 S1-L`, znaczniki krawędzi A i B, pin 1 każdego złącza.

## Kontrole (29.09.2026, `src/run_release.py`, KiCad 10.0.6 w Dockerze)

| Kontrola | Wynik | Raport |
|---|---|---|
| ERC | 0 naruszeń (6 arkuszy) | `verification/erc.json` |
| Netlista pin po pinie z `parts.py` | 122 części, 511/511 pinów, 0 różnic | `schematic-check.json` |
| Mapa v6.1 | 310 pinów, 8 udokumentowanych różnic R2/R4, 0 nieoczekiwanych; piny dawnych złączy sprawdzane po sieci na J_BP | `v61-compare.json` |
| Funkcje i stany domyślne (z R5, poprawione pod nowe złącza) | 53/53; mutacje 43/43 | `function-checks.json`, `function-mutations.json` |
| Budżet resetu + szacunek zbocza R6 | 8/8; mutacje 4/4 | `reset-budget.json` |
| J_BP, PFAIL_N, listwy serwisowe (C0–C11) | 12/12; próby ujemne 22/22 + zerowa | `jbp-checks.json`, `jbp-negative-controls.json` |
| Tabele (BOM, zakupy, netlista, J_BP, SERWIS, reguła THT/SMD) | PASS, 511 pinów, 114 części do zakupu | `table-checks.json` |

Nowe kontrole z zadania: każda sieć dawnego złącza dokładnie raz na J_BP (C1), nieparzyste = GND z listą wyjątków (C3), GND przy zegarach (C4), PFAIL_N z rezystorem szeregowym i podciągnięciem (C6), kołki serwisowe z rezystorami (C9), GND na końcach listew (C8). Każda kontrola ma co najmniej jedną próbę ujemną.

Nie przeniesiono kontroli R3 „złącza równe zamrożonym mapom sąsiadów” (P02-R3 J3, P04-R2.1 J2, P05-R1 J1): te mapy przestały obowiązywać, a nowe powstaną w rewizjach S1 sąsiadów i w P12. Do tego czasu jedynym kontraktem jest `docs/J_BP.csv`.

## Otwarte punkty

1. Akceptacja przesunięć grup (TEMP, PFAIL_N, P07) i wyjątków od reguły „nieparzyste = GND”.
2. GPIO3 dla PFAIL_N (formalnie strap JTAG) — akceptacja albo inna decyzja.
3. VOL LM2903 przy 0,6 mA i stan nieokreślony PFAIL_N przy P02 bez zasilania — pomiar w odbiorze; ewentualna zmiana po stronie P02 (np. pull-up P02 do 5V_SYS przez dzielnik albo bufor push-pull).
4. Zbocze SUP_N_OUT: szacunek 8,3 ns/V przy 30 pF; wymaganie długości ścieżki dla P12 i pomiar na P04.
5. Ilości THT 10 kΩ i K15 wobec posiadanych.
6. Spadek 5V_SYS na drodze P02 → P12 → P03 (8 styków IDC, dwie żyły na złącze): ok. 40–60 mV przy 0,8 A — do potwierdzenia pomiarem wobec wymagania 4,85 V z R5 (teraz na J_BP2.19–20).
7. Wysokość M1 na listwach i przymiarka modułów przed layoutem.
8. B2B P03–P05 z R5 przestaje być problemem (brak B2B w S1); `docs/B2B-STATUS.md` z R5 nie jest przenoszony.

## Pliki

- `eda/P03.kicad_sch` (+ 5 arkuszy podrzędnych), `eda/libraries/`, `eda/P03.kicad_pro` (reguły z R5, bez PCB).
- `output/pdf/P03-R6-schemat.pdf` (6 stron), podglądy `output/previews/sch-*.png`.
- `docs/J_BP.csv` i `docs/SERWIS.csv` (dla P12), `docs/BOM.csv`, `docs/zakupy.csv`, `docs/netlist-pinowa.csv`, `docs/parts.json`, `docs/ODBIOR.md`, `docs/MECHANIKA.md`, `docs/ODTWARZANIE.md`; z R5 bez zmian treści: `STANY-DOMYSLNE.csv`, `ZRODLA.md`, `KONTRAKT-RESET.md` i `ZASILANIE-RESET.md` (z notą R6 na górze).
- `src/`: generator (`parts.py`, `jbp_pinout.py`, `serwis_pinout.py`, `build_schematic.py`, `write_tables.py`), kontrole (`verify_*.py`, `compare_v61.py`), `run_release.py`.
- `reference/`: netlisty R1 i R5, import v6.1, mapa części P04 do budżetu resetu, footprinty z P02.
