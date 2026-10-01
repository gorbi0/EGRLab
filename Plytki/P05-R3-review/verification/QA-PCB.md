# P05-R3 — QA PCB (format S1, klasa 2/3; plik generowany przez src/run_release.py)

DRC (świeży, wszystkie poziomy): naruszenia 4, niepołączone 0, niezgodności ze schematem 0 (naruszenia to wyłącznie lib_footprint_mismatch części z przyciętym nadrukiem, przyjęte przez verify_pcb.py; szczegóły w pcb-checks.json).
Kontrole PCB: 30/30. Próby ujemne: 31/31 (w tym próba zerowa).

| Kontrola | Wynik |
|---|---|
| Fresh native DRC: 0 violations / 0 unconnected / 0 schematic parity (all severities; lib_footprint_mismatch only for parts whose silk silkscreen.py trimmed) | PASS |
| 119 on-board parts + 8 mounting holes, nothing else | PASS |
| Every value, footprint ID and pad net equals the exported schematic netlist | PASS |
| S1-2 section 4: parts on the bottom only SMD <= 1.5 mm (heights.py, BOM thickness note for the capacitors), no SOIC, >= 1 mm from THT pads | PASS |
| 2 copper layers, 1.6 mm board (S1: FR4 1.6 mm) | PASS |
| Both copper layers 35 um (S1) | PASS |
| Outline class 2/3: 106.5 x 100.0 mm, 4 corner arcs R 1.0 mm (format-s1.json) | PASS |
| M3 holes: 8 NPTH 3.2 mm exactly at the S1 positions (x_w_slocie + 53.5 k, y 14 / 86) | PASS |
| Standoff zones D7: no courtyard and no copper (pads, tracks, vias, pours) within 3.5 mm of a hole centre; rule areas on both layers | PASS |
| Rules as P02 R3 / R4 (net classes: clearance >= 0.25, PWR 0.30, track >= 0.30, edge 0.5), annular ring >= 0.25 mm (S1 section 3); custom rules only: track >= 0.30 outside, clearance 0.15 / track 0.2 only for items touching the courtyard of U1 / U3 (fine pitch, README); no DRC exclusions | PASS |
| Every track >= 0.30 mm (S1 section 3); narrower ones (>= 0.2) only where they touch the courtyard of U1 / U3 | PASS |
| Every PTH pad and via has an annular ring >= 0.25 mm (measured on the copper) | PASS |
| J_BP1 / J_BP2 (edge A): IDC 2x5 / 2x10 angled, body front at y = 0, pin centre x = 26.5 / 80.0 (slots S1 / S2), pin 1 at the smaller x, pinout = docs/J_BP.csv (P12 contract) | PASS |
| Service headers J_SV1 / J_SV2 (edge B, S1 section 6): <= 13 pins in x 10..43 of the slot, pin 1 at the larger x, pins out ~6 mm, GND on both ends, one series resistor per pin as docs/SERWIS.csv and of its S1 class (1K, 10K for high-impedance / pull-up nodes, 4.7K VBAT_SENSE) <= 10 mm from its node, one silk label per pin with the name of its node (LABEL in silkscreen.py), GND at both ends | PASS |
| Reserved strip of edge A (S1 §5: y 0-10, x 10-43 of each J_BP slot): no other part on either side | PASS |
| Every part <= 16.5 mm above the board (level 3, S1 section 4; src/heights.py) | PASS |
| U1 decoupling on the copper (R2 table, review P5-01): AVCC 1 / 48 / 37 / 38, REGCAP 36 / 39 and REFIN/OUT 42 (100 nF) <= 3 mm, VDRIVE 23 <= 4 mm, 22 uF on REFIN/OUT 42 and REFCAP 44 / 45 <= 6 mm (pad centre to pad centre) | PASS |
| REGCAP_A, REGCAP_D and REFCAP without vias, their capacitors (and the 22 uF on ADC_REF) on top; ADC_REF has one via only (to C11 on the bottom, 100 nF <= 1.5 mm, README) | PASS |
| DOUT (AD_DOUT_LOCAL) not under U1 on B.Cu and no via inside the U1 courtyard (review P5-01) | PASS |
| U1 ground: every GND pin touches the F.Cu pour inside the pad ring (solid connection) on a piece that holds a GND via, >= 4 GND vias inside the ring to B.Cu | PASS |
| No copper of other nets in the U1 courtyard (only the nets of U1 pins: escapes, decoupling, inner pour vias; README) | PASS |
| Panel side: TAPS J4 and AUX J6 anchor holes 1.5-6 mm from x = 0 (cables leave through the panel), solder rows <= 25 mm in; SW1 (E-Switch M6) bushing and lever beyond x = 0, support legs and poles on the board | PASS |
| Decoupling at the IC pins: capacitor pad <= 6 mm from its supply / output pin (U2-U12; C1 220 uF at R1 pin 2 = 5VA_P05; limit as P03 R6 / P09 R2) | PASS |
| Series resistors at the driver (R26 DOUT, R27 BUSY: pad <= 6 mm from U11.3 / U11.6) and flyback diodes at their coils (D1-D3 anode <= 6 mm from K1-K3 pin 8) | PASS |
| Input filters C27-C34 on the channel copper <= 12 mm from their U1 inputs (pins 49-63; 45 deg fan to the filter column) | PASS |
| GND pours on both layers: B.Cu >= 50 % of the board; island removal always (every island tied) | PASS |
| Every visible reference outside the courtyards of other parts | PASS |
| Every visible reference nearer its own part than any other (text centre to courtyard; review 1.10) | PASS |
| Pin 1 marks of the wire tails TAPS J4 and AUX J6 on the silkscreen, <= 3 mm from their pads (S1 §9) | PASS |
| Silkscreen: board name "P05 R3 S1-2/3 S1-S2", edge markers A and B | PASS |

## Próby ujemne

| Wada | Oczekiwana kontrola | Wykryta | Zgłoszone |
|---|---|---|---|
| null_control | none (all PASS) | tak | 0 |
| mount_shift | M3 holes | tak | 1 |
| jbp_shift | J_BP1 / J_BP2 | tak | 2 |
| sv_no_gnd_end | Service headers | tak | 3 |
| sv_pin_without_resistor | Service headers | tak | 3 |
| sv_resistor_far | Service headers | tak | 2 |
| label_missing | Service headers | tak | 1 |
| label_swap | Service headers | tak | 1 |
| too_tall | Every part <= | tak | 1 |
| refcap_far | U1 decoupling | tak | 4 |
| regcap_far | U1 decoupling | tak | 3 |
| refcap_via | REGCAP_A, REGCAP_D and REFCAP | tak | 2 |
| dout_under | DOUT | tak | 2 |
| u1_gnd_thermal | U1 ground | tak | 2 |
| foreign_in_u1 | No copper of other nets in the U1 | tak | 2 |
| fine_rule_everywhere | Rules as P02 | tak | 1 |
| narrow_track | Every track >= | tak | 2 |
| bottom_soic | S1-2 section 4 | tak | 4 |
| sw1_inside | Panel side | tak | 4 |
| taps_turned | Panel side | tak | 4 |
| decap_far | Decoupling at the IC pins | tak | 2 |
| driver_far | Series resistors at the driver | tak | 4 |
| diode_far | Series resistors at the driver | tak | 3 |
| filter_far | Input filters | tak | 4 |
| gnd_pour_removed | GND pours | tak | 2 |
| ref_on_part | Every visible reference | tak | 3 |
| ref_far | Every visible reference nearer | tak | 2 |
| strip_part | Reserved strip of edge A | tak | 2 |
| mark_missing | Pin 1 marks | tak | 1 |
| zone_copper | Standoff zones D7 | tak | 2 |
| title_wrong | Silkscreen: board name | tak | 1 |

Nadruk: ukryte oznaczenia (brak miejsca): R11, R18, R33, R5, R7, C10, C14, C20, C25, C28, C12; nieumieszczone napisy: brak.

Oględziny PDF: wpis ręczny w README (sekcja „PCB”); render stron w output/previews/pcb-*.png.
