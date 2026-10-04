# Formularz odbioru S1 (LOGGER) — do wydruku

*Wersja 1, 4.10.2026. Identyfikatory i kryteria jak w `URUCHOMIENIE.md` (tam też punkty pomiarowe i co sprawdzić przy wyniku złym). Kolumna „Oczekiwane” to skrót — przy wątpliwości rozstrzyga `URUCHOMIENIE.md`. Wpisz zmierzoną wartość z jednostką, a w ostatniej kolumnie OK / NIE / — (nie dotyczy). Puste pole = NIE ZBADANO. Oscylogramy zapisuj na pendrive DHO804 jako `<ID>.png` (np. `LOG-01.png`) i dopisz nazwę pliku w uwagach.*

Wydruk: A4 poziomo; każda płytka zaczyna się od nowej strony (w edytorze lub przeglądarce: podział strony przed nagłówkiem „##”).


## Zwarcia i oględziny (rozdz. 2)

Płytka / egzemplarz: P02 ____ P03 ____ P05 ____ P06 ____ P09 ____ P10 ____

| ID | Czynność | Oczekiwane | Zmierzono | OK / NIE |
|---|---|---|---|---|
| Z-01 | wszystkie: oględziny pod lupą: mostki, polaryzacja elektrolitów i diod, pin 1 … | brak uwag | | |
| Z-02 | P02: J_BP.2–J_BP.1 (5V_SYS), J_BP.8–.7 (3V3_IO), J_BP.20–.19 (VBAT_SENSE) … | > 100 Ω, rośnie (szac.); zwarcie < 10 Ω | | |
| Z-03 | P02: kołki J_SV2: 4 VMOTOR, 5 BAT_IN, 8 SW_COM, 9 VSW, 10 VLOG, 12 HOLD_C … | odczyt wyraźnie większy niż rezystor szeregowy; ≈ 4,70 kΩ / 1,00 kΩ = zwarcie węzła | | |
| Z-04 | P03: J_BP2.17–.15 (5V_SYS), J_BP3.5–.3 (3V3_IO); J_SV1.10 3V3_CORE i … | jak Z-02 / Z-03 | | |
| Z-05 | P03: J_SV1.9 (3V3_IO) – J_SV1.10 (3V3_CORE) | wyraźnie > 2,0 kΩ; ≈ 2,00 kΩ = szyny zwarte ze sobą (zakazane) | | |
| Z-06 | P05: J_BP1.2–J_BP1.1 (5V_SYS); J_SV1.6 3V3_DAQ – J_SV1.7 (1 kΩ); U1: piny … | jak Z-02 / Z-03 | | |
| Z-07 | P05: każdy kołek J_SV1/J_SV2 do swojego węzła … | wartość rezystora ± 1 % | | |
| Z-08 | P06: J_BP.10–.9 (5V_SYS), J_SV2.3 5VA_P06 i J_SV2.4 3V3_P06 (1 kΩ) do GND; … | jak Z-02 / Z-03; tor mocy bez połączenia z GND | | |
| Z-09 | P09: J1.2–J1.1 (5V_SYS), J1.4–J1.3 (3V3_IO); J2 kołki 2–12 do węzłów | > 100 Ω; 1 kΩ ± 1 % | | |
| Z-10 | P10: J1.2–J1.1, J1.4–J1.3; J2 kołki 2–6 (1 kΩ), 7–8 (10 kΩ); J3 H–L: brak … | > 100 Ω; rezystory ± 1 %; H–L wysoka rezystancja | | |

Uwagi / odstępstwa: ____________________________________________________________________________

Decyzja: odebrana / odebrana z uwagami / nieodebrana     Podpis: ______________________  Data: ____________


## P02 R4 — zasilanie z pakietu 4S (rozdz. 3)

Egzemplarz P02 R4: ________  Numer PCB / data produkcji: ________  Data odbioru: ________

Przyrządy (multimetr, zasilacz, DHO804, sondy): ______________________________________  Temperatura otoczenia: ______ °C

| ID | Czynność | Oczekiwane | Zmierzono | OK / NIE |
|---|---|---|---|---|
| P02-01 | 10,0 V, limit 50 mA, PWR rozwarty → prąd zasilacza | < 15 mA (szac.); nic się nie grzeje | | |
| P02-02 | J_SV2.5 BAT_IN, J_SV2.8 SW_COM | BAT_IN = zasilacz; SW_COM = zasilacz − 0…0,7 V | | |
| P02-03 | J_SV1.9 AUX5; J_SV1.11 REF | AUX5 4,85–5,15 V; REF 2,483–2,507 V (multimetr 10 MΩ przez 10 kΩ zaniża o ok. 2,5 mV) | | |
| P02-04 | J_SV1.8 OK, J_SV1.2 ENABLE, J_SV2.9 VSW, J_SV1.10 PFAIL_N; … | OK i ENABLE ≤ 0,4 V; VSW ≈ 0 V; PFAIL_N ≈ 0 V (3V3_IO brak, F3 wyjęty); LED zgaszona | | |
| P02-05 | 12,0 V, PWR zwarty, limit 1,0 A; zasilacz powoli w górę do … → J_SV2.9 VSW (multimetr) albo LED; napięcie zasilacza na … | załączenie 12,90–14,08 V (nom. 13,50), wyłączenie 11,98–13,11 V (nom. 12,55), histereza ≥ 0,84 V, bez migania … | | |
| P02-06 | Załączenie przy 14,5 V z limitem 1,0 A → prąd zasilacza | krótkie wejście zasilacza w ograniczenie (do ok. 50 ms) jest oczekiwane: C12 2200 µF ładuje się przez R40 22 … | | |
| P02-07 | 14,5 V, włączone → J_SV2.2 GATE, J_SV2.10 VLOG, J_SV2.12 HOLD_C, J_SV1.8 OK, … | GATE co najmniej 8 V poniżej SW_COM (szac.); VLOG = VSW − ok. 0,5 V; HOLD_C = VSW − ok. 0,3 V po ok. 0,3 s; … | | |
| P02-08 | Pakiet 3S i odwrócone ogniwo: PWR rozwarty, ustaw 12,6 V, … → LED, VSW | brak startu w obu przypadkach (O-03) | | |
| P02-09 | Szybkość narastania VSW: PWR zwierany przy 14,5 V → DHO804: CH1 J_SV2.9 VSW, 5 V/dz, 1 ms/dz, wyzwalanie … | narastanie VSW 5–15 V/ms (nom. 11,5 V/ms; O-04, Z-07) | | |
| P02-10 | PWR rozwarty, włóż F2 (TSR 5 V), PWR zwarty → J_BP.2–.1 (5V_SYS) | 4,90–5,10 V (TSR ± 2 %) | | |
| P02-11 | PWR rozwarty, włóż F3 (TSR 3,3 V), PWR zwarty → J_BP.8–.7 (3V3_IO); J_SV1.3 SUP5_N; J_SV1.4 PSU_OK; … | 3V3_IO 3,23–3,37 V; SUP5_N, PSU_OK, PFAIL_N ≥ 3,0 V | | |
| P02-12 | prąd zasilacza przy 14,5 V bez obciążenia | zapisać (oczekiwane kilkadziesiąt mA (szac.)) | | |
| P02-13 | Makieta komplet LOGGER: PWR rozwarty, na pigtailu J_BP … → DHO804 jak w 9.1 (CH1 5V_SYS na J_SV2.11, CH2 PSU_OK … | jak kryterium 9.1: narastanie monotoniczne, bez restartów (foldback), 5V_SYS po starcie 4,90–5,10 V pod 1 A | | |
| P02-14 | Podtrzymanie (O-05, wyłącznik): obciążenie 4,7 Ω (≈ 6 W z … → DHO804: CH1 J_SV1.10 PFAIL_N (wyzwalanie opadające 1,6 V, 5 … | od zbocza PFAIL_N do 5V_SYS < 4,75 V ≥ 10 ms (Z-08 w najgorszym narożniku; nominalnie ok. 17 ms do VLOG = 7 … | | |
| P02-15 | jw. | ≥ 20 ms (szac. z 22,3 ms w najgorszym narożniku); nominalnie ok. 33 ms | | |
| P02-16 | VBAT (O-08): drugi kanał zasilacza albo ten sam przez … → J_BP.20 VBAT_SENSE (bez P05), J_SV2.3 | VBAT_SENSE = J15 z dokładnością ≤ 20 mV (szac.: upływ P6KE24CA µA na 10 kΩ); nie przekraczać 20 V | | |
| P02-17 | Odwrotna polaryzacja (O-01), opcjonalnie, przed łączeniem z … → prąd, temperatura Q9 | prąd ≤ 1 mA (szac.: upływy), nic się nie grzeje; potem powtórzyć P02-02…P02-04 | | |
| P02-18 | Pakiet bez P02: napięcie i polaryzacja na XT60, BMS, … → multimetr na XT60 | 13,0–16,8 V (≥ 3,25 V/ogniwo, inaczej P02 może nie wystartować — próg do 14,08 V), plus na przewodzie do J1.1 | | |
| P02-19 | PWR rozwarty, XT60 do P02 (F2/F3 włożone, F1 wyjęty, … → LED, J_BP.2 5V_SYS, J_BP.8 3V3_IO, PSU_OK | start, wartości jak P02-10/P02-11 | | |
| P02-20 | Podtrzymanie (O-05, wyjęcie pakietu): obciążenie 4,7 Ω, … → jak P02-14 | ≥ 10 ms jak P02-14 | | |

Pakiet 4S: ogniwa (typ / partia) ________ BMS ________ napięcia ogniw przed próbą: ____ / ____ / ____ / ____ V

Progi UVLO zmierzone: załączenie ______ V, wyłączenie ______ V, histereza ______ V


Uwagi / odstępstwa: ____________________________________________________________________________

Decyzja: odebrana / odebrana z uwagami / nieodebrana     Podpis: ______________________  Data: ____________


## P03 R6 — CORE (rozdz. 4)

Egzemplarz P03 R6: ________  Numer PCB / data produkcji: ________  Data odbioru: ________

Przyrządy (multimetr, zasilacz, DHO804, sondy): ______________________________________  Temperatura otoczenia: ______ °C

Firmware (wariant / wersja): ______________

| ID | Czynność | Oczekiwane | Zmierzono | OK / NIE |
|---|---|---|---|---|
| P03-01 | Moduł M1 wyjęty. 5,00 V z zasilacza na J_BP2.17/.19/.20, … → prąd | < 10 mA (szac.: LTC4412 i podciągnięcia) | | |
| P03-02 | J_SV2.2 5V_SYS, J_SV2.12 5V_M1, J_SV1.10 3V3_CORE | 5V_SYS = 5,00 V; 5V_M1 = 4,95–5,00 V (Q1 włączony przez LTC4412) (szac.); 3V3_CORE ≈ 0 V (LDO jest na module) | | |
| P03-03 | USB, J_BP niepodłączone → konsola | linie z tabeli 1.1 (`PSRAM=16777216`, `CORE: … SD mount complete`, `PFAIL_N (GPIO3) = 1, tryb stolowy = 0`); … | | |
| P03-04 | J_SV1.10 3V3_CORE; J_SV2.12 5V_M1; J_SV2.2 5V_SYS | 3V3_CORE 3,20–3,40 V; 5V_M1 = USB − D1 modułu (zapisać, ok. 4,6–4,9 V (szac.)); 5V_SYS < 0,1 V | | |
| P03-05 | prąd wsteczny USB → 5V_SYS | < 50 µA ustalonego prądu (impulsy zanotować osobno) | | |
| P03-06 | J_SV2.3 PFAIL_N | ≥ 3,0 V (R43 100 kΩ, J_BP2 otwarte) | | |
| P03-07 | Przycisk RESET modułu przytrzymany (i osobno: tryb … → J_SV2: 4 ADC_RESET, 5 MEAS_EN, 7 ADC_CONVST = 0; 8 ADC_CS, … | „0” ≤ 0,4 V, „1” ≥ 2,9 V | | |
| P03-08 | RESET przytrzymany (przycisk modułu = EN = SUP_N) → J_SV3.12 SUP_N, J_SV2.11 SUP_RAW_N | SUP_N = L (≤ 0,6 V), SUP_RAW_N zostaje H (TPS3808 widzi poprawne 3V3_CORE); po puszczeniu SUP_N = H i ponowny … | | |
| P03-09 | PWR zwarty, USB odłączony → P03 J_SV2.2 5V_SYS, J_SV2.12 5V_M1, J_SV1.10 3V3_CORE, … | 5V_SYS ≥ 4,85 V; 3V3_CORE 3,20–3,40 V; 3V3_IO 3,23–3,37 V | | |
| P03-10 | Obciążenie ok. 0,5 A: 10 Ω / 5 W na złączce 5V_SYS przy P03 … → P03 J_SV2.2 5V_SYS względem P03 GND; ten sam pomiar na P02 … | na P03 ≥ 4,85 V; zapisać spadek P02 → P03 (z P12 będzie mniejszy) | | |
| P03-11 | Tryb stołowy (F-02): PWR rozwarty (P02 bez zasilania), USB … → konsola; J_SV2.3 PFAIL_N | komunikat `TRYB STOLOWY…`; PFAIL_N < 0,825 V (szac. 0,33 V); na karcie brak nowego katalogu sesji | | |
| P03-12 | PWR: włącz i wyłącz kilka razy (USB podłączony, żeby CORE … → DHO804: CH1 P02 J_SV1.2 ENABLE, CH2 P03 J_SV2.3 PFAIL_N … | opadanie PFAIL_N na P03 ≤ 100 µs od ENABLE; L < 0,825 V (szac. 0,43 V przy VOL 0,4 V); po włączeniu H ≥ 2,5 … | | |

Uwagi / odstępstwa: ____________________________________________________________________________

Decyzja: odebrana / odebrana z uwagami / nieodebrana     Podpis: ______________________  Data: ____________


## P05 R3 — DAQ (rozdz. 5)

Egzemplarz P05 R3: ________  Numer PCB / data produkcji: ________  Data odbioru: ________

Przyrządy (multimetr, zasilacz, DHO804, sondy): ______________________________________  Temperatura otoczenia: ______ °C

Firmware (wariant / wersja): ______________

| ID | Czynność | Oczekiwane | Zmierzono | OK / NIE |
|---|---|---|---|---|
| P05-01 | 5,00 V, limit 100 mA, potem 250 mA; MEAS_EN = 0 → prąd; J_SV1.4 5V_SYS, J_SV1.5 5VA_P05, J_SV1.6 3V3_DAQ | 5VA = 5V_SYS − 12…20 mV (różnicowo J_SV1.4–.5); 3V3_DAQ 3,20–3,40 V | | |
| P05-02 | Przed skręceniem stosu → REF_2V5 na C24 (multimetr) albo J_SV1.8 miernikiem ≥ 1 GΩ | 2,4988–2,5013 V | | |
| P05-03 | Okno DAQ_OK: zasilacz powoli 4,60 → 5,30 → 4,60 V (nie … → J_SV2.10 DAQ_RAIL_N, J_SV2.9 DAQ_OK; zasilacz na J_SV1.4 | dolny próg 4,756–4,845 V (nom. 4,800), górny 5,141–5,230 V (nom. 5,186); DAQ_OK = 1 tylko w oknie | | |
| P05-04 | 5,00 V; nadzorcy → J_SV2.11 P05_SUP3_N, J_SV2.12 P05_SUP5_N, J_SV2.9 DAQ_OK | wszystkie H przy 5,00 V; DAQ_OK = 0 przy braku któregokolwiek warunku (krok 6) | | |
| P05-05 | Przekaźniki przed wlutowaniem (10a) → cewka z zasilacza, ok. 23 °C | zadziałanie ≤ 3,9 V każdej sztuki | | |
| P05-06 | Pomiar 5V_SYS przy ok. 23 °C (krok 3) → J_SV1.4 | 4,93–5,07 V — to kryterium dla szyny z P02 w 9.2 | | |
| P05-07 | Kondensatory U1 przed skręceniem (krok 11) → TP2–TP5 (TP1 = GND) | Ceff C12/C13 ≥ 10 µF przy 2,5/4,4 V (karta DC-bias lub pomiar) | | |
| P05-08 | Start (PWR), konsola przez USB → konsola, `status` | start bez restartów; po `logger` stan LOGGER, `adc=1`, licznik `lost` = 0 | | |
| P05-09 | Rozruch AD7606B (F-04): wyłącz/włącz PWR → DHO804: CH1 P05 J_SV2.6 ADC_RESET, CH2 J_SV2.7 MEAS_EN, CH3 … | RESET jeden impuls ok. 20 µs, nie wcześniej niż 10 ms po zasileniu; aktywność CS (konfiguracja) ≥ 2,1 s po … | | |
| P05-10 | Takt próbkowania → CH4 ADC_CONVST, CH3 J_SV2.4 ADC_BUSY, 200 µs/dz | CONVST co 500 µs (2 kS/s); po każdym CONVST jeden impuls BUSY; zapisać szerokość BUSY | | |
| P05-11 | Wejście testowe CH7: 12,00 V z zasilacza na P02 J15 … → zapis 30 s (`logger`, potem `stop`), `egrlog.py export` → … | przed kalibracją kod ok. 6351 (±1 %) przy zakresie ±10 V (12,00 V / 6,1918 / 10 V × 32768; przez R38 10 kΩ na … | | |
| P05-12 | jw. | kod ok. 7938 (±1 %); stosunek kodów 15/12 z dokładnością 0,2 % (szac.) | | |
| P05-13 | Kanały CH1–CH5 przez docelowe adaptery (krok 12 ODBIOR) | znaki i kanały zgodne; kalibracja dwupunktowa `cal 0 kanał gain offset`, sprawdzenie w trzecim punkcie | | |
| P05-14 | Drgania DAQ_OK (MINOR-4 recenzji): `logger` przy 2 kS/s, … → DHO804: CH1 P05 J_SV2.9 DAQ_OK — wyzwalanie opadające 1,6 … | zero wyzwoleń w 30 min, przekaźniki nie klikają; tętnienia i szpilki 5VA (p-p, zapisać) mniejsze niż połowa … | | |
| P05-15 | jw. | jak P05-14 | | |
| P05-16 | `daq_stats` w `events_NNN.ndjson` po 30 min → `convst`, `samples`, `adc_errors`, `lost_ticks` | `convst` = `samples`, `adc_errors` = 0, `lost_ticks` = 0 (F-05) | | |
| P05-17 | Zanik P05 w sesji: rozłącz żyły 5V_SYS P05 (bez ponownego … → konsola, log | FAULT / błąd ADC, MEAS_EN = 0; bez starych próbek jako nowych. Ponowny start całości → pełny RESET + 2,1 s | | |

Progi okna DAQ_OK zmierzone: dolny ______ V, górny ______ V; REF_2V5 ______ V; przekaźniki K1 ____ K2 ____ K3 ____ V

Kalibracja CH1–CH8 (`cal 0 …`): wpisać do profilu i tutaj: ____________________________________________


Uwagi / odstępstwa: ____________________________________________________________________________

Decyzja: odebrana / odebrana z uwagami / nieodebrana     Podpis: ______________________  Data: ____________


## P06 R2 — I-LOGGER (rozdz. 6)

Egzemplarz P06 R2: ________  Numer PCB / data produkcji: ________  Data odbioru: ________

Przyrządy (multimetr, zasilacz, DHO804, sondy): ______________________________________  Temperatura otoczenia: ______ °C

Firmware (wariant / wersja): ______________

| ID | Czynność | Oczekiwane | Zmierzono | OK / NIE |
|---|---|---|---|---|
| P06-01 | E01–E03 bez zasilania → J3/J4, RSH1, SW1 | tor przez bocznik zawsze zamknięty; BYPASS zwiera równolegle; brak połączenia z GND | | |
| P06-02 | E04: 5,00 V, limit 30 mA, BYPASS → J_SV2.2 5V_SYS, .3 5VA_P06, .4 3V3_P06, J_SV1.5 REF_BUF; … | VREF 2,475–2,525 V | | |
| P06-03 | E05: MEASURE, limit 250 mA, 4,75 / 5,00 / 5,25 V → prąd; temperatura R21, R6 | < 180 mA; R21 ciepły (0,64–0,71 W) | | |
| P06-04 | E06–E07 → J_SV2.10 LOGGER_CURRENT_OK, J_SV2.9 SHUNT_ENABLED, … | MEASURE: READY = H; BYPASS: SHUNT_ENABLED = L i READY = L; wymuszone SUP3_N / SUP5_RAW → READY = L | | |
| P06-05 | E09: start 5 V → CH1 J_SV2.2, CH2 J_SV2.3 (Math CH1 − CH2 = prąd R6 1 Ω), … | przy wpięciu do żywego 5 V prąd przez R6 ≤ ok. 5 A, τ ≈ 0,22 ms; przy narastaniu zasilacza znacznie mniej | | |
| P06-06 | E10: prąd 0, MEASURE, `logger` → DHO804: J_SV2.11 CS_LOCAL_N, J_SV2.12 CLK_LOCAL; log … | 16 taktów na CS, kod ok. 2048, stały; wspólna linia ADC_DOUTA bez konfliktu z P05 (brak zniekształconych … | | |
| P06-07 | E11: zero po 1 s → J_SV1.2 I_L_OUT, J_SV1.5 REF_BUF, J_SV1.3 ADC_AIN … | I_L_OUT ≈ REF_BUF (ok. 2,5 V), ADC_AIN ≈ 1,25 V; szum kodu zapisać (cel po kalibracji: offset < 20 mA, RMS < … | | |
| P06-08 | Kalibracja ADC lokalnego: w SAFE `bank 0`; dwa punkty prądu … → — | `adc_gain = (V2 − V1)/(raw2 − raw1)` ≈ 0,00122 V/kod; `adc_offset = V1 − raw1·adc_gain` ≈ 0 | | |
| P06-09 | Skala V/A: ±0,5 / 1 / 3 A (potem ±6 A), odwracanie … → I_L_OUT względem REF_BUF; wzorzec prądu | ok. 0,25 V/A (5 mΩ × 50) w obu kierunkach | | |
| P06-10 | Wpisy: `iscal 0 adc_gain adc_offset V/A`, `currentcal 0 … → `profile` | wartości jak wpisane | | |
| P06-11 | E13: kontrola w punktach ±0,5 / 1 / 3 / 6 A przy 5V_SYS z … → prąd z logu vs wzorzec | reszta ≤ max(30 mA, 1 % wskazania) | | |
| P06-12 | E14: BYPASS przy ustalonym prądzie 1 A → J_SV2.9, J_SV2.10; log | SHUNT_ENABLED = L, READY = L; w logu brak ważnych amperów (kolumna A pusta) | | |
| P06-13 | E15: bierny tor 10 A, 30 s, potem 10 min (35 µm miedzi!) → temperatura pól J3/J4/RSH1 (termopara P09 albo termowizja); … | przyrost < 30 °C, stały spadek, brak odbarwień | | |

Kalibracja: adc_gain ________ adc_offset ________ V/A ________ zero ________ V; VREF ______ V; τ filtra (E16) ______ µs


Uwagi / odstępstwa: ____________________________________________________________________________

Decyzja: odebrana / odebrana z uwagami / nieodebrana     Podpis: ______________________  Data: ____________


## P09 R2 — TEMP (rozdz. 7)

Egzemplarz P09 R2: ________  Numer PCB / data produkcji: ________  Data odbioru: ________

Przyrządy (multimetr, zasilacz, DHO804, sondy): ______________________________________  Temperatura otoczenia: ______ °C

Firmware (wariant / wersja): ______________

| ID | Czynność | Oczekiwane | Zmierzono | OK / NIE |
|---|---|---|---|---|
| P09-01 | Nośnik bez modułów → J2.2 3V3_IO, J2.3 5V_SYS, J2.8/.9 CS1_BUF/CS2_BUF, … | szyny bez zwarć, pobór kilka mA (szac.); oba CS = H (≥ 2,9 V); OE1_N, OE2_N = H | | |
| P09-02 | Kwalifikacja modułów 1–4, wybór VIN (JP1/JP2, jedna zwora … → J2.4/.5 TC1/TC2_VIN, J2.6/.7 TC1/TC2_3VO | 3Vo 3,0–3,6 V przy wybranym VIN | | |
| P09-03 | Po przylutowaniu modułów (pin 1 = VIN, nadruk „1”) | jak P09-02, brak zwarć kołków 4–7 do GND | | |
| P09-04 | Start (F-07) → log / konsola | konfiguracja CR0 = 91h, CR1 = 03h potwierdzona odczytem; pierwsza ważna próbka po 300 ms; brak błędu … | | |
| P09-05 | MISO i CS → DHO804: J2.12 SPI3_MISO, J2.8/.9 CS1/CS2_BUF, J2.10/.11 … | przy nieaktywnych CS MISO w stanie Z; CS setup/hold 2 takty przy 1 MHz; przerwa obu CS = H ≥ 1 µs; podczas … | | |
| P09-06 | Temperatura otoczenia: obie termopary obok termometru … → T1/T2 w logu (`status` pokazuje T1) | \ | | |
| P09-07 | Woda z lodem: kruszony lód + woda, mieszać, końcówka w … → T1, T2 | 0,0 ± 2,5 °C (szac.: termopara klasy 2 ±2,5 °C); zapisać przesunięcie każdego kanału — to korekta do profilu | | |
| P09-08 | Ogrzanie końcówki (dłoń / ciepła woda) i powrót → T1/T2 | wzrost i powrót bez skoków | | |
| P09-09 | Termopara odłączona od terminala → log | fault, wartość NAN, poprawny status — nigdy 0 °C | | |
| P09-10 | Odłączona P09 (wyłącz, zdejmij W4, włącz) → log | błąd komunikacji, brak fikcyjnego 0 °C (moduł jest przylutowany, więc to zastępuje „moduł odłączony”) | | |

VIN: TC1 ____ V (JP1 ____), TC2 ____ V (JP2 ____). Przesunięcie w 0 °C: TC1 ______ °C, TC2 ______ °C; termometr odniesienia: ________


Uwagi / odstępstwa: ____________________________________________________________________________

Decyzja: odebrana / odebrana z uwagami / nieodebrana     Podpis: ______________________  Data: ____________


## P10 R2 — CAN (rozdz. 8)

Egzemplarz P10 R2: ________  Numer PCB / data produkcji: ________  Data odbioru: ________

Przyrządy (multimetr, zasilacz, DHO804, sondy): ______________________________________  Temperatura otoczenia: ______ °C

Firmware (wariant / wersja): ______________

| ID | Czynność | Oczekiwane | Zmierzono | OK / NIE |
|---|---|---|---|---|

Magistrala stołowa (węzły, bitrate, obciążenie %): ______________________  Długość W3: ______ mm


Uwagi / odstępstwa: ____________________________________________________________________________

Decyzja: odebrana / odebrana z uwagami / nieodebrana     Podpis: ______________________  Data: ____________


## Komplet LOGGER (rozdz. 9)

Egzemplarz komplet: ________  Numer PCB / data produkcji: ________  Data odbioru: ________

Przyrządy (multimetr, zasilacz, DHO804, sondy): ______________________________________  Temperatura otoczenia: ______ °C

Firmware (wariant / wersja): ______________

| ID | Czynność | Oczekiwane | Zmierzono | OK / NIE |
|---|---|---|---|---|
| LOG-01 | DHO804: CH1 P02 J_SV2.11 5V_SYS (1 V/dz), CH2 P02 J_SV1.4 … → przebiegi | 5V_SYS rośnie monotonicznie do ≥ 4,75 V, czas 10–90 % zapisać (oczekiwane rzędu 5 ms z karty TSR; kryterium … | | |
| LOG-02 | Math CH3 − CH4 | szczyt prądu ładowania C1 ≤ 0,5 A (szac.: 220 µF × 5 V / 5 ms ≈ 0,22 A) | | |
| LOG-03 | Math | szczyt ≤ 0,5 A (szac.) | | |
| LOG-04 | Powtórz LOG-01 pięć razy; potem przy 13,6 V (blisko progu … | każdy start jak LOG-01; przy 13,6 V brak cyklicznego załączania (UVLO + prąd startu) | | |
| LOG-05 | P03 po starcie → konsola | jeden start, bez resetów brownout | | |
| LOG-06 | `logger`, sesja 30 min, zapis SD, ruch CAN z magistrali … → prąd zasilacza przy 14,5 V | < 0,43 A (6 W z VLOG, Z-05) | | |
| LOG-07 | 5V_SYS: P02 J_SV2.11, P03 J_SV2.2, P05 J_SV1.4, P06 … | P03 ≥ 4,85 V; P05 4,93–5,07 V przy ok. 23 °C (warunek okna DAQ_OK); pozostałe ≥ 4,85 V | | |
| LOG-08 | 3V3_CORE P03 J_SV1.10, 5V_M1 J_SV2.12 | 5V_M1 ≥ 4,60 V, 3V3_CORE stabilne (oscylogram podczas zapisu SD) | | |
| LOG-09 | log po 30 min | `daq_stats`: `convst` = `samples`, `adc_errors` = 0, `lost_ticks` = 0; `can_stats` bez strat w … | | |
| LOG-10 | temperatura: P02 Q1/Q9, U5/U6 (TSR), D1; P03 M1 (LDO), Q1; … | nic nie parzy po 30 min (szac.); zapisać najcieplejszy element | | |
| LOG-11 | PFAIL z zapisem (F-01): w trakcie sesji rozewrzyj PWR (USB … → DHO804: CH1 P03 J_SV2.3 PFAIL_N (wyzwalanie opadające), CH2 … | GPIO41 = H od zbocza PFAIL_N do zamknięcia plików, ≤ 10 ms, i przed spadkiem 5V_SYS < 4,75 V; ostatnia linia … | | |
| LOG-12 | jw. | jw. | | |
| LOG-13 | Zakłócenie krótkie: impuls L < 30 µs na PFAIL_N … → log | `pfail_glitch`, sesja trwa | | |

Czas narastania 5V_SYS (10–90 %): ______ ms; szczyt prądu C1 ______ A, C3 ______ A; pobór przy 14,5 V ______ A; PFAIL → zamknięcie plików ______ ms


Uwagi / odstępstwa: ____________________________________________________________________________

Decyzja: odebrana / odebrana z uwagami / nieodebrana     Podpis: ______________________  Data: ____________


## Firmware 6.2-s1 na sprzęcie (rozdz. 10)

Firmware (wariant, SHA-256 obrazu z `verification/builds.json`): ______________________  Karta SD: ______________

| ID | Wymaganie | Gdzie | Kryterium | Wynik / plik | OK / NIE |
|---|---|---|---|---|---|
| F-01 | PFAIL_N na GPIO3: napęd w dół, zamknięcie plików | LOG-11, LOG-12, LOG-13 | ≤ 10 ms od zbocza do zamknięcia (GPIO41), `power_fail` jako ostatnia linia; impuls < 30 µs = `pfail_glitch` | | |
| F-02 | Tryb stołowy | P03-11 | `TRYB STOLOWY`, brak katalogu sesji, licznik sesji w NVS nie rośnie (numer kolejnej sesji normalnej = … | | |
| F-03 | CH7 = VBAT_SENSE, mnożnik 6,0898 (6,1918 przez R38 na P02) | P05-11, P05-12 | kod 6351 / 7938 ± 1 % przed kalibracją; w `meta.json` CH7 opisany jako akumulator auta | | |
| F-04 | Rozruch AD7606B: RESET 20 µs, 2100 ms, konfiguracja przed MEAS_EN, 25 … | P05-09, P05-17 | jak P05-09; po zaniku P05 pełny RESET + 2,1 s, bez samoczynnego TEST | | |
| F-05 | Próbkowanie i `daq_stats` | P05-10, P05-16, LOG-09 | 2 kS/s przy SPI 1 MHz: `convst` = `samples`, `lost_ticks` = 0. 10 kS/s / 4 MHz — poza tym odbiorem: wymaga … | | |
| F-06 | Łańcuch prądu P06 R2, `current_chain` w `config` | P06-06…P06-12 | `config` zawiera `current_chain`; przy READY = 0 i w BYPASS prąd nieważny | | |
| F-07 | MAX31856: CS 2/2, 300 ms, odczyt CR0/CR1, błąd = NAN, fault 255 | P09-04, P09-09, P09-10 | jak w krokach | | |
| F-08 | CAN w osobnym zadaniu, `can_config`, `can_stats`, dekoder RPM | P10-04…P10-10 | jak w krokach; `can_config`: 500000, listen_only | | |
| F-09 | `profiles/hardware.json` = zmontowane rewizje | po montażu | P02 R4, P03 R6, P05 R3, P06 R2, P09 R2, P10 R2 zgodne z nadrukiem płytek; uzupełnić numery egzemplarzy w … | | |

Uwagi / odstępstwa: ____________________________________________________________________________

Decyzja: odebrana / odebrana z uwagami / nieodebrana     Podpis: ______________________  Data: ____________

