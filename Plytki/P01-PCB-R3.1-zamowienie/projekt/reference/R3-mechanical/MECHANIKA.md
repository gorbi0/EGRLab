# P01 R3 — wykonanie mechaniczne do layoutu

PCB160×100mm,2L,FR4 1,6mm,Cu70µm. Mocowania NPTHØ3,2:(5,5),(155,5),(5,95),(155,95).
Wokół mocowań Ø8mm bez miedzi i elementów. To założenia layoutu, nie Gerbery.

## HS1/HS2

Dwa **Fischer SK129-63STS**, pionowo, L63,5mm, profil42×25mm, Rth4,5K/W.
Wybrano STS z kołkami, nie niedostępny STIS. Źródło wymiarów: rysunek producenta
001020452 w reference/Fischer_SK129_STS.pdf. KołkiØ≤2,3mm, raster25,4mm,
wystają≤4,5mm. Footprint lokalny daje Ø2,8mm/pad4,8mm. Zostawić wolny obrys
46×30mm i wysokość75mm. Pady kołków są odizolowane od wszystkich sieci.

Tranzystor/dioda na środkowym żebrze, otwór na wysokości13,5mm od dolnej krawędzi
radiatora. Pozostałe fabryczne otwory18,3/25,4mm nie są otworami PCB.
Użyć M3×10, podkładki, nakrętki, izolatora TO-220 i tulejki dopasowanej do M3.
Izolator≤0,3mm; cienka pasta przy mice zgodnie z instrukcją izolatora.
Nie traktować anodowania jako izolacji. Po skręceniu sprawdzić izolację tab–radiator.

Nominalnie środek D2/Q1 względem środka HS jest x=0; płaszczyzna tab przy przedniej
powierzchni żebra. Footprint TO-220 ma tył obudowy y=-3,15mm od rzędu padów;
przy żebrze+0,9mm i izolatorze0,25mm wstępna pozycja rzędu padów wynosi y=4,30mm,
a pad1 x=-2,54mm względem osi radiatora. To wymiar montażowy do potwierdzenia
na rzeczywistym komplecie, nie tolerancja gwarantowana przez model KiCad.
Najpierw skręcić element z radiatorem, dopiero potem lutować wyprowadzenia bez
naprężeń. Niewielkie formowanie nóg jest dopuszczalne z dala od korpusu.
Radiatory opierają się na PCB i własnych kołkach; w obudowie dodać obejmę/podparcie
izolacyjne przeciw drganiom. Nie mogą wisieć na nogach półprzewodnika.

## Miedź i lutowanie

J7: cztery szprychy na warstwę, szerokość1,2mm, szczelina0,3mm. Ustawienia zapisano
w footprintcie. Przy wypełnieniu obu warstw sprawdzić, że wszystkie szprychy rzeczywiście
powstały i nie ma przewężeń. Wypadkowy przekrój8×1,2×0,07=0,672mm² na krótkim odcinku;
nie zastępuje to odbioru termicznego całej ścieżki. Lutować grotem o dużej pojemności
cieplnej; możliwość podgrzania PCB pozostaje. Nie obcinać żył dla dopasowania do PTH.

Tor mocy: szerokie pola, korytarz początkowo≥5mm na obu warstwach; ocenić także
przewężenia przy TO-220 i LK1. LK1: zwora z linki/drutu Cu2,5mm², odcinek około20mm,
uformowana P10, pozostawiona dostępna od góry. Trwały opór połączenia zmierzyć
czteroprzewodowo, docelowo≤0,5mΩ. Model przyjmuje0,2mΩ; bez weryfikacji nie
przypisywać mu dowolnej obciążalności impulsowej.

TP1 i TP2 umieścić przy nóżkach S/G Q1, docelowo≤5mm ścieżki. Para sense LK1
odchodzi od wewnętrznych brzegów padów mocy; nie pobiera prądu odbiorników.
Brak odgałęzienia VPROT przed LK1. Pętla Q2–R27–GATE–SOURCE krótka, C5/C6/D4
lokalnie. R1/R23 uniesione3mm i odsunięte od TL431/dzielników. D1 przy BAT,
D3 przy wyjściu, powrót ich prądów poza masą pomiarową komparatorów.

Wiązki: PTH i kotwy12,5mm od lutów; pas do opaski pusty. Przed Gerberami sprawdzić
wydruk1:1 i realne części. Kontrola radiatorów jest teraz określona wymiarowo;
przymiarka i ocena zamkniętej obudowy pozostają czynnościami fizycznymi.
