# Odpowiedź na recenzje M1-R1 (Astra: M1-01…07 i Ultra: M1-08…12)

*8.10.2026. Recenzje: `Plytki/M1-R1-recenzja-Astra/RECENZJA-M1-R1.md`, `Plytki/M1-R1-recenzja-Ultra/RECENZJA-M1-R1-ULTRA.md` (oba katalogi bez zmian). Wszystkie 12 zgłoszeń przyjęte; żadnego nie podważam.*

**Najważniejsze:** płytka (PCB, Gerbery, ZIP dla producenta `824058fb…`) **bez zmian** — M1-01 rozwiązuje decyzja użytkownika (wylutowanie D1 na module ESP32), M1-02 zworka na listwie. Poprawki dotyczą firmware (6.3.1-m1), eksportera, generatora schematu i instrukcji.

## Zgłoszenia

| ID | Waga | Rozwiązanie | Dowód zamknięcia |
|---|---|---|---|
| M1-01 | ważne | **Decyzja użytkownika 8.10: wylutować D1 na module Waveshare** (USB VBUS → pin 5V). Samo USB niczego nie zasila; programowanie i konsola tylko przy włączonym pakiecie; kolejność pakiet → USB, USB → pakiet. Przed wylutowaniem potwierdzić oznaczenie i rewizję diody na posiadanym egzemplarzu. Opis: SPECYFIKACJA sekcja 4, README firmware R-01, odbiór pkt 7 | tabela stanów pakiet/USB i sekwencja TSR — odbiór sprzętu |
| M1-02 | ważne | TEST: przewód auta odpięty z X1.13, zworka X1.13 ↔ X1.3 (VMOTOR), nigdy oba naraz; zakres 9,0–17,3 V; `config.ch7_source`, `hotsoak_point.vbat_source` | `probe_review_m1.py`: 0 / 8,9 / 17,4 V → SUPPLY, 13,5 / 16,8 V → READY (R1: 16,8 V → SUPPLY) |
| M1-03 | ważne | bramka napędu nie zwalnia się bez pełnego startu TWDT + RTC WDT; `test` odrzucany; tylko restart | rzeczywiste `safety()` + `board_release()`: R1 DRIVE_EN = 1, 6.3.1 DRIVE_EN = 0 |
| M1-04 | ważne | opis „1 s” usunięty; stan niezapisanej kolejki i ostatniego fsync w `daq_stats` / `status`; procedura wyłączenia | dokumentacja + pola logu; strata przy zaniku — odbiór pkt 10 |
| M1-05 | ważne | generator schematu uzupełnia `.kicad_pro` (tylko `meta`, `sheets`); bramka `check_pro_preserved.py` w `run_schematic.py` | na generatorze R1 bramka zgłasza utratę `board`, `net_settings` i 6 innych sekcji; na poprawionym — zachowane |
| M1-06 | ważne | tabela LOGGER → TEST → LOGGER: pięć żył ECU (X1.5, X1.7–X1.10) odłączonych i zaizolowanych, zworki X1.11–X1.13, pomiar ciągłości; usunięte pozostałości „nowy ARM” | SPECYFIKACJA sekcja 5, `06-diagnostyka.md` |
| M1-07 | drobne | `tests/fixtures/` (profile 6.2-s1, `board.c` P09 R1) z SHA-256 i commitem; `test_preflight.py`; model 6.1-rc1 w paczce recenzji | Python 104/104 bez zależności od innych katalogów poza 6.1-rc1 |
| M1-08 | ważne | wydruki konsoli po zwolnieniu blokady; przycisk w każdym obiegu `safety`; ruch bez oceny sterowania > 20 ms = STOP (`control_stale`); watchdog tylko przy postępie albo bez napędu | blokada 400 ms w MANUAL: R1 DRIVE_EN = 1, 0 odczytów przycisku; 6.3.1 DRIVE_EN = 0, STOP, 400 odczytów; kontrola: bez blokady MANUAL trwa |
| M1-09 | ważne | ważność próbki = migawka i bieżący stan drivera; INVALID do rekonfiguracji z nowym `config_id` (`adc_recovery`), ponowienia co 1 s | TIMEOUT → dwa dobre transfery: R1 rekordy bez INVALID; 6.3.1 INVALID, brak wartości, żądanie odzyskania |
| M1-10 | ważne | eksporter: pola MCP3201 tylko przy `local_current: true`; kolumna `sens_5v_v` | sesja −1 / 0 / +1 A: R1 puste; 6.3.1 −0,99979 / 0,00017 / 1,00012 A (błąd < 1e-4) |
| M1-11 | ważne | `cal <bank> 5` kasuje `icalok` i metrykę; `daqmodule` kasuje akceptację prądu | R1 ical = 1 po `cal 1 5`; 6.3.1 ical = 0, `qualify` niemożliwe bez nowego odbioru; `cal 1 2` nie rusza prądu |
| M1-12 | drobne | REF / FEEDBACK tylko dla skończonych napięć | NaN: R1 maska 9, 6.3.1 maska 0; prawdziwe 4 V nadal REF |

Regresje: `Rewizje/EGRLab-v6.3-m1/tests/probe_review_m1.py` (w `run_host.py`), wyniki `verification/review-regressions.json` (6.3.1) i `review-regressions-r1.json` (te same bodźce na źródłach R1: wszystkie grupy FAIL). Próby mutacyjne: 39/39 z zerową, w tym 8 nowych cofających poprawki (`r_m102…r_m112`).

## Uwagi bez wagi błędu (przyjęte jako punkty odbioru)

- TPS2553: limit z R31 232 k to ok. 99–139 mA (typ. 117 mA), nie twarde 100 mA — poprawiony opis w SPECYFIKACJI.
- Zero prądu zależy od 5 V (ok. 20 mA na 10 mV): odbiór — zero zimne / ciepłe, przy SD, Wi-Fi i PWM.
- PWM a 2 kS/s (OS8 to ok. 10 µs, nie średnia z 500 µs): kwalifikacja metryk ze wzorcem i oscyloskopem.
- Kelvin K_MINUS 25 mm przez In2: próba DC / PWM ze wzorcem i skok wspólny przy zerowym prądzie; przy następnej zmianie layoutu zbliżyć trasy.
- Kontrola powrotów odsprzęgania (`return_check`) nie obejmuje U3 i bada tylko GND — do rozszerzenia przy następnej rewizji PCB (stałe limity par, przelotki, mutacje rzeczywistej kopii PCB).
- AVCC 4,75–5,25 V a dokładność TSR i spadek na R7: budżet przy deklaracji zakresu temperatur.

## Czego nie zmieniano

PCB / CAM / paczka `Plytki/M1-PCB-R1-zamowienie` (ZIP `824058fb…` ważny; `projekt/` to migawka wydania R1 — od niej różnią się tylko narzędzia `src/build_schematic.py`, `run_schematic.py`, nowy `check_pro_preserved.py` i pliki weryfikacji schematu; plik PCB bajtowo ten sam). **Sprzęt: NIE ZBADANO.**
