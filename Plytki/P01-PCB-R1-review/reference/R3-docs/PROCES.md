# Proces wykrywający błędy zachowania obwodu

R1 przeszedł ERC, ponieważ zapis wiernie odtwarzał błędny obwód. Zabrakło analizy
prądu pojemności i wydajności drivera w przejściu. Wprowadzamy trzy oddzielne
kontrole: poprawność zapisu, zachowanie elektryczne i pomiar prototypu.

## Kontrakt modułu — jedna strona przed schematem

Wpisać wejścia/wyjścia, stan bez zasilania, domyślne OFF, napięcie/prąd/temperaturę,
obciążenie i pojemność, czasy reakcji oraz punkty pomiarowe. Oznaczać źródło limitu:
GWARANTOWANE, TYPOWE, ZAŁOŻONE lub ZMIERZONE. Typowe hFE nie staje się gwarancją
przy innym prądzie. Każde ważne założenie trafia do konkretnej próby.

P01:5A po termice; start C≤220µF/I≤1,5A, KPWR OFF; prototyp0…50°C; OVP18V,
od VIN18,5V do VGS<0,5V≤100µs. VS48V to limit napięcia resztkowego impulsu,
nie jego specyfikacja ani deklaracja ISO.

## Tabela przejść — obowiązkowa przed PCB

| Przejście | Co trzeba policzyć lub zmierzyć |
|---|---|
| OFF→podłączenie | i=C·dV/dt, dzielnik pojemności zanim AUX/MCU zdąży zadziałać. |
| OFF→ON | Ładowanie wyjścia, obciążenie, VDS/ID/czas i SOA, nie tylko moc średnia. |
| ON→błąd | Q/I, RC, wydajność drivera, storage, osobny czas detektora i odcięcia. |
| Zanik jednej szyny | Prądy przez złącza/diody, zasilanie USB/3V3 nadal obecne. |
| Błąd→powrót | Brak samoczynnego ARM, stabilność zasilania przed KPWR. |
| Odbicia i rozłączanie | Kondensator naładowany, indukcyjność, masa odniesienia. |

P05 dodatkowo: nasycenie, settling ADC, wejście przy wyłączonym zasilaniu.
P07: recyrkulacja, hamowanie/PWM, martwy czas, blokada ECU — po zdjęciu HOLD.

## Obliczenia i model

Najpierw niezależny rachunek skrajności: dzielnik, Q/I, RC, C/L, prąd szczytowy,
napięcie i moc. Potem lokalny model tam, gdzie rachunek nie wystarcza. Sprawdzić
szybki i wolny proces oraz przeciwne tolerancje; pojedyncza zmiana Vth nie jest
pełnym modelem temperatury. Granic nieznanych nie ukrywać w wartościach typowych.

Model pobiera R/C i połączenia z eksportu FAKTYCZNEGO schematu. Zapisywać XML,
hash, talie, parametry, wersję solvera i przebiegi. Brak wektora, błąd zbieżności
lub urwany przebieg oznacza błąd testu. Podwojenie rozdzielczości czasowej sprawdza
numerykę; niezależny rachunek i pomiar sprawdzają sens fizyczny. Pominięcia modelu
mają jawne próby sprzętowe, nigdy automatyczny PASS.

## Regresja każdej znalezionej usterki

ID uwagi → przyczyna → poprawka → test → dowód → status. Stary wariant zostaje
jako negatywna kontrola: test R1-01 musi odrzucać R1 pod tym samym bodźcem.
Kontrole XML celowo zamieniają piny, wartości i MPN w kopiach. Porównanie formuły
z nią samą nic nie sprawdza. Po zmianie C5/Q2 ponawiamy macierz całej bramki,
powiązane czasy i interfejs SAFE, nie cały niezmieniony firmware.

## Zamrożenie i recenzja różnicy

Recenzent dostaje jedną paczkę z hashem, deltę, kryteria i otwarte pozycje.
Ma odtworzyć poprzedni błąd i zbadać wpływ poprawki, nie generować niekończącej
się listy sugestii. Rozdziela błąd, sugestię i brak dowodu. Statusy:
OTWARTE → POPRAWIONE_W_PROJEKCIE → SPRAWDZONE_NIEZALEŻNIE → ZMIERZONE.
NIE_DOTYCZY wymaga uzasadnienia. Druga opinia nie jest pomiarem.

- Do layoutu: zero nierozstrzygniętych błędów schematu, przejścia przeanalizowane,
  recenzja różnicy, konkretne części/mocowania; jawna lista przyszłych pomiarów.
- Do zamówienia: DRC, PCB↔schemat, odczyt Gerberów/wierceń, wydruk1:1 z częściami,
  dostęp do TP, śrub i kotew, przewężenia i powroty prądów.
- Do integracji: sam moduł przeszedł protokół na stole; dopiero potem dołączamy
  kolejny moduł i badamy interfejs oraz zanik jednej szyny.

Dla P01 wystarczą lokalne obliczenia/model, recenzja i dobrze określone pomiary.
Żaden zielony raport nie zastępuje następnego etapu. Nie obiecujemy projektu bez
wszelkich błędów; tworzymy powtarzalny sposób znajdowania ich przed kolejnym kosztem.


## R3 — obowiązkowe uzupełnienie procesu

1. Każda ochrona ma test początku błędu, trwania, powrotu i serii krótkich błędów.
   Oprócz rezystora używać modelu mocy stałej z jawnym UVLO. Sprawdzić zimny start
   i stan z naładowanymi kondensatorami. Kryterium ochrony mocy jest oddzielne od
   kryterium ciągłości pomiarów.
2. Przed zamrożeniem testu zdefiniować przyrząd, sposób odniesienia masy, punkty
   pomiarowe i niepewność. Sprawdzić instrukcję przyrządu. Wynik z marginesem
   mniejszym od niepewności ma status NIE ROZSTRZYGNIĘTO.
3. Zmiana C/R/tolerancji/footprintu wymaga ponownego zestawu podłączenie–start–OFF–powrót.
   Zmiana wartości dopuszczalnej wymaga decyzji z uzasadnieniem i zachowania starego
   wyniku; nie wolno usuwać niezaliczonej próby.
4. Przed layoutem dobór obejmuje zakup1–5szt., właściwy wariant obudowy, montaż,
   narzędzia i lutowanie. Stan sklepu zapisać z datą; nie jest gwarancją dostępności.
5. Testy mają czytać rzeczywisty eksport CAD. Nowe połączenie musi mieć mutację
   wykrywaną przez test: w R3 są to obejście LK1 i powrót do niewłaściwego C6.
6. Zamrozić schemat dopiero po przeglądzie delty; podczas layoutu zmiany wracają
   do schematu/BOM i odpowiednich testów. Po layout: DRC, pin1 złączy, rzeczywiste
   szprychy, brak obejścia bocznika, odstępy radiatorów i kontrola wydruku1:1.
