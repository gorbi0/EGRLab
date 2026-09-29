# P02 R4 — stan prac (29.09.2026, przerwane przed schematem)

Dokument do wznowienia pracy w dowolnej sesji, także w chmurze. Decyzje i wymagania są w `SPECYFIKACJA-P02-R4.md`, liczby w `obliczenia.json` (`python src/obliczenia.py`).

## Zrobione

1. Specyfikacja przyjęta przez użytkownika 29.09: D-01 ze zmianą (VBAT z klemy akumulatora w komorze silnika), D-02…D-07 bez zmian. Przetwornice TSR zostają.
2. Obliczenia: UVLO dla topologii z P01, podtrzymanie 2200 µF, ładowanie C_H, straty, CH7, czas pracy pakietu.
3. Rozpoznany łańcuch generatorów P02 R3 (`Plytki/P02-R3-review/src/`), na którym ma powstać R4:
   - `parts.py`: jawna lista części z pinami i sieciami, footprinty kopiowane z bibliotek KiCad 10.0.6 albo generowane;
   - `build_schematic_r2.py`: arkusze A3; każdy niepodłączony pin dostaje etykietę swojej sieci;
   - `verify_schematic.py`: netlista z kicad-cli porównywana pin po pinie z `parts.py`, ERC = 0;
   - dalej `build_board.py`, `run_layout.py`, `route_critical.py`, `check_electrical.py`, `negative_controls.py`, `verify_pcb.py`, `make_pdf_r2.py`, `package_review.py`.
4. Rozpoznany tor włącznika i sterowania P01 R3 (`Plytki/P01-R3-review/docs/parts.json`). Przechodzi do R4 1:1, zestawienie niżej.

## Poprawka architektury

Pierwsza wersja specyfikacji miała jeden P-MOSFET do dwóch zadań. P-MOSFET chroniący przed odwrotną polaryzacją ma dren od strony pakietu, więc jego dioda strukturalna przewodzi w kierunku zasilania i wyłączony tranzystor nie odcina obciążenia. Dlatego są dwa tranzystory przeciwsobnie, połączone źródłami (węzeł SW_COM):

- **Q_REV** (SUP53P06): D = BAT_IN, S = SW_COM, bramka 100 kΩ do GND, BZX55C15 między bramką a źródłem (katoda do SW_COM). Przy poprawnej polaryzacji jest stale włączony, przy odwrotnej zatkany.
- **Q_SW** (SUP53P06, dawne Q1 z P01): S = SW_COM, D = VSW, sterowany torem z P01 R3.

Straty przy 3,5 A: po 0,37 W na każdy tranzystor, radiatory niepotrzebne.

## Tor sterowania przeniesiony z P01 R3

| P01 R3 | W P02 R4 | Zmiana |
|---|---|---|
| Q1 SUP53P06 | Q_SW: G = GATE, D = VSW, S = SW_COM | dren do VSW (w P01 przez LK1 do VPROT) |
| Q2 SUP53P06 + R27 10 Ω/2 W | Q_OFF: szybkie wyłączanie, podciąga GATE do SW_COM | bez zmian |
| R23 2,2 kΩ/2 W (bramka Q_OFF do GND) | **22 kΩ/0,5 W** | **decyzja użytkownika 29.09:** w P01 szybkość była potrzebna na OVP, którego przy pakiecie nie ma; ok. 55 µs zamiast ok. 7 µs i 13 mW zamiast 128 mW strat stałych |
| R24 100 kΩ, D9 BZX55C15 (bramka Q_OFF) | bez zmian | — |
| Q3 2N5551, R17 4,7 kΩ, R18 47 kΩ, R21 100 kΩ | załączanie Q_SW | bez zmian |
| Q4 2N5401, R25 47 kΩ, R26 10 kΩ; Q5 2N5551, R19 4,7 kΩ, R20 47 kΩ | zwalnianie Q_OFF przy ENABLE | bez zmian |
| R22 470 kΩ, C5 10 nF (GATE–VSW), C6 1 µF MKS2 (GATE–SW_COM), D4 BZX55C15 | bramka Q_SW | C5 do VSW zamiast VPROT |
| Q6 2N5551, R14 4,7 kΩ, D7/D8 1N4148, R15 100 kΩ, R16 10 kΩ | ENABLE z linii OK | bez zmian |
| U1 LM2936Z-5.0, C7 22 µF, C8 100 nF, R1 | AUX5 | wejście z V_CTRL = suma diodowa SW_COM i VLOG (2 × 1N4148), więc AUX5 trwa przez podtrzymanie; bez D5 1.5KE18A (napięcie pracy 15,3 V < 16,8 V); R1 150 Ω/2 W można zmniejszyć (nie ma udarów z instalacji) |
| U2 LM2903 | sekcja A: UVLO; sekcja B: PFAIL_N z tego samego węzła CMP | zamiast sekcji OVP |
| R9–R12 HOLCO 0,1 %, RV1, C12, D6 | nowy dzielnik UVLO na rezystorach 1 % | bez trymera i precyzyjnych rezystorów (±0,34 V wystarcza) |
| U3 TL431BILP, R3 820 Ω, R4 10 kΩ | REF z AUX5 | bez zmian |
| U4 MCP120-450, R13 2,2 kΩ | POR linii OK i jej podciągnięcie do AUX5 | bez zmian |
| Q7/Q8 2N5551, R30–R33, R34 0 Ω | SAFE_N i pętla PG_SEND–PG_LINK (J13) | bez zmian |
| J3 INHIBIT | przełącznik PWR w dzielniku UVLO (J14) | rozwarty albo przerwany przewód = wyłączone |
| D2 STPS20100CT, D1 15KPA24CA, radiatory SK129, IB-6 | — | odpadają; 5KP18A (D3) przechodzi jako transil na VSW |

## UVLO (przeliczone dla tej topologii)

SW_COM → 1,0 kΩ → J14.1 → przełącznik PWR → J14.2 → 41,2 kΩ → DIV (10 nF do GND, 10,0 kΩ do GND) → R_iso 10,0 kΩ → CMP ← Rh 464 kΩ ← OK (0/5 V).

Wynik: załączenie 13,53 V, wyłączenie 12,51 V (3,38 / 3,13 V na ogniwo), rozrzut ±0,34 V. Dzielnik pobiera 0,32 mA przy 16,8 V. Wartości z pierwszej wersji specyfikacji (43,2 kΩ i 536 kΩ, OK przełączające do napięcia pakietu) są nieaktualne.

Podtrzymanie po PFAIL_N (2200 µF −20 %): 14,2 ms przy 6 W i 28,3 ms przy 3 W, czyli wymaganie Z-08 jest spełnione.

## Pozostałe bloki (bez zmian względem specyfikacji)

- **Podtrzymanie:** R_ch 22 Ω bezpiecznikowy → D_ch STPS20100CT → C_H 2200 µF/35 V (+ 10 kΩ rozładowujący) → D1 STPS20100CT (suma z VSW) → VLOG.
- **VSW:** transil 5KP18A i ≤ 100 µF; VMOTOR przez F_M 5 A; F2/F3 1 A (bezpieczniki samochodowe mini, D-04).
- **Przetwornice i PSU_OK:** TSR z C5–C8 jak R3. PSU_OK z MCP120-300/-450, 74LVC125A na adapterze i SN74HC08N; bramki B–D wolne, wejścia do GND.
- **VBAT:** J15 → 10 kΩ 0,5 W → P6KE24CA → J11.1 (Mini-Fit 2p).
- **Złącza J1–J16:** według `interfejsy.csv`.

## Bilans części z zakupów P01 (rejestr `Zamowione/`)

| Część | Kupione | Potrzebne w R4 |
|---|---|---|
| SUP53P06-20 | 3 | 3 (Q_REV, Q_SW, Q_OFF), dokupić 1–2 na zapas |
| 2N5551 | 7 | 5 (Q3, Q5, Q6, Q7, Q8) |
| 2N5401 | 3 | 1 |
| BZX55C15 | 4 | 3 |
| 1N4148 | 5 | 4 |
| LM2936Z-5.0 / LM2903P / TL431BILP | 2 / 2 / 2 | po 1 |
| MCP120-450 (P01 U4) | kupiony | 1 |
| MKS2 1 µF | 2 | 1 |
| STPS20100CT | 2 | 2 (D1, D_ch), bez zapasu |
| 5KP18A | 2 | 1 |

## Następny krok

1. Nowy pakiet `Plytki/P02-R4-review/` na kopii generatorów z `P02-R3-review/src/`, z footprintami TO-220, wiązki PG i zwory z P01 R3.
2. `parts.py` R4. Proponowane arkusze:
   - WEJ: pakiet, Q_REV/Q_SW/Q_OFF, VSW, VMOTOR, podtrzymanie;
   - STER: AUX5, UVLO, ENABLE, SAFE_N, PFAIL_N, LED;
   - LV: TSR i złącza LV;
   - MON: PSU_OK, VBAT.
3. Schemat, `verify_schematic` (netlista pin po pinie, ERC 0) i `check_electrical` (UVLO, podtrzymanie, straty, zakresy napięć) z próbami ujemnymi.
4. PCB ≤ 115 × 85 mm, DRC, przymiarka, recenzja.

Wykonanie: etap 1 (kroki 1–3, schemat) w sesji w chmurze, polecenie w `docs/CHMURA.md` („Kolejne zadania”); etap 2 (krok 4, PCB) po lokalnej recenzji schematu.
