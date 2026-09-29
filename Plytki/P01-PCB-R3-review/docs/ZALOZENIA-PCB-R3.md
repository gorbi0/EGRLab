# P01 PCB-R3 - karta projektu przed trasowaniem

Punkt wyjścia: zweryfikowana PCB-R2 Opusa, schemat P01-R3. Format 160 x 120 mm,
dwie warstwy po 70 um, otwory i interfejsy pozostają zgodne z R2. Nie uruchamiamy
globalnego automatu rozmieszczenia ani ponownego autoroutingu sprawdzonych bloków.

## Decyzje rozmieszczenia

1. D4 przenieść do wnęki HS2, pomiędzy Q1 i C6. Katoda do SOURCE, anoda do GATE.
   Przewidywane pady: K=(113,08;26,50), A=(102,92;26,50) mm. Lokalna droga do
   G/S ma być <=8 mm na każdej gałęzi, bez powrotu przez odległą szynę VS.
2. C6 przesunąć do Y=32,1 mm, zachowując pad1 X=105,5 i pad2 X=110,5.
   Odległość padów C6 od odpowiadających G/S Q1 <=10 mm. Prześwit korpusów
   D4-C6 co najmniej 1 mm nominalnie; montaż D4/C6 przed Q1 i radiatorem.
3. TP1 SOURCE=(114,60;24,50), TP2 GATE=(101,40;24,50). Ścieżka do właściwego
   pinu Q1 <=5 mm. Podstawowy dostęp pomiarowy od spodu PCB, z opisami B.SilkS.
   Nie wymagać wkładania sond pomiędzy radiator, Q1 i C6 od góry.
4. Zachować zakazy miedzi F.Cu pod profilami radiatorów i izolację tabów.
   Dodać lokalne modele gabarytowe: radiatory, TO-220, C6 i duże THT.
   Modele to obrysy do przeglądu montażu, nie dokumentacja wykonawcza radiatorów.
5. Zachować funkcjonalne bloki R2, C10 przy U2, C11 przy U4 oraz wyjście J5
   ku dolnej krawędzi. Oznaczenia rezystorów udostępnić także od spodu.

## Moc i pomiary

BAT_FUSED: zachować odcinek 3 mm z R2, jako lokalne odstępstwo od wytycznej 5 mm.
29 mm / 3 mm / 70 um daje nominalnie około 2,4 mOhm w temperaturze pokojowej,
12 mV i 0,06 W przy 5 A. Nie jest to kwalifikacja całego toru; ocenić lutowanie,
przewężenia i nagrzewanie podczas odbioru. Bezpiecznik nie jest ogranicznikiem 5 A.

Kelvin LK1: pomiary bez prądu roboczego przez małe pady. Zachować termiki J7.
VGS mierzyć różnicowo między TP2 i TP1; SOURCE nie jest masą oscyloskopu.
Kryteria dynamiczne i termiczne pozostają z ODBIOR/METROLOGIA schematu R3.

## Kontrole przed wydaniem

- Przegląd rozmieszczenia i przekroju wnęki przed prowadzeniem nowych tras.
- Ponowny odczyt PCB po zapisaniu: sieci, pad geometria, nowe trasy, reguły.
- Jedno polecenie wykonuje świeży DRC/parity, kontrole i eksport pod jednym
  odciskiem wejść. Nie ufa wcześniej zapisanemu DRC ani samemu exit code 0.
- Próby rzeczywistej przerwy, zwarcia i nieaktualnego raportu na osobnych kopiach.
- Wydruk 1:1 i widok spodu wskazują stronę oglądania oraz skalę.
- BOM montażowy A1 jawnie wymienia faktycznie zamówione części i różnice od R3.

Przymiarka rzeczywistych części oraz pomiary pozostają do wykonania przez
budującego. Projekt i pliki przeglądowe powstają teraz; oznaczenie sprzętu jako
sprawdzonego wymaga rzeczywistych wyników. P07 nadal HOLD.
