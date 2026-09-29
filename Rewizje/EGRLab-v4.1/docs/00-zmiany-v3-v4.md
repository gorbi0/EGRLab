# Zmiany v3 → v4

Data 22.09.2026. Podstawa: EGRLab-v3 i [raport OCENA-v3.md](history/OCENA-v3.md). Manifest oryginału: `verification/v3-source-sha256.json`.

| Uwaga | Poprawka | Weryfikacja |
|---|---|---|
| R01 | SUP_N oddzielne od SAFE_N; Q9 przenosi błąd supervisora. /CLR U7 z SUP_N, kondensator U7 między 14–15. | Lista pinów, test sieci; odbiór startu i timeoutu |
| R02 | Osobne styki sprzętowe i diagnostyczne; zewnętrzne pull-downy; B4=1 oznacza puste gniazda. | Tabela logiki, IODIRB=0x7F, GPPUB=0x0E |
| R03 | JSON 2048 B; config przez oddzielną kolejkę, ACK po fflush/fsync, publikacja ID dopiero po ACK. | Rzeczywisty serializer z długimi liczbami |
| R04 | Jeden manager: PAUSE/ACK przed przekaźnikami, ADC i metadanymi. | Przegląd kodu, próby odbioru opóźnień |
| R05 | ACK od właściciela ADC; osobny mutex całej konwersji; zakres UNKNOWN po błędzie; detektory tylko w akwizycji. | Testy błędów funkcji ADC; kompilacja ESP-IDF |
| R06 | Zero z nowego okna ≥1 s, zgodnego ID i banku, wszystkich ważnych próbek, bez podłączonego LOGGER. | Test summary i próba stanowiskowa |
| R07 | Brak config / ADC nieważny → brak wartości fizycznych. `learned=false` → brak pozycji. | Testy eksportera |
| R08 | Niefinitywne liczby zapisywane jako `null`; ścisły czytnik JSON. | Serializer i test NaN |
| R09 | Jeden AP/netif na boot; osobny task radia; STOP blokuje GPIO natychmiast z tokenem generacji. | Kompilacja Wi-Fi; cykle AP do sprawdzenia na sprzęcie |
| R10 | Strumieniowe segmenty, min/max wszystkich próbek, HTML offline, eksport okna, opcja `--full`. | Pojedynczy pik zachowany na wykresie |
| R11 | MCP w BOM, STOP NC+NO, piny logiki/ADC, komplet zworek/adaptorów, komendy kalibracji. | CSV i testy walidacji profilu |
| R12 | Zasilanie sensora ±10 V, feedback ±5 V, masa ±2,5 V; nasycenie unieważnia dany kanał. | Test zakresów i saturacji |
| R13 | Deadtime ≥5 ms od zakończenia potwierdzonego zapisu I²C. | Kod board_drive; pomiar na odbiorze |

Dodatkowo: metryka FRICTION `sample_mean_20ms` z domyślnie wyłączoną kwalifikacją; limit TC1 60°C bez deklaracji „oczyszczenia zaworu”; jawne ograniczenia RPM biernego; OBD 4/5/16 niepodłączone; rotacja RAW i zdarzeń co 1 GiB. Poprawiono WR na pinie10 AD7606B, RILIM TPS2553 do 232k i liczbę styków TEST do12. Zmiana dowolnej części mapy sensora unieważnia LEARN.

Zachowano oddzielny KCUR, OVP, okno 5V_A, AUX DPDT, sześć permutacji IDENTIFY, poprawne rejestry ADC i domyślnie zablokowany TEST. „Poprawiono” oznacza zmianę projektu/kodu; stan prób fizycznych jest oddzielnie oznaczony w rozdziale06.
