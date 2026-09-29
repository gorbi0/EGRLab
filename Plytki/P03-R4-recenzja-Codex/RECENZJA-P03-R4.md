# Recenzja P03-R4 — 27.09.2026

**Werdykt: poprawka Opusa z U6 jest zasadna i wykonana lokalnie, ale nie zamyka całego toru resetu. Nie wydawałbym jeszcze P03 do zamówienia. Potrzebna jest niewielka korekta doboru U4 oraz zamknięcie znanego tematu mechaniki P03–P05. Nie widzę powodu do ponownego trasowania całej płytki.**

To recenzja, bez zmian w schemacie, PCB i BOM. Źródło: `../P03-R4-review`. Sprawdzono także interfejs resetu w `../P04-R2.1-review/docs/parts.json`. Pomiary sprzętowe pozostają niewykonane. Obliczenia poniżej są oszacowaniami, a nie wynikami oscyloskopu.

## 1. U4 nadal otrzymuje zbyt wolne zbocze — poprawić przed zamknięciem

**Miejsce:** P03 U3 → SUP_RAW_N, R13, U4; `docs/ZASILANIE-RESET.md`, sekcja „Reset bez rozjazdu stanu MCP i ESP32”; schemat POWER.

U6 usuwa wolne zbocze na wejściu P04, lecz wcześniej w tym samym torze znajduje się **U4 SN74LVC1G07**, bez wejścia Schmitta. Jego wejście jest podciągane przez **R13 = 10 kΩ** po zwolnieniu wyjścia open-drain TPS3808.

TI wymaga dla U4 przy zasilaniu 3,3 V ±0,3 V szybkości przejścia nie gorszej niż **10 ns/V**. Sama typowa pojemność wejścia U4 wynosi **4 pF**. Już dla niej:

```text
τ = 10 kΩ × 4 pF = 40 ns
t(0,8 → 2,0 V) = 40 ns × ln[(3,3−0,8)/(3,3−2,0)] = 26,16 ns
średnio: 21,8 ns/V; lokalnie przy 2,0 V: 30,8 ns/V
```

Pominięto pojemność wyjścia supervisora, ścieżek i punktu pomiarowego, które dodatkowo spowalniają zbocze. Nie jest to dowód, że każdy egzemplarz będzie generował zakłócenia, ale nominalne oszacowanie już nie spełnia wymagań wejścia. U6 umieszczony dalej tego nie naprawia. Możliwy skutek to zakłócenie resetu lub dodatkowy prąd bramki w trakcie przejścia. [TI SN74LVC1G07, warunki pracy i charakterystyki elektryczne](https://www.ti.com/lit/ds/symlink/sn74lvc1g07.pdf).

**Rekomendacja:** zastąpić U4 układem **SN74LVC1G37 w obudowie DBV (SOT-23-5)**. Zachowuje nieodwracającą funkcję i wyjście open-drain, dodając wejście Schmitta. Rozkład pinów jest ten sam: 1 NC, 2 A, 3 GND, 4 Y, 5 VCC. Karta dopuszcza 100 ms/V oraz prąd wyjścia 32 mA przy 3 V, zatem istniejący ogranicznik R34 pozostaje odpowiedni. Zamiana nie wymaga zmiany miedzi przy zachowaniu obudowy DBV. Dostępność i pełny kod zamówieniowy trzeba ustalić przed zamrożeniem BOM. [TI SN74LVC1G37, Rev. A](https://www.ti.com/lit/gpn/SN74LVC1G37).

Nie rozwiązywać tego przez samo zmniejszenie R13: karta TPS3808 wymaga rezystora podciągającego nie mniejszego niż 10 kΩ. [TI TPS3808, sekcja 7.3.3](https://www.ti.com/lit/gpn/TPS3808).

Po zamianie poprawić także symbol/wartość, BOM, instrukcję montażu oraz testy, które obecnie wymagają dokładnie LVC1G07 i niezmienionych wartości części R3. Wykazać, że zmiana względem R4 dotyczy tylko U4 i dokumentacji; nie wyłączać kontroli różnic.

## 2. Stan LOW przy wyłączonym CORE — poprawić budżet upływności P03–P04

**Miejsce:** P03 U6 → R41 → J4.15 → P04 J2.15, R17 = 100 kΩ, U9.5; `docs/ZASILANIE-RESET.md` i `docs/ZMIANY-R4.md`.

Dokumentacja uznaje Ioff U6 za wystarczającą podstawę stwierdzenia, że R17 zawsze ustali LOW. Ioff oznacza ograniczoną upływność, a nie idealną przerwę. Dopuszczalne moduły prądów to:

- U6 SN74LVC1G17: Ioff do 10 µA;
- P04 U9 74LVC125A Nexperia: prąd wejścia do 5 µA dla zakresu do 85°C, do 20 µA dla zakresu do 125°C.

[TI SN74LVC1G17](https://www.ti.com/lit/ds/symlink/sn74lvc1g17.pdf), [Nexperia 74LVC125A, tabela 6](https://assets.nexperia.com/documents/data-sheet/74LVC125A.pdf).

Konserwatywne sumowanie modułów, przy niekorzystnym kierunku upływności i R17 z tolerancją +1%, daje 1,515 V dla 85°C lub 3,03 V dla 125°C. **To budżet graniczny, nie przewidywanie rzeczywistego napięcia ani kierunku prądu niezasilonego U6.** Nie uzasadnia jednak deklaracji gwarantowanego LOW ≤0,8 V. Wystarcza już rozpatrzenie zakresu do 85°C; nie narzucam urządzeniu pracy przy 125°C.

**Rekomendacja:** zmienić **R17 na P04 z 100 kΩ na 10 kΩ**. Ten sam footprint; budżet spada odpowiednio do 0,152/0,303 V. Dodatkowe obciążenie aktywnego wyjścia U6 to około 0,33 mA. Zmianę zapisać również w dokumentacji i testach P04, nie tylko w opisie P03.

Nie stwierdzam, że obecna płytka samoczynnie załączy silnik — P04 ma dalsze warunki zezwolenia. Chodzi o poprawne i przewidywalne działanie tego konkretnego wejścia podczas zaniku zasilania CORE. Odbiór powinien obejmować CORE wyłączone, P04 włączone oraz obie kolejności rozruchu.

## 3. Dwie korekty obliczeń resetu — nie wymagają przebudowy PCB

**Miejsce:** `docs/ZASILANIE-RESET.md` i wiersz „Zbocze SUP_N_OUT na P04” w `docs/ODBIOR.md`.

**Poziom LOW SUP_N.** Twierdzenie „VOL ≤0,1 V przy 100 µA–0,7 mA” nie wynika z karty U4. Wartość 0,1 V jest specyfikowana przy 100 µA. Dla konserwatywnego obliczenia przyjąć 0,4 V, dostępne przy 3 V i obciążeniu 16 mA. Z dwoma nominalnymi podciągnięciami 10 kΩ i R34 = 220 Ω otrzymuje się SUP_N około **0,52 V**, a nie gwarantowane 0,25 V. Przy VDD = 3 V wychodzi około 0,51 V, nadal poniżej przyjętego w projekcie VIL MCP23017 = 0,2 VDD = 0,6 V. Jest zapas, ale mniejszy niż opisany. Przeliczyć całość dla finalnego U4 i tolerancji rzeczywistego modułu Waveshare.

**R41 i „36 pF”.** Obliczenie 220 Ω × 20 pF daje poprawnie τ = 4,4 ns. Granica około 36 pF wynika jednak z idealnego źródła i pojedynczego RC. Pomija rezystancję i skończoną szybkość wyjścia U6, niezerowe VOL oraz obciążenie sondą. Nie nazywać jej gwarantowanym limitem interfejsu. Sam czas 10–90% ≤17 ns też nie dowodzi dla dowolnego przebiegu spełnienia 10 ns/V w całym obszarze przełączania.

**Rekomendacja:** pozostawić R41 = 220 Ω jako wartość startową. Odbiór prowadzić na **P04 U9.5**, z docelową taśmą, uwzględnioną pojemnością sondy i właściwym pasmem pomiarowym. Sprawdzić monotoniczność, oba zbocza i szybkość przejścia przez obszar 0,8–2,0 V, a na wyjściu odbiornika brak dodatkowych impulsów. R41 zmieniać dopiero na podstawie pomiaru, ponownie kontrolując prąd zwarcia. To zadanie uruchomieniowe, nie powód do nowego layoutu.

## 4. Ocena punktów zgłoszonych przez Opusa

| Punkt | Ocena |
|---|---|
| Dodanie U6 Schmitta przed P04 | Zasadne; prawidłowa funkcja, pinout i kierunek sygnału. Pozostaje uwaga o wcześniejszym U4. |
| R41 w szczelinie między J4 i U12 | Akceptuję lokalizację i jawnie ograniczony wyjątek dla opisu na sitodruku. Nie znalazłem nowej kolizji na obejrzanych rysunkach. |
| HW_ARMED_CORE przez dwie przelotki | Akceptuję dla wolnego sygnału stanu; nie wymaga zmiany. |
| U6 zasilany z 3V3_CORE | Akceptuję architekturę, z uzupełnieniem budżetu upływności i zmianą R17 po stronie P04. |
| R41 = 220 Ω | Rozsądna wartość startowa; uproszczonego RC nie traktować jako gwarancji szybkości. |
| Lokalna zmiana miedzi R3 → R4 | Potwierdzona kontrolą geometrii: 3 odcinki usunięte, 25 elementów miedzi dodanych, 8 istniejących odcinków jedynie zablokowanych. |
| C15 i montaż U6 | Lokalny kondensator oraz droga masy są odpowiednie. Zachować opisaną kolejność: małe SMD przed J4 i listwami adaptera U12. |
| R14 CORE_LINK = 1 kΩ | Poprawka wcześniejszego problemu zachowana; kontrola funkcjonalna przechodzi. |

Drobna niespójność redakcyjna: `MECHANIKA.md` mówi o wszystkich rezystorach THT DIN0207, mimo że nowy R41 jest SMD 1206. Dopisać wyjątek dla R41.

## 5. Znany warunek przed zamówieniem: mechanika P03–P05

`docs/MECHANIKA.md` nadal wymaga zatwierdzenia przekroju i przymiarki pary kątowych złączy B2B. Kandydaci SSW-108-02-G-D-RA / TSW-108-08-G-D-NA oraz poprawna mapa pinów nie dowodzą zgodności wysokości rzędów i zazębienia. Genericzny footprint też tego nie rozstrzyga.

**Przed zamówieniem P03 i P05 ustalić dokładną parę, przekrój, odstęp PCB, pozycje rzędów i podparcie mechaniczne.** To otwarty punkt już uczciwie wskazany przez Opusa, a nie nowa wada R4. Nie oznacza automatycznie konieczności zmiany footprintów — rozstrzygnie dokumentacja wymiarowa i przymiarka.

## 6. Weryfikacja wykonana w tej recenzji

Pracowano na osobnej kopii 170 plików zgodnych z manifestem źródłowym. Ponownie wyeksportowano netlistę ze schematu i uruchomiono kontrole z KiCad 10.0.6.

| Kontrola | Świeży wynik |
|---|---|
| ERC według konfiguracji projektu | 0 naruszeń |
| Schemat / nowy eksport netlisty | 430 pinów, 91 części, 132 sieci; PASS |
| Kontrole funkcjonalne | 53/53 |
| Mutacje funkcjonalne | 43/43 wykryte |
| Kontrole PCB | 30/30 |
| DRC, połączenia, zgodność ze schematem | 0 / 0 / 0 |
| Kontrola różnic R3 → R4 | Skrypt zgłasza 13/13; kontrolę nienaruszenia katalogu R3 pominął z powodu braku katalogu obok kopii. Osobno sprawdzono manifest rzeczywistego R3 — wynik w `dowody/source-integrity-final.json`. |

Kontrole ERC/DRC korzystają z zapisanych ustawień projektu; listy wyłączonych kategorii są jawne w dołączonych JSON. „0” nie oznacza zbadania wszystkich możliwych problemów elektrycznych. Testy projektu sprawdzają między innymi topologię i zgodność danych; nie zastępują analizy zboczy, upływności ani fizycznej przymiarki.

Nie powtarzano pełnej regeneracji projektu ani 18 negatywnych prób layoutu — ich PASS pochodzi z raportów autora R4, nie z nowego wykonania. Obejrzano wyrenderowany arkusz POWER oraz strony montażu, miedzi górnej i dolnej, ze zbliżeniem okolicy U6/R41/J4. To przegląd zmiany i powiązanego resetu, nie ponowna pełna kwalifikacja wszystkich podsystemów EGRLab.

Dowody: `dowody/fresh-results.json`, logi poleceń, świeże raporty ERC/DRC i weryfikatorów, `dowody/obliczenia.json`, `skrypty/obliczenia.py`, obrazy przeglądu oraz manifesty integralności. SHA-256 badanego PCB: `bbf06e6663018034969ad666d6be14d7f58909125f61fdecb10de2694bf8f7ac`.

## 7. Minimalny zakres następnej poprawki

1. Ustalić dostępny wariant SN74LVC1G37 DBV i zmienić tylko U4 oraz powiązane dane/testy.
2. Osobno zarejestrować zmianę R17 = 10 kΩ w P04 i uzgodnić kontrakt resetu obu modułów.
3. Poprawić obliczenia LOW i zboczy oraz kryteria odbioru; nie dodawać nowych obwodów bez potrzeby.
4. Zamknąć mechanikę B2B P03–P05.
5. Powtórzyć kontrole po zmianach i wykazać zakres różnic względem R4. Dopiero wtedy przygotować CAM do zamówienia.

Do procesu warto dodać jedną krótką tabelę dla każdego łącza między modułami: nadajnik, odbiornik, zasilanie, stan bez zasilania, prądy upływu, rezystory ustalające stan i limit szybkości zboczy. Wystarczy przeliczać wiersze objęte zmianą. Właśnie tych parametrów nie sprawdzają obecne testy połączeń.
