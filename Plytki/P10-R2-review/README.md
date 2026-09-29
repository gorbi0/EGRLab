# P10 R2 — CAN pasywny w formacie S1 (schemat)

29.09.2026, sesja w chmurze. **Status: schemat i kontrole do lokalnej recenzji. PCB nie powstało** (layout robi sesja lokalna), sprzęt NIE ZBADANO. R2 powstała na kopii generatora z `Plytki/P10-R1-review` (zamknięty pakiet, niezmieniony); wymagania: `Plytki/Format-S1/SPECYFIKACJA-FORMATU-S1.md` (S1-2) i zadanie `Plytki/Format-S1/zadania/ZADANIE-P09-P10-S1.md`.

**Klasa płytki:** 1/3 (53 × 100 mm), slot S1 poziomu 1 (dystans nad nią 25 mm, SOIC od spodu dozwolone na tym poziomie). Topologia bez zmian: TCAN1051V z S i TXD na stałe do VIO, PESD2CAN, bufor RX 74LVC125AD z Ioff, brak terminatora, brak ścieżki CAN_TX do transceivera; tylko odbiór.

## Zmiany R1 → R2

| Element | R1 | R2 |
|---|---|---|
| Złącza do innych płytek | J1 LV10 (Mini-Fit 4p) i J2 CAN_CORE (IDC 6) lutowane do PTH | **J1 = J_BP**: kątowe obudowane IDC 2×5, krawędź A, środek slotu; piny nieparzyste GND, parzyste: 5V_SYS ×2 (piny 2, 10), 3V3_IO (4), CAN_TX (6), CAN_RX (8) |
| Wejście OBD | J3, skrętka 300 mm lutowana do PTH | bez zmian (J3, W3) |
| Punkty pomiarowe | TP1–TP6 (pola) | **J2 = listwa serwisowa** kątowy goldpin 1×9 na krawędzi B, GND na kołkach 1 i 9; kołki 2–8 przez R3–R9: 5V_SYS, 3V3_IO, RX_RAW, CAN_RX, CAN_TX (1 kΩ), CAN_H, CAN_L (10 kΩ) |
| R2 (10 k), R8, R9 (10 k serwisowe) | DIN0207 leżący | **posiadane MF0207 na stojąco** (`…P5.08mm_Vertical`) |
| R1 (100 Ω), R3–R7 (1 k) | THT | **nowe SMD 1206** |
| C1–C3 (100 n) | 0805 | **posiadane K104K15X7RF5TH5, radialne 5 mm** |
| C4, C5 (4µ7) | 0805 | **nowe SMD 1206** X7R 25 V |
| U1, U2, D1 | bez zmian | bez zmian |
| Obrys / mocowanie | 80 × 70 mm | 53 × 100 mm, otwory slotu M3 wg S1 (rysuje layout) |

Przypisanie części do rejestru wynika z dosłownego dopasowania wartości i typu do `Zamowione/zamowione.csv` (kolumna `zrodlo` w `docs/BOM.csv`). Bilans zapasu razem z P09: `docs/ZAKUPY.md`.

## Wyniki (szczegóły: `verification/QA.md`)

| Kontrola | Wynik |
|---|---|
| ERC (2 arkusze) | 0 naruszeń |
| Netlista pin po pinie względem `parts.py` | 20 części, 74/74 pinów, 19 sieci, 0 błędów |
| Kontrole elektryczne | 32/32 PASS (w tym nowe: J_BP nieparzyste = GND, parzyste tylko użyte sygnały i zasilania, ciągłość z R1, 5V_SYS ×2, zgodność z `J_BP.csv`; listwa ≤ 13, GND na końcach, rezystor przy węźle, zgodność z `SERWIS.csv`; CAN_TX tylko do J_BP i kołka; źródła części THT/SMD) |
| Próby ujemne | 36/36 mutacji wykrytych, próba zerowa (bez zmiany) czysta |
| Orientacyjna zajętość (`src/powierzchnia.py`) | suma obrysów części 1208 mm² wobec ok. 4486 mm² użytecznej powierzchni 53 × 100 mm (27 %, bez rozmieszczenia) |

## Decyzje projektowe (sporne oznaczone)

- **5V_SYS na dwóch pinach J_BP** — zgodnie z S1 §5 („co najmniej 2 pinach”); wszystkie 5 parzystych pinów 2×5 jest użytych, a P10 pobiera z 5 V ok. 70 mA (transceiver).
- **CAN_H i CAN_L na listwie przez 10 kΩ, nie 1 kΩ** — to węzły zewnętrznej magistrali pojazdu; spadnięta sonda lub zwarcie sąsiednich kołków ma ją obciążać jak najmniej. Wada: pasmo obserwacji kołków ok. 1 MHz, więc przebiegi mierzyć na J3.
- **Kołek CAN_TX zostaje** (przez 1 kΩ), bo próba „brak TX” w odbiorze wymaga wglądu w ten sygnał (R1: TP6); nadal brak jakiejkolwiek ścieżki do U1.
- **Rezystory serwisowe 10 kΩ z rejestru (THT na stojąco)** — dosłowne stosowanie reguły „wartość i typ jak w rejestrze”; zużywa zapas, zob. otwarte punkty.

## Otwarte punkty

1. Zapas z rejestru: 10 k — P09 + P10 razem 9 szt. wobec 7; 100 n — razem 6 szt. wobec 5 (opis PR).
2. Listwa serwisowa musi być **kątowa** (posiadana 1×40 jest prosta); typ IDC J_BP do wyboru w zakupach.
3. J3 (OBD) i kotwa 12 mm: położenie na krótkiej krawędzi płytki do ustalenia w layoutcie; płytka jest na poziomie 1, więc wychodzi bliżej ściany wejść.
4. `docs/MONTAZ.md` i `REPRODUKCJA.md` z R1 nie są przenoszone (dotyczą PCB 80 × 70 mm); powstaną z layoutem. `docs/INTEGRACJA.md` przeniesione (poprawiona jedna linia o TP6).

## Uruchomienie

W chmurze: `scripts/egrlab-docker python3 src/run_schematic.py` (ok. 15 s): budowa schematu, `make_docs.py` (CSV dla P12 i zakupy), ERC, netlista, `verify_schematic.py`, `verify_electrical.py`, PDF i PNG, `QA.md`, manifest SHA-256. Lokalnie: Python KiCada 10.0.6, `KICAD_CLI` i `PDFTOPPM`.

## Zawartość

| Ścieżka | Zawartość |
|---|---|
| `eda/` | Projekt KiCad 10 (2 arkusze A3), biblioteki lokalne |
| `output/pdf/P10-R2-schemat.pdf`, `output/previews/` | Schemat i podglądy |
| `docs/J_BP.csv`, `docs/SERWIS.csv` | Kontrakty dla płytki połączeń P12 i dla odbioru |
| `docs/parts.json`, `docs/BOM.csv`, `docs/ZAKUPY.md`, `docs/interfejsy.csv`, `docs/WIAZKI.md` | Części, piny, źródło (rejestr/nowe), zakupy, jedyna wiązka W3 |
| `docs/ODBIOR.md`, `docs/INTEGRACJA.md` | Formularz odbioru (kołki listwy), zależności firmware |
| `reference/` | Części P02-R3/J10 i P03-R2/J8 (sprawdzenie ciągłości sygnałów z R1) |
| `verification/` | ERC, netlista, kontrole, próby ujemne, logi, manifest |
| `src/` | Generatory (`cadlib.py`, `parts.py`, `build_schematic.py`, `make_docs.py`, kontrole, `run_schematic.py`) |
