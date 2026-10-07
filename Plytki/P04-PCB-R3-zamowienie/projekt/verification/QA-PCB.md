# P04-R3 — QA PCB (format S1, klasa L; plik generowany przez src/run_release.py)

DRC (świeży, wszystkie poziomy): naruszenia 6, niepołączone 0, niezgodności ze schematem 0 (naruszenia to wyłącznie lib_footprint_mismatch części z przyciętym nadrukiem, przyjęte przez verify_pcb.py; szczegóły w pcb-checks.json).
Kontrole PCB: 31/31. Próby ujemne: 33/33 (w tym próba zerowa).

| Kontrola | Wynik |
|---|---|
| Fresh native DRC: 0 violations / 0 unconnected / 0 schematic parity (all severities; lib_footprint_mismatch only for parts whose silk silkscreen.py trimmed and whose pads equal the library) | PASS |
| 100 on-board parts + 12 mounting holes, nothing else | PASS |
| Every value, footprint ID and pad net equals the exported schematic netlist | PASS |
| S1-2 section 4: parts on the bottom only SMD <= 1.5 mm, no SOIC (level 6 is not level 1), >= 1 mm from THT pads (P04 R3: none on the bottom) | PASS |
| 2 copper layers, 1.6 mm board (S1: FR4 1.6 mm) | PASS |
| Both copper layers 35 um (S1) | PASS |
| Outline class L: 160.0 x 100.0 mm, 4 corner arcs R 1.0 mm (format-s1.json) | PASS |
| M3 holes: 12 NPTH 3.2 mm exactly at the S1 positions (x_w_slocie + 53.5 k, y 14 / 86) | PASS |
| Standoff zones D7: no courtyard and no copper (pads, tracks, vias, pours) within 3.5 mm of a hole centre; rule areas on both layers | PASS |
| Rules as P02 R3 / R4 (clearance >= 0.25, track >= 0.30, edge 0.5), annular ring >= 0.25 mm (S1 section 3); class PWR 0.4 mm for 3V3_IO, P04_3V3, PANEL_3V3, 5V_SYS; no custom rules file, no DRC exclusions | PASS |
| Every track >= 0.30 mm (S1 section 3) | PASS |
| Supply nets 3V3_IO, P04_3V3, PANEL_3V3, 5V_SYS: every track >= 0.4 mm (task 5.10: P04_3V3, 5V_SYS, PANEL_3V3 >= 0.4 mm; 3V3_IO in the same class) | PASS |
| Every PTH pad and via has an annular ring >= 0.25 mm (measured on the copper) | PASS |
| J_BP1..3 (edge A): IDC 2x8 / 2x10 / 2x10 angled, body front at y = 0, pin centre x = 26.5 / 80.0 / 133.5 (slots S1-S3), pin 1 at the smaller x, odd pins GND, pinout = docs/J_BP.csv (P12 contract) | PASS |
| Service headers J_SV1..3 (edge B, S1 section 6): <= 13 pins in x 10..43 of the slot, pin 1 at the larger x, pins out ~6 mm, GND on both ends, one series resistor per pin as docs/SERWIS.csv and of its class (1K; 10K SAFE_N / ARM_BUTTON_N, README decision 6) <= 10 mm from its node (a pad or locked via of the node net), one silk label per pin with the name of its node (LABEL in silkscreen.py), GND at both ends | PASS |
| Reserved strip of edge A (S1 §5: y 0-10, x 10-43 of each J_BP slot): no other part | PASS |
| Every part <= 16.5 mm above the board (limit above level 6, user decision 5.10; src/heights.py) | PASS |
| Watchdog RC traces (WD_RC, WD_C) <= 15 mm each, locked, F.Cu only, without vias (P04 R2.2) | PASS |
| C1 lands on the U1 timing nodes (C1.1 = U1.15 = WD_RC, C1.2 = U1.14 = WD_C), not on ground (P04 R2.2) | PASS |
| SAFE_N ends at U2.11: C18 (1 nF) pad <= 5 mm, R5 (100 k) pad <= 16 mm, both SAFE_N / GND (P04 R2.2 R4-04) | PASS |
| Series resistors at their connector pins (P04 R2.2 R4-03 / R4-07, MECHANIKA): R40 PANEL_3V3, R42 MECH_OK, R3 ARM_CONTACT, R41 TEST_KEY at J_BP1, R39 P04_3V3 and R38 PG_SEND at J_BP2; the connector-side net holds only pin + resistor (+ its service resistor), pad <= 10 mm from the pin (R39 <= 15 mm: end of the P04_3V3 escape), copper within the limit | PASS |
| SUP_N_OUT short and referenced to GND (KONTRAKT-RESET, README): copper <= 20 mm, <= 1 via, J_BP3.11 / .13 GND, GND pour on the other layer under >= 70 % of its length (pour, tracks or pads), U9.5 <= 10 mm and R17 <= 6 mm from it; net = J_BP3.12 + R17.1 + U9.5 only | PASS |
| Decoupling at the IC supply pins: 100 nF pad 1 (3V3_IO) <= 6 mm from the VCC pin on the copper (U1-U11, second 100 nF C15-C17 at U8-U10) | PASS |
| Decoupling, ground side: capacitor GND pad -> GND pin of its IC through GND copper <= 1.3 x straight + 3 mm (gndpath.py; P05 R3 review 2.10 method) | PASS |
| Default-state resistors at their buffers (MECHANIKA): R12-R22 (input side) and R25-R35 (output side) pad <= 12 mm from the U8-U10 pin | PASS |
| GND pours on both layers: B.Cu >= 50 % of the board; island removal always (every island tied) | PASS |
| Every visible reference outside the courtyards of other parts | PASS |
| Every visible reference nearer its own part than any other (text centre to courtyard; P03 R6 review 1.10) | PASS |
| Pin 1 of every connector (J_BP1..3, J_SV1..3) marked "1" on the silkscreen <= 3 mm from the pad (S1 §9) | PASS |
| Silkscreen legible: every visible text on F.SilkS / B.SilkS >= 1.0 mm high with a >= 0.15 mm line (JLCPCB legend minimum) | PASS |
| Silkscreen: board name "P04 R3 S1-L S1-S3", edge markers A and B | PASS |

## Próby ujemne

| Wada | Oczekiwana kontrola | Wykryta | Zgłoszone |
|---|---|---|---|
| null_control | none (all PASS) | tak | 0 |
| mount_shift | M3 holes | tak | 1 |
| jbp_shift | J_BP1..3 | tak | 2 |
| jbp_flip | J_BP1..3 | tak | 6 |
| sv_no_gnd_end | Service headers | tak | 3 |
| sv_pin_without_resistor | Service headers | tak | 3 |
| sv_resistor_far | Service headers | tak | 2 |
| label_missing | Service headers | tak | 1 |
| label_swap | Service headers | tak | 1 |
| too_tall | Every part <= | tak | 1 |
| bottom_soic | S1-2 section 4 | tak | 4 |
| narrow_track | Every track >= | tak | 2 |
| narrow_supply | Supply nets | tak | 1 |
| wd_via | Watchdog RC | tak | 2 |
| wd_unlocked | Watchdog RC | tak | 1 |
| c1_grounded | C1 lands | tak | 3 |
| c18_far | SAFE_N ends at U2.11 | tak | 4 |
| ser_detour | Series resistors at their connector | tak | 2 |
| ser_extra_pad | Series resistors at their connector | tak | 3 |
| supn_long | SUP_N_OUT short | tak | 2 |
| supn_r17_far | SUP_N_OUT short | tak | 3 |
| supn_no_ref | SUP_N_OUT short | tak | 1 |
| decap_far | Decoupling at the IC | tak | 5 |
| default_far | Default-state resistors | tak | 4 |
| gnd_pour_removed | GND pours | tak | 3 |
| zone_copper | Standoff zones D7 | tak | 2 |
| ref_on_part | Every visible reference | tak | 3 |
| ref_far | Every visible reference nearer | tak | 2 |
| strip_part | Reserved strip of edge A | tak | 5 |
| mark_missing | Pin 1 of every connector | tak | 1 |
| title_wrong | Silkscreen: board name | tak | 1 |
| silk_small | Silkscreen legible | tak | 2 |
| rules_dru | Rules as P02 | tak | 2 |

Nadruk: ukryte oznaczenia (brak miejsca): R14, R16, R17, R18, R19, R2, R21, R25, R29, R32, R33, R42, R44, R46, R54, R56, R6, R61, C11, C13, C15, C16, C17; nieumieszczone napisy: brak.

Oględziny PDF: wpis ręczny w README (sekcja „PCB”); render stron w output/previews/pcb-*.png.
