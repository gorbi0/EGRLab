# P10-R2 — QA schematu (plik generowany przez src/run_schematic.py)

ERC: 0 naruszeń na 2 arkuszach. Netlista: 20 części, 74 pinów sprawdzonych pin po pinie względem `parts.py`, 0 błędów, 19 sieci.

Kontrole elektryczne: 32/32 PASS. Próby ujemne: 36/36 mutacji wykrytych; próba zerowa (bez zmiany): czysta.

| Kontrola | Wynik |
|---|---|
| JBP-10-PINS | PASS |
| JBP-ODD-GND | PASS |
| JBP-EVEN-SIGNALS | PASS |
| JBP-CONTINUITY-R1 | PASS |
| JBP-S1-SUPPLY-PINS | PASS |
| JBP-SUPPLY-USED | PASS |
| JBP-CSV | PASS |
| SRV-MAX-13 | PASS |
| SRV-ENDS-GND | PASS |
| SRV-GND-ONLY-ENDS | PASS |
| SRV-SERIES-R-AT-NODE | PASS |
| SRV-COVERS-ODBIOR | PASS |
| SRV-CSV | PASS |
| PARTS-SOURCES | PASS |
| TCAN-PINOUT | PASS |
| TCAN-V-SUFFIX | PASS |
| RX-IOFF-BUFFER | PASS |
| RX-IOFF-MPN | PASS |
| TVS-PINOUT | PASS |
| OBD-TWO-WIRES | PASS |
| TX-ONLY-JBP-AND-SERVICE-PIN | PASS |
| RX-NO-BUFFER-BYPASS | PASS |
| NO-TERM-NO-EXTRA-CAN-LOAD | PASS |
| RES-R1 | PASS |
| RES-R2 | PASS |
| CAP-1 | PASS |
| CAP-2 | PASS |
| CAP-3 | PASS |
| CAP-4 | PASS |
| CAP-5 | PASS |
| ACTUAL-NETS-SILENT | PASS |
| ACTUAL-NETS-RX | PASS |

## Próby ujemne

| Mutacja | Oczekiwane | Wykryta | Zgłosiły kontrole |
|---|---|---|---|
| silent-low | detected | tak | TCAN-PINOUT, ACTUAL-NETS-SILENT |
| MCU-to-TXD | detected | tak | TCAN-PINOUT, TX-ONLY-JBP-AND-SERVICE-PIN, ACTUAL-NETS-SILENT |
| swap-CAN | detected | tak | TCAN-PINOUT, NO-TERM-NO-EXTRA-CAN-LOAD |
| TVS-common-wrong | detected | tak | TVS-PINOUT |
| RX-buffer-bypass | detected | tak | TCAN-PINOUT, RX-NO-BUFFER-BYPASS |
| RX-OE-wrong | detected | tak | RX-IOFF-BUFFER, ACTUAL-NETS-RX |
| unused-input-float | detected | tak | RX-IOFF-BUFFER |
| missing-RX-pullup | detected | tak | RES-R2 |
| RX-R-bypass | detected | tak | RX-NO-BUFFER-BYPASS, RES-R1, ACTUAL-NETS-RX |
| extra-120R | detected | tak | PARTS-SOURCES, NO-TERM-NO-EXTRA-CAN-LOAD |
| jbp-odd-pin-signal | detected | tak | JBP-ODD-GND, JBP-CSV, RX-NO-BUFFER-BYPASS |
| jbp-odd-pin-NC | detected | tak | JBP-ODD-GND, JBP-CSV |
| jbp-even-pin-GND | detected | tak | JBP-EVEN-SIGNALS, JBP-CONTINUITY-R1, JBP-S1-SUPPLY-PINS, JBP-CSV, TX-ONLY-JBP-AND-SERVICE-PIN |
| jbp-second-5V-lost | detected | tak | JBP-EVEN-SIGNALS, JBP-CONTINUITY-R1, JBP-S1-SUPPLY-PINS, JBP-CSV |
| jbp-TX-RX-swapped | detected | tak | JBP-CSV, TX-ONLY-JBP-AND-SERVICE-PIN, RX-NO-BUFFER-BYPASS, ACTUAL-NETS-RX |
| jbp-unused-signal | detected | tak | JBP-CONTINUITY-R1, JBP-S1-SUPPLY-PINS, JBP-CSV, NO-TERM-NO-EXTRA-CAN-LOAD |
| jbp-CSV-mismatch | detected | tak | JBP-CONTINUITY-R1, JBP-S1-SUPPLY-PINS, JBP-SUPPLY-USED, JBP-CSV |
| srv-first-not-GND | detected | tak | SRV-ENDS-GND, SRV-GND-ONLY-ENDS, SRV-CSV |
| srv-last-not-GND | detected | tak | SRV-ENDS-GND, SRV-GND-ONLY-ENDS, SRV-CSV, NO-TERM-NO-EXTRA-CAN-LOAD |
| srv-extra-GND-inside | detected | tak | SRV-GND-ONLY-ENDS, SRV-SERIES-R-AT-NODE, SRV-COVERS-ODBIOR, SRV-CSV |
| srv-10th-pin | detected | tak | SRV-GND-ONLY-ENDS, SRV-SERIES-R-AT-NODE, SRV-CSV |
| srv-no-resistor | detected | tak | SRV-SERIES-R-AT-NODE, SRV-COVERS-ODBIOR, SRV-CSV |
| srv-resistor-shorted | detected | tak | SRV-SERIES-R-AT-NODE, SRV-COVERS-ODBIOR |
| srv-CAN-resistor-1k | detected | tak | SRV-SERIES-R-AT-NODE, PARTS-SOURCES |
| srv-resistor-0R | detected | tak | SRV-SERIES-R-AT-NODE |
| srv-CAN_TX-to-transceiver | detected | tak | SRV-SERIES-R-AT-NODE, SRV-COVERS-ODBIOR, TCAN-PINOUT, ACTUAL-NETS-SILENT |
| srv-duplicate-node | detected | tak | SRV-SERIES-R-AT-NODE, SRV-COVERS-ODBIOR |
| srv-node-GND | detected | tak | SRV-SERIES-R-AT-NODE, SRV-COVERS-ODBIOR, RX-NO-BUFFER-BYPASS |
| R1-fp-THT | detected | tak | PARTS-SOURCES |
| R2-fp-SMD | detected | tak | PARTS-SOURCES |
| C1-fp-SMD | detected | tak | PARTS-SOURCES |
| C4-fp-THT | detected | tak | PARTS-SOURCES |
| U1-mpn | detected | tak | TCAN-V-SUFFIX |
| U2-mpn | detected | tak | RX-IOFF-MPN |
| C2-value | detected | tak | PARTS-SOURCES, CAP-2 |
| R1-value | detected | tak | PARTS-SOURCES, RES-R1 |
| null-control (no change) | clean | nie | — |

Schemat; PCB w README, sekcja „PCB” (layout 30.09–1.10.2026). Kontrole nie zastępują odbioru na sprzęcie.
