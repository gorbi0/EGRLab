# P02-R3 — formularz odbioru prototypu

*R3: wkładki F1–F4 dobrane, kwalifikacja przy zgaszonym silniku (punkt 8a), oczekiwany wynik po wyjęciu F1 (punkt 12), jasność LED (punkt 7).*

Wszystkie wyniki poniżej: **NIE ZBADANO**. Data: _______  Wykonawca: _______  Numery partii: _______

## Przymiarka przed zamówieniem PCB

- Wydruk 1:1, belka kontrolna 100 mm: _______
- C1–C3 rzeczywiste D35/H45 i raster 10 mm: _______
- U1/U2: raster 2,54, orientacja VIN/GND/VOUT: _______
- Mini-Fit Au, otwory ustalające, zatrzaski i wtyki: _______
- Adapter Kamami: 18×18 mm, rzędy 15,24; dostęp do C16 i pinów: _______
- R20: korpus 10×3,9 mm, rozstaw 17,78; brak kolizji F1/TP3: _______
- Mocowanie puszek do obudowy, wentylacja, osłona spodu banku: _______
- Wkładki Schurter SPT 5 × 20, 300 VDC: F1 0001.2507 T2A, F2/F3 0001.2504 T1A, F4 0001.2501 T0,5A; nadruk na korpusach zgodny z nadrukiem PCB (T2A / T1A / T500mA): _______

## Uruchamianie

1. Montaż bez C1–C3, zasilacz laboratoryjny, limit 0,2 A. Sprawdź polaryzację, wejście/wyjście TSR, U8 K/A/REF, brak zwarć. Nie podłączaj auta, ECU ani mostka.
2. Zwiększ limit odpowiednio do obciążenia. Zmierz 5V_SYS i 3V3_IO, działanie PSU_OK podczas powolnego narastania/opadania i wyłączania obu szyn. Sprawdź brak zasilania wstecz przez U5 przy zaniku jego VCC.
3. Na adapterze U5 zmierz napięcie i tętnienia bezpośrednio przy pinach 14/7; potwierdź montaż C16.
4. Test komparatorów wykonaj z bankiem niezamontowanym. Podaj symulowane HOLD_STORE z zasilacza o ograniczeniu prądu do punktu montażowego C1+, z GND wspólną. Przejrzyj wpływ tej konfiguracji na D1/F1 i przetwornice. Drugie zasilanie VPROT utrzymuj stabilnie, bez wymuszania napięcia na wyjściu aktywnego zasilacza.
5. Zapisz progi rosnące/opadające obu torów. Powtórz przy 0, 25 i 50°C, jeśli te temperatury mają być używane. Granice: bank wzrost 9,805…10,474 V, spadek 9,612…10,252 V; VPROT wzrost 11,810…12,623 V, spadek 11,573…12,349 V. Uwzględnij błąd miernika. Wynik: _______
6. Oscyloskop: wolne rampy 0,01/1/10 V/s; tętnienia 10/50/100 mVpp na źródle w pobliżu progu; obserwuj X, Y i OUT. Zanotuj szerokość zakłóceń powodujących przełączenie. Nie może być ciągłej oscylacji przy stałym wejściu. Czas reakcji, overshoot, zachowanie przy zanikach 5V/3V3: _______
7. Wyłącz i rozładuj. Zainstaluj bank, sprawdź F1, polaryzację, opaski/obejmy i osłonę. Ustaw VPROT=13,5 V. R17 na blasze zgodnie z TE. Zmierz ładowanie, TP3, R17 oraz stan LED po 15 s; LED1 (R16 470 Ω, ok. 2–3 mA) ma być widoczna przy świetle dziennym w kabinie. Powtórz start na zimno i przy C+20%/największej dostępnej pojemności. Wynik: _______
8. Zasil całą przewidywaną elektronikę (lub obciążenia na wyjściach). Zmierz sumę poboru na VLOG_RES, maks. 6 W z uwzględnieniem strat TSR. Odłącz VPROT: minimum 50 ms z VLOG_RES≥7 V oraz prawidłowymi szynami. Testuj różne proporcje obciążenia 5V/3V3. Wynik: _______
8a. Zgaszony silnik lub zasilacz 12,2 / 12,4 / 12,6 V na VPROT: zapisz, przy jakim napięciu LED się zapala (oczekiwane 11,81–12,62 V, nominalnie 12,25 V). Kwalifikacja ręczna przy zgaszonym silniku: przez 15 s TP1 ≥ 11,6 V i TP3 ≥ 9,7 V (multimetr 10 MΩ). Wynik: _______
9. Zmierz Ceff i ESR oraz maksymalny spadek bank→VLOG_RES przy podtrzymaniu; wymagane Ceff≥52,8 mF i spadek≤1,2 V. TP3 ma R20=1k: uwzględnij pasmo sondy przy ESR. Bezpieczny pomiar prądu wykonuj po stronie za F1, nie zwierając surowego banku.
10. Test TP3: przy ograniczonym zasilaniu sprawdź rezystancję ochronną 1k i brak obejścia R20. Przy 32 V zwarcie samego TP3 powinno dać <35 mA; obserwuj temperaturę R20. Nie zwieraj lutów C1–C3.
11. Tor VMOTOR: stopniowe obciążenie do 5 A, spadek J1→J2 i temperatura pinów, pola masy i wiązek. Zapisz czas testu i temperaturę otoczenia: _______
12. Bezpieczniki: potwierdź rozruch bez przypadkowego przepalania i koordynację zwarciową na stanowisku z kontrolą energii. Nie wykonuj swobodnego zwarcia akumulatora ani surowego banku. Wyjmij F1 przy naładowanym banku (VPROT 13,5 V): LED ma zgasnąć po ok. 1–2 min, bo odcięty bank rozładowują R1 i dzielnik R6/R7 (maks. ok. 115 s). Do tego czasu świeci mimo braku rezerwy — to oczekiwane opóźnienie wskaźnika. Zapisz czas: _______

Odbiór końcowy: _______  Załączone przebiegi/pomiary: _______  Pozostałe poprawki: _______
