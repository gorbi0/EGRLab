# Stan weryfikacji pakietu v3

Data: 2026-09-22.

## Wykonano

**23 testy Pythona — wszystkie przechodzą.**

```text
python -m unittest discover -s tests -p "test_*.py" -v
Ran 23 tests — OK
```

**Testy formatu i narzędzi (17).** Zgodność rozmiarów struktur, zapis i odczyt, CRC, urwany blok, nieprawidłowa długość bloku, monotoniczność czasu, wszystkie sześć permutacji mapowania pinów, zgodność wstecz z plikami wersji 1 i 2, NaN zamiast fałszywego zera przy nieznanym mapowaniu, odrzucenie kalibracji o złej długości, eksport CSV, raport HTML, przegląd zdarzeń NDJSON z odpornością na uszkodzoną linię oraz z wykryciem konfiguracji o niepotwierdzonym ADC.

Trzy z nich to **regresje na błędy znalezione w v2**:

* zmiana zakresu w połowie sesji nie zmienia eksportowanego napięcia — to samo 25 mV po obu stronach zmiany, w granicach kwantyzacji danego zakresu (v2: ×4 w górę);
* zero prądu idzie za konfiguracją, nie za sesją (v2: 0,4 A przy faktycznym zerze);
* brak zdarzenia `config` dla użytego `config_id` daje **ostrzeżenie**, a nie ciche przeliczenie.

**Kontrola składni źródeł C (6).** `tests/test_c_sanity.py` sprawdza wszystkie pliki `firmware/main/*.[ch]` i `tests/*.c`: koniec wiersza wewnątrz stałej znakowej, niezamknięte literały i komentarze, bilans nawiasów klamrowych, okrągłych i kwadratowych, domknięcie wywołań `printf`/`snprintf`/`storage_event`, obecność `#pragma once` w nagłówkach, brak tabulatorów. Sprawdziłem, że **wykrywa dokładnie ten błąd, który uniemożliwiał kompilację v2** (`app_main.c:339`).

**Przykład `examples/samples.egr`** — 4000 próbek, osiem kanałów, 2 kS/s, format 3, ze **zmianą konfiguracji w połowie**: pierwsza sekunda na ±10 V, druga na ±5/±2,5 V i z innym zerem prądu. Do tego `examples/events.ndjson` z dwoma zdarzeniami `config` i znacznikiem. Zawiera zasymulowany krótki zanik sygnału pozycji (1,0 s) i skok masy do 0,42 V (1,40–1,55 s). **To nie jest dowód, że takie uszkodzenie występuje w samochodzie** — to dane do sprawdzenia narzędzi.

## Przygotowano, ale nie uruchomiono

**`tests/test_control.c`** — jedenaście testów czystej logiki: permutacje pinów, wymagane 2 s stabilności i timeout IDENTIFY, zakresy zależne od trybu ADC, zawartość migawki konfiguracji (w tym to, że niesie zakres **potwierdzony**, a nie żądany), ratio i pozycja przy ujemnym zakresie, prąd ze zmierzonego zera i z flagą ważności, osiem osobnych blokad wywracających stan w FAULT, brak ARM i błąd `DRIVE_IO` blokujące ruch, zapis prądu zerwania w FRICTION, kasowanie kampanii HOT-SOAK przez FAULT, limity rozkazów.

**W środowisku, w którym powstał pakiet, nie ma kompilatora C ani ESP-IDF**, więc ani te testy, ani firmware nie zostały skompilowane. Nie deklaruję poprawnej kompilacji, działania peryferiów ani żadnej przepustowości. Uruchomienie testów logiki to pierwsza rzecz do zrobienia — instrukcja w `03-uruchomienie.md`, sekcja „Zanim zaczniesz lutować".

## Nie wykonano

ERC/DRC w programie EDA, routingu PCB, pomiarów napięć, prądów, opóźnień, temperatury, EMC ani impulsów automotive. Pliki CSV w `hardware/` to lista sygnałów i przypisanie bramek, **nie netlista** — nóżki konkretnych obudów dobierasz z datasheetów. Źródła dokumentacji producentów zebrano przy v1; w v3 sprostowano cztery punkty na podstawie przeglądu (patrz `05-zrodla.md`), ale nie odpytywano tych adresów ponownie.

## Co zmieniło się w stanie ryzyka względem v2

| Element | v2 | v3 |
|---|---|---|
| Kalibracja w pliku | jedna, ze startu sesji | migawka per `config_id`, dobierana per próbka |
| Tryb ADC | zgadywany, cichy fallback | wybór przy kompilacji, weryfikacja odczytem, **błąd blokuje TEST** |
| Węzeł SAFE_N | wyjście push-pull na wire-AND, drugi pull-up | wyłącznie wyjścia otwarte, jeden pull-up przez grzybek |
| Ochrona wejścia | P-MOS w złej orientacji, TVS ponad zakres TSR | moduł LM74800EVM-CD z mierzonym OVP |
| Multiplekser prądu | drugi biegun przekaźnika banku | osobny przekaźnik z własną cewką |
| Nadzór 5V_A | usunięty | przywrócony (okno + odniesienie) |
| Bufor zapisu | 1 MiB (16 s) | 8 MiB (131 s) |
| Kierunek napędu | zapamiętywany przed potwierdzeniem I²C | po potwierdzeniu; błąd → `DRIVE_IO` |
| Polecenia | dwie ścieżki (konsola, WWW) | jeden dispatcher |
| Składnia C | brak kontroli, pakiet się nie kompilował | test składni w zestawie |

## Otwarte ryzyka techniczne

| Element | Co trzeba rozstrzygnąć | Jak v3 ogranicza skutek |
|---|---|---|
| Rejestry AD7606B | adresy i bity dla Twojej rewizji, zworki OS | weryfikacja odczytem; niezgodność blokuje TEST i jest w każdym rekordzie |
| Mapowanie pinów 4/5/6 | dwa źródła w projekcie mówiły różne rzeczy | IDENTIFY sprawdza sześć permutacji i wymaga jednoznaczności |
| Próg ostrzegawczy masy | 0,05 V to wartość startowa | do ustawienia po pomiarze szumu w etapie 5 |
| Złącza OEM | obudowa, klucze, orientacja CUD87 | zakup dopiero po fotografii i pomiarze |
| Limity zaworu | brak potwierdzonych OEM prądów i temperatur | limity rozruchowe, twardy trip ±4 A, ostrożny LEARN, limit TC1 w profilu |
| Kwalifikacja czasowa | jitter `esp_timer`, opóźnienia SD | 2 kS/s jako punkt startowy; powyżej ~5 kS/s trzeba timera sprzętowego |
| Adapter L1 | bocznik i dwie pary styków zmieniają obwód | L2 jako pierwszy krok; flaga ważności prądu w logu |
| SD i FAT | brak rotacji i odzyskiwania po zaniku zasilania | format znosi urwany ostatni blok; ok. 18,4 h przy 2 kS/s |
| Bezpieczeństwo | projekt warsztatowy | brak deklaracji SIL/ASIL i odporności na dowolną pojedynczą awarię |

## Czego ten pakiet nadal nie zmienia

Najtańsze rozstrzygnięcie kampanii leży w procedurze v3 i skopie, a EGRLab wchodzi po niej. Budowa to kilkanaście wieczorów; Test A, Krok 2, test opalarką i wiggle to weekend. Kolejność w `02-procedury.md` jest tam dlatego, że rozpięcie CUD87 zaburza hipotezę H6 — a nie z ostrożności redakcyjnej.
