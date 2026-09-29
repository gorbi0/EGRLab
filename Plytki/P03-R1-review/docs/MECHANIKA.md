# P03 PCB R1 — mechanika i przymiarka

25.09.2026 · Claude. Współrzędne w mm od lewego górnego narożnika płytki (oś y w dół), z `eda/P03.kicad_pcb`. Do przymiarki 1:1 służy strona 2 pliku `output/pdf/P03-R1-PCB.pdf` (druk 100 %, belka 100 mm).

## Obrys i mocowanie

160 × 120 mm, otwory Ø3,2 mm: H1 (5; 5), H2 (155; 5), H3 (5; 115), H4 (155; 115) — jak P01/P02 — oraz **H5 (155; 38)**. H2 i H5 obejmują złącze J1 z obu stron (17,8 i 18,9 mm od jego środka): v6.1 wymaga dwóch punktów mocowania każdej płytki blisko złącza B2B, bo złącze nie jest elementem nośnym. Asymetryczny wspornik z v6.1 (blokada obrotu i przesunięcia o rząd) to element obudowy, nie PCB.

## J1 DAQ → P05

| Parametr | Wartość |
|---|---|
| Typ | gniazdo kątowe 2 × 8, 2,54 mm (footprint KiCad PinSocket_2x08_P2.54mm_Horizontal) |
| Pin 1 / pin 15 | (147,00; 31,00) / (147,00; 13,22); piny nieparzyste x = 147,00, parzyste x = 149,54 |
| Czoło gniazda | x = 159,63 (0,37 mm przed krawędzią), otwory w stronę P05 |
| Klucz | pozycja 2: pin usunięty z wtyku P05, otwór gniazda zaślepiony (v6.1) |

P05 R1 (Astra) przyjął dokładnie to położenie J1 z kopii roboczej P03 i dystans krawędzi 1 mm (P05 od x = 161); w wydaniu R1 J1 się nie zmieniło. P05 ma kątowy wtyk 2 × 8 przy lewej krawędzi. Wtyk i gniazdo patrzą na siebie, więc układ pinów widziany od czoła jest lustrzany — **test ciągłości pin 1 → 1 … 16 → 16 ma pierwszeństwo przed wyglądem listew** (v6.1). Odstęp płytek wynika z długości pinów wtyku i głębokości gniazda, a różnicę wysokości rzędów styków nad płytkami wyrównują dystanse; oba złącza i dystanse kupić przed zamówieniem PCB P03 i P05.

## Moduły na gniazdach

| Moduł | Położenie | Uwagi |
|---|---|---|
| M1 Waveshare ESP32-S3-DEV-KIT-N32R16V | rzędy x = 11,43 (J3) i 34,29 (J1), piny y = 3,41 … 56,75; pin 1 obu rzędów na dole (od strony anteny) | USB-C przy y ≈ 0,25 (górna krawędź, wtyk wchodzi z zewnątrz); koniec anteny y ≈ 64,75, pod nim strefa bez miedzi 7,1–38,6 × 58,25–72,75. Obrys 25,5 × 64 mm przyjęty z klasy DevKitC-1 — **potwierdzić na posiadanym module**. Mocowanie tylko 44 stykami gniazd |
| SD1 Adafruit 4682 | listwa 1 × 9 w y = 96,60 (pin 1 x = 58,50 … pin 9 x = 38,18); dystanse M2.5 w (58,50; 114,38) i (38,18; 114,38) | Karta wysuwa się przy dolnej krawędzi (koniec karty 0,5 mm przed krawędzią). Strefy bez miedzi Ø6 mm pod dystanse i nakrętki |

## Złącza wiązek

| Złącze | Krawędź | Obrys (x; y) | Uwagi |
|---|---|---|---|
| J10 LV03 (z P02) | górna | pady y = 16,0 (1 = 5V przy x = 44,0 … 4 = GND przy 55,43); kotwa (41,0; 3,5) i (58,43; 3,5) | żyły lutowane, opaska 12,5 mm od lutów, pas bez miedzi pod opaską |
| J8 CAN (P10) | górna | 64,4–80,8 | IDC 2 × 3, klucz 4 |
| J3 ITEST (P07) | górna | 92,9–109,2 | IDC 2 × 3, klucz 2 |
| J2 ILOG (P06) | górna | 112,2–131,1 | IDC 2 × 4, klucz 2 |
| J4 SAFE (P04) | lewa | y 77,7–106,8 | IDC 2 × 8, klucz 4 |
| J6 SFAULT (P08) | dolna | 16,1–32,5 | IDC 2 × 3, klucz 3 |
| J7 TEMP (P09) | dolna | 64,3–85,7 | IDC 2 × 5, klucz 4 |
| J9 PANELCORE (P11) | dolna | 88,6–107,7 | Mini-Fit Jr 8p, pionowe |
| J5 DIR (P07) | dolna | 110,6–129,5 | IDC 2 × 4, klucz 4 |

Wszystkie box headery leżą dłuższym bokiem wzdłuż krawędzi (taśma zagina się po łatwej osi), rząd nieparzysty (sygnały) od strony płytki.

## Wysokości (orientacyjnie, do potwierdzenia na częściach)

Najwyżej: M1 na gniazdach 1 × 22 (gniazdo ok. 8,5 mm + moduł), SD1 na gnieździe 1 × 9, złącza IDC z wtykami, Mini-Fit z wtykiem. Adaptery SO14 na goldpinach ok. 6–7 mm, MCP23017 i 74HC139 w podstawkach. Nad USB-C i kartą nic nie wystaje poza krawędź płytki.

## Przymiarka 1:1 — lista

1. Belka 100 mm i obrys na wydruku.
2. Moduł Waveshare: rzędy na 22,86 mm, położenie USB-C na krawędzi, koniec anteny nad strefą bez miedzi.
3. Moduł 4682: listwa 1 × 9 i otwory M2.5, karta przy krawędzi.
4. Jeden adapter Kamami SO14 (18 × 18 mm) na dowolnym U1x/U2x.
5. Gniazdo J1 z wtykiem P05 i dystansami: czoło przy krawędzi, zgodność wysokości.
6. Box headery IDC i Mini-Fit: obrysy i kierunek zatrzasku.
