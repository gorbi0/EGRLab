# P08-R2 — QA schematu (plik generowany przez src/run_schematic.py)

ERC: 0 naruszeń na 4 arkuszach. Netlista: 52 części, 194 pinów sprawdzonych pin po pinie względem `parts.py`, 0 błędów, 47 sieci.

Kontrole elektryczne: 49/49 PASS. Próby ujemne: 49/49 mutacji wykrytych; próba zerowa (bez zmiany): czysta.

| Kontrola | Wynik |
|---|---|
| JBP-2x8 | PASS |
| JBP-ODD-GND | PASS |
| JBP-EVEN-NO-GND | PASS |
| JBP-CONTINUITY-R1 | PASS |
| JBP-S1-SUPPLY-PINS | PASS |
| JBP-NO-NC | PASS |
| JBP-CSV | PASS |
| JBP-DIRECTIONS | PASS |
| CONTRACT-P04-R2.2-SENSOR | PASS |
| CONTRACT-P03-R6-SFAULT | PASS |
| CONTRACT-P02-R4-SUPPLIES | PASS |
| IF-TSENSOR | PASS |
| SRV-MAX-13 | PASS |
| SRV-ENDS-GND | PASS |
| SRV-SERIES-R-AT-NODE | PASS |
| SRV-COVERS-ODBIOR | PASS |
| SRV-NOT-ON-SENSOR-OUTPUT | PASS |
| SRV-CSV | PASS |
| PARTS-SOURCES | PASS |
| NO-TESTPADS-NO-HARNESS-TAILS | PASS |
| R1-CIRCUIT-PARITY | PASS |
| TPS-DBV-PINS | PASS |
| CURRENT-LIMIT-RESISTOR | PASS |
| RELAY-CONTACTS | PASS |
| DRIVER | PASS |
| FLYBACK | PASS |
| SUP-U6 | PASS |
| SUP-U7 | PASS |
| SUP-U8 | PASS |
| SUP-PULLUPS | PASS |
| FAULT-PULLUP-3V3 | PASS |
| NO-FAULT-EN-FEEDBACK | PASS |
| GUARD-DIVIDER | PASS |
| GUARD-MARGINS | PASS |
| HC08-PINS | PASS |
| IOFF-TRANSLATION | PASS |
| DEFAULT-R5 | PASS |
| DEFAULT-R6 | PASS |
| DEFAULT-R7 | PASS |
| DEFAULT-R8 | PASS |
| DEFAULT-R9 | PASS |
| DEFAULT-R10 | PASS |
| DEFAULT-R12 | PASS |
| DEFAULT-R14 | PASS |
| OUTPUT-SERIES | PASS |
| DISCHARGE | PASS |
| NO-GROUND-BYPASS | PASS |
| INPUT-OUTPUT-CAPS | PASS |
| ACTUAL-NETLIST-TRUTH | PASS |

## Próby ujemne

| Mutacja | Oczekiwane | Wykryta | Zgłosiły kontrole |
|---|---|---|---|
| NC-NO-swap | detected | tak | R1-CIRCUIT-PARITY, RELAY-CONTACTS |
| ground-bypass | detected | tak | R1-CIRCUIT-PARITY, DISCHARGE, NO-GROUND-BYPASS |
| reversed-flyback | detected | tak | R1-CIRCUIT-PARITY, FLYBACK |
| bad-TPS-pin | detected | tak | R1-CIRCUIT-PARITY, TPS-DBV-PINS |
| missing-guard | detected | tak | R1-CIRCUIT-PARITY, SUP-U8 |
| wrong-guard-power | detected | tak | R1-CIRCUIT-PARITY, SUP-U8 |
| 5V-to-HC | detected | tak | R1-CIRCUIT-PARITY, HC08-PINS |
| ready-permit-loop | detected | tak | R1-CIRCUIT-PARITY, HC08-PINS, ACTUAL-NETLIST-TRUTH |
| fault-retry-loop | detected | tak | R1-CIRCUIT-PARITY, NO-FAULT-EN-FEEDBACK, HC08-PINS, ACTUAL-NETLIST-TRUTH |
| health-wrong-gate | detected | tak | R1-CIRCUIT-PARITY, HC08-PINS, ACTUAL-NETLIST-TRUTH |
| no-IOff | detected | tak | R1-CIRCUIT-PARITY, IOFF-TRANSLATION |
| no-pulldown | detected | tak | R1-CIRCUIT-PARITY, DEFAULT-R14 |
| coil-common | detected | tak | R1-CIRCUIT-PARITY, DRIVER |
| jbp-odd-pin-signal | detected | tak | JBP-ODD-GND, JBP-CSV |
| jbp-odd-pin-NC | detected | tak | JBP-ODD-GND, JBP-NO-NC, JBP-CSV |
| jbp-even-pin-GND | detected | tak | JBP-EVEN-NO-GND, JBP-CONTINUITY-R1, JBP-NO-NC, JBP-CSV, CONTRACT-P04-R2.2-SENSOR |
| jbp-second-5V-lost | detected | tak | JBP-S1-SUPPLY-PINS, JBP-NO-NC, JBP-CSV |
| jbp-PERMIT-missing | detected | tak | JBP-CONTINUITY-R1, JBP-NO-NC, JBP-CSV, CONTRACT-P04-R2.2-SENSOR |
| jbp-HEALTHY-renamed | detected | tak | JBP-CONTINUITY-R1, JBP-CSV, CONTRACT-P03-R6-SFAULT |
| jbp-spare-used | detected | tak | JBP-EVEN-NO-GND, JBP-CONTINUITY-R1, JBP-NO-NC, JBP-CSV |
| jbp-spare-back-to-NC | detected | tak | JBP-EVEN-NO-GND, JBP-NO-NC, JBP-CSV |
| jbp-spare14-NC | detected | tak | JBP-EVEN-NO-GND, JBP-NO-NC, JBP-CSV |
| jbp-extra-3V3 | detected | tak | JBP-EVEN-NO-GND, JBP-NO-NC, JBP-CSV |
| jbp-OK-driven-raw | detected | tak | JBP-DIRECTIONS, R1-CIRCUIT-PARITY, OUTPUT-SERIES, ACTUAL-NETLIST-TRUTH |
| tsensor-return-to-GND | detected | tak | IF-TSENSOR, NO-GROUND-BYPASS |
| tsensor-swapped | detected | tak | IF-TSENSOR, SRV-NOT-ON-SENSOR-OUTPUT |
| srv-first-not-GND | detected | tak | SRV-ENDS-GND, SRV-CSV |
| srv-last-not-GND | detected | tak | SRV-ENDS-GND, SRV-SERIES-R-AT-NODE, SRV-COVERS-ODBIOR, SRV-CSV |
| srv-extra-GND-inside | detected | tak | SRV-ENDS-GND, SRV-SERIES-R-AT-NODE, SRV-COVERS-ODBIOR, SRV-CSV |
| srv-14th-pin | detected | tak | SRV-MAX-13, SRV-ENDS-GND, SRV-SERIES-R-AT-NODE, SRV-CSV |
| srv-no-resistor | detected | tak | SRV-SERIES-R-AT-NODE, SRV-COVERS-ODBIOR, SRV-CSV |
| srv-resistor-shorted | detected | tak | SRV-SERIES-R-AT-NODE, SRV-COVERS-ODBIOR |
| srv-duplicate-node | detected | tak | SRV-SERIES-R-AT-NODE, SRV-COVERS-ODBIOR |
| srv-node-GND | detected | tak | SRV-SERIES-R-AT-NODE, SRV-COVERS-ODBIOR |
| srv-on-AGND_SENSOR | detected | tak | SRV-SERIES-R-AT-NODE, SRV-COVERS-ODBIOR, NO-GROUND-BYPASS |
| srv-on-5V_SENSOR | detected | tak | SRV-SERIES-R-AT-NODE, SRV-COVERS-ODBIOR, SRV-NOT-ON-SENSOR-OUTPUT |
| wrong-limit | detected | tak | R1-CIRCUIT-PARITY, CURRENT-LIMIT-RESISTOR |
| bad-divider | detected | tak | PARTS-SOURCES, R1-CIRCUIT-PARITY, GUARD-DIVIDER, GUARD-MARGINS |
| wrong-variant | detected | tak | TPS-DBV-PINS |
| wrong-supervisor | detected | tak | SUP-U8 |
| srv-TPS_EN-1k | detected | tak | SRV-SERIES-R-AT-NODE |
| srv-rail-0R | detected | tak | SRV-SERIES-R-AT-NODE |
| jbp-wrong-header | detected | tak | JBP-2x8 |
| R2-fp-THT | detected | tak | PARTS-SOURCES |
| R15-fp-SMD | detected | tak | PARTS-SOURCES |
| C3-fp-0805 | detected | tak | PARTS-SOURCES |
| R1-circuit-value-changed | detected | tak | PARTS-SOURCES, R1-CIRCUIT-PARITY, DISCHARGE |
| testpad-reintroduced | detected | tak | NO-TESTPADS-NO-HARNESS-TAILS |
| extra-part-on-AGND | detected | tak | R1-CIRCUIT-PARITY, NO-GROUND-BYPASS |
| null-control (no change) | clean | nie | — |

Ocena powierzchni (bez rozmieszczenia, `src/powierzchnia.py`): suma prostokątów obrysów 2356 mm² wobec 4486 mm² użytecznej powierzchni 53 × 100 mm (53 %).

QA schematu; PCB: `verification/QA-PCB.md` (src/run_release.py). Kontrole nie zastępują odbioru na sprzęcie.
