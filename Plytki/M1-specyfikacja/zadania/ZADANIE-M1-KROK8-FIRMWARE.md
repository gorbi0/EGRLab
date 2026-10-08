# Zadanie M1, krok 8 — firmware dla płytki M1 (sesja w chmurze)

*8.10.2026. Gałąź zadania: `m1-firmware` (od `m1`), PR do `m1`.*

## Cel

`Rewizje/EGRLab-v6.3-m1/`: kopia części programowej `Rewizje/EGRLab-v6.2-s1` (firmware, profile, narzędzia, testy) zmieniona pod sprzęt M1. Wydanie 6.2-s1 zostaje bez zmian (wzorzec regresji, jak 6.1-rc1 dla 6.2-s1). Struktura, styl i sposób dokumentowania jak w README 6.2-s1 (tabela zmian z ID, kontrole, status).

## Źródła prawdy o sprzęcie M1 (czytaj tylko te)

- `Plytki/M1-specyfikacja/SPECYFIKACJA.md`: kanały AD7606B (sekcja 2), piny ESP32 (sekcja 3), listwa X1, tryby LOGGER / TESTER.
- `Plytki/M1-specyfikacja/AUDYT.md`: decyzje D-M1-1…13, zwłaszcza D-M1-4, -5, -6, -7.
- `Plytki/M1-R1-review/docs/GPIO.csv`: mapa GPIO z netlisty (obowiązuje, gdy różni się od tekstu).
- `Plytki/M1-R1-review/docs/parts.json` (wartości części) i `output/pdf/M1-R1-schemat.pdf`.

## Różnice sprzętu względem 6.2-s1 (do wprowadzenia)

| ID | M1 | Skutek dla firmware |
|---|---|---|
| M-01 | Brak MCP23017, I²C, dekodera CS, P04 SAFE, P05 TAPS / MEAS_EN / READY, MCP3201 | usunąć sterowniki i logikę zależną (blokady, przekaźniki, gotowość); GPIO wg `GPIO.csv` |
| M-02 | AD7606B jak w P05 R3: tryb szeregowy programowy, OS = 111, wewnętrzne odniesienie, ±10 V; SCLK 9, DOUTA 11, SDI 2, CS 12, CONVST 13, BUSY 14, **RESET GPIO10 wprost** (było przez ekspander; 10 k do GND) | rozruch F-04 bez zmian czasów; RESET bezpośrednio z GPIO |
| M-03 | Kanały: CH1 P1_EGR i CH2 P3 dzielnik 300 k / 100 k; CH3–CH5 P4–P6 i CH8 SENS_5V 100 k szeregowo; CH7 VBAT_CAR 499 k / 100 k. Każdy z 220 pF. Wejście AD7606B 5 MΩ (jak F-03) | współczynniki skali z tych wartości; opis w `meta.json` |
| M-04 | **Prąd silnika na CH6:** bocznik 5 mΩ, INA240A2 (×50), REF1 = 5 V, REF2 = GND → U = VS/2 + 0,25 V/A (VS = 5 V z TSR 2-2450), filtr 1 k / 1 n; liniowo ok. ±9 A. **Ten sam tor w LOGGER i TESTER** (D-M1-7) | prąd z CH6 próbkowany razem z napięciami (koniec MCP3201 i jego opóźnienia). Zero (VS/2) zapisywane przy wyłączonym mostku i bez prądu ECU, nie stała 2,5 V |
| M-05 | IBT-2 przez 74AHCT125: **RPWM GPIO1, LPWM GPIO21** (LEDC), **DRIVE_EN GPIO39** → R_EN + L_EN; 100 k do GND na wszystkich trzech | kierunek = który PWM; enable osobno; ≤ 25 kHz (BTS7960); po starcie i przy błędzie wszystko w stanie niskim |
| M-06 | Brak sprzętowego okna OC i zatrzasku (D-M1-4): mostek wyłącza tylko firmware + watchdog ESP32 | watchdog zadań i RTC; przy panic / resecie DRIVE_EN niski (pull-down). **Do potwierdzenia w PR:** programowe ograniczenie prądu z CH6 (domyślnie 8 A, Kconfig, z możliwością wyłączenia) — zaproponuj, zaimplementuj jako opcję |
| M-07 | Zasilanie czujnika: TPS2553 **EN GPIO40** (aktywny H, 100 k do GND), **FAULT_N GPIO42** (10 k do 3V3), kontrola napięcia na CH8 | SENS_5V tylko w TESTER; w LOGGER zawsze wyłączone (D-M1-5) |
| M-08 | MAX31856 ×2 (moduły) na SPI3: SCK 4, MOSI 5, MISO 6, **CS GPIO8 / GPIO16 wprost**; SDO przez bufor z OE = CS (przezroczysty dla firmware); karta SD na SPI3, CS GPIO7 | łata F-07 bez zmian; CS bez dekodera |
| M-09 | CAN: TCAN1051V z TXD i S na stałe w 3V3 (cichy); **RX GPIO18**, GPIO17 niepodłączony | TWAI listen-only jak F-08 |
| M-10 | Brak PFAIL_N (GPIO3 to pole testowe, brak detekcji zaniku zasilania) | F-01 i tryb stołowy F-02 usunąć albo przerobić; opisać zachowanie przy zaniku zasilania (pliki mogą zostać niedomknięte) |
| M-11 | USB tylko do programowania (D-M1-6): przy samym USB peryferia 3,3 V (SD, AD7606B VDRIVE, MAX31856) są bez zasilania | brak SD / AD7606B nie może zawieszać firmware; czytelny stan w konsoli |
| M-12 | Przycisk START / STOP **GPIO15** (aktywny L, 10 k do 3V3 + 100 nF); LED stanu = dioda RGB modułu **GPIO38**; wyzwalacz oscyloskopu GPIO41 | sterownik RGB (RMT / led_strip) zamiast HEART na GPIO21 |
| M-13 | `profiles/hardware.json`: nowa konfiguracja „M1-R1” | schemat profilu z wersją; tożsamości jak w 6.2-s1 |

## Kontrole (wymagane)

- Kompilacja ESP-IDF 5.4.3 w Dockerze (`scripts/egrlab-idf`, obraz `espressif/idf:v5.4.3`) dla wariantów, które mają sens na M1. Brak wariantu z P07 lub P04 opisz w README.
- Jeśli obraz ESP-IDF jest w chmurze niedostępny, nie obchodź tego. Zapisz to w PR i zrób testy hosta.
- Testy hosta jak w 6.2-s1 (`tests/run_host.py`, `python3 -m unittest`), zaktualizowane do M1. Nowe testy dla M-02…M-07 (mapa GPIO z `GPIO.csv`, skale kanałów z `parts.json`, stany bezpieczne mostka, SENS_EN w LOGGER).
- Próby mutacyjne nowych kontroli z próbą zerową (jak `probe_v62_mutations.py`).
- README 6.3-m1: tabela zmian M-01…M-13, wyniki, status **odbiór sprzętu: NIE ZBADANO**, `EGR_HARDWARE_ACCEPTED=0`.

## Zasady (docs/CHMURA.md)

- Bez procesów dłuższych niż ok. 15 min; długie wyjścia do pliku, pokazuj koniec. Dwie nieudane próby czegoś = zapisz stan i opisz w PR (zasada 9).
- Po każdym etapie commit i push na `m1-firmware`.
- Nie zmieniaj: `Rewizje/EGRLab-v6.2-s1/`, `Rewizje/EGRLab-v6.1-rc1/`, `Plytki/`, `EGRLab-AKTYWNE.md`, `docs/` (poza nową sekcją „6.3-m1” w `docs/04-firmware-logi.md`, jeśli zmieniasz zdarzenia logu), `scripts/`, `.gitignore`.
- Zakończ PR-em do `m1` po polsku. Pytania (np. M-06) wpisz do opisu PR. Nie włączaj śledzenia PR.
