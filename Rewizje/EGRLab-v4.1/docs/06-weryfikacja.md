# Weryfikacja EGRLab v4.1

Data: 22.09.2026. [Zakres poprawek](00-zmiany-v4-v4.1.md).

## Wykonane testy

**44 testy Pythona — OK. 266 asercji C — OK.** Wyniki zapisano w `verification/`.

- Python: dotychczasowa analiza logów oraz nowe przypadki historycznych metadanych, ostrzeżeń w CSV/HTML i rzeczywistego grafu interlocku z mutacjami przewodów.
- Sterowanie: 107 asercji; profile/JSON/pomiary/triggery: 37; wymuszane błędy ADC: 93.
- Nowe kontrakty bufora zdarzeń: 29 asercji, rzeczywiste funkcje z podstawionym API FIFO/SD. Wpis krótki, granica 2047 B + NUL, odrzucenie przepełnienia i obcięcia, zwracanie wpisów po błędzie SD i przy błędnym rozmiarze. Serializatory summary/hotsoak wytworzyły pełne, poprawne JSON 503/292 B; null także sprawdzono ścisłym parserem. Nie testuje to schedulera ani samej biblioteki ringbuffer.

Host: TinyCC 0.9.27 z lokalnym nagłówkiem zgodności opisanym w [instrukcji odtworzenia](../verification/README.md). Firmware: ESP-IDF v5.4.3, commit `ea1c174c1cbb7348bd8ba0ff1eb306246938dd80`, Xtensa GCC `esp-14.2.0_20250730`.

| Wariant | Rozmiar aplikacji | Kompilacja i linkowanie | Hardware accepted |
|---|---:|---|---:|
|LOGGER|415 216 B|OK|0|
|TEST|415 184 B|OK|0|
|WIFI|967 648 B|OK|0|

Logi kompilacji nie zawierają diagnostyk `warning:`/`error:`. SHA-256 aplikacji i konfiguracje są w `verification/`. Format logów/NVS pozostaje 4, nazwa firmware w meta to EGRLab-v4.1. Nie dołączono obrazów do wgrania bez sprawdzenia posiadanego modułu.

## Kontrola dokumentacji i zakres dowodu

Sprawdzono strukturę CSV, komplet 64 pinów ADC w testach, XML schematów blokowych, lokalne odnośniki oraz niezmienność źródłowych v3, v4 i S1. Dołączone rysunki S1 są identyczne z wcześniej wydanymi. Lista nowych i zmienionych plików: `verification/changes-from-v4.json`. Poprzednie wyniki zachowano w `verification/history-v4/` jako historyczne.

**Nie uruchomiono firmware na ESP32 ani nie wykonano prób elektrycznych.** Kompilacja v4 nie ujawniła błędnej alokacji 2 MiB kolejki; ten przykład pokazuje granicę samego buildu. Kontrole grafu nie są ERC ani symulacją elektroniki. Brak pomiarów progów, czasów odcięcia, regeneracji, sekwencji zasilania, wpływu adapterów i odporności automotive/EMC.

Do odbioru 4.1 dodano start z buforem w PSRAM, przeciążenie krótkimi/długimi zdarzeniami i ponowne ARM po pauzie ADC/konfiguracji. Wypełnij [ODBIOR.md](../verification/ODBIOR.md) przed odblokowaniem TEST. Domyślne `EGR_HARDWARE_ACCEPTED=0` i `metric 0` pozostają.
