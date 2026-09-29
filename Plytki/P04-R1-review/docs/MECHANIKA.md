# Montaż P04-R1 i przymiarka

PCB 160 × 120 mm, FR4 1,6 mm, 2 × 35 µm, soldermaska obu stron. M3 NPTH 3,2 mm w (5,5), (155,5), (5,115), (155,115) mm; pod podkładkami promień 4 mm bez miedzi. Prześwit ścieżek ≥0,25 mm, szerokość ≥0,30 mm; via 0,8/0,4 mm. Wszystkie elementy na górze.

Wybrany duży obrys odpowiada P01/P02 i upraszcza lutowanie oraz sondowanie. To nie jest projekt piętrowego stosu z P03. Zostawić co najmniej 25 mm wysokości nad P04 plus miejsce na wtyki i łuk przewodów; ostateczny dystans ustalić po przymiarce. Wszystkie złącza wyciąga się prostopadle do PCB, podtrzymując płytkę. Nie opierać sił wypinania na taśmie.

## Kolejność

1. Wydruk PDF strony montażowej 100%, bez dopasowania. Belka 100 mm i obrys muszą zgadzać się z linijką. Przyłożyć rzeczywiste elementy i wtyki.
2. R1–R38, podstawki U1–U7, małe kondensatory i testpady. Nie montować dodatkowych LED na SAFE_N.
3. Q1–Q3 i U11: zgodność oznaczenia oraz pinów. Delikatnie rozgiąć nóżki TO92 do rastra 2,54 mm, bez zginania przy obudowie. U11 ma inny układ funkcjonalny pinów niż tranzystory.
4. C1/C2: WIMA 1 µF 63 V PET, rozstaw 5 mm, korpus 7,2 × 5 × 10 mm. C3: 10 µF 50 V, Ø5 mm, raster 2 mm. Sprawdzić polaryzację C3.
5. J3–J8: sprawdzić stronę zatrzasku oraz pin 1 z rysunkiem producenta. Usunąć styki kluczy w IDC przed lutowaniem; ich pady pozostają fizycznie na PCB, lecz są elektrycznie NC. Wtyki otrzymują odpowiadające zaślepki.
6. U8–U10: 74LVC125AD SO14 na adapterze Kamami 575068, rzędy 15,24 mm, raster 2,54 mm. Sprawdzić omomierzem wszystkie 14 połączeń. Dolutować C15/C16/C17 między VCC(14) i GND(7) przy samym układzie na każdym adapterze, z krótkimi izolowanymi wyprowadzeniami. Te trzy kondensatory **nie mają miejsc na płycie bazowej**. Adaptery w dwie listwy żeńskie 1×7 2,54 mm; bez pomylenia ich z wąską podstawką DIP14 7,62 mm. Góra adaptera ma zostać dostępna do sondy i oględzin.
7. Wiązki H_LV04/H_SAFE zgodnie z opisem poniżej, dopiero potem układy w podstawkach po pierwszym sprawdzeniu zasilania.

## Końce lutowane

J1: cztery przewody AWG22, długość 200 mm od wyjścia z PTH do wtyku Mini-Fit 4p. Raster padów 3,5 mm, otwór 1,1 mm. J2: taśma 16 żył AWG28, raster żył 1,27 mm, długość 150 mm; końcówka żeńska IDC16 Au z kluczem 4. Na PCB są dwa rzędy padów 2,54 mm — rozpleść krótki odcinek i prowadzić żyły zgodnie z numerami, nie według intuicyjnego lewo/prawo wtyku.

W J2 żyły nieparzyste idą do górnego rzędu od lewej, parzyste do dolnego. J1 piny 1–4 rosną w prawo. Rysunek zawsze dotyczy **widoku z góry PCB**, nie widoku czoła wtyku. Czerwona krawędź taśmy = żyła 1. Po zacisku IDC sprawdzić każdą żyłę miernikiem. Pozycja 4 SAFE nie przenosi sygnału — nie łączyć jej z GND.

Dla obu wiązek dwa otwory NPTH 3,2 mm leżą na linii 12 mm powyżej pierwszego rzędu lutów. W SAFE drugi rząd ma odległość 14,54 mm od tej linii. Przewody wprowadzać od góry, lutować w otworach metalizowanych, pozostawić niewielki łuk bez naprężenia. Opaska 2,5 mm z miękką podkładką obejmuje izolację, nie gołą żyłę. Odcinek do kotwy nie jest zapasem do ciągnięcia. Pod opaską nie ma ścieżek ani wylewek na obu stronach. Połączenia J3–J8 pozostają rozłączne; ich drugi koniec lutowany jest na module będącym właścicielem wiązki.

## Punkty do zamknięcia przed zamówieniem PCB

| Kontrola | Wynik początkowy |
|---|---|
| J3 Würth 61201021621: raster, gabaryt i kodowanie zgodne z zakupionym wariantem; dokument wymiarowy 10p do dołączenia | NIE ZBADANO; karta 10p nie pobrała się, nie uznano jej za potwierdzoną |
| J4–J6 Würth 61200621621: otwory 1,2 mm; karta podaje piny 0,64±0,15 mm, zalecane otwory 1,1±0,15 mm | KARTA SPRAWDZONA; przymiarka NIE ZBADANO |
| J7/J8 Molex 39-29-9069 / 39-29-9109: Au, pionowe, kołki PCB; footprint serii 5566 A2, raster pól w rzędach 4,2 mm, odstęp rzędów ogonków 5,5 mm | WŁAŚCIWOŚCI KATALOGOWE SPRAWDZONE; potwierdzić rysunek ogonków/kołków i przymierzyć |
| Adapter 575068: 18×18 mm, 15,24 mm między rzędami i zgodność numeracji | WYMIARY PRZYJĘTE Z WCZEŚNIEJSZEGO PROJEKTU; przymiarka NIE ZBADANO |
| Podstawki DIP i listwy adapterów nie zachodzą na kondensatory | NIE ZBADANO |
| Dostęp do TP1–TP13 po włożeniu układów, złączy i wiązek | NIE ZBADANO |
| U11 MCP100-315DI/TO i Q1–Q3: rzeczywiste oznaczenia/wyprowadzenia | NIE ZBADANO |
| Średnice, lutowanie i próba pociągnięcia obu wiązek | NIE ZBADANO |

Model 3D jest poglądowy: część bibliotek nie ma korpusów 3D, adaptery są obrysami, kolor LED w renderze nie jest specyfikacją zakupową. Wiążące są BOM, footprint i przymiarka. Rezystory/układy mają referencje nadrukowane w obrysie korpusu, widoczne przed montażem i w PDF; po montażu do identyfikacji używać rysunku.
