# P12 R1 — płytka połączeń krawędzi A (wariant LOGGER), schemat i PCB

*4.10.2026, komputer 24/7 (KiCad 10.0.6 + Freerouting 2.1.0 w Dockerze). Łańcuch skryptów z `Plytki/P10-R2-review/src` (wzór P03 R6 / P09 R2), dostosowany do płytki pionowej. Wejście: kontrakty `Plytki/P12-przygotowanie` (0 błędów, 23 sieci OK, 27 czeka).*

**Status: PCB gotowa do zamówienia** (paczka `Plytki/P12-PCB-R1-zamowienie`). Sprzętu nie zbudowano; przymiarki taśm NIE ZBADANO.

## Co to jest

Płytka 160 × 92 mm, która zastępuje wiązki krawędzi A: 10 prostych obudowanych gniazd IDC i 4 pola pomiarowe, bez elementów aktywnych i biernych. Każde złącze krawędzi A płytek LOGGER ma na P12 swoje gniazdo w tym samym x i na wysokości osi kątowego IDC płytki. Krótka taśma IDC łączy je bez skrętu.

| Ref | Płytka i złącze | Typ | x stosu [mm] | z osi [mm] |
|---|---|---|---:|---:|
| J1 | P02 R4 J_BP (poziom 1, S3) | IDC 2×10 | 133,5 | 14,05 |
| J2 | P03 R6 J_BP1 (poziom 2, S1) | IDC 2×10 | 26,5 | 40,65 |
| J3 | P03 R6 J_BP2 (poziom 2, S2) | IDC 2×10 | 80,0 | 40,65 |
| J4 | P03 R6 J_BP3 (poziom 2, S3) | IDC 2×10 | 133,5 | 40,65 |
| J5 | P05 R3 J_BP1 (poziom 3, S1) | IDC 2×5 | 26,5 | 62,25 |
| J6 | P05 R3 J_BP2 (poziom 3, S2) | IDC 2×10 | 80,0 | 62,25 |
| J7 | P09 R2 J1 (poziom 3, S3) | IDC 2×8 | 133,5 | 62,25 |
| J8 | P06 R2 J_BP (poziom 4, S2) | IDC 2×8 | 80,0 | 83,85 |
| J9 | P10 R2 J1 (poziom 4, S3) | IDC 2×5 | 133,5 | 83,85 |
| J10 | P11 R2 J_P12 (panel, taśma z P11) | IDC 2×10 | 26,5 | 14,05 |
| TP1–TP4 | pola pomiarowe GND / 5V_SYS / 3V3_IO / GND | THT Ø2,0 | 94 / 100 / 106 / 112 | 14,05 |

Tabela dla programów: `docs/GEOMETRIA.csv`. Pinout pin po pinie: `docs/kontrakt-P12.json`.

## Geometria (do potwierdzenia przy przymiarce)

- **Ustawienie:** P12 stoi pionowo, równolegle do krawędzi A, ok. 18–20 mm przed nią (y ≈ −18 w układzie stosu). Strona F (gniazda) jest od strony stosu, a strona B od ściany A. Montaż: dystanse M3 do ściany A (makieta: ściana 30 mm przed krawędzią A).
- **Układ płytki:** x = x stosu (0 = strona panelu, 160 = wejścia), z = wysokość nad dnem obudowy. W KiCadzie X = x, Y = 96 − z, więc widok KiCada to widok od stosu z z w górę. Obrys x 0…160, z 4…96 (wnętrze ok. 99 mm), narożniki R1, FR4 1,6 mm, 2 × 35 µm.
- **Wysokość złącza:** z = spód płytki stosu (8,0 / 34,6 / 56,2 / 77,8, `zlacza-P12.csv`) + 1,6 + 4,45 mm. 4,45 mm to oś rzędów kątowego IDC nad płytką (korpus 8,9 mm, rzędy symetrycznie; footprint `IDC-Header_2x…_P2.54mm_Horizontal`, Amphenol T821 / Würth 612…21621). Karty z tym wymiarem w repo nie ma. Ewentualną odchyłkę ±0,5 mm pokrywa taśma.
- **Taśmy stosu:** gniazda IDC bez odciążki. Taśma wychodzi z gniazda w górę lub w dół i zawija się między krawędzią A a P12; gniazda stoją wtedy „plecami do siebie”. Szacunek: kątowy wtyk wystaje ok. 4 mm za krawędź A, a gniazdo na P12 z obudową ma ok. 13 mm. Przy złączach na tej samej wysokości odstęp P12 od krawędzi A to więc ok. 18–20 mm, a taśma ok. 30 mm (S1 §5). Przy tym x i z gniazda się nie zderzają. Sąsiednie poziomy są 21,6 mm wyżej i niżej, a pętla taśmy zajmuje kilka milimetrów.
- **Taśma P11 (J10):** P11 leży poziomo na dnie strefy panelu (x < 0). J10 stoi nisko przy lewej krawędzi, w miejscu slotu S1 poziomu 1. P02 ma tam pustą krawędź (jedyne złącze poziomu 1 jest w S3), a przestrzeń z 18–36 nad J10 jest wolna od innych taśm. Piny 10 i 13–16 stoją pod tymi samymi pinami P03 J_BP1 (J2), więc ścieżki idą prosto. Taśma wychodzi z gniazda w górę, skręca w stronę −x i wychodzi poza x = 0 do strefy panelu. **Szacowana długość: 65–80 mm** (zależy od położenia J_P12 na P11, którego layout jest w toku). Zalecam taśmę 100 mm i skrócenie przy przymiarce. P12 nie jest wydłużona w stronę x < 0, bo za panelem są porty AT04, przyciski i kanał przewodów (głębokość 25–45 mm, makieta).
- **Otwory M3 (NPTH 3,2, strefy Ø7 bez miedzi):** (x, z) = (4,5; 8,5), (4,5; 91,5), (155,5; 8,5), (155,5; 91,5), (53,25; 51,45), (106,75; 51,45). Są w rogach i w przerwach między slotami poziomów 2 i 3, gdzie nie ma złączy ani taśm. Obrysy złączy są co najmniej 1 mm poza strefą.

### Orientacja (rząd nieparzysty / parzysty)

Na płytkach stosu kątowe IDC ma pin 1 od mniejszego x, a rząd parzysty bliżej krawędzi A. Piny rzędu dalszego (nieparzystego) muszą przejść nad pinami bliższego, więc w otworze wtyku rząd nieparzysty jest **na górze**, a parzysty na dole.

Płaska taśma bez skrętu zachowuje x żył, więc pin 1 zostaje od mniejszego x. Gniazda IDC mają stałą chiralność. Widziane od strony styku: „pin 1 z lewej ⇒ rząd nieparzysty u góry”. Gniazdo na płytce stosu jest odwrócone stykiem w +y. To samo gniazdo przy P12 patrzy w −y, więc przy pinie 1 od mniejszego x jego rząd nieparzysty wypada **na dole**.

Na P12 jest więc: pin 1 od mniejszego x, pin 2 nad pinem 1 (footprint `IDC-Header_2x…_P2.54mm_Vertical`, obrót 90°). Taki układ daje kolejność styków zgodną ze standardową chiralnością złącza, a klucze obudów pasują przy taśmie prostej. Rozumowanie pokazuje strona 5 PDF.

Kontrole: `verify_pcb.py` „Orientation” (pin 2k dokładnie 2,54 mm nad 2k−1, piny nieparzyste rosną w +x) i próby ujemne `conn_turned` oraz `rows_swapped`. Elektrycznie przy obudowach z kluczem i taśmie 1:1 styk k zawsze łączy się ze stykiem k. Orientacja decyduje tylko o tym, czy taśmę trzeba skręcać.

## Elektryka

- **Łączenie wyłącznie po nazwie sieci, nigdy pin w pin.** Każdy pin dostaje sieć z pinoutu płytki (GND jawnie), wczytanego z tych samych plików co raport kontraktów. `src/kontrakt.py` sprawdza bloby git z `kontrakty.json`. Przykład z recenzji: P03 J_BP2 16/17/19/20 to PFAIL_N / 5V_SYS / 5V_SYS / 5V_SYS, a P05 J_BP2 16/17/19/20 to GND. Kontrole K5 (netlista) i „5V_SYS, 3V3_IO and GND separate” (PCB) mają próby ujemne: zwarcie 5V_SYS–GND i ścieżkę J3.17–J6.17.
- **27 sieci połączonych** (z GND), wśród nich 22 sieci sygnałowe.
  - 5V_SYS: J1.2/4/6 (źródło P02) → P03 J_BP2 17/19/20, P05 J_BP1 2/4, P09 J1 2/16, P06 J_BP 10/12, P10 J1 2/10 i TP2.
  - 3V3_IO: J1.8/10 → P03 J_BP3 5, P09 J1 4, P06 J_BP 14, P10 J1 4, P11 J_P12 20 i TP3.
- **Trzy sieci w stanie „czeka” są połączone:** ADC_SCLK i ADC_DOUTA (P03 ↔ P05 ↔ P06; czekają tylko na koniec P07) oraz TEST_KEY (P03 ↔ P11; czeka na P04). Ich końce LOGGER muszą być połączone, bo bez tego P06 nie dostanie zegara ani danych ADC, a TEST_KEY nie dojdzie z panelu. Brakujący koniec dojdzie w wariancie pełnym.
- **24 piny bez połączenia** (sieci, których drugi koniec jest na P04 / P07 / P08): `docs/NIEPODLACZONE.csv`. Na schemacie mają znacznik NC i opis z nazwą sieci.

  | Czeka na | Sieci (pin P12) |
  |---|---|
  | P04 | P02 J_BP: PSU_OK (J1.12), P04_3V3 (J1.15), SAFE_N (J1.16), PG_SEND (J1.17), PG_LINK (J1.18); P03 J_BP3: SENSOR_ENABLE (J4.9), SUP_N_OUT (J4.12), CORE_LINK (J4.13), PWM (J4.14), HEARTBEAT (J4.16), HW_ARMED (J4.17), MCU_ARM (J4.18), INTERLOCK (J4.20); P05 J_BP1: DAQ_OK (J5.6); P11 J_P12: PANEL_3V3 (J10.2), MECH_OK (J10.4), STOP_NC_OUT (J10.6), ARM_CONTACT (J10.8) |
  | P07 | P03 J_BP1: CS_ITEST_N (J2.4), ENA_DIAG (J2.17), ENB_DIAG (J2.18), MOTOR_INA (J2.19), MOTOR_INB (J2.20) |
  | P08 | P03 J_BP1: SENSOR_HEALTHY (J2.12) |

- **PG_SEND–PG_LINK:** P02 R4 ma na płytce zworę R34 0 Ω między PG_SEND a PG_LINK (specyfikacja P02 R4 Z-10, `ZADANIE-P02-R4-ETAP2.md`: „Zwora PG_SEND–PG_LINK zostaje na płytce”). P12 R1 jej nie powtarza, a piny J1.17/18 zostają wolne. Mostek na P12 dublowałby R34 (kontrola K8, próba `PG_SEND_PG_LINK_zmostkowane`).
- **Szerokości:** 5V_SYS 1,0 mm (klasa PWR, odstęp 0,3; budżet ok. 1,09 A, 3 styki źródła), 3V3_IO 0,5 mm (klasa P3V3), sygnały 0,3 mm (≥ 0,25), odstęp 0,25 mm.
- **GND:** wylewka na obu warstwach (F.Cu i B.Cu po ok. 85 %) z przelotkami GND (55: siatka 10 mm i przelotki routera do płaszczyzny). Linie SPI (ADC_*, SPI3_*, CS) biegną krótko i drzewem bez pętli, z GND po obu stronach.
- **Pola pomiarowe:** TP1 / TP4 GND, TP2 5V_SYS, TP3 3V3_IO — do pomiarów na stole przed włożeniem do obudowy.

## Wyniki (szczegóły: `verification/QA.md`, `verification/QA-PCB.md`)

| Kontrola | Wynik |
|---|---|
| Kontrakt (`src/kontrakt.py`) | 10 złączy, 172 piny, 7/7 źródeł z blobami jak w `kontrakty.json`, 0 błędów |
| ERC | 0 naruszeń (1 arkusz) |
| Netlista pin po pinie wobec `parts.py` | 14 części, 176 pinów, 0 błędów |
| Netlista wobec kontraktów (`src/verify_kontrakt.py`, K1–K10) | 10/10; próby ujemne 14/14 z zerową: zamieniony pin (2), brak sieci, brak końca, zwarcie 5V_SYS–GND, pin w pin J3/J6 (2), zły typ złącza (2), P04_3V3→3V3_IO, mostek PG, TP, dodatkowa część |
| DRC (świeży, wszystkie poziomy, parity) | 0 naruszeń / 0 niepołączonych / 0 niezgodności |
| Kontrole PCB (`src/verify_pcb.py`) | 21/21: położenia ±0,5 mm (zmierzone 0,00), orientacja, piny = kontrakt, M3 i strefy, szerokości, rozdział zasilań, dojście zasilań do źródła, GND, nadruk ≥ 1,0/0,15, bez nadruku na korpusach złączy i w strefach M3 |
| Próby ujemne PCB | 20/20 z zerową |
| Trasowanie | Freerouting 2.1.0, 1. próba (3 przebiegi), bez tras planera |

PDF przeglądowy `output/pdf/P12-R1-PCB.pdf` (5 stron: przegląd, montaż 1:1, F.Cu, B.Cu, geometria) obejrzany 4.10. Schemat: `output/pdf/P12-R1-schemat.pdf`.

## Decyzje (sporne oznaczone)

1. **Sporne:** sieci ADC_SCLK, ADC_DOUTA i TEST_KEY są połączone, choć zadanie mówiło „sieci czeka — nie łączymy”. Mają co najmniej dwa końce na płytkach LOGGER, a bez nich P06 i panel nie działają (wyżej).
2. **J10 (P11) w x 26,5 / z 14,05**, bez wydłużania P12 w stronę panelu (wyżej).
3. **Wysokość osi kątowego IDC 4,45 mm** z korpusu 8,9 mm (karty w repo brak). Odchyłkę pokrywa taśma.
4. Oznaczenia footprintów są ukryte, bo opis przy złączu zawiera oznaczenie (np. „J3  P03 J_BP2 (poziom 2, S2)”). Znacznik „1” stoi z lewej strony korpusu, na wysokości rzędu pinu 1.
5. Gniazda: Amphenol FCI T821 1xx A1**S**100CEU (proste, xx = 10 / 16 / 20) lub odpowiednik — kod „S” (proste) do potwierdzenia w zakupach. Taśmy: 6 × 2×10, 2 × 2×8, 2 × 2×5, w tym taśma P11 ok. 100 mm; gniazda IDC bez odciążki.

## Pytania do użytkownika

1. **Odstęp P12 od krawędzi A:** przyjąć 18–20 mm (gniazda „plecami do siebie”, taśma ok. 30 mm), czy wolisz więcej miejsca na pętlę (np. 22 mm, ściana A i tak jest 30 mm przed krawędzią)? Płytki to nie zmienia, tylko dystanse do ściany A.
2. **Taśma P11:** czy przy layoucie P11 dać J_P12 w rogu od strony krawędzi A i stosu (x ≈ −5…−15)? Wtedy taśma ma ok. 65–80 mm.
3. **Decyzja 1:** potwierdź połączenie ADC_SCLK / ADC_DOUTA / TEST_KEY w R1 (bez tego LOGGER traci P06 i kluczyk TEST).

## Uruchomienie

- Schemat: `scripts/egrlab-docker python3 src/run_schematic.py` (ok. 15 s).
- Całość: `scripts/egrlab-docker python3 src/run_release.py` (ok. 5 min). Odtwarza wynik routera `routing/P12.ses`; z `--new-route` uruchamia Freerouting od nowa.

## Zawartość

| Ścieżka | Zawartość |
|---|---|
| `src/kontrakt.py` | kontrakt pinowy z pinoutów płytek → `docs/kontrakt-P12.json`, `GEOMETRIA.csv`, `NIEPODLACZONE.csv` |
| `src/parts.py`, `build_schematic.py`, `cadlib.py` | schemat (jeden arkusz A3, układ jak na płytce) |
| `src/verify_kontrakt.py` | netlista wobec kontraktów + próby ujemne |
| `src/board.py`, `placement.py`, `build_board.py`, `export_dsn.py`, `prepare_routing.py`, `import_routing.py`, `cleanup.py`, `complete_routes.py`, `stitch.py`, `run_layout.py` | layout |
| `src/silkscreen.py`, `set_rules.py`, `set_stackup.py`, `verify_pcb.py`, `negative_controls.py`, `export_views.py`, `make_pdf.py`, `run_release.py` | nadruk, kontrole, PDF, wydanie |
| `eda/` | projekt KiCad (`P12.kicad_sch`, `P12.kicad_pcb`, biblioteki) |
| `verification/` | ERC, netlista, DRC z pokwitowaniem, kontrole, próby ujemne, QA, `manifest.json` |
