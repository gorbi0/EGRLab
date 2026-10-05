# P08-R2 — QA PCB (format S1, klasa 1/3; plik generowany przez src/run_release.py)

DRC (świeży, wszystkie poziomy): naruszenia 2, niepołączone 0, niezgodności ze schematem 0 (naruszenia to wyłącznie lib_footprint_mismatch części z przyciętym nadrukiem, przyjęte przez verify_pcb.py; szczegóły w pcb-checks.json).
Kontrole PCB: 28/28. Próby ujemne: 27/27 (w tym próba zerowa).

| Kontrola | Wynik |
|---|---|
| Fresh native DRC: 0 violations / 0 unconnected / 0 schematic parity (all severities; lib_footprint_mismatch only for parts whose silk silkscreen.py trimmed) | PASS |
| 52 on-board parts + 4 mounting holes, nothing else | PASS |
| Every value, footprint ID and pad net equals the exported schematic netlist | PASS |
| S1-2 section 4: parts on the bottom only SMD <= 1.5 mm, no SOIC (level 5), >= 1 mm from THT pads | PASS |
| 2 copper layers, 1.6 mm board (S1: FR4 1.6 mm) | PASS |
| Both copper layers 35 um (S1) | PASS |
| Outline class 1/3: 53.0 x 100.0 mm, 4 corner arcs R 1.0 mm (format-s1.json) | PASS |
| M3 holes: 4 NPTH 3.2 mm exactly at the S1 positions (x_w_slocie + 53.5 k, y 14 / 86) | PASS |
| Standoff zones D7: no courtyard and no copper (pads, tracks, vias, pours) within 3.5 mm of a hole centre; rule areas on both layers | PASS |
| Rules as P02 R3 / R4 (clearance >= 0.25, track >= 0.30, edge 0.5) and annular ring >= 0.25 mm (S1 section 3); no DRC exclusions | PASS |
| Every track >= 0.30 mm (S1 section 3) | PASS |
| Every PTH pad and via has an annular ring >= 0.25 mm (measured on the copper) | PASS |
| J1 = J_BP (edge A): IDC 2x8 angled, body front at y = 0, pin centre x = 26.5, pin 1 at the smaller x, pinout = docs/J_BP.csv (P12 contract) | PASS |
| Service header J2 (edge B, S1 section 6): <= 13 pins in x 10..43, pins out ~6 mm, GND on both ends, one series resistor per pin of the value in docs/SERWIS.csv, <= 10 mm from its node, one silk label per pin with the name of its node (LABEL in silkscreen.py), GND at the ends | PASS |
| Reserved strip of edge A (S1 §5: y 0-10, x 10-43 of each J_BP slot): no other part on either side; the edge-B zone of the service headers is reported only (S1 §6 gives the header position, not a reserved strip) | PASS |
| Every part <= 16.5 mm above the board (level 5, S1 section 4; src/heights.py; G6K 5.2, DIP18 5.33, C10 12.5) | PASS |
| J4 (TSENSOR pair W4) at the panel side: anchor holes 12 mm from the pads towards x = 0, hole edge 1.5-6 mm from x = 0 (the pair leaves through the panel to the TEST port), solder row <= 25 mm in, not in the edge A / B zones; no copper within 3 mm of the anchor centres | PASS |
| Sensor path through K1 (task 5.10): U1.6 -> K1.3 <= 8 mm, K1.4 -> J4.1 (5V_SENSOR) and K1.5 -> J4.2 (AGND_SENSOR) <= 12 mm of track; the return contact K1.6 joined solid (no thermal spokes) to the GND pour on both layers | PASS |
| Track widths of the supply and sensor path: every 5V_SYS track >= 0.6 mm, every SENSOR_LIMITED / 5V_SENSOR / AGND_SENSOR track >= 0.5 mm (task 5.10) | PASS |
| Decoupling at the pins: capacitor pad <= 7 mm from its supply pin (C1 / C2 U1 IN / OUT, C3-C5 U3-U5 VCC, C6-C8 supervisors VDD, C9 K1 coil +) | PASS |
| Series resistor at its driver: R11 (SENSOR_OK) / R13 (SENSOR_HEALTHY) 100 R pad <= 6 mm from U4.6 / U5.6 | PASS |
| Decoupling, ground side: capacitor GND pad -> GND pin of its part through GND copper <= 1.3 x straight + 3 mm (gndpath.py, as P05 R3 review 2.10) | PASS |
| GND pours on both layers: B.Cu >= 50 % of the board; island removal always (every island tied) | PASS |
| Every visible reference outside the courtyards of other parts | PASS |
| Every visible reference nearer its own part than any other (text centre to courtyard; review 1.10) | PASS |
| Pin 1 mark of the TSENSOR wire field J4 on the silkscreen, <= 3 mm from its pad (S1 §9) | PASS |
| Silkscreen legible: every visible text on F.SilkS / B.SilkS >= 1.0 mm high with a >= 0.15 mm line (JLCPCB legend minimum; as P05 R3 review 2.10) | PASS |
| Silkscreen: board name "P08 R2 S1-1/3 S1", edge markers A and B | PASS |

## Próby ujemne

| Wada | Oczekiwana kontrola | Wykryta | Zgłoszone |
|---|---|---|---|
| null_control | none (all PASS) | tak | 0 |
| mount_shift | M3 holes | tak | 1 |
| jbp_shift | J1 = J_BP | tak | 4 |
| sv_no_gnd_end | Service header J2 | tak | 3 |
| sv_pin_without_resistor | Service header J2 | tak | 3 |
| sv_resistor_far | Service header J2 | tak | 2 |
| label_missing | Service header J2 | tak | 1 |
| too_tall | Every part <= | tak | 1 |
| j4_turned | J4 (TSENSOR | tak | 5 |
| anchor_track | J4 (TSENSOR | tak | 2 |
| k1_thermal | Sensor path through K1 | tak | 1 |
| sensor_cut | Sensor path through K1 | tak | 2 |
| sensor_narrow | Track widths of the supply | tak | 1 |
| supply_narrow | Track widths of the supply | tak | 1 |
| decap_far | Decoupling at the pins | tak | 2 |
| driver_far | Series resistor at its driver | tak | 4 |
| narrow_track | Every track >= | tak | 2 |
| bottom_soic | S1-2 section 4 | tak | 5 |
| gnd_pour_removed | GND pours | tak | 4 |
| ref_on_part | Every visible reference | tak | 3 |
| ref_far | Every visible reference nearer | tak | 3 |
| label_swap | Service header J2 | tak | 1 |
| strip_part | Reserved strip of edge A | tak | 5 |
| mark_missing | Pin 1 mark of the TSENSOR | tak | 1 |
| small_text | Silkscreen legible | tak | 2 |
| zone_copper | Standoff zones D7 | tak | 2 |
| title_wrong | Silkscreen: board name | tak | 1 |

Nadruk: ukryte oznaczenia (brak miejsca): R16, R10, R11, R18, R6, R9, C1, U1; nieumieszczone napisy: brak.

Oględziny PDF: wpis ręczny w README (sekcja „PCB”); render stron w output/previews/pcb-*.png.
