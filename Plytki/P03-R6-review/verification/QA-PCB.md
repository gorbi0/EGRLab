# P03-R6 — QA PCB (format S1, klasa L; plik generowany przez src/run_release.py)

DRC (świeży, wszystkie poziomy): 6 naruszeń / 0 niepołączonych / 0 niezgodności ze schematem (naruszenia to wyłącznie lib_footprint_mismatch części z przyciętym nadrukiem, przyjęte przez verify_pcb.py; szczegóły w pcb-checks.json).
Kontrole PCB: 25/25. Próby ujemne: 16/16 (w tym próba zerowa).

| Kontrola | Wynik |
|---|---|
| Fresh native DRC: 0 violations / 0 unconnected / 0 schematic parity (all severities; lib_footprint_mismatch only for parts whose silk silkscreen.py trimmed) | PASS |
| 122 on-board parts + 12 mounting holes, nothing else | PASS |
| Every value, footprint ID and pad net equals the exported schematic netlist | PASS |
| S1-2 section 4: parts on the bottom only SMD <= 1.5 mm, no SOIC (level 2), >= 1 mm from THT pads | PASS |
| 2 copper layers, 1.6 mm board (S1: FR4 1.6 mm) | PASS |
| Both copper layers 35 um (S1) | PASS |
| Outline class L: 160.0 x 100.0 mm, 4 corner arcs R 1.0 mm (format-s1.json) | PASS |
| M3 holes: 12 NPTH 3.2 mm exactly at the S1 positions (x_w_slocie + 53.5 k, y 14 / 86) | PASS |
| Standoff zones D7: no courtyard and no copper (pads, tracks, vias, pours) within 3.5 mm of a hole centre; rule areas on both layers | PASS |
| Rules as P02 R3 / R4 (clearance >= 0.25, edge 0.5), annular ring >= 0.25 mm (S1); tracks >= 0.20 mm, 3V3_CORE class 0.30, PWR 0.60 (user decision 30.09: signals 0.2 mm on P03 R6 only); no DRC exclusions | PASS |
| Every PTH pad and via has an annular ring >= 0.25 mm (measured on the copper) | PASS |
| J_BP1..3 (edge A): IDC 2x10 angled, body front at y = 0, pin centre x = 26.5 / 80 / 133.5, pin 1 at the smaller x, pinout = docs/J_BP.csv (P12 contract) | PASS |
| Service headers J_SV1..3 (edge B, S1 section 6): <= 13 pins in x 10..43 of the slot, pins out ~6 mm, GND on both ends, one series resistor per pin as docs/SERWIS.csv and of its S1 class (1K, 10K for pull-up / open-drain nodes) <= 10 mm from its node, one silk label per pin | PASS |
| Every part <= 16.5 mm above the board (level 2, S1 section 4; src/heights.py) | PASS |
| M1 Waveshare: two 1x22 rows 22.86 mm apart, USB-C end towards edge B (face <= 6.5 mm inside it), antenna end towards edge A | PASS |
| ANTENNA keepout: M1 antenna end + 3 mm sides + 8 mm beyond, both layers, no track / via / pad / pour inside; no other part inside | PASS |
| SD1 Adafruit 4682: card towards edge B (tip <= 6.5 mm inside it), M2.5 keepouts r 3 mm around both holes, both layers, no copper | PASS |
| 5 V path: continuous locked copper >= 1.2 mm J_BP2.19 -> Q1 D and Q1 S -> M1 J1-21; copper resistance <= 50 mOhm (20 C, 35 um) | PASS |
| Decoupling at the pins: capacitor pad 1 <= 6 mm from its supply pin (C14 at M1 J1-21) | PASS |
| Series / termination resistors at their drivers: pad <= 6 mm from the driver pin (R36-R40 source termination, R41, R34) | PASS |
| README layout requirements: U21 by J_BP2 (<= 30 mm), U22 by J_BP1 (<= 30 mm; decision 30.09, disputed: README asked J_BP2), U23 by J_BP3 (<= 25 mm), U6 / R41 / C15 at J_BP3.12, R42 at M1 J1-13, R43 at J_BP2.16 | PASS |
| SUP_N_OUT copper on P03 <= 30 mm (reset edge budget: local 3 pF of the 30 pF, README "Reset do P04") | PASS |
| GND pours on both layers: B.Cu >= 50 % of the board; island removal always (every island tied) | PASS |
| Every visible reference outside the courtyards of other parts | PASS |
| Silkscreen: board name "P03 R6 S1-L", edge markers A and B | PASS |

## Próby ujemne

| Wada | Oczekiwana kontrola | Wykryta | Zgłoszone |
|---|---|---|---|
| null_control | none (all PASS) | tak | 0 |
| mount_shift | M3 holes | tak | 1 |
| jbp_shift | J_BP1..3 | tak | 4 |
| sv_no_gnd_end | Service headers | tak | 3 |
| sv_pin_without_resistor | Service headers | tak | 3 |
| too_tall | Every part <= | tak | 1 |
| usb_far | M1 Waveshare | tak | 4 |
| sd_far | SD1 Adafruit | tak | 2 |
| antenna_track | ANTENNA keepout | tak | 2 |
| spine_neck | 5 V path | tak | 1 |
| decap_far | Decoupling | tak | 3 |
| term_far | Series / termination | tak | 2 |
| r43_far | README layout requirements | tak | 4 |
| supout_long | SUP_N_OUT copper | tak | 2 |
| label_missing | Service headers | tak | 1 |
| ref_on_part | Every visible reference | tak | 2 |

Nadruk: ukryte oznaczenia (brak miejsca): R27, R41, R51, R53, R9, C2, U6; nieumieszczone napisy: brak.

Oględziny PDF: strony 1–5 obejrzane przy tworzeniu pakietu (render w output/previews/pcb-*.png).
