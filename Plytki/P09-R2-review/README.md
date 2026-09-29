# P09 R2 — TEMP w formacie S1 (schemat)

29.09.2026, sesja w chmurze. **Status: schemat i kontrole do lokalnej recenzji. PCB nie powstało** (layout robi sesja lokalna), sprzęt NIE ZBADANO. R2 powstała na kopii generatora z `Plytki/P09-R1-review` (zamknięty pakiet, niezmieniony); wymagania: `Plytki/Format-S1/SPECYFIKACJA-FORMATU-S1.md` (S1-2) i zadanie `Plytki/Format-S1/zadania/ZADANIE-P09-P10-S1.md`.

**Klasa płytki:** 1/3 (53 × 100 mm), slot S3 poziomu 3. Logika (U1/U2 74LVC125AD z Ioff, dekoder U3 HC139, moduły MAX31856 XU, JP1/JP2 wyboru VIN) bez zmian względem R1.

## Zmiany R1 → R2

| Element | R1 | R2 |
|---|---|---|
| Złącza do innych płytek | J1 LV09 (Mini-Fit, 4 żyły) i J2 TEMP (IDC 10, taśma) lutowane do PTH | **J1 = J_BP**: kątowe obudowane IDC 2×8, krawędź A, środek slotu; piny nieparzyste GND, parzyste: 5V_SYS ×2, 3V3_IO, SPI3_SCLK, SPI3_MOSI, SPI3_MISO, TC1_CS, TC2_CS |
| Punkty pomiarowe | TP1–TP13 (pola) | **J2 = listwa serwisowa** kątowy goldpin 1×13 na krawędzi B, GND na kołkach 1 i 13; kołki 2–12 przez rezystory R20–R30 (1 kΩ, przy węzłach): 3V3_IO, 5V_SYS, TC1_VIN, TC2_VIN, TC1_3VO, TC2_3VO, CS1_BUF, CS2_BUF, OE1_N, OE2_N, SPI3_MISO |
| FLT/DRDY modułów | pola TP10–TP13 | nieprzyłączone (NC) |
| R1, R2, R5, R6, R18, R19 (10 k), R3, R4, R7–R10, R13 (100 k) | DIN0207 leżące, raster 10,16 | **posiadane MF0207 na stojąco** (raster 5,08, obudowa `…P5.08mm_Vertical`) |
| R11, R12 (100 Ω), R14–R17 (47 Ω) | THT | **nowe SMD 1206** |
| C1–C3 (100 n) | 0805 | **posiadane K104K15X7RF5TH5, radialne 5 mm** |
| C4, C5 (4µ7), C6, C7 (1 µ) | 0805 | **nowe SMD 1206** X7R 25 V |
| Pozostałe | — | bez zmian (U1–U3, J3/J4 gniazda modułów, JP1/JP2) |
| Obrys / mocowanie | 100 × 100 mm, 4 otwory | 53 × 100 mm, otwory slotu M3 wg S1 (rysuje layout) |

Przypisanie części do rejestru wynika z dosłownego dopasowania wartości i typu do `Zamowione/zamowione.csv` (kolumna `zrodlo` w `docs/BOM.csv`). Bilans zapasu: `docs/ZAKUPY.md`.

## Wyniki (szczegóły: `verification/QA.md`)

| Kontrola | Wynik |
|---|---|
| ERC (4 arkusze) | 0 naruszeń |
| Netlista pin po pinie względem `parts.py` | 46 części, 171/171 pinów, 49 sieci, 0 błędów |
| Kontrole elektryczne | 52/52 PASS (w tym nowe: J_BP nieparzyste = GND, parzyste tylko użyte sygnały i zasilania, ciągłość z R1, 5V_SYS ×2, zgodność z `J_BP.csv`; listwa ≤ 13, GND na końcach, 1 kΩ przy węźle, zgodność z `SERWIS.csv`; źródła części THT/SMD) |
| Próby ujemne | 35/35 mutacji wykrytych, próba zerowa (bez zmiany) czysta |
| Orientacyjna zajętość (`src/powierzchnia.py`) | suma obrysów części 3314 mm² wobec ok. 4486 mm² użytecznej powierzchni 53 × 100 mm (74 %, bez rozmieszczenia; oba gniazda modułów ok. 700 mm² każde) |

## Decyzje projektowe (sporne oznaczone)

- **5V_SYS na dwóch pinach J_BP** — zgodnie z S1 §5 („co najmniej 2 pinach”), choć P09 pobiera z 5 V niewiele (tylko VIN modułów przy JP 2–3 i C5); wszystkie 8 parzystych pinów 2×8 jest użyte.
- **Wszystkie kołki serwisowe po 1 kΩ** — węzły P09 to szyny i logika; 3Vo modułów też (wyjście regulatora, nie węzeł wysokoimpedancyjny).
- **Na listwie brak wejść SCLK/MOSI/TC1_CS/TC2_CS z J_BP** — 11 kołków wystarcza na punkty odbioru specyficzne dla P09 (VIN, 3Vo, CS za buforem, OE, MISO); wejścia mierzy się na listwie P03.
- **FLT/DRDY nieprzyłączone** — bez pól testowych i wolnych żył.

## Otwarte punkty

1. Przymiarka 1:1 modułów MAX31856 XU i kwalifikacja zasilania (`docs/MODUL-KWALIFIKACJA.md`) — bez zmian względem R1; obrys gniazd nadal prowizoryczny.
2. Layout: 74 % zajętości wg obrysów; J_BP środek x = 26,5 mm, listwa J2 w x = 10–43 mm, rezystory R20–R30 od spodu.
3. Zapas części z rejestru (zob. `docs/ZAKUPY.md` i opis PR): 100 n wymaga 6 szt. na P09+P10 wobec 5.
4. Listwa serwisowa musi być **kątowa** (posiadana 1×40 jest prosta); typ IDC J_BP do wyboru w zakupach.
5. Poprawka firmware MAX31856 z R1 (`P09-R1-review/firmware`) bez zmian, do scalenia przy integracji P03.

## Uruchomienie

W chmurze: `scripts/egrlab-docker python3 src/run_schematic.py` (ok. 20 s): budowa schematu, `make_docs.py` (CSV dla P12 i zakupy), ERC, netlista, `verify_schematic.py`, `verify_electrical.py`, PDF i PNG, `QA.md`, manifest SHA-256. Lokalnie: Python KiCada 10.0.6, `KICAD_CLI` i `PDFTOPPM`.

## Zawartość

| Ścieżka | Zawartość |
|---|---|
| `eda/` | Projekt KiCad 10 (4 arkusze A3), biblioteki lokalne |
| `output/pdf/P09-R2-schemat.pdf`, `output/previews/` | Schemat i podglądy |
| `docs/J_BP.csv`, `docs/SERWIS.csv` | Kontrakty dla płytki połączeń P12 i dla odbioru |
| `docs/parts.json`, `docs/BOM.csv`, `docs/ZAKUPY.md` | Części, piny, źródło (rejestr/nowe), zakupy |
| `docs/PROJEKT.md`, `docs/ODBIOR.md`, `docs/MODUL-KWALIFIKACJA.md` | Opis, formularz odbioru (kołki listwy), kwalifikacja modułu (bez zmian) |
| `reference/` | Części P02-R3/J9 i P03-R2/J7 (sprawdzenie ciągłości sygnałów z R1) |
| `verification/` | ERC, netlista, kontrole, próby ujemne, logi, manifest |
| `src/` | Generatory (`cadlib.py`, `parts.py`, `build_schematic.py`, `make_docs.py`, kontrole, `run_schematic.py`) |
