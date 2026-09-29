# P02-R2 — mapa zmian dla Opusa

25.09.2026. Baza: P02-R1-review Opusa. Recenzja wejściowa: `reference/RECENZJA-P02-R1.md`. Oryginał R1 nie jest modyfikowany; jego pliki mają manifest w `reference/R1-source-sha256.json`.

| Uwaga z recenzji R1 | Zmiana w R2 | Dowód / stan |
|---|---|---|
| R-01: status utrzymany poniżej wymaganych napięć | Nowe Rt/Rb/Rf, dzielniki 0,1%; analiza pełnych kombinacji tolerancji | `HOLD-ANALIZA.md`, `electrical-checks.json`; sprzęt do odbioru |
| R-02: pojemność na węźle dodatniego sprzężenia | R18/R19 oddzielają C14/C15 od wejść; 10 nF zamiast 100 nF | arkusz HOLD; kontrola prawdziwej netlisty, obliczenia RC i skoku regeneracji; pomiar stabilności do wykonania |
| R-03: TP3 na surowym banku | R20 1 kΩ/2 W przy banku, TP3 tylko za R20; opis BANK/1k | PCB, niezależna kontrola topologii i celowa mutacja; analiza zwarcia |
| R-04: nieczytelny schemat | Cztery A3: P02, LV, MON, HOLD; rzeczywiste przewody toru HOLD | finalny PDF z natywnego KiCada; kontrola wizualna |
| Nieistniejąca kwalifikacja firmware | Wprost zapisano ręczne 15 s, brak integracji J12.3 w P04/CORE | karta i formularz odbioru; nie dodano automatycznego ARM |
| Energia i rozładowanie | 33,79 J nominalnie, do 40,55 J; około 22 min do 1 V | skrypt obliczeń, nadruk, mechanika |
| MPN złączy Au | 39-29-6048 / 39-29-6148, styki 39-00-0074 | źródła Molex w `ZAKUPY-P02.md`; przymiarka zamówionych części nadal wymagana |
| Dobór bezpieczników DC | F1 Schurter 0001.2507: T2A, 300 VDC, 1500 A | **Częściowo zamknięte**: F2/F3/F4 pozostają jawnymi pozycjami do zatwierdzenia, bez wymyślonego MPN |
| Gabaryty, wtyki, adapter | Lokalne modele 3D: bank, TSR, adapter, obwiednie wtyków | modele przybliżone, nie dowód dopasowania; mechaniczny odbiór w formularzu |
| Odsprzęganie U5 | C16 100 nF na adapterze, oprócz C11 na P02 | BOM i arkusz MON, kontrola lutowania przy odbiorze |

## Co pozostało celowo niezmienione

Format 160×120 mm, 2×70 µm, kotwy wiązek, bank na P02, R17 poza PCB, tor VMOTOR 5 A, nadzór PSU_OK i pinouty złączy. P03/P04/P07 nie zmieniono. P07 pozostaje wstrzymany do oceny kupionego modułu mostka.

Górne rezystory dzielników pozostają przy źródłach. Nie dodano przelotek masy wyłącznie dla liczby — sprawdzana jest ciągłość i geometria rzeczywistych pól.

## Prośba do recenzenta

Proszę rozpocząć od modelu progów i jego założeń, następnie sprawdzić zgodność netlisty z PCB, mechanikę TP3/R20 i adaptera oraz wydruki. Oprócz DRC proszę sprawdzić, czy zadeklarowane obwiednie tolerancji i testy warsztatowe wystarczają dla tego prototypu. Wyniki pomiarów są puste celowo: nie ma zmontowanego egzemplarza.

Ten pakiet jest **rewizją do niezależnej recenzji**, nie zamkniętym zleceniem produkcyjnym. Nie zawiera Gerberów. Do decyzji zakupowej pozostają F2/F3/F4 i przymiarka konkretnych złączy/adaptera; ich wybór należy domknąć przed zatwierdzeniem zamówienia PCB.
