# P02-R1 — niezależna recenzja Codex

Data: 25.09.2026. Oceniany pakiet: `EGRLab/Plytki/P02-R1-review` autorstwa Opusa/Claude.
Schemat i PCB pozostawione bez zmian. Pomiary sprzętowe i przymiarka nie były wykonywane.

## Werdykt

**Przyjąć architekturę i zasadniczy layout. Wykonać lokalną korektę toru HOLD_READY, ochronę punktu TP3 i poprawić dokumentację przed zamknięciem projektu PCB. Nie ma uzasadnienia do projektowania całej P02 od nowa.**

To uporządkowany projekt: funkcjonalne rozmieszczenie, osobne tory silnika i podtrzymania, sensowne przekroje miedzi, jasno opisane odstępstwa i rzeczywiście działające kontrole. Deklarowane wyniki CAD odtworzyłem. Nie znalazłem w przejrzanych połączeniach błędnego podłączenia D_OR, zamiany szyn LV ani powrotu energii banku do silnika przez połączenie miedziane.

Najważniejsza luka dotyczy znaczenia nowego sygnału gotowości, a nie routingu. Zielona LED nie gwarantuje warunków zapisanych w kontrakcie HOLD C1. Pozostałe uwagi dotyczą dynamicznego działania komparatora, serwisu i czytelności schematu.

## Co sprawdziłem niezależnie

| Sprawdzenie | Wynik |
|---|---|
| Pliki względem manifestu wydania | Wszystkie hashe zgodne przed badaniem |
| Świeży ERC obu arkuszy | 0 naruszeń |
| Świeżo wyeksportowana netlista vs `parts.json` | 70 części, 200 pinów, 44 sieci, 0 błędów |
| Świeży DRC wszystkich ważności, z ponownym wypełnieniem stref i zgodnością ze schematem | 0 / 0 / 0 |
| Ponowne wykonanie `verify_pcb.py` | 28/28 PASS |
| Ponowne wykonanie ośmiu prób ujemnych | 8/8 wykrytych przez wskazane kontrole |
| Osobne porównanie z importem P02 v6.1 | Wszystkie 32 wcześniejsze części zmapowane; 125 pozycji pinowych porównanych; tylko oczekiwane zmiany |
| Osobne porównanie połączeń HOLD z `contract.json` | Brak rozbieżności |
| Oględziny | Oba arkusze schematu, cztery strony dokumentacji PCB, montaż, obie warstwy miedzi i render z góry |
| Zachowanie pakietu źródłowego | Żaden plik oryginalnego P02-R1 nie został zmieniony |

Zmiany względem importu: wejścia F2/F3 na VLOG_RES, wykorzystanie wolnych bramek U6 do HOLD_READY i wykorzystanie J12.3. Znormalizowano nazwy VIN_DC5/VIN_DC33 oraz dawne opisowe nazwy pinów przetwornic i bezpieczników. Pozycja 5 PSUOK pozostaje elektrycznie niepodłączona i służy kodowaniu końca IDC.

Badania uruchamiano na kopii, bez przebudowy ani ponownego routingu oryginału. Są to powtórzone kontrole gotowego wydania, nie deklaracja odtworzenia całego generatora `run_release.py`.

## R-01 — HOLD_READY nie dowodzi gotowości określonej w C1

**Priorytet P2, błąd funkcjonalnej interpretacji wskaźnika.** Lokalny sygnał nie steruje ARM, więc nie jest to nowa droga samoczynnego uruchomienia silnika.

Miejsca: `src/parts.py` — U7, R6–R13, LED1; `reference/contract.json`; `docs/ZALOZENIA-P02-R1.md`; `docs/BOM.csv` — opis LED1.

Kontrakt wymaga przed zdarzeniem banku co najmniej 9,5 V oraz kwalifikacji VPROT co najmniej 11,5 V przez 15 s. Dokumentacja R1 opisuje świecącą LED jako bank ≥9,5 V i VPROT ≥11,6 V, ale:

1. Histereza świadomie utrzymuje BANK_OK do około 9,1 V i VPROT_OK do około 11,1 V. Opis LED pomija jej historię.
2. Wartości progów są nominalne; nie uwzględniono tolerancji rezystorów, wzorca, komparatora i szyn zasilających.
3. Timer 15 s jest odłożony do przyszłego firmware, a HOLD_READY nie jest jeszcze odbierany przez CORE. W aktualnej rewizji cała kwalifikacja nie działa automatycznie.

Przeliczyłem dzielniki z rzeczywistych wartości w `parts.json`, uwzględniając obciążenie wyjścia przez rezystor histerezy. Przy REF=2,495 V, pull-up=3,3 V i przykładowym VOL=0,15 V:

| Próg | Nominalnie | Zakres tylko od R ±1% i REF ±0,5% |
|---|---:|---:|
| BANK załączenie | 9,44 V | 9,26–9,63 V |
| BANK wyłączenie | 9,06 V | 8,88–9,24 V |
| VPROT załączenie | 11,55 V | 11,31–11,79 V |
| VPROT wyłączenie | 11,05 V | 10,82–11,28 V |

To demonstracja luki, **nie pełna analiza najgorszego przypadku**. VOL nie jest stałe, a offset, prądy wejściowe, temperatura oraz odchyłka 3V3_IO poszerzają analizę. TL431 w klasie B ma początkową dokładność ±0,5%; charakterystyki LM2903 należy brać dla zamówionego LM2903P, nie dla nowszego LM2903B. Źródła: [TI TL431](https://www.ti.com/product/TL431), [TI LM2903](https://www.ti.com/lit/ds/symlink/lm2903.pdf), tabela 5.10.

Konkretny przykład: po wcześniejszym załączeniu BANK_OK może pozostać HIGH przy banku 8,90 V. Gdy VPROT wróci i PSU_OK jest HIGH, LED może zaświecić przed doładowaniem. Dla granic C1: C=52,8 mF, spadek 1,2 V, minimalne wyjście 7 V oraz 6 W + 0,15 W rezerwy, model stałego spadku daje:

`t = C × ((8,90 − 1,20)² − 7²) / (2 × 6,15) = 44,2 ms`

To mniej niż wymagane 50 ms. Jest to wynik obliczeniowy dla dopuszczonego zestawu granic, nie zaobserwowana usterka sprzętu. Warunek C1 „bank ≥9,5 V” nadal zapewnia przewidziany zapas; problemem jest uznanie LED za potwierdzenie tego warunku.

**Zalecenie:** zachować lokalny komparator, ale dobrać progi i tolerancje tak, aby minimalny próg wyłączenia BANK_OK nie był niższy od przyjętej granicy gotowości. Analogicznie rozstrzygnąć granicę VPROT. Weryfikować także maksymalny próg załączenia względem napięcia osiągalnego po ładowaniu. Opisać wskaźnik jako gotowość napięciową; 15 s i odbiór pod obciążeniem pozostają oddzielnymi warunkami. Do integracji CORE dodać jednoznaczną procedurę ręcznej kwalifikacji, a nie udawać, że odłożony firmware już ją realizuje. Nie trzeba teraz zmieniać P03/P04.

## R-02 — filtry C14/C15 opóźniają również dodatnie sprzężenie komparatora

**Priorytet P2, konkretna słabość topologii wymagająca korekty lub weryfikacji dynamicznej.**

Miejsca: `src/parts.py` — R6–R13, C14/C15 i U7; arkusz `MON.kicad_sch`.

C14 i C15 są bezpośrednio na wejściach nieodwracających U7, do których dochodzi też sprzężenie przez 2,2 MΩ. Stałe czasowe tych węzłów wynoszą około 7,04 i 7,50 ms. Po zmianie wyjścia napięcie wejścia nie może skoczyć natychmiast, więc również regeneracyjne działanie histerezy zostaje spowolnione. Sam rachunek progów DC i kontrola długości ścieżki tego nie badają.

Nie stwierdzam, że ten egzemplarz na pewno będzie oscylował. Wskazuję konkretny mechanizm podatności na wielokrotne przełączenia przy wolnym przechodzeniu przez próg i zakłóceniach. TI zwraca uwagę dokładnie na taką konfigurację: [odpowiedź TI dotycząca kondensatora w węźle dodatniego sprzężenia](https://e2e.ti.com/support/amplifiers-group/amplifiers/f/amplifiers-forum/1215061/lm2903b-q1-comparator-hysteresis-calculation).

**Zalecenie:** oddzielić filtrowany węzeł pomiarowy od węzła szybkiego sprzężenia albo zastosować sprawdzoną topologię filtru z histerezą i przeliczyć ją razem z R-01. Sprawdzić narastanie/opadanie banku i VPROT, szczególnie wolną rampę wokół progów, szum oraz ponowne włączenie. Obserwować oba wyjścia U7, nie tylko LED. Zostawić LM2903P, jeżeli po zmianie układ spełni wymagania; nie jest konieczna wymiana całej koncepcji nadzoru.

## R-03 — TP3 powinien być punktem pomiarowym z ograniczeniem prądu

**Priorytet P2, decyzja serwisowa do poprawy przed PCB.** Opus sam trafnie wskazał ten punkt do rozstrzygnięcia.

Miejsca: `src/parts.py` — TP3; `src/route_critical.py`; `docs/MECHANIKA.md`.

TP3 jest bezpośrednio na HOLD_STORE, po stronie banku niezabezpieczonej przez F1. Zwarcie sondy omija bezpiecznik. Nie zmienia tego blokada ścieżki w CAD ani ostrzeżenie na nadruku. Ten punkt służy do pomiaru napięcia, więc bezpośrednie połączenie o dużej wydajności prądowej nie jest potrzebne.

**Zalecenie:** bank → lokalny rezystor 1 kΩ / 2 W → TP3. Rezystor przy odczepie, przed odsłoniętym punktem. Przy 32 V zwarcie TP3 oznacza około 32 mA i początkowo 1,024 W. Dla wejścia miernika 10 MΩ błąd podziału wynosi około 0,01%, dla oscyloskopu 1 MΩ około 0,10% — mały, lecz nie zerowy. Zapisać go w procedurze pomiaru. Prąd testu obciążeniowego prowadzić osobnym, przeznaczonym do tego torem za F1. Nadal osłonić luty banku od spodu.

Nie jest to powód do wymiany banku ani dodawania rozbudowanego systemu zabezpieczeń. To jeden rezystor ułatwiający pracę przy stole.

## R-04 — schemat PDF ma widoczne kolizje i elementy przy tabliczce

**Priorytet P2 dla dokumentacji montażowej, bez wykazanego błędu połączeń.**

Miejsca: `src/build_schematic.py`, `src/cadlib.py`, `output/pdf/P02-R1-schemat.pdf`.

Oględziny obu pełnych arkuszy wykazały:

- Arkusz P02: wartości i opisy J3–J10 nachodzą na piny/etykiety; opis J11 nachodzi na symbol; blok LV wchodzi w obszar tabliczki. Ramka arkusza hierarchicznego MON przy górnej krawędzi znajduje się częściowo poza obszarem roboczym.
- Arkusz MON: opis U3 nakłada się na jego linię RST; dolny rząd niewykorzystanych bramek, w tym U5D, wchodzi w tabliczkę; opis LED1 przy prawej krawędzi jest przycięty. Dopisek o progach leży pod dolną ramką.

ERC i zgodność 200 pinów nie sprawdzają czytelności rysunku. Natomiast czterostronicowy PDF **PCB** jest znacznie czytelniejszy: rozmieszczenie, komentarze i belki skali są użyteczne, a widok B.Cu uczciwie oznaczono jako widok przez płytkę, bez odbicia.

**Zalecenie:** przenieść rząd niewykorzystanych bramek i rozdział LV na dodatkowy arkusz lub przebudować rozmieszczenie dwóch arkuszy. Wykorzystywać wolne miejsce na widoczne przewody między elementami toru zasilania i nadzoru, zamiast oddzielnych etykiet na każdym pinie. Następnie ponownie obejrzeć całe PDF-y przy czytelnym powiększeniu. Nie zmieniać połączeń przy tej korekcie graficznej.

## Ocena decyzji pozostawionych przez Opusa do recenzji

| Decyzja | Ocena |
|---|---|
| Bank HOLD na P02 | Przyjąć. Eliminuje dodatkową wiązkę dużej pojemności i pomyłkę HOLD/SUPPLY. |
| R_CHARGE poza PCB | Przyjąć. Dokumentacja blachy, mocowania i próba temperatury pozostają zadaniem montażowym. |
| HOLD_READY lokalnie | Przyjąć zgodnie z założeniem użytkownika; naprawić R-01/R-02 i jawnie opisać nieobecny timer. |
| Timer 15 s w CORE | Przyjąć jako plan integracji. Nie trzeba budować osobnego długiego timera RC na P02. |
| GMSTBA 7,62 zamiast PC4 | Przyjąć dla toru do 5 A. Producent podaje 12 A; odpowiedni wtyk to GMSTB 2,5/3-ST-7,62, 1767012. Zachować zmianę w kontrakcie do przyszłej P07. P07 nadal HOLD. |
| Rezystory górne dzielników przy źródle | Przyjąć. Wysokoimpedancyjny przewód za rezystorem jest sensowniejszy niż długi odczep surowego banku. |
| Brak przelotek zszywających | Nie uznaję za błąd blokujący. Przewlekane pady GND łączą warstwy. Kilka lokalnych połączeń może pomóc, lecz liczba przelotek nie jest kryterium jakości sama w sobie. |
| LM2903 zasilany z 5 V, wejście dzielnika chwilowo wyżej | Nie odrzucać tylko z tego powodu. Karta dopuszcza właściwe działanie przy jednym wejściu w prawidłowym zakresie wspólnym. Sprawdzić osobno rozruch/zanik 5V_SYS i granice napięć. |

Źródło złącza: [Phoenix 1766246, parametry i akcesoria](https://www.phoenixcontact.com/en-ca/products/pcb-header-gmstba-25-3-g-762-1766246). Warunek wejść komparatora: TI LM2903, przypis (3) pod tabelą 5.10.

## Co domknąć bez przeprojektowywania płytki

1. **Konkretne wkładki bezpiecznikowe i MPN złączy.** R1 otwarcie pozostawia je do wyboru. Dobrać je przed ostatecznym BOM i odbiorem. Sama informacja „DC ≥32 V” nie określa zdolności wyłączania ani I²t banku. F2/F3 1 A są wyborem dla ograniczonej mocy EGRLab, nie obietnicą poboru pełnych 2 A z każdej przetwornicy przy każdym napięciu wejściowym.
2. **Mechanika banku i kompletne obrysy przestrzenne.** W widoku 3D brakuje m.in. Mini-Fitów, adaptera U5 oraz widocznych korpusów U1/U2. Nie potrzebujemy fotorealistycznych modeli: wystarczą poprawne obwiednie z wtykami i dostępem do zatrzasków. Dla trzech dużych kondensatorów ustalić mocowanie do PCB/obudowy oraz osłonę lutów. Snap-in i cztery śruby PCB nie opisują całego mocowania na drgania.
3. **Odsprzęganie adaptera U5.** C11 jest blisko pinu 14 adaptera, ale kontrola nie obejmuje dodatkowej drogi po adapterze do nóżek układu. Sprawdzić adapter; w razie potrzeby dać 100 nF bezpośrednio na nim. Nie ma potrzeby przebudowy głównej płyty tylko dla tego punktu.
4. **Dwie korekty liczb.** Energia nominalnych 66 mF przy 32 V to 33,8 J, a przy +20% pojemności 40,6 J — nadruk „do około 41 J przy 32 V” jest trafniejszy niż uniwersalne „≥40 J”. Rozładowanie przez 4k7 do 1 V przy 32 V, C +20% i R +1% trwa około 21,7 min; „około 19 min” wymaga ograniczenia napięcia początkowego do około 18 V. Pomiar przed pracą pozostaje właściwą procedurą.
5. **Budżet całego urządzenia.** Przy integracji policzyć realną moc na VLOG_RES oraz sumę pojemności na 5V_SYS/3V3_IO. P02 nie tworzy ośmiu niezależnych zasilaczy 2 A. Wymóg HOLD jest zdefiniowany dla ≤6 W łącznie ze stratami; wzrost obciążenia wymaga ponownego rachunku i testu.

## Uzupełnienie procesu

Obecne próby ujemne są użyteczne i nie są dekoracją. Zachować je. Dodać trzy małe bramki odbioru:

1. **Funkcja analogowa:** liczone z BOM progi załączenia i wyłączenia, tolerancje, osiągalność napięcia po ładowaniu; osobne PASS/FAIL dla warunku 9,5 V i zapasu czasu. Nie porównywać jedynie netlisty z tym samym generatorem.
2. **Zachowanie w czasie:** plan i wyniki wolnych ramp, krótkich/seryjnych zaników, rozładowanego banku, przerwanego F1 i zasilania z USB. Przerwany F1 może pozostawić naładowany bank i świecącą LED mimo braku dostępnej rezerwy — napięciowy wskaźnik nie jest autotestem drożności toru. Nie wymagam dodawania takiego autotestu sprzętowego, lecz rozróżnienia tych pojęć w odbiorze.
3. **Oględziny całego finalnego schematu:** żadnych opisów poza ramką, w tabliczce ani na pinach. Model 3D musi zawierać gabaryty istotnych części, jeżeli służy do odbioru mechaniki.

Praktyczna kolejność: poprawki R-01/R-02 i TP3 → poprawa rysunków → ponowny komplet kontroli → przymiarka banku/złączy → zamknięty BOM i pakiet produkcyjny → uruchomienie samej P02. Zachować bank i 2-warstwowy układ funkcjonalny R1.

## Dowody w tej recenzji

- `review_checks.py`, `independent-review-checks.json`: manifest, niezmienność źródła, porównanie z v6.1 i C1, niezależny rachunek progów oraz przykład 44,2 ms.
- `evidence/`: świeży ERC, eksport netlisty, świeży DRC z proweniencją, 28 kontroli i osiem prób ujemnych.
- `original-sha256.json`: stan pakietu źródłowego na początku recenzji.

Oryginalny projekt pozostaje niezmieniony. Ta recenzja nie jest zatwierdzeniem produkcji ani dowodem z pomiaru sprzętu.
