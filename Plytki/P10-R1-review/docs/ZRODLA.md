# Źródła i zakres weryfikacji — 27.09.2026

Dokumenty producentów odczytane przy projektowaniu; założenia projektu oddzielono od ich
parametrów. Oznaczenia pinów porównane do tabel producentów, a nie zdjęć gotowych modułów.

| Źródło | Sprawdzone informacje |
|---|---|
| [TI TCAN1051-Q1, Rev.D](https://www.ti.com/lit/ds/symlink/tcan1051-q1.pdf) | Tablica pinów wariantuV:1TXD,2GND,3VCC,4RXD,5VIO,6CANL,7CANH,8S. S=HIGH: odbiór przy wyłączonym nadajniku. ZakresyVCC/VIO, UVLO obu szyn, zachowanie RXD przy zaniku szyn, limity wejść/wyjść, prąd trybu silent, SOIC8. |
| [Nexperia PESD2CAN](https://assets.nexperia.com/documents/data-sheet/PESD2CAN.pdf) | SOT23:1/2 równoważne linie,3 wspólny pin;24 V standoff, pojemność i parametry impulsowe. Nie kwalifikuje całego urządzenia. |
| [Nexperia74LVC125A](https://assets.nexperia.com/documents/data-sheet/74LVC125A.pdf) | Układ bramek/pinów, zasilanie3,3 V, aktywne niskim OE, Ioff i tolerancja napięć wejściowych. SO14 wariantuAD. |
| [Espressif ESP32-S3 TWAI](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/twai.html) | Classical CAN, brak CAN FD; listen-only bez ACK i dominantnych bitów. Odczytany przewodnikv6.1; nie migruje automatycznie API bazowego firmware. |

Snapshoty lokalne w `reference/source-sha256.json`: bazowe P10 XML/BOM/interfejsy
z EGRLab-v6.1-rc1, board.c/app_main.c oraz aktualne kontrakty części P02-R3/P03-R2.
Te kopie są materiałem porównawczym, nie aktywnymi schematami. Karta P10 ma własną
numerację referencji. Znaczenie listy zakupów: ilości netto dla jednej płytki.

Decyzje projektowe, nie gwarancje producenta: odczep300 mm, W1/W2 długości200/150 mm,
rezerwa10 mA na każdej szynie, brak CMC na pierwszą kwalifikację500 kbit/s, rozmieszczenie
kotew i budżet logowania. Weryfikacja na stanowisku musi objąć rzeczywisty kabel i PCB.

OBD6/14 użyto zgodnie z dotychczasowym kontraktem projektu. Nie jest to zweryfikowany
schemat całej instalacji konkretnego VIN. Przed użyciem potwierdzić protokół, prędkość
i numerację złącza w aucie. Nie kopiować poglądowego rysunku wtyku bez rozróżnienia
widoku czoła/styków/lutowania.
