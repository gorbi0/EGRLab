> Historia poprzedniego wydania. Korekta R17 i aktualny status: ZMIANY-R2.2.md, README.md.

# P04 R2 — zmiany względem R1

26.09.2026 · Claude. Podstawa: R1 Astry (`Plytki/P04-R1-review`, pozostaje bez zmian) i moja recenzja `Plytki/P04-R1-recenzja/RECENZJA-P04-R1.md`. Numery pinów wszystkich ośmiu złączy są te same co w R1. Zmieniły się tylko sieci na J7.1 (`PG_3V3`) i J8.1 (`PANEL_3V3`): nadal jest tam 3,3 V, ale za rezystorem. `verification/interface-scope.json` wymienia obie zmiany jako udokumentowane i odrzuca każdą inną.

## Uwagi recenzji i ich wykonanie

| Uwaga | Wykonanie | Dowód |
|---|---|---|
| R4-01: próg U11 | MCP100-315 → **MCP100-300DI/TO** (2,85–3,00 V). Footprint i wariant D bez zmian. Oszacowany zapas przy 3,18 V DC: +130 mV zamiast −20 mV, przy założeniu histerezy 50 mV TYP; nie jest to gwarancja (korekta R2.1) | PCB: wartość i MPN; ODBIOR E02/E16; ZRODLA |
| R4-02: watchdog tylko przez Q1 | Wolna bramka U7D: **SAFE_WD = SAFE_OK & WD_Q** kasuje U3 (CLR) i bramkuje MOTOR_PERMIT (U5D) oraz SENSOR_PERMIT (U5B). Pola TP14 (SAFE_WD) i TP15 (baza Q1) | Elektryka: symulacja z rozwartym Q1 (zatrzymany heartbeat → HW_ARMED, MOTOR, PWM i SENSOR = L, choć SAFE_N = H); mutacje U3.1/U5.13 → SAFE_OK wykryte; ODBIOR E21 |
| R4-03: 3V3 bez ograniczenia | R38 0 Ω → **1 kΩ** (PG_SEND), **R39 1 kΩ** (J7.1), **R40 100 Ω** (J8.1). Zwarcie w wiązce PG: 3,3 mA na żyłę, w wiązce panelu: 33 mA | Elektryka: 3V3_IO nie ma na żadnym złączu poza J1.3; PCB: sieć od strony złącza ma tylko pin i pad rezystora; ODBIOR E22 |
| R4-04: SAFE_N i R5 | R5 pod U2 (pad 13,9 mm od U2.11; w R1 74 mm od najbliższego węzła). **C18 1 nF C0G** 3,0 mm od U2.11. Miedź SAFE_N: 241 mm (R1: 291 mm) | PCB: koniec SAFE_N przy U2; mutacja „C18 daleko” wykryta |
| R4-05: klucze IDC | Napis **KEY n** przy J3–J6 w linii z pinem klucza, tuż za obudową | PCB: przesunięcie wzdłuż złącza 0–0,4 mm; mutacja wykryta |
| R4-06: zszycie GND | **55** przelotek w siatce 10 mm poza obrysami części oraz **14** w kawałkach wylewki zamkniętych ścieżkami (bez przelotki KiCad by je usunął). Wylewka: F.Cu 76,5 %, B.Cu 73,7 % płytki (R1: 75,7 / 73,9 %, 2 przelotki GND) | PCB: ≥ 40 przelotek, największa wyspa ≥ 75 % (82,9 / 80,3 %); `routing/stitching.json` |
| R4-07: linie panelu | **R41/R42 1 kΩ** szeregowo z TEST_KEY i MECH_OK, pionowo nad J8.3/J8.4 (4,5 mm miedzi od pinu). Pulldowny R23/R24 po stronie bramek, więc przerwany rezystor daje L. Poziom H ok. 2,94 V | Elektryka: styki panelu dochodzą do bramek tylko przez R41/R42; PCB: rezystor przy pinie |

## Czego nie wdrożono

- **100–220 Ω na wyjściach do taśm** (opcja w R4-03). Wyjścia HC08/HC74 nie mają gwarantowanego ograniczenia zwarciowego. Zwarcie może uszkodzić bramkę i zakłócić zasilanie; nie wykonywać prób zwarcia wyjść push-pull. Rezystory na wyjściach są nadal opcją przy integracji, nie warunkiem poprawności obecnej mapy logicznej. P04 kwalifikujemy dla sprawdzonej wiązki i obciążeń logicznych. E22 dotyczy wyłącznie trzech wyjść zasilających zabezpieczonych R38/R39/R40. Próba wyłączenia przez SAFE_N pozostaje dopuszczalna, bo jest to linia z pasywnym pull-upem i kolektorami.
- **10 nF przy R41/R42** (opcja w R4-07). Zakłócenie na TEST_KEY lub MECH_OK może tylko zdjąć zgody i rozbroić ARM, bo to kierunek bezpieczny. O filtrze zdecyduje próba I03 z prawdziwą wiązką panelu. Na płytce nie zarezerwowano miejsca.
- **Okresowa próba watchdoga w firmware** (R4-02). Dotyczy P03, nie P04. Opis jest w PROJEKT i w ODBIOR E21.

## Zmiany płytki poza uwagami

- Rozmieszczenie: grzebień R41, R42 i R4 nad J8.3–J8.5. R4 stoi teraz pionowo nad J8.5 (NC), bo jego miejsce w rzędzie zajął R42. R40 poziomo na lewo, R39 pionowo między J8 i J7, C18 na prawo od U2.11, R5 pod U2. TP8 przesunięty o 4,5 mm w dół, żeby zrobić miejsce na C18. Obrys, otwory i wszystkie złącza bez zmian.
- **Pas „GND ROW J2”**: pod rzędem GND złącza J2 obowiązuje zakaz ścieżek i przelotek, a wylewka jest dozwolona. W próbach Freerouting owijał ścieżkę PWM wokół J2, przez co J2.2 zostawał na odizolowanej wysepce, a pady wiązki muszą zachować termiki. *Sporne:* to nowa reguła layoutu, której nie było w R1 ani w recenzji. Wprowadziłem ją, bo bez niej zgodność z kontrolą Astry („pady GND złączy zachowują termiki”) zależała od losu.
- Pełne połączenie z wylewką dostał jeden pad: U9.1. W R1 były to U8.4, U8.7 i R17.2.
- Nadruk: oznaczenie J8 stoi pod złączem, bo nad nim są rezystory. Znaczniki pinu 1 przy J1/J2 mogą przesunąć się do 1 mm, bo przelotka MCU_ARM stoi w miejscu znacznika J2. Tekst może leżeć na pierścieniu przelotki (przelotki są zakryte maską), ale nie na jej otworze.

## Zmiany w łańcuchu wydania

| Skrypt | Zmiana |
|---|---|
| `complete_routes.py` | `--plan` bierze pary z natywnego DRC (dopasowanie po UUID) i działa w rundach aż do zera niepołączonych. Pad odcięty od wylewki łączy z największą wyspą wylewki. W R1 pary były wpisane na sztywno |
| `cleanup.py` | Przeniesiony z P03 R1. Usuwa po UUID na poziomie pliku, bo `Remove()` psuje obiekty SWIG w procesie. Usuwa duplikaty i ślepe końcówki: w tej płytce 16 zdublowanych i 8 ślepych odcinków po Freeroutingu. Przy luce przywraca plik i kończy kodem 3 |
| `run_layout.py` | Do 6 prób Freeroutinga; kod 3 oznacza lukę trasowania, każdy inny błąd przerywa. Zagłodzone termiki rozpoznaje po UUID (niezależnie od języka KiCad). Pad złącza nie może dostać pełnego połączenia — wtedy nowa próba. SES każdej próby trafia do `routing/attempt-N.ses`. Opcja `--reuse-ses --replan` |
| `stitch.py` | Nowy (z P03), z drugim etapem ratowania zamkniętych kawałków wylewki |
| `silkscreen.py` | KEY n; otwory przelotek jako przeszkoda dla tekstu |
| `make_tables.py` | Zakres interfejsów dopuszcza tylko udokumentowane zmiany J7.1/J8.1. Uwagi w ZAKUPY są przypisane do części, a nie brane z pierwszej części grupy |
| `verify_electrical.py` | +3 kontrole i +4 mutacje: 22/22, 14/14 |
| `verify_pcb.py` | +6 kontroli i +6 mutacji: 26/26, 11/11 |

Trasowanie: SES pochodzi z pierwszej próby ostatniego przebiegu (`routing/attempts.json`). Wcześniejsze przebiegi odrzuciłem podczas strojenia łańcucha i nie są częścią wydania. Dwie ścieżki uzupełniające (R22.2 i R18.2 do wylewki) są w `routing/completion-routes.json`. Freerouting nie jest powtarzalny, więc nowe trasowanie oznacza nową recenzję layoutu.

## Dla płytek sąsiednich

- **P07:** ARM_CLK (J3.5) przy każdym włączeniu P04 ma impuls H trwający ok. 4–13 ms. Zatrzask P07 musi kasować SAFE_N, a nie samo zbocze. EN mostka bramkować jednocześnie przez MOTOR_PERMIT i SAFE_N.
- **P11:** J8.1 ma teraz 100 Ω w szereg. Każdy dodatkowy 1 mA pobierany przez panel (np. LED) obniża PANEL_3V3 o 0,1 V, a SAFE_N w stanie H o ok. 0,09 V. Cel to ≥ 2,7 V.
- **P00:** wymuszenia H_* biorą 3,3 V z TP1, nie z J8.1 (`P00-P04.md`).
- **P03:** pakiet `Plytki/P03-R2-review` (26.09, powstał równolegle) nadal ma R14 = 0 Ω z 3V3_CORE na CORE_LINK. Obiecana w recenzji zmiana na 1 kΩ (na P04 daje 3,0 V przy R16 10 kΩ) jest do zgłoszenia przy recenzji P03 R2. Nowy SUP_N z P03 R2 (bufor OD + 220 Ω, podciąganie 10 kΩ ∥ 10 kΩ modułu) daje na P04 ok. 3,1 V przy R17 100 kΩ — zgodne z wejściem U9B.
