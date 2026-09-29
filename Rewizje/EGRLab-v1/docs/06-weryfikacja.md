# Stan weryfikacji pakietu

Data: 2026-09-21. Rewizja A.

**Wykonano na komputerze:** dziewięć testów narzędzia do logów. Sprawdzają zgodność rozmiarów ABI, zapis/odczyt, CRC, wykrycie urwanego bloku, odrzucenie nieprawidłowej długości, obie polaryzacje sensora, stan UNKNOWN, eksport CSV i monotoniczność czasu. Wszystkie przeszły.

Przykład `examples/synthetic.egr` zawiera4000syntetycznych próbek, osiem kanałów,2kS/s i celowo zasymulowany krótki spadek feedbacku. Nie jest dowodem występowania takiego uszkodzenia w samochodzie. Czytnik potwierdza stały krok500µs oraz brak błędów CRC.

**Przygotowano, lecz nie uruchomiono:** testy logiki stanów w `tests/test_control.c`; projekt ESP-IDF. Brak lokalnego kompilatora C/ESP-IDF. Nie deklarujemy poprawnej kompilacji, działania peryferiów ani konkretnej przepustowości na ESP32 na podstawie testów Pythona.

**Nie wykonano:** ERC/DRC w EDA, routingu PCB, testów napięć, prądów, latencji, błędów sprzętowych, temperatury, EMC i impulsów automotive. Pliki CSV są listą montażową, a nie netlistą KiCad. Źródła dokumentacji producentów sprawdzono; nie zastępuje to odbioru zmontowanego urządzenia.

## Otwarte ryzyka techniczne

| Element | Co trzeba rozstrzygnąć |
|---|---|
| ADC20 kS/s | Osiem transakcji w hardware mode może przekroczyć50 µs; kwalifikacja lub szybszy wariant sterownika |
| Złącza OEM | Fizyczny numer obudowy, klucze i orientacja pinów przed zakupem |
| Limity zaworu | Brak potwierdzonych OEM prądów i temperatur; profil z ostrożnego LEARN i pomiarów |
| Automotive | Energia load dump, ujemne impulsy, masa, EMC i termika muszą być zbadane dla instalacji |
| CAN/RPM | Rok auta nie określa ID broadcast; bazowo brak TX, możliwy odczyt odpowiedzi zewnętrznego skanera |
| Pretrigger |10 s przy 2k;6,55 s przy 20k w tej implementacji; SD stall może nadpisać historię |
| SD | Brak automatycznej rotacji plików i gwarancji odzyskania FAT po zaniku zasilania |
| Safety | Projekt warsztatowy, bez deklaracji SIL/ASIL lub odporności na każdą pojedynczą awarię |

Wybór MCU: posiadany ESP32-S3 N32R16 V wystarcza do tej architektury. Zmiana MCU nie usuwa potrzeby prawidłowego front-endu, kwalifikacji SPI/SD i niezależnych zabezpieczeń.
