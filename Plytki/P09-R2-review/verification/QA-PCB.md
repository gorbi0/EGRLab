# P09-R2 — QA PCB (format S1, klasa 1/3; plik generowany przez src/run_release.py)

DRC (świeży, wszystkie poziomy): 2 naruszeń / 0 niepołączonych / 0 niezgodności ze schematem (naruszenia to wyłącznie lib_footprint_mismatch części z przyciętym nadrukiem, przyjęte przez verify_pcb.py; szczegóły w pcb-checks.json).
Kontrole PCB: 22/22. Próby ujemne: 16/16 (w tym próba zerowa).

| Kontrola | Wynik |
|---|---|
| Fresh native DRC: 0 violations / 0 unconnected / 0 schematic parity (all severities; lib_footprint_mismatch only for parts whose silk silkscreen.py trimmed) | PASS |
| 46 on-board parts + 4 mounting holes, nothing else | PASS |
| Every value, footprint ID and pad net equals the exported schematic netlist | PASS |
| S1-2 section 4: parts on the bottom only SMD <= 1.5 mm, no SOIC (level 3), >= 1 mm from THT pads | PASS |
| 2 copper layers, 1.6 mm board (S1: FR4 1.6 mm) | PASS |
| Both copper layers 35 um (S1) | PASS |
| Outline class 1/3: 53.0 x 100.0 mm, 4 corner arcs R 1.0 mm (format-s1.json) | PASS |
| M3 holes: 4 NPTH 3.2 mm exactly at the S1 positions (x_w_slocie + 53.5 k, y 14 / 86) | PASS |
| Standoff zones D7: no courtyard and no copper (pads, tracks, vias, pours) within 3.5 mm of a hole centre; rule areas on both layers | PASS |
| Rules as P02 R3 / R4 (clearance >= 0.25, track >= 0.30, edge 0.5) and annular ring >= 0.25 mm (S1 section 3); no DRC exclusions | PASS |
| Every track >= 0.30 mm (S1 section 3) | PASS |
| Every PTH pad and via has an annular ring >= 0.25 mm (measured on the copper) | PASS |
| J1 = J_BP (edge A): IDC 2x8 angled, body front at y = 0, pin centre x = 26.5, pin 1 at the smaller x, pinout = docs/J_BP.csv (P12 contract) | PASS |
| Service header J2 (edge B, S1 section 6): <= 13 pins in x 10..43, pins out ~6 mm, GND on both ends, one 1 kOhm series resistor per pin as docs/SERWIS.csv, <= 10 mm from its node, one silk label per pin | PASS |
| Every part <= 16.5 mm above the board (level 3, S1 section 4; src/heights.py; the module socket is an estimate at the limit) | PASS |
| J3 / J4 MAX31856 sockets (MODUL-KWALIFIKACJA.md): module outline on the board, thermocouple terminal towards the input wall (x = 53.0, S1 sections 2 and 7), pin 1 / VIN at the smaller y; 6 mm support holes with 4.0 mm keepouts (washers OD 8 mm) on both layers, no copper in them | PASS |
| Decoupling at the IC pins: 100 nF pad <= 6 mm from its supply pin (C1 U1.14, C2 U2.14, C3 U3.16; limit as P03 R6) | PASS |
| Module supply capacitors: C6 / C7 pad <= 6.5 mm from the VIN pin of J3 / J4 (the module outline overhangs pin 1; see the comment) | PASS |
| Series resistors at their drivers: pad <= 6 mm from the driver pin (R14-R17 at U1, R11 / R12 at U2) | PASS |
| GND pours on both layers: B.Cu >= 50 % of the board; island removal always (every island tied) | PASS |
| Every visible reference outside the courtyards of other parts | PASS |
| Silkscreen: board name "P09 R2 S1-1/3", edge markers A and B | PASS |

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
| module_turned | J3 / J4 MAX31856 | tak | 3 |
| support_track | J3 / J4 MAX31856 | tak | 2 |
| decap_far | Decoupling | tak | 4 |
| driver_far | Series resistors at their drivers | tak | 2 |
| narrow_track | Every track >= | tak | 2 |
| bottom_tht | S1-2 section 4 | tak | 2 |
| gnd_pour_removed | GND pours | tak | 2 |
| ref_on_part | Every visible reference | tak | 2 |

Nadruk: ukryte oznaczenia (brak miejsca): R16, C7, R1, R19, R7, R8; nieumieszczone napisy: brak.

Oględziny PDF: strony 1–5 obejrzane przy tworzeniu pakietu (render w output/previews/pcb-*.png).
