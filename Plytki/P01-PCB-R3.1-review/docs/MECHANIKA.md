# P01 PCB-R3 - przymiarka i montaż

**Wydanie R3.1 (25.09.2026):** zmieniona kolejność montażu C6 i opis serwisu wnęki HS2
(uwagi PCB3-01 i PCB3-03 z `Plytki/P01-PCB-R3-recenzja/`). Płytka bez zmian.

Status: **NIE ZBADANO rzeczywistymi częściami**. Nominalne gabaryty są uwzględnione
w PCB i lokalnych modelach. Brak wyniku w tabeli nie oznacza PASS.

Wydruk strony 2 PDF: 100%, bez dopasowania. Zmierzyć belkę 100 mm i wymiary
160 x 120 mm. Otwory M3: (5;5), (155;5), (5;115), (155;115), Ø3,2 mm.

| Kontrola | Co sprawdzić | Wynik |
|---|---|---|
| Radiatory | SK129-63STS, 42 x 25 x 63,5; kołki P25,4 / Ø2,8 PCB; brak naprężeń | NIE ZBADANO |
| Q1 i D2 | raster 2,54, A-K-A / G-D-S; tab i tulejka odizolowane od radiatora; dojście śruby Q1 od przodu tylko przed wlutowaniem C6, od tyłu kanału HS2 zawsze | NIE ZBADANO |
| Q2 | metalowy tył po stronie grubej linii i TAB | NIE ZBADANO |
| D4 | pasek katody po prawej, do SOURCE; korpus między Q1 i C6 | NIE ZBADANO |
| C6 | WIMA 7,2 x 7,2 x 13 mm, raster 5; nominalnie 1,075 mm od D4 i 4,85 mm od czoła Q1 | NIE ZBADANO |
| TP1/TP2 | swobodne dojście od spodu, krótkie końcówki sondy różnicowej; bez dodatkowych pętelek | NIE ZBADANO |
| Wiązka J7 | dwie linki 2,5 mm², wyjście ku górnej krawędzi, opaska 12,5 mm od lutów | NIE ZBADANO |
| Wiązka J5 | sześć AWG22 ku dolnej krawędzi, opaska 12,5 mm od lutów, wolne przejście do obudowy | NIE ZBADANO |
| J6 | pasowanie rzeczywistego wtyku, miejsce do rozłączania i wkrętaka od prawej | NIE ZBADANO |
| Spód | luty, kołki HS i kotwy nie dotykają podstawy; izolacyjne dystanse M3x10 | NIE ZBADANO |
| Serwis | dostęp do LK1 i możliwość wyjęcia P01; wymiana C6/D4 bez zdejmowania HS2: po wylutowaniu wyjąć pionowo przez otwarty od góry kanał, najpierw C6 | NIE ZBADANO |

## Kolejność montażu

1. Kontrola gołej PCB: netlist, brak zwarć, rozdzielenie DRAIN-VPROT bez LK1.
2. Niskie THT i układy, w tym D4 (przed Q1/HS2). **C6 jeszcze nie montować.** R1 i R23 unieść o około 3 mm.
3. Q2 zgodnie z TAB. Złożyć izolowane Q1/D2 z radiatorami i dokręcić śruby wkrętakiem od przodu;
   dopiero potem lutować nóżki i kołki, żeby dokręcanie nie obciążało lutów.
4. C6 wsunąć od góry w kanał HS2 (kanał 17 mm, C6 7,2 mm) i przylutować od spodu. Po wlutowaniu C6
   łeb śruby Q1 jest od przodu niedostępny: C6 ma 13 mm wysokości, a oś śruby leży na 13,5 mm.
5. Pozostałe duże elementy, złącze J6, wiązki i LK1 zgodnie z procedurą odbioru.
6. Opaski zakładać na izolację, z luzem między lutem a kotwą. Sprawdzić każdą żyłę.
7. Sprawdzić izolację radiatorów, dostęp pomiarowy i dopiero uruchamiać samą P01.

Dokręcanie albo wymiana izolacji Q1 przy wlutowanym C6: śruba od tyłu kanału HS2 (za płytą
radiatora nie ma elementów), nakrętkę po stronie Q1 trzymać kluczem płaskim 5,5 mm wsuniętym od góry.

H_BAT i H_PG mają po 200 mm gotowej długości. Składniki są w BOM-MECHANIKA.csv.
J5 od prawej na widoku z góry: 1=3V3_IO, 2=SAFE_N, 3=GND, 4=PG_SEND,
5=PG_LINK, 6=GND. J7: lewy pad BAT_FUSED, prawy GND. J6 od dołu: 1=VPROT,
2=GND, 3=NC. Nie odwracać pinoutu na podstawie lustrzanego rysunku spodu.

Modele VRML są uproszczonymi bryłami do przeglądu. Profil HS oparto o rysunek
Fischer 001020452 (reference/Fischer_SK129_STS.pdf); żebra i otwory w wizualizacji
są przybliżone. C6 ma nominalne gabaryty WIMA. Złącze pokazuje gabaryt korpusu,
nie wnętrze ani wtyk. Dla innych THT modele są przybliżonymi obrysami; nie służą
do automatycznego orzekania pasowania lub do wykonywania części mechanicznych.

Data: __________  Wykonawca: __________  Korekty: __________________________
