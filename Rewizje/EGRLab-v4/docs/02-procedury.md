# Procedury diagnostyczne EGRLab v4

Cel: odróżnić usterki zasilania/masy/feedbacku/napędu/wiązki zależne od ciepła i osobno zbadać szarpanie1500–1700rpm. Dobry wynik stołowy nie wyklucza problemu występującego pod ciśnieniem spalin, podczas drgań lub przy pracy ECU. Nie zakładamy wspólnej przyczyny obu objawów.

## Przygotowanie

Najpierw odbiór z rozdziału03. Elektronika w kabinie albo na stole; w komorze silnika tylko odpowiednie przewody i izolowane termopary. Zapisz temperaturę otoczenia, AC ON/OFF, stan rozgrzania, numer zaworu/adaptera i odczytane DTC/freeze-frame z osobnego testera. Nie kasuj danych diagnostycznych przed ich zapisaniem.

Pierwsza sesja: L2 bez ruszania fabrycznego złącza, bo rozpięcie może zmienić opór jego styków. Potem L1 do prądu, z porównaniem wpływu dodanej wiązki. TEST tylko z wypiętym ECU, na zgaszonym silniku albo stole.

## IDENTIFY → TEST → LEARN

1. Podłącz L2/L1 w trybie kluczyka LOGGER. Konsola: `stop`, `bind VALVE01 ADAPTER01`, `bank 0`, `bypass 1` dlaL2 (dlaL1 bez mostka `bypass 0`), `logger`, `identify`.
2. ECU zasila sensor. Przez≥2s musi istnieć dokładnie jedna trójka: masa−0,2…0,3V, referencja4,5…5,5V, feedback0,2…4,8V względem masy. Timeout30s bez jednoznaczności nie uprawnia do TEST. Sprawdź `status`; indeks2/3/4 odpowiada OEM4/5/6.
3. `stop`, `save`. Wyłącz zapłon; wypnij LOGGER i fabryczne ECU z zaworu. Ustaw dwie zworki T zgodnie z tabelą07, sprawdź miernikiem, dopiero podłącz T. Powiązanie ID opisuje zestaw pomiarowy dla danego zaworu; nie zmieniaj ID między IDENTIFY i TEST tego samego zestawu, bo `bind` celowo kasuje mapę przy zmianie ID.
4. KEY TEST, STOP zwolniony, `test`. Następuje przełączenie bez motoru i200ms stabilnego SENSOR_CHECK. Zły sensor/pętla daje FAULT. Sam `test` nie uruchamia napędu.
5. Zasilacz motoru ograniczony do0,5A, `limits 0.1 0.5 60` w SAFE **przed** `test`. TC1 ważny. Fizyczny ARM; `manual 0.05 20`, obserwacja; następnie krótkie impulsy w obu kierunkach. Nie dobijać do krańca długim wymuszeniem.
6. Ustal powtarzalne ratio zamknięcia/otwarcia i znak otwierania. `learn 0.15 0.85 1` to wyłącznie przykład składni — wpisz własne liczby. |span|>0,2, oba ratio0,02…0,98, powtarzalność≤2%FS. Zacięcie może udawać kraniec; wymagane niezależne potwierdzenie mechaniczne.
7. `stop`, `save`. LEARN jest kalibracją EGRLab, **nie adaptacją ECU**. Zmiana mapy lub identyfikatora kasuje jego ważność. Nie ma automatycznego szukania twardych ograniczników.

## MANUAL / GOTO / SWEEP

`manual duty czas_ms`: znaki±, maks250ms; domyślny max_duty0,35, na pierwsze próby≤0,1. Motor musi być uzbrojony; każde naruszenie warunków kończy ruchem0 i FAULT.

`goto 0.1…0.9`: regulatorP Kp0,8, martwa strefa1%, potwierdzenie błędu<2% przez100ms. Timeout2s. `sweep`:10→20→…→90→80→…→10%, w punkcie300ms. Przerwanie zamiast omijania trudnego punktu. Surowe pomiary umożliwiają analizę przeregulowania i histerezy, ale firmware nie drukuje gotowego raportu wszystkich tych wskaźników.

## FRICTION

`goto 0.2`, potem `friction 1`; ponownie0.2 i`friction -1`. Powtórz dla0.5/0.8, po trzy razy, przy podobnym napięciu i temperaturze. Rampa duty0,01/50ms, ruch≥1% z potwierdzeniem20ms, ograniczenia10–90%, timeout2s. Po wykryciu ruchu duty jest zerowane podczas potwierdzenia; powrót sprężyny może przerwać potwierdzenie, co oznacza nieudany pomiar, nie „brak tarcia”.

Prąd zerwania to `sample_mean_20ms` z okna bezpośrednio przed pierwszym wykrytym ruchem. `metric 0` (domyślnie) powoduje `null`. `metric 1` wolno zapisać po porównaniu ze skopem dla rzeczywistych częstotliwości PWM, duty, kierunków, temperatur i zasilania. Średnia próbek i RMS próbek nie są automatycznie średnią/RMS fizycznego PWM. Jeśli aliasing uniemożliwia powtarzalność, pozostaw `metric 0`, a prąd odczytaj ze skopu. Triggery prądowe pozostają kandydatami do sprawdzenia.

## CYCLE / THERMAL / HOTSOAK

`cycle 20`:20 pełnych cykli10↔90%, maks200, postoje500ms. Obserwuj trend, nie próbuj „rozruszać” uszkodzonego zaworu przez długie przeciążenie. `thermal` wykonuje pojedynczy SWEEP w aktualnej temperaturze; nie steruje grzałką ani termostatem.

`hotsoak 180 12`: po zgaszeniu silnika i bez ECU, dopiero gdy **TC1≤60°C** oraz wszystkie warunki TEST są spełnione. Każda seria:50%, friction+,50%, friction−,10%,90%,10%. Po końcu serii odczekuje180s do następnej;12 serii trwa dłużej niż33min, zależnie od czasu ruchów. Pomiędzy seriami motor nie jest zasilany; latch ARM może pozostawać uzbrojony.

Każdy punkt zapisuje TC1/TC2, VPROT, oba prądy zerwania (lubnull), czasy komend10→90 i90→10 oraz ID kalibracji. Te czasy zawierają początek komendy/zwłokę sterownika, nie są laboratoryjnym czasem między przekroczeniami dokładnych progów10/90%. `hotsoak_stop` oraz fizyczny STOP przerywają także ruch trwającej serii.

| Wynik w faktycznie sprawdzonym zakresie, np.60→40°C | Interpretacja |
|---|---|
|Powtarzalne wydłużenie ruchu/skok prądu przy dobrej referencji i feedbacku|kandydat: mechanika, przekładnia, motor; potwierdź niezależnie|
|Skok napięcia feedbacku bez zgodnego ruchu|kandydat: tor czujnika albo styk|
|Wyniki płaskie i czysty ruch|brak odtworzenia usterki w tych warunkach; nie uniewinnia zaworu|
|Problem występuje dopiero powyżej60°C|v4 nie wykonuje tam aktywnej próby; obserwuj pasywny LOGGER podczas naturalnej pracy|

Nie podnosimy limitu do100°C na podstawie samej temperatury otoczenia. Na stole grzej kontrolowanym źródłem z niezależnym termostatem i pomiarem TC1; unikanie miejscowych przegrzań jest warunkiem porównywalności. TC2 może być cieplejsza niż TC1; nie utożsamiaj kołnierza z uzwojeniem.

## LOGGER — kampania w aucie

1. Zimny silnik: loguj od startu, zaznacz MARK przy szarpaniu1500–1700rpm. Kierowca nie obsługuje konsoli; oznaczenia robi pasażer lub przycisk zamocowany bezpiecznie. Powtórz porównywalne warunki biegu/obciążenia po rozgrzaniu.
2. Osobna sesja po rozgrzaniu: porównuj AC OFF/ON, napięcie instalacji, masę sensora, referencję, feedback, motor A/B oraz TC1/TC2. Zmieniają się też wentylatory/obciążenie alternatora; korelacja z AC nie dowodzi zwarcia wiązek.
3. AUX HI do rozpoznanego przewodu ECV, LO do badanego punktu masy względemB−. Oddzielne przejazdy dla dwóch punktów. Nie łącz masy sondy z punktem pomiarowym.
4. RPM: uruchom odczyt PID0C w osobnym skanerze. EGRLab tylko słucha odpowiedzi0x7E8–0x7EF. Brak odpowiedzi oznacza brak informacji, nie0rpm. Do porównania pozycji rzeczywistej z żądaną potrzebny jest oddzielny odczyt parametrów ECU; nie ma zmyślonego DBC.
5. Najpierw `inspect` (CRC/GAP/ID), następnie `scan`, raport i pełny eksport okna wokół MARK/trigger. Sprawdź jakość każdego kanału przed interpretacją.

Ratio=(feedback−ground)/(supply−ground). Pozycja=(ratio−closed)/(open−closed), bez obcięcia do0…1; ujemny span jest dopuszczony. Zachowaj też napięcia absolutne — ratio może ukryć wspólny zapad szyn. Ground warn50mV/event300mV, ref4,5–5,5V, feedback0,2–4,8V, jump5%/około1ms: to progi przyrządu, nie warunki nadania P0404 przez ECU. Własny szum i dryf zmierz przed użyciem warn50mV.

`stall` (prąd>0,3A i pozycja stoi200ms) może oznaczać normalne trzymanie pozycji. `open` (motor>2V, prąd<0,1A przez50ms) jest podejrzeniem przerwy wymagającym sprawdzenia PWM. W L2 oba kryteria są wyłączone przez nieważność prądu. Nieudana identyfikacja i brak danych nie są dowodem uszkodzenia EGR.
