# EGRLab v1 — pakiet projektu, rewizja A

2026-09-21 • Kia Sportage 1.7 CRDi, 2013 r. • 28410-2A850 • Waveshare ESP32-S3-DEV-KIT-N32R16-M

Projekt warsztatowego testera i rejestratora EGR, do składania modułami. MCU: ESP32-S3-WROOM-2-N32R16V, 32 MB Flash, 16 MB PSRAM. Pinout 1/3 = silnik, 4 = pozycja jest **założeniem przekazanym przez użytkownika**; przed wykonaniem wiązki potwierdź numerację widzianą od strony styków. Nie znaleziono niezależnej, publicznej dokumentacji OEM rozstrzygającej ją dla konkretnego VIN. Nie podajemy wymyślonej orientacji wtyczki ani numeru jej obudowy.

## Czytaj w tej kolejności

1. [Projekt i połączenia](docs/01-projekt.md) — architektura, zasilanie, pomiary, ADC, napęd, blokady, pinout, CAN.
2. [Procedury i diagnostyka](docs/02-procedury.md) — IDENTIFY, LEARN, MANUAL, SWEEP, FRICTION, CYCLE, THERMAL, LOGGER; P0404 i 1500–1700 rpm.
3. [Uruchomienie i odbiór](docs/03-uruchomienie.md) — etapy, pomiary, kryteria przerwania, ograniczenia.
4. [Firmware i format danych](docs/04-firmware-logi.md) — stany, moduły, pamięć, komendy, format binarny, analiza.
5. [BOM](hardware/BOM.csv), [pinout](hardware/pinout.csv), [połączenia](hardware/connections.csv), [źródła](docs/05-zrodla.md).

Dokumenty zawierają schematy połączeń na poziomie elementów i modułów. [Schemat blokowy](hardware/architecture.svg) pokazuje całość. [Wyniki kontroli](docs/06-weryfikacja.md) określają, co rzeczywiście sprawdzono. `firmware/` jest projektem źródłowym ESP-IDF, `tools/egrlog.py` czyta i eksportuje logi, `tests/` sprawdza format i algorytmy bez sprzętu. `examples/` zawiera wyłącznie **syntetyczny** zapis testowy.

## Granica gotowości

To kompletna dokumentacja konstrukcyjna **prototypu warsztatowego** z referencyjną implementacją oprogramowania, a nie zatwierdzone urządzenie samochodowe. Nie ma tutaj wykonanej i sprawdzonej PCB, Gerberów ani wyników testów EMC/ISO 7637/ISO 16750. W tym środowisku nie ma ESP-IDF/toolchainu ani fizycznego sprzętu: kompilacja na docelowy MCU i odbiór sprzętowy pozostają do wykonania według instrukcji. Nie opisujemy ich jako zaliczonych.

Domyślne źródła mają aktywację silnika wyłączoną w konfiguracji. Jej włączenie wymaga zakończenia odbioru z rozdziału 03, kalibracji torów i profilu zaworu. To celowa blokada pierwszego uruchomienia. Nominalne 20 kS/s jest celem podlegającym pomiarowi; bezstratność oraz jitter nie są zagwarantowane samą szybkością SPI.

Automatyczne rozpoznawanie 5/6 działa przez **bierny pomiar w LOGGER przy zasilaniu czujnika przez ECU**. Jeśli masz tylko odłączony zawór i brak zapisanego profilu, TEST pozostaje zablokowany; układ nie odwraca napięcia próbnie. Profil dotyczy konkretnego zaworu i adaptera.

Najważniejsza korekta wcześniejszej koncepcji: osobne porty nie oznaczają izolacji galwanicznej. Wspólna masa i odczepy pomiarowe pozostają połączeniami elektrycznymi; separujemy źródła energii i blokujemy TEST sprzętowo przy podłączonym adapterze LOGGER.
