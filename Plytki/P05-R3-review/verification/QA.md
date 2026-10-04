# P05-R3 — QA schematu (plik generowany przez src/run_schematic.py)

ERC: 0 naruszeń na 9 arkuszach. Netlista: 120 części, 468 pinów sprawdzonych pin po pinie względem `parts.py`, 0 błędów, 111 sieci.

Kontrole elektryczne (`verify_electrical.py`): 21/21 PASS; mutacje 12/12 wykrytych.
Okno DAQ_OK (10 ppm/K + 0,1 % na lutowanie/starzenie): dolny 4.7564–4.8445 V, górny 5.1414–5.2304 V.

Kontrakt S1 (`verify_s1.py`): 26/26 PASS; mutacje 33/33 wykrytych przez kontrolę docelową; próba zerowa: czysta.

| Kontrola S1 | Wynik |
|---|---|
| JBP1-PINOUT | PASS |
| JBP2-PINOUT | PASS |
| JBP-FOOTPRINTS | PASS |
| JBP2-DAQ-PINS-AS-P03R6 | PASS |
| JBP-ODD-PINS-GND | PASS |
| JBP-GND-AROUND-SCLK-MEAS_EN | PASS |
| JBP-OLD-NETS-EXACTLY-ONCE | PASS |
| JBP-3V3_IO-ABSENT | PASS |
| JBP-NO-TAPS-AUX | PASS |
| J_SV1-MAX-13-PINS | PASS |
| J_SV1-GND-ENDS | PASS |
| J_SV1-SERIES-R-AT-NODE-CLASS | PASS |
| J_SV1-GROUP | PASS |
| J_SV1-RAILS-NEXT-TO-GND-OR-RAIL | PASS |
| J_SV2-MAX-13-PINS | PASS |
| J_SV2-GND-ENDS | PASS |
| J_SV2-SERIES-R-AT-NODE-CLASS | PASS |
| J_SV2-GROUP | PASS |
| J_SV2-RAILS-NEXT-TO-GND-OR-RAIL | PASS |
| SRV-EACH-NODE-ONCE | PASS |
| SRV-COVERS-ODBIOR | PASS |
| CSV-J_BP | PASS |
| CSV-SERWIS | PASS |
| PARTS-S1-SOURCES | PASS |
| PARTS-PRECISION-SERIES | PASS |
| R2-CIRCUIT-KEPT | PASS |

| Kontrola elektryczna | Wynik |
|---|---|
| AD7606B all 64 physical pins | PASS |
| Separate REGCAP and reference capacitors | PASS |
| VDRIVE supplied from local AVCC-derived regulator | PASS |
| All digital supply pins share local domain | PASS |
| Open-collector window and supervisor bondout | PASS |
| READY and relay permit: actual HC08 truth table | PASS |
| RX ADC_SCLK | PASS |
| RX ADC_SDI | PASS |
| RX ADC_CS | PASS |
| RX ADC_CONVST | PASS |
| RX ADC_RESET | PASS |
| RX MEAS_EN | PASS |
| Defaults on both sides of RX buffers | PASS |
| Window reference REF50xx SOIC-8: 2 VIN, 4 GND, 6 VOUT, others open | PASS |
| MISO tri-state and BUSY Ioff output | PASS |
| Relay driver input/output/COM and pull-down | PASS |
| G6K NO contacts and coil polarity | PASS |
| Channel lower arms and grounded current placeholder | PASS |
| AUX switch: HI = AUX_HI + shunt, LO = AUX_LO without shunt (E-Switch M6 geometry) | PASS |
| Rail-window tolerance stays inside ADC static limits | PASS |
| Window corners as computed for R3 (10 ppm/K + 0.1 % allowance) | PASS |

## Próby ujemne S1

| Mutacja | Kontrola docelowa | Wykryta | Zgłosiły |
|---|---|---|---|
| DAQ_OK and VBAT_SENSE swapped | JBP1-PINOUT | tak | JBP1-PINOUT, CSV-J_BP |
| reserve pin 16 carries PFAIL_N as on P03 | JBP2-PINOUT | tak | JBP2-PINOUT, JBP-OLD-NETS-EXACTLY-ONCE, CSV-J_BP |
| J_BP2 vertical header | JBP-FOOTPRINTS | tak | JBP-FOOTPRINTS |
| SCLK and DOUTA swapped | JBP2-DAQ-PINS-AS-P03R6 | tak | JBP2-PINOUT, JBP2-DAQ-PINS-AS-P03R6, CSV-J_BP |
| odd pin 3 of J_BP1 carries DAQ_OK | JBP-ODD-PINS-GND | tak | JBP1-PINOUT, JBP-ODD-PINS-GND, JBP-OLD-NETS-EXACTLY-ONCE, CSV-J_BP |
| 5V_SYS next to MEAS_EN (pin 15) | JBP-GND-AROUND-SCLK-MEAS_EN | tak | JBP2-PINOUT, JBP-ODD-PINS-GND, JBP-GND-AROUND-SCLK-MEAS_EN, JBP-OLD-NETS-EXACTLY-ONCE, CSV-J_BP |
| second 5V_SYS pin lost | JBP-OLD-NETS-EXACTLY-ONCE | tak | JBP1-PINOUT, JBP-OLD-NETS-EXACTLY-ONCE, CSV-J_BP |
| DAQ_OK duplicated on reserve pin 20 | JBP-OLD-NETS-EXACTLY-ONCE | tak | JBP2-PINOUT, JBP-OLD-NETS-EXACTLY-ONCE, CSV-J_BP |
| 3V3_IO brought back on reserve pin 8 | JBP-3V3_IO-ABSENT | tak | JBP1-PINOUT, JBP-OLD-NETS-EXACTLY-ONCE, JBP-3V3_IO-ABSENT, CSV-J_BP |
| TAP_P1 routed to J_BP2 pin 16 | JBP-NO-TAPS-AUX | tak | JBP2-PINOUT, JBP-OLD-NETS-EXACTLY-ONCE, JBP-NO-TAPS-AUX, CSV-J_BP |
| 14th pin on J_SV2 | J_SV2-MAX-13-PINS | tak | J_SV2-MAX-13-PINS, CSV-SERWIS |
| J_SV1 vertical header | J_SV1-MAX-13-PINS | tak | J_SV1-MAX-13-PINS |
| first pin of J_SV1 not GND | J_SV1-GND-ENDS | tak | J_SV1-GND-ENDS, J_SV1-SERIES-R-AT-NODE-CLASS, J_SV1-RAILS-NEXT-TO-GND-OR-RAIL, CSV-SERWIS |
| last pin of J_SV2 not GND | J_SV2-GND-ENDS | tak | J_SV2-GND-ENDS, J_SV2-SERIES-R-AT-NODE-CLASS, CSV-SERWIS |
| REF_2V5 next to 3V3_DAQ (pins 7 and 8 swapped) | J_SV1-RAILS-NEXT-TO-GND-OR-RAIL | tak | J_SV1-RAILS-NEXT-TO-GND-OR-RAIL, CSV-SERWIS |
| VBAT_SENSE next to 5V_SYS (pins 2 and 3 swapped) | J_SV1-RAILS-NEXT-TO-GND-OR-RAIL | tak | J_SV1-RAILS-NEXT-TO-GND-OR-RAIL, CSV-SERWIS |
| DAQ node on the analog strip | J_SV1-GROUP | tak | J_SV1-SERIES-R-AT-NODE-CLASS, J_SV1-GROUP, SRV-EACH-NODE-ONCE |
| pin wired straight to the node (no resistor) | J_SV2-SERIES-R-AT-NODE-CLASS | tak | J_SV2-SERIES-R-AT-NODE-CLASS, SRV-COVERS-ODBIOR, CSV-SERWIS |
| REF_2V5 through 1K instead of 10K | J_SV1-SERIES-R-AT-NODE-CLASS | tak | J_SV1-SERIES-R-AT-NODE-CLASS, CSV-SERWIS |
| VBAT_SENSE through 1K instead of 4.7K | J_SV1-SERIES-R-AT-NODE-CLASS | tak | J_SV1-SERIES-R-AT-NODE-CLASS, CSV-SERWIS |
| service resistor shorted | J_SV1-SERIES-R-AT-NODE-CLASS | tak | J_SV1-SERIES-R-AT-NODE-CLASS, J_SV1-RAILS-NEXT-TO-GND-OR-RAIL, SRV-COVERS-ODBIOR, CSV-SERWIS |
| analog node on the DAQ strip | J_SV2-GROUP | tak | J_SV2-SERIES-R-AT-NODE-CLASS, J_SV2-GROUP, SRV-EACH-NODE-ONCE |
| same node on both strips | SRV-EACH-NODE-ONCE | tak | J_SV2-SERIES-R-AT-NODE-CLASS, SRV-EACH-NODE-ONCE |
| MEAS_COIL_LOW missing (resistor on a dead net) | SRV-COVERS-ODBIOR | tak | J_SV1-SERIES-R-AT-NODE-CLASS, J_SV1-GROUP, SRV-COVERS-ODBIOR |
| J_BP.csv out of date (netlist moved MEAS_EN) | CSV-J_BP | tak | JBP2-PINOUT, JBP2-DAQ-PINS-AS-P03R6, CSV-J_BP |
| SERWIS.csv out of date (strip order changed) | CSV-SERWIS | tak | CSV-SERWIS |
| resistor value differs from SERWIS.csv (R45 10K) | CSV-SERWIS | tak | J_SV2-SERIES-R-AT-NODE-CLASS, CSV-SERWIS |
| new resistor as 0805 | PARTS-S1-SOURCES | tak | PARTS-S1-SOURCES |
| standing THT resistor not from the register | PARTS-S1-SOURCES | tak | PARTS-S1-SOURCES |
| 1210 outside the C12/C13 exception | PARTS-S1-SOURCES | tak | PARTS-S1-SOURCES |
| window resistor R5 at 25 ppm/K | PARTS-PRECISION-SERIES | tak | PARTS-PRECISION-SERIES |
| comparator inputs swapped | R2-CIRCUIT-KEPT | tak | R2-CIRCUIT-KEPT |
| SW1 pole B mirrored (JS202011AQN mapping) | R2-CIRCUIT-KEPT | tak | R2-CIRCUIT-KEPT |
| null control (no change) | — | nie | — |

## Próby ujemne elektryczne

| Mutacja | Kontrola docelowa | Wykryta |
|---|---|---|
| WR wrongly grounded | AD7606B all 64 physical pins | tak |
| REGCAPs shorted | Separate REGCAP and reference capacitors | tak |
| Independent VDRIVE supply | VDRIVE supplied from local AVCC-derived regulator | tak |
| READY bypasses SUP3 | READY and relay permit: actual HC08 truth table | tak |
| Relay permit bypasses READY | READY and relay permit: actual HC08 truth table | tak |
| MISO always enabled | MISO tri-state and BUSY Ioff output | tak |
| Relay on NC terminal | G6K NO contacts and coil polarity | tak |
| AUX LO still shunted (pole B mirrored as for the JS slide) | AUX switch: HI = AUX_HI + shunt, LO = AUX_LO without shunt (E-Switch M6 geometry) | tak |
| Missing CS default | Defaults on both sides of RX buffers | tak |
| REF TEMP pin loaded | Window reference REF50xx SOIC-8: 2 VIN, 4 GND, 6 VOUT, others open | tak |
| CH7 back on VPROT | Channel lower arms and grounded current placeholder | tak |
| window resistors 25 ppm/K (RT1206BRD07) with 0.1 % allowance | Rail-window tolerance stays inside ADC static limits | tak |

Tylko schemat: PCB nie powstało (layout robi sesja lokalna). Kontrole plików nie zastępują odbioru na sprzęcie (`docs/ODBIOR.md`).
