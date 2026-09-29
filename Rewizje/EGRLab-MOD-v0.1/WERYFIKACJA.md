# Weryfikacja podziału MOD v0.1

## Wykonano

- Przeczytano schemat S1 i dokumentację v4.1, w tym rzeczywisty przydział GPIO, MCP, kanałów ADC, zasilania i blokad.
- Przypisano wszystkie pozycje indeksu elementów S1 do modułów, adapterów, panelu albo pozycji zastępowanych przez PWR-THT. Przy U18 jawnie zapisano podział na trzy lokalne drivery.
- Dodano mapę 72 elementów PWR-THT do P01. F1 pozostaje przy źródle; dotychczasowe EVM i jego rezystory nie przechodzą do nowego podziału.
- Zachowano sąsiedztwo torów Kelvin/INA, ADC/filtrów i mostka/lokalnych elementów ochronnych.
- Sprawdzono, że proponowany pinout C-ADC zachowuje GPIO v4.1. Nowy sygnał na MCP.B7 wymaga zmiany kierunku portu i obsługi current_valid.
- Wyodrębniono zagrożenia powstałe przez rozdzielenie PCB: przerwanie błędu OC, brak zasilania modułu, zasilanie przez GPIO, konflikt MISO, pojemność na VPROT, spadki masy i indukcyjność przewodów.
- Sprawdzono podstawowe zalecenia producentów dla ADC, INA, buforów Ioff i dostępność dokumentacji rodziny Waveshare. Podane długości przewodów i wymiary płytek są założeniami tego projektu, a nie parametrami gwarantowanymi przez producentów układów.

Wynik kontroli pokrycia jest zapisany w `verification/podzial.json`. To kontrola kompletności przypisania, nie ERC schematu elektrycznego, analiza uszkodzeń ani odbiór sprzętu.

## Do zamknięcia w schematach poszczególnych PCB

1. Finalne numery styków i niezamienne złącza wszystkich wiązek, ich footprinty oraz widoki montażowe. IDC20 dla ADC jest propozycją kontraktu, nie zamówionym złączem.
2. Konkretne obwody READY i ich nadzorów na P02/P05/P06/P07/P08, okna napięciowe, opóźnienia startu, stany bez zasilania, połączenia do SAFE oraz pętle obecności. Sam opis READY nie tworzy zabezpieczenia.
3. Lokalny latch OC i bramki wyłączenia na P07. W v4.1 komparator sterował wspólnym SAFE_N; MOD wymaga dodatkowego lokalnego toru. Dotychczasowy test v4.1 nie dowodzi działania tej nowej funkcji.
4. Ochrona przejść między zasilaniem Waveshare i 3V3_IO. Koniecznie rozstrzygnąć bidirectional I2C, SPI MISO z trójstanem, OE i brownout. Nie kopiować bez zmian połączeń v4.1 i deklarować, że problem rozwiązał sam podział PCB.
5. Bilans mocy i pojemności po dodaniu lokalnych driverów, kondensatorów i buforów. P01 pozostaje projektem prototypowym z odrębnym protokołem odbioru; podział PCB nie stanowi potwierdzenia jego odporności automotive.
6. Kompletna lokalna masa, szerokości miedzi, drogi prądu, mocowanie radiatorów i odległości elementów termoczułych. Grube przewody omijające ścieżki nie zastępują mechanicznego odciążenia zacisków.
7. Ostateczne obrysy po ułożeniu realnych modułów, przekaźników i złączy. Wymiary w README są planistyczne.
8. Warianty firmware uruchomieniowego i docelowego MOD. Brak peryferium musi mieć jawne znaczenie, a atrapa nie może pozostawać w produkcyjnej ścieżce bezpieczeństwa. Nowy B7 nie może nadal być wyjściem.
9. ERC/DRC każdej PCB oraz kontrola całej wiązki jako osobnego obwodu. ERC osobnych kartek nie wykryje wszystkich pomyłek przewodów między nimi.

## Źródła lokalne

- `../EGRLab-v4.1/docs/01-projekt.md`
- `../EGRLab-v4.1/docs/03-uruchomienie.md`
- `../EGRLab-v4.1/docs/07-polaczenia.md`
- `../EGRLab-v4.1/hardware/pinout.csv`
- `../EGRLab-v4.1/hardware/ic-pins.csv`
- `../EGRLab-v4.1/schemat-S1/dane/indeks-elementow.csv`
- `../EGRLab-v4.1/firmware/main/board.c`
- `../EGRLab-PWR-THT-v1/README.md`
- `../EGRLab-PWR-THT-v1/hardware/components.json`

Źródła katalogowe są podlinkowane przy uzasadnieniach w README. Nie wykonano symulacji kompletnego urządzenia, projektów CAD ani nowych pomiarów sprzętowych. Wcześniejszych katalogów nie modyfikowano.
