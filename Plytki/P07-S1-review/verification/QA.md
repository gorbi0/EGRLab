# P07-S1 — QA schematu (plik generowany przez src/make_qa.py)

ERC: 0 naruszeń na 8 arkuszach. Netlista: 147 części, 494 pinów sprawdzonych pin po pinie względem `parts.py`, 0 błędów, 116 sieci.

Kontrole elektryczne (`verify_electrical.py`): 16/16 PASS; mutacje 19/19 wykrytych; próba zerowa: czysta. Tabela logiki: 2304 wierszy.
Kontrakt S1 / P12 (`verify_s1.py`): 30/30 PASS; mutacje 24/24 wykrytych przez kontrolę docelową; próba zerowa: czysta.
Powierzchnia (klasa 2/3, `powierzchnia.py`): suma courtyardów 6219 mm² wobec 9022 mm² użytecznych — 69 % (metoda P06 R2: tam 41 %); wnętrze bez złączy krawędzi 50 %, z rezystorami i małymi kondensatorami 1206 od spodu 37 %.

| Kontrola elektryczna | Wynik | Uwagi |
|---|---|---|
| LOGIC-TABLE | PASS | {"rows": 2304, "bad": []} |
| LOGIC-BLOCK-ALL-L | PASS | {"rule": "bez MOTOR_PERMIT / SAFE_N, przy OC lub zlych szynach -> RPWM, LPWM, R_EN, L_EN = L", "bad": []} |
| DEAD-DOMAINS-OPEN-TAPE | PASS | {"3V3_IO off": {"RPWM": 0, "LPWM": 0, "R_EN": 0, "L_EN": 0, "KPWR_COIL_LOW": null}, "3V3A off": {"RPWM": 0, "LPWM": 0, "R_EN": 0, "L_EN": 0, "KPWR_COIL_LOW": null}, "5VA off": {"RPWM": 0, "LPWM": 0, "R_EN": 0, "L_EN": 0, |
| OPEN-TAPE-DEFINED | PASS | {"PERMIT_P07": 0, "PWM_P07": 0, "SAFE_OK": 0, "ARM_CLK": 0} |
| OE-BLOCKS-STUCK-GATE | PASS | {"RPWM_L": {"RPWM": 0, "LPWM": 0, "R_EN": 0, "L_EN": 0}, "LPWM_L": {"RPWM": 0, "LPWM": 0, "R_EN": 0, "L_EN": 0}} |
| LATCH-SEQUENCES | PASS | [] |
| SPI-DOUT-TRISTATE | PASS | DOUT_TX nadaje tylko przy CS_ITEST_N = L; P03 bez zasilania -> CS nieaktywne (R17) |
| OC-WINDOW | PASS | {"plus_A": [8.01, 8.11], "minus_A": [7.99, 8.03], "nominal": [8.06, 8.008]} |
| OC-BELOW-INA-SATURATION | PASS | {"INA_out_at_trip_max_V": 4.579, "OC_HIGH_max_V": 4.578, "5VA_min_V": 4.8} |
| ITEST-SCALE | PASS | {"ratio": 0.5, "tau_ms": 0.255, "range_A": 10.0} |
| SHUNT-POWER-10A | PASS | {"P10A_W": 0.5} |
| PRECHARGE-R | PASS | {"R_ohm": [1000.0], "fault_W": 0.282, "rating_W": 1.0, "Imotor_open_mA": 16.8, "MOD_BP_open_ratio": 0.909} |
| KPWR-DRIVE-CLAMP | PASS | {"Ib_mA": 3.01, "Icoil_mA": 33.3, "clamp_V": 32.5, "coil_ratio": 1.4} |
| TVS-VMOTOR | PASS | ["SMCJ18A"] |
| IS-DIAG | PASS | {"R_IS": [1.64, 4.62], "L_IS": [1.64, 4.62]} |
| GND-PGND-SEPARATE | PASS | {"both": [], "mod_gnd": [["R43", 10.0]]} |

| Kontrola S1 / P12 | Wynik |
|---|---|
| J_BP1-PINOUT | PASS |
| J_BP1-FOOTPRINT | PASS |
| J_BP1-ODD-PINS-GND | PASS |
| J_BP2-PINOUT | PASS |
| J_BP2-FOOTPRINT | PASS |
| J_BP2-ODD-PINS-GND | PASS |
| JBP-POWER-PINS | PASS |
| JBP1-SPI-PINS-AS-P03R6 | PASS |
| JBP2-PINS-AS-P04R3 | PASS |
| P12-WAITING-NETS-END-ON-P07 | PASS |
| P04-NETS-DIRECTIONS | PASS |
| JBP-NO-FOREIGN-NETS | PASS |
| CSV-J_BP | PASS |
| WIRES-MOTOR-PATH | PASS |
| JMOD-PINOUT | PASS |
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
| CSV-SERWIS | PASS |
| RSH1-KELVIN-MOTOR-LINE | PASS |
| INA240-KELVIN-INPUTS | PASS |
| PART-TYPES-S1 | PASS |

## Próby ujemne elektryczne

| Mutacja | Kontrola docelowa | Wykryta | Zgłosiły |
|---|---|---|---|
| SAFE_OK bypassed (U13.2 -> 3V3_IO) | LOGIC-TABLE | tak | LOGIC-TABLE, LOGIC-BLOCK-ALL-L, LATCH-SEQUENCES |
| OC does not clear the latch (U12.5 -> 3V3_IO) | LOGIC-TABLE | tak | LOGIC-TABLE, LATCH-SEQUENCES |
| no OE blocking on RPWM (U16.1 -> GND) | OE-BLOCKS-STUCK-GATE | tak | OE-BLOCKS-STUCK-GATE |
| re-arm under PERMIT (U15.2 -> 3V3_IO) | LATCH-SEQUENCES | tak | LATCH-SEQUENCES |
| NO_TRIP not preset at power-up (U15.10 -> 3V3_IO) | LATCH-SEQUENCES | tak | LATCH-SEQUENCES |
| no pull-down on MOTOR_PERMIT (R28 open) | OPEN-TAPE-DEFINED | tak | OPEN-TAPE-DEFINED |
| Q2 collector off SAFE_N | LOGIC-TABLE | tak | LOGIC-TABLE, LATCH-SEQUENCES |
| DOUT always driving (U7.10 -> GND) | SPI-DOUT-TRISTATE | tak | SPI-DOUT-TRISTATE |
| OC_HIGH too high (R11 12K) | OC-WINDOW | tak | LOGIC-TABLE, LOGIC-BLOCK-ALL-L, LATCH-SEQUENCES, OC-WINDOW, OC-BELOW-INA-SATURATION |
| OC_HIGH saturates INA240 (R11 9.53K) | OC-BELOW-INA-SATURATION | tak | LOGIC-TABLE, LOGIC-BLOCK-ALL-L, LATCH-SEQUENCES, OC-WINDOW, OC-BELOW-INA-SATURATION |
| ITEST divider unequal (R9 10K) | ITEST-SCALE | tak | ITEST-SCALE |
| precharge 100R | PRECHARGE-R | tak | PRECHARGE-R |
| Zener 27 V | KPWR-DRIVE-CLAMP | tak | KPWR-DRIVE-CLAMP |
| TVS 15 V | TVS-VMOTOR | tak | TVS-VMOTOR |
| IS divider 10K/10K | IS-DIAG | tak | IS-DIAG |
| B- tied to GND (R5.2 -> GND) | GND-PGND-SEPARATE | tak | PRECHARGE-R, GND-PGND-SEPARATE |
| shunt 10 mOhm | SHUNT-POWER-10A | tak | OC-WINDOW, ITEST-SCALE, SHUNT-POWER-10A |
| LPWM gate without OE (U16.4 -> GND) | OE-BLOCKS-STUCK-GATE | tak | OE-BLOCKS-STUCK-GATE |
| KPWR base resistor 4.7K | KPWR-DRIVE-CLAMP | tak | KPWR-DRIVE-CLAMP |

## Próby ujemne S1 / P12

| Mutacja | Kontrola docelowa | Wykryta | Zgłosiły |
|---|---|---|---|
| J_BP1.6 CS_ITEST_N <-> 8 MOTOR_INA | J_BP1-PINOUT | tak | J_BP1-PINOUT, CSV-J_BP |
| J_BP2.16 SAFE_N -> 15 | J_BP2-ODD-PINS-GND | tak | J_BP2-PINOUT, J_BP2-ODD-PINS-GND, JBP2-PINS-AS-P04R3, CSV-J_BP |
| J_BP1 vertical footprint | J_BP1-FOOTPRINT | tak | J_BP1-FOOTPRINT |
| J_BP2 one 5V_SYS pin -> GND | JBP-POWER-PINS | tak | J_BP2-PINOUT, JBP-POWER-PINS, CSV-J_BP |
| ADC_SCLK on J_BP1.16 | JBP1-SPI-PINS-AS-P03R6 | tak | J_BP1-PINOUT, JBP1-SPI-PINS-AS-P03R6, CSV-J_BP |
| DRIVE_OK on J_BP2.10 | JBP2-PINS-AS-P04R3 | tak | J_BP2-PINOUT, JBP2-PINS-AS-P04R3, CSV-J_BP |
| ENB_DIAG missing (J_BP1.14 -> GND) | P12-WAITING-NETS-END-ON-P07 | tak | J_BP1-PINOUT, P12-WAITING-NETS-END-ON-P07, CSV-J_BP |
| VMOTOR on the tape (J_BP2.14) | JBP-NO-FOREIGN-NETS | tak | J_BP2-PINOUT, JBP-POWER-PINS, JBP-NO-FOREIGN-NETS, CSV-J_BP |
| M+ wire to the TEST port directly (J3.1 -> T_EGR_P1) | WIRES-MOTOR-PATH | tak | WIRES-MOTOR-PATH |
| J_MOD VCC/GND swapped | JMOD-PINOUT | tak | JMOD-PINOUT |
| J_SV1 14 pins | J_SV1-MAX-13-PINS | tak | J_SV1-MAX-13-PINS |
| J_SV2.13 not GND | J_SV2-GND-ENDS | tak | J_SV2-GND-ENDS, CSV-SERWIS |
| service R of REF25 1K | J_SV1-SERIES-R-AT-NODE-CLASS | tak | J_SV1-SERIES-R-AT-NODE-CLASS |
| pack rail R 1K | J_SV1-SERIES-R-AT-NODE-CLASS | tak | J_SV1-SERIES-R-AT-NODE-CLASS |
| analog node on J_SV2 (SRV_RAILS_OK -> REF25 via R67) | J_SV2-GROUP | tak | J_SV2-SERIES-R-AT-NODE-CLASS, J_SV2-GROUP, J_SV2-NEIGHBOURS, SRV-EACH-NODE-ONCE |
| J_SV1 pin 8 GND -> pin 7 net (analog next to pack) | J_SV1-NEIGHBOURS | tak | J_SV1-NEIGHBOURS, CSV-SERWIS |
| node probed twice (R71 -> RAILS_OK) | SRV-EACH-NODE-ONCE | tak | J_SV2-SERIES-R-AT-NODE-CLASS, SRV-EACH-NODE-ONCE |
| SERWIS.csv stale (J_SV2.12 -> RAILS_OK) | CSV-SERWIS | tak | J_SV2-SERIES-R-AT-NODE-CLASS, CSV-SERWIS |
| shunt sense pads swapped | RSH1-KELVIN-MOTOR-LINE | tak | RSH1-KELVIN-MOTOR-LINE |
| INA240 IN+ on K_MINUS side | INA240-KELVIN-INPUTS | tak | INA240-KELVIN-INPUTS |
| R15 in 0805 | PART-TYPES-S1 | tak | PART-TYPES-S1 |
| U5 in VSSOP (v6.1) | PART-TYPES-S1 | tak | PART-TYPES-S1 |
| J_BP.csv direction of DRIVE_OK flipped | P04-NETS-DIRECTIONS | tak | P04-NETS-DIRECTIONS |
| J_BP.csv stale (CSV-J_BP) | CSV-J_BP | tak | P12-WAITING-NETS-END-ON-P07, CSV-J_BP |
| null control (unchanged netlist) | — | nie | — |

Tylko schemat: PCB nie powstało (layout robi sesja lokalna, `docs/CHMURA.md` zasada 6). Kontrole plików nie zastępują pomiarów modułu (POMIARY-MODULU D/E) ani odbioru na sprzęcie.
Ostrzeżenie kicad-cli „schemat posiada błędy numeracji” dotyczy oznaczeń `J_BP1`, `J_BP2`, `J_SV1`, `J_SV2` (nazwy z formatu S1, jak w P06 R2); ERC go nie zgłasza.
