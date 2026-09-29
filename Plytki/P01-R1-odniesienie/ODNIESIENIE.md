# Odniesienie do recenzji Opusa — P01-R1

23.09.2026. Przeczytano `P01-R1-recenzja/RECENZJA-P01-R1.md`, kod modelu i jego
wyniki; porównano wskazane elementy ze schematem/BOM P01-R1 i dokumentacją
producentów Q1/Q2. Model Opusa uruchomiono ponownie — wydruk zgodny z recenzją.
Nie zmieniono recenzji, opublikowanego P01-R1 ani wcześniejszych wersji projektu.

**Decyzja: P01-R1 nie przechodzi do layoutu. Uwaga R1-01 jest zasadna. Proponowane
cztery wartości traktujemy jako wariant do dopracowania, nie zatwierdzoną poprawkę.**

## Ocena uwag

| ID Opusa | Ocena | Działanie przed następnym etapem |
|---|---|---|
| R1-01 | Przyjęta, blokuje layout. Dzielnik C5/C6 może otworzyć Q1 podczas szybkiego narastania VS mimo OFF. | Zmiana sterowania bramką, obliczenia tolerancji i dynamiki; następnie aktualizacja schematu, BOM, footprintów i testów. Wariant 22n/680n/47k/33R jeszcze niezamrożony. |
| R1-02 | Przyjęta, z doprecyzowaniem pomiaru. Samo włączenie zasilacza może zamaskować problem. | Udokumentowane zbocze na VS, VGS mierzone różnicowo, pomiar prądu gałęzi Q1 i VPROT; uwzględnienie drgań styków oraz ograniczenia energii źródła. |
| R1-03 | Przyjęta jako warunek mechaniczny przed Gerberami. | Średnica rzeczywistej odizolowanej żyły 2,5mm² z zapasem na cynowanie i tolerancję otworu; wpis do karty wiązki. Nie określa jej sama wartość przekroju. |
| R1-04 | Przyjęta jako brak w doborze złącza zasilania. | Wskazać konkretną część współpracującą z 1757019 oraz sposób mocowania po stronie źródła. Nie blokuje schematu P01. |

## R1-01: mechanizm jest rzeczywisty

C5=220nF łączy bramkę z wyjściem utrzymywanym przez C3 i dalsze kondensatory.
C6=47nF sprzęga ją ze źródłem. Dla bardzo szybkiej zmiany VS bramka nie nadąża
za źródłem; idealizowany podział pojemności daje przyrost VSG około 0,82 przyrostu
VS, zanim zadziała ograniczenie D4 i przepłynie odpowiedni prąd przez Q2/R27.
Q2 ma skończoną wydajność i czas odpowiedzi. Warunek statycznego OFF nie jest
tym samym co utrzymanie OFF przy takim zboczu.

Wcześniejsza kontrola autora nie obejmowała tego mechanizmu. ERC, identyczność
netlisty i testy mutacyjne pozostają poprawnymi kontrolami przeniesienia projektu
do CAD, ale ich dodatni wynik nie potwierdza działania dynamicznego.

Powtórzenie modelu daje m.in. dla R1 około 79,5A przy 0→14V/1µs oraz 193,3A przy
0→24V/1µs. To wyniki modelu z przyjętym źródłem i uproszczonym tranzystorem,
**nie przewidywanie gwarantowanego prądu rzeczywistego układu i nie wynik pomiaru**.
Wystarczają do zakwestionowania założenia OFF, bez traktowania liczby amperów
jako dokładnej. Model nie uwzględnia m.in. indukcyjności wiązki, pełnego modelu
D2 ani prądów pojemnościowych we wszystkich równaniach węzłowych.

## Uzupełnienia do proponowanej poprawki

Kierunek jest prawidłowy: zmniejszenie C5, zwiększenie C6, większe R21 dla
zachowania łagodnego startu oraz mniejsze R27 dla silniejszego wyłączenia.
Nie wystarczy jednak sprawdzić tylko nominalnych 22nF i 680nF.

### 1. Próg 0,8V nie jest spełniony przez wszystkie tolerancje ±5%

Dla szybkiego zbocza i prawie stałego VPROT właściwa postać uproszczenia to:

```text
ΔVSG ≈ ΔVS × (C5 + Crss) / (C5 + C6 + Ciss)
Ciss = Cgs + Cgd, a Crss ≈ Cgd
```

W obliczeniu pomocniczym przyjęto typowe Ciss=3,5nF i Crss=0,29nF z karty Q1.
Dla 24V wychodzi około 0,758V nominalnie. Przy C5 większym o 5% i C6 mniejszym
o 5% wynik wynosi około **0,835V**, już powyżej proponowanej granicy 0,8V.
To analiza granicznego podziału ładunku bez pomocy Q2, a nie symulacja konkretnego
zbocza 1µs. Pokazuje, że postulowana statyczna kontrola wymaga tolerancji i zapasu.
Przy pojemnościach ±10% wynik rośnie do około 0,919V.

Typowe pojemności samego MOSFET-a zmieniają się z napięciem; nie wolno traktować
ich jako gwarantowanych korzystnych składników marginesu. Również napięcie progowe
Q1 jest określone przy małym prądzie testowym i zależy od temperatury. Wynik modelu
„0A”, oparty na ostrym odcięciu poniżej Vt, nie jest fizyczną gwarancją braku prądu.
[Karta SUP53P06-20](https://www.vishay.com/docs/68633/sup53p06-20.pdf).

### 2. Czas 80µs pozostawia mały budżet na resztę toru

Wariant Opusa daje około **80,1µs od natychmiastowego przełączenia idealnych stanów
Q2/Q3** do VSG<0,5V. Kryterium odbioru P01 liczy natomiast 100µs od przekroczenia
progu napięcia, obejmując komparator, bufor i sterowanie tranzystorów.
Pozostaje około 20µs na pominięte opóźnienia i tolerancje. Nie można automatycznie
uznać całego kryterium za spełnione.

Model przyjmuje β Q2=60 również przy prądach kilkuset mA. Karta 2N5401YBU nie
gwarantuje takiej wartości w tym punkcie; minimalne hFE podano dla innych prądów.
Pomocnicza analiza wrażliwości daje ok.91,5µs dla założonej β=20 i 129,7µs dla
β=10. Te dwie wartości β **nie są ustalonymi granicami katalogowymi** — pokazują
zależność wyniku od założenia modelu. Nie kwalifikować Q2 samym porównaniem
chwilowego prądu z absolutnym limitem 600mA.
[Karta 2N5401](https://www.onsemi.com/download/data-sheet/pdf/2n5401-d.pdf).

### 3. Zakres zboczy musi odpowiadać zakresowi ochrony P01

Recenzja bada podłączenie 24V i skok 18→30V. W dokumentacji P01 występuje też
granica VS≤48V dla zdefiniowanych prób impulsowych. Próby do 24V nie zamykają
tej części wymagań. Trzeba opisać również czas narastania, impedancję i energię
wybranego impulsu; samo „VS≤48V” nie oznacza odporności na dowolny przebieg.

Dla ilustracji granicy modelu: w tym samym uproszczeniu, przy wymuszonym
0→48V/1µs i Vt=1V, wariant 22n/680n daje VSG≈1,50V i przewodzenie Q1.
Nie jest to symulacja całego wejścia z D1/D2 ani twierdzenie, że taki przebieg
wystąpi w samochodzie. Pokazuje tylko, że poprawka nie dowodzi OFF dla wszystkich
napięć, jakie wcześniej dopuszczono w opisie odbioru.

## R1-02: pomiar do doprecyzowania

Styk przełączający już ustalone napięcie źródła jest sensownym testem podłączenia.
Przyrząd musi jednak zarejestrować rzeczywisty czas narastania na VS, a nie tylko
moment włączenia styku. Ograniczenie prądu zasilacza i rezystancja dodatkowego
zabezpieczenia mogą spowolnić zbocze; trzeba zapisać je jako warunki próby.

Nie należy użyć samego kryterium „brak prądu wejściowego”: normalnie popłynie prąd
ładowania C1/C2 i zasilania AUX. Do wykrycia niepożądanego przewodzenia potrzebna
jest obserwacja gałęzi Q1, VGS i VPROT, z rozróżnieniem prądu kanału i krótkiego
prądu pojemnościowego. Kryteria amplitudy, ładunku i wzrostu VPROT trzeba ustalić
przed pomiarem. Pierwsze próby z atrapą obciążenia i kontrolowaną energią źródła.

## Konsekwencje dla procesu

1. E-01 pozostaje otwarte z R1-01 jako blokadą; M-01/B-01 nadal otwarte.
2. Następna rewizja dotyczy sterowania Q1 oraz wskazanych braków wykonawczych;
   nie wymaga przebudowy reszty EGRLab. P07 nadal wstrzymane.
3. Obliczenia i model muszą czytać wartości z bieżącego projektu, zamiast własnej
   stałej krotki. Dodać kontrolę tolerancji i próbę mutacyjną cofającą dobór do R1.
4. Aktualizować jednocześnie schemat, BOM, footprint C6, opis startu, odbiór i testy.
   Nie zmieniać zamrożonej bazy tylko po to, aby przeszło porównanie; planowane
   różnice mają być jawnie dozwolone i udokumentowane.
5. Po sprawdzeniu poprawki wykonać ponowną recenzję zmienionego toru. Dopiero
   potem layout, a po wykonaniu PCB — osobny odbiór dynamiczny na stole.

Pliki dowodowe obok: `powtorzenie-modelu.txt`, `sprawdzenie_recenzji.py`,
`dodatkowe-obliczenia.json`. Nie stanowią nowej wersji schematu ani pakietu PCB.
