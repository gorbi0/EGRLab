# EGRLab — bieżący etap projektu



Aktualizacja: 30.09.2026. P02 R4: PCB w klasie L scalona (PR #4) i paczka produkcyjna gotowa (`Plytki/P02-PCB-R4-zamowienie`, ZIP aa7b526b…, pod JLCPCB; nie zamówiona). Format S1-3 (P10 na poziomie 4). Schematy S1: P03 R6, P05 R2, P09 R2, P10 R2 scalone, layouty lokalnie. P00 i P04 mają pakiety do zamówienia PCB (`Plytki/Zamowienie-Satland/`), P01 i stare P02 wstrzymane (zasilanie z pakietu 4S). Baza odniesienia: `Rewizje/EGRLab-v6.1-rc1`.

Pakiety płytek i ich recenzje znajdują się w `Plytki/`.




## P02 R4 — PACZKA PRODUKCYJNA (30.09.2026)

Płytka zaakceptowana przez użytkownika, PR #4 scalony (26caff4). Paczka `Plytki/P02-PCB-R4-zamowienie/`: `DO-ZAMOWIENIA_P02-PCB-R4.zip` (SHA-256 aa7b526b…; 7 warstw Gerber X2 z opisem na obu stronach i 2 pliki Excellon), SPECYFIKACJA-DLA-PRODUCENTA.txt z ustawieniami dla JLCPCB (FR-4 1,6 mm, 1 oz, HASL bezołowiowy, przelotki zakryte) i uwagą dla Satlandu. Kontrole: DRC 0/0/0 (14 zgłoszeń lib_footprint_mismatch przyjętych jawnie — nadruk przycięty skryptem), kontrola CAM własnym parserem 20/20 (w tym nowa kontrola obrysu z narożnikami R1 formatu S1), próby ujemne CAM 8/8 + zerowa, oględziny podglądów; 363 PTH (97 przelotek) i 16 NPTH, wiertła 0,4–4,2 mm, ścieżka ≥ 0,3 mm, pierścień ≥ 0,25 mm. Skrypty skopiowane z paczki P04 i dostosowane do S1. Nie zamówiona; przymiarka 1:1 i odbiór sprzętu: NIE ZBADANO. P01-R3.1 i P02-R3 z folderu Satland nie zamawiać.

## P02 R4 — ETAP 2: PCB W KLASIE L (30.09.2026, lokalnie, PR #4)

Pakiet `Plytki/P02-R4-review/` (gałąź `p02-r4-pcb`, PR #4): płytka 160 × 100 mm (klasa L, cały poziom 1), dwie warstwy 35 µm. Rozmieszczenie: blok mocy z pilota przesunięty o 53,5 mm do ściany wejść; blok sterowania rozsunięty ×1,35, a potem na wskazanie użytkownika z wydruku 1:1 jeszcze raz w stronę wolnego pola (górna połowa ×1,25, dolna ×1,12; układy sztywno z odsprzęganiem i rezystorami serwisowymi); grupa podtrzymania 8 mm w lewo razem z wylewkami; R5 obok D11, bo PWR_A z bloku mocy nie miała drogi do J14. Rdzeń mocy bez zmian (decyzja użytkownika: jego miedź jest narysowana wokół części). Zajętość obrysami w pasach 20 mm: 42 / 43 / 41 / 40 / 41 / 23 / 76 / 68 % (wcześniej 49 / 60 / 36 / 24 / 29 / 34 / 76 / 68 %). Trasowanie: Freerouting 2.1.0 domknął się w 1. próbie, planer dokańczania dołożył 7 tras. W skryptach pilota poprawione: planer (warstwa pola SMD), zszywanie GND (siatka na 2/3 płytki, klastry bez połączenia), porządki, wylewki pod końcami blaszek Q9/Q1 (wchodził tam GND), nadruk, kontrole, próby ujemne i PDF liczone dla klasy 2/3. Wynik: DRC 0 niepołączonych / 0 niezgodności / 0 innych naruszeń, jedyne zgłoszenia to niezgodności footprintów z biblioteką u części z przyciętym nadrukiem (przyjęte jawnie); kontrole PCB 23/23; próby ujemne 12/12; tor 5 A ≥ 4,1 mm miedzi. Otwarte: przymiarka 1:1, 9 oznaczeń ukrytych z braku miejsca, pełne połączenie GND na wyprowadzeniu D3 (P600 — mocniejsza lutownica). Scalone 30.09 (PR #4); paczka produkcyjna — sekcja wyżej.

## FORMAT S1-3 — P02 R4 W KLASIE L, P10 NA POZIOMIE 4 (29.09.2026)

Decyzja użytkownika („opcja 1”): P02 R4 w klasie L (160 × 100 mm, cały poziom 1), bo w klasie 2/3 trasowanie się nie domykało (15 niepołączeń w obu metodach). Skutek zapisany jako specyfikacja S1-3 (`Plytki/Format-S1/SPECYFIKACJA-FORMATU-S1.md` §7, `format-s1.json`): P10 na poziomie 4, slot S3 — J3 (OBD) wychodzi ścianą wejść razem z pozostałymi przewodami z auta; od spodu bez SOIC, elementy od góry ≤ 16,5 mm. P10 R2 zakładał slot S1 poziomu 1 — do sprawdzenia przed layoutem. Wariant pełny: na poziomie 4 zostaje tylko S2, więc P04 (2/3) potrzebuje szóstego poziomu (albo P10) — do decyzji przy wariancie pełnym. Wysokość stosu LOGGER bez zmian.

## P03 R6 — SCHEMAT CORE W FORMACIE S1 (PR #6, scalony 29.09.2026)

Pakiet `Plytki/P03-R6-review/` (sesja w chmurze, bez PCB): obwód P03-R5 w klasie L na poziomie 2; złącza J_BP1–J_BP3 (IDC 2×10 kątowe, po jednym na slot), trzy listwy serwisowe, wejście PFAIL_N z P02 R4 (J_BP2.18 → R42 1 kΩ → GPIO3, podciągnięcie R43 do 3V3_CORE). ERC 0 (6 arkuszy), 511 pinów, kontrole J_BP / PFAIL_N / listew 12/12, próby ujemne 22/22 z zerową. Do zrobienia przy layoucie (lokalnie), z uwag do PR: R43 10 kΩ → 100 kΩ, J_BP2.17 GND → 5V_SYS, dodatkowe części jako SMD, krótka droga SUP_N przez P12.

## P09 R2 / P10 R2 — SCHEMATY W FORMACIE S1 (PR #5, scalony 29.09.2026)

Pakiety `Plytki/P09-R2-review/` i `Plytki/P10-R2-review/` (sesja w chmurze, bez PCB). P09 R2: J_BP IDC 2×8, listwa serwisowa 1×13, posiadane rezystory THT na stojąco; kontrole 52/52, próby ujemne 35/35. P10 R2: J_BP IDC 2×5, listwa serwisowa 1×9; kontrole 32/32, próby ujemne 36/36. P10 przechodzi w S1-3 na poziom 4, slot S3 (wyżej): przed layoutem układy SOIC na górę, J3 przy ścianie wejść. **P09 R2 — PCB (30.09 wieczorem, komputer 24/7, gałąź `p09-r2-pcb`):** DRC 0 niepołączonych / 0 niezgodności / 0 innych naruszeń (2 przyjęte `lib_footprint_mismatch` J1/J2), kontrole PCB 22/22, próby ujemne 16/16; moduły terminalami do ściany wejść. Sporne: wysokość gniazda z modułem (szacunek = limit 16,5 mm), pin 1 listwy J2 od większego x (dokumenty poprawione), 4 pola z pełnym połączeniem z wylewką; szczegóły w README pakietu, sekcja „PCB”.

## REPOZYTORIUM GIT I SESJE W CHMURZE (29.09.2026)

Katalog jest repozytorium git: **github.com/gorbi0/EGRLab** (prywatne), gałąź main, pierwszy commit 45dce9c; aplikacja Claude GitHub ma dostęp do repozytorium. Zasady pracy w chmurze i zadanie pierwszej sesji: `docs/CHMURA.md`; kopia pamięci Claude: `docs/pamiec-claude/`. Pliki bajt w bajt (`* -text`), archiwa zip recenzji poza repozytorium, 15 arkuszy `AUX`/`CON` (nazwy zarezerwowane w Windows) jako skip-worktree — nowych tak nie nazywać. P02 R4: praca przerwana przed schematem; poprawka architektury (dwa SUP53P06 przeciwsobnie, tor sterowania z P01 R3) i nowe UVLO 13,53/12,51 V w `Plytki/P02-R4-specyfikacja/STAN-PRAC.md`. Środowisko chmury sprawdzone 29.09 (gałąź `chmura-srodowisko`): KiCad 10.0.6 z obrazu Docker (PPA i mirrory Debiana zablokowane), kontrole P02-R3 i P04-PCB-R2.2 odtworzone z wynikami jak w repozytorium; opis i różnice Windows/Linux w `docs/CHMURA.md`.

## P05 R2 — SCHEMAT (PR #3, 29.09.2026)

P05 R2, etap schematu (PR #3, scalony 29.09): R5 6,04 kΩ, R7 5,11 kΩ, R13 47 kΩ, CH7 = VBAT_SENSE, arkusze AUX_IN/ZLACZA, ODBIOR i INTEGRACJA według recenzji; ERC 0, 421/421, 23/23, 12/12. U2 w klasie wysokiej — decyzja użytkownika: REF5025ID (Mouser 595-REF5025ID, 35,82 zł; REF5025AIDR z listy 2 to klasa standardowa 0,1 % i daje dolny narożnik okna DAQ_OK 4,7477 V < 4,75 V — mój błąd na liście). Layout P05 w S1 osobnym zadaniem; wzór odsprzęgania U1 w `Plytki/P05-R2-review/wip-layout-obrys-R1/`. Lista zakupowa 2 poprawiona o REF5025ID i oznaczona „do przeliczenia” po decyzjach z 29.09. **1.10.2026:** decyzja użytkownika — dwa złącza J_BP (J_BP2 2×10 z magistralą DAQ w slocie S2, na tych samych pinach co P03 R6; J_BP1 2×5 z 5V_SYS ×2, DAQ_OK i VBAT_SENSE w slocie S1); schemat w S1 (R3) robi sesja w chmurze: `Plytki/Format-S1/zadania/ZADANIE-P05-S1.md`, gałąź `p05-s1`, polecenie w `docs/CHMURA.md`.

## FORMAT S1 — PRZYJĘTY (29.09.2026)

Studium formatu S1 (`Plytki/Format-S1/STUDIUM-FORMATU-S1.md`, przyjęte przez użytkownika 29.09 (specyfikacja `Plytki/Format-S1/SPECYFIKACJA-FORMATU-S1.md`; posiadane rezystory THT na stojąco, nowe SMD 1206; wszystkie płytki z JLCPCB)): stos poziomych płytek w formacie ok. 160 × 100 mm z tercjami (L, 2/3, 1/3), płytka połączeń zamiast wiązek na jednej długiej krawędzi, listwy serwisowe z kołkami do odbioru na drugiej (wymaganie użytkownika), panel na krótkiej. Szacunek: LOGGER ok. 231 × 133 × 105 mm (3,2 l zamiast 11,4 l), pełny ok. 231 × 133 × 127 mm (3,9 l zamiast 14,5 l). Części zajmują dziś 21–53 % powierzchni płytek. P02 R4 w obecnej technice potrzebuje ok. 155 cm² wobec celu 98 cm², więc etap 2 (PCB) wstrzymany do decyzji o formacie; do wstrzymania także layout P05 R2 i zamówienie PCB P04.

## P02 R4 — RECENZJA ETAPU 1 I DECYZJE (29.09.2026)

PR #2 scalony (merge 4ac375d). Recenzja: `Plytki/P02-R4-recenzja/RECENZJA-P02-R4-ETAP1.md`. Decyzje użytkownika: D3 5KP24A (Z-01), C_H 2200 µF bez zmian (Z-08: ≥ 10 ms w najgorszym narożniku, jest 11,1 ms), UVLO bez zmian (Z-02/O-02: obwiednia 12,90–14,08 / 11,98–13,11 V). Bezpiecznik przy klemie 1 A. Na panelu (P11) włącznik PWR ze złoconymi stykami (ok. 0,3 mA w dzielniku UVLO). Etap 2 (PCB): `Plytki/P02-R4-specyfikacja/ZADANIE-P02-R4-ETAP2.md`. Równolegle P05 R2 (`Plytki/P05-R2-specyfikacja/ZADANIE-P05-R2.md`, gałąź `p05-r2`). SW1 P05 → E-Switch 100DP1T1B1M2REH (Mouser 612-100-F1122, 17,07 zł, złocone styki, nóżki do druku, korpus jak C&K 7201; rozstaw nóżek do potwierdzenia przy recenzji P05 R2).

## P02 R4 — ETAP 1: SCHEMAT (29.09.2026, sesja w chmurze, gałąź p02-r4-schemat)

Pakiet `Plytki/P02-R4-review/` (bez PCB): 4 arkusze A3 (WEJ, STER, LV, MON), 131 części, ERC 0, netlista 317/317 pinów, kontrole elektryczne 35/35, próby ujemne 19/19 z zerową. Q9 (Q_REV) i Q1 (Q_SW) przeciwsobnie, tor bramki z P01 R3 z R23 = 22 kΩ; UVLO nominalnie 13,50/12,55 V, obwiednia załączenia 12,90–14,08 V, wyłączenia 11,98–13,11 V. Wyłączanie Q1 z R23 22 kΩ trwa 44–71 µs nominalnie i do ok. 240 µs w narożniku (model skalibrowany na ngspice P01 R3). Narastanie VSW 11,5 V/ms, 2,53 A przy 220 µF. Do decyzji: Z-08 w najgorszym narożniku 11,1/22,3 ms (6/3 W) zamiast 14/28 ms (albo C_H 3300 µF); rozrzut UVLO większy niż ±0,34 V (Z-02); Z-01 25 V sprzeczne z 5KP18A. Odstępstwo od dosłownego D-06: PFAIL_N z U2A buforującej OK (bez rozjazdu z ENABLE). P04_3V3 (J13.1) celowo oddzielone od lokalnego 3V3_IO. Następny krok: lokalna recenzja schematu, potem PCB (etap 2).

## P02 R4 — SPECYFIKACJA ZASILANIA Z PAKIETU 4S (29.09.2026)

Pakiet `Plytki/P02-R4-specyfikacja/` (SPECYFIKACJA-P02-R4.md, interfejsy.csv, src/obliczenia.py). Zastępuje P01 i HOLD P02 R3. Q1 SUP53P06 z UVLO 13,47/12,47 V (TL431 + LM2903, Rt 43,2k, Rb 10,0k, Rh 536k), włącznik PWR na panelu, VSW ≤ 220 µF (limit P01), C_H 2200 µF ładowany przez 22 Ω + diodę i oddawany przez D1b (po PFAIL_N ≥ 14 ms przy 6 W, ≥ 28 ms przy 3 W), TSR 2-2450/2-2433 i PSU_OK jak R3, złącze PG (SAFE_N, PG_SEND/PG_LINK) przeniesione z P01 — P04 bez zmian, CH7 P05 = VBAT auta (propozycja: OBD pin 16), PFAIL_N do P03 (nowe wejście w następnej rewizji P03). Moduły przetwornic z Allegro odrzucone dla szyn pomiarowych (TSR kupione, mniejsze, ze specyfikacją tętnień). Czeka na akceptację decyzji D-01…D-07; potem schemat.

## DECYZJE 29.09.2026 — ZASILANIE Z OGNIW 18650, ZAMIENNIKI

Przyrząd zasilany z pakietu Li-ion 18650 (rekomendacja 4S: 12,0–16,8 V, ok. 50 Wh), ogniwa ładowane poza autem, koszyk na zewnątrz obudowy; akumulator auta zostaje tylko jako sygnał mierzony VBAT. P01 PROTECT i HOLD w P02 zbędne — do zaprojektowania nowa płytka zasilania: bezpiecznik, BMS 4S, P-MOSFET (SUP53P06 z zakupów P01) z UVLO i PG zamiast diody D2, TSR 5 V/3,3 V, rozdział LV, VMOTOR z bezpiecznikiem, złącze PG do P04 bez zmian (PG_SEND, PG_LINK, SAFE_N). Radiatory i blachy niepotrzebne (MOSFET ok. 0,3 W przy 3,5 A). Transil 1.5KE18A (VWM 15,3 V) nie pasuje do 4S.
**Zamówienie PCB P01 i P02 wstrzymane**; P00 i P04 bez zmian. Zamienniki przyjęte: EAO → zwykłe przyciski, PBV → bocznik 2512 Kelvin (zmiana PCB P06), C&K 7201 i NKK S6A → zwykłe przełączniki (P05 SW1 — zmiana footprintu), DEUTSCH tylko przy adapterach (panel: tańsze złącze z kluczem), przewody i dystanse lokalnie. Lista zakupowa 2 do przeliczenia. NIC JESZCZE NIE ZMIENIONO W CAD.

## KASETA R1 — KONCEPCJA OBUDOWY (29.09.2026)

Pakiet `Plytki/Kaseta-R1/` (KASETA-R1.pdf: widoki 1:2 obu wariantów, tabela wiązek, widoki z góry 1:1 do przymiarki w aucie; skala 1:1 sprawdzona na rastrze). Płytki pionowo na prętach M3 przez wspólne otwory 150 × 110 mm (P01–P05), dwie kolumny za P03 i za P05, małe płytki na płytach nośnych, panel z przodu, P11 za panelem przed P05.
LOGGER (P01 z SK129 25,4, P02, P03, P05, P06, P09, P10, P11): wnętrze 355 × 203 × 145 mm, ze ściankami 361 × 209 × 151 mm (11,4 l). PEŁNY (+ P04, P07, P08; SK129 63,5): 355 × 259 × 145, ze ściankami 361 × 265 × 151 mm (14,5 l). Szacunek z 28.09 (7,3 / 11,2 l) był zaniżony — bez strefy panelu, kanałów wiązek i płyt nośnych.
Długości wiązek v6.1 są pod płaski nośnik: w kasecie mieści się 5 z 20 (LOGGER) i 6 z 36 (PEŁNY). Do decyzji: J7 (TAPS) na P11 przed J4 P05 (P11-R2), ogonki DT i VSENSE (tor analogowy), SAFE ok. 180 mm (przeliczyć zbocze), SPI ILOG/TEMP/ITEST. Obudowa do kabiny (płytki 0–50 °C). NIE ZBADANO: makieta, przymiarka w aucie, termika.

## PCB P00 / P01 / P02 / P04 — ZAMÓWIENIE W SATLAND (28.09.2026)

Folder do wysyłki: `Plytki/Zamowienie-Satland/` — cztery ZIP-y (P00-R3, P01-R3.1, P02-R3, P04-R2.2), specyfikacje PL, `INSTRUKCJA-SATLAND.md` (z sekcją ustawień JLCPCB, wszystko 1 oz), `MAIL-DO-SATLAND.txt`.
Nowe paczki `Plytki/P00-PCB-R3-zamowienie` i `P02-PCB-R3-zamowienie` (wzór P01): DRC 0/0/0 z wypełnieniem stref i zgodnością schematu, kontrola CAM własnym parserem 20/20, próby ujemne 7/7 + zerowa, oględziny podglądów. P01 bez zmian (paczka z 27.09).
P00 i P02: opis tylko na górze (dolny w projekcie pusty). **Miedź 35 µm na wszystkich trzech** — P01/P02 zmienione z 70 µm decyzją użytkownika (koszt ok. 4×; przy 5 A odcinki 2 mm P01 +17 °C zamiast +5 °C); warunek: próba nagrzewania 0,1/1/3,5/5 A przed pierwszym uruchomieniem P07. Laminat w Satlandzie 1,5 mm. Fabrykapcb.pl odrzucona (pierścienie ≥ 0,4 mm, odstępy ≥ 0,3 mm, dłuższy termin z maską i metalizacją).
P04: paczka `Plytki/P04-PCB-R2.2-zamowienie` (ZIP 1f7e9b84…), płytka bajtowo = P04-R2.2 (miedź = R2.1): DRC 0/0/0, CAM 20/20, próby ujemne 8/8 + zerowa; 450 PTH, w tym 101 przelotek 0,8/0,4 mm z pierścieniem 0,20 mm (minimum Satlandu — pytanie w mailu), 12 NPTH, ścieżka min. 0,3 mm, opis tylko na górze, 35 µm. Poprawki skryptów przy P04: `.kicad_prl` tworzony przez kicad-cli jest usuwany, otwory na połówce mikrometra parowane z tolerancją 0,001 mm (nowa próba ujemna 5 µm), pierścień liczony z geometrii.
NIE ZBADANO: przymiarka 1:1 części, próby elektryczne i cieplne.

## ZAKUPY 2 — LISTA DLA P00, P02–P06, P08–P11 (28.09.2026)

Lista: `Plytki/Zakupy-2/ZAKUPY-2.md` (+ `TME-wklej.txt`, `TME-przewody-wklej.txt`, `FARNELL-wklej.txt`, `MOUSER-wklej.txt`, `zakupy-2.csv`, generator w `src/`).
Netto po zamówieniach z 24.09; P03-R5, P04-R2.2, P05 z wartościami z recenzji. NIE ZAMÓWIONE.
TME ok. 855 zł netto (106 pozycji), Kamami ok. 42 zł brutto, Farnell 247 zł (9), Mouser 344 zł (20); wszystko na stanie 28.09.
Zamiany 1:1 bez zmiany PCB (do wpisania w kolejne rewizje): P05 U2 ADR4525BRZ → REF5025AIDR, P03 U4 SN74LVC1G37DBVR → DBVRQ1, P06 R3/R4 5k1 → 5k11 0,1 %, P11 J7 39-29-9129 → 39-29-6128. Do decyzji: bocznik PBV (tylko DigiKey 163 zł), przyciski EAO (panel, poza PCB).
Korekta ZAKUPY-P00 (R3): wiązka stanowiskowa do P04 potrzebuje męskiego IDC16 i męskiego Mini-Fit 4p (J2/J1).

## P01 — PAKIET DO ZAMÓWIENIA PCB (27.09.2026)

Aktualny eksport produkcyjny: `Plytki/P01-PCB-R3.1-zamowienie`.
**Do producenta:** `Plytki/P01-PCB-R3.1-zamowienie/DO-ZAMOWIENIA_P01-PCB-R3.1.zip`.
Parametry i instrukcja: `INSTRUKCJA-ZAMOWIENIA.md` w tym samym katalogu.
PCB 160 × 120 mm, 2 warstwy, FR4 1,6 mm, Cu 70 µm/2 oz NA KAŻDEJ STRONIE,
HASL bezołowiowy, maska zielona i biały nadruk na obu stronach, test elektryczny.

Wydanie na podstawie P01-PCB-R3.1-review; źródła i geometria niezmienione.
Świeży DRC 0/0/0, 31/31 kontroli, 5/5 celowych usterek wykrytych, 28/28 kontroli
CAM. Sprawdzono 202 otwory PTH i 8 NPTH oraz 199 pól THT na każdej warstwie;
obejrzano rzeczywiste eksporty. ZIP zawiera tylko 7 Gerberów i 2 pliki Excellon.
SHA-256 ZIP: `abca5949b1b4c9ba828e2db8908b6113154fcc55073037c41cc0b58e6469e094`.

Status dotyczy plików do wykonania prototypu. Przymiarka rzeczywistych części,
próby elektryczne i termiczne nadal NIE ZBADANO. Eksport wykonano na bieżące
zlecenie użytkownika; nie uznano wcześniejszego warunku przymiarki za zaliczony.
Przy montażu C6 dopiero po dokręceniu Q1/HS2. Zachować BOM A1 i procedury R3.1.
Poprzedni pakiet review pozostaje materiałem źródłowym. P07 nadal HOLD.

## P07 DRIVE — WSTRZYMANE



Decyzja użytkownika: zamiast Pololu 1451 rozważamy moduł z dwoma BTS7960B. Powrót do projektu P07 dopiero po otrzymaniu płytki i sprawdzeniu jej rzeczywistego wykonania. Nie zatwierdzać layoutu, nie zamawiać PCB P07 i nie kupować Pololu z dotychczasowego BOM bez ponownego rozstrzygnięcia wariantu.



Przed wznowieniem: oznaczenia układów, połączenia bufora 74HC244 i jego zasilanie, poziomy sterujące, R_EN/L_EN, sposób odczytu R_IS/L_IS, stany rozruchu/STOP, hamowanie i przebieg PWM, mechanika modułu. Zachować własny bocznik/INA240/MCP3201, lokalne OC, zatrzask i KPWR. Zmiana obejmie P07 i jego obsługę; nie stanowi zatwierdzonej zamiany pin za pin. W trybie LOGGER mostek testera nadal nie jest połączony z ECU.



## P01 PROTECT — HISTORIA PRZEGLĄDU I PRZYMIARKI R3/R3.1



Aktualny layout: `Plytki/P01-PCB-R3-review`, archiwum `Plytki/P01-PCB-R3-review.zip`

(+ `.sha256`). PCB-R3 przygotował Codex na bazie PCB-R2 Opusa i recenzji

`Plytki/P01-PCB-R2-recenzja-Codex`. Poprzednie pakiety pozostają bez zmian.



160 x 120 mm, 2L, FR4 1,6 mm, miedź 70 um/stronę. D4 przeniesiona przy Q1,

C6 odsunięty o 2,1 mm; szyna VS B.Cu omija pad GATE C6. TP1/TP2 sondować od

spodu; drogi do Q1 po 4,62 mm. Zachowano bloki funkcjonalne R2, izolację radiatorów,

oznaczenia TO-220, interfejsy, Kelvin LK1 i termiki J7. Modele gabarytowe lokalne.



Montaż A1: `docs/BOM-MONTAZOWY-A1.csv` - rzeczywiście zamówione części,

z R8=221 kΩ i rezystorami PR02 5%. Nominalny schemat nadal P01-R3:

`Plytki/P01-R3-review`. PDF do przymiarki: `output/pdf/P01-PCB-R3-dokumentacja.pdf`.



Świeży DRC 0/0/0, 30 kontroli PCB PASS, 5 celowych usterek wykrytych.

Odbiór jednym poleceniem wiąże wynik z PCB, schematem, regułami i skryptami.

Nie korzysta z nieaktualnego raportu DRC. Wynik w `verification/release-status.json`.



Recenzja PCB-R3 (Claude): `Plytki/P01-PCB-R3-recenzja/` — przyjęta; DRC 0/0/0, 30/30 kontroli

i 5/5 prób odtworzone niezależnie. **Poprawki zastosowane w wydaniu R3.1:**

`Plytki/P01-PCB-R3.1-review` (+ `.zip`, `.sha256`), płytka identyczna z R3 (miedź, nadruk,

wiercenia). Zmieniona kolejność montażu (C6 po dokręceniu Q1 — zasłania łeb śruby od przodu),

BOM A1 (U4 z TME, zachowane uwagi o wyprowadzeniach i polaryzacji z BOM R3), 31/31 kontroli.

**Do przymiarki i montażu używać R3.1** (`output/pdf/P01-PCB-R3.1-dokumentacja.pdf`, `docs/BOM-MONTAZOWY-A1.csv`).



**Następny krok: wydruk 100% i przymiarka rzeczywistych części** według

`docs/MECHANIKA.md` PCB-R3. Gerber/Excellon po przymiarce. Wcześniejszy layout

R2 i jego recenzja pozostają odniesieniem; nie zlecać PCB z katalogów testowych.

Przymiarka, SOA, termika i pomiary sprzętu nadal NIE ZBADANO.



Po PCB i montażu obowiązuje ODBIOR/METROLOGIA R3: najpierw sama P01. P01 odcina

moc; rezerwa LOGGER-a ma powstać na P02-HOLD. Bank HOLD nie trafia bezpośrednio

na VPROT. SAFE_N nie potwierdza ustalonego VPROT; przed KPWR wymagane stabilne

VPROT przez≥300ms, także przy CORE z USB. Szczegóły pozostają w R3/integration/P02-HOLD.



P07 nadal HOLD do kontroli rzeczywistego BTS7960. Nie kupować Pololu z dawnego

BOM ani nie zatwierdzać P07 jako automatycznego zamiennika.



## P02 PSU + HOLD — R3, PROJEKT ZAMKNIĘTY (26.09.2026)

Aktualny pakiet: `Plytki/P02-R3-review` (+ `.zip`, `.zip.sha256`). Recenzja R2 Astry (Claude):

`Plytki/P02-R2-recenzja/RECENZJA-P02-R2.md` — R2 przyjęte, zmiany R-01…R-04 poprawne, progi

odtworzone niezależnie co do mV. R3 = ostatnia iteracja (decyzja użytkownika); miedź, rozmieszczenie

i strefy identyczne z R2 (kontrola R2→R3). Wkładki Schurter SPT 5×20, 300 VDC: F1 T2A, F2/F3 T1A

(zwłoczne, jak zaleca TRACO dla TSR2), F4 T0,5A. R16 470 Ω (LED 2–3 mA). `--rebuild` odtwarza

płytkę (SES w pakiecie, zagłodzone termiki po UUID — R2 zależało od języka KiCada). Opisane: praca

przy zgaszonym silniku (VPROT_OK ~12,25 V, kwalifikacja ręczna TP1/TP3), przerwany F1 wykrywany po 1–2 min.

ERC 0, 208/208, DRC 0/0/0, PCB 29/29, elektryczne 11/11, zakres R2→R3 8/8; mutacje 10/10 i 8/8;

9 stron PDF obejrzanych. Otwarte: przymiarka 1:1, zakup (0001.2501 poza TME, Mini-Fit 4p TME 0 szt.),

I²t F1:F2 z karty PDF Schurtera, odbiór ODBIOR.md. Gerbery po przymiarce. Mapa: `docs/ZMIANY-R3.md`.



## P02 R2 — HISTORIA / BAZA DLA R3 (25.09.2026)



Aktualny pakiet: `Plytki/P02-R2-review`, archiwum `Plytki/P02-R2-review.zip`

(+ `.zip.sha256`). R2 przygotował Codex na bazie R1 Opusa i recenzji Codexa.

Oryginalny R1 zachowany; zgodność 156 plików potwierdzona hashami.



Poprawiono progi HOLD_READY z analizą tolerancji, oddzielono filtry od dodatniego

sprzężenia przez R18/R19, zabezpieczono TP3 rezystorem R20 1 kΩ/2 W. Schemat

podzielono na cztery arkusze A3. BOM, modele gabarytowe, formularz odbioru i mapę

zmian zaktualizowano. Od recenzji zacząć od `docs/ODPOWIEDZ-NA-RECENZJE.md`.



ERC 0, netlista 208/208, DRC 0/0/0, 29/29 kontroli PCB, 8/8 elektrycznych,

4/4 kontroli zakresu zmian; wykryto 10/10 mutacji PCB i 5/5 elektrycznych.

Wszystkie 4+5 stron PDF obejrzane. Wyniki i hashe: `verification/QA.md`.



Nadal OTWARTE: MPN wkładek F2/F3/F4 z parametrami DC, przymiarka części,

pomiary na sprzęcie. F1 wybrany: Schurter 0001.2507. Brak Gerberów.

HOLD_READY lokalnie; 15 s kwalifikuje operator. P03/P04 bez zmian; P07 nadal HOLD.



## P02 R1 - HISTORIA / BAZA DLA R2 (25.09.2026)



Pakiet: `Plytki/P02-R1-review` (+ `.zip`), schemat i layout Claude, recenzja: Astra.

Decyzje użytkownika 25.09: bank HOLD (3 × 22 mF / 35 V) na płytce P02; HOLD_READY

tylko lokalnie (komparator, LED, pole pomiarowe, zarezerwowany pin 3 w PSUOK),

P03/P04 bez zmian. R_CHARGE 47 Ω / 25 W poza płytką (J13), D_OR z osobnymi anodami,

F2/F3 zasilane z VLOG_RES. VMOTOR: GMSTBA 7,62 zamiast PC 4 (do decyzji w recenzji).



160 × 120 mm, 2 × 70 µm, M3 jak P01. ERC 0, netlista 200/200, DRC 0/0/0,

28/28 kontroli PCB, 8/8 prób ujemnych. Opis: `README.md`, `docs/LAYOUT.md`,

`docs/MECHANIKA.md`; stan części: `docs/ZAKUPY-P02.md`. Sprzęt: NIE ZBADANO.

Nie zamawiać PCB P02 przed recenzją i przymiarką (bank 45 mm, oprawki, złącza).



## P00 FIXTURE — R3, PLIKI GOTOWE DO ZAMKNIĘCIA (27.09.2026)

Aktualny pakiet: `Plytki/P00-R3-review` (+ `.zip`, `.zip.sha256` 97783cea…). Recenzja R2 Astry (Claude):

`Plytki/P00-R2-recenzja/RECENZJA-P00-R2.md` — bez blokera PCB; R01–R05 z R1 zamknięte poprawnie.

Główna uwaga: mapa wiązki w R2 opisywała P04 v6.1 (J13–J20, H_* z J16.1, trzy gałęzie) — w R3

przepisana na P04-R2.1 i sprawdzana `check_harness.py` na zamrożonej netliście P04 (10/10, 12/12 mutacji).

Miedź, rozmieszczenie, wartości i MPN identyczne z R2 (kontrola R2→R3 10/10; Gerbery: tylko F.Silkscreen).

Nadruk: „+VIN 6-15V” pod J10, TP3 „ZA D1” (w R2 napis +VIN stał 2 mm od TP3 za diodą). Nowe kontrole:

budżet 65 mA ≥ maksimum z netlisty 57,1 mA, poziom H heartbeat (typowo ≥2,45 V; narożnik min. VOH

TLC555 1,87 V wobec VIH 2,0 V — rozstrzyga pomiar na J9, środek zaradczy RL9 4,7 kΩ), próby ujemne

z próbą zerową (w R2 DRC każdej kopii oblewał przez brak biblioteki). Plan B temperatury: 12 V

(radiator koliduje z C5/C7). ERC 0, 145/145, DRC 0/0/0, PCB 25/25, elektr. 14/14, próby 11/11 + zerowa,

9/9, 12/12; czysta regeneracja PASS. Otwarte: przymiarka 1:1, zakup (zapasy z P01: EEUFR1H220,

L-934GD, 1 Ω 0207), odbiór `docs/ODBIOR-P00-R2.md`. Mapa zmian: `docs/ZMIANY-R3.md`.



## P00 R2 — HISTORIA / BAZA DLA R3 (25.09.2026)



Aktualny pakiet: `Plytki/P00-R2-review`, archiwum `Plytki/P00-R2-review.zip`

(+ `.zip.sha256`). R2 przygotował Codex po niezależnej recenzji R1.

Oryginał R1 pozostaje niezmieniony; potwierdzenie hashów w pakiecie R2.



Wejście 6-15 V (zalecane 9-12 V), R5 560 Ω jako stałe obciążenie regulatora,

C6 EEUFR1H220 22 µF / 50 V z R6 1 Ω w jego powrocie. Poprawione BOM i etykiety.

Generator jest samodzielny: lokalne wejściowe footprinty, bez zależności od P02.

Dodano mapę wiązki do P04 v6.1 oraz procedurę uruchomienia i odbioru.

Recenzję zacząć od `docs/ZAMKNIECIE-RECENZJI.md`.



ERC 0, netlista 145/145, DRC 0/0/0, 24/24 kontroli PCB, 11/11 elektrycznych;

wykryto 10/10 mutacji PCB i 6/6 elektrycznych. Pełna regeneracja w czystym katalogu

zakończona zgodną geometrią i netlistą. Obejrzano 1+4 strony PDF.

Gerbery i wiercenia są w pakiecie do kontroli przed zamówieniem.

Status: DO RECENZJI. Przymiarka, stabilność, temperatura i testy P04: NIEWYKONANE.



## P00 R1 - HISTORIA / BAZA DLA R2 (25.09.2026)



Pakiet: `Plytki/P00-R1-review` (+ `.zip`), schemat i layout Claude, recenzja: Astra.

Przyrząd stanowiskowy (nie do auta): 8 źródeł 3,3 V/GND przez 1 kΩ + heartbeat TLC555 ok. 102 Hz.

Decyzje użytkownika 25.09: wyjścia na listwach 2,54 mm (Dupont), zasilanie 5–15 V z LM2937 3,3 V

(+ D1 przed odwrotną polaryzacją), LED stanu przy każdym kanale. Dodatek R1: SW9 RUN/STOP heartbeatu.

Przełączniki Würth WS-SLTV: wspólny styk na środkowym pinie, „opposite side connection” — symbol

przenumerowany, kierunek potwierdzić omomierzem przed montażem. 115 × 70 mm, 2 × 35 µm.

ERC 0, netlista 141/141, DRC 0/0/0, 22/22 kontroli, 8/8 prób ujemnych. Sprzęt: NIE ZBADANO.





## P03-R5 / P04-R2.2 — POPRAWKI RESETU (28.09.2026)

Aktualne pakiety: `Plytki/P03-R5-review` i `Plytki/P04-R2.2-review`, każdy także jako ZIP z SHA-256.
P03: U4 SN74LVC1G37DBVR (Schmitt + open-drain) zamiast SN74LVC1G07; U6/R41 pozostają.
P04: R17 100 kΩ → 10 kΩ / 1%; R30 nadal 100 kΩ. Interfejsy i routing zachowane.
Nowe schematy, BOM/zakupy, PDF montażowe i obliczenia: `docs/ZMIANY-R5.md`,
`docs/ZMIANY-R2.2.md`, wspólny `docs/KONTRAKT-RESET.md`; świeże wyniki w `verification/QA.md`.

Obie płytki: ERC/DRC 0/0/0, kontrola dozwolonego zakresu zmian i odtworzenie CAD
w pustym katalogu PASS. P03: 30/30 PCB, 53/53 funkcje, 44 mutacje funkcji oraz 18 PCB + próba zerowa;
P04: 26/26 PCB, 22/22 logika, 11/11 wartości. Budżet resetu w obu: 7/7 i 4/4 mutacje.
Poprawiono generator P03, aby ponowny eksport schematu zachowywał reguły PCB.
Oryginały P03-R4 (170 kontrolowanych plików) i P04-R2.1 (143) bez zmian.

**Do recenzji i przymiarki, bez CAM do produkcji.** B2B P03–P05 nadal otwarte:
`Plytki/P03-R5-review/docs/B2B-STATUS.md`. Pomiary zboczy na P04, resetu przy zaniku
zasilania i przymiarka części NIE ZBADANO. P05 i firmware niezmieniane; P07 HOLD.

## P03 CORE — R4, HISTORIA / BAZA DLA R5 (27.09.2026)

Historyczny pakiet: `Plytki/P03-R4-review` (+ `.zip`, `.zip.sha256` 36d73f76…). Decyzja użytkownika po końcowej recenzji R2 (P3-01).

U6 SN74LVC1G17DBVR (A = SUP_N, Y → R41 220 Ω 1206 → SUP_N_OUT = J4.15), C15 100 nF przy U6, zasilanie 3V3_CORE. P04 dostaje jedno zbocze

ok. 10 ns zamiast narastania EN modułu (τ ≈ 5 ms); przy taśmie H_SAFE 150 mm ≤ 5,5 ns/V w oknie 0,8–2,0 V (limit 10 ns/V do ok. 36 pF).

PCB bez nowego trasowania: miedź R3 z `routing/P03-R3.ses` zasiana jako zablokowana (seed_r3.py), zmiana przy J4 położona ręcznie (route_critical.py).

Bilans wobec R3 (13/13): −3 odcinki R3, +25 elementów w obszarze 6–31 × 58–84 mm, HW_ARMED_CORE obchodzi U6 po B.Cu (2 przelotki); reszta identyczna.

ERC 0, 430 pinów, DRC 0/0/0, PCB 30/30, funkcje 53/53, mutacje 43/43, próby 18/18 + zerowa; czyste odtworzenie PASS.

Otwarte: recenzja layoutu przy J4, przekrój B2B P03–P05 (przed zamówieniem obu PCB), antena, LDO, ODBIOR (nowe próby U6/R41). Gerbery po recenzji i przekroju B2B.



## P03 CORE — R3, HISTORIA / BAZA DLA R4 (27.09.2026)

Aktualny pakiet: `Plytki/P03-R3-review` (+ `.zip`, `.zip.sha256` 8f25ac8f…). Końcowa recenzja R2 Astry (Claude):

`Plytki/P03-R2-recenzja/RECENZJA-P03-R2.md` — bez blokera; P03-01…07 z R1 zamknięte (sprawdzone w netliście

i kartach: LTC4412 zasilany z VIN lub SENSE → USB-only trzyma Q1 zamknięty; RESET MCP23017 = Schmitt).

Interfejsy pin w pin z P02-R3 (LV03), P04-R2.1 (H_SAFE), P05-R1 (B2B, bez lustrzanego odwrócenia rzędów).

R3: tylko R14 (CORE_LINK) 0 Ω → 1 kΩ; miedź i rozmieszczenie = R2 (kontrola 11/11). Nowe kontrole: szyny

zasilania na złączach, złącza vs zamrożeni sąsiedzi; próby ujemne z próbą zerową (w R2 DRC kopii oblewał przez

brak bibliotek — błąd mojego skryptu z R1; dangling_lock był pozorny). ERC 0, 421 pinów, DRC 0/0/0, PCB 29/29,

funkcje 51/51, mutacje 37/37, próby 15/15 + zerowa; czysta regeneracja PASS. **Do decyzji użytkownika:**

SUP_N (wspólny z EN modułu, 1 µF) ma na J4.15 zbocze ms, a P04 odbiera je na 74LVC125A (≤10 ns/V) — skutki

tylko w stanie rozbrojonym; czysta poprawka = SN74LVC1G17 przed J4.15, wymaga nowego trasowania. Otwarte:

przekrój B2B P03–P05 (przed zamówieniem obu PCB), antena, LDO, ODBIOR. Gerbery po przekroju B2B.



## P03 R2 — HISTORIA / BAZA DLA R3 (26.09.2026)

Aktualny pakiet: `Plytki/P03-R2-review` (+ `.zip`, `.zip.sha256`). Poprawki po recenzji
`Plytki/P03-R1-recenzja-Codex`; oryginał R1 bez zmian (98/98 hashy).

Stany domyślne przed buforami, wspólny reset EN/MCP/P04 przez bufor OD, blokada
USB→5V_SYS na LTC4412/AO3401A, C3 przy VDD6, krótkie rezystory szeregowe SPI,
pięć czytelnych arkuszy A3. Zachowane złącza, pozycje modułów i GPIO.

ERC 0, 421 pinów, DRC 0/0/0, kontrole PCB 29/29, funkcjonalne 48/48;
wykryto 15/15 usterek PCB i 33/33 usterek netlisty. Odtworzenie z pustego katalogu
bez sąsiedniego P02 zaliczone. Dokumentacja: `docs/ZMIANY-R2.md`,
`docs/DLA-RECENZENTA.md`, `verification/QA.md`; BOM i wykaz ilości w `docs/`.

Pakiet do niezależnej recenzji, bez Gerberów. Otwarte: przymiarka P03–P05,
pomiary resetu, USB, SD/SPI i temperatur. P05 firmware poza zakresem, P07 nadal HOLD.

## P03 R1 — HISTORIA / BAZA DLA R2 (25.09.2026)



Pakiet: `Plytki/P03-R1-review`, archiwum `Plytki/P03-R1-review.zip` (+ `.zip.sha256`).

Schemat i layout Claude, recenzja: Astra. ESP32-S3 Waveshare N32R16V na gniazdach, microSD

Adafruit 4682, MCP23017, 74HC139, TPS3808 na PA0085, siedem 74LVC125A na adapterach SO14.

Decyzje użytkownika 25.09: listwy modułu co 22,86 mm; P03 i P05 obok siebie, J1 DAQ kątowe

przy prawej krawędzi; format 160 × 120 jak P01/P02; PA0085 2 × 3 co 15,24 mm; CAN jako IDC

2 × 3 z kluczem 4 (5–6 NC — wiązka do P10 ma 6 pozycji).



Schemat = import v6.1 pin w pin (310 pinów, 0 różnic; dodane TP1–TP6). 2 × 35 µm,

piąty otwór H5 (155; 38) przy J1. USB-C modułu na górnej krawędzi, antena w głąb płytki nad

strefą bez miedzi (sporne: zasięg Wi-Fi). Sygnały 0,30/0,25 mm, zasilanie 0,6 mm, 5V_SYS 1,0 mm;

wylewki GND zszyte 48 przelotkami. ERC 0, netlista 347/347, DRC 0/0/0, 26/26 kontroli PCB,

14/14 prób ujemnych. J1 identyczne z kopią P03 użytą w P05 R1 (pin 1 w (147; 31)).



Otwarte: przymiarka 1:1 (moduł Waveshare, 4682, para J1/P05 z dystansami, adapter SO14),

zasięg Wi-Fi, zbocza magistrali ADC na P05. Sprzęt NIE ZBADANO. Brak Gerberów.

Zakupy: `docs/ZAKUPY-P03.md` (m.in. gniazdo kątowe J1 kupować razem z wtykiem P05).



## P04 SAFE — R2.1, HISTORIA / BAZA DLA R2.2 (26.09.2026)

Historyczny pakiet: `Plytki/P04-R2.1-review` (+ `.zip`, `.zip.sha256`).
Zacząć od `docs/ZAMKNIECIE-P04.md`. Recenzja Codexa: brak błędu wymagającego
zmiany schematu lub miedzi. Projekt zamknięty do wykonania prototypu.

CAD, wiercenia, nadruk i oba PDF identyczne z P04-R2 Opusa. R2.1 poprawia opis
histerezy/resetu, skutków zwarcia wyjść HC i zakres E01–E22; dodaje testy wartości,
BOM oraz połączeń z aktualnymi P01/P02/P03/P05. Karty wymiarowe złączy sprawdzone.

Świeże ERC 0, DRC 0/0/0; 26 kontroli PCB, 22 logiki, 11 wartości/interfejsów;
49/49 celowych usterek wykrytych. Niezależna generacja z czystych źródeł daje ten
sam layout. Cała miedź GND tworzy jedną grupę. Sprzęt NIE ZBADANO.

Następny krok: przymiarka rzeczywistych części na wydruku 100% (M01), następnie
Gerber/Excellon i prototyp. Po lutowaniu E01–E22 z P00. Kolejna recenzja modelu
nie jest wymagana bez nowej, konkretnej niezgodności. P07 nadal HOLD; uwaga o
P03 R14 CORE_LINK 0Ω→1kΩ pozostaje osobnym zadaniem integracji.

Oryginały P04-R1 i P04-R2 zachowane.

## P04 R1 — HISTORIA / BAZA DLA R2 (25.09.2026)



Pakiet: `Plytki/P04-R1-review`, archiwum `Plytki/P04-R1-review.zip`

(+ `.zip.sha256`). Nowa płytka Codexa: sprzętowy STOP, watchdog, ARM,

INTERLOCK, MOTOR_PERMIT i SENSOR_PERMIT. Baza: v6.1-rc1; zachowano

aktywne piny interfejsów. P03, P00 oraz wcześniejsze pakiety bez zmian.



160 × 120 mm, 2L 35 µm, FR4 1,6 mm, montaż THT + trzy SO14 na adapterach.

Lokalny MCP100-315DI/TO, regeneracja SAFE_N przez HC14, otwarte kolektory

2N3904, filtr ARM, odsprzęganie, kotwy taśm 12–14,54 mm od lutów.

SENSOR przechodzi z IDC4 na IDC6 M2.2 (1–4 zachowane, 5–6 NC):

przy projektowaniu P08 obowiązuje nowa wiązka. SAFE do CORE bez zmian pinów.



ERC 0, netlista 343/343, DRC 0/0/0, 20/20 kontroli PCB, 19/19 elektrycznych.

131072 kombinacje wejść; wykryto 10/10 mutacji logicznych i 5/5 PCB.

Czyste odtworzenie dało identyczną geometrię. PDF: 6 arkuszy schematu,

4 strony PCB/montażu. Od recenzji zacząć od `docs/DLA-RECENZENTA.md`.



Otwarte: przymiarka adapterów i konkretnych złączy (w tym karta 10p Würth

oraz geometria ogonków/kołków Mini-Fit), pomiar HC123 przy 3,3 V, kwalifikacja

ARM i współpraca z modułami. Nie wydano Gerberów do zamawiania.

Sprzęt NIE ZBADANO. P07 nadal HOLD do oceny rzeczywistego BTS7960.





## P05 DAQ — SCHEMAT I PCB R1 DO RECENZJI (25.09.2026)



Pakiet: `Plytki/P05-R1-review`, archiwum `Plytki/P05-R1-review.zip`

(+ `.zip.sha256`). AD7606BBSTZ, osiem kanałów napięciowych, przekaźniki

odczepów, VSENSE/AUX i sprzętowy nadzór DAQ_OK. Baza: v6.1-rc1 i zapisana

kopia interfejsów P03. P03 i poprzednie płytki pozostają bez zmian.



160 × 120 mm, 2L 35 µm, FR4 1,6 mm. Lokalny MCP1700 zasila VDRIVE

oraz logikę P05. Bufory Ioff na wejściach i DOUT/BUSY; MEAS_EN & DAQ_OK

sprzętowo włącza cewki. B2B koplanarne z P03; pięć wiązek lutowanych

w PTH z kotwami 11,5–15 mm od rzędów. C27–C34 mają oznaczenia B.SilkS,

powtórzone na niebiesko w rysunku montażowym od góry.



ERC 0, netlista 421/421, DRC 0/0/0, 20/20 kontroli PCB, 21/21 elektrycznych.

Wykryto 9/9 mutacji elektrycznych i 5/5 PCB. Czyste odtworzenie dało

identyczny odcisk geometrii. PDF: 8 arkuszy schematu i 4 strony PCB.

Recenzję rozpocząć od `docs/DLA-RECENZENTA.md`.



Otwarte przed produkcją: fizyczna przymiarka i numeracja kontaktów B2B

P03/P05, wariant SW1 oraz kwalifikacja Ceff C12/C13. Przed pracą ADC:

sekwencja resetu z oczekiwaniem 2100 ms i obsługa zaniku P05 według

`docs/INTEGRACJA.md`; niezmieniony firmware nie został zakwalifikowany.

Formularz pomiarów: `docs/ODBIOR.md`. Sprzęt NIE ZBADANO.

Nie wydano Gerberów do zamówienia. P07 nadal HOLD do oceny BTS7960.

**Recenzja R1 (Claude, 27.09.2026):** `Plytki/P05-R1-recenzja/RECENZJA-P05-R1.md` (+ skrypty dowodowe). Logika i połączenia poprawne,

świeże ERC 0 / DRC 0/0/0, netlista zgodna z pakietem. Przed PCB: P5-01 — odsprzęganie AD7606B (REFCAP, REFIN/REFOUT, REGCAP, AVCC 37/38/48)

stoi 7–21 mm drogi od pinów, obok jest wolne miejsce, a DOUT biegnie po B.Cu pod U1; P5-02 — okno DAQ_OK ciaśniejsze niż TSR 2-2450 (±2 % + dryft), R5 5,90k → 6,04k i R7 5,23k → 5,11k.

Dalej: próba zadziałania przekaźników w upale (P5-03), R13 10k → 47k (P5-05), opcjonalna 1N5817 (P5-06), budżet pojemności 5V_SYS (P5-07).

P5-04 zamknięte 28.09 kartą AD7606B Rev. B od użytkownika (kopia w `zrodla/`): 64/64 piny i odsprzęganie REFIN/REFOUT zgodne z kartą.



## P06 I-LOGGER — SCHEMAT I PCB R1 DO RECENZJI (27.09.2026)

Pakiet: `Plytki/P06-R1-review`, archiwum `Plytki/P06-R1-review.zip` (+ `.zip.sha256`).
PCB 120 × 100 mm, dwuwarstwowa FR4 1,6 mm, Cu 70 µm/stronę. PBV 5 mΩ / 0,5%,
INA240A2 SOIC, MCP6022, lokalny MCP3201, SPI do P03-R2. NKK S6A na panelu:
MEASURE/BYPASS, niezależny styk pomocniczy; READY oznacza szyny i pozycję, nie kalibrację.
Pięć wiązek PTH z kotwami; LV06 do P02/J6, ILOG do P03/J2, ISERIES do przyszłej P11.

Względem v6.1: dzielnik 5K1/5K1, filtr 470 nF / 133 Hz do trendu prądu 2 ksps,
R8=100K i bleed R24 ograniczają zasilanie wyłączonej domeny. R21 obciąża srebrny styk;
budżet P06 wzrasta do 180 mA/5 V, do uwzględnienia w odbiorze HOLD całego urządzenia.
Nie zmieniono limitów aktywnego testera ani poprzednich płytek; P07 nadal HOLD.

ERC 0, netlista 208/208, DRC 0/0/0, 32 kontrole elektryczne i 24 PCB PASS,
27/27 celowych błędów wykrytych; jeden połączony obszar GND. Czyste odtworzenie
od pustego katalogu CAD daje identyczną geometrię. 6+4 stron PDF obejrzane.
Źródła, wyniki i manifest w pakiecie. Zacząć od `docs/DLA-RECENZENTA.md`.

Otwarte: niezależna recenzja R1, przymiarka rzeczywistych części (zwłaszcza PBV,
PTH/przewody, SW1 i wtyki), kwalifikacja R6, temperatura/prąd i odbiór ODBIOR.md.
Zakres pomiaru do początkowej kwalifikacji ±6 A; próba cieplna biernego toru 10 A.
Filtr nie odtwarza impulsów PWM. Sprzęt NIE ZBADANO. Gerbery po przymiarce.


## P08 SENSOR — SCHEMAT I PCB R1 DO RECENZJI (27.09.2026)

Pakiet: `Plytki/P08-R1-review`, archiwum `Plytki/P08-R1-review.zip` (+ `.zip.sha256`).
PCB 100 × 80 mm, dwuwarstwowa FR4 1,6 mm, Cu 35 µm/stronę. TPS2553DBVR,
G6K-2P-Y DC5 THT rozłączający plus i powrót, TBD62083, nadzorcy MCP120,
bufory 74LVC125AD. Limit TPS około 117 mA typowo, obliczeniowo 99–139 mA.
Początkowa identyfikacja sensora nadal przy osobnym limicie 20 mA.

Wiązki PTH z kotwami: LV08 do P02-R3/J8, SENSOR 6p KEY2 do P04-R2.1/J4,
SFAULT 6p KEY3 do P03-R2/J6. J4 TSENSOR Mini-Fit 2p; W4 należy do przyszłej P11.
Poprawiono footprint G6K według rysunku producenta (3,2 mm zamiast 3,0 mm).
U8 niezależnie wymusza LOW na TPS_EN podczas brownout. SENSOR_OK/HEALTHY
nie potwierdzają styków ani napięcia na sensorze.

ERC 0, netlista 172/172, DRC 0/0/0, 35 kontroli elektrycznych i 25 PCB PASS,
35/35 celowych błędów wykrytych, jeden połączony obszar GND. Odtworzenie
od pustego CAD/raportów daje identyczną geometrię i ponownie ERC/DRC 0.
Obejrzano 4+4 strony PDF. Zacząć od `docs/DLA-RECENZENTA.md`.

Otwarte do integracji: 750 ms stabilnej gotowości przed pierwszym PERMIT i po
zaniku zasilania; bazowe 100 ms w board_mode() nie gwarantuje zwolnienia U8.
Wspólnego firmware nie zmieniono. CORE musi zatrzasnąć FAULT i cofnąć PERMIT.
Otwarte do odbioru: fizyczna przymiarka, brownout/Ioff, margines cewki przy 3,3 V,
limit prądu/temperatura i ODBIOR.md. Sprzęt NIE ZBADANO. Gerbery po przymiarce
i recenzji. Poprzednich płytek nie zmieniono; P07 nadal HOLD.


## P09 TEMP — SCHEMAT I PCB R1 DO RECENZJI (27.09.2026)

Pakiet: `Plytki/P09-R1-review`, archiwum `Plytki/P09-R1-review.zip` (+ `.zip.sha256`).
Nośnik dwóch kupionych MAX31856 XU, oferta Allegro 18805671895; PCB 100×100 mm,
2 warstwy, FR4 1,6 mm, Cu35 µm. LV09 do P02-R3/J9, TEMP10p KEY4 do P03-R2/J7.
Wiązki PTH z kotwami, moduły w gniazdach. Niezależne selektory VIN, domyślnie OPEN.
U1/U2 74LVC125AD z Ioff, U3 HC139 wybiera pojedynczy MISO. Przerwa CS ≥1 µs.

ERC0, netlista147/147, DRC0/0/0, 43 kontroli obwodu i20 PCB PASS; 25/25 celowych
błędów CAD wykrytych. Jeden połączony obszar GND. Czysta odbudowa daje identyczną
geometrię; 4+4 strony PDF obejrzane. Zacząć od `docs/DLA-RECENZENTA.md`.

Wykryto i poprawiono błędną mapę rejestrów MAX31856 w bazowym board.c:
temperatura0x0C–0x0E, SR0x0F. Dołączono diff i27 testów funkcji +3 regresje.
Pełna kompilacja ESP-IDF oraz scalenie zmian P05/P08 pozostają do integracji.

Otwarte przed produkcją: przymiarka kupionych modułów, raster i podparcie,
kwalifikacja VIN/3Vo oraz poziomów SPI. Otwory Ø6 mm pod nylonowe M2.5 są
regulacją, nie potwierdzeniem wymiarów producenta. Sprzęt NIE ZBADANO.
Gerbery po potwierdzeniu mechaniki i recenzji. Poprzednich płytek nie zmieniono;
P07 nadal HOLD dla wariantu BTS7960.


## P10 CAN — SCHEMAT I PCB R1 DO RECENZJI (27.09.2026)

Pakiet: `Plytki/P10-R1-review`, archiwum `Plytki/P10-R1-review.zip` (+ `.zip.sha256`).
PCB 80×70 mm, dwuwarstwowa FR4 1,6 mm, Cu35 µm. TCAN1051VDRQ1, PESD2CAN,
bufor RX 74LVC125AD z Ioff. S i TXD stale do VIO; CAN_TX z CORE tylko do TP6.
P10 pasywna sprzętowo, bez terminacji120 Ω. Bufor RX oddziela wyłączoną P10
od podciągania na P03 zasilanej z USB. Stan częściowego zaniku do zmierzenia.

W1 LV10 200 mm do P02-R3/J10, W2 CAN IDC6 KEY4 150 mm do P03-R2/J8,
W3 skrętka120 Ω 300 mm do OBD6/14. Wszystkie trzy wiązki PTH z kotwami.
OBD4/5/16 NC; wspólna masa z pojazdem przez główne zasilanie EGRLab.

ERC0, netlista57/57, DRC0/0/0, 26 kontroli obwodu i21 PCB PASS; 28/28 celowych
błędów CAD wykrytych. Jeden połączony obszar GND. Czysta odbudowa: identyczna
geometria i dwa pliki schematów; ponownie kontrole PASS. Obejrzano 2+4 strony PDF.
Zacząć od `docs/DLA-RECENZENTA.md` i `verification/QA.md`.

P10 nie nadaje zapytań OBD ani ACK. RPM wymaga potwierdzonego źródła/ID/dekodera.
Wspólnego firmware nie zmieniono; wymaga testu kolejek, strat i opóźnień CAN/SD/DAQ.
Stanowisko: dwa aktywne węzły z ACK i prawidłowa terminacja, P10 jako odczep.
Sprzęt NIE ZBADANO. Gerbery po recenzji i przymiarce; przed autem ODBIOR.md.
Poprzednich płytek nie zmieniono. P07 nadal HOLD dla wariantu BTS7960.


## P11 PANEL — SCHEMAT I PCB R1 DO RECENZJI (27.09.2026)

Pakiet: `Plytki/P11-R1-review`, archiwum `Plytki/P11-R1-review.zip` (+ `.zip.sha256`).
Pasywna dystrybucja panelu,PCB160×110 mm,2 warstwy Cu70 µm,FR4 1,6 mm.
J1 Phoenix1755752,J7 Molex39-29-9129 Au z kołkami. Dziewięć lutowanych wiązek PTH
z kotwami10,5–14,7 mm. Przełączniki,detektory,DT i BNC montowane poza PCB.

TEST i LOGGER mają oddzielne ścieżki3 mm bez przelotek;powrót AGND_SENSOR
pozostaje odseparowany od GND. Kontrakty P03-R2/P04-R2.1/P05-R1/P06-R1/P08-R1.
PANEL_3V3 z P04 przez100 Ω;bez dodatkowego obciążenia na P11. Pełny model
obciążenia daje SAFE_N2,748 V przy3,18 V;sumę upływności i stan gorący trzeba
potwierdzić na stanowisku. Podano referencyjne styki EAO low-level dla małych prądów.

Wspólne TAPy:dozwolony jeden adapter naraz. DT nie zawiera detektorów — własne
popychacze muszą rozłączać NC LOGGER przed pierwszym kontaktem elektrycznym.
Mechanika panelu i testy obciążenia pozostają do odbioru. TMOTOR/P07 nadal HOLD.

ERC0,159/159 pinów,DRC0/0/0.38 kontroli elektrycznych,36 PCB,64 stany kontaktów;
30/30 celowych usterek wykrytych. Czysta odbudowa:ta sama geometria i4 schematy,
ponownie kontrole PASS. Obejrzano4+4 strony PDF. Formularz ODBIOR niewypełniony.

Start:`docs/DLA-RECENZENTA.md`,`verification/QA.md`,`docs/ZAKUPY.md`.
Sprzęt NIE ZBADANO,brak Gerberów zatwierdzonych do produkcji.
Wcześniejszych płytek ani wspólnego firmware nie zmieniono.

