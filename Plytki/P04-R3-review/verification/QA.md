# P04-R3 — QA schematu (plik generowany przez src/run_schematic.py)

ERC: 0 naruszeń na 7 arkuszach. Netlista: 100 części, 397 pinów sprawdzonych pin po pinie względem `parts.py`, 0 błędów, 95 sieci.

Kontrole elektryczne R2.2 (`verify_electrical.py`, tabele prawdy 131072 wierszy): 22/22 PASS; mutacje 16/16 wykrytych.
Wartości i MPN (`verify_values.py`): 10/10 PASS; mutacje 24/24 wykrytych.
Budżet resetu z P03 R6 (`verify_reset.py`): 7/7 PASS; mutacje 4/4 wykrytych.

Kontrakt S1 i P12 (`verify_s1.py`): 34/34 PASS; mutacje 42/42 wykrytych przez kontrolę docelową; próba zerowa: czysta.

| Kontrola S1 / P12 | Wynik |
|---|---|
| J_BP1-PINOUT | PASS |
| J_BP1-FOOTPRINT | PASS |
| J_BP2-PINOUT | PASS |
| J_BP2-FOOTPRINT | PASS |
| J_BP3-PINOUT | PASS |
| J_BP3-FOOTPRINT | PASS |
| JBP-ODD-PINS-GND | PASS |
| JBP-R22-CONNECTOR-NETS-EXACTLY-ONCE | PASS |
| JBP-PINS-AS-COUNTERPARTS | PASS |
| P12-WAITING-NETS-ON-JBP | PASS |
| P12-ONE-TRANSMITTER | PASS |
| P12-NO-FOREIGN-NAMES | PASS |
| P12-POWER-NOT-SOURCED | PASS |
| P07-DRIVE-NAMES-AS-R22 | PASS |
| P08-SENSOR-NAMES-AS-R22-AND-P08R1 | PASS |
| CSV-J_BP | PASS |
| CSV-DIRECTIONS | PASS |
| J_SV1-MAX-13-PINS | PASS |
| J_SV1-GND-ENDS | PASS |
| J_SV1-SERIES-R-AT-NODE-CLASS | PASS |
| J_SV1-NEIGHBOURS | PASS |
| J_SV2-MAX-13-PINS | PASS |
| J_SV2-GND-ENDS | PASS |
| J_SV2-SERIES-R-AT-NODE-CLASS | PASS |
| J_SV2-NEIGHBOURS | PASS |
| J_SV3-MAX-13-PINS | PASS |
| J_SV3-GND-ENDS | PASS |
| J_SV3-SERIES-R-AT-NODE-CLASS | PASS |
| J_SV3-NEIGHBOURS | PASS |
| SRV-EACH-NODE-ONCE | PASS |
| SRV-COVERS-R22-TESTPADS | PASS |
| CSV-SERWIS | PASS |
| PARTS-S1-SOURCES | PASS |
| R22-CIRCUIT-KEPT | PASS |

| Kontrola elektryczna | Wynik |
|---|---|
| Watchdog pinout and independent clear | PASS |
| Watchdog capacitor is between 15 and 14, never ground | PASS |
| Local supervisor D bondout | PASS |
| Both supervisors qualify watchdog | PASS |
| Latch and Schmitt conditioning | PASS |
| ARM contact topology | PASS |
| SAFE_N has only one passive pull-up and open collectors | PASS |
| Panel contacts reach the gates only through R41/R42 1 k; pulldowns on the gate side | PASS |
| 3V3 leaves the board only through current-limiting resistors (R38/R39 1 k, R40 100 R) | PASS |
| Watchdog clears the latch and both permits without Q1 (single-fault) | PASS |
| All command/READY ports mapped | PASS |
| Input and post-buffer pull-downs | PASS |
| Exact Ioff buffer and unused channel safe | PASS |
| One decoupler per IC plus second 100n at U8-U10 (R2.2 adapter capacitors) | PASS |
| DRIVE and SENSOR nets leave on J_BP with the R2.2 names | PASS |
| Truth table INTERLOCK | PASS |
| Truth table SAFE_N | PASS |
| Truth table HW_ARMED | PASS |
| Truth table MOTOR_PERMIT | PASS |
| Truth table PWM_OUT | PASS |
| Truth table SENSOR_PERMIT | PASS |
| Fault recovery never automatically rearms | PASS |

## Próby ujemne S1 / P12

| Mutacja | Kontrola docelowa | Wykryta | Zgłosiły |
|---|---|---|---|
| SENSOR_PERMIT and SENSOR_OK swapped | J_BP1-PINOUT | tak | J_BP1-PINOUT, CSV-J_BP |
| MOTOR_PERMIT and PWM_OUT swapped | J_BP2-PINOUT | tak | J_BP2-PINOUT, CSV-J_BP |
| SENSOR_ENABLE and CORE_LINK swapped | J_BP3-PINOUT | tak | J_BP3-PINOUT, CSV-J_BP |
| vertical IDC header | J_BP2-FOOTPRINT | tak | J_BP2-FOOTPRINT |
| J_BP1 as 2x10 | J_BP1-FOOTPRINT | tak | J_BP1-FOOTPRINT |
| odd pin 19 of J_BP3 carries 3V3_IO | JBP-ODD-PINS-GND | tak | J_BP3-PINOUT, JBP-ODD-PINS-GND, JBP-R22-CONNECTOR-NETS-EXACTLY-ONCE, CSV-J_BP |
| second 3V3_IO pin lost | JBP-R22-CONNECTOR-NETS-EXACTLY-ONCE | tak | J_BP3-PINOUT, JBP-R22-CONNECTOR-NETS-EXACTLY-ONCE, CSV-J_BP |
| PWM duplicated on 5V_SYS pin | JBP-R22-CONNECTOR-NETS-EXACTLY-ONCE | tak | J_BP3-PINOUT, JBP-R22-CONNECTOR-NETS-EXACTLY-ONCE, P12-WAITING-NETS-ON-JBP, CSV-J_BP, J_SV3-SERIES-R-AT-NODE-CLASS |
| PSU_OK and P04_3V3 swapped (P02 J_BP.12) | JBP-PINS-AS-COUNTERPARTS | tak | J_BP2-PINOUT, JBP-PINS-AS-COUNTERPARTS, CSV-J_BP |
| TEST_KEY and DAQ_OK swapped (P11 / P03 pin 14) | JBP-PINS-AS-COUNTERPARTS | tak | J_BP1-PINOUT, JBP-PINS-AS-COUNTERPARTS, CSV-J_BP |
| HEARTBEAT and MCU_ARM swapped (P03 J_BP3.16/18) | JBP-PINS-AS-COUNTERPARTS | tak | J_BP3-PINOUT, JBP-PINS-AS-COUNTERPARTS, CSV-J_BP |
| DAQ_OK missing (pin to GND) | P12-WAITING-NETS-ON-JBP | tak | J_BP1-PINOUT, JBP-R22-CONNECTOR-NETS-EXACTLY-ONCE, P12-WAITING-NETS-ON-JBP, CSV-J_BP |
| reset net under the R2.2 name SUP_N | P12-WAITING-NETS-ON-JBP | tak | J_BP3-PINOUT, JBP-R22-CONNECTOR-NETS-EXACTLY-ONCE, JBP-PINS-AS-COUNTERPARTS, P12-WAITING-NETS-ON-JBP, P12-NO-FOREIGN-NAMES, CSV-J_BP |
| P02 name PFAIL_N on a P04 pin | P12-NO-FOREIGN-NAMES | tak | J_BP3-PINOUT, JBP-R22-CONNECTOR-NETS-EXACTLY-ONCE, P12-NO-FOREIGN-NAMES, CSV-J_BP, J_SV3-SERIES-R-AT-NODE-CLASS |
| HW_ARMED declared as input in J_BP.csv (no transmitter) | P12-ONE-TRANSMITTER | tak | P12-ONE-TRANSMITTER, CSV-DIRECTIONS |
| PSU_OK declared as output (two transmitters) | P12-ONE-TRANSMITTER | tak | P12-ONE-TRANSMITTER, CSV-DIRECTIONS |
| 3V3_IO declared as source | P12-POWER-NOT-SOURCED | tak | P12-POWER-NOT-SOURCED, CSV-DIRECTIONS |
| ARM_CLK renamed on the connector | P07-DRIVE-NAMES-AS-R22 | tak | J_BP2-PINOUT, JBP-R22-CONNECTOR-NETS-EXACTLY-ONCE, P12-NO-FOREIGN-NAMES, P07-DRIVE-NAMES-AS-R22, CSV-J_BP |
| SENSOR_OK renamed on the connector | P08-SENSOR-NAMES-AS-R22-AND-P08R1 | tak | J_BP1-PINOUT, JBP-R22-CONNECTOR-NETS-EXACTLY-ONCE, P12-NO-FOREIGN-NAMES, P08-SENSOR-NAMES-AS-R22-AND-P08R1, CSV-J_BP |
| J_BP.csv out of date (netlist swapped PG_LINK / PG_SEND) | CSV-J_BP | tak | J_BP2-PINOUT, JBP-PINS-AS-COUNTERPARTS, CSV-J_BP |
| direction word changed in J_BP.csv | CSV-DIRECTIONS | tak | CSV-DIRECTIONS |
| 14th pin on J_SV1 | J_SV1-MAX-13-PINS | tak | J_SV1-MAX-13-PINS, CSV-SERWIS |
| J_SV2 vertical header | J_SV2-MAX-13-PINS | tak | J_SV2-MAX-13-PINS |
| first pin of J_SV1 not GND | J_SV1-GND-ENDS | tak | J_SV1-GND-ENDS, J_SV1-SERIES-R-AT-NODE-CLASS, J_SV1-NEIGHBOURS, CSV-SERWIS |
| last pin of J_SV3 not GND | J_SV3-GND-ENDS | tak | J_SV3-GND-ENDS, J_SV3-SERIES-R-AT-NODE-CLASS, J_SV3-NEIGHBOURS, CSV-SERWIS |
| SAFE_N next to ARM_CLK (interior GND swapped) | J_SV1-NEIGHBOURS | tak | J_SV1-NEIGHBOURS, CSV-SERWIS |
| ARM_BUTTON_N next to HW_ARMED | J_SV1-NEIGHBOURS | tak | J_SV1-NEIGHBOURS, CSV-SERWIS |
| rail next to logic (PG_SEND resistor moved to INTERLOCK) | J_SV3-NEIGHBOURS | tak | J_SV2-SERIES-R-AT-NODE-CLASS, J_SV2-NEIGHBOURS, J_SV3-SERIES-R-AT-NODE-CLASS, J_SV3-NEIGHBOURS |
| SAFE_N through 1K instead of 10K | J_SV1-SERIES-R-AT-NODE-CLASS | tak | J_SV1-SERIES-R-AT-NODE-CLASS, CSV-SERWIS |
| Q1_B through 10K (E21 would fail) | J_SV1-SERIES-R-AT-NODE-CLASS | tak | J_SV1-SERIES-R-AT-NODE-CLASS, CSV-SERWIS |
| pin wired straight to the node (no resistor) | J_SV2-SERIES-R-AT-NODE-CLASS | tak | J_SV2-SERIES-R-AT-NODE-CLASS, SRV-COVERS-R22-TESTPADS |
| service resistor shorted | J_SV3-SERIES-R-AT-NODE-CLASS | tak | J_SV3-SERIES-R-AT-NODE-CLASS, J_SV3-NEIGHBOURS, SRV-COVERS-R22-TESTPADS, CSV-SERWIS |
| same node on two strips | SRV-EACH-NODE-ONCE | tak | J_SV2-SERIES-R-AT-NODE-CLASS, SRV-EACH-NODE-ONCE, SRV-COVERS-R22-TESTPADS |
| LOCAL_SUP_N missing (resistor on a dead net) | SRV-COVERS-R22-TESTPADS | tak | J_SV1-SERIES-R-AT-NODE-CLASS, SRV-COVERS-R22-TESTPADS |
| SERWIS.csv out of date (strip order changed) | CSV-SERWIS | tak | CSV-SERWIS |
| resistor value differs from SERWIS.csv | CSV-SERWIS | tak | J_SV3-SERIES-R-AT-NODE-CLASS, CSV-SERWIS |
| new resistor as 0805 | PARTS-S1-SOURCES | tak | PARTS-S1-SOURCES |
| buffer back on the Kamami adapter | PARTS-S1-SOURCES | tak | PARTS-S1-SOURCES |
| electrolytic outside the C3 exception | PARTS-S1-SOURCES | tak | PARTS-S1-SOURCES |
| watchdog CLR moved to SAFE_N | R22-CIRCUIT-KEPT | tak | R22-CIRCUIT-KEPT |
| R1 value changed (watchdog time) | R22-CIRCUIT-KEPT | tak | R22-CIRCUIT-KEPT |
| Q2 collector and emitter swapped | R22-CIRCUIT-KEPT | tak | R22-CIRCUIT-KEPT |
| null control (no change) | — | nie | — |

## Próby ujemne elektryczne

| Mutacja | Kontrola docelowa | Wykryta |
|---|---|---|
| watchdog CLR on SAFE_N | Watchdog pinout and independent clear | tak |
| watchdog Cext to ground | Watchdog capacitor is between 15 and 14, never ground | tak |
| bypassed local supervisor | Both supervisors qualify watchdog | tak |
| MCP100 pins reversed | Local supervisor D bondout | tak |
| missing TEST_KEY gate | Truth table INTERLOCK | tak |
| bypassed MCU arm | Truth table MOTOR_PERMIT | tak |
| sensor incorrectly requires manual ARM | Truth table SENSOR_PERMIT | tak |
| no SAFE conditioning | Latch and Schmitt conditioning | tak |
| push-pull output on shared SAFE | SAFE_N has only one passive pull-up and open collectors | tak |
| missing receiver default | Input and post-buffer pull-downs | tak |
| SENSOR_OK moved off its R2.2 name | DRIVE and SENSOR nets leave on J_BP with the R2.2 names | tak |
| LED load on SAFE_N | SAFE_N has only one passive pull-up and open collectors | tak |
| R1 latch clear (watchdog only via Q1) | Watchdog clears the latch and both permits without Q1 (single-fault) | tak |
| motor permit on SAFE_OK only (masked by the latch clear in steady state; structural check) | Latch and Schmitt conditioning | tak |
| panel line straight to a gate | Panel contacts reach the gates only through R41/R42 1 k; pulldowns on the gate side | tak |
| 3V3 straight to the panel | 3V3 leaves the board only through current-limiting resistors (R38/R39 1 k, R40 100 R) | tak |

PCB: `verification/QA-PCB.md` (łańcuch `src/run_release.py`). Kontrole plików nie zastępują odbioru na sprzęcie (`docs/ODBIOR.md`).
Ostrzeżenie kicad-cli „schemat posiada błędy numeracji” dotyczy oznaczeń `J_BP1…3` i `J_SV1…3` (nazwy z formatu S1, jak w P03 R6 / P06 R2); ERC go nie zgłasza.
