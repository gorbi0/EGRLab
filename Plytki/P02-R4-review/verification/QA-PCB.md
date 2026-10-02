# P02-R4 — QA PCB (etap 2, format S1; plik generowany przez src/run_release.py)

DRC (świeży, wszystkie poziomy): 14 naruszeń / 0 niepołączonych / 0 niezgodności ze schematem.
Kontrole PCB: 23/23. Próby ujemne: 12/12 (w tym próba zerowa).

| Kontrola | Wynik |
|---|---|
| Fresh native DRC: 0 violations / 0 unconnected / 0 schematic parity (all severities; lib_footprint_mismatch only for parts whose silk silkscreen.py trimmed) | PASS |
| 127 on-board parts + 12 mounting holes, nothing else | PASS |
| Every value, footprint ID and pad net equals the exported schematic netlist | PASS |
| S1-2 section 4: parts on the bottom only SMD <= 1.5 mm (SOIC allowed on level 1), >= 1 mm from THT pads (standoff zones: check below) | PASS |
| 2 copper layers, 1.6 mm board (S1: FR4 1.6 mm) | PASS |
| Both copper layers 35 um (S1) | PASS |
| Outline class L: 160.0 x 100.0 mm, 4 corner arcs R 1.0 mm (format-s1.json) | PASS |
| M3 holes: 12 NPTH 3.2 mm exactly at the S1 positions (x_w_slocie + 53.5 k, y 14 / 86) | PASS |
| Standoff zones D7: no courtyard and no copper (pads, tracks, vias, pours) within 3.5 mm of a hole centre; rule areas on both layers | PASS |
| Rules as P02 R3 (clearance >= 0.25, track >= 0.30, edge 0.5) and annular ring >= 0.25 mm (S1); no DRC exclusions | PASS |
| Every PTH pad and via has an annular ring >= 0.25 mm (measured on the copper) | PASS |
| J_BP (edge A): IDC 2x10 angled, body front at y = 0, centre x = 133.5 (slot S3), pin 1 at smaller x, pinout = S1 section 8 | PASS |
| Service headers (edge B, S1 section 6): <= 13 pins in x 10..43 of the slot, pins out ~6 mm, GND on both ends, one series resistor of its class at the node (<= 10 mm or in its pour), one silk label per pin | PASS |
| Every part <= 21.5 mm above the board (level 1, S1 section 4; heights in parts.py) | PASS |
| 5 A path J1 -> Q9 -> SW_COM -> Q1 -> VSW -> F1 -> J2 and the GND return: >= 4.0 mm of net copper on every cross-section (+/-3 mm) between the pads (IPC-2152, 35 um, 5 A, <= 20 K) | PASS |
| GND return corridor on B.Cu: rule area contains J1.2 and J2.2, no track or via inside | PASS |
| GND pours: B.Cu >= 50 % of the board; island removal always (every island tied) | PASS |
| TO-220 (Q9, Q1, Q2, D1, D2): under each tab only copper of the tab net (pin 2) on F.Cu | PASS |
| Decoupling at the pins (task section 2): capacitor pad <= 8 mm from its pin | PASS |
| C_H, D2 and D1 close together: HOLD_C pads within 20 mm of each other | PASS |
| J1 BAT, J2 VMOTOR, J15 VBAT_IN at the input wall x = 160 (pads/anchors <= 17 mm from it); J2 mating face at the edge | PASS |
| Every visible reference outside the courtyards of other parts | PASS |
| Silkscreen: board name "P02 R4 S1-L S1-S3", edge markers A and B | PASS |

## Próby ujemne

| Wada | Oczekiwana kontrola | Wykryta | Zgłoszone |
|---|---|---|---|
| null_control | none (all PASS) | tak | 0 |
| mount_shift | M3 holes | tak | 1 |
| jbp_shift | J_BP (edge A) | tak | 3 |
| sv_no_gnd_end | Service headers | tak | 3 |
| sv_pin_without_resistor | Service headers | tak | 3 |
| too_tall | Every part <= | tak | 1 |
| neck_5a | 5 A path | tak | 3 |
| decap_far | Decoupling | tak | 3 |
| tab_foreign | TO-220 | tak | 2 |
| corridor_track | GND return corridor | tak | 3 |
| hold_far | C_H, D2 and D1 | tak | 3 |
| label_missing | Service headers | tak | 1 |

Nadruk: ukryte oznaczenia (brak miejsca): R67, R23, D9, R35, R30, R26, R22, R42, R10, R16, Q9, Q2, C6, F1, F2, F3, U6, U5, J_SV2, J_SV1; nieumieszczone napisy: 1, 1, 1, 1, 1, 1.

Oględziny PDF: strony 1–5 obejrzane przy tworzeniu pakietu (render w output/previews/pcb-*.png).
