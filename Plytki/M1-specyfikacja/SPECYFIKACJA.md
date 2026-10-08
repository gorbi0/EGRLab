# M1 — specyfikacja (krok 3)

*8.10.2026. Na podstawie `AUDYT.md` (decyzje D-M1-1…9 przyjęte). Jedna płytka, montaż ręczny, IBT-2 poza płytką, przewody lutowane do PCB, w obudowie jedna listwa śrubowa X1, kable na zewnątrz przez mufy. Punkty do decyzji: D-M1-10…13 na końcu.*

## 1. Schemat blokowy

```
Pakiet 4S + BMS ──X1──► PCB: F1 7,5 A ─┬─► VMOTOR ──X1──► IBT-2 B+ / B−
                                        ├─► TSR 2-2450 ─► 5V ─┬─► ESP32 DEV-KIT (5V), AD7606B AVCC, INA240, TPS2553, IBT-2 VCC
                                        │                     └─► TPS2553 ─► SENS_5V ──X1──► czujnik EGR (TESTER)
                                        └─► TSR 2-2433 ─► 3V3 ──► AD7606B VDRIVE, MAX31856 ×2, TCAN1051 VIO, karta SD
X1 P1_ECU ──► bocznik 5 mΩ (Kelvin → INA240 → AD7606B CH6) ──► X1 P1_EGR      (jedyna linia przez PCB)
X1 P3, P4, P5, P6 (ECU i EGR na jednym zacisku) ── cienki odczep ──► dzielnik + RC ──► AD7606B CH1…CH5
X1 VBAT_CAR ──► dzielnik ──► AD7606B CH7;  CH8: SENS_5V (kontrola zasilania czujnika w TESTER)
ESP32-S3: SPI2 → AD7606B; SPI3 → SD + MAX31856 ×2; TWAI → TCAN1051 ──X1──► CAN H / L;  GPIO → 74AHCT125 → IBT-2 (RPWM, LPWM, EN)
Termopary 2 × K ── osobna mufa ──► wprost do zacisków modułów MAX31856 (nie przez X1)
```

## 2. Kanały AD7606B (±10 V, oversampling ×8, 2 kS/s)

| Kanał | Sygnał | Tor (jak S1 P05, klasy z `electrical-checks.json`) |
|---|---|---|
| CH1 | P1 (silnik, za bocznikiem — strona EGR) | MOTOR: 300 k / 100 k + RC |
| CH2 | P3 (silnik) | MOTOR |
| CH3–CH5 | P4, P5, P6 (czujnik: zasilanie / masa / sygnał w nieznanej permutacji — firmware rozpoznaje) | SENSOR: 100 k szeregowo + RC |
| CH6 | prąd silnika: INA240A2 (×50) z bocznika 5 mΩ, REF1 = 5 V, REF2 = GND (wyjście w połowie VS, bez bufora odniesienia), 1 k / 1 n do kanału | 2,5 V + 0,25 V/A; liniowo ok. ±9 A (powyżej F1 7,5 A); zero zapisywane przy wyłączonym silniku |
| CH7 | VBAT auta | VSENSE: 499 k / 100 k + RC |
| CH8 | SENS_5V (wyjście TPS2553) | SENSOR |

Był w S1: CH6 zakończony 10 k (rezerwa), CH8 AUX — oba odzyskane. Prąd próbkowany jednocześnie z napięciami (koniec opóźnienia MCP3201).

## 3. Piny ESP32-S3 (Waveshare ESP32-S3-DEV-KIT-N32R16V, posiadany, na listwach 2 × 1×22)

Numeracja jak firmware 6.2-s1 (`board.c`) tam, gdzie sygnał został; nowe przypisania na pinach zwolnionych przez I²C / MCP23017. Zakazane jak w P03 R6: GPIO0/45/46 (start), 19/20 (USB), 33–37 (pamięć oktalna), 43/44 (CH343P), 47/48 (domena 1,8 V).

| GPIO | Sygnał | 6.2-s1 |
|---|---|---|
| 9 / 11 / 2 / 12 | ADC SCLK / DOUTA / SDI / CS (SPI2) | bez zmian |
| 13 / 14 | CONVST / BUSY | bez zmian |
| 10 | ADC RESET | było SDA I²C (reset przez MCP23017) |
| 4 / 5 / 6 | SPI3 SCK / MOSI / MISO | bez zmian |
| 7 / 8 / 16 | CS karty SD / CS TC1 / CS TC2 (10 k do 3V3) | bez zmian; SDO modułów MAX31856 przez 74LVC125 z OE = CS na wspólne MISO (SDO modułu nie jest gwarantowanie w stanie Z — funkcja, nie zabezpieczenie) |
| 17 / 18 | TWAI TX (niepodłączony: TXD i S transceivera na 3V3, odbiór cichy) / RX przez 100 R | bez zmian |
| 1 | RPWM (LEDC) → 74AHCT125 → IBT-2; 100 k do GND | było PWM (bramki AND na P07) |
| 21 | LPWM (LEDC) → 74AHCT125 → IBT-2; 100 k do GND | było HEART (8.10: GPIO38 steruje diodą RGB modułu) |
| 39 | DRIVE_EN → 74AHCT125 → IBT-2 R_EN + L_EN; 100 k do GND (mostek wyłączony w resecie ESP32) | było ARM |
| 40 | SENS_EN → TPS2553 EN; 100 k do GND | było HW_ARM |
| 42 | SENS_FAULT_N ← TPS2553 (otwarty dren, 10 k do 3V3) | było INTERLOCK |
| 15 | przycisk START / STOP (do GND, 10 k do 3V3) | było SCL I²C |
| 38 | LED stanu = dioda RGB modułu DEV-KIT (bez części na płytce) | było CURRENT_CS |
| 41 | wyzwalacz oscyloskopu — pole testowe | bez zmian (SCOPE) |
| 3 | wolny (pole testowe) | było PFAIL_N |

21 pinów zajętych, bez ekspandera i dekodera. IS modułu IBT-2 (R_IS / L_IS) nieużywane — prąd mierzy INA240.

## 4. Budżet zasilania

| Szyna | Odbiorniki (typ. / szczyt) | Źródło |
|---|---|---|
| Pakiet 4S, 10–16,8 V | wszystko; silnik EGR 1,5–3,5 A (próba bierna toru do 10 A) | BMS 40 A, F1 7,5 A MINI na PCB |
| 5 V | ESP32 DEV-KIT (do ok. 350 mA przy Wi-Fi), AD7606B AVCC ok. 25 mA, INA240 2 mA, IBT-2 VCC ok. 20 mA, 74AHCT125 1 mA, TPS2553 (czujnik ok. 10 mA, limit ok. 100 mA) | TSR 2-2450 (2 A) |
| 3,3 V | karta SD do 100 mA, MAX31856 ×2 (moduły, VIN = 3,3 V) ok. 5 mA, AD7606B VDRIVE 1 mA, TCAN1051V VIO 1 mA | TSR 2-2433 (2 A) |

Razem z 5 V ok. 0,45 A szczytowo, z 3,3 V ok. 0,15 A: zapas kilkukrotny. ESP32 ma własne LDO modułu z 5 V; peryferia z osobnego 3,3 V (wspólna masa).

## 5. Listwa X1 (kontrakt — tak jak dawne J_BP)

ECU i EGR tej samej linii lądują na **jednym zacisku** (przelotowo w listwie) — przez PCB przechodzi tylko P1 (bocznik). Do pozostałych zacisków z PCB idzie cienki odczep.

| X1 | Sieć | Przewód PCB ↔ listwa | Uwagi |
|---|---|---|---|
| 1 / 2 | BAT+ / BAT− (pakiet za BMS) | 2,0 mm² | |
| 3 / 4 | VMOTOR (za F1) → IBT-2 B+ / IBT-2 B− (X1.4 zmostkowany z X1.2 na listwie, bez PCB) | 2,0 mm² | jedna masa GND na PCB; prąd silnika nie płynie przez płytkę |
| 5 | P1_ECU (silnik od ECU; w TESTER: IBT-2 M+) | 2,0 mm² | wejście bocznika |
| 6 | P1_EGR (silnik do zaworu) | 2,0 mm² | wyjście bocznika |
| 7 | P3 (silnik; ECU / zawór; w TESTER: IBT-2 M−) | 0,25 mm² odczep | przelotowo w listwie |
| 8 / 9 / 10 | P4 / P5 / P6 (czujnik) | 0,25 mm² odczepy | przelotowo |
| 11 | SENS_5V (TESTER: do pinu zasilania czujnika) | 0,5 mm² | |
| 12 | GND przyrządu / masa auta (odniesienie pomiarów) | 0,5 mm² | **w LOGGER podłączyć do masy auta** |
| 13 | VBAT_CAR (akumulator auta, pomiar) | 0,25 mm² | |
| 14 / 15 / 16 | CAN_H / CAN_L / CAN_GND | skrętka 0,25 mm² | |

**Tryby (świadomy użytkownik, przepięcia na listwie):** LOGGER — X1.5 = przewód silnika od ECU, X1.6 = przewód do zaworu, czujnik ECU ↔ zawór przelotowo na X1.8–10, SENS_EN wyłączone. TESTER — przewód ECU odpięty z X1.5, na X1.5 / X1.7 wyjścia IBT-2 M+ / M−, X1.11 do pinu zasilania czujnika, X1.12 do masy czujnika.

Kontrola schematu i PCB (jak `verify_s1`): każda sieć z tabeli ma pole przewodu na PCB, pola przy jednej krawędzi w kolejności X1, przekroje jak w tabeli.

IBT-2 (logika): pola na PCB dla RPWM, LPWM, R_EN, L_EN, VCC (5 V), GND — przewody lutowane do listwy kołkowej modułu (bez złącza na PCB).

## 6. Plan płytki (wstępny)

- Jedna płytka ok. 120 × 100 mm; **4 warstwy** (D-M1-10): In1 GND pod AD7606B / INA240 / Kelvinem, tor 10 A tylko w P1 (X1.5 → bocznik → X1.6) — krótki, przy krawędzi pól.
- Krawędź „listwy”: pola przewodów w kolejności X1 z otworami na opaski.
- Róg mocy: BAT, F1, VMOTOR, przetwornice; obok bocznik + INA240.
- Środek: AD7606B z dzielnikami ośmiu kanałów (kolumna filtrów jak P05 R3).
- Przeciwległa krawędź: ESP32 DEV-KIT (USB dostępne z obudowy, antena poza miedzią), moduł SD Adafruit 4682 (posiadany).
- Krawędź termopar: 2 × MAX31856 XU (terminale termopar w stronę muf).
- TCAN1051 + PESD2CAN przy polach CAN; 74AHCT125 przy polach IBT-2.
- Pola testowe (bez listew) przy szynach i kanałach; GPIO3 / GPIO41 jako pola.

## 7. Decyzje (rekomendacje)

| # | Pytanie | Rekomendacja |
|---|---|---|
| D-M1-10 | 2 czy 4 warstwy | **4** — płaszczyzna GND pod AD7606B i INA240, trasowanie bez walki (lekcja P07) |
| D-M1-11 | Moduł SD | **posiadany Adafruit 4682** na listwie 1×9 lutowanej (bez gniazda) |
| D-M1-12 | Moduły MAX31856 i ESP32: wlutowane wprost czy na gniazdach | **wlutowane wprost** (jak decyzja P09 1.10) — mniej złączy; ESP32 DEV-KIT także na kołkach lutowanych |
| D-M1-13 | Bezpiecznik F1 | **MINI 7,5 A w oprawce lutowanej** (jak decyzja 5.10 dla P02) |

**8.10 — D-M1-10…13 przyjęte przez użytkownika** (4 warstwy, Adafruit 4682 wlutowany, moduły MAX31856 i ESP32 wlutowane wprost, F1 MINI 7,5 A w oprawce lutowanej).

**8.10 — poprawki przy schemacie (krok 4):** LPWM na GPIO21 (GPIO38 = dioda RGB modułu, ona jest LED stanu); bufor MISO 74LVC125 dla modułów MAX31856; IBT-2 B− na listwie (X1.4 zmostkowany z X1.2), na PCB jedna masa; INA240 z REF1 = 5 V / REF2 = GND bez bufora odniesienia (zakres liniowy ok. ±9 A zamiast deklarowanych ±10 A — wystarcza, bo F1 ma 7,5 A).

Krok 4 — schemat z jednego generatora: `Plytki/M1-R1-review` (`src/parts.py`, `verification/QA.md`).
