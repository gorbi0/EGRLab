# Założenia aktualne

Prototyp ma ustalić przyczynę nawracających usterek przypisywanych EGR, porównując sygnały elektryczne i temperaturę w aucie oraz zachowanie zaworu na stole. Nie zakładamy z góry, że pięć podobnych przypadków ma jedną przyczynę. Zachowujemy LOGGER i TESTER, modułową naprawę, wymianę pojedynczych zespołów i możliwość dodania innej marki po wyborze konkretnego zaworu.

Szybkie napięcia mierzy AD7606B na P05, a prądy mają już własne MCP3201 na P06/P07. Log zapisuje różnicę czasu pomiaru, nie udaje jednoczesnej konwersji różnych ADC. Kelvin, odniesienia i szybkie obwody OC pozostają lokalne. I²C pozostaje lokalne na CORE; między modułami przesyłamy dane SPI oraz sygnały sprzętowych blokad.

Zapas toru mocy, złączy i przewodów nie podnosi limitów badanego zaworu. Zachowano ochronę P01, ograniczenia prądu, STOP i fizyczny rozdział TEST/LOGGER. Priorytetem jest etapowe uruchamianie i dostęp pomiarowy; urządzenie nie jest zoptymalizowane do produkcji seryjnej.

Dla kolejnego EGR klasy dc12_analog5 możliwy nowy adapter i profil po sprawdzeniu zasilania, prądu, pozycji i zakresów. Inna klasa zaworu wymaga nowego DRIVE/SENSOR/sterownika. Nie traktować samej zgodności liczby pinów jako zgodności elektrycznej. Wymiana modułu wymaga zapisania jego numeru, rewizji M2 i kalibracji. Opis bieżącego wykonania i granice gotowości są w README oraz docs/09–10.
