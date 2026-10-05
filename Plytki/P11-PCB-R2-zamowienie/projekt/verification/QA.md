# P11-R2 — QA schematu (plik generowany przez src/run_schematic.py)

ERC: 0 naruszeń na 3 arkuszach. Netlista: 16 części, 104 pinów sprawdzonych pin po pinie względem `parts.py`, 0 błędów.

Kontrole elektryczne (`verify_electrical.py`): 35/35 PASS; mutacje 22/22 wykrytych. Model: 256 stanów styków × 2 warianty, szyna 3.18 V dla H i 3.42 V dla L, obciążenia −1 %, rezystory szeregowe +1 %.

LOGGER (R1 obsadzony, bez P04): minimalne H LOGGER_CLEAR 3.086 V, MARK 3.180 V, TEST_KEY 3.086 V, TEST_PRESENT 3.086 V; prąd z 3V3_IO maks. 0.935 mA; prąd zamkniętego styku 311.7 µA – 0.318 mA.
Pełny (P04 R40, R1 DNP; obciążenia P04-R2.1): minimalne H ARM_BUTTON_N 3.180 V, LOGGER_CLEAR 3.028 V, MARK 3.180 V, MECH_OK_P04 2.748 V, SAFE_N 2.748 V, TEST_KEY 3.028 V, TEST_KEY_P04 2.748 V, TEST_PRESENT 3.028 V; prąd maks. 1.501 mA; prąd styku 27.8 µA – 0.87 mA.
Zwarcie PANEL_3V3–GND przy R1: 118 mW w R1 (1206, 0,25 W).

Kontrakt P12 (`verify_p12.py`): 22/22 PASS; mutacje 13/13 wykrytych przez kontrolę docelową; próba zerowa: czysta.

| Kontrola P12 | Wynik | Uwagi |
|---|---|---|
| J_P12-20-PINS | PASS |  |
| P03-POS-N_J_SCOPE_HOT | PASS | P03 R6 [('J_BP1', 10)] / P11 [10] |
| DIR-N_J_SCOPE_HOT | PASS | P03 out, P11 in |
| P03-POS-MARK | PASS | P03 R6 [('J_BP1', 13)] / P11 [13] |
| DIR-MARK | PASS | P03 in, P11 out |
| P03-POS-TEST_KEY | PASS | P03 R6 [('J_BP1', 14)] / P11 [14] |
| DIR-TEST_KEY | PASS | P03 in, P11 out |
| P03-POS-LOGGER_CLEAR | PASS | P03 R6 [('J_BP1', 15)] / P11 [15] |
| DIR-LOGGER_CLEAR | PASS | P03 in, P11 out |
| P03-POS-TEST_PRESENT | PASS | P03 R6 [('J_BP1', 16)] / P11 [16] |
| DIR-TEST_PRESENT | PASS | P03 in, P11 out |
| P12-WAITING-COVERED | PASS | ['LOGGER_CLEAR', 'MARK', 'N_J_SCOPE_HOT', 'TEST_KEY', 'TEST_PRESENT'] |
| PANELSAFE-NETS | PASS | P04-R2.1 J8: ['ARM_CONTACT', 'MECH_OK', 'PANEL_3V3', 'STOP_NC_OUT', 'TEST_KEY'] |
| 3V3_IO-ONE-PIN | PASS | 3V3_IO exists on P12 (P02 R4 source, P06 R2 J_BP.14) |
| NO-FOREIGN-NETS | PASS | [] |
| ODD-GND | PASS | odd pins GND except 13 / 15 |
| GND-COUNT | PASS |  |
| 3V3_IO-NOT-NEXT-TO-PANEL_3V3 | PASS | 3V3_IO 20, PANEL_3V3 2 |
| SCOPE-BETWEEN-GND | PASS | edge signal shielded in the ribbon |
| ALL-USED-ON-P11 | PASS | [] |
| CSV-EQUALS-NETLIST | PASS |  |
| CSV-KIND | PASS |  |

| Kontrola elektryczna | Wynik | Uwagi |
|---|---|---|
| R1-CONTACT-FIELD | PASS | J11.1..18 = R1 J11.1..18 (R1 19/20 were NC) |
| R1-CONTACT-X11 | PASS | functional terminals as R1 |
| R1-CONTACT-X12 | PASS | functional terminals as R1 |
| R1-CONTACT-X13 | PASS | functional terminals as R1 |
| R1-CONTACT-X14 | PASS | functional terminals as R1 |
| R1-CONTACT-X15 | PASS | functional terminals as R1 |
| R1-CONTACT-X16 | PASS | functional terminals as R1 |
| R1-CONTACT-X17 | PASS | functional terminals as R1 |
| TEST-PORT-10-11 | PASS | X8 cavity 10/11 as R1, other cavities not on P11 |
| TEST-FIELD-J8 | PASS |  |
| PORTS-L1-L2-OFF-P11 | PASS | P11-4/P11-5 |
| NO-MOTOR-TAP-SENSOR-NETS | PASS | decisions P11-4, P11-5 |
| SCOPE | PASS |  |
| PARTS-SET | PASS | no active parts, no LEDs, no added pulls on P11 |
| 3V3_IO-ONLY-TO-R1 | PASS | the only path 3V3_IO -> PANEL_3V3 is R1 |
| PANEL_3V3-FEED | PASS |  |
| R1-VALUE | PASS |  |
| VARIANT-LOGGER-ONE-SOURCE | PASS | [('P11 R1', 100.0)] |
| VARIANT-FULL-ONE-SOURCE | PASS | [('P04 R40', 100.0)] (R1 must be DNP with P04) |
| BOM-R1-VARIANT | PASS | DNP note in BOM |
| NODAL-256-LOGGER | PASS | 0 receiver levels wrong; thresholds H {'LVC': 2.0, 'MCP23017': 2.64, 'P04_HC08': 2.4, 'SAFE_N': 2.7, 'HC14': 2.4}, L <= 0.8 V |
| NO-SHORT-LOGGER | PASS | max source current 0.94 mA (no closed-contact path PANEL_3V3 -> GND) |
| NODAL-256-FULL | PASS | 0 receiver levels wrong; thresholds H {'LVC': 2.0, 'MCP23017': 2.64, 'P04_HC08': 2.4, 'SAFE_N': 2.7, 'HC14': 2.4}, L <= 0.8 V |
| NO-SHORT-FULL | PASS | max source current 1.50 mA (no closed-contact path PANEL_3V3 -> GND) |
| PANEL_3V3-NEVER-TO-GND | PASS | ARM / MARK only to GND, never bridged to PANEL_3V3 |
| OPEN-WIRE-KILLS-X15.1 | PASS |  |
| OPEN-WIRE-KILLS-X12.1 | PASS |  |
| OPEN-WIRE-KILLS-X12.2 | PASS |  |
| OPEN-WIRE-KILLS-X13.1 | PASS |  |
| OPEN-WIRE-KILLS-X13.2 | PASS |  |
| OPEN-WIRE-KILLS-X8.10 | PASS |  |
| OPEN-WIRE-KILLS-X8.11 | PASS |  |
| STOP-OPEN-WIRE | PASS |  |
| R1-SHORT-POWER | PASS | 118 mW at 3.42 V vs 0.25 W rated (<= 50 %) |
| BUTTONS-GOLD | PASS | P11-7 |

## Próby ujemne P12

| Mutacja | Kontrola docelowa | Wykryta | Zgłosiły |
|---|---|---|---|
| MARK <-> TEST_KEY (13/14) | P03-POS-MARK | tak | P03-POS-MARK, P03-POS-TEST_KEY, CSV-EQUALS-NETLIST |
| N_J_SCOPE_HOT na 12 | P03-POS-N_J_SCOPE_HOT | tak | P03-POS-N_J_SCOPE_HOT, SCOPE-BETWEEN-GND, CSV-EQUALS-NETLIST |
| TEST_PRESENT <-> LOGGER_CLEAR (16/15) | P03-POS-TEST_PRESENT | tak | P03-POS-LOGGER_CLEAR, P03-POS-TEST_PRESENT, CSV-EQUALS-NETLIST |
| 3V3_IO na 4 (obok PANEL_3V3) | 3V3_IO-NOT-NEXT-TO-PANEL_3V3 | tak | 3V3_IO-NOT-NEXT-TO-PANEL_3V3, CSV-EQUALS-NETLIST |
| pin 9 GND -> STOP_NC_OUT (dubel) | ODD-GND | tak | PANELSAFE-NETS, ODD-GND, SCOPE-BETWEEN-GND, CSV-EQUALS-NETLIST |
| brak PANEL_3V3 (pin 2 -> GND) | PANELSAFE-NETS | tak | PANELSAFE-NETS, 3V3_IO-NOT-NEXT-TO-PANEL_3V3, CSV-EQUALS-NETLIST |
| brak ARM_CONTACT (pin 8 -> GND) | PANELSAFE-NETS | tak | PANELSAFE-NETS, CSV-EQUALS-NETLIST |
| brak 3V3_IO (pin 20 -> GND) | 3V3_IO-ONE-PIN | tak | 3V3_IO-ONE-PIN, 3V3_IO-NOT-NEXT-TO-PANEL_3V3, CSV-EQUALS-NETLIST |
| obca siec 5V_SYS na 18 | NO-FOREIGN-NETS | tak | NO-FOREIGN-NETS, ALL-USED-ON-P11, CSV-EQUALS-NETLIST |
| GND obok SCOPE zabrany (11 -> MECH_OK) | SCOPE-BETWEEN-GND | tak | PANELSAFE-NETS, ODD-GND, SCOPE-BETWEEN-GND, CSV-EQUALS-NETLIST |
| CSV: pin 14 opisany jako MARK | CSV-EQUALS-NETLIST | tak | DIR-TEST_KEY, CSV-EQUALS-NETLIST |
| CSV: kierunek TEST_KEY = in | DIR-TEST_KEY | tak | DIR-TEST_KEY |
| MARK nieuzywany na P11 (J11.16 i X14.2 -> NC) | ALL-USED-ON-P11 | tak | ALL-USED-ON-P11 |
| proba zerowa (bez zmian) | — | nie | — |

## Próby ujemne elektryczne

| Mutacja | Wykryta | Zgłosiły |
|---|---|---|
| R1 brak (nieobsadzony w LOGGER) | tak | PARTS-SET, 3V3_IO-ONLY-TO-R1, PANEL_3V3-FEED, R1-VALUE, VARIANT-LOGGER-ONE-SOURCE, NODAL-256-LOGGER |
| R1 obsadzony przy P04 (wariant FULL) | tak | VARIANT-FULL-ONE-SOURCE, BOM-R1-VARIANT |
| R1 DNP w LOGGER (BOM) | tak | VARIANT-LOGGER-ONE-SOURCE, BOM-R1-VARIANT, NODAL-256-LOGGER |
| R1.1 -> 3V3_CORE | tak | 3V3_IO-ONLY-TO-R1, VARIANT-LOGGER-ONE-SOURCE, NODAL-256-LOGGER |
| R1 omijany: J_P12.20 -> PANEL_3V3 | tak | 3V3_IO-ONLY-TO-R1 |
| R1 = 10R | tak | R1-VALUE |
| X13.4 -> PANEL_3V3 | tak | R1-CONTACT-X13, NODAL-256-LOGGER, NODAL-256-FULL |
| X12.2 -> TEST_KEY | tak | R1-CONTACT-X12, NODAL-256-FULL |
| X15.2 -> PANEL_3V3 | tak | R1-CONTACT-X15, NODAL-256-LOGGER, NODAL-256-FULL |
| X11.1 -> PANEL_3V3 | tak | R1-CONTACT-X11, NODAL-256-FULL |
| X14.1 -> PANEL_3V3 | tak | R1-CONTACT-X14, NODAL-256-LOGGER, NODAL-256-FULL |
| X16.1 -> GND | tak | R1-CONTACT-X16, NODAL-256-FULL |
| X17.2 -> TEST_KEY | tak | R1-CONTACT-X17, NODAL-256-LOGGER, NODAL-256-FULL, OPEN-WIRE-KILLS-X15.1 |
| J8.1 -> MECH_OK | tak | TEST-FIELD-J8 |
| X8.10 -> MECH_OK | tak | TEST-PORT-10-11, NODAL-256-FULL |
| J11.12 -> GND | tak | R1-CONTACT-FIELD |
| X2.1 -> ECU_P1 | tak | PORTS-L1-L2-OFF-P11, NO-MOTOR-TAP-SENSOR-NETS |
| X8.3 -> 5V_SENSOR | tak | TEST-PORT-10-11, NO-MOTOR-TAP-SENSOR-NETS |
| J6.2 -> PANEL_3V3 | tak | SCOPE |
| X13.2 -> MECH_OK | tak | R1-CONTACT-X13, NODAL-256-FULL, OPEN-WIRE-KILLS-X8.10, OPEN-WIRE-KILLS-X8.11 |
| dodatkowa LED PANEL_3V3-GND | tak | PARTS-SET, PANEL_3V3-FEED, NODAL-256-FULL |
| przycisk bez zlocenia (X14) | tak | BUTTONS-GOLD |

PCB: osobny raport `verification/QA-PCB.md` (src/run_release.py, 4.10.2026). Kontrole plików nie zastępują odbioru na sprzęcie.
Model pełnego wariantu używa zamrożonego P04-R2.1 (P04 w S1 jeszcze nie istnieje) — do powtórzenia przy P04 w S1.
Ostrzeżenie kicad-cli „schemat posiada błędy numeracji” dotyczy oznaczenia `J_P12` bez numeru (jak `J_BP` w P02 R4 i P06 R2); ERC go nie zgłasza.
