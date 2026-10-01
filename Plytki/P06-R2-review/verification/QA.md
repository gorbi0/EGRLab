# P06-R2 — QA schematu (plik generowany przez src/run_schematic.py)

ERC: 0 naruszeń na 7 arkuszach. Netlista: 74 części, 243 pinów sprawdzonych pin po pinie względem `parts.py`, 0 błędów, 54 sieci.

Kontrole elektryczne (`verify_electrical.py`): 33/33 PASS; mutacje 30/30 wykrytych.
Filtr: τ nominalnie 1200.9 µs (132.5 Hz), pasmo z tolerancją R 0,1 % i C1 X7R ±10 % / temperatura: 918–1388 µs. Dzielnik 1:2 w narożnikach (0,1 % + 25 ppm/K × 50 K): 0.498875–0.501125.
C3 220 µF: energia ładowania przy 5,25 V 3.03 mJ (tyle wydziela R6), τ = R6·C3 = 220 µs. Pojemność na 5V_SYS: P06 220.3 µF + P05 R3 265.7 µF wobec 600 µF (TSR 2-2450). R21: 0.64 W przy 5,00 V, 0.71 W przy 5,25 V (PR02 2 W).

Kontrakt S1 (`verify_s1.py`): 27/27 PASS; mutacje 37/37 wykrytych przez kontrolę docelową; próba zerowa: czysta.

| Kontrola S1 | Wynik |
|---|---|
| JBP-PINOUT | PASS |
| JBP-FOOTPRINT | PASS |
| JBP-BUS-PINS-AS-P03R6-P05R3 | PASS |
| JBP-ODD-PINS-GND | PASS |
| JBP-OLD-NETS-EXACTLY-ONCE | PASS |
| JBP-NO-ISERIES-BYPASS | PASS |
| CSV-J_BP | PASS |
| CSV-DIRECTIONS-VS-P03R6 | PASS |
| J_SV1-MAX-13-PINS | PASS |
| J_SV1-GND-ENDS | PASS |
| J_SV1-SERIES-R-AT-NODE-CLASS | PASS |
| J_SV1-GROUP | PASS |
| J_SV1-NEIGHBOURS | PASS |
| J_SV2-MAX-13-PINS | PASS |
| J_SV2-GND-ENDS | PASS |
| J_SV2-SERIES-R-AT-NODE-CLASS | PASS |
| J_SV2-GROUP | PASS |
| J_SV2-NEIGHBOURS | PASS |
| SRV-EACH-NODE-ONCE | PASS |
| SRV-COVERS-R1-TESTPADS | PASS |
| CSV-SERWIS | PASS |
| RSH1-KELVIN-2512 | PASS |
| RSH1-5MOHM | PASS |
| C3-220U | PASS |
| PARTS-S1-SOURCES | PASS |
| PARTS-PRECISION-SERIES | PASS |
| R1-CIRCUIT-KEPT | PASS |

| Kontrola elektryczna | Wynik | Uwagi |
|---|---|---|
| IF-JBP | PASS | R2: J1 LV06 + J2 ILOG -> J_BP (task ZADANIE-P06-S1 2). |
| JBP-FUNCTIONS | PASS | Each J_BP signal reaches the same element as R1 J1/J2. |
| IF-ISERIES | PASS | R2 local layout 1.10: 2 pads (R1 pads 3/4 were empty). |
| INA-SOIC-PINS | PASS |  |
| INA-GAIN-MPN | PASS |  |
| KELVIN | PASS |  |
| SHUNT-VALUE | PASS | R2: Kelvin SMD 2512 (pads 1/4 force, 2/3 sense; geometry checked in verify_s1.py). |
| INPUT-RESISTORS | PASS | Matched 0.1 % thin film (Yageo RT ...BR... = 0.1 %). |
| OPAMP-FEEDBACK | PASS |  |
| REF-PINS | PASS |  |
| REF-COMPENSATION | PASS | MCP1525 CL 1..10 uF; C5 effective 2.52..5.95 uF. |
| LDO-OUTPUT-CAP | PASS | MCP1702 COUT >= 1 uF ceramic; C4 effective >= 2.52 uF. |
| ADC-PINS | PASS |  |
| DIVIDER | PASS | R2: 5.11K 0.1 % 25 ppm/K (list 2 replacement 1:1 for 5K1); ratio 1:2 unchanged. |
| INA-LOAD-GE10K | PASS | Swing specification uses 10k load to GND; divider 10.22k (10.21k at -0.1 %). |
| LPF | PASS | Nominal tau 1.2008ms / 132.54Hz; not a brick-wall anti-alias filter. |
| ADC-DRIVE | PASS |  |
| LDO | PASS |  |
| NO-PARALLEL-LDO | PASS | 3V3_IO only to J_BP.14 and its service resistor (R1: J1.3 and TP4). |
| C3-220U | PASS | Decision 1.10: 220 uF (was 470 uF). |
| R6-POWER | PASS | 1 R / 1 W lying; C3 charge pulse ~3 mJ. |
| SUP3 | PASS |  |
| SUP5 | PASS |  |
| DIODE-DIRECTION | PASS |  |
| IOFF-MPN | PASS |  |
| SPI-TRISTATE | PASS |  |
| SPI-IDLE | PASS |  |
| READY-LEVEL-TRANSLATION | PASS |  |
| READY-PULLDOWNS | PASS |  |
| READY-SERIES | PASS |  |
| BYPASS-WIRING | PASS |  |
| WETTING | PASS |  |
| READY-TRUTH | PASS | Eight combinations from exported gate wiring. |

## Próby ujemne S1

| Mutacja | Kontrola docelowa | Wykryta | Zgłosiły |
|---|---|---|---|
| CS_ILOG_N and LOGGER_CURRENT_OK swapped | JBP-PINOUT | tak | JBP-PINOUT, CSV-J_BP |
| vertical IDC header | JBP-FOOTPRINT | tak | JBP-FOOTPRINT |
| ADC_SCLK and ADC_DOUTA swapped | JBP-BUS-PINS-AS-P03R6-P05R3 | tak | JBP-PINOUT, JBP-BUS-PINS-AS-P03R6-P05R3, CSV-J_BP |
| odd pin 15 carries 3V3_IO | JBP-ODD-PINS-GND | tak | JBP-PINOUT, JBP-ODD-PINS-GND, JBP-OLD-NETS-EXACTLY-ONCE, CSV-J_BP |
| second 5V_SYS pin lost | JBP-OLD-NETS-EXACTLY-ONCE | tak | JBP-PINOUT, JBP-OLD-NETS-EXACTLY-ONCE, CSV-J_BP |
| CS_ILOG_N duplicated on reserve pin 16 | JBP-OLD-NETS-EXACTLY-ONCE | tak | JBP-PINOUT, JBP-OLD-NETS-EXACTLY-ONCE, CSV-J_BP |
| SW_RAW routed to reserve pin 16 | JBP-NO-ISERIES-BYPASS | tak | JBP-PINOUT, JBP-OLD-NETS-EXACTLY-ONCE, JBP-NO-ISERIES-BYPASS, CSV-J_BP |
| 14th pin on J_SV2 | J_SV2-MAX-13-PINS | tak | J_SV2-MAX-13-PINS, CSV-SERWIS |
| J_SV1 vertical header | J_SV1-MAX-13-PINS | tak | J_SV1-MAX-13-PINS |
| first pin of J_SV1 not GND | J_SV1-GND-ENDS | tak | J_SV1-GND-ENDS, J_SV1-SERIES-R-AT-NODE-CLASS, CSV-SERWIS |
| last pin of J_SV2 not GND | J_SV2-GND-ENDS | tak | J_SV2-GND-ENDS, J_SV2-SERIES-R-AT-NODE-CLASS, CSV-SERWIS |
| 3V3_IO next to SHUNT_ENABLED (1K logic) | J_SV2-NEIGHBOURS | tak | J_SV2-NEIGHBOURS, CSV-SERWIS |
| interior GND pin 5 swapped with SHUNT_ENABLED (3V3_P06 next to 1K logic) | J_SV2-NEIGHBOURS | tak | J_SV2-NEIGHBOURS, CSV-SERWIS |
| rail on the analog strip next to I_L_OUT (ADC_AIN resistor moved to 5VA_P06) | J_SV1-NEIGHBOURS | tak | J_SV1-SERIES-R-AT-NODE-CLASS, J_SV1-GROUP, J_SV1-NEIGHBOURS, SRV-EACH-NODE-ONCE, SRV-COVERS-R1-TESTPADS |
| logic node on the analog strip | J_SV1-GROUP | tak | J_SV1-SERIES-R-AT-NODE-CLASS, J_SV1-GROUP, SRV-COVERS-R1-TESTPADS |
| analog node on the rail/logic strip | J_SV2-GROUP | tak | J_SV2-SERIES-R-AT-NODE-CLASS, J_SV2-GROUP, SRV-COVERS-R1-TESTPADS |
| pin wired straight to the node (no resistor) | J_SV2-SERIES-R-AT-NODE-CLASS | tak | J_SV2-SERIES-R-AT-NODE-CLASS, SRV-COVERS-R1-TESTPADS, CSV-SERWIS |
| REF25 through 1K instead of 10K | J_SV1-SERIES-R-AT-NODE-CLASS | tak | J_SV1-SERIES-R-AT-NODE-CLASS, CSV-SERWIS |
| SUP3_N through 1K instead of 10K | J_SV2-SERIES-R-AT-NODE-CLASS | tak | J_SV2-SERIES-R-AT-NODE-CLASS, CSV-SERWIS |
| service resistor shorted | J_SV2-SERIES-R-AT-NODE-CLASS | tak | J_SV2-SERIES-R-AT-NODE-CLASS, J_SV2-NEIGHBOURS, SRV-COVERS-R1-TESTPADS, CSV-SERWIS |
| same node on both strips | SRV-EACH-NODE-ONCE | tak | J_SV2-SERIES-R-AT-NODE-CLASS, J_SV2-GROUP, SRV-EACH-NODE-ONCE, SRV-COVERS-R1-TESTPADS |
| CLK_LOCAL missing (resistor on a dead net) | SRV-COVERS-R1-TESTPADS | tak | J_SV2-SERIES-R-AT-NODE-CLASS, J_SV2-GROUP, SRV-COVERS-R1-TESTPADS |
| J_BP.csv out of date (netlist moved 3V3_IO) | CSV-J_BP | tak | JBP-PINOUT, CSV-J_BP |
| SERWIS.csv out of date (strip order changed) | CSV-SERWIS | tak | CSV-SERWIS |
| resistor value differs from SERWIS.csv | CSV-SERWIS | tak | J_SV2-SERIES-R-AT-NODE-CLASS, CSV-SERWIS |
| force and sense swapped on the ECU end | RSH1-KELVIN-2512 | tak | RSH1-KELVIN-2512 |
| Kelvin pair crossed | RSH1-KELVIN-2512 | tak | RSH1-KELVIN-2512 |
| shunt in a 2-pad 2512 | RSH1-KELVIN-2512 | tak | RSH1-KELVIN-2512, PARTS-S1-SOURCES |
| shunt 50 mOhm | RSH1-5MOHM | tak | RSH1-5MOHM |
| C3 back to 470 uF | C3-220U | tak | C3-220U |
| new resistor as 0805 | PARTS-S1-SOURCES | tak | PARTS-S1-SOURCES |
| standing THT resistor not from the register | PARTS-S1-SOURCES | tak | PARTS-S1-SOURCES |
| electrolytic outside the C3 exception | PARTS-S1-SOURCES | tak | PARTS-S1-SOURCES |
| R21 as 2512 without justification in the exception list | PARTS-S1-SOURCES | tak | PARTS-S1-SOURCES |
| divider resistor R3 1 % | PARTS-PRECISION-SERIES | tak | PARTS-PRECISION-SERIES |
| INA240 inputs swapped | R1-CIRCUIT-KEPT | tak | R1-CIRCUIT-KEPT |
| BYPASS commons moved | R1-CIRCUIT-KEPT | tak | R1-CIRCUIT-KEPT |
| null control (no change) | — | nie | — |

## Próby ujemne elektryczne

| Mutacja | Wykryta | Zgłosiły |
|---|---|---|
| wrong INA package pin | tak | INA-SOIC-PINS |
| wrong gain | tak | INA-GAIN-MPN |
| shunt 50m | tak | SHUNT-VALUE |
| Kelvin from force | tak | KELVIN |
| wrong divider | tak | DIVIDER, LPF |
| old 5K1 divider | tak | DIVIDER |
| divider 1 % | tak | DIVIDER |
| old filter cap | tak | LPF |
| REF reversed | tak | REF-PINS |
| REF cap missing compensation | tak | REF-COMPENSATION |
| REF cap too large | tak | REF-COMPENSATION |
| LDO cap too small | tak | LDO-OUTPUT-CAP |
| ADC CS/DOUT swapped | tak | ADC-PINS |
| MISO permanently enabled | tak | SPI-TRISTATE |
| HC in place of LVC | tak | IOFF-MPN |
| AND ready bypassed | tak | READY-TRUTH |
| wrong bypass common | tak | BYPASS-WIRING |
| wetting 39k | tak | WETTING |
| wetting resistor 1 W 2512 | tak | WETTING |
| strong external CS pullup backpowers rail | tak | SPI-IDLE |
| missing ready default | tak | READY-PULLDOWNS |
| wrong 5V supervisor | tak | SUP5 |
| wrong LDO pin | tak | LDO |
| discharge diode reversed | tak | DIODE-DIRECTION |
| C3 back to 470u | tak | C3-220U |
| 3V3_IO tied to local 3V3 | tak | NO-PARALLEL-LDO |
| J_BP CS on reserve pin | tak | IF-JBP |
| J_BP 5V_SYS lost | tak | IF-JBP |
| ISERIES pin swap | tak | IF-ISERIES |
| R6 0.6 W | tak | R6-POWER |

Tylko schemat: PCB nie powstało (layout robi sesja lokalna). Kontrole plików nie zastępują odbioru na sprzęcie (`docs/ODBIOR.md`).
Ostrzeżenie kicad-cli „schemat posiada błędy numeracji” dotyczy oznaczenia `J_BP` bez numeru (nazwa z zadania, jak w P02 R4); ERC go nie zgłasza.
