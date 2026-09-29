# EGRLab 4.1 — weryfikacja uwag Opusa do v4

Data: 22.09.2026. Rewizja poprawkowa, bez zmiany formatu logów i profilu (nadal 4). Oryginalne v3, v4 oraz schemat S1 pozostają zachowane. Nie wykonano uruchomienia sprzętu.

## Wynik przeglądu

| Uwaga | Ustalenie i poprawka |
|---|---|
| 1024 × 2048 B na zdarzenia | Potwierdzono błąd. Dodatkowo `xQueueCreate()` w użytym ESP-IDF 5.4.3 korzysta z **wewnętrznego RAM**, nie automatycznie PSRAM. Alokacja 2 MiB może zatrzymać start. Zastąpiono ją FIFO zmiennej długości z obszarem **256 KiB jawnie w PSRAM** i strukturą sterującą wewnętrzną. |
| Propozycja elementów po 256 B | Nie można skrócić wszystkich wpisów do tej długości: rzeczywisty serializator w próbie hosta wytworzył `summary` 503 B i `hotsoak_point` 292 B. Zachowano limit JSON 2047 B i osobną kolejkę `config` 1 × 2048 B z fsync/ACK. FIFO odkłada długość wpisu wraz z NUL, nie stałe 2048 B. |
| Puste wartości ze starych metadanych bez ostrzeżenia | Potwierdzono. Eksport i raport ostrzegają o braku `adc_config_ok`, `current_valid` i `learned`, z nazwą pliku `--meta` lub `config_id`. Nie przypisują brakującym deklaracjom wartości true. Test odtwarza format 2 + stare ręczne metadane. |
| Pozorny test interlocku | Potwierdzono. Nowy test przeszukuje graf przewodów z `connections.csv` i przyłączeń z `ic-pins.csv`, dodając styki zamknięte dla danej kombinacji. Sprawdza 16 kombinacji oraz wykrywa usunięcie każdego przewodu toru i obejście blokady LOGGER/pętli T. To kontrola topologii, nie analogowa symulacja ani pomiar styków. |
| ARM po zmianie konfiguracji | Potwierdzono brak wyjaśnienia. Pauza ADC zatrzymuje odświeżanie heartbeat; po wygaśnięciu monostabilnego zatrzask wymaga nowego fizycznego ARM. Nie każdy commit musi go wyzerować: bank daje 100 ms, włączenie sensora dodatkowe 100 ms, a zapis SD ma zmienny czas. Po `zero`/LEARN/zapisie także sprawdź status. Nie dodano automatycznego uzbrajania ani sztucznego heartbeat. |
| Umiejscowienie deadtime | Kod v4 już liczył pełne 5 ms od potwierdzonego zapisu INA/INB. Doprecyzowano procedurę: kill → zapis kierunku z mostkiem wyłączonym → minimum 5 ms → ewentualne zezwolenie/PWM. Nie ma gwarantowanych 5 ms przed zapisem kierunku. |
| AD7606B CONVST/WR | Potwierdzono w karcie producenta Rev. B, Table 9, str. 13: **9=CONVST, 10=WR**. Pinowa netlista v4 była poprawna; pozostał błędny opis GPIO13 w `pinout.csv`, teraz poprawiony. Dodano asercję dla pinu 9. |

## Pamięć i przeciążenie

Obszary dużych danych: RAW 8 MiB + zdarzenia 0,25 MiB = **8,25 MiB PSRAM**, zamiast żądania 8 MiB PSRAM i niewykonalnej kolejki 2 MiB w wewnętrznym RAM. To nie jest całkowite zużycie pamięci urządzenia: stosy, sterowniki, Wi-Fi i pozostałe obiekty zajmują dodatkowe miejsce.

FIFO to `xRingbufferCreateStatic(..., RINGBUF_TYPE_NOSPLIT, ...)` z `heap_caps_malloc(..., MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT)` dla danych. ESP-IDF obsługuje wielu producentów. Wywołania projektu są tylko z tasków; nie wolno użyć tego interfejsu z ISR ani przy wyłączonym cache. Każdy odebrany wpis jest zwracany także po błędzie SD. Przepełnienie, za długi wpis i błąd zapisu nadal unieważniają stan zapisu.

Narzut wpisu: nagłówek 8 B oraz wyrównanie długości z NUL do 4 B; przy zawijaniu może zostać niewykorzystany koniec bufora. Pojemność zależy od rozmiaru wpisów. Dla JSON 200 B jest to około 1200 zdarzeń, dla maksymalnych linii około 126–127. Nie ma gwarantowanych 36 s: czas zależy m.in. od natężenia CAN i opóźnień SD. Próbę obciążeniową trzeba wykonać na urządzeniu.

## Schemat S1 i źródła

Dołączono wcześniejszy komplet rysunków w `schemat-S1/`. Oznaczenie S1/v4 na rysunkach jest zachowane celowo — poprawki 4.1 nie zmieniają okablowania. W dokumentacji i BOM 4.1 uwzględniono doprecyzowanie OVP z S1: M5.R8=9,10 kΩ, M5.R3=38,3 kΩ, M5.R4=3,48 kΩ. Uzupełnienia elementów i połączeń są opisane w [uwagach S1](08-schemat-S1.md); przy składaniu korzystaj z całego kompletu S1, nie wyłącznie starej listy połączeń v4.

- [AD7606B Rev. B, Table 9](https://www.analog.com/media/en/technical-documentation/data-sheets/AD7606B.pdf): CONVST/WR.
- [Kod alokatora FreeRTOS w ESP-IDF 5.4.3](https://github.com/espressif/esp-idf/blob/v5.4.3/components/freertos/heap_idf.c): `portFREERTOS_HEAP_CAPS = MALLOC_CAP_INTERNAL | MALLOC_CAP_8BIT`. Sprawdzono również lokalną kopię tego tagu.
- [ESP-IDF 5.4.3: ring buffers](https://docs.espressif.com/projects/esp-idf/en/v5.4.3/esp32s3/api-reference/system/freertos_additions.html): zmienna długość, wielu producentów, narzut i zwracanie odebranych wpisów.

Wyniki bieżących testów: [weryfikacja 4.1](06-weryfikacja.md). Sam poprawny build nie wykrył błędnego rozmiaru poprzedniej kolejki i nie jest dowodem uruchomienia urządzenia.
