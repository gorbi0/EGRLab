# Końcowa recenzja P03-R2 (CORE)

27.09.2026 · Claude. Przedmiot: `Plytki/P03-R2-review` Astry (26.09.2026), wykonane po recenzji mojego R1 (`Plytki/P03-R1-recenzja-Codex`). Pakiet nietknięty. Zakres: poprawność, wykonalność i zgodność z interfejsami, bez oceny zasadności.

## Werdykt

**W schemacie i PCB nie ma blokera.** Wszystkie siedem uwag z recenzji R1 jest zamkniętych poprawnie. Sprawdziłem to w netliście i w kartach katalogowych, nie tylko w raportach. Interfejsy zgadzają się pin w pin z zamkniętymi P02-R3 (LV03) i P04-R2.1 (H_SAFE) oraz z P05-R1 (B2B).

Znalazłem dwie rzeczy do zmiany wartości lub skryptów i jedno odstępstwo od karty katalogowej, które wymaga decyzji:

- CORE_LINK wychodzi na złącze przez 0 Ω.
- Próby ujemne nie mają czystego punktu odniesienia DRC. To błąd mojego kodu z R1, przeniesiony do R2.
- **Wspólny reset daje na złączu do P04 zbocze rzędu milisekund.** Wejście 74LVC125A w P04 dopuszcza 10 ns/V. Skutki analizuję niżej: występują w stanie rozbrojonym. Usunięcie wymaga nowego trasowania.

Rewizja zamykająca bez zmiany miedzi: `Plytki/P03-R3-review`. Warunkiem zamówienia PCB pozostaje zatwierdzony przekrój mechaniczny pary B2B P03–P05.

## Co sprawdziłem

| Kontrola | Wynik |
|---|---|
| Integralność pakietu | 155/155 plików zgodnych z manifestem, SHA256 ZIP zgodny |
| ERC / netlista (świeży eksport) | 0 naruszeń, 5 arkuszy; 88 części, 421 pinów, 129 sieci — identyczne z `verification/P03.xml` |
| DRC (świeży, wszystkie ważności, zgodność ze schematem, wypełnienie stref) | 0 / 0 / 0 |
| Pełna regeneracja w osobnej kopii (`run_release.py`) | PCB 29/29, funkcje 48/48, próby 15/15 i 33/33; `rebuild-compare.py`: wszystkie kategorie zgodne, XOR wypełnień 0 mm² na obu warstwach |
| Niezależna analiza netlisty (`skrypty/analiza_netlisty.py`) | Szyny na złączach, węzeł EN na złączu, stan wejść buforów, interfejsy P02/P04/P05 |
| Karty katalogowe | LTC4412 (Linear 4412f: funkcje pinów s. 5, działanie s. 6 i 8), 74LVC125A (Nexperia Rev. 12, tab. 5–6), SN74LVC1G07, TPS3808, AO3401A, MCP23017 DS20001952 (DC), schemat rodziny Waveshare |
| Geometria B2B P03 J1 ↔ P05 J1 | Pin n na tej samej wysokości y; rzędy parzyste po obu stronach bliżej krawędzi (dolny rząd kątowy) — bez lustrzanego odwrócenia |
| Oględziny | 5 arkuszy A3 i 4 strony PCB; montaż SMD w powiększeniu 400 dpi |

## Uwagi z R1 — stan

| R1 | Zamknięcie w R2 | Moja weryfikacja |
|---|---|---|
| P03-01 stany przed buforami | R15–R25 po stronie `_SRC` | Każde wejście 74LVC125A ma dokładnie jeden rezystor. Wyjątek: CS_ILOG/CS_ITEST, sterowane stale aktywnym 74HC139, który przy GPIO38 w powietrzu blokuje R1. Żaden z używanych GPIO nie jest pinem konfiguracyjnym (strapping: 0, 3, 45, 46 — wszystkie NC) |
| P03-02 reset MCU/MCP | TPS3808 → U4 (OD) → R34 → SUP_N = EN + RESET MCP + P04 | Poprawne logicznie. RESET MCP23017 ma przerzutnik Schmitta (VIL 0,2 VDD, VIH 0,8 VDD), więc wolne zbocze mu nie szkodzi. Stan niski ≈ 0,25 V (U4 ≤ 0,1 V przy 0,66 mA + 0,15 V na R34), a nie „< 0,7 V” z dokumentu — 0,7 V byłoby powyżej 0,66 V. Zob. P3-01 |
| P03-03 USB → 5V_SYS | LTC4412 + AO3401A (D = SYS, S = M1) | Karta LTC4412: zasilają go **oba** piny, VIN i SENSE, a bramka jest klampowana 7 V poniżej wyższego z nich. Bez P02 (VIN = 0), z USB na SENSE, układ jest w trybie wyłączenia wstecznego, a dioda D→S jest zaporowa. Wyprowadzenia AO3401A: G1 S2 D3, RDS(on) < 60 mΩ przy −4,5 V |
| P03-04 C3 | C3 przy VDD = pin 6 | Potwierdzone; kontrola i mutacja istnieją |
| P03-05 samodzielność | footprinty w `reference/footprints` | Moja regeneracja w osobnej kopii zgodna co do geometrii |
| P03-06 wejścia odłączonych modułów | R26–R33 | Poprawne. Uwagi interfejsowe P3-04 i P3-05 |
| P03-07 czytelność | 5 arkuszy A3 | Bez kolizji, tytuły mieszczą się |

## Uwagi

| ID | Waga | Stan w R2 | Propozycja |
|---|---|---|---|
| P3-01 | średnia, do decyzji | SUP_N łączy J4.15 (do P04) z EN modułu, który ma 10 kΩ/1 µF. Narastanie: τ = (R35 ∥ 10 kΩ modułu) × 1 µF ≈ 5 ms, czyli ok. 2,8 ms/V przy progu. Opadanie przez R34: τ ≈ 0,22 ms. P04 odbiera SUP_N na **74LVC125A (U9), który wymaga Δt/ΔV ≤ 10 ns/V** (Nexperia Rev. 12, tab. 5). Grozi to seriami impulsów na SUP_N_P04/SUP_OK przy zwolnieniu i narzuceniu resetu. Analiza P04-R2.1: zatrzask ARM (HC74) nie ustawi się, bo jego zegar pochodzi wyłącznie z przycisku ARM (przez HC14), a PRE = H. Przy zwolnieniu resetu HEARTBEAT = L (MCU w resecie), więc HC123 nie wyzwala. Przy zapadzie MCU może jeszcze działać: możliwe krótkie wznowienia WD_Q/SENSOR_PERMIT w czasie trwania serii, bez HW_ARMED. Stan końcowy zawsze jest rozbrojony. | R3: bez zmiany miedzi. Opis w `ZASILANIE-RESET.md` i nowa próba w ODBIOR: oscyloskop na SUP_N_P04 (U9.6) i SUP_OK (TP4 P04) przy zwolnieniu i narzuceniu resetu CORE, razem z E16 P04. **Czyste rozwiązanie:** bufor Schmitta SN74LVC1G17 (DBV, jak U4) z szeregowym rezystorem przed J4.15. Wymaga nowego trasowania i ponownej recenzji layoutu, więc zostawiam do Twojej decyzji |
| P3-02 | drobna | R14 = 0 Ω: J4.13 CORE_LINK to bezpośrednio 3V3_CORE. W taśmie IDC sąsiaduje z J4.14 GND. Zwarcie żył zwiera LDO modułu. Wszystkie inne źródła 3,3 V na złączach EGRLab mają już rezystory (P04 R2) | **R14 = 1 kΩ** (ta sama obudowa). P04 widzi ≥ 2,85 V (10 kΩ, VIH 2,0 V); zwarcie to 3,3 mA. Nowa kontrola „szyna na złączu przez < 100 Ω” z mutacją |
| P3-03 | drobna (weryfikacja) | Każda kopia w próbach ujemnych dostaje 30 × `lib_footprint_issues` (brak tabeli bibliotek w katalogu kopii). Kontrola „Fresh native DRC” oblewa więc wszystkie 15 kopii, także bez wady miedzi. Wykrycie `dangling_lock` przypisane DRC nie jest dowodem (wadę łapie też kontrola zablokowanych segmentów). **To mój kod z R1** — ten sam błąd był w P00-R2 | Tabela bibliotek w kopii i próba zerowa: kopia bez wady = wszystko PASS, czysty DRC |
| P3-04 | uwaga interfejsowa | CAN_RX ma 10 kΩ do 3V3_CORE po stronie złącza. To poprawny stan recesywny, ale przy wyłączonym P10 do 0,35 mA wpływa do jego RXD | Wymaganie dla P10: RXD odporny na wstrzyknięcie (Ioff lub rezystor szeregowy na P10). Zapis w `ZALOZENIA` |
| P3-05 | uwaga interfejsowa | SPI3_MISO łączy karty SD (na płytce) z P09 (J7.5). Adafruit 4682 ma drabinki „473” (47 kΩ, najpewniej podciąganie linii SD); z R33 10 kΩ spoczynkowo daje to ≈ 0,58–0,61 V, czyli poprawne L (VIL 0,8 V) | Wymaganie dla P09: wyjście MISO w wysokiej impedancji także bez zasilania P09, bo inaczej odczyt SD w trybie USB-only się posypie. Wpis do `ZALOZENIA` |
| P3-06 | drobna (dokument) | `ZASILANIE-RESET.md`: „LOW pozostaje poniżej 0,7 V” — próg MCP to 0,66 V. Brak lokalnej kopii karty LTC4412 | Poprawić liczby (≈ 0,25 V); dołączyć kartę LTC4412 do `reference/datasheets` |

## Potwierdzone bez uwag

LV03 (P02-R3 J3), H_SAFE (P04-R2.1 J2) i DAQ (P05-R1 J1) zgadzają się pin w pin. W B2B pin n leży na tej samej wysokości, a rzędy nie są zamienione. Domyślnie nieaktywne są CS ADC/TC/SD/ILOG/ITEST, a MEAS_EN, ADC_RESET i CONVST są w L. Po resecie MCP23017 (IODIR = 0xFF, GPPU = 0) stan wyznaczają rezystory. Zasilanie buforów z 3V3_CORE z Ioff, bez połączenia 3V3_CORE–3V3_IO. SMD: U4 SOT23-5, U5 TSOT23-6, Q1 SOT23, C12–C14 1206 z oznaczeniem pinu 1, bez QFN/BGA. Tor 5 V ma 1 mm, a C3 stoi przy VDD6. Odtwarzalność pakietu jest pełna.

## Pozostaje otwarte (bez zmian)

- Przekrój mechaniczny pary B2B (konkretne MPN, wysokości rzędów, szczelina między płytkami) przed zamówieniem P03 i P05.
- Antena (Wi-Fi do pomiaru na gotowym zestawie).
- Temperatura LDO modułu i zapas 5V_M1 ≥ 4,60 V.
- Zbocza SPI na końcu P05/P09 i dobór R36–R40.
- Wszystkie próby sprzętowe z `ODBIOR.md`.

## Pliki recenzji

`skrypty/analiza_netlisty.py` + `.json`, `skrypty/rebuild-r2.log`, `work/` (kopia z odtworzonymi kontrolami), `rebuild/` (pełna regeneracja), `fresh/` (świeże ERC/DRC/netlista).

## Dopisek po przebiegu R3 (27.09.2026)

Tego dnia Astra wydała P06-R1, P08-R1, P09-R1 i P10-R1. Ich złącza zgadzają się pin w pin z P03: P06 J2 = J2 (ILOG), P08 J3 = J6 (SFAULT), P09 J2 = J7 (TEMP), P10 J2 = J8 (CAN). Wymagania P3-04 i P3-05 są w nich już spełnione. P10 ma bufor RX 74LVC125A z Ioff, który oddziela wyłączoną P10 od podciągania CAN_RX na P03. P09 ma 74LVC125A z Ioff, a jeden MISO wybiera 74HC139. Obie uwagi zostają jako wymagania do utrzymania w ich recenzjach.
