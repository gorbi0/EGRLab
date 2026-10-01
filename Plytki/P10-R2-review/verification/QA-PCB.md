# P10-R2 — QA PCB (format S1, klasa 1/3; plik generowany przez src/run_release.py)

DRC (świeży, wszystkie poziomy): naruszenia 2, niepołączone 0, niezgodności ze schematem 0 (naruszenia to wyłącznie lib_footprint_mismatch części z przyciętym nadrukiem, przyjęte przez verify_pcb.py; szczegóły w pcb-checks.json).
Kontrole PCB: 24/24. Próby ujemne: 26/26 (w tym próba zerowa).

| Kontrola | Wynik |
|---|---|
| Fresh native DRC: 0 violations / 0 unconnected / 0 schematic parity (all severities; lib_footprint_mismatch only for parts whose silk silkscreen.py trimmed) | PASS |
| 20 on-board parts + 4 mounting holes, nothing else | PASS |
| Every value, footprint ID and pad net equals the exported schematic netlist | PASS |
| S1-2 section 4: parts on the bottom only SMD <= 1.5 mm, no SOIC (level 4), >= 1 mm from THT pads | PASS |
| 2 copper layers, 1.6 mm board (S1: FR4 1.6 mm) | PASS |
| Both copper layers 35 um (S1) | PASS |
| Outline class 1/3: 53.0 x 100.0 mm, 4 corner arcs R 1.0 mm (format-s1.json) | PASS |
| M3 holes: 4 NPTH 3.2 mm exactly at the S1 positions (x_w_slocie + 53.5 k, y 14 / 86) | PASS |
| Standoff zones D7: no courtyard and no copper (pads, tracks, vias, pours) within 3.5 mm of a hole centre; rule areas on both layers | PASS |
| Rules as P02 R3 / R4 (clearance >= 0.25, track >= 0.30, edge 0.5) and annular ring >= 0.25 mm (S1 section 3); no DRC exclusions | PASS |
| Every track >= 0.30 mm (S1 section 3) | PASS |
| Every PTH pad and via has an annular ring >= 0.25 mm (measured on the copper) | PASS |
| J1 = J_BP (edge A): IDC 2x5 angled, body front at y = 0, pin centre x = 26.5, pin 1 at the smaller x, pinout = docs/J_BP.csv (P12 contract) | PASS |
| Service header J2 (edge B, S1 section 6): <= 13 pins in x 10..43, pins out ~6 mm, GND on both ends, one series resistor per pin of the value in docs/SERWIS.csv, <= 10 mm from its node, one silk label per pin with the name of its node (LABEL in silkscreen.py), GND at the ends | PASS |
| Reserved strip of edge A (S1 §5: y 0-10, x 10-43 of each J_BP slot): no other part on either side; the edge-B zone of the service headers is reported only (S1 §6 gives the header position, not a reserved strip) | PASS |
| Every part <= 16.5 mm above the board (level 4, S1 section 4; src/heights.py) | PASS |
| J3 (OBD tail, W3) at the input wall: anchor holes towards x = 53.0 (12 mm from the solder row, hole edge 2-6 mm from the edge), pad 1 CAN_H at the smaller y, not in the edge A / B zones; no copper within 3 mm of the anchor-hole centres; no part under the cable between the anchor and the wall; D1 (PESD2CAN) pads <= 6 mm from the J3 pads and CAN_H / CAN_L pass through them to U1; other nets >= 1 mm from the J3 pads (hand-soldered wires) | PASS |
| Decoupling at the IC pins: 100 nF pad <= 6 mm from its supply pin (C1 U1.3 VCC, C2 U1.5 VIO, C3 U2.14; limit as P03 R6 / P09 R2) | PASS |
| Series resistor at its driver: R1 (100 R, CAN_RX to P03) pad <= 6 mm from U2.3 | PASS |
| GND pours on both layers: B.Cu >= 50 % of the board; island removal always (every island tied) | PASS |
| Every visible reference outside the courtyards of other parts | PASS |
| Every visible reference nearer its own part than any other (text centre to courtyard; review 1.10) | PASS |
| Pin 1 / polarity marks of module and wire connectors on the silkscreen, <= 3 mm from their pads (S1 §9; review 1.10) | PASS |
| Silkscreen: board name "P10 R2 S1-1/3 S3", edge markers A and B | PASS |

## Próby ujemne

| Wada | Oczekiwana kontrola | Wykryta | Zgłoszone |
|---|---|---|---|
| null_control | none (all PASS) | tak | 0 |
| mount_shift | M3 holes | tak | 1 |
| jbp_shift | J1 = J_BP | tak | 2 |
| sv_no_gnd_end | Service header J2 | tak | 3 |
| sv_pin_without_resistor | Service header J2 | tak | 3 |
| sv_resistor_far | Service header J2 | tak | 2 |
| label_missing | Service header J2 | tak | 1 |
| too_tall | Every part <= | tak | 1 |
| obd_turned | J3 (OBD tail | tak | 5 |
| anchor_track | J3 (OBD tail | tak | 2 |
| cable_blocked | J3 (OBD tail | tak | 3 |
| d1_far | J3 (OBD tail | tak | 3 |
| decap_far | Decoupling | tak | 3 |
| driver_far | Series resistor at its driver | tak | 4 |
| narrow_track | Every track >= | tak | 2 |
| bottom_soic | S1-2 section 4 | tak | 3 |
| gnd_pour_removed | GND pours | tak | 2 |
| ref_on_part | Every visible reference | tak | 3 |
| ref_far | Every visible reference nearer | tak | 2 |
| label_swap | Service header J2 | tak | 1 |
| strip_part | Reserved strip of edge A | tak | 2 |
| mark_missing | Pin 1 / polarity marks | tak | 1 |
| can_bypass | J3 (OBD tail | tak | 2 |
| j3_close | J3 (OBD tail | tak | 2 |
| zone_copper | Standoff zones D7 | tak | 2 |
| title_wrong | Silkscreen: board name | tak | 1 |

Nadruk: ukryte oznaczenia (brak miejsca): R1, R3, D1; nieumieszczone napisy: brak.

Oględziny PDF: wpis ręczny w README (sekcja „PCB”); render stron w output/previews/pcb-*.png.
