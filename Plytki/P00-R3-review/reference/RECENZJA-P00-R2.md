# Recenzja P00-R2 (przyrząd stanowiskowy)

27.09.2026 · Claude. Przedmiot: `Plytki/P00-R2-review` Astry (25.09.2026), pakiet nietknięty. Zakres jak zawsze: poprawność, wykonalność i zgodność z interfejsami, bez oceny zasadności projektu.

## Werdykt

**Brak blokera w PCB.** Miedź, rozmieszczenie i wartości R2 mogą iść do produkcji po przymiarce 1:1. Uwagi R1 (6–15 V, obciążenie minimalne, C6 z ESR, niezależny generator) są zamknięte poprawnie.

Do poprawy jest **dokument wiązki do P04**. Opisuje P04 v6.1, a P04 jest już zamknięte w R2.1 z inną numeracją i innymi warunkami. Poza tym jest kilka drobnych uwag do opisów, nadruku i metody weryfikacji. Wszystko mieści się w rewizji zamykającej bez zmiany miedzi (`Plytki/P00-R3-review`).

## Co sprawdziłem

| Kontrola | Wynik |
|---|---|
| Integralność pakietu | 122/122 plików zgodnych z manifestem, SHA256 ZIP zgodny |
| ERC i netlista (świeży eksport kicad-cli) | 0 naruszeń; 66 części, 145 pinów, 37 sieci — identyczne z `verification/P00.xml` |
| DRC (świeży, wszystkie ważności, zgodność ze schematem) | 0 / 0 / 0 |
| Kontrole PCB / elektryczne / próby ujemne | 24/24, 11/11 + 6/6, 10/10 — odtworzone na kopii |
| Pełna regeneracja z SES (`run_release.py --no-package`) | Odcisk geometrii `ebf7d955…` identyczny z wydaniem; log: `skrypty/rebuild-r2.log` |
| Gerbery i wiercenia | Wygenerowane ponownie z tej PCB: identyczne z `output/fabrication` (raport wierceń różni się tylko datą) |
| Punkty pracy | Własny model z netlist P00 i P04-R2.1: `skrypty/punkty_pracy.py`, wynik `punkty_pracy.json` |
| Oględziny | Schemat (A3) i cztery strony PCB z własnego renderu 300 dpi |

Nie zweryfikowałem liczb LM2937-3.3 z SNVS015F: link Mousera nie odpowiada (limit czasu), a linki TI zwracają 404. Wartości VIN ≥ 4,75 V, IOUT ≥ 5 mA, ESR 0,01–3 Ω i RθJA 77,9 K/W biorę z cytatów Astry. Dane TLC555 sprawdziłem w TI SLFS043K (rev. 01.2026).

## Punkty pracy (niezależnie)

| Wielkość | Wynik | Uwaga |
|---|---|---|
| VIN na U2 przy 6 V na J10, budżet D1 0,6 V | 5,4 V | wymagane ≥ 4,75 V |
| Obciążenie minimalne bez U1 (R5 + LED10) | ≥ 6,57 mA; sam R5 ≥ 5,54 mA | wymagane ≥ 5 mA |
| Obciążenie maksymalne z netlisty | 57,1 mA | wszystkie J1–J8 zwarte, wszystkie LED, J9 zwarty |
| Obciążenie typowe z P04 | ok. 22 mA | kanały H na 10 kΩ, HB pracuje |
| U2 przy TA 40 °C, IG 20 mA, RθJA 77,9 K/W | 15 V: TJ 116 °C maks., 84 °C typ.; 12 V: 98 / 74 °C | < 125 °C także w najgorszym przypadku |
| Kanał H na wejściu 74LVC125A P04 (10 kΩ) | ≥ 2,85 V | VIH 2,0 V |
| KEY/MECH na bramce HC08 (R41/R42 + 10 kΩ) | ≥ 2,61 V | ok. 2,36 V (interpolacja jak w P04-R2.1) |
| H_SUP na SUP_N (100 kΩ) | ≥ 3,11 V | — |
| Heartbeat H na wejściu P04 | typowo 2,45–2,82 V; przy minimalnym VOH z karty 1,87–2,25 V | VIH 2,0 V — uwaga P0-04 |

Minima uwzględniają szynę 3,14 V, rezystory 1 % i 100 ppm/K w 10–40 °C.

## Uwagi

| ID | Waga | Stan w R2 | Propozycja |
|---|---|---|---|
| P0-01 | **ważna** | `docs/P00-P04-WIAZKA.md` opisuje P04 v6.1: J13–J20, H_* z J16.1, trzy odgałęzienia, „MECH_OK ma dwa pulldowny”, STOP J16.1–J16.7, ARM J16.9–J16.10. P04-R2.1 ma J6.1/J5.1/J3.7/J4.3/J2.13/J7.5/J8.3/J8.4/J2.3, H_* z **TP1 P04** (3V3_IO) w pięciu gałęziach, pojedynczy pulldown MECH_OK, STOP J8.1–J8.7, ARM J8.9–J8.10 i styk SAFE_N J7.2–J7.3. `P04-R2.1/docs/P00-P04.md` wprost zastępuje starą numerację, ale pakiet P00 dalej ją zawiera, a README nazywa ją „mapowaniem wejść P04 v6.1”. | Przepisać na P04-R2.1. Tabelę sprawdzać skryptem względem zamrożonej netlisty P04-R2.1: sieć, pulldown, wejście bufora, próg H, a do tego próby ujemne. |
| P0-02 | **ważna** | `ZAKUPY-P00.md` (wiązka) ma trzy odgałęzienia 1 kΩ. Brakuje H_PWM i H_SENSOR (E04, E06, E08), styku testowego SAFE_N (E10) i wybieraka HB (H_HB i J9.1 wzajemnie wykluczone). Nie ma też typów złączy współpracujących — P04 jest już zamknięte. | Pięć gałęzi, wybierak HB, styki ARM/STOP/SAFE_N oraz lista złączy: IDC 16/10/6, Mini-Fit Jr 6/10 i Mini-Fit Jr 4 do zasilania J1. |
| P0-03 | drobna | Bilans cieplny liczony z budżetu 65 mA i IG 20 mA. Kontrola nie wiąże budżetu z netlistą. Plan B „mały radiator TO-220” nie zmieści się: tab U2 jest zwrócony do C5/C7, ok. 1,5 mm od ich obrysu. Opis „blisko granicy” jest zbyt alarmujący. | Kontrola: budżet ≥ maksimum z netlisty (57,1 mA). Planem B jest ograniczenie do 12 V, radiator tylko po przymiarce. Uwaga: przy 15 V i zwarciach J1–J8 kryterium obudowy < 85 °C zależy od rzeczywistego IG (przy 20 mA obudowa ok. 96 °C przy 23 °C, przy 3 mA ok. 77 °C). To kryterium odbioru, nie wada. |
| P0-04 | drobna | LED9 (ok. 1 mA) obciąża wyjście TLC555 przed R3. SLFS043K: VOH min 4,1 V przy 5 V/1 mA i 1,5 V przy 2 V/0,3 mA (typ. 4,8 i 1,9 V). W narożniku minimalnego VOH H na wejściu P04 spada do 1,87–2,25 V wobec VIH 2,0 V. Typowo 2,45–2,82 V. | RL9 bez zmian — rozstrzyga pomiar. W ODBIOR: H na J9 z 10 kΩ ≥ 2,4 V przed podłączeniem P04, a przy niższym wyniku RL9 → 4,7 kΩ albo inny egzemplarz TLC555. |
| P0-05 | drobna | Każda kopia w próbach ujemnych dostaje 9 ostrzeżeń `lib_footprint_issues` (brak biblioteki „P00” w katalogu kopii). Kontrola „Fresh native DRC” oblewa więc wszystkie 10 kopii, także te bez wady miedzi. Wykrycie `dangling_lock` przypisane DRC nie jest dowodem, choć wadę łapie też kontrola zablokowanych segmentów, a w DRC kopii jest `track_dangling`. Brak próby zerowej. QA twierdzi, że każda mutacja oblewa test szczegółowy, „a nie tylko dowolny DRC”. | Kopiować tabele i biblioteki do katalogu kopii. Dodać próbę zerową: kopia bez wady przechodzi 24/24. |
| P0-06 | drobna | `run_layout.py` rozpoznaje zagłodzone termiki po polskim opisie DRC („Pole PTH”, „ na ”). Na angielskim KiCadzie nie zadziała. Dziś bez skutku, bo P00 nie ma zagłodzonych termików. To odwrotny przypadek niż P02-R2. | Rozpoznawać po UUID, jak w P02-R3. |
| P0-07 | drobna | Napis „+VIN 6-15V” stoi 2 mm od pola TP3 (opisanego „VIN”) i dalej od J10. TP3 leży za D1. Czytając płytkę, można uznać TP3 za wejście zasilania. Podłączenie tam omija D1, a odwrotna polaryzacja uszkodzi C4. | „+VIN 6-15V” pod J10, a TP3 opisać „ZA D1”. Kontrola: napis bliżej J10.1 niż TP3. |
| P0-08 | kosmetyka | Docstring `cleanup.py` mówi o VPROT i U5.12 (kopia z P02). Tolerancja R6 nie ma znaczenia, bo okno ESR wynosi 0,01–3 Ω. `ZAMKNIECIE-RECENZJI` R05: „potwierdzić po wydaniu PCB P04” — P04 jest wydane. ODBIOR odsyła do „zatwierdzonej rewizji P04” zamiast E04/E11/E17 z P04-R2.1. | Uzupełnić opisy. R6: dowolny 1 Ω 0207, 1–5 %. |

## Potwierdzone bez uwag

Kierunek przełączników: pin 3 (GND) nad pinem 2 (3V3) na wszystkich dziewięciu, zgodnie z nadrukiem. Droga zasilania J10 → D1 → U2, polaryzacje D1, C4, C6 i LED. R5 bezpośrednio 3V3–GND. C6 wraca wyłącznie przez R6. Każde wyjście Jn.1 idzie tylko przez 1 kΩ. Kondensatory przy pinach U1/U2. Otwory M3 z wolną strefą. Średnice otworów pasują do wyprowadzeń: MKDS 1,3 mm, TO-220 1,4 mm, DO-41 1,1 mm, listwy 1,0 mm, reszta 0,8–0,9 mm. Częstotliwość 102 Hz (92–115 Hz z samych tolerancji R i C) wobec okna watchdoga P04 50–150 ms: dowolny egzemplarz się mieści.

## Czego nie zmieniam

Miedź, rozmieszczenie, strefy i wartości. RL9 zostaje 1 kΩ; rozstrzyga pomiar z instrukcją z P0-04. LED przy ok. 1–1,5 mA. Zasilanie 6–15 V (zalecane 9–12 V). C6 + R6.

## Pliki recenzji

`skrypty/punkty_pracy.py` + `punkty_pracy.json` (model niezależny), `skrypty/nc_inspect.py` (analiza prób ujemnych), `skrypty/rebuild-r2.log` (pełna regeneracja), `work/` (kopia R2 z odtworzonymi kontrolami), `rebuild/` (regeneracja z SES), `fresh/` (świeże ERC/DRC/netlista/Gerbery).
