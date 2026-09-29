# Założenia mechaniczne P01-R1

Plan stref znajduje się w `P01-strefy.svg`. To rozplanowanie powierzchni, nie
rysunek wierceń radiatorów ani rozmieszczenie każdego elementu.

PCB 160 × 100 mm, FR4 1,6 mm, 2 warstwy. Propozycja miedzi: 70 µm na warstwę;
mało kosztowny zapas dla prototypu. Cztery otwory mocujące NPTH Ø3,2 mm:
(5,5), (155,5), (5,95), (155,95) mm względem lewego górnego rogu.
Rezerwacja wolna od miedzi i elementów Ø8 mm wokół każdego mocowania.
Wymiary do utrwalenia po przeglądzie; nie używać SVG jako pliku produkcyjnego.

## Radiatory i dostęp

Kandydat: dwa osobne **Fischer SK 129 63,5 STIS**, nominalnie 4,5 K/W w warunkach
producenta. Profil 42 × 25 mm, długość 63,5 mm; plan zakłada pionową długość 63,5 mm
i obrys w PCB 42 × 25 mm. Rezerwować dwa pola 46 × 30 mm oraz wolną wysokość
co najmniej 75 mm nad PCB. Przed przyjęciem obudowy potwierdzić tę orientację
na rysunku konkretnego wariantu TO-220 oraz sposób przykręcenia tranzystora.

[Karta Fischera](https://www.tme.eu/Document/3f44de1970b9ae8f6a3dac0e6790ddd5/SK12963.5STIS.pdf)
potwierdza profil i Rth; **położenie kołków oraz otworów nie zostało przeniesione
do footprintu**. To otwarta pozycja M-01 przed layoutem, nie „zatwierdzone wiercenie”.
Alternatywa mechaniczna: osobne radiatory przykręcone do wspornika obudowy,
pod warunkiem krótkich wyprowadzeń D2/Q1 oraz ponownego zatwierdzenia mocowania.

D2 tab=VS, Q1 tab=VPROT. Oba mocowania z izolacją elektryczną: podkładka termiczna
i tulejka śruby; sprawdzić omomierzem po dokręceniu. Nie polegać na anodowaniu
aluminium jako izolatorze. Nie łączyć różnych tabów wspólnym metalowym mocowaniem.
Jeżeli wariant STIS zawiera podkładkę, nie dokładać drugiej; tulejkę dobrać do śruby.
Radiator nie może wisieć wyłącznie na nóżkach TO-220.

## Prowadzenie płytki

Tor BAT_FUSED–D2–Q1–VPROT w górnej strefie; szerokie pola po obu stronach PCB,
krótkie połączenia i kontrola przewężeń przy padach. Startowe minimum korytarza
miedzi 5 mm; po trasowaniu obliczyć wzrost temperatury dla rzeczywistych długości,
miedzi i przewężeń. Sama szerokość nie nadaje płytce deklaracji „10 A”. Dopuszczony
prąd systemu pozostaje 5 A po odbiorze. Możliwość przylutowania równoległej linki
2,5 mm² na torze mocy przewidzieć jako rezerwę, nie obejście błędnego layoutu.

D1 tuż przy J7, D3 przy Q1/wyjściu, powroty TVS krótkie do GND mocy.
Masa komparatora/wzorca osobną drogą do punktu GND_STAR przy wejściu, bez prądu
transili w tej ścieżce. Nie tworzyć przerwy w masie pod sygnałami przez dzielenie
poligonu „na oko”. Q2/R27/D4/C5/C6 blisko Q1, pętla wyłączenia minimalna.
R1 i R23 unieść około 3 mm nad PCB i odsunąć od wzorca oraz dzielników.
U3/D6/R5–R11 nie umieszczać przy radiatorach. RV1 dostępny dla izolowanego wkrętaka.

Odległość rzędu lutów H_BAT/H_PG od kotwy: 12,5 mm, już zawarta w footprintach.
Przewody wychodzą w stronę kotwy; elementy nie mogą zajmować pasa między lutem
i kotwą. Dodatkowo pozostawić dostęp do zamka opaski i przestrzeń dla gięcia żył.
Duże transile podparte, bez naprężania obudowy podczas gięcia końcówek.

## Biblioteka a rzeczywiste części

TO-92 używa rastra szerokiego 2,54 mm: końcówki części o rastrze 1,27 mm trzeba
delikatnie uformować przed lutowaniem. Nie rozginać ich przy samym plastiku.
Przed Gerberami wydrukować stronę montażową 1:1, sprawdzić miarką skalę oraz
przymierzyć TO-220, transile P600, złącze Phoenix, kondensatory i radiatory.
Przymiarka nie zastępuje kontroli średnic otworów w pliku PCB.
