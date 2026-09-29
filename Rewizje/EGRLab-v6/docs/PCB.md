# Karty modułów V6 / HW6.0 / interfejs M2

BOM-y zawierają pozycje „Wiązka”; ich części są rozpisane w wiazki-czesci.csv. Zakupy.csv liczy części wiązek zamiast całych wiązek, bez podwajania. Długość jest długością gotową od PTH do czoła wtyku; zapas cięcia podano tylko w częściach.

## AL1 LOGGER L1 adapter
Wykonanie: **trwały montaż lutowany / nośnik / panel**. BOM: [hardware/AL1-BOM.csv](../hardware/AL1-BOM.csv).
| Wiązka / łącze | Długość gotowa | Wtyk | Lutowany koniec / właściciel |
|---|---:|---|---|
| EXT_L1 | 1000 mm | DEUTSCH DT06-12SB + DT04-12PB | BRAK: zaciskane styki DEUTSCH na obu końcach; BOM AL1 |

Montaż: Sprawdzić mapę styków; lutować odczepy przez rezystory, odizolować i odciążyć mechanicznie.
Odbiór: oględziny obu stron, ciągłość pin–pin, brak zwarć sąsiednich żył, identyfikacja kluczy; następnie próby z ODBIOR.csv. Odłączać wyłącznie bez zasilania.

## AL2 LOGGER L2 adapter
Wykonanie: **trwały montaż lutowany / nośnik / panel**. BOM: [hardware/AL2-BOM.csv](../hardware/AL2-BOM.csv).
| Wiązka / łącze | Długość gotowa | Wtyk | Lutowany koniec / właściciel |
|---|---:|---|---|
| EXT_L2 | 1000 mm | DEUTSCH DT06-12SC + DT04-12PC | BRAK: zaciskane styki DEUTSCH na obu końcach; BOM AL2 |

Montaż: Sprawdzić mapę styków; lutować odczepy przez rezystory, odizolować i odciążyć mechanicznie.
Odbiór: oględziny obu stron, ciągłość pin–pin, brak zwarć sąsiednich żył, identyfikacja kluczy; następnie próby z ODBIOR.csv. Odłączać wyłącznie bez zasilania.

## AT TEST adapter
Wykonanie: **trwały montaż lutowany / nośnik / panel**. BOM: [hardware/AT-BOM.csv](../hardware/AT-BOM.csv).
| Wiązka / łącze | Długość gotowa | Wtyk | Lutowany koniec / właściciel |
|---|---:|---|---|
| EXT_T | 1000 mm | DEUTSCH DT06-12SA + DT04-12PA | BRAK: zaciskane styki DEUTSCH na obu końcach; BOM AT |

Montaż: Sprawdzić mapę styków; lutować odczepy przez rezystory, odizolować i odciążyć mechanicznie.
Odbiór: oględziny obu stron, ciągłość pin–pin, brak zwarć sąsiednich żył, identyfikacja kluczy; następnie próby z ODBIOR.csv. Odłączać wyłącznie bez zasilania.

## EXT Zasilanie zewnętrzne
Wykonanie: **trwały montaż lutowany / nośnik / panel**. BOM: [hardware/EXT-BOM.csv](../hardware/EXT-BOM.csv).
| Wiązka / łącze | Długość gotowa | Wtyk | Lutowany koniec / właściciel |
|---|---:|---|---|
| BAT | 200 mm | MSTB 5.08 2p >=12A z tulejkami, KEY BAT | P01/J_BATB; BOM P01 |

Montaż: Sprawdzić mapę styków; lutować odczepy przez rezystory, odizolować i odciążyć mechanicznie.
Odbiór: oględziny obu stron, ciągłość pin–pin, brak zwarć sąsiednich żył, identyfikacja kluczy; następnie próby z ODBIOR.csv. Odłączać wyłącznie bez zasilania.

## P00 FIXTURE
Wykonanie: **trwały montaż lutowany / nośnik / panel**. BOM: [hardware/P00-BOM.csv](../hardware/P00-BOM.csv).
| Wiązka / łącze | Długość gotowa | Wtyk | Lutowany koniec / właściciel |
|---|---:|---|---|
| Brak stałej wiązki między PCB | — | przewody stanowiskowe | nie dotyczy |

Montaż: Sprawdzić mapę styków; lutować odczepy przez rezystory, odizolować i odciążyć mechanicznie.
Odbiór: oględziny obu stron, ciągłość pin–pin, brak zwarć sąsiednich żył, identyfikacja kluczy; następnie próby z ODBIOR.csv. Odłączać wyłącznie bez zasilania.

## P01 PROTECT
Wykonanie: **PCB dwuwarstwowa zamawiana**. BOM: [hardware/P01-BOM.csv](../hardware/P01-BOM.csv).
Rezerwa obrysu 100 × 160 mm. Otwory z modules.json są założeniem do rozmieszczenia.
| Wiązka / łącze | Długość gotowa | Wtyk | Lutowany koniec / właściciel |
|---|---:|---|---|
| PG | 200 mm | Mini-Fit Jr żeński 6p, styki Au, klucz PG | P01/J_PGB; BOM P01 |
| SUPPLY | 200 mm | MSTB 5.08 3p >=12A z tulejkami, KEY SUPPLY | P02/J_SUPPLYB; BOM P02 |
| BAT | 200 mm | MSTB 5.08 2p >=12A z tulejkami, KEY BAT | P01/J_BATB; BOM P01 |

Montaż: TVS/bezpiecznik → sterowanie ochroną → MOSFET-y i radiatory → obciążenie sztuczne.
Odbiór: oględziny obu stron, ciągłość pin–pin, brak zwarć sąsiednich żył, identyfikacja kluczy; następnie próby z ODBIOR.csv. Odłączać wyłącznie bez zasilania.

## P02 PSU
Wykonanie: **trwały montaż lutowany / nośnik / panel**. BOM: [hardware/P02-BOM.csv](../hardware/P02-BOM.csv).
Rezerwa obrysu 80 × 70 mm. Otwory z modules.json są założeniem do rozmieszczenia.
| Wiązka / łącze | Długość gotowa | Wtyk | Lutowany koniec / właściciel |
|---|---:|---|---|
| PSUOK | 150 mm | IDC żeński 6p Au z odciążką, KEY 5 | P02/J_PSUOKB; BOM P02 |
| SUPPLY | 200 mm | MSTB 5.08 3p >=12A z tulejkami, KEY SUPPLY | P02/J_SUPPLYB; BOM P02 |
| VMOTOR | 200 mm | MSTB 5.08 3p >=12A z tulejkami, KEY VMOTOR | P07/J_VMOTORB; BOM P07 |
| LV03 | 200 mm | Mini-Fit Jr żeński 4p, styki Au, klucz LV03 | P03/J_LV03B; BOM P03 |
| LV04 | 200 mm | Mini-Fit Jr żeński 4p, styki Au, klucz LV04 | P04/J_LV04B; BOM P04 |
| LV05 | 200 mm | Mini-Fit Jr żeński 4p, styki Au, klucz LV05 | P05/J_LV05B; BOM P05 |
| LV06 | 200 mm | Mini-Fit Jr żeński 4p, styki Au, klucz LV06 | P06/J_LV06B; BOM P06 |
| LV07 | 200 mm | Mini-Fit Jr żeński 4p, styki Au, klucz LV07 | P07/J_LV07B; BOM P07 |
| LV08 | 200 mm | Mini-Fit Jr żeński 4p, styki Au, klucz LV08 | P08/J_LV08B; BOM P08 |
| LV09 | 200 mm | Mini-Fit Jr żeński 4p, styki Au, klucz LV09 | P09/J_LV09B; BOM P09 |
| LV10 | 200 mm | Mini-Fit Jr żeński 4p, styki Au, klucz LV10 | P10/J_LV10B; BOM P10 |

Montaż: Przewody mocy → TSR → pomiar obu szyn → sygnał PSU_OK.
Odbiór: oględziny obu stron, ciągłość pin–pin, brak zwarć sąsiednich żył, identyfikacja kluczy; następnie próby z ODBIOR.csv. Odłączać wyłącznie bez zasilania.

## P03 CORE
Wykonanie: **trwały montaż lutowany / nośnik / panel**. BOM: [hardware/P03-BOM.csv](../hardware/P03-BOM.csv).
Rezerwa obrysu 110 × 90 mm. Otwory z modules.json są założeniem do rozmieszczenia.
| Wiązka / łącze | Długość gotowa | Wtyk | Lutowany koniec / właściciel |
|---|---:|---|---|
| DAQ | 0 mm | TSW-108-07-G-D / SSW-108-01-G-D | BRAK przewodów; oba złącza lutowane do PCB; BOM BRAK |
| ILOG | 100 mm | IDC żeński 8p Au z odciążką, KEY 2 | P06/J_ILOGB; BOM P06 |
| ITEST | 100 mm | IDC żeński 6p Au z odciążką, KEY 2 | P07/J_ITESTB; BOM P07 |
| SAFE | 150 mm | IDC żeński 16p Au z odciążką, KEY 4 | P04/J_SAFEB; BOM P04 |
| DIR | 150 mm | IDC żeński 8p Au z odciążką, KEY 4 | P07/J_DIRB; BOM P07 |
| SFAULT | 150 mm | IDC żeński 6p Au z odciążką, KEY 3 | P08/J_SFAULTB; BOM P08 |
| TEMP | 100 mm | IDC żeński 10p Au z odciążką, KEY 4 | P09/J_TEMPB; BOM P09 |
| CAN | 150 mm | IDC żeński 4p Au z odciążką, KEY 4 | P10/J_CANB; BOM P10 |
| PANELCORE | 300 mm | Mini-Fit Jr żeński 8p, styki Au, klucz PANELCORE | P11/J_PANELCOREB; BOM P11 |
| LV03 | 200 mm | Mini-Fit Jr żeński 4p, styki Au, klucz LV03 | P03/J_LV03B; BOM P03 |

Montaż: Podstawki MCU/SD → zasilanie → bufory i rezystory → B2B DAQ → wgrywanie CORE.
Odbiór: oględziny obu stron, ciągłość pin–pin, brak zwarć sąsiednich żył, identyfikacja kluczy; następnie próby z ODBIOR.csv. Odłączać wyłącznie bez zasilania.

## P04 SAFE
Wykonanie: **trwały montaż lutowany / nośnik / panel**. BOM: [hardware/P04-BOM.csv](../hardware/P04-BOM.csv).
Rezerwa obrysu 100 × 80 mm. Otwory z modules.json są założeniem do rozmieszczenia.
| Wiązka / łącze | Długość gotowa | Wtyk | Lutowany koniec / właściciel |
|---|---:|---|---|
| SAFE | 150 mm | IDC żeński 16p Au z odciążką, KEY 4 | P04/J_SAFEB; BOM P04 |
| DRIVE | 150 mm | IDC żeński 10p Au z odciążką, KEY 2 | P07/J_DRIVEB; BOM P07 |
| SENSOR | 150 mm | IDC żeński 4p Au z odciążką, KEY 2 | P08/J_SENSORB; BOM P08 |
| DAQOK | 150 mm | IDC żeński 6p Au z odciążką, KEY 4 | P05/J_DAQOKB; BOM P05 |
| PSUOK | 150 mm | IDC żeński 6p Au z odciążką, KEY 5 | P02/J_PSUOKB; BOM P02 |
| PG | 200 mm | Mini-Fit Jr żeński 6p, styki Au, klucz PG | P01/J_PGB; BOM P01 |
| PANELSAFE | 300 mm | Mini-Fit Jr żeński 10p, styki Au, klucz PANELSAFE | P11/J_PANELSAFEB; BOM P11 |
| LV04 | 200 mm | Mini-Fit Jr żeński 4p, styki Au, klucz LV04 | P04/J_LV04B; BOM P04 |

Montaż: Masa/100nF → bramki i nadzór → watchdog → latch/ARM → próby P00.
Odbiór: oględziny obu stron, ciągłość pin–pin, brak zwarć sąsiednich żył, identyfikacja kluczy; następnie próby z ODBIOR.csv. Odłączać wyłącznie bez zasilania.

## P05 DAQ
Wykonanie: **PCB dwuwarstwowa zamawiana**. BOM: [hardware/P05-BOM.csv](../hardware/P05-BOM.csv).
Rezerwa obrysu 110 × 100 mm. Otwory z modules.json są założeniem do rozmieszczenia.
| Wiązka / łącze | Długość gotowa | Wtyk | Lutowany koniec / właściciel |
|---|---:|---|---|
| DAQ | 0 mm | TSW-108-07-G-D / SSW-108-01-G-D | BRAK przewodów; oba złącza lutowane do PCB; BOM BRAK |
| DAQOK | 150 mm | IDC żeński 6p Au z odciążką, KEY 4 | P05/J_DAQOKB; BOM P05 |
| LV05 | 200 mm | Mini-Fit Jr żeński 4p, styki Au, klucz LV05 | P05/J_LV05B; BOM P05 |
| TAPS | 50 mm | Mini-Fit Jr żeński 12p, styki Au, klucz TAPS | P05/J_TAPSB; BOM P05 |

Montaż: ADC i kondensatory lokalne → referencja → analog/dzielniki → bufory/B2B → pomiar znanych napięć.
Odbiór: oględziny obu stron, ciągłość pin–pin, brak zwarć sąsiednich żył, identyfikacja kluczy; następnie próby z ODBIOR.csv. Odłączać wyłącznie bez zasilania.

## P06 I-LOGGER
Wykonanie: **trwały montaż lutowany / nośnik / panel**. BOM: [hardware/P06-BOM.csv](../hardware/P06-BOM.csv).
Rezerwa obrysu 80 × 65 mm. Otwory z modules.json są założeniem do rozmieszczenia.
| Wiązka / łącze | Długość gotowa | Wtyk | Lutowany koniec / właściciel |
|---|---:|---|---|
| ILOG | 100 mm | IDC żeński 8p Au z odciążką, KEY 2 | P06/J_ILOGB; BOM P06 |
| LV06 | 200 mm | Mini-Fit Jr żeński 4p, styki Au, klucz LV06 | P06/J_LV06B; BOM P06 |
| ISERIES | 150 mm | MSTB 5.08 4p >=12A z tulejkami, KEY ISERIES | P06/J_ISERIESB; BOM P06 |

Montaż: Bocznik i Kelvin → INA/REF → MCP3201 → bufory → zero i oba znaki prądu.
Odbiór: oględziny obu stron, ciągłość pin–pin, brak zwarć sąsiednich żył, identyfikacja kluczy; następnie próby z ODBIOR.csv. Odłączać wyłącznie bez zasilania.

## P07 DRIVE
Wykonanie: **PCB dwuwarstwowa zamawiana**. BOM: [hardware/P07-BOM.csv](../hardware/P07-BOM.csv).
Rezerwa obrysu 120 × 100 mm. Otwory z modules.json są założeniem do rozmieszczenia.
| Wiązka / łącze | Długość gotowa | Wtyk | Lutowany koniec / właściciel |
|---|---:|---|---|
| ITEST | 100 mm | IDC żeński 6p Au z odciążką, KEY 2 | P07/J_ITESTB; BOM P07 |
| DRIVE | 150 mm | IDC żeński 10p Au z odciążką, KEY 2 | P07/J_DRIVEB; BOM P07 |
| DIR | 150 mm | IDC żeński 8p Au z odciążką, KEY 4 | P07/J_DIRB; BOM P07 |
| VMOTOR | 200 mm | MSTB 5.08 3p >=12A z tulejkami, KEY VMOTOR | P07/J_VMOTORB; BOM P07 |
| LV07 | 200 mm | Mini-Fit Jr żeński 4p, styki Au, klucz LV07 | P07/J_LV07B; BOM P07 |
| TMOTOR | 150 mm | MSTB 5.08 5p >=12A z tulejkami, KEY TMOTOR | P11/J_TMOTORB; BOM P11 |

Montaż: Zasilanie/OC bez mostka → latch → nośnik VNH5019 → obciążenie sztuczne.
Gotowe VNH5019 / MAX31856 zachowują listwy i gniazda na swoim nośniku; nie lutować taśmy do gotowego modułu.
Odbiór: oględziny obu stron, ciągłość pin–pin, brak zwarć sąsiednich żył, identyfikacja kluczy; następnie próby z ODBIOR.csv. Odłączać wyłącznie bez zasilania.

## P08 SENSOR
Wykonanie: **trwały montaż lutowany / nośnik / panel**. BOM: [hardware/P08-BOM.csv](../hardware/P08-BOM.csv).
Rezerwa obrysu 65 × 55 mm. Otwory z modules.json są założeniem do rozmieszczenia.
| Wiązka / łącze | Długość gotowa | Wtyk | Lutowany koniec / właściciel |
|---|---:|---|---|
| SENSOR | 150 mm | IDC żeński 4p Au z odciążką, KEY 2 | P08/J_SENSORB; BOM P08 |
| SFAULT | 150 mm | IDC żeński 6p Au z odciążką, KEY 3 | P08/J_SFAULTB; BOM P08 |
| LV08 | 200 mm | Mini-Fit Jr żeński 4p, styki Au, klucz LV08 | P08/J_LV08B; BOM P08 |
| TSENSOR | 150 mm | Mini-Fit Jr żeński 2p, styki Au, klucz TSENSOR | P11/J_TSENSORB; BOM P11 |

Montaż: Stabilne 5V → ogranicznik TPS → przekaźnik → SENSOR_OK.
Odbiór: oględziny obu stron, ciągłość pin–pin, brak zwarć sąsiednich żył, identyfikacja kluczy; następnie próby z ODBIOR.csv. Odłączać wyłącznie bez zasilania.

## P09 TEMP
Wykonanie: **trwały montaż lutowany / nośnik / panel**. BOM: [hardware/P09-BOM.csv](../hardware/P09-BOM.csv).
Rezerwa obrysu 75 × 55 mm. Otwory z modules.json są założeniem do rozmieszczenia.
| Wiązka / łącze | Długość gotowa | Wtyk | Lutowany koniec / właściciel |
|---|---:|---|---|
| TEMP | 100 mm | IDC żeński 10p Au z odciążką, KEY 4 | P09/J_TEMPB; BOM P09 |
| LV09 | 200 mm | Mini-Fit Jr żeński 4p, styki Au, klucz LV09 | P09/J_LV09B; BOM P09 |

Montaż: Podstawki MAX31856 → bufory → próby dwóch termopar.
Gotowe VNH5019 / MAX31856 zachowują listwy i gniazda na swoim nośniku; nie lutować taśmy do gotowego modułu.
Odbiór: oględziny obu stron, ciągłość pin–pin, brak zwarć sąsiednich żył, identyfikacja kluczy; następnie próby z ODBIOR.csv. Odłączać wyłącznie bez zasilania.

## P10 CAN
Wykonanie: **trwały montaż lutowany / nośnik / panel**. BOM: [hardware/P10-BOM.csv](../hardware/P10-BOM.csv).
Rezerwa obrysu 60 × 50 mm. Otwory z modules.json są założeniem do rozmieszczenia.
| Wiązka / łącze | Długość gotowa | Wtyk | Lutowany koniec / właściciel |
|---|---:|---|---|
| CAN | 150 mm | IDC żeński 4p Au z odciążką, KEY 4 | P10/J_CANB; BOM P10 |
| LV10 | 200 mm | Mini-Fit Jr żeński 4p, styki Au, klucz LV10 | P10/J_LV10B; BOM P10 |

Montaż: Transceiver/ESD → odbiór CAN na stanowisku → listen-only w aucie.
Odbiór: oględziny obu stron, ciągłość pin–pin, brak zwarć sąsiednich żył, identyfikacja kluczy; następnie próby z ODBIOR.csv. Odłączać wyłącznie bez zasilania.

## P11 PANEL
Wykonanie: **trwały montaż lutowany / nośnik / panel**. BOM: [hardware/P11-BOM.csv](../hardware/P11-BOM.csv).
Rezerwa obrysu 100 × 60 mm. Otwory z modules.json są założeniem do rozmieszczenia.
| Wiązka / łącze | Długość gotowa | Wtyk | Lutowany koniec / właściciel |
|---|---:|---|---|
| PANELSAFE | 300 mm | Mini-Fit Jr żeński 10p, styki Au, klucz PANELSAFE | P11/J_PANELSAFEB; BOM P11 |
| PANELCORE | 300 mm | Mini-Fit Jr żeński 8p, styki Au, klucz PANELCORE | P11/J_PANELCOREB; BOM P11 |
| TAPS | 50 mm | Mini-Fit Jr żeński 12p, styki Au, klucz TAPS | P05/J_TAPSB; BOM P05 |
| ISERIES | 150 mm | MSTB 5.08 4p >=12A z tulejkami, KEY ISERIES | P06/J_ISERIESB; BOM P06 |
| TMOTOR | 150 mm | MSTB 5.08 5p >=12A z tulejkami, KEY TMOTOR | P11/J_TMOTORB; BOM P11 |
| TSENSOR | 150 mm | Mini-Fit Jr żeński 2p, styki Au, klucz TSENSOR | P11/J_TSENSORB; BOM P11 |
| EXT_T | 1000 mm | DEUTSCH DT06-12SA + DT04-12PA | BRAK: zaciskane styki DEUTSCH na obu końcach; BOM AT |
| EXT_L1 | 1000 mm | DEUTSCH DT06-12SB + DT04-12PB | BRAK: zaciskane styki DEUTSCH na obu końcach; BOM AL1 |
| EXT_L2 | 1000 mm | DEUTSCH DT06-12SC + DT04-12PC | BRAK: zaciskane styki DEUTSCH na obu końcach; BOM AL2 |

Montaż: Złącza i mikrowyłączniki → wiązki mocy → sygnały → test braku pomyłek.
Odbiór: oględziny obu stron, ciągłość pin–pin, brak zwarć sąsiednich żył, identyfikacja kluczy; następnie próby z ODBIOR.csv. Odłączać wyłącznie bez zasilania.
