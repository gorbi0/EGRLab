# P06-R2 — QA PCB (format S1, klasa 2/3; plik generowany przez src/run_release.py)

DRC (świeży, wszystkie poziomy): naruszenia 3, niepołączone 0, niezgodności ze schematem 0 (naruszenia to wyłącznie lib_footprint_mismatch części z przyciętym nadrukiem, przyjęte przez verify_pcb.py; szczegóły w pcb-checks.json).
Kontrole PCB: 34/34. Próby ujemne: 37/37 (w tym próba zerowa).

| Kontrola | Wynik |
|---|---|
| Fresh native DRC: 0 violations / 0 unconnected / 0 schematic parity (all severities; lib_footprint_mismatch only for parts whose silk silkscreen.py trimmed) | PASS |
| 73 on-board parts + 8 mounting holes, nothing else | PASS |
| Every value, footprint ID and pad net equals the exported schematic netlist | PASS |
| S1-2 section 4: parts on the bottom only SMD <= 1.5 mm (heights.py, BOM thickness note for the capacitors), no SOIC, >= 1 mm from THT pads | PASS |
| 2 copper layers, 1.6 mm board (S1: FR4 1.6 mm) | PASS |
| Both copper layers 35 um (S1) | PASS |
| Outline class 2/3: 106.5 x 100.0 mm, 4 corner arcs R 1.0 mm (format-s1.json) | PASS |
| M3 holes: 8 NPTH 3.2 mm exactly at the S1 positions (x_w_slocie + 53.5 k, y 14 / 86) | PASS |
| Standoff zones D7: no courtyard and no copper (pads, tracks, vias, pours) within 3.5 mm of a hole centre; rule areas on both layers | PASS |
| Rules as P02 R3 / R4 (clearance >= 0.25, PWR 0.30 / 0.6 mm for 5V_SYS, 5VA_P06, SW_RAW, track >= 0.30, edge 0.5), annular ring >= 0.25 mm (S1 section 3); no custom rule file, no DRC exclusions | PASS |
| Every track >= 0.30 mm (S1 section 3) and every track of 5V_SYS, 5VA_P06, SW_RAW >= 0.6 mm (class PWR) | PASS |
| Every PTH pad and via has an annular ring >= 0.25 mm (measured on the copper) | PASS |
| J_BP (edge A): IDC 2x8 angled in slot S2, body front at y = 0, pin centre x = 80.0, pin 1 at the smaller x, pinout = docs/J_BP.csv (P12 contract) | PASS |
| Service headers J_SV1 / J_SV2 (edge B, S1 section 6): <= 13 pins in x 10..43 of the slot, pin 1 at the larger x, pins out ~6 mm, GND on both ends, one series resistor per pin as docs/SERWIS.csv and of its S1 class (1K, 10K for the analog nodes and supervisor outputs) <= 10 mm from its node, one silk label per pin with the name of its node (LABEL in silkscreen.py), GND at both ends | PASS |
| Reserved strip of edge A (S1 §5: y 0-10 along J_BP, x 63.5-96.5): no other part on either side | PASS |
| Every part <= 16.5 mm above the board (level 4, S1 section 4; src/heights.py) | PASS |
| Force pours ECU_P1 / EGR_P1: one zone per net on F.Cu and on B.Cu, priority above GND, solid connection (no thermals) on every force pad (J3, J4, RSH1 1/4), each pad inside the fill of every layer it is on | PASS |
| Force path >= 4 mm wide on both layers (fill shrunk by 2 mm stays one piece): J3.1-J4.1 (ECU_P1) and J3.2-J4.2 (EGR_P1); towards the shunt the 4 mm corridor reaches <= 3.5 mm from the force pad centre (the pad itself is 2.03 mm wide) | PASS |
| Force pours stitched: >= 8 vias per net (plus the PTH pads of J3 / J4); no via in or within 0.3 mm of an RSH1 pad | PASS |
| Nothing under the shunt: no copper of any net on B.Cu in the RSH1 courtyard (tracks, vias, pours) and on F.Cu only the RSH1 nets (ECU_P1, EGR_P1, K_PLUS, K_MINUS) | PASS |
| Kelvin pair from the sense pads (README): K_PLUS RSH1.2 -> R1 <= 12 mm, K_MINUS RSH1.3 -> R2 <= 8 mm, R1 / R2 -> U1.8 / U1.1 <= 6 mm, F.Cu only, no via, no pour on these nets; the two lines run as a pair (every point of K_MINUS / INA_MINUS <= 5 mm from K_PLUS / INA_PLUS) | PASS |
| No track or via of another net in the box spanned by the Kelvin pair (shunt to U1, both layers; pours allowed) | PASS |
| Measuring loop short: J3.1 -> RSH1.1 and RSH1.4 -> J3.2 pad centres <= 10 mm apart; U1 (INA240) <= 20 mm from the shunt sense pads (README) | PASS |
| Panel side: J3 / J4 / J5 pad rows in one column <= 18 mm from x = 0, anchor holes 1-6 mm from x = 0 with their 3 mm rule areas and no track in them, no part on the cable between the anchors and the pads; column J3.1 ECU, J3.2 EGR, J4.2 EGR, J4.1 ECU (each force net one piece of copper) | PASS |
| R21 (PR02, 0.7 W) >= 20 mm (courtyard to courtyard) from RSH1, U1 (INA240), U10 (reference) and the op-amp / ADC U2 / U3; PR02 on top | PASS |
| Decoupling and filter capacitors at their pins: pad <= 6 mm from the supply / input pin (100 nF at every IC, C1 / C2 / C16 / C4), C5 4.7 uF <= 5 mm from U10.2 (MCP1525 data sheet), C3 220 uF <= 8 mm from R6.2 (5VA_P06) | PASS |
| GND pours on both layers: B.Cu >= 50 % of the board; island removal always (every island tied) | PASS |
| Analog block: no track and no via other than GND between the pin rows of U2 / U3 (both layers) and in the strip between them (B.Cu); review 2.10 F2 / F3 (service tracks ran under U2 / U3 and cut the B.Cu plane) | PASS |
| Decoupling return through GND copper: capacitor GND pad -> GND pin of its part <= 1.3 x straight + 3 mm (both layers, gndpath.py; C6 accepted at <= 14 mm; review 2.10 F2: GND islands under U2 / U3, C15 -> U10.1 about 30 mm) | PASS |
| Every visible reference outside the courtyards of other parts | PASS |
| Every visible reference nearer its own part than any other (text centre to courtyard; review 1.10) | PASS |
| Net marks of the tails J3 / J4 (ECU / EGR) and J5 (5VA / SW / GND) on the silkscreen next to their pads (text centre <= pad edge + 3 mm; S1 §9) | PASS |
| Silkscreen legible: every visible text on F.SilkS / B.SilkS >= 1.0 mm high with a >= 0.15 mm line (JLCPCB legend minimum; review 2.10 F1: service labels, edge markers, pin marks and six references were 0.8-0.9 / 0.12 mm) | PASS |
| Silkscreen: board name "P06 R2 S1-2/3 S1-S2", edge markers A and B | PASS |

## Próby ujemne

| Wada | Oczekiwana kontrola | Wykryta | Zgłoszone |
|---|---|---|---|
| null_control | none (all PASS) | tak | 0 |
| mount_shift | M3 holes | tak | 1 |
| jbp_shift | J_BP (edge A) | tak | 3 |
| sv_no_gnd_end | Service headers | tak | 3 |
| sv_pin_without_resistor | Service headers | tak | 3 |
| sv_resistor_far | Service headers | tak | 2 |
| label_missing | Service headers | tak | 1 |
| label_swap | Service headers | tak | 1 |
| too_tall | Every part <= | tak | 1 |
| narrow_track | Every track >= | tak | 2 |
| pwr_thin | Every track >= | tak | 1 |
| bottom_soic | S1-2 section 4 | tak | 5 |
| dru_present | Rules as P02 | tak | 1 |
| force_pour_missing | Force pours ECU_P1 | tak | 3 |
| force_thermal | Force pours ECU_P1 | tak | 2 |
| force_narrow | Force path >= 4 mm | tak | 1 |
| via_in_shunt_pad | Force pours stitched | tak | 3 |
| under_shunt | Nothing under the shunt | tak | 3 |
| kelvin_via | Kelvin pair | tak | 1 |
| foreign_in_kelvin | No track or via of another net | tak | 2 |
| anchor_track | Panel side | tak | 2 |
| part_on_cable | Panel side | tak | 4 |
| tail_turned | Panel side | tak | 5 |
| column_swap | Panel side | tak | 5 |
| r21_near | R21 | tak | 4 |
| c5_far | Decoupling and filter | tak | 2 |
| decap_far | Decoupling and filter | tak | 5 |
| gnd_pour_removed | GND pours | tak | 3 |
| ref_on_part | Every visible reference outside | tak | 3 |
| ref_far | Every visible reference nearer | tak | 3 |
| strip_part | Reserved strip of edge A | tak | 4 |
| mark_missing | Net marks of the tails | tak | 1 |
| zone_copper | Standoff zones D7 | tak | 2 |
| title_wrong | Silkscreen: board name | tak | 1 |
| silk_small | Silkscreen legible | tak | 2 |
| analog_track | Analog block | tak | 1 |
| return_cut | Decoupling return | tak | 1 |

Nadruk: ukryte oznaczenia (brak miejsca): R12, R11, U10; nieumieszczone napisy: brak.

Oględziny PDF: wpis ręczny w README (sekcja „PCB”); render stron w output/previews/pcb-*.png.
