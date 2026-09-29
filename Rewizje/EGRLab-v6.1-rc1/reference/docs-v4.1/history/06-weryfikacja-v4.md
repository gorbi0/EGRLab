# Weryfikacja EGRLab v4

Data: 22.09.2026. Rewizja zawiera poprawki R01–R13 z przeglądu v3. Zakres każdego testu i niezbędnego pomiaru rozróżniono w [macierzy zmian](00-zmiany-v3-v4.md).

## Wyniki wykonanych sprawdzeń

**Trzy warianty firmware skompilowano i zlinkowano dla ESP32-S3 z ESP-IDF v5.4.3.** Końcowe przebudowanie zmienionych modułów nie zgłosiło ostrzeżeń. Zlikwidowano m.in. problem przekazywania wskaźników do niewyrównanych pól rekordu RAW: sterownik ADC odbiera teraz wyrównane bufory, a rekord jest wypełniany po zakończeniu odczytu.

| Wariant | Rozmiar aplikacji | Build | Hardware accepted |
|---|---:|---|---:|
| LOGGER | 414 800 B | OK | 0 |
| TEST | 414 768 B | OK | 0 |
| WIFI | 967 248 B | OK | 0 |

Wariant Wi-Fi mieści się w domyślnej partycji aplikacji 1 MiB, z około 8% zapasu. Dodawanie większych modułów może wymagać zmiany tabeli partycji. Żadnego z tych obrazów nie uruchomiono na fizycznym ESP32. Konfiguracje, logi oraz skróty aplikacji są w `verification/`.

**40 testów Pythona — OK.** Obejmują format i CRC, uszkodzone bloki, wersje historyczne, mapowanie, zmiany konfiguracji w środku sesji, brak konfiguracji, nieważny ADC, brak LEARN, saturację, ścisły JSON, zachowanie pojedynczego piku przez agregację min/max, segmenty, eksport okna, walidację poleceń profilu oraz podstawowe kontrole zgodności dokumentacji pinów. Kontrole tekstu C są tylko dodatkiem do kompilacji.

**237 asercji C — OK:**

- 107 w 11 grupach czystej logiki sterowania: identyfikacja, zakresy, migawki, prąd, blokady, FAULT, FRICTION i limity.
- 37 w rzeczywistych modułach profile/jsonlog/measure/trigger/control: atomowe odrzucanie błędnych poleceń, zasilanie sensora ±10 V, długi config JSON z `null`, saturacja, okno prądu i summary z własnym ID/bankiem.
- 93 z wymuszaniem błędów w funkcji sterownika ADC: brak mutexu, włączona akwizycja, błędy kolejnych zapisów, błąd wyjścia z trybu rejestrowego, poprawne zakończenie i wariant legacy.

Kod hosta kompilowano TinyCC z opisanym nagłówkiem zgodności; firmware — oddzielnie oficjalnym GCC Espressif. Źródła, wyniki i polecenia odtworzenia: [verification/README.md](../verification/README.md).

Przykład `examples/` zawiera **4000 syntetycznych próbek formatu 4**, zmianę konfiguracji, krótki zanik feedback i skok napięcia masy. Eksport okna i raport offline powstały bez ostrzeżeń. Dane nie pochodzą z samochodu. Wykres pełnej rozdzielczości używa rzeczywistych znaczników czasu; podgląd całej sesji pokazuje obwiednię min/max.

## Kontrole pakietu

Sprawdzono parsowanie CSV i SVG, odnośniki do lokalnych plików dokumentacji, ścisłe parsowanie rzeczywistego config JSON oraz składnię JavaScript raportu offline. Listy pinów ADC mają 64 pozycje. Kontrole CSV potwierdzają spójność zapisanych założeń, **nie stanowią ERC schematu ani symulacji elektroniki**. Dwa rysunki obejrzano jako obrazy PNG.

Sumy SHA-256 źródłowego v3 zapisano przed pracą i porównano przy wydaniu. Wynik kontroli oryginału jest w `verification/v3-unchanged.json`. Plik `SHA256SUMS.txt` opisuje wyłącznie zawartość v4 i nie obejmuje samego siebie.

## Do wykonania na urządzeniu

Nie wykonano PCB, ERC/DRC, montażu ani prób elektrycznych. Nie potwierdzono działania peryferiów, przepustowości i jitteru na sprzęcie, pracy wielogodzinnej SD, progów zabezpieczeń, odporności automotive/EMC, mapy złącza konkretnego zaworu ani jego limitów fabrycznych. Źródła producentów podano w rozdziale 05; pomiar egzemplarza pozostaje konieczny.

Najważniejsze punkty odbioru: start i powrót watchdoga bez samouzbrojenia; fizyczny STOP podczas awarii I²C/SD; brak przełączania banku przed ACK akwizycji; brak publikacji config przed fsync/ACK; sekwencja niezależnych szyn zasilania bez zasilania pasożytniczego; OVP 17,5–18,5 V; deadtime liczony od zakończenia I²C; wpływ L1 na obwód ECU; kwalifikacja próbkowanej metryki prądu względem oscyloskopu.

`metric 0` oraz `EGR_HARDWARE_ACCEPTED=0` są stanami wydania. [Formularz odbioru](../verification/ODBIOR.md) nie zawiera fikcyjnych pomiarów. Brak usterki w warsztatowym HOT-SOAK nie rozstrzyga przyczyny P0404 ani szarpania w aucie.
