# P09-R2 — QA schematu (plik generowany przez src/run_schematic.py)

ERC: 0 naruszeń na 4 arkuszach. Netlista: 46 części, 171 pinów sprawdzonych pin po pinie względem `parts.py`, 0 błędów, 49 sieci.

Kontrole elektryczne: 52/52 PASS. Próby ujemne: 35/35 mutacji wykrytych; próba zerowa (bez zmiany): czysta.

| Kontrola | Wynik |
|---|---|
| JBP-16-PINS | PASS |
| JBP-ODD-GND | PASS |
| JBP-EVEN-SIGNALS | PASS |
| JBP-SPI-NETS | PASS |
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
| U1-INPUT-IOFF | PASS |
| U2-MISO-IOFF | PASS |
| U3-HC139 | PASS |
| MPN | PASS |
| MODULE-PINOUT-J3 | PASS |
| VIN-SELECT-J3 | PASS |
| ISOLATED-J3-3VO | PASS |
| MODULE-PINOUT-J4 | PASS |
| VIN-SELECT-J4 | PASS |
| ISOLATED-J4-3VO | PASS |
| RES-1 | PASS |
| RES-2 | PASS |
| RES-3 | PASS |
| RES-4 | PASS |
| RES-5 | PASS |
| RES-6 | PASS |
| RES-7 | PASS |
| RES-8 | PASS |
| RES-9 | PASS |
| RES-10 | PASS |
| RES-11 | PASS |
| RES-12 | PASS |
| RES-13 | PASS |
| RES-14 | PASS |
| RES-15 | PASS |
| RES-16 | PASS |
| RES-17 | PASS |
| RES-18 | PASS |
| RES-19 | PASS |
| CAP-1 | PASS |
| CAP-2 | PASS |
| CAP-3 | PASS |
| CAP-4 | PASS |
| CAP-5 | PASS |
| CAP-6 | PASS |
| CAP-7 | PASS |
| ACTUAL-NETLIST-TRUTH | PASS |

## Próby ujemne

| Mutacja | Oczekiwane | Wykryta | Zgłosiły kontrole |
|---|---|---|---|
| swap-decoder | detected | tak | U3-HC139, ACTUAL-NETLIST-TRUTH |
| enable-on-both-CS | detected | tak | U3-HC139, ACTUAL-NETLIST-TRUTH |
| unused-input-float | detected | tak | U2-MISO-IOFF |
| 5V-logic | detected | tak | U1-INPUT-IOFF |
| VIN-output-short | detected | tak | MODULE-PINOUT-J3, ISOLATED-J3-3VO |
| module-reversed | detected | tak | MODULE-PINOUT-J4 |
| bypass-MISO-R | detected | tak | RES-11 |
| missing-CS-pullup | detected | tak | RES-1 |
| wrong-VIN-select | detected | tak | VIN-SELECT-J3 |
| DRDY-bus-short | detected | tak | MODULE-PINOUT-J4 |
| jbp-odd-pin-signal | detected | tak | JBP-ODD-GND, JBP-SPI-NETS, JBP-CSV |
| jbp-odd-pin-NC | detected | tak | JBP-ODD-GND, JBP-CSV |
| jbp-even-pin-GND | detected | tak | JBP-EVEN-SIGNALS, JBP-SPI-NETS, JBP-CONTINUITY-R1, JBP-S1-SUPPLY-PINS, JBP-CSV |
| jbp-second-5V-lost | detected | tak | JBP-EVEN-SIGNALS, JBP-CONTINUITY-R1, JBP-S1-SUPPLY-PINS, JBP-CSV |
| jbp-CS-swapped | detected | tak | JBP-SPI-NETS, JBP-CSV |
| jbp-unused-signal | detected | tak | JBP-S1-SUPPLY-PINS, JBP-CSV |
| jbp-CSV-mismatch | detected | tak | JBP-SPI-NETS, JBP-CONTINUITY-R1, JBP-S1-SUPPLY-PINS, JBP-CSV |
| srv-first-not-GND | detected | tak | SRV-ENDS-GND, SRV-GND-ONLY-ENDS, SRV-CSV |
| srv-last-not-GND | detected | tak | SRV-ENDS-GND, SRV-GND-ONLY-ENDS, SRV-CSV |
| srv-extra-GND-inside | detected | tak | SRV-GND-ONLY-ENDS, SRV-SERIES-R-AT-NODE, SRV-COVERS-ODBIOR, SRV-CSV |
| srv-14th-pin | detected | tak | SRV-MAX-13, SRV-GND-ONLY-ENDS, SRV-SERIES-R-AT-NODE, SRV-CSV |
| srv-no-resistor | detected | tak | SRV-SERIES-R-AT-NODE, SRV-COVERS-ODBIOR, SRV-CSV |
| srv-resistor-shorted | detected | tak | SRV-SERIES-R-AT-NODE, SRV-COVERS-ODBIOR |
| srv-resistor-100R | detected | tak | SRV-SERIES-R-AT-NODE |
| srv-resistor-0R | detected | tak | SRV-SERIES-R-AT-NODE |
| srv-extra-load-on-pin | detected | tak | SRV-SERIES-R-AT-NODE, SRV-COVERS-ODBIOR, U3-HC139 |
| srv-duplicate-node | detected | tak | SRV-SERIES-R-AT-NODE, SRV-COVERS-ODBIOR |
| srv-node-GND | detected | tak | SRV-SERIES-R-AT-NODE, SRV-COVERS-ODBIOR |
| R1-fp-SMD | detected | tak | PARTS-SOURCES |
| R11-fp-THT | detected | tak | PARTS-SOURCES |
| C1-fp-SMD | detected | tak | PARTS-SOURCES |
| C4-fp-THT | detected | tak | PARTS-SOURCES |
| R11-value | detected | tak | PARTS-SOURCES, RES-11 |
| C6-value | detected | tak | CAP-6 |
| U1-mpn | detected | tak | MPN |
| null-control (no change) | clean | nie | — |

Tylko schemat: PCB nie powstało (layout robi sesja lokalna). Kontrole nie zastępują odbioru na sprzęcie.
