# M1 — audyt uproszczeń S1 (krok 1)

*8.10.2026. Gałąź `m1` z main (`bdbd348`, tag `s1-zamowienie`). Założenia użytkownika 8.10: świadomy użytkownik, wycinamy nadmiarowe zabezpieczenia, jak najprostsza konstrukcja spełniająca pierwotne funkcje, minimum płytek, bez nadmiarowych modułów i złączy; przewody zewnętrzne lutowane do PCB, w obudowie jedna listwa śrubowa, na zewnątrz kable przez mufy.*

Audyt jest na poziomie bloków (arkuszy schematu S1). Lista części powstaje w kroku schematu. **Do decyzji użytkownika** są punkty D-M1-1 … D-M1-9 na końcu.

## 1. Funkcje pierwotne (do potwierdzenia)

Na podstawie `Rewizje/EGRLab-v6.1-rc1/docs/00-zalozenia.md`, `01-architektura.md` i `ZALOZENIA-ROZWOJU-EGRLab.md`:

| # | Funkcja | Tryb |
|---|---|---|
| F1 | Zapis 8 napięć jednocześnie próbkowanych (AD7606B, 2 kS/s): odczepy na liniach ECU ↔ EGR (silnik, czujnik pozycji, zasilanie czujnika, masa) | LOGGER |
| F2 | Pomiar prądu silnika EGR w szeregu między ECU a zaworem (bocznik 5 mΩ + INA240) | LOGGER |
| F3 | Dwie temperatury (termopary K, MAX31856) | LOGGER / TESTER |
| F4 | Pasywny odczyt CAN z OBD (bez nadawania) | LOGGER |
| F5 | Napięcie akumulatora auta (VBAT) | LOGGER |
| F6 | Sterowanie zaworem na stole: mostek H, PWM, kierunek, pomiar prądu | TESTER |
| F7 | Zasilanie czujnika pozycji zaworu 5 V z ograniczeniem prądu | TESTER |
| F8 | Zapis na kartę SD, zegar / znacznik czasu, ESP32 (Waveshare), firmware 6.2 | oba |
| F9 | Zasilanie przyrządu z pakietu 4S 18650 (5 V / 3,3 V dla logiki, VMOTOR dla mostka) | oba |
| F10 | Obsługa: przycisk(i), LED stanu, start/stop zapisu | oba |

Poza zakresem M1 (było w S1 jako rozbudowa): wymienność modułów, druga marka EGR, P00 (stanowisko uruchomieniowe), port SCOPE / AUX jako złącze.

## 2. Kategorie

**F** funkcja (zostaje) · **Z** zabezpieczenie przed błędem użytkownika (wycinamy) · **A** zabezpieczenie auta / ECU / ogniw (oznaczone osobno, decyzja użytkownika) · **I** interfejs między płytkami (znika z podziałem) · **S** serwis (listwy J_SV → pola testowe) · **D** duplikat (szyny, nadzorcy, odsprzęganie powielone na każdej płytce).

## 3. Bloki S1

| Płytka / arkusz (części) | Zawartość | Kat. | M1 |
|---|---|---|---|
| **P02 WEJ** (37) | 2 × SUP53P06 przeciwsobnie (odwrotna polaryzacja + wyłącznik), szybkie wyłączanie bramki (Q2–Q5), TVS 5KP24A, F1 5 A, diody sumujące, podtrzymanie 2200 µF | Z / A / F | **F1 zostaje (A: pożar ogniw/przewodów).** Wyłącznik zasilania — zwykły przełącznik w obwodzie (F10). Odwrotna polaryzacja, TVS, podtrzymanie, szybkie wyłączanie — Z, wycięte |
| **P02 STER** (42) | LM2936, TL431, UVLO komparatorem, reset, ENABLE, PFAIL_N, SAFE_N/PG do P04, LED | Z / A / I | **UVLO pakietu — A** (głębokie rozładowanie ogniw; zbędne, jeśli pakiet ma własne BMS — D-M1-3). Reszta Z / I, wycięta |
| **P02 LV** (9) | TSR 2-2450, TSR 2-2433, F2 / F3 | F / Z | 5 V i 3,3 V zostają (2 przetwornice). F2 / F3 — Z |
| **P02 MON** (15) | PSU_OK (2 × MCP120, LVC125, HC08), VBAT przez R38 + TVS | D / F | VBAT: dzielnik do AD7606B lub ADC ESP32 (F5). PSU_OK — D, wycięte |
| **P03 P03** (19) | Waveshare ESP32, MCP23017, HC139 (dekoder CS), SD | F / I | ESP32 + SD zostają. MCP23017 i HC139 tylko jeśli zabraknie GPIO po wycięciu buforów (wstępnie: nie) |
| **P03 POWER** (21) | TPS3808, LTC4412 (USB / 5V_SYS), LVC1G37, LVC1G17 | Z / D | Wycięte; ESP32 z 3,3 V przyrządu, USB tylko do programowania przy zasilaniu z pakietu (D-M1-6) |
| **P03 IO / OUT** (42) | 7 × 74LVC125 (Ioff między domenami zasilania płytek) | I | Wycięte (jedna domena 3,3 V) |
| **P04 SAFE** (wszystkie, 100) | watchdog HC123, zatrzask HC74, STOP / ARM, blokady HC08, odbiorniki LVC125, MCP100 | Z / A | **Wycięte w całości.** Jedno do decyzji (A): niezależne od firmware wyłączenie mostka, gdy ESP32 się zawiesi (watchdog). Propozycja M1: enable mostka z GPIO + watchdog sprzętowy ESP32 (bez części) — D-M1-4 |
| **P05 ADC** (12) | AD7606B | F | Zostaje (F1) |
| **P05 READY** (20) | REF5025, TLV1702 (okno DAQ_OK), HC08, 2 × MCP120, LVC125 | D / Z | REF5025 do decyzji (AD7606B ma wewnętrzne 2,5 V; dokładność wystarczy) — wstępnie wycięte. Reszta D / Z |
| **P05 TAPS** (15) | 3 przekaźniki G6K + TBD62083 odłączające odczepy | A | Wejścia AD7606B mają 1 MΩ także bez zasilania i znoszą ±21 V. **A — propozycja: wyciąć** (D-M1-5) |
| **P05 DIG** (17) | 3 × LVC125 | I | Wycięte |
| **P05 P05** (15) | MCP1700 3V3_DAQ, odsprzęganie | D | Wspólne 3,3 V, wycięte |
| **P05 AUX** (11) | wejście koncentryczne AUX | S | Wycięte (oscyloskop podłącza się do zacisków listwy) |
| **P06 I-LOGGER** (74) | bocznik WSK2512 5 mΩ, INA240A2, MCP6022, MCP1525, MCP3201, LVC125, MCP1702, 2 × MCP120, HC08, BYPASS (SW1) | F / I / D / Z | **Bocznik + INA240 zostają; wyjście INA240 wprost na kanał AD7606B** (jednoczesne próbkowanie z napięciami, 16 bit). MCP3201, REF, bufory, nadzorcy — wycięte. BYPASS — Z |
| **P07 DRIVE** (132) | KPWR (przekaźnik), bocznik + INA240 + MCP3201 (ITEST), okno OC + zatrzask, logika blokady (3 × HC08, HC74, LVC14), AHCT125 do modułu IBT-2, PTC 5V_MOD | F / Z / A | **Mostek + jego sterowanie zostają.** Prąd TEST mierzy **ten sam** bocznik + INA240 co LOGGER (tryby się wykluczają: zawór jest albo w aucie, albo na stole) — D-M1-7. OC i zatrzask — Z (BTS7960 / VNH mają ochronę wewnętrzną). KPWR — Z. Blokada LOGGER / TEST — A (D-M1-4) |
| **P08 SENSOR** (52) | TPS2553 (5 V z limitem), przekaźnik rozłączający + i powrót, logika HC08, 2 × LVC125, 3 × MCP120 | F / A / D | **TPS2553 zostaje (F7; włączanie z GPIO).** Przekaźnik rozłączający powrót czujnika — A (nie podać 5 V na linię ECU, gdy podpięte jest auto) — D-M1-5. Reszta D / I |
| **P09 TEMP** (46) | 2 × MAX31856 XU (moduły), 2 × LVC125, HC139, zworki VIN | F / I | MAX31856 zostają (moduły albo układy — D-M1-2). Bufory, dekoder, zworki — wycięte |
| **P10 CAN** (20) | TCAN1051V, PESD2CAN, LVC125 | F / I | TCAN1051 + PESD2CAN zostają (PESD — A, 2 części, zostawiam). LVC125 — wycięty |
| **P11 PANEL** (5) | styki portów AT04, logika styków, SCOPE BNC | I / S | Wycięte (porty zastępuje listwa + mufy) |
| **P12** (20) | 16 gniazd IDC | I | Wycięta |
| **Listwy J_SV (wszystkie płytki, ok. 167 części)** | goldpiny + rezystory szeregowe | S | Zastąpione polami testowymi przy węzłach (0 części) |

## 4. Co zostaje (szacunek)

ESP32 (moduł Waveshare) + slot SD, AD7606B z filtrami i dzielnikami 8 kanałów, bocznik + INA240 (+ przełączanie toru LOGGER / TEST — D-M1-7), 2 × MAX31856, TCAN1051 + ESD, mostek H (moduł albo układ — D-M1-2), TPS2553, 2 przetwornice (5 V, 3,3 V), F1 + wyłącznik, 1–2 przyciski, 1–2 LED, odsprzęganie, pola przewodów.

**Ok. 110–150 części zamiast 818** (bez listew serwisowych, buforów, nadzorców i logiki blokad). Szacunek powierzchni (do sprawdzenia w kroku 3): **jedna płytka ok. 120 × 100 mm** przy montażu ręcznym, mniejsza przy PCBA.

## 5. Podłączenie zewnętrzne (listwa + mufy)

Wszystkie przewody zewnętrzne lutowane do pól na PCB (z otworami na opaskę jak J1–J4 w P07), w obudowie jedna listwa śrubowa, na zewnątrz kable przez mufy. Wstępna lista zacisków:

| Grupa | Zaciski | Przekrój |
|---|---|---|
| Pakiet 4S | +, − | 2,0 mm² |
| Auto: VBAT, masa auta | 2 | 0,5 mm² |
| ECU strona (LOGGER): silnik +/−, 5 V czujnika, sygnał pozycji, masa czujnika | 5 | silnik 2,0 / reszta 0,5 mm² |
| EGR strona (LOGGER i TESTER): te same 5 linii | 5 | jw. |
| CAN H, CAN L, masa (OBD) | 3 | skrętka |
| **Termopary 2 × (+/−)** | **— nie przez listwę** | patrz niżej |

**Uwaga techniczna (termopary):** przewód termopary nie powinien przechodzić przez miedzianą listwę śrubową — każde przejście K/Cu to dodatkowe złącze termoelektryczne i błąd pomiaru zależny od temperatury listwy. Propozycja: termopary wchodzą przez własną mufę wprost do zacisków MAX31856 (albo przez gniazdo termoparowe typu K w ściance) — D-M1-8.

TESTER: zawór na stole podłącza się do tych samych 5 zacisków strony EGR, a strona ECU zostaje wolna; tryb wybiera przełącznik albo firmware (D-M1-7).

## 6. Decyzje do podjęcia (rekomendacje)

| # | Pytanie | Rekomendacja |
|---|---|---|
| D-M1-1 | Montaż: ręczny czy PCBA w JLCPCB | **Ręczny** (części posiadane, SOIC / 1206 / LQFP64 AD7606B ręcznie jak w S1); PCBA rozważyć tylko przy chęci zmniejszenia płytki |
| D-M1-2 | Moduły czy układy: MAX31856 (moduły XU), mostek (IBT-2 poza płytką / VNH5019 na płytce / BTS7960 na płytce), ESP32 (moduł Waveshare) | MAX31856 — **moduły** (posiadane, sprawdzone 8.10); mostek — **IBT-2 poza płytką** (posiadany, radiator, 10 A; na płytce 4 linie sterowania przez jeden 74AHCT125 — 74HC244 modułu przy 5 V wymaga ok. 3,5 V na wejściu, 3,3 V z ESP32 to za mało); ESP32 — **moduł** |
| D-M1-3 | UVLO pakietu (ochrona ogniw przed głębokim rozładowaniem) | **Wyciąć, jeśli pakiet 4S ma BMS**; jeśli nie — zostawić jeden komparator + MOSFET (A) |
| D-M1-4 | Niezależne od firmware wyłączenie mostka / blokada LOGGER–TEST | **Wyciąć**; enable mostka z GPIO z pull-down (mostek wyłączony, gdy ESP32 w resecie) + watchdog ESP32 |
| D-M1-5 | Przekaźniki odłączające: odczepy DAQ (3 × G6K) i powrót czujnika (P08) | Odczepy — **wyciąć**. Czujnik — **zostawić TPS2553 bez przekaźnika** (5 V wyłączone w LOGGER) |
| D-M1-6 | Zasilanie z USB | Tylko programowanie; zasilanie przyrządu wyłącznie z pakietu |
| D-M1-7 | Jeden tor prądu dla LOGGER i TESTER | **Tak, jeden bocznik + INA240 na kanale AD7606B**; tryb wybiera użytkownik **przepięciem dwóch przewodów silnika na listwie** (ECU albo wyjścia IBT-2 na wejście bocznika) — bez przełącznika; alternatywa: przełącznik 2 × 10 A |
| D-M1-8 | Termopary | Własna mufa wprost do MAX31856 (bez listwy) |
| D-M1-9 | Liczba płytek | **Jedna** (IBT-2 osobno jako posiadany moduł) |

**8.10 — decyzje użytkownika: wszystkie rekomendacje przyjęte.** D-M1-3: pakiet 4S z posiadanym modułem BMS / PCM 4S 14,8 V 40 A (Allegro, kupiony hurtem) — ochrona ogniw (przeładowanie, głębokie rozładowanie, przeciążenie) jest w BMS, UVLO na płytce wycięte. Próg odcięcia BMS i obecność balansowania odczytać z etykiety / karty modułu przy odbiorze; przyrząd pracuje w całym zakresie 4S (ok. 10–16,8 V).

Po decyzjach: krok 3 (specyfikacja, budżet zasilania, lista zacisków jako kontrakt, plan płytki), potem schemat z jednego generatora.
