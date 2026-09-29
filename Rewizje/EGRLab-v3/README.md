# EGRLab v3

2026-09-22 · Kia Sportage SL 2013, 1.7 CRDi D4FD, Bosch EDC17C08 · zawór EGR 28410-2A850, złącze CUD87 · Waveshare ESP32-S3-DEV-KIT-N32R16-M

Warsztatowy rejestrator i tester zaworu EGR, do złożenia modułami. Projektowany pod jedną kampanię — przerywany P0404 opisany w `../docs/01-overview.md` — i pod dwa sposoby użycia: **wielogodzinną rejestrację ośmiu kanałów w jadącym aucie** oraz **sterowanie zaworem przy zgaszonym silniku, bez demontażu zaworu**.

v3 zastępuje `../EGRLab-v2/`, która zastąpiła `../EGRLab-v1/`. Oba starsze katalogi zostają jako punkty odniesienia — nie buduj z nich. v3 powstała po zewnętrznym przeglądzie v2 (`../EGRLab-v2/OCENA-v2.md`), który znalazł osiem błędów blokujących; wszystkie są naprawione, a co dokładnie i dlaczego — [00-zmiany-v2-v3.md](docs/00-zmiany-v2-v3.md).

## Czytaj w tej kolejności

1. [Zmiany v2 → v3](docs/00-zmiany-v2-v3.md) — odpowiedź na przegląd, punkt po punkcie. Jeśli znasz v2, zacznij tutaj.
2. [Projekt elektryczny](docs/01-projekt.md) — architektura, adaptery, zasilanie, mostek, bezpieczeństwo, ADC, pinout, SCOPE_TRIG, interfejs na telefon.
3. [Procedury](docs/02-procedury.md) — **dokument do auta**: IDENTIFY, LEARN, SWEEP, FRICTION, HOT-SOAK, LOGGER, SUBSTITUTE LOAD, HARNESS-ONLY, macierz rozstrzygania mapowana na H1–H7.
4. [Budowa i odbiór](docs/03-uruchomienie.md) — plan na wieczory, próby niezależności zabezpieczeń, kalibracja, zakupy i logistyka.
5. [Firmware i format danych](docs/04-firmware-logi.md) — stany, dispatcher, triggery, migawki konfiguracji, EGRLOG1 wersja 3, narzędzia.
6. [Źródła](docs/05-zrodla.md) · [Stan weryfikacji](docs/06-weryfikacja.md) · [BOM](hardware/BOM.csv) · [pinout](hardware/pinout.csv) · [połączenia](hardware/connections.csv) · [schemat blokowy](hardware/architecture.svg)

Historia starszej rewizji: [zmiany v1 → v2](docs/00-zmiany-v1-v2.md).

## Co to potrafi, czego nie potrafi skop

DHO804 ma cztery kanały, pasmo i głęboką pamięć — i nie wie, kiedy patrzeć. EGRLab ma osiem kanałów wspólnie próbkowanych, prąd uzwojenia, temperatury, CAN i godziny ciągłego zapisu — i nie ma pasma. Dlatego mają pracować razem: przy każdym wykrytym zdarzeniu firmware wystawia impuls na **SCOPE_TRIG**, który wyzwala skop. Zastrzeżenie: DHO804 nie ma osobnego wejścia wyzwalania, więc ten sygnał **zajmuje jeden kanał analogowy**, a detektory `stall` i `open` z definicji spóźniają się o 200 i 50 ms — ustaw na skopie głębokość przed wyzwoleniem.

| Kanał | Sygnał |
|---|---|
| 1, 2 | pin 1 i pin 3 (napęd, obie strony) |
| 3, 4, 5 | pin 4, 5, 6 — zasilanie, masa i sygnał czujnika w kolejności ustalonej przez IDENTIFY |
| 6 | prąd uzwojenia aktywnego banku (z flagą ważności) |
| 7 | napięcie instalacji |
| 8 | **AUX** — punkt spoza EGR: linia ECV klimatyzacji (H7) albo masa GUD09 (H2) |

Kanał masy czujnika pracuje po identyfikacji na zakresie ±2,5 V, czyli **76 µV na działkę**. Rozdzielczość to jednak nie wykrywalność: próg ostrzegawczy ustawia się po zmierzeniu szumu własnego toru, nie z katalogu.

## Co v3 naprawia względem v2

Najgroźniejszy błąd v2 nie powodował awarii, tylko **wiarygodnie wyglądającą nieprawdę**: po przejściu kanału masy na czulszy zakres eksport mnożył napięcie przez cztery, więc 20 mV wyglądało jak 80 mV — dokładnie tam, gdzie szukamy H2. W v3 każda próbka niesie `config_id`, a pełna migawka kalibracji trafia do `events.ndjson`; eksporter dobiera ją per próbka. Pilnuje tego test regresyjny.

Poza tym: obwód STOP przerobiony tak, żeby wire-AND naprawdę działał (żadnych wyjść push-pull na węźle, jeden pull-up przez grzybek); ochrona wejścia z powrotem na module z mierzonym OVP; osobny przekaźnik na multiplekser prądu; tryb ADC wybierany przy kompilacji z twardym błędem zamiast cichego fallbacku; jedna ścieżka poleceń dla konsoli i telefonu; przywrócony nadzór 5V_A i bufor zapisu 8 MiB. Plus test składni C, bo v2 wyszła z literalnym końcem wiersza w stałej znakowej i nie kompilowała się w ogóle.

## Granica gotowości

To jest kompletna dokumentacja konstrukcyjna **prototypu warsztatowego** z referencyjną implementacją oprogramowania, a nie zatwierdzone urządzenie samochodowe. Nie ma tu wykonanej PCB, Gerberów ani wyników testów EMC/ISO 7637/ISO 16750. Firmware nie został skompilowany na docelowy MCU — w środowisku, w którym pakiet powstał, nie ma ESP-IDF ani kompilatora C. Testy Pythona (23) przechodzą; testy logiki w C są napisane, ale **nieuruchomione**. Szczegóły: [06-weryfikacja.md](docs/06-weryfikacja.md).

Źródła mają `EGR_HARDWARE_ACCEPTED = 0` i `CONFIG_EGR_ACTIVE_TEST = n`. Odblokowanie wymaga przejścia odbioru z rozdziału 03, kalibracji obu banków i obu pozycji zworki AUX oraz wpisania **zmierzonych** współczynników. To nie zastępuje fizycznego przycisku ARM — ten pozostaje konieczny zawsze, także przy sterowaniu z telefonu.

Piny 1/3 jako napęd są **założeniem przekazanym przez użytkownika**; mapowanie pinów 4/5/6 urządzenie ustala pomiarowo, bo dwa źródła w tym projekcie podawały różne wersje. Przed wykonaniem adapterów potwierdź numerację widzianą od strony styków ze schematem Monolith (strony PDF 56–59). Pomyłka na pinach 1/3 zwiera gałąź mostka.

## Kolejność, o której warto pamiętać

Najpierw procedura skopowa v3 w aucie: Test A, masa pod obciążeniem, opalarka, wiggle — back-probe, **bez rozpinania CUD87**. Dopiero potem LOGGER L2, potem L1 z prądem, a TEST i HOT-SOAK wtedy, gdy powyższe wskażą na zawór albo nie wskażą na nic. Rozpięcie złącza jest operacją zaburzającą hipotezę H6 i raz zrobione nie da się cofnąć.

## Szybki start narzędzi

```bash
python -m unittest discover -s tests -p "test_*.py" -v
python tools/egrlog.py inspect examples/samples.egr
python tools/egrlog.py scan examples/events.ndjson
python tools/egrlog.py report examples/samples.egr --html raport.html
```

A zanim weźmiesz lutownicę — uruchom testy logiki, których ja uruchomić nie mogłem:

```bash
gcc -std=c11 -I firmware/main -o test_control tests/test_control.c firmware/main/control.c -lm
```

Python używa wyłącznie biblioteki standardowej. Dane w `examples/` są oznaczone jako **syntetyczne** i nie pochodzą z auta.
