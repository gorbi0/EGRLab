# EGRLab v2

2026-09-21 · Kia Sportage SL 2013, 1.7 CRDi D4FD, Bosch EDC17C08 · zawór EGR 28410-2A850, złącze CUD87 · Waveshare ESP32-S3-DEV-KIT-N32R16-M

Warsztatowy rejestrator i tester zaworu EGR, do złożenia modułami. Projektowany pod jedną kampanię — przerywany P0404 opisany w `../docs/01-overview.md` — i pod dwa sposoby użycia: **wielogodzinną rejestrację ośmiu kanałów w jadącym aucie** oraz **sterowanie zaworem przy zgaszonym silniku, bez demontażu zaworu**.

v2 zastępuje `../EGRLab-v1/` (rewizja A). Tamten katalog zostaje jako punkt odniesienia — nie buduj z niego. Co dokładnie się zmieniło i dlaczego: [00-zmiany-v1-v2.md](docs/00-zmiany-v1-v2.md).

## Czytaj w tej kolejności

1. [Zmiany v1 → v2](docs/00-zmiany-v1-v2.md) — jeśli znasz v1, zacznij tutaj.
2. [Projekt elektryczny](docs/01-projekt.md) — architektura, adaptery, zasilanie, mostek, bezpieczeństwo, ADC, pinout, SCOPE_TRIG, interfejs na telefon.
3. [Procedury](docs/02-procedury.md) — **dokument do auta**: IDENTIFY, LEARN, SWEEP, FRICTION, HOT-SOAK, LOGGER, SUBSTITUTE LOAD, HARNESS-ONLY, macierz rozstrzygania mapowana na H1–H7.
4. [Budowa i odbiór](docs/03-uruchomienie.md) — plan na wieczory, próby niezależności zabezpieczeń, kalibracja, zakupy i logistyka.
5. [Firmware i format danych](docs/04-firmware-logi.md) — stany, konsola, triggery, EGRLOG1 wersja 2, narzędzia.
6. [Źródła](docs/05-zrodla.md) · [Stan weryfikacji](docs/06-weryfikacja.md) · [BOM](hardware/BOM.csv) · [pinout](hardware/pinout.csv) · [połączenia](hardware/connections.csv) · [schemat blokowy](hardware/architecture.svg)

## Co to potrafi, czego nie potrafi skop

DHO804 ma cztery kanały, pasmo i głęboką pamięć — i nie wie, kiedy patrzeć. EGRLab ma osiem kanałów wspólnie próbkowanych, prąd uzwojenia, temperatury, CAN i godziny ciągłego zapisu — i nie ma pasma. Dlatego mają pracować razem: przy każdym wykrytym zdarzeniu firmware wystawia impuls na **SCOPE_TRIG**, który wyzwala skop.

| Kanał | Sygnał |
|---|---|
| 1, 2 | pin 1 i pin 3 (napęd, obie strony) |
| 3, 4, 5 | pin 4, 5, 6 — zasilanie, masa i sygnał czujnika w kolejności ustalonej przez IDENTIFY |
| 6 | prąd uzwojenia aktywnego banku |
| 7 | napięcie instalacji |
| 8 | **AUX** — punkt spoza EGR: linia ECV klimatyzacji (H7) albo masa GUD09 (H2) |

Kanał masy czujnika pracuje po identyfikacji na zakresie ±2,5 V, czyli **76 µV na działkę** — próg 30 mV z Kroku 2 procedury v3 to około 400 działek przetwornika, a nie sto.

## Granica gotowości

To jest kompletna dokumentacja konstrukcyjna **prototypu warsztatowego** z referencyjną implementacją oprogramowania, a nie zatwierdzone urządzenie samochodowe. Nie ma tu wykonanej PCB, Gerberów ani wyników testów EMC/ISO 7637/ISO 16750. Firmware nie został skompilowany na docelowy MCU — w środowisku, w którym pakiet powstał, nie ma ESP-IDF, kompilatora C ani sprzętu. Testy Pythona przechodzą; testy logiki w C są napisane, ale nieuruchomione. Szczegóły: [06-weryfikacja.md](docs/06-weryfikacja.md).

Źródła mają `EGR_HARDWARE_ACCEPTED = 0` i `CONFIG_EGR_ACTIVE_TEST = n`. Odblokowanie wymaga przejścia odbioru z rozdziału 03, kalibracji obu banków i wpisania **zmierzonych** współczynników. To nie zastępuje fizycznego przycisku ARM — ten pozostaje konieczny zawsze, także przy sterowaniu z telefonu.

Piny 1/3 jako napęd są **założeniem przekazanym przez użytkownika**; mapowanie pinów 4/5/6 urządzenie ustala pomiarowo, bo dwa źródła w tym projekcie podawały różne wersje. Przed wykonaniem adapterów potwierdź numerację widzianą od strony styków ze schematem Monolith (strony PDF 56–59). Pomyłka na pinach 1/3 zwiera gałąź mostka.

## Kolejność, o której warto pamiętać

Najpierw procedura skopowa v3 w aucie: Test A, masa pod obciążeniem, opalarka, wiggle — back-probe, **bez rozpinania CUD87**. Dopiero potem LOGGER L2, potem L1 z prądem, a TEST i HOT-SOAK wtedy, gdy powyższe wskażą na zawór albo nie wskażą na nic. Rozpięcie złącza jest operacją zaburzającą hipotezę H6 i raz zrobione nie da się cofnąć.

## Szybki start narzędzi

```bash
python -m unittest discover -s tests -p "test_*.py" -v
python tools/egrlog.py inspect examples/synthetic.egr
python tools/egrlog.py scan examples/events.ndjson
python tools/egrlog.py report examples/synthetic.egr --meta examples/synthetic.json --html raport.html
```

Python używa wyłącznie biblioteki standardowej. Dane w `examples/` są oznaczone jako **syntetyczne** i nie pochodzą z auta.
