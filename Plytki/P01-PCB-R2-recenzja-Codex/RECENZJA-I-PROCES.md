# P01-PCB-R2 — porównanie z R1 i zmiana sposobu projektowania

Data: 24.09.2026. Recenzja Codex. Zakres: gotowe PCB R1 i R2, dokumentacja, generatory i kontrole; bez zmiany schematu ani layoutu. Oryginały w `EGRLab/Plytki` pozostają nietknięte. Próby błędów wykonano wyłącznie na kopiach w katalogu tej recenzji.

## Wniosek

**R2 jest wyraźnie lepszą bazą do wykonania P01. Przyjmuję kierunek Opusa.** Poprawa wynika przede wszystkim z rozmieszczenia elementów według ich funkcji, uwzględnienia metalowych radiatorów i sposobu montażu. Nie sprowadza się do estetyki ani zwiększenia liczby testów.

W R1 popełniłem błędy projektowe: dopuściłem miedź pod metalowymi profilami radiatorów i usunąłem czytelną informację o orientacji Q2. Sprawdzałem zgodność połączeń i reguły CAD, ale nie objąłem kontrolą wszystkich istotnych warunków fizycznego montażu. Rozmieszczenie drobnych elementów zbyt mocno zależało od szukania wolnego miejsca. Raport 17/17 PASS dawał przez to nadmierne poczucie kompletności sprawdzenia.

R2 przechodzi niezależnie powtórzony DRC. Nie znalazłem powodu, żeby wracać do rozmieszczenia R1 albo ponownie zaczynać całą PCB. Przed eksportem produkcyjnym pozostają konkretne uzgodnienia montażowe i elektryczne opisane poniżej. Nie wykonano przymiarki ani pomiarów sprzętu.

## Co sprawdziłem samodzielnie

- Natywny KiCad 10.0.6, ponowne wypełnienie stref podczas DRC, kontrola zgodności ze schematem: **0 naruszeń / 0 niepołączonych / 0 rozbieżności**.
- Uruchomienie kontroli R2: **24/24 PASS**. Uruchomienie jej prób ujemnych: **6/6 wykrytych**; ograniczenie jednej z tych prób opisuję dalej.
- Własny odczyt długości ścieżek, liczby przelotek oraz przypisanych modeli 3D z obu plików `.kicad_pcb`.
- Przegląd rozmieszczenia, widoków miedzi, montażu, dokumentacji mechanicznej, zakupionych zamienników i kodu kontroli.
- Manifest R2: wszystkie 173 wymienione pliki zgodne. Hash PCB R2 zgadza się z jej raportem kontroli. W R1 nie zgadza się z manifestem tylko `output/previews/assembly.png`; sam plik PCB jest zgodny. Dlatego porównanie geometrii opieram na PCB, a nie na zmienionym podglądzie R1.

Dowody: [DRC R2](independent-drc.json), [własne pomiary](independent-metrics.json), [kontrole](checks-run.log), [próby ujemne](mutations-run.log), [migawka plików źródłowych](source-snapshot.json).

## R1 → R2: ocena zmian

| Obszar | Problem mojego R1 | Rozwiązanie R2 i ocena |
|---|---|---|
| Radiatory | Ścieżki i wylewki F.Cu pod przewodzącym profilem; izolację od miedzi zapewniała praktycznie maska. Kontrola samych kołków bez przypisanej sieci tego nie sprawdzała. | Obszary zakazu miedzi pod profilem, z otwartą wnęką tranzystora, plus kontrola rzeczywiście wypełnionych stref. **Zasadna poprawka konstrukcyjna.** B.Cu pod profilem jest oddzielona laminatem; izolacja tabów i śrub nadal wymaga prawidłowego montażu. |
| Orientacja TO-220 | Przy usuwaniu kolizji nadruku zniknęła informacja o stronie metalowego tyłu Q2. | Obrys, gruba linia strony taba oraz napis TAB przy Q2. **Zachować.** Nie wolno ponownie usuwać informacji montażowej tylko po to, żeby wyzerować DRC nadruku. |
| Rozmieszczenie funkcjonalne | Elementy związane ze sobą elektrycznie rozrzucone po wolnych miejscach; długie drogi odniesienia i sterowania. | Osobne, uporządkowane grupy AUX, komparatora, nadzoru, bufora i sterowania bramką. **Najważniejsza zmiana metody projektowania.** |
| Odsprzęganie | C10/C11 nie realizowały przypisania z BOM: U4 nie miał kondensatora blisko zasilania. | C10 przy U2, C11 przy U4; dodana kontrola sąsiedztwa. **Poprawne.** To przeoczyły zarówno kontrole R1, jak i pierwsza recenzja oraz pierwszy przebieg R2. Wymaganie musi trafić do planu rozmieszczenia, nie pozostawać tylko uwagą w BOM. |
| C6, D9 | C6 daleko od Q1; D9 daleko od Q2. | C6 we wnęce radiatora przy Q1 i D9 bliżej Q2. **Elektrycznie korzystny kierunek**, przy C6 trzeba potwierdzić montaż i dostęp sondy. |
| Wiązka J5 | Kotwa spełniała odległość 12,5 mm, ale wiązka była skierowana w głąb PCB, ku innym elementom. | Wyjście ku dolnej krawędzi, wolny pas przewodów. **Zachować.** W kolejnych PCB sprawdzać całą drogę do obudowy, nie tylko lut–opaska. |
| Oznaczenia serwisowe | Brak nazw sieci przy istotnych polach pomiarowych. | Dodano nazwy i numerację. **Poprawa.** Oznaczenia rezystorów pod korpusem pomagają przy montażu, ale po montażu będą zasłonięte; przy wolnym miejscu lepszy jest nadruk obok lub dodatkowy opis na spodzie. |

Wyniki własnego pomiaru długości ścieżek w plikach PCB, zaokrąglone do 0,1 mm:

| Sieć / miara | R1 | R2 |
|---|---:|---:|
| OV_REF | 107,1 mm | 11,5 mm |
| OV_SENSE | 51,4 mm | 23,7 mm |
| UV_SENSE | 78,7 mm | 28,2 mm |
| REF | 97,4 mm | 45,6 mm |
| BUF_BASE | 74,7 mm | 12,9 mm |
| OK | 210,4 mm | 103,0 mm |
| ENABLE | 124,2 mm | 133,3 mm |
| Suma poza BAT_FUSED, VS, DRAIN, VPROT i GND | 1894,4 mm | 884,6 mm |
| Przelotki | 11 | 3 |

Potwierdzam więc liczby Opusa. Są to sumy segmentów poszczególnych sieci, nie pomiar indukcyjności, pojemności ani odporności na zakłócenia. Wzrost długości ENABLE nie przekreśla poprawy. Nie należy optymalizować layoutu wyłącznie pod sumę długości lub liczbę przelotek.

Zalecenie lokalnego odsprzęgania i ograniczenia sprzężeń w otoczeniu komparatora ma też oparcie w [nocie TI LM2903, rozdział Layout](https://www.ti.com/lit/ds/symlink/lm2903.pdf). Ta nota nie jest jednak źródłem uniwersalnego limitu 5 mm od toru mocy ani 8 mm do kondensatora — takie limity są założeniem naszego layoutu i wymagają uzasadnienia dla konkretnego obwodu.

## Luka w procesie: świeży hash PCB nie oznacza świeżego DRC

`verify_pcb.py` czyta istniejący `verification/drc.json`, po czym zapisuje raport z hashem aktualnej PCB. Nie sprawdza, czy wczytany DRC został wykonany właśnie dla tej PCB i jej aktualnych reguł. To kod odziedziczony z mojego R1, pozostawiony w R2.

Sprawdziłem to doświadczalnie na dodatkowej kopii:

1. Zostawiłem zapisany czysty DRC z R2.
2. Poszerzyłem istniejący odcinek SAFE_N z 0,5 do 12 mm, celowo powodując kolizje miedzi.
3. `verify_pcb.py` nadal zwrócił **24/24 PASS** z hashem zmodyfikowanej PCB.
4. Dopiero nowy natywny DRC wykazał **37 naruszeń, w tym 18 zgłoszeń `shorting_items`**.

Dowód: [opis eksperymentu](stale-drc-evidence.json), [świeży DRC uszkodzonej kopii](stale-drc-fresh.json). To nie jest wada zwarciowa dostarczonej R2: jej oryginalny layout przeszedł mój świeży DRC bez naruszeń. Dokumentacja Opusa nakazuje powtórzenie DRC; luka polega na tym, że program sam nie wymusza tej kolejności.

W kolejnych wydaniach potrzebne jest jedno polecenie odbioru, które zawsze wykonuje nowy DRC, sprawdza jego treść oraz kojarzy wynik z PCB, schematem, regułami i użytymi bibliotekami. Sam kod zakończenia procesu KiCada nie wystarczy: w tej próbie wynosił 0 mimo wykrytych naruszeń.

Drugi szczegół: próba `probe_open` w R2 zmienia szerokość ścieżki do TP2, a nie przerywa połączenia. Potwierdza wykrywanie zmiany zablokowanej trasy. Należy ją tak nazwać i osobno przetestować rzeczywistą przerwę. Liczba wykrytych mutacji nie mówi sama, jakie awarie zostały pokryte.

## Co jeszcze doprecyzować w R2

**1. Przymiarka C6, TP1/TP2 i radiatora jest nadal potrzebna.** W PCB obu rewizji HS1, HS2 i C6 nie mają przypisanych modeli 3D; R27 również nie. Obecny render nie może więc dowodzić braku kolizji w najciaśniejszej części konstrukcji. Wystarczą proste bryły o rzeczywistych wymiarach, przekrój przez wnękę i przymiarka na wydruku 1:1. Sprawdzić także śrubę, narzędzie i możliwość wymiany C6. Nie trzeba modelować dekoracyjnie każdego rezystora.

Pętelki pomiarowe lub dostęp od spodu mogą rozwiązać problem dostępności, ale sposób pomiaru szybkiego VGS musi zachować krótkie połączenie pomiarowe. Samo dodanie długich przewodów do sondowania nie jest równoważnym rozwiązaniem. Warunek fizycznej przymiarki pochodzi już z pakietu R2; niniejsza recenzja nie oznacza go jako wykonanego.

**2. BAT_FUSED 3 mm nie jest automatycznym powodem do przebudowy.** Dla samego prostego odcinka 29 mm, szerokości 3 mm i nominalnej miedzi 70 µm rezystancja w temperaturze pokojowej wynosi około 2,4 mΩ: przy 5 A około 12 mV i 0,06 W. To rozsądna skala strat dla prototypu. Nie potwierdza jednak obciążalności całego toru, przewężeń, lutów ani zachowania podczas zwarcia. Bezpiecznik 5 A nie ogranicza prądu natychmiast do 5 A.

Przyjąłbym ten odcinek jako jawnie uzasadnione odstępstwo od wcześniejszej wytycznej ≥5 mm, z pomiarem temperatury podczas odbioru. Nie przedstawiałbym szacunku „+3°C” jako gwarantowanego wyniku. Jeśli proste przesunięcie elementu pozwoli uzyskać większy margines bez innych strat, warto je rozważyć; nie ma potrzeby przeprojektowywać całej PCB tylko dla jednej nominalnej szerokości.

**3. D4 i pętla szybkiego wyłączania wymagają konkretnego kryterium odbioru.** Skrócenie pętli przez C6 jest korzystne. Pozostają podane przez Opusa odcinki do D4: około 19 mm od G i 34 mm od S. Zdanie, że C6 przejmuje szybkie zaburzenia, a D4 dłuższe, jest uzasadnieniem koncepcji, nie dowodem zachowania kompletnego układu. Przy zamykaniu rozmieszczenia sprawdziłbym możliwość zbliżenia D4, a w odbiorze zachował pomiar VGS i czasu odcięcia przy skokach zasilania/obciążenia. Tego nie rozstrzyga sam DRC ani reguła odległości padów.

**4. Zakupione części powinny tworzyć jednoznaczny BOM montażowy.** Dokument Opusa uczciwie wykazuje zamienniki, ale PCB nadal przechowuje MPN i wartości z R3. Trzeba powiązać z wydaniem listę faktycznie montowaną: m.in. R8 221 kΩ zamiast 220 kΩ, tolerancje PR02 oraz producenta D3. Zachować historyczny BOM R3, dopisać zatwierdzony wariant montażowy i wynik oceny różnic. Zgodność obudowy nie zastępuje oceny parametrów elektrycznych; w tej recenzji nie wykonano ponownej kwalifikacji wszystkich zamienników.

**5. Limity w kontrolach powinny odpowiadać zjawisku.** Obecna kontrola C10/C11 sprawdza odległość do pinu zasilania, nie długość pełnej pętli wraz z powrotem GND. Kontrola odsunięcia wrażliwych sieci od mocy obejmuje ścieżki, a nie wszystkie pady i strefy. To użyteczne filtry błędów, ale ich opis i końcowa ocena nie powinny obiecywać więcej. Dla następnej PCB najpierw określić wymaganie, potem sposób jego sprawdzenia; nie dobierać limitów tylko do już wygenerowanej geometrii.

## Jak zmienić generowanie kolejnych PCB

**Największa zmiana: najpierw projekt rozmieszczenia i montażu, potem automatyczne trasowanie i raporty.** Proponuję sześć krótkich etapów, bez mnożenia dokumentów i obowiązkowych akceptacji użytkownika po każdym kroku.

| Etap | Co robię | Warunek przejścia dalej |
|---|---|---|
| 1. Jedna karta założeń płytki | Funkcje bloków, rzeczywiste MPN i gabaryty, prądy, złącza, orientacja, radiatory, kotwy, miejsca sondowania i naprawy. Kilka wymagających sieci opisanych osobno. | Wymagania z dokumentacji i BOM przeniesione do konkretnych elementów, stref i połączeń; rozbieżności zakupowe jawne. |
| 2. Rozmieszczenie bez tras | Najpierw mechanika i części krytyczne, potem elementy w grupach funkcjonalnych. Sprawdzam 2D oraz bryły wysokich i ciasno ustawionych części. | Brak kolizji; widać polaryzację, tor przewodów do krawędzi, dostęp sondy i narzędzi. Kondensatory przy przypisanych układach. Ten widok pokazuję użytkownikowi jako pierwszy namacalny wynik. |
| 3. Trasy krytyczne | Jawnie prowadzę moc wraz z powrotem, bramki, odniesienia, Kelvin i ważne sygnały cyfrowe. Oglądam obie warstwy i wypełnione strefy. | Każda ważna pętla ma uzasadniony przebieg; żaden kluczowy wymóg nie zależy od późniejszego autoroutera. |
| 4. Pozostałe połączenia i nadruk | Autorouter tylko dla pozostałych sieci. Po imporcie kontrola reguł projektu, połączeń i delty. Zachowuję znaczniki orientacji i opisy złącz. | Świeży DRC oraz ponowny przegląd gotowej PCB, w tym rzeczywistych powrotów GND i miejsc lutowania. |
| 5. Jeden automatyczny odbiór | Nowy DRC/parity, kontrole specyficzne dla płytki, kilka sensownych prób błędów; następnie eksport z tego samego pliku i manifest. | Wyniki związane z faktycznymi wejściami; nieaktualny raport lub brak wyniku daje błąd. Sprawdzone pliki i eksport muszą się zgadzać. |
| 6. Odbiór fizyczny | Przymiarka 1:1 istotnych części i dostępności; potem produkcja, montaż i uruchomienie samego modułu według jego procedury. | Oddzielnie zapisany wynik plików, przymiarki i pomiarów. DRC nie jest wynikiem testu sprzętu. |

Praktyczne zmiany w narzędziach:

- Zrezygnować z globalnego „najbliższe wolne miejsce” jako sposobu ustalania funkcjonalnego rozmieszczenia. Automat może pomóc wyrównać elementy lub wykryć kolizję, ale nie powinien przesuwać np. rezystora odniesienia między radiatory.
- Zastąpić ręcznie pamiętaną kolejność skryptów jednym sterownikiem procesu. Import SES nie może po cichu zmienić reguł na domyślne; stan reguł sprawdzać po imporcie. Każdy zapis przez API weryfikować ponownym odczytem istotnych sieci i geometrii.
- Traktować wygląd fizyczny footprintu jako część projektu: obrys korpusu, metal, orientacja, przestrzeń montażowa i serwisowa. Strefy zakazu miedzi muszą być zapisane w CAD, nie tylko narysowane w PDF. [Dokumentacja KiCad 10](https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html) opisuje obszary reguł i przypisywanie modeli 3D; sama obecność tych mechanizmów nie zwalnia z poprawnego zdefiniowania geometrii.
- Rozdzielić sprawdzanie zachowania zaprojektowanych tras od sprawdzania ich sensowności. Porównanie z `prerouted.kicad_pcb` wykryje zmianę trasy, ale zachowa także trasę zaprojektowaną źle.
- Widoki kontrolne opierać na geometrii z końcowego CAD. Pokazywać: rozmieszczenie, F.Cu z metalowymi bryłami/strefami, B.Cu z powrotami oraz zbliżenia ciasnych miejsc. Niestandardowy generator PDF może dodawać opisy, lecz nie powinien stać się drugim, rozbieżnym źródłem kształtu PCB.
- Po poprawce sprawdzać także najbliższe skutki uboczne: przeniesienie C6 → dostęp sondy; obrócenie J5 → pinout wiązki; zmiana radiatora → miedź, izolacja i narzędzia. Nie powtarzać bez potrzeby całej historii projektu.

Dla kolejnych modułów ta sama metoda ma obejmować ich własne punkty krytyczne: lokalne odniesienie i odsprzęganie ADC, pętle pomiaru prądu, połączenie CORE–DAQ płytka–płytka, a dla wiązek lutowanych kotwy 10–15 mm od lutów i wolną drogę przewodów. Nie przenosić bezmyślnie limitów długości z P01 na ADC czy interfejs cyfrowy.

**Najbliższy krok dla P01:** zachować R2, domknąć przymiarkę wnęki HS2 i zapis BOM montażowego, uzgodnić odstępstwo 3 mm oraz kryteria pomiaru układu bramki, a następnie wykonać eksport przez poprawiony przebieg odbioru. P07 pozostaje wstrzymana do sprawdzenia rzeczywistego modułu BTS7960. Niniejszy dokument proponuje zmiany procesu; nie wprowadza ich po cichu do plików R2.

## Identyfikacja materiału

- PCB R1 SHA-256: `80a4c95e0ff5e2c019273c9a992f9a2c6fb0794f7dc3ec098b12ed0d8eb02c3c`.
- PCB R2 SHA-256: `f521cea4317f678b49a8cacd4d964ecf1061ad9a222c7b0569255181bc6a620e`.
- Skrypty użyte wyłącznie do tej recenzji: `audit_pcb_r2_setup.py` i `audit_pcb_r2_metrics.py` w katalogu głównym przestrzeni roboczej Codex.
- Końcowe porównanie wszystkich plików oryginalnych pakietów potwierdziło brak zmian podczas recenzji: [wynik kontroli](source-unchanged.json).
- `input-R2` jest kopią roboczą. `stale-drc-fixture` i pliki prób ujemnych zawierają celowe błędy; **nie są materiałem do produkcji**.
