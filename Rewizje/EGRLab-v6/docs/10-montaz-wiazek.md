# Wiązki i bezpośrednie CORE–DAQ — M2

Rozstrzygająca tabela: `interfejsy.csv` (identyczna kopia w hardware). Kolumna **koniec_lutowany** podaje moduł i oznaczenie PTH, **wlasciciel_wiazki** wskazuje BOM, a **dlugosc_mm** jest długością gotową. Pełna numeracja żył pochodzi z wiring.csv. Koniec A jest rozłączalny przy CORE/SAFE/PSU/PANEL; koniec B pozostaje przy swoim module. Nie ma jednej nowej wielkiej płyty bazowej: funkcje rozdziału pozostają na istniejących P02/P03/P04/P11.

## PTH i kotwa

1. Po stronie modułu rozdziel koniec taśmy tylko tyle, ile potrzeba do wejścia w PTH. Odcinek od końca izolacji do pola nie powinien być odsłonięty poza obszarem lutu. Pin 1 oznacz na obu końcach i czerwonym skrajem taśmy. Numery oznaczają sygnały elektryczne, nie odbicie lustrzane wynikające z patrzenia od spodu.
2. Dla AWG28 przyjmij na początku otwór **0,8 mm po metalizacji**, pad 1,8 mm; dla AWG22/24 otwór 1,0 mm, pad 2,2 mm. Sprawdź wejście konkretnej ocynowanej linki przed wykonaniem PCB. Pola sygnałowe na rastrze 2,54 mm, dwa rzędy gdy odpowiada to IDC. Dla przewodu mocy 2,5 mm² oddzielne duże PTH: wstępnie 2,4 mm / pad 5,0 mm, raster co najmniej 7,62 mm, do weryfikacji przekrojem konkretnej linki. Te pola mają łączyć się z szyną mocy, a nie tylko pierścieniem uniwersalnej.
3. Kotwa ma **dwa otwory niemetalizowane**, nominalnie 3,2 mm dla opaski 2,5 mm; dla grubszej opaski powiększyć zgodnie z jej przekrojem. Środek poprzecznej linii kotwienia umieść **10–15 mm od rzędu lutów**, mierząc wzdłuż przewodu. Rozstaw otworów poprzecznie = szerokość taśmy/wiązki + około 4 mm. Brak miedzi przy otworach i pod naciskiem opaski. Na uniwersalnej wybierz płytkę z metalizowanymi otworami; kotwę wywierć w wolnym obszarze, usuwając sąsiednie pola.
4. Przewód leży na izolowanej powierzchni; miękka przekładka pod opaską. Opaska chwyta izolację, nie pobielone żyły. Docisk ma powstrzymywać przesunięcie, bez przecinania izolacji. Między kotwą a lutem mała, luźna rezerwa; żadnego zginania na granicy cyny. Nie zalewać całej końcówki klejem, który uniemożliwia naprawę.
5. Z drugiej strony IDC: jeden żeński wtyk zaciskany z odciążką. Na płycie bazowej pojedynczy box-header. Usuń tylko wskazany pin klucza i zaślep odpowiadający otwór wtyku. Żyłę tej pozycji pozostaw odizolowaną od obwodu, z zaizolowanym końcem. Inne NC pozostają bez połączenia. Nie łącz wszystkich pozycji NC razem.
6. Przed wpięciem sprawdź każdy tor 1→1 oraz zwarcia do obu sąsiednich żył i GND; wykonaj próbę poruszania za kotwą z omomierzem. W module nie może poruszać się odcinek zalutowany. Zdjęcia obu stron, długość i oznaczenie wiązki wpisz do odbioru.

Otwory przyjęto jako reguły do projektu mechanicznego, nie gotowe współrzędne wiercenia wszystkich płytek. Wiązka należy do modułu: przy wymianie odłączasz tylko wtyk po stronie bazowej i śruby modułu.

## LV, analog i moc

**Mini-Fit Jr 4,2 mm** zastępuje Micro-Fit: LV 4p, PG 6p, PANELCORE 8p, PANELSAFE 10p, TSENSOR 2p, TAPS 12p. Stosuj zgodne styki Au–Au; nie dobieraj jednego złoconego styku do cynowanego partnera. Każda gałąź LV ma ten sam pinout i może być zamieniana wyłącznie z inną LV. Pozostałe liczby pozycji różnicują funkcje.

Na uniwersalnej nie wciskaj złącza 4,2 mm w raster 2,54 mm. Bazowy wariant montażowy to **męski korpus kablowy zamocowany w uchwycie** przy krawędzi nośnika, z krótkimi ogonkami do PTH. BOM opisuje taki komplet jako gniazdo bazowe; jego korpus, komplet męskich styków i ogonki są jednym zespołem zakupowym. Długość ogonków ≤30 mm, dla TAPS ≤15 mm; dolicz je do długości całej drogi sygnału. Można kupić przewody ze stykami i przyciąć wolny koniec. Nie powstaje dodatkowe rozłączne połączenie. Wszystkie korpusy i opaski mocuje się do nośnika, nie pozostawia wiszących na lutach.

TAPS to pięć sygnałów przeplatanych pięcioma GND, dwie pozycje NC. **TAP_P5 i TAP_P6 są wejściami pomiarowymi, nie przewodami masy.** Sygnałów nie uziemia się przed rozpoznaniem. Wewnętrzny odcinek analogowy pozostaje krótki, 50 mm; P05 umieść przy panelowym wyjściu TAPS. Styki niskopoziomowe TAPS/AUX i READY: złocone, czyste i mechanicznie nieruchome. BNC dla zewnętrznych AUX/SCOPE pozostają, ponieważ są przydatne do sondowania. Styk w wejściu wysokoimpedancyjnym nie dodaje wprost całej swojej rezystancji do błędu napięcia; praktyczne problemy to przerywanie, nieliniowość zabrudzeń, upływ i termo-EMF. Lokalnego Kelvina bocznika nie wyprowadzamy przez żadne złącze.

**Moc:** BAT/SUPPLY/VMOTOR/ISERIES/TMOTOR: osobne linki 2,5 mm² z PTH po stronie B, wtyk śrubowy MSTB 5,08 mm ≥12 A po A. Zaciskać tulejkę; nie pobielać żyły pod śrubą. SUPPLY i VMOTOR mają identyczny pinout; pozostałe różną liczbę pozycji. Nie przenosić prądu motoru taśmą AWG28. Gotowy VNH5019 nadal korzysta ze swoich zacisków i listew na P07; pigtail kończy się na nośniku P07, nie na fabrycznej płytce. Analogicznie MAX31856 na P09 zostają w swoich gniazdach.

**Na zewnątrz:** DEUTSCH TEST/L1/L2, klucze A/B/C i złącza zaworu pozostają. Rezystory odczepów montować przy EGR/ECU przed długim przewodem. Ekran przewodów odczepowych połączyć z GND urządzenia tylko na końcu urządzenia; nie z nieustalonym pinem sensora. Ekran nie jest żyłą prądu silnika. Piny 12 GND w LOGGER służą odniesieniu/ekranowi zgodnie z mapą; TEST ma pin 12 NC. Dla ekranowania TEST użyć połączenia obudowy/ekranu przy panelu, bez zmieniania NC na masę. Bezpieczna długość i pasmo całego odczepu wymagają odbioru z faktycznym kablem: rezystancja źródłowa i pojemność kabla filtrują sygnał PWM.

## CORE–DAQ bez kabla

P03 J_DAQA: **Samtec SSW-108-01-G-D** (gniazdo PTH 2×8); P05 J_DAQB: **TSW-108-07-G-D** (wtyk PTH 2×8). 15 połączeń elektrycznych oraz pozycja 2 jako klucz: usunięty pin, zaślepione gniazdo. Numery pinów i sieci zachowano z V5. Nie ma dodatkowej taśmy ani „przedłużacza do pierwszych testów” w konfiguracji bazowej.

Obie płytki równoległe, z częściowym zakładem wyłącznie przy złączu na krawędzi; analog P05 odsunięty od ESP32, SD i anteny. Wtyk i gniazdo zamontowane na zwróconych do siebie stronach. Rozmieszczenie pinów na dolnym widoku jest lustrzane — continuity test pin 1→1 itd. ma pierwszeństwo przed podobnym wyglądem listew. Wysokość dystansów dobrać z rysunków złączy i próbnego zestawienia tak, aby styki miały właściwą głębokość wsunięcia i nie były naprężone; nie narzucać arbitralnie dystansu 10 mm.

Złącze nie jest elementem nośnym: po dwa punkty mocowania każdej PCB blisko styku i podpory dalszych krawędzi. Asymetryczny wspornik/prowadnica ma uniemożliwiać obrót oraz przesunięcie o jeden rząd/kolumnę; same nieosłonięte listwy i opis nie spełniają tego wymagania. Przed integracją wykonać przymiarkę wzajemnego położenia PCB, nośnika ESP i dostępu do lutów. Złącze i dystanse kupić przed ustaleniem finalnego layoutu.

3V3_CORE i 3V3_IO pozostają odrębnymi domenami; B2B nie zasila DAQ ani nie zwiera tych szyn. DAQ dostaje osobne LV05. Bufory Ioff i odsprzęganie pozostają. Bezpośrednie złącze skraca drogę; nie zwalnia z odbioru zboczy SCLK/CS/CONVST i pracy ze wszystkimi odgałęzieniami SPI.

M2 nie jest mechanicznie zamienne z M1. Nie podłączać dawnej sześciopinowej TAPS ani kabla DAQ do nowych gniazd przez przypadkową przejściówkę. Przy zmianie modułu stosować jego kartę, rewizję i kalibrację.

Źródła: [Samtec SSW](https://www.samtec.com/products/ssw-108-01-g-d), [Samtec TSW](https://www.samtec.com/products/tsw-108-07-g-d), [Mini-Fit Jr](https://www.molex.com/en-us/products/connectors/wire-to-board-connectors/mini-fit-connectors), [przewody Mini-Fit ze stykiem i wolnym końcem](https://www.molex.com/en-us/products/series-chart/215328).
