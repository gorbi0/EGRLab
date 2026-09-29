# EGRLab v5 — prototyp modułowy

Rewizja 5.0, 22.09.2026. Kia Sportage 1.7 CRDi 2013 / EGR 28410-2A850. Zachowano ESP32-S3 N32R16V, LOGGER i TESTER oraz osobny układ ochrony THT. Dziesięć wymiennych PCB, opcjonalny PANEL i przyrząd P00 do uruchamiania.

**To kompletny pakiet obwodu i oprogramowania do budowy prototypu, z netlistą pinową i kontraktem wiązek. Nie zawiera rozmieszczenia i trasowania PCB, plików KiCad ani Gerberów.** Granice płytek i otwory są założeniami mechanicznymi do layoutu. Nie wykonano fizycznego odbioru urządzenia. Wyniki kompilacji i testów programu są w `verification/`; formularz prób sprzętu pozostaje niewypełniony.

## Od czego zacząć

1. [Zmiany i architektura](docs/01-architektura.md).
2. [Połączenia, GPIO i mechanika](docs/02-interfejsy.md), [pełna lista przewodów](hardware/wiring.csv).
3. [Uruchamianie etapami](docs/03-uruchomienie.md), [karty poszczególnych PCB](docs/PCB.md).
4. [Atlas połączeń wszystkich elementów](schematy/index.html), [netlista](hardware/netlist.csv).
5. [BOM według płytek](hardware/BOM.csv), [wykaz nazwa–ilość](hardware/zakupy.csv), [jak kupować etapami](docs/07-zakupy.md).
6. [Firmware i format logów](docs/04-firmware-logi.md), [kalibracja i profile](docs/05-profile.md), [procedury diagnostyczne](docs/06-diagnostyka.md).
7. [Stan weryfikacji](verification/README.md), [arkusz odbioru](verification/ODBIOR.csv).

Najważniejsze zmiany: lokalne ADC prądu na I-LOGGER i DRIVE; wspólna kadencja 2 kS/s z jawną różnicą czasu konwersji; dodatnie sygnały gotowości; lokalny zatrzask OC na DRIVE; korekta GPB7 → GPA4; osobne kalibracje modułów; wersja 5 logu 40 B i czytnik zachowujący zgodność z formatami 1–4; warianty firmware CORE/minimal/LOGGER/TEST/Wi-Fi.

`reference/` zawiera niezmienione materiały v4.1 **wyłącznie jako historię i opis odziedziczonych obwodów**. Do okablowania v5 używaj `hardware/` i nowego atlasu. Nie łącz obu BOM-ów. `P01-PROTECT/` opisuje samodzielny układ zasilania; jego elementy są już policzone w głównym BOM-ie. Pliki starych wydań poza tym katalogiem pozostają bez zmian.
