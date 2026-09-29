# Karty modułów v5

Numeracja pinów wszystkich elementów: `hardware/netlist.csv`; każdy moduł ma także arkusze w atlasie.

Wymiary to zarezerwowane obrysy przed layoutem, nie gotowe PCB do frezowania.


## P01 PROTECT

Rezerwa miejsca: 100×160 mm; HW5.0, IF M1.

Elementy: 77 wpisów BOM. Zestaw części: `hardware/P01-BOM.csv`.

Złącza między modułami: BAT, PG, SUPPLY.

Odbiór: Polaryzacja i prąd wsteczny; OVP/UVLO/histereza; Soft-start i pojemność; 5 A ciągłe / radiatory; FAULT i utrata P01.


## P02 PSU

Rezerwa miejsca: 80×70 mm; HW5.0, IF M1.

Elementy: 30 wpisów BOM. Zestaw części: `hardware/P02-BOM.csv`.

Złącza między modułami: LV03, LV04, LV05, LV06, LV07, LV08, LV09, LV10, PSUOK, SUPPLY, VMOTOR.

Odbiór: Szyny pod obciążeniem; Tętnienia i prąd rozruchu; PSU_OK przy zaniku każdej szyny.


## P03 CORE

Rezerwa miejsca: 110×90 mm; HW5.0, IF M1.

Elementy: 48 wpisów BOM. Zestaw części: `hardware/P03-BOM.csv`.

Złącza między modułami: CAN, DAQ, DIR, ILOG, ITEST, LV03, PANELCORE, SAFE, SFAULT, TEMP.

Odbiór: 3V3_CORE oddzielne od IO; PSRAM MEMTEST; SD write/read; A4 input / B7 output; CS38 i SCOPE41; Brak zasilania przez sygnały.


## P04 SAFE

Rezerwa miejsca: 100×80 mm; HW5.0, IF M1.

Elementy: 66 wpisów BOM. Zestaw części: `hardware/P04-BOM.csv`.

Złącza między modułami: DAQOK, DRIVE, LV04, PANELSAFE, PG, PSUOK, SAFE, SENSOR.

Odbiór: Tabela wszystkich gotowości; LOGGER/TEST/klucz/pętla; Watchdog bez MCU; STOP i brak samowznowienia; SENSOR bez ARM motoru.


## P05 DAQ

Rezerwa miejsca: 110×100 mm; HW5.0, IF M1.

Elementy: 87 wpisów BOM. Zestaw części: `hardware/P05-BOM.csv`.

Złącza między modułami: DAQ, DAQOK, LV05, TAPS.

Odbiór: Piny CONVST/WR/REGCAP; Osiem torów raw; Kalibracja obu banków; Zakresy i readback; Czas/szum/faza odczepów; DAQ_OK bez zasilania.


## P06 I-LOGGER

Rezerwa miejsca: 80×65 mm; HW5.0, IF M1.

Elementy: 46 wpisów BOM. Zestaw części: `hardware/P06-BOM.csv`.

Złącza między modułami: ILOG, ISERIES, LV06.

Odbiór: Pinout REF/LDO; Zero/skala obu znaków; BYPASS z sygnałem nieważności; Prąd/temperatura shuntu; SPI z pozostałymi odbiornikami; Przedział czasu konwersji.


## P07 DRIVE

Rezerwa miejsca: 120×100 mm; HW5.0, IF M1.

Elementy: 106 wpisów BOM. Zestaw części: `hardware/P07-BOM.csv`.

Złącza między modułami: DIR, DRIVE, ITEST, LV07, TMOTOR, VMOTOR.

Odbiór: Zero/skala obu znaków; Progi lokalnego OC; Zatrzask i fizyczny ARM; Permit/PWM po zaniku przewodu; Odcięcie bez ESP; Kierunek i 5 ms; Termika / obciążenie.


## P08 SENSOR

Rezerwa miejsca: 65×55 mm; HW5.0, IF M1.

Elementy: 28 wpisów BOM. Zestaw części: `hardware/P08-BOM.csv`.

Złącza między modułami: LV08, SENSOR, SFAULT, TSENSOR.

Odbiór: Limit i sygnał FAULT; Oba styki odłączone; SENSOR_OK niezależne od permit; Zanik permit/zasilania.


## P09 TEMP

Rezerwa miejsca: 75×55 mm; HW5.0, IF M1.

Elementy: 12 wpisów BOM. Zestaw części: `hardware/P09-BOM.csv`.

Złącza między modułami: LV09, TEMP.

Odbiór: Dwie temperatury i przerwane sondy; Wspólna praca SD/SPI; Błąd odniesienia i termika złącz.


## P10 CAN

Rezerwa miejsca: 60×50 mm; HW5.0, IF M1.

Elementy: 9 wpisów BOM. Zestaw części: `hardware/P10-BOM.csv`.

Złącza między modułami: CAN, LV10.

Odbiór: Listen-only bez ACK; Brak dodatkowej terminacji; Przeciążenie / licznik strat; Potwierdzone źródło RPM.


## P11 PANEL

Rezerwa miejsca: 100×60 mm; HW5.0, IF M1.

Elementy: 17 wpisów BOM. Zestaw części: `hardware/P11-BOM.csv`.

Złącza między modułami: EXT_L1, EXT_L2, EXT_T, ISERIES, PANELCORE, PANELSAFE, TAPS, TMOTOR, TSENSOR.

Odbiór: Zgodność pinów; NC STOP; Pętla adaptera T; MARK i brak pomyłek złącz; Mechaniczne rozwieranie obu NC przy wtyku LOGGER.


## P00 Przyrząd stanowiskowy

Rezerwa miejsca: 80×60 mm; HW5.0, IF M1.

Elementy: 33 wpisów BOM. Zestaw części: `hardware/P00-BOM.csv`.

Złącza między modułami: .

Odbiór: Częstotliwość około 102 Hz; Amplituda 3,3 V; Osiem przełączników i rezystory 1 kΩ.
