# Zakres zewnętrznego odbioru 6.1-rc1

Wykonany tutaj przegląd i testy są samokontrolą autora poprawek. Nie są nową recenzją Opusa. Do niezależnej recenzji przekazać cały ten pakiet, nie sam opis zmian.

1. Odtwórz baseline-fail oraz pełne testy aktualnego wydania. Sprawdź, że mutacje przewodów, masy i pull-down są wykrywane.
2. Sprawdź F01–F07 po pinach, po stronie obu modułów i w firmware. Oceń dodatkowy bezpiecznik VSENSE i zgodność przewodu/obudowy; LV ma pozostać wymienne.
3. W SFAULT sprawdź brak zasilania P08, przerwę żyły, FAULT przy włączonym SENSOR, brak automatycznego wznowienia oraz niedopuszczenie pętli EN/FAULT. Potwierdź świadomy podział: ograniczenie prądu lokalne, zatrzask błędu w programie, hardware ARM osobno.
4. Zweryfikuj AD7606B z dokumentacją producenta, w tym CONVST9, WR10, BUSY14, FRSTDATA15, SDI29, VDRIVE23, REGCAP36/39, REFSELECT34, AVCC i AGND. Porównaj rzeczywisty tryb SPI z pętlą odczytu w board.c.
5. P01: obejrzyj także niezmienione elementy. SOA/start, TVS, ESR LM2936, margines komparatora, progi i dryft, orientacja Q1/D2, odcięcie przy zaniku AUX5, separacja radiatorów. Wynik DC nie zastępuje testu dynamiki.
6. Zanim zatwierdzisz moduł do layoutu, zakończ kontrolę pin→pad, obudów części, wymiarów B2B i kotew. Arkusze EDA są importem, nie podpisanym schematem wykonawczym.

Wynik: lista konkretnych nowych usterek z lokalizacją, albo podpisany zakres „nie znaleziono nowych usterek w sprawdzonym zakresie”. Każde nowe znalezisko otrzymuje ID i test, bez ponownego pisania całego projektu. Pomiary fizyczne pozostają oddzielne.
