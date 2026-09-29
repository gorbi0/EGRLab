# Kontrakt P05-R1

- AD7606BBSTZ lutowany bezpośrednio; osiem kanałów napięciowych. CH6 jest terminacją zera. Prąd jest mierzony osobno na P06/P07.
- Dwie warstwy PCB, montaż domowy, dostęp do punktów pomiarowych. Wyprowadzenia i funkcje interfejsów według kopii v6.1/P03 w `reference/`.
- CORE–DAQ bez kabla, para złączy kątowych w układzie koplanarnym. Fizyczne dopasowanie wymaga potwierdzenia przed produkcją.
- Pozostałe pięć wiązek lutowanych w PTH po stronie P05; kotwy 10–15 mm od lutów. Długości i drugi koniec w `docs/interfejsy.csv` oraz `docs/wiazki-BOM.csv`.
- DAQ_OK nadzoruje zasilanie. MEAS_EN nie włącza cewek przy niepoprawnym DAQ_OK. Gotowość ADC i ważność kalibracji pozostają osobnymi warunkami programu.
- Natywne ERC/DRC bez wyłączeń, porównanie padów z netlistą, niezależne reguły elektryczne, kontrole z celowo wprowadzonymi usterkami, przegląd PDF i odtworzenie PCB ze źródeł.
- Wydanie R1 jest przeznaczone do recenzji. Kryteria prób sprzętowych i integracji określają `docs/ODBIOR.md` i `docs/INTEGRACJA.md`. P07 pozostaje wstrzymane.

Instrukcja odtworzenia oraz wersje narzędzi: `verification/QA.md`. Ten katalog jest częścią pakietu także wtedy, gdy nie ma dodatkowych plików z wymaganiami.
