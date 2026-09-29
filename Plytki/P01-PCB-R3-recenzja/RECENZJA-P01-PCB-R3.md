# Recenzja P01-PCB-R3

24.09.2026 · recenzent: Claude (Opus 5.5) · przedmiot: `../P01-PCB-R3-review/`, czyli PCB-R3 Astry zbudowana na moim PCB-R2. Archiwum zgodne z `.sha256` (67ed7500…d9a6), hash płytki `5fbb1dc4…eb6b` zgodny z raportem kontroli pakietu. Pakietu nie zmieniano. Wszystkie przebiegi szły na kopii, a dowody leżą w `dowody/`.

**Wynik: R3 przyjmuję jako bazę do przymiarki 1:1 i eksportu.** Zmiany są lokalne, poprawne i dokładnie takie, jak je opisano. Zamykają mój otwarty punkt o D4 z R2 i luki procesu wskazane w recenzji R2 Astry. Przed przymiarką trzeba poprawić dwie rzeczy w dokumentacji. Żadna nie wymaga zmiany miedzi.

## Rejestr uwag

| ID | Waga | Krótko |
|---|---|---|
| PCB3-01 | przed przymiarką (montaż) | Po wlutowaniu C6 wkrętak nie dojdzie do śruby Q1 od przodu. Kolejność montażu R3 („D4 i C6 przed Q1/HS2”) tego nie uwzględnia |
| PCB3-02 | drobne (BOM A1) | U4 (MCP120-450) figuruje w BOM montażowym jako niekupiony, bo skrypt źle dopasowuje pozycję „P01 U4” |
| PCB3-03 | informacyjne | Wiersz „Serwis” w MECHANIKA: wymiana C6 i D4 nie wymaga demontażu HS2 |
| PCB3-04 | informacyjne (proces) | Kontrola „Four mounting keepouts” oblewa też przy usunięciu strefy HS2, bo liczy wszystkie obszary reguł. To kod z mojego R2 |

## Co sprawdziłem niezależnie

- **Świeży DRC** mojego wywołania `kicad-cli` z reguł projektu (klasa 0,30 mm, minimum 0,25 mm, nadruk 0,15 mm, bez wyłączeń): **0 naruszeń / 0 niepołączonych / 0 rozbieżności ze schematem**. Plik: `dowody/swiezy-drc-r3.json`.
- **Delta R2 → R3** (`dowody/delta-r2-r3.txt`, skrypt obok):
  - przesunięte są tylko D4, C6, TP1 i TP2;
  - usunięto 13 odcinków, dodano 15, a przelotki i strefy zostały bez zmian;
  - wszystkie zmienione odcinki leżą we wnęce HS2, w grzbiecie GATE, w gałęzi C5 i na szynie VS (B.Cu);
  - na nadruku zmienił się tytuł i doszło 38 opisów na spodzie.
- **Moje kontrole z R2 na płytce R3** (`dowody/kontrole-r2-na-pcb-r3.json`): 22 z 23 PASS; 24. kontrola, DRC, w tym trybie jest pomijana, a DRC puściłem osobno (wyżej). Jedyny FAIL to „zachowanie tras krytycznych R2”, a wskazuje on dokładnie 9 odcinków, które R3 zmienia celowo i opisuje.
- **Odtworzenie odbioru Astry u mnie:** `verify_pcb.py` daje 30/30 PASS ze świeżym DRC wewnątrz, a próby ujemne 5/5 wykrytych, w tym rzeczywista przerwa i zwarcie przy starym raporcie.
- **Liczby z ZMIANY-R3 potwierdzone:**
  - D4 K–S 5,25 mm, A–G 6,78 mm;
  - TP1/TP2 po 4,62 mm;
  - C6 9,8 mm od G/S Q1;
  - nominalny prześwit D4–C6 1,075 mm, a Q1–C6 ok. 4,9 mm.

## Ocena zmian R2 → R3

| Zmiana | Ocena |
|---|---|
| D4 we wnęce HS2, między Q1 a C6 | **Zasadne.** Droga ograniczenia VGS skraca się z ~19/34 mm (R2) do 6,8/5,3 mm. Katoda po prawej, do SOURCE, zgodnie z Q1 G-D-S |
| C6 o 2,1 mm dalej od Q1 | Akceptowalny koszt. Pętla G–S przez C6 rośnie z ~39 do ~49 mm², a C6 nadal stoi bezpośrednio pod G i S |
| TP1/TP2 od spodu, opisy S/G, „S IS NOT GND” | **Zasadne.** Usuwa mój problem dostępu z R2, bo pady są przelotowe. Opis ostrzega przed masą sondy na SOURCE |
| Uskok szyny VS na B.Cu do Y = 36 | Poprawny. Szerokość 5 mm zachowana, 0,5 mm od pada GATE C6, DRC czysty |
| Odcinek VS przy X = 93,8 | Skrócony do Y = 36,75, czyli tam, gdzie zaczyna się trasa VS z autoroutera. Poprawne sprzątanie po D4, bez wiszącej miedzi |
| Gałąź C5 na F.Cu do grzbietu GATE | Prościej niż w R2: jeden zablokowany odcinek zamiast czterech z autoroutera (po dwa na F.Cu i B.Cu) |
| Opisy rezystorów od spodu | Zasadne. To uwaga Astry do mojego R2 (opisy pod korpusem znikają po montażu) |
| Modele gabarytowe (77) | Użyteczne. Profil SK129 (42 × 25 × 63,5 mm, kanał 17 mm, otwór na 13,5 mm) zgadza się z wymiarami, których użyłem w R2. To z tych modeli wynika PCB3-01 |
| BOM montażowy A1 i pola Assembly* w PCB | Dobre rozwiązanie: schemat nominalny R3 zostaje, wariant montażowy jest jawny. Analiza R8/R27/R1/R23/D3 zgodna z moimi rachunkami. Jeden błąd, PCB3-02 |
| Odbiór: świeży DRC, wiązanie hashy wejść, próby rzeczywistej przerwy i starego raportu | Zamyka luki mojego R2 wskazane w recenzji R2. Sprawdzone doświadczalnie |

## PCB3-01 — dostęp do śruby Q1

Liczby z modeli R3 i dokumentacji R3 (`dowody/sruba_q1.py`, wynik w `sruba_q1.txt`):

- oś otworu TO-220/SK129 leży na wysokości 13,5 mm;
- czoło łba śruby wypada przy Y ≈ 23,9 mm (tab 1,27 mm + kołnierz tulejki ok. 1 mm + łeb M3 ok. 2,5 mm; to założenia);
- korpus C6 zaczyna się na Y = 28,5 mm i ma 13 mm wysokości, czyli kończy się 0,5 mm pod osią śruby.

Trzonek wkrętaka na osi 13,5 mm zahacza więc o C6, a między łbem a C6 jest tylko 4,6 mm. R3 każe wlutować D4 i C6 przed Q1/HS2, a potem skręcić Q1 z radiatorem przed lutowaniem nóżek. Przy dokręcaniu na płytce od przodu to się nie uda. **To samo było w moim R2:** tam C6 stał jeszcze bliżej, 2,5 mm od łba. D4 nie przeszkadza, bo leży do ok. 2,4 mm nad PCB.

Rozwiązanie bez zmiany PCB, do wpisania w MECHANIKA:

- **śruba od tyłu:** kanał za płytą HS2 i pas PCB za nim są wolne, bez elementów, co sprawdziłem na courtyardach. Wkrętak idzie od górnej krawędzi płytki, nakrętkę po stronie Q1 trzyma płaski klucz 5,5 mm wsunięty od góry kanału;
- **albo zmiana kolejności:** D4 → Q1 + HS2 dokręcone → C6. C6 (7,2 mm) wchodzi od góry w kanał szeroki na 17 mm i lutuje się od spodu.

Druga droga zostawia montaż zwykłym wkrętakiem, pierwsza pozwala zachować kolejność R3. Oba warianty trzeba potwierdzić na przymiarce z rzeczywistą tulejką i śrubą.

## PCB3-02 — U4 w BOM-MONTAZOWY-A1

W wierszu U4 jest „BOM R3 / PCB pads or local wire” bez dostawcy. Tymczasem MCP120-450DI/TO zamówiono w TME: wiersz rejestru ma pozycje „P01 U4, P02 U_SUP5” (`dowody/u4-bom-a1.txt`). `assembly_bom.py` porównuje oznaczenie z całymi członami po przecinku, więc „U4” ≠ „P01 U4”. Pozostałe wiersze P01 mają same oznaczenia, dlatego błąd dotyczy tylko U4.

Poprawka: dopasowywać po ostatnim słowie członu. Pole AssemblyMPN U4 w PCB zmieni wtedy tekst, więc trzeba powtórzyć `run_release.py`, bez zmian miedzi. Warto dodać kontrolę, że każdy element z pozycją w rejestrze zakupów ma w A1 źródło z rejestru.

## PCB3-03, PCB3-04

- **PCB3-03.** Wiersz „Serwis: wymiana C6/D4 po demontażu HS2” jest zbyt ostrożny. Kanał profilu jest otwarty od góry, więc C6, a za nim D4, da się po wylutowaniu wyjąć pionowo bez zdejmowania radiatora.
- **PCB3-04.** Próba `missing_heatsink_keepout` oblewa też kontrolę otworów montażowych, bo ta liczy wszystkie obszary reguł (= 6). To mój kod z R2. Nie zmienia wyniku, ale komunikat myli. Warto rozdzielić liczenie stref M3 i HS.

Drobiazg bez akcji: TP1/TP2 są teraz ok. 0,9 mm od ścianek kanału (w R2 1,4–1,6 mm). Radiator jest pływający, a dotknięcie jednego pola nie łączy dwóch sieci. Wystarczy obejrzeć przy przymiarce.

## Uwagi Astry do mojego R2

Przyjmuję je bez zastrzeżeń. `verify_pcb.py` czytał zapisany `drc.json` i nie wymuszał świeżego DRC. Próba `probe_open` zmieniała szerokość zamiast przerywać połączenie. Opisy rezystorów pod korpusem znikały po montażu. Brakowało modeli brył i jednoznacznego BOM montażowego. R3 usuwa każdy z tych punktów. BAT_FUSED 3 mm jako jawne odstępstwo z kryterium nagrzewania ≤ 20 K w ODBIOR-R3-DODATEK to lepsze ujęcie niż mój szacunek „+3 °C”.

## Zastosowanie poprawek: wydanie R3.1 (25.09.2026)

Pakiet `../P01-PCB-R3.1-review/` (+ `.zip`, `.sha256` 6b4c1044…9ee8) to kopia R3 z poprawkami. Pakiet R3 pozostaje nietknięty (zip nadal 67ed7500…). Przebieg `run_release.py --rebuild` odtworzył płytkę z R2 i dał: świeży DRC 0/0/0, **31/31** kontroli, próby ujemne 5/5. Porównanie z R3 obejmuje 2036 elementów: footprinty, pady, grafikę, ścieżki, przelotki, strefy z wypełnieniem, nadruk i tabliczkę. **Geometria jest identyczna.** Różni się tylko ukryte pole AssemblyMPN U4.

| Uwaga | Co zrobiono |
|---|---|
| PCB3-01 | MECHANIKA, ZAŁOŻENIA i PDF (s. 2 i 6): D4 przed Q1/HS2, C6 dopiero po dokręceniu Q1. Przy wlutowanym C6: śruba od tyłu kanału, nakrętka kluczem 5,5 mm od góry |
| PCB3-02 | `assembly_bom.py` dopasowuje po ostatnim słowie członu; U4 ma źródło TME. Skrypt przerywa pracę, jeśli część inna niż pole, zakończenie wiązki lub drut nie ma źródła w rejestrze |
| PCB3-03 | Serwis: C6 i D4 wymienia się przez otwarty od góry kanał, bez zdejmowania HS2 |
| PCB3-04 | Kontrola otworów montażowych liczy strefy M3 i HS osobno. Próba `missing_heatsink_keepout` oblewa teraz tylko kontrolę radiatora |
| **Dodatkowo (przeoczone w tej recenzji)** | BOM A1 zastępował uwagi BOM R3 uwagą z rejestru zakupów: w 70 z 89 wierszy znikały wyprowadzenia (U1 „nie pinout 78L05”, U3, U4, Q6, D2), polaryzacje „1=plus” i zalecenia montażu. Uwaga R3 zostaje, a uwaga zakupowa jest dopisana po „zakup:” |
| Nowa kontrola (31.) | BOM A1: każda część kupowana ma źródło w rejestrze, uwagi R3 są zachowane, a pola AssemblyMPN/AssemblyValue w PCB zgadzają się z BOM |

Obserwacja: `--rebuild` odtwarza geometrię 1:1, ale nie bajty pliku. Dwa kolejne przebiegi dały różne hashe PCB przy identycznej geometrii. Kontrole wiążą wynik z konkretnym plikiem, więc to nie jest błąd, ale hash PCB nie nadaje się do porównywania przebiegów.

## Następny krok

1. ~~Poprawić MECHANIKA (PCB3-01, PCB3-03) i `assembly_bom.py` (PCB3-02), potem powtórzyć `run_release.py`. Miedź się nie zmienia.~~ Zrobione w R3.1 (wyżej).
2. Zrobić wydruk 1:1 i przymiarkę według MECHANIKA R3, ze szczególną uwagą na Q1/D4/C6 we wnęce, śrubę i tulejkę, dostęp do TP1/TP2 od spodu, J6 i wiązki.
3. Eksport Gerber/Excellon z tego samego przebiegu odbioru.
