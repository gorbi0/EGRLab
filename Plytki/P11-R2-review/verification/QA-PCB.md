# P11-R2 — QA PCB (płytka okablowania panelu; plik generowany przez src/run_release.py)

DRC (świeży, wszystkie poziomy): naruszenia 1, niepołączone 0, niezgodności ze schematem 0 (lib_footprint_mismatch dopuszczalne tylko u części z przyciętym nadrukiem, przyjęte przez verify_pcb.py; szczegóły w pcb-checks.json).
Kontrole PCB: 20/20. Próby ujemne: 29/29 (w tym próba zerowa).

| Kontrola | Wynik |
|---|---|
| Fresh native DRC: 0 violations / 0 unconnected / 0 schematic parity (all severities; lib_footprint_mismatch only for parts whose silk silkscreen.py trimmed) | PASS |
| Parts: the 5 on-board parts of the schematic + 4 mounting holes, nothing else | PASS |
| Netlist: every value, footprint ID and pad net equals the exported schematic netlist | PASS |
| Board stack: 2 copper layers of 35 um, FR4 1.6 mm | PASS |
| All parts on the top side (wire fields and the header are soldered from the top; nothing under the board lying on the panel-zone floor) | PASS |
| Outline: 36 x 100 mm within the limit 45 x 130 mm (user 4.10), long side along y (the panel wall), 4 corner arcs R 1 | PASS |
| M3 holes: 4 NPTH 3.2 mm, one per corner, 4 mm from the long edges; bottom pair <= 4.5 mm from the short edge, top pair directly behind J_P12 (D7 zone edge 0-6 mm beyond its courtyard: the header fills the short edge) | PASS |
| Standoff zones D7: no courtyard and no copper (pads, tracks, vias, pours) within 3.5 mm of a hole centre; rule areas on both layers | PASS |
| Rules: clearance >= 0.25, track >= 0.3, copper to edge 0.5, ring >= 0.25, DRC legend minimum 1.0 / 0.15 mm (JLCPCB), class P3V3 0.4 mm for PANEL_3V3 / 3V3_IO; no DRC exclusions | PASS |
| Track widths: every track >= 0.3 mm; PANEL_3V3 and 3V3_IO >= 0.4 mm (user 4.10) | PASS |
| Every PTH pad and via has an annular ring >= 0.25 mm (measured on the copper) | PASS |
| J_P12: IDC 2x10 right-angle box header on the short edge y = 0 (wall A, ribbon to P12): mating face within 0.3 mm of the edge, pins centred on the width, pin 1 at the smaller x with one silk "1" next to it, pinout = docs/J_P12.csv | PASS |
| Wire fields J11 / J8 / J6 at the panel edge x = 0: holes 1.0-1.1 mm, pads >= 2.0 mm (AWG24); 2 cable-tie anchors Ø3.2 NPTH between the pads and the panel edge (hole edge 2-6 mm from it, spanning the pad rows), no copper within 3 mm of the anchors, no other part in the strip where the wires lie | PASS |
| Field labels: every column of J11 / J8 / J6 has exactly one silk label beside it naming the panel contact; the label resolves (parts.json X11-X17 / X6 pins, docs/PORTY.csv TEST cavities) to exactly the nets of the column pads | PASS |
| R1 variant note on the silkscreen next to R1 (<= 12 mm): "LOGGER: LUTOWAC" and "Z P04: DNP", matching the variant in parts.json | PASS |
| Legend size: every visible silk text >= 1.0 mm high with a line >= 0.15 mm (JLCPCB minimum) | PASS |
| GND pours on both layers (each >= 50 % of the board), island removal always, >= 20 GND stitching vias | PASS |
| Every visible reference outside the courtyards of other parts; every part has a visible reference | PASS |
| Every visible reference nearer its own part than any other and <= 3 mm from its courtyard (text centre) | PASS |
| Silkscreen: board name "P11 R2 PANEL" and the marker "STRONA PANELU" along the panel edge x = 0 | PASS |

## Próby ujemne

| Wada | Oczekiwana kontrola | Wykryta | Zgłoszone |
|---|---|---|---|
| null_control | none (all PASS) | tak | 0 |
| drc_short | Fresh native DRC | tak | 1 |
| ref_renamed | Parts | tak | 3 |
| value_changed | Netlist | tak | 2 |
| copper_18um | Board stack | tak | 1 |
| small_ring | Every PTH pad and via | tak | 2 |
| rules_relaxed | Rules | tak | 1 |
| outline_arc_missing | Outline | tak | 2 |
| mount_shift | M3 holes | tak | 2 |
| zone_copper | Standoff zones D7 | tak | 2 |
| jp12_off_edge | J_P12 | tak | 4 |
| jp12_pinout | J_P12 | tak | 3 |
| pin1_mark_missing | J_P12 | tak | 1 |
| narrow_track | Track widths | tak | 2 |
| supply_03 | Track widths | tak | 1 |
| field_turned | Wire fields | tak | 3 |
| field_drill | Wire fields | tak | 2 |
| anchor_track | Wire fields | tak | 2 |
| strip_blocked | Wire fields | tak | 5 |
| label_missing | Field labels | tak | 1 |
| label_swap | Field labels | tak | 1 |
| label_swap_test | Field labels | tak | 1 |
| variant_missing | R1 variant note | tak | 1 |
| small_text | Legend size | tak | 2 |
| gnd_pour_removed | GND pours | tak | 2 |
| bottom_part | All parts on the top side | tak | 2 |
| ref_on_part | Every visible reference outside | tak | 2 |
| ref_far | Every visible reference nearer | tak | 2 |
| title_wrong | Silkscreen: board name | tak | 1 |

Nadruk: ukryte oznaczenia (brak miejsca): brak; nieumieszczone napisy: brak.

Oględziny PDF: wpis ręczny w README (sekcja „PCB”); render stron w output/previews/pcb-*.png.
