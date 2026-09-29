> Dokument historyczny. Aktualne wymagania: ZMIANY-R5.md i ZASILANIE-RESET.md.

# P03-R4 — zmiany względem R3 (bufor Schmitta w resecie do P04)

27.09.2026 · Claude. Decyzja użytkownika po końcowej recenzji R2 (uwaga P3-01): między wspólnym resetem SUP_N a J4.15 dodać bufor Schmitta SN74LVC1G17. Podstawa: R3 (`Plytki/P03-R3-review`, w pakiecie zamrożone `reference/R3.kicad_pcb`, `reference/R3-parts.json` i manifest R3). Pakiety R1–R3 bez zmian.

## Schemat

| Pozycja | Wartość / MPN | Połączenia |
|---|---|---|
| U6 (nowy) | SN74LVC1G17DBVR, SOT-23-5 | 1 NC, 2 A = SUP_N, 3 GND, 4 Y = SUP_N_DRV, 5 VCC = 3V3_CORE |
| R41 (nowy) | 220 Ω 1 % 1206, RC1206FR-07220RL | SUP_N_DRV → SUP_N_OUT |
| C15 (nowy) | 100 nF 50 V X7R 1206, GRM31CR71H104KA01L | 3V3_CORE – GND przy U6.5 |
| J4.15 | SUP_N → **SUP_N_OUT** | na P04 (J2.15) sygnał nadal nazywa się SUP_N |

SUP_N do EN modułu, RESET MCP23017 i TP5 bez zmian. Uzasadnienie elektryczne (progi, R41, obciążenie taśmą, opóźnienia): `ZASILANIE-RESET.md`, sekcja R4.

## PCB

Nie trasowano płytki od nowa. **Miedź R4 = miedź R3 + jawna zmiana przy J4.** Całą zmianę kładzie ręcznie i blokuje `src/route_critical.py` (blok R4). Resztę miedzi `src/seed_r3.py` bierze z wyniku routera R3 (`routing/P03-R3.ses`). DRC kolizji na zasianej płytce nie wskazał żadnej sieci do przetrasowania. Czyszczenie i zszywanie GND dały ten sam wynik co w R3: te same 54 przelotki zszywające.

- **Rozmieszczenie.** U6 (10,1; 75,3) stoi nad J4, między strefą anteny a J4. C15 (15,0; 74,0) leży w pustym pasku pod strefą anteny. R41 (11,7; 80,4) stoi pionowo w szczelinie 2,95 mm między obudową J4 a adapterem U12. Pozycje części R3 bez zmian.
- **SUP_N:** ta sama droga R3 wzdłuż lewej krawędzi (B.Cu, x = 6,5). Kończy się przelotką (7,25; 75,3) i krótkim odcinkiem F.Cu do U6.2, a nie na J4.15.
- **U6.4 → R41 → przelotka (9,3; 81,95) → B.Cu → J4.15.** Od góry do J4.15 po F.Cu nie da się dojść, bo zamyka go MCU_ARM. W R3 J4.15 też był zasilany po B.Cu.
- **GND:** U6.3 i C15.2 mają zablokowane przelotki GND 1,0/0,5 mm, jak pozostałe kondensatory odsprzęgające.
- **3V3_CORE** dla U6/C15 idzie z U12.14 wzdłuż górnej krawędzi adaptera U12 (0,6 mm, F.Cu).
- **HW_ARMED_CORE:** ukośny odcinek R3 przechodził przez miejsce U6/R41. Zastępuje go odcinek B.Cu między przelotkami (7,5; 73,76) na przekątnej R3 i (13,6; 78,69) na odcinku R3 między U12.1 a U12.2. Reszta drogi R3 bez zmian.
- **Bilans** (`src/check_revision.py`, 13/13): usunięte 3 odcinki R3 (2 × HW_ARMED_CORE, koniec SUP_N do J4.15). Dodane 25 elementów (19 odcinków, 6 przelotek), wszystkie zablokowane, w obszarze 6–31 × 58–84 mm i tylko na sieciach zmiany. 8 odcinków R3 obu zastąpionych przewodów ma tę samą geometrię, ale jest teraz zablokowanych. Pozostałe footprinty, pozycje, pady, strefy i obrys są jak w R3.
- **Nadruk:** jak R3, plus oznaczenia U6, C15, R41 i tytuł „PCB R4”.

## Potok i kontrole

- Nowe `seed_r3.py`, `seed_sig.py` i `unseed.py`: zasianie miedzi R3 i jej odblokowanie przed czyszczeniem, żeby czyszczenie traktowało ją jak w R3.
- `import_routing.py` przyjmuje wynik routera tylko dla sieci ze zbioru przetrasowania (w R4 zbiór jest pusty). Powód: DSN zapisuje współrzędne powyżej 100 mm z rozdzielczością 1 µm, więc zasiana ścieżka jest do 0,5 µm obok padu. Przy pierwszej próbie R4 Freerouting „naprawił” to nakładającym się odcinkiem RESET_DRV_N, który DRC zgłosił jako wiszący. Własny licznik routera kończy na „1 unrouted” (w R2/R3 było „5 unrouted” przy kompletnej płytce). Nie mierzy on połączeń tej płytki, bo GND powstaje z wylewek dopiero po imporcie. Rozstrzyga DRC KiCada: 0 niepołączonych.
- `verify_function.py`: 53/53. Osobne kontrole „wspólny reset MCU/MCP” i „reset do P04 przez U6 i R41”, kontrola C15, alias w zamrożonej mapie P04 (ich SUP_N = mój SUP_N_OUT). Sześć nowych mutacji, razem 43/43.
- `verify_pcb.py`: 30/30. 91 części, C15 w kontroli odsprzęgania. Nowa kontrola: U6 ≤ 15 mm od J4.15, U6.4 → R41 ≤ 5 mm, R41 → J4.15 ≤ 15 mm drogi (jest 8,4 / 2,8 / 5,8 mm). Kontrolę zablokowanej miedzi odniesiono do `routing/critical-routed.kicad_pcb`.
- `negative_controls.py`: trzy nowe próby (U6 daleko od J4, C15 daleko od U6, oznaczenie R41 poza szczeliną); razem 18/18 plus próba zerowa.
- `compare_v61.py`: J4.15 jako jawna zmiana R4. Proweniencja DRC obejmuje wejścia zasiewania.

## Czego nie zmieniano

Pozostałe części, wartości i MPN. SUP_N do EN i MCP, U4/R34/R35, U3/R13. LTC4412 + AO3401A. Złącza (poza siecią J4.15) i ich pozycje, strefy i otwory. Brak Gerberów — powstaną po recenzji layoutu, zatwierdzeniu przekroju B2B i przymiarce.

## Sporne

- **Oznaczenie R41 w szczelinie.** R41 stoi sam między obudową J4 a adapterem U12. Żadne miejsce poza jego obrysem nie jest bliżej R41 niż tych dwóch części. Oznaczenie stoi więc pionowo tuż pod R41, a reguła „najbliższej części” pomija tylko J4 i U12 (`silkscreen.py`, `verify_pcb.py`; próba `r41_label_out` pilnuje, żeby nie odjechało).
- **HW_ARMED_CORE przez dwie przelotki.** Alternatywą było odsunięcie U6 od J4, co wydłuża drogę szybkiego zbocza SUP_N_OUT po płytce. Dwie przelotki na wolnozmiennym sygnale stanu nie mają znaczenia elektrycznego.
- **U6 zasilany z 3V3_CORE, jak U4, a nie z 3V3_IO.** Przy wyłączonym CORE wyjście U6 jest w Ioff, a R17 100 kΩ w P04 daje L, więc P04 jest rozbrojone.
- **R41 = 220 Ω:** kompromis między prądem zwarcia żyły 15 (≤ 16 mA) a zboczem na P04. Przy taśmie 150 mm najgorszy punkt okna 0,8–2,0 V to 5,5 ns/V wobec limitu 10 ns/V. Limit obowiązuje do ok. 36 pF, a więc nie dla znacznie dłuższej taśmy.
- **Layout zmieniony lokalnie.** Wymaga recenzji layoutu przy J4 (kolejność w `DLA-RECENZENTA.md`).

## Wyniki

`verification/QA.md`.
