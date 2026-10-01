# Firmware pod format S1 — wymagania ze zmian sprzętu (zadanie, 1.10.2026)

**Stan:** wymagania zebrane z pakietów płytek. Kodu nie zmieniano.
**Baza:** `Rewizje/EGRLab-v6.1-rc1/firmware` (zamknięta; nowa wersja powstaje jako kopia).
**Wykonawca i miejsce kompilacji:** do decyzji. ESP-IDF jest u Codexa na laptopie (`docs/pamiec-claude/egrlab-codex-toolchains.md`); na komputerze 24/7 go nie ma.

## 1. Zgodność pinów — sprawdzone 1.10.2026

Numery GPIO w `firmware/main/board.c` (v6.1) porównane z netlistą P03 R6 (`docs/netlist-pinowa.csv`, gałąź `p03-r6-pcb`, moduł M1, mapa J1/J3 → GPIO z `src/parts.py`). **Wszystkie się zgadzają:**

| Funkcja | GPIO (v6.1) | M1 (P03 R6) |
|---|---|---|
| PWM, ADC_SDI | 1, 2 | J3-4, J3-5 |
| INTERLOCK, SCOPE, HW_ARM, ARM, CURRENT_CS | 42, 41, 40, 39, 38 | J3-6 … J3-10 |
| HEART | 21 | J3-18 |
| ADC: SCLK, DOUTA, CS, CONVST, BUSY | 9, 11, 12, 13, 14 | J1-15, J1-17 … J1-20 |
| SPI3: SCLK, MOSI, MISO, SD_CS, TC1_CS, TC2_CS | 4, 5, 6, 7, 8, 16 | J1-4 … J1-7, J1-12, J1-9 |
| I2C: SDA, SCL | 10, 15 | J1-16, J1-8 |
| TWAI: TX, RX (LISTEN_ONLY) | 17, 18 | J1-10, J1-11 |
| MCP23017 GPA4 = LOGGER_CURRENT_OK (wejście, IODIRA 0x10) | — | U1 pin 25 |

**Nowe w S1:** tylko GPIO3 (J1-13) = PFAIL_N_CORE (P03 R6, wejście z P02 R4).

## 2. Wymagania

| ID | Źródło | Wymaganie | Odbiór |
|---|---|---|---|
| F-01 | P03 R6 README „PFAIL_N”; P02 R4 SPEC Z-08, Z-09, §9 | GPIO3 jako wejście **bez wewnętrznego pull-down** (ok. 45 kΩ wobec R43 100 kΩ dałoby L). Aktywny niski; przerwanie na zbocze opadające (P02: opada ≤ 100 µs po utracie ENABLE). Po PFAIL_N zatrzymać zapis i domknąć plik w **≤ 10 ms**: podtrzymanie ≥ 10 ms przy 6 W, w najgorszym narożniku 11,1 ms. W logu zapisać zdarzenie „wyłączenie przez UVLO”. | Czas od zbocza PFAIL_N do zamkniętego pliku na oscyloskopie (GPIO znacznikowe), plik czytelny po wyjęciu pakietu. ODBIOR P02 R4 O-05. |
| F-02 | P03 R6 README „Stany” | Tryb tylko-USB (P02 bez zasilania): PFAIL_N = L na stałe (ok. 0,33 V). Firmware go wtedy ignoruje — patrz D-2. | Start z USB bez P02: brak zdarzeń PFAIL, sesja działa. |
| F-03 | P05 R2 README (CH7), P02 R4 Z-12 | CH7 (indeks 6, `CH_VBAT` w `control.h`) = akumulator auta przez P02 R4 (VBAT_SENSE), dzielnik 499k/100k na P05 jak w R2. Sprawdzić skalę w profilu i opis w metadanych (dawniej VPROT_SENSE). Warunek 9–16,5 V w `control.c` dotyczy akumulatora, nie pakietu 4S. | Odczyt CH7 wobec multimetru przy 12 i 14 V. |
| F-04 | P05 R2 `docs/INTEGRACJA.md` „Rozruch” | AD7606B: ≥ 10 ms od stabilnego AVCC/VDRIVE do RESET; RESET ≥ 3 µs; po pierwszym RESET **2100 ms** (dziś w kodzie 10 ms). Konfiguracja zapis + odczyt kontrolny; błąd → `adc_config_ok = false`, brak TEST. MEAS_EN dopiero po poprawnej konfiguracji, potem ≥ 20 ms na przekaźniki. Po zaniku DAQ_OK: stop akwizycji, unieważnienie konfiguracji, bez samoczynnego powrotu do TEST. | ODBIOR P05 kroki 8–10; próba zaniku 5V_SYS przy sesji. |
| F-05 | P05 R2 INTEGRACJA „Tempo i dane”, „Kalibracja” | Start: SPI 1 MHz i do 2 kSPS; kwalifikacja 4 MHz i 10 kSPS. Zliczanie CONVST i próbek, surowe kody, `config_id`, bank. Kalibracja offsetu i wzmocnienia w firmware, nie w rejestrach AD7606B. Profil AUX HI/LO i kalibracja w metadanych; położenia SW1 P05 nie odczytuje. | ODBIOR P05 kroki 12–17. |
| F-06 | P06 R1 `docs/FIRMWARE.md` | MCP3201: SPI mode 0, 500 kHz, `raw = (word >> 1) & 0x0FFF`, 2 kS/s. Pola sesji (płytka, bocznik, INA240A2 G50, dzielnik 1:2, τ 1198,5 µs, ZERO/gain) albo plik boczny `P06-calibration.json`. Odrzucanie danych przy READY = 0 i w BYPASS. Test wspólnej magistrali z P05: powrót do trybu SPI AD7606B. **Do potwierdzenia po rewizji S1 płytki P06** (bocznik 2512). | Test wspólnej magistrali na stole. |
| F-07 | P09 R1 `firmware/P09-temperature.diff`, P09 R2 `docs/MODUL-KWALIFIKACJA.md` krok 4, `docs/J_BP.csv` | Wgrać łatę MAX31856: `cs_ena_pretrans/posttrans`, 300 ms po konfiguracji, przy błędzie `NAN` i `fault = 255`. CR0 = 0x91, CR1 = 0x03, odczyt 0x0C–0x0F. Brak modułu daje błąd komunikacji, nigdy 0 °C. Między kanałami oba CS w stanie wysokim ≥ 1 µs. | MODUL-KWALIFIKACJA krok 4; odłączony moduł → błąd w logu. |
| F-08 | P10 R2 `docs/INTEGRACJA.md` | TWAI listen-only także przy sprzętowym S = H; brak TX. Odbiór w osobnym zadaniu opróżniającym kolejkę. Liczniki przepełnień RX i kolejki zdarzeń oraz błędów CAN w logu z czasem. Metadane: bitrate, listen-only, źródło czasu, profil CAN. Dekoder RPM (Mode01 PID0C, ID 0x7E8–0x7EF): kontrola DLC/ISO-TP, wybór jednego ECU, brak danych ≠ 0 rpm. | ODBIOR P10 „Ruch ciągły”: 10 min, liczba ramek w loggerze = we wzorcu. |
| F-09 | `profiles/hardware.json` (schema 6) | Rewizje płytek S1 i interfejs zamiast „M2”: P02 R4, P03 R6, P05 R3, P09 R2, P10 R2 (P06, P11 po rewizjach). | Profil v6 bez zmian w znaczeniu kalibracji (README v6.1: nie wgrywać V5 jako V6). |

## 3. Decyzje użytkownika (1.10.2026)

- **D-1 — przyjęte:** kompilacja ESP-IDF w Dockerze na komputerze 24/7 (ten sam wzorzec co `scripts/egrlab-docker`: najniższa waga CPU i limit rdzeni, bo Frigate ma pierwszeństwo; obraz ok. 3–5 GB). Wersja firmware: 6.2-s1.
- **D-2 — przyjęte:** tryb tylko-USB (F-02) rozpoznawany po PFAIL_N = L od startu przez ≥ 100 ms → tryb stołowy bez zapisu sesji i bez TEST. Zbocze opadające po starcie z H to zawsze prawdziwy PFAIL.
- **D-3 — przyjęte:** przy PFAIL_N najpierw `board_emergency_stop()`, potem domknięcie pliku. P04 i tak rozbraja sprzętowo przez SAFE_N, ale firmware nie zostawia PWM aktywnego na czas podtrzymania.

## 4. Kolejność

1. Bez nowego sprzętu: F-07 (łata gotowa), F-08, F-09 i sprawdzenie F-03.
2. F-01 i F-02 (decyzje D-2 i D-3 przyjęte 1.10).
3. Przy uruchamianiu P05: F-04 i F-05.
4. Po rewizji S1 płytki P06: F-06.

Testy hosta z v6.1 (`tests/run_host.py`, `test_v61.py`) mają przechodzić bez zmian w znaczeniu; nowe zachowania (PFAIL, licznik CAN) dopisać jako testy hosta tam, gdzie da się je odseparować od sprzętu.
