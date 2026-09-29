# P03 — stan zakupów względem R1

25.09.2026. Porównanie `docs/BOM.csv` z rejestrem `Zamowione/ZAMOWIONE.md` (zamówienia TME, Mouser i Kamami z 24.09). Nic tu nie jest zamawiane; lista pomaga złożyć następne zamówienie.

## Już zamówione lub posiadane

| Pozycja | Ilość | Źródło |
|---|---|---|
| Waveshare ESP32-S3-DEV-KIT-N32R16V (M1) | 1 | posiadany |
| MCP23017-E/SP (U1) | 1 | Mouser |
| SN74HC139N (U2) | 1 | Mouser |
| TPS3808G33DBVR (U3) + Chip Quik PA0085 | 1 + 1 zapasowy TPS3808 | Mouser |
| 74LVC125AD Nexperia (U11–U14, U21–U23) | 7 | Mouser |
| Adapter Kamami 575068 SO14 → DIP (18 × 18 mm) | 7 | Kamami |
| Podstawka DIP16 (U2), 2 × DIP14 w linii jako DIP28 (U1) | 1 + 2 | Kamami |
| Goldpin 1 × 40 na piny adapterów | wspólna pula | Kamami |

## Do kupienia

| Pozycja | Ilość | Uwagi |
|---|---|---|
| 100 nF X7R, raster 5 mm (Vishay K104K15X7RF53H5) | 11 | C1–C11 |
| 10 k 1 % 0207 | 9 | R1, R2, R3, R5, R6, R7, R8, R11, R13 |
| 4k7 1 % 0207 | 2 | R9, R10 (I²C) |
| 330 Ω 1 % 0207 | 1 | R12 (SCOPE_TRIG) |
| 1 k 1 % 0207 | 1 | R4 (LED) |
| 0 Ω 0207 lub drut | 1 | R14 (CORE_LINK) |
| LED 3 mm zielona (Kingbright L-934GD) | 1 | LED1 |
| Listwa żeńska 1 × 22, 2,54 mm (lub przycięta 1 × 40) | 2 | gniazda M1 |
| Adafruit 4682 (microSD 3 V) | 1 | SD1; do tego listwa żeńska 1 × 9, 2 dystanse M2.5 z wkrętami i nakrętkami |
| **Gniazdo kątowe 2 × 8, 2,54 mm, Au** (np. Samtec SSW-108-02-G-D-RA) | 1 | J1 DAQ. **Kupić razem z kątowym wtykiem 2 × 8 dla P05 i dystansami** — wysokości rzędów obu części decydują o dystansach (v6.1). Wcześniej planowane pionowe SSW-108-01-G-D nie pasuje do decyzji „obok siebie” |
| Box header IDC 2 × 3, 2,54 mm, Au | 3 | J3 ITEST, J6 SFAULT, J8 CAN |
| Box header IDC 2 × 4, 2,54 mm, Au | 2 | J2 ILOG, J5 DIR |
| Box header IDC 2 × 5, 2,54 mm, Au | 1 | J7 TEMP |
| Box header IDC 2 × 8, 2,54 mm, Au | 1 | J4 SAFE |
| Molex Mini-Fit Jr 5566-08A, pionowe 8p, styki Au | 1 | J9 PANELCORE |
| Dystanse M3 do płytki | 5 | cztery narożniki jak P01/P02 + H5 przy J1 |

Wtyki IDC z odciążką, taśmy i wiązka LV03 należą do BOM modułów po drugiej stronie (v6.1, kolumna „właściciel wiązki”), nie do P03. Wiązka CAN do P10 ma teraz 6 pozycji (2 × 3).

## Przed zamówieniem PCB

Przymiarka 1:1 z modułem Waveshare, modułem 4682, gniazdem J1 z wtykiem P05 i jednym adapterem SO14 (patrz `docs/MECHANIKA.md`).
