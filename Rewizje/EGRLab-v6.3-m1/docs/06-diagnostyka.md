# Procedury i plan porównania samochodów

Każda sesja: identyfikator auta, egzemplarza EGR, przebieg jeśli znany, data montażu zaworu, adapter, moduły, temperatura otoczenia, stan zimny/gorący, opis objawu, kody i freeze-frame z zewnętrznej diagnostyki. EGRLab nie odczytuje sam pamięci DTC i nie wykonuje adaptacji ECU. Nie zmieniaj dwóch rzeczy jednocześnie w porównywanych próbach.

## LOGGER

Najpierw L2, potem L1 z prądem: zapis zimnego startu, nagrzewania, stabilnej pracy i nawrotu objawu. Powtarzalna próba okolic 1500–1700 rpm z tym samym obciążeniem, biegiem i temperaturą ma większą wartość niż sam przegazowany silnik. Dojazd z uruchomionym zapisem, znacznik przy objawie (6.3-m1: krótkie naciśnięcie START / STOP, zdarzenie `button` + `mark`), zachowanie historii przed i po. Obsługę urządzenia organizuj tak, aby nie odciągała kierowcy od prowadzenia.

RPM: z potwierdzonego dekodera CAN albo odpowiedzi na żądanie innego przyrządu OBD. Bez takiego źródła traktuj zakres obrotów jako opis operatora; timestamp MARK nie jest dokładnym pomiarem obrotów. Nie przenoś niezweryfikowanych identyfikatorów ramek z innego rocznika.

## IDENTIFY i przygotowanie TEST

Komenda `logger`, następnie `identify`. Program pasywnie sprawdza sześć przypisań trzech przewodów 4/5/6; wymaga jednej stabilnej odpowiedzi przez 2 s, ma timeout. Oczekiwany feedback dla 28410-2A850 jest na pinie4; 5/6 identyfikowane jako referencja i masa. Niejednoznaczności nie rozstrzyga się podaniem zasilania na próbę. Porównaj widok gniazda, wyniki i adapter, zapisz profil. Dwie zwory adaptera T ustawiają własne zasilanie i powrót na rozpoznanych stykach.

Przepnij listwę według tabeli niżej (wszystkie pięć żył ECU odłączone), wybierz TEST (`bank 1`), `stop`, `test`. SENSOR_CHECK zasila tylko czujnik i sprawdza zakres oraz stabilność przed READY. M1 nie ma fizycznego ARM (6.1 / S1: „nowy ARM przed ruchem” nie dotyczy M1). Silnik pozostaje na pinach 1/3.

**6.3.1-m1 (M1-R1; recenzja M1-02 i M1-06):** nie ma adapterów z detekcją ani fizycznego ARM. Tryb TESTER to przepięcie na listwie X1 (SPECYFIKACJA M1, sekcja 5):

| Krok | Zacisk | Czynność (pakiet i zapłon wyłączone) |
|---|---|---|
| 1 | X1.5, X1.7, X1.8, X1.9, X1.10 | odłączyć i zaizolować **wszystkie pięć przewodów strony ECU** (P1, P3, P4, P5, P6); przewody zaworu zostają |
| 2 | X1.5 / X1.7 | IBT-2 M+ na X1.5, IBT-2 M− na X1.7 |
| 3 | X1.13 | przewód akumulatora auta odpięty; zworka X1.13 ↔ X1.3 (VMOTOR) — CH7 mierzy zasilanie mostka, zakres TEST 9,0–17,3 V (`config.ch7_source = vmotor_x1_3`) |
| 4 | X1.11 / X1.12 | SENS_5V do zacisku pinu zasilania czujnika, GND do zacisku masy czujnika |
| 5 | — | omomierzem przy odłączonych źródłach: żadna żyła strony ECU nie łączy się z X1 |

Powrót do LOGGER: zdjąć zworki (X1.11, X1.12, X1.13 ↔ X1.3), odpiąć IBT-2, podłączyć pięć przewodów ECU, X1.12 do masy auta, X1.13 do akumulatora. Rozkaz `test` jest odrzucany (`test_rejected`), gdy CH1/CH2, CH3–CH5 albo CH8 mają ponad 0,5 V — czyli gdy ECU nadal steruje silnikiem albo zasila czujnik. Przy zgaszonym zapłonie ECU nic nie podaje, więc kontrola go nie wykryje: przepięcie trzeba zrobić świadomie. W SENSOR_CHECK CH8 (SENS_5V) musi mieć 4,5–5,5 V i zgadzać się (0,3 V) z pinem uznanym za zasilanie. W stanach TEST każde naciśnięcie START / STOP to natychmiastowy STOP. LEARN dotyczy mapy pozycji testera, nie adaptacji zapamiętywanej przez ECU auta.

## MANUAL i LEARN

`manual duty czas_ms` — krótki, ograniczony impuls; maksymalnie 250 ms w jednym poleceniu. Start np. 0,05/20 ms, później według odpowiedzi zaworu. Sprawdź znak ruchu. Nie utrzymuj motoru na mechanicznym ograniczniku w celu „nauki”.

Zanotuj ratio bezpiecznie rozpoznanego zamknięcia/otwarcia, następnie `learn ratio_closed ratio_open sign` w READY. Wartości muszą spełniać warunki rozpiętości i nie być skrajnym odczytem czujnika. Sprawdź pozycje pośrednie. Brak LEARN pozostawia ratio dostępne; procent pozycji jest nieważny.

## SWEEP, FRICTION, CYCLE

`sweep`: seria pozycji w zakresie roboczym 10–90%; sprawdź płynność, powtarzalność ratio, prąd i opóźnienia. `goto 0.5` ustawia środek. `friction 1` i `friction -1`: narastający napęd z rozpoznaniem ruszenia; zapis metryki prądu jest ważny dopiero po odbiorze okna 20 ms. `cycle N`: powtarzanie, N≤200. Przy każdej próbie obowiązują prąd, czas, temperatura, sprzętowe blokady i sprawny zapis (6.3-m1: zamiast blokad sprzętowych programowe ograniczenie prądu z CH6 i watchdogi ESP32, M-06).

## THERMAL i HOT-SOAK

`thermal`: powtarzalny przebieg wraz z temperaturą, a nie automatyczny sterownik grzałki. `hotsoak okres_s liczba_punktow` uruchamia kampanię na stygnącym zaworze: okres 10–3600 s, 1–200 punktów. Przykład po LEARN i osiągnięciu READY: `hotsoak 60 10`; zakończenie `hotsoak_stop`. Porównuj prąd ruszenia obu kierunków, czas 10→90/90→10, napięcie zasilania i temperaturę korpusu.

Obecny aktywny profil ma limit TC1 do 60°C i zakres akceptacji elektroniki P01 do 50°C otoczenia. To zakres początkowy testera; nie jest specyfikacją dopuszczalnej temperatury zaworu w aucie. LOGGER może rejestrować wyższą temperaturę według zakresu termopary/modułu. Jeżeli objaw występuje poza zakresem aktywnego testu, pierwszą podstawą jest gorący log w aucie, a rozszerzenie temperatury testera wymaga potwierdzenia parametrów zaworu i odbioru profilu.

## Interpretacja zdarzeń

| Obserwacja w logu | Następny pomiar |
|---|---|
| Spadek referencji lub wzrost masy czujnika razem ze skokiem feedbacku | Złącza/wiązka/zasilanie; AUX jako dodatkowy punkt masy lub napięcia (M1 nie ma AUX — punkt dodatkowy tylko oscyloskopem) |
| Prąd rośnie, pozycja nie zmienia się | Porównanie mechanicznego obciążenia, tarcia i sygnału; samo utrzymywanie pozycji też może tak wyglądać |
| Napięcie na motorze bez spodziewanego prądu | Ciągłość uzwojenia/złącza, tor mostka, potwierdzenie oscyloskopem |
| Zmiana feedbacku bez odpowiadającego ruchu/prądu | Tor czujnika, referencja, masa, kontakt złącza |
| Zawór przechodzi test stołowy, problem pozostaje w aucie | Warunki obciążenia przepływem, układ dolotowy, inne sygnały i sterowanie; rozszerz pomiary |
| Problem dopiero po rozgrzaniu jednej płytki testera | Najpierw napraw/skalibruj interfejs, zanim przypiszesz efekt EGR |

Triggery „stall/open/ref/ground/jump” oznaczają kandydatów do obejrzenia, nie automatyczną diagnozę. Nie da się z samego napięcia mostka wyznaczyć żądanej pozycji ECU. Raw pozostaje podstawą analizy. Przy porównaniu pięciu aut zachowaj tę samą wersję adaptera/skal i opisz każdą różnicę.
