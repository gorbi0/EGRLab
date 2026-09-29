# P03 PCB R1 — layout

25.09.2026 · Claude. Płytka z netlisty schematu P03-R1 (`verification/P03.xml`), rozmieszczenie `src/placement.json`, trasy zablokowane `src/route_critical.py`, reszta Freerouting 2.1.0. Liczby z `verification/pcb-checks.json` i `routing/*.json`.

## Format i rozkład

160 × 120 mm jak P01/P02, 2 × 35 µm, laminat 1,6 mm. Otwory M3 (3,2 mm) w narożnikach P01/P02 i piąty, H5 (155; 38), przy złączu DAQ; wokół każdego obszar bez miedzi Ø8 mm.

| Strefa | Zawartość |
|---|---|
| Lewa górna | M1 Waveshare (USB-C na górnej krawędzi), pod nim strefa anteny bez miedzi |
| Góra | J10 LV03 (kotwa opaski przy krawędzi) z polami TP pod padami, J8 CAN, J3 ITEST, J2 ILOG |
| Prawa krawędź | J1 DAQ (kątowe, czołem do P05) między H2 i H5 |
| Środek | U11/U23 obok M1, U21/U22 + U2 przy DAQ, U14, U1 MCP23017, U3 TPS3808, U13 |
| Lewa dolna | J4 SAFE przy lewej krawędzi, U12 z pull-downami |
| Dół | J6 SFAULT, SD1 (karta przy krawędzi), J7 TEMP, J9 PANELCORE, J5 DIR |

Rozmieszczenie powstało w dwóch krokach. Najpierw wyżarzanie (narzędzia robocze `src/tools/place_geom.py`, `place_anneal.py`, `place_rudy.py`; nie wchodzą do łańcucha wydania, wejściem wydania jest `src/placement.json`): koszt = długość minimalnych drzew połączeń wszystkich sieci poza GND, złącza i SD1 trzymane na krawędziach, układy razem z kondensatorem 100 nF, odstęp 3 mm między blokami na ścieżki. Potem ręczne poprawki: R3 i R14 spod anteny do U12, SAFE odsunięte od strefy anteny, pola TP pod padami LV03 o tej samej sieci. Wynik ręcznego rozkładu początkowego: 4,1 m połączeń; po optymalizacji 3,9 m przy zachowanych kanałach.

## Miedź

| Część | Wykonanie |
|---|---|
| 5V_SYS | 1,0 mm F.Cu, zablokowane: J10.1 → M1.J1-21 po lewej stronie pasa opaski; odczep do TP1 |
| Odsprzęganie | przy każdym z 10 układów 100 nF ≤ 4,9 mm od pinu zasilania; odcinek 0,6 mm zablokowany (droga ≤ 5,3 mm); pad GND kondensatora → przelotka 1,0/0,5 mm 2,2 mm dalej |
| Sygnały | Freerouting 2.1, klasa 0,30/0,25 mm; zasilania 3V3_CORE i 3V3_IO klasa 0,6/0,3 mm |
| GND | wylewki na obu warstwach (F.Cu 72,8 %, B.Cu 69,6 % płytki; największa wyspa 88 % / 81 % wylewki), zszyte 48 przelotkami 0,8/0,4 mm w siatce 10 mm (tylko tam, gdzie obie wylewki mają miejsce, poza obrysami części i strefami) |
| Przelotki | 80: 22 z routera, 10 przy kondensatorach, 48 zszywających |
| Strefy bez miedzi | antena M1 (7,1–38,6 × 58,25–72,75 mm), dystanse SD1 (Ø6 mm), pas opaski LV03 (38,4–61,0 × 0,9–6,1 mm), otwory M3 |

Łączna długość ścieżek ok. 4,7 m. Długie odcinki magistrali ADC (M1 → U21/U11 → J1 DAQ) biegną wzdłuż górnej części płytki; v6.1 nie ma rezystorów szeregowych na tych liniach i wymaga odbioru zboczy SCLK/CS/CONVST na P05.

## Oczyszczanie po routerze

`cleanup.py`: usuwa łańcuchy dublujące zablokowaną miedź (Freerouting łączył między sobą przelotki GND przy kondensatorach), odcinki < 5 µm, dublowane odcinki i ślepe końcówki (w pierwszym trasowaniu MOTOR_INA wychodziło 5 mm i wracało), skleja końce rozjechane < 5 µm. Pady GND, przy których DRC zgłasza zagłodzoną termikę, dostają pełne połączenie z wylewką — **23 pady: J4.2, U1.10, U2.3, U11.7, U11.10, U12.1, U12.4, U12.10, U12.13, U13.4, U13.10, U13.13, U14.1, U14.5, U14.12, U21.4, U21.13, U22.4, U22.7, U22.10, U22.13, U23.1, U23.13**; przy lutowaniu dłużej grzać. Freerouting nie jest powtarzalny, więc `run_layout.py` bez `--reuse-ses` ponawia trasowanie, jeśli wylewki nie sięgną któregoś padu GND (tu wystarczyła pierwsza próba); wydanie importuje zapisany `routing/P03.ses`.

## Nadruk

Oznaczenia rezystorów i DIP wewnątrz korpusów, M1 i SD1 wewnątrz obrysów modułów, pozostałe obok części. Nazwy złączy z numerem modułu docelowego (np. „SAFE P04”); przy każdym IDC „KEY n” w linii z pozycją klucza, tuż za obudową. Pola TP: opisy sieci; TP1/TP4/TP3/TP6 leżą dokładnie pod padami 1–4 LV03 z tą samą siecią, więc czytają się też jako pinout wiązki. „USB-C”, „ANTENA: BEZ MIEDZI”, „microSD”, tytuł płytki. Wszystko poza obrysami innych części.

## Czego nie sprawdzono

Przymiarka 1:1 (moduł Waveshare, 4682, gniazdo J1 z wtykiem P05, adaptery), zasięg Wi-Fi, zbocza magistrali ADC, termika, odbiór ODBIOR P03. Sprzęt: NIE ZBADANO.
