# Zmiany względem bazowej P09 i integracja firmware

P09-R1 zachowuje kontrakt LV09 i TEMP. Dodaje nośnik dla posiadanych modułów MAX31856 XU, dwa selektory VIN, niezależne punkty3Vo/FLT/DRDY, dwustronne buforowanie SPI z Ioff i dekoder CS dla wspólnego MISO. Taśmy mają luty PTH i kotwy na nośniku, wtyki na P02/P03. Gniazda kupnych modułów pozostają rozłączne. Rezystory są pojedyncze DIN0207.

W bazowym `board_temperature()` odczyt zaczynał się od0x0A, następnie rx[2:4] interpretowano jako temperaturę, a rx[5] jako fault. Według mapy MAX31856 są to przesunięte dane: rx[2] jest CJTL, a rx[5] jest LTCBL, nie SR. To błąd funkcjonalny niezależny od projektu PCB.

`firmware/P09-temperature.diff` i pełna kopia `firmware/board.c` wprowadzają wyłącznie:

- odczyt LTCBH/LTCBM/LTCBL z0x0C–0x0E i SR z0x0F;
- kontrolę CR0=0x91 i CR1=0x03 przed każdym odczytem, aby odłączony moduł z MISO=0 nie wyglądał jak poprawne0°C;
- poprawną konwersję liczby19-bitowej ze znakiem i LSB1/128°C;
- NAN/fault255 przy błędzie komunikacji, NAN przy fault czujnika;
- 300 ms oczekiwania po konfiguracji, przed pierwszym wynikiem;
- CS setup/hold po2 takty przy1 MHz i przerwy1 µs przed transakcjami. Oboma urządzeniami TC zarządza jeden task, jak w bazowym firmware.

CR0/CR1 nie są rejestrami identyfikacji urządzenia. Ich zgodność nie potwierdza autentyczności MAX31856 ani świeżości kolejnej konwersji. DRDY ma jedynie punkt pomiarowy. Zawieszony przetwornik wysyłający stale poprawną ramkę wymaga dalszej diagnostyki. Błędy i czas odczytu zachować w logu; diagnostyka termiczna nie może zależeć od fikcyjnego0°C.

Test hostowy kompiluje wyciętą rzeczywistą funkcję z dostarczonego `board.c`, z niezależnymi wektorami bajtów i atrapą SPI. 27 przypadków oraz trzy mutacje: zły adres, zły bajt SR, usunięta kontrola konfiguracji. To test funkcji, **nie kompilacja pełnego ESP-IDF ani test na sprzęcie**. Włączenie zmian P05/P08 do wspólnego firmware pozostaje osobną integracją. Nie zastępować nowszego `board.c` pełną kopią z tego pakietu; nanieść diff i rozwiązać ewentualne konflikty. Bazowe pliki nie zostały zmienione.

Przy odbiorze uruchomić firmware z TEMP włączonym i innymi niegotowymi podzespołami wyłączonymi w konfiguracji. Po pomyślnej kwalifikacji połączyć z SD i potwierdzić brak błędów magistrali. Nie używać tego pakietu jako gotowej scalonej wersji całego EGRLab.
