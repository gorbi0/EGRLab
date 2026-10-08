# M1-R1 — QA schematu (plik generowany przez src/make_qa.py)

Części na płytce: 91 (+ 2 DNP), w tym 10 pól testowych bez elementu. Poza płytką: listwa X1, IBT-2, BMS, pakiet.
ERC: 0 naruszeń na 7 arkuszach. Netlista: 93 części, 357 pinów sprawdzonych pin po pinie względem `parts.py`, 0 błędów, 99 sieci.
Kontrole M1 (`verify_m1.py`): 8/8 PASS; mutacje 15/15 wykrytych przez kontrolę docelową; próba zerowa: czysta.

| Kontrola | Wynik | Uwagi |
|---|---|---|
| X1 | PASS | 16 X1 rows, wire pads J1/J2/J5/J6 all listed |
| GPIO | PASS | 36 module GPIOs vs SPECYFIKACJA 3; forbidden [0, 19, 20, 33, 34, 35, 36, 37, 43, 44, 45, 46, 47, 48] NC; 5 V in J1-21, module 3V3 not tied |
| ADC | PASS | CH1 P1_EGR: FS 40.6 V; CH2 P3: FS 40.6 V; CH3 P4: FS 10.2 V; CH4 P5: FS 10.2 V; CH5 P6: FS 10.2 V; CH7 VBAT_CAR: FS 60.9 V; CH8 SENS_5V: FS 10.2 V |
| PRAD | PASS | INA240A2: 0.250 V/A around 2.5 V; linear +-9.2 A (need +-8.0 A > F1 7.5 A) |
| START | PASS | bridge inputs and sensor supply off while the ESP32 is in reset; CS lines idle high |
| MISO | PASS | 3 MISO sources: SD1 + U5 gates enabled by the matching module CS |
| ZASILANIE | PASS | 5V: 508 mA / 2000 mA; 3V3: 113 mA / 2000 mA (peak, derated to 50 %) |
| SIECI | PASS | no net with a single pin |

## Próby ujemne

| Mutacja | Kontrola docelowa | Wykryta | Zgłosiły |
|---|---|---|---|
| J6.1 swapped with J6.2 (P3 / P4) | X1 | tak | X1 |
| LPWM back on GPIO38 (module RGB LED) | GPIO | tak | GPIO |
| GPIO0 (strap) used for BTN | GPIO | tak | GPIO |
| module 3V3 tied to the board 3V3 | GPIO | tak | GPIO |
| CH1 divider bottom removed (100k only into 1M) | ADC | tak | ADC |
| CH7 without RC | ADC | tak | ADC |
| Kelvin pins swapped | PRAD | tak | PRAD |
| INA240 REF1 on GND (unidirectional) | PRAD | tak | PRAD |
| DRIVE_EN pull-down removed | START | tak | START |
| U7 OE on 3V3 | START | tak | START |
| TC2 SDO straight on MISO | MISO | tak | MISO, SIECI |
| buffer OE swapped (TC1 gate on TC2_CS) | MISO | tak | MISO |
| F1 bypassed (VMOTOR on BAT_P) | ZASILANIE | tak | X1, ZASILANIE |
| SD card on 5V | ZASILANIE | tak | ZASILANIE |
| button pull-up disconnected from BTN | SIECI | tak | SIECI |

Etap: schemat (krok 4 planu M1). PCB jeszcze nie powstało; kontrole plików nie zastępują odbioru na sprzęcie.
