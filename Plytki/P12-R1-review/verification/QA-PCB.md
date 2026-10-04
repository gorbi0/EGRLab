# P12-R1 — QA PCB (płytka połączeń krawędzi A, LOGGER; plik generowany przez src/run_release.py)

DRC (świeży, wszystkie poziomy): naruszenia 0, niepołączone 0, niezgodności ze schematem 0 (szczegóły w pcb-checks.json).
Kontrole PCB: 21/21. Próby ujemne: 19/19 (w tym próba zerowa).

| Kontrola | Wynik |
|---|---|
| Fresh native DRC: 0 violations / 0 unconnected / 0 schematic parity (all severities, zones refilled) | PASS |
| 14 parts of the netlist + 6 mounting holes, nothing else; every footprint ID and pad net equals the netlist | PASS |
| Every connector: straight IDC of the contract type on the top side; every pad net = docs/kontrakt-P12.json (NC pins of P04/P07/P08 unconnected) | PASS |
| Connector centres (x of the stack, z above the floor) = zlacza-P12.csv x and z_bottom + 1.6 + 4.45 mm, within 0.5 mm (J10: x 26.5, z 14.05) | PASS |
| Orientation of every connector: pin 1 at the smaller x, odd pins in one row along +x, pin 2k directly 2.54 mm ABOVE pin 2k-1 (odd row lower: mirror of the angled IDC on the boards, untwisted ribbon) | PASS |
| 2 copper layers, 1.6 mm | PASS |
| Both copper layers 35 um | PASS |
| Outline 160 x 92 mm (x 0..160, z 4..96), 4 corner arcs R 1 | PASS |
| M3: 6 NPTH 3.2 mm at the README positions | PASS |
| Standoff zones D7: no copper within 3.5 mm of a hole centre; courtyards >= 1 mm outside the zone (screw head, ribbon sockets); rule areas on both layers | PASS |
| Rules: clearance >= 0.25, edge 0.5, ring 0.25, silk text >= 1.0 / 0.15 mm, no DRC exclusions; class PWR (5V_SYS) 1.0 mm, P3V3 (3V3_IO) 0.5 mm | PASS |
| Track widths: 5V_SYS >= 1.0 mm, 3V3_IO >= 0.5 mm, every other track >= 0.25 mm | PASS |
| Every PTH pad and via has an annular ring >= 0.25 mm | PASS |
| 5V_SYS, 3V3_IO and GND separate (no DRC short); P03 J_BP2 16/17/19/20 (PFAIL_N, 5V_SYS) and P05 J_BP2 16/17/19/20 (GND) without a copper path | PASS |
| Every 5V_SYS / 3V3_IO pad joined over copper to the source P02 J_BP (J1.2 / J1.8) | PASS |
| GND pours on both layers (each >= 50 % of the board, island removal always) and >= 20 GND stitching vias | PASS |
| Test pads TP1 / TP4 GND, TP2 5V_SYS, TP3 3V3_IO | PASS |
| Every silkscreen text >= 1.0 mm high and >= 0.15 mm stroke (JLCPCB) | PASS |
| Every connector: one label "Jn  Pxx <connector> (poziom k, Sx)" centred above it and one "1" mark <= 7.5 mm from pin 1, nearer pin 1 than the last odd pin | PASS |
| No silkscreen text inside a connector / pad courtyard (stays visible next to a mated socket) or off the board | PASS |
| Silkscreen: board name "P12 R1 S1 LOGGER" and orientation marks (STRONA STOSU, x = 0 PANEL) | PASS |

## Próby ujemne

| Wada | Oczekiwana kontrola | Wykryta | Zgłoszone |
|---|---|---|---|
| null_control | none (all PASS) | tak | 0 |
| conn_shift | Connector centres | tak | 4 |
| conn_low | Connector centres | tak | 3 |
| conn_turned | Orientation | tak | 4 |
| rows_swapped | Orientation | tak | 5 |
| hole_shift | M3: | tak | 1 |
| zone_copper | Standoff zones D7 | tak | 2 |
| v5_narrow | Track widths | tak | 1 |
| v3_narrow | Track widths | tak | 1 |
| pin_in_pin | 5V_SYS, 3V3_IO and GND separate | tak | 2 |
| pad_net | Every connector: straight IDC | tak | 4 |
| wrong_type | Every connector: straight IDC | tak | 3 |
| gnd_pour_removed | GND pours | tak | 2 |
| label_missing | Every connector: one label | tak | 1 |
| label_swap | Every connector: one label | tak | 1 |
| pin1_missing | Every connector: one label | tak | 1 |
| small_text | Every silkscreen text | tak | 2 |
| label_on_body | No silkscreen text inside | tak | 3 |
| title_wrong | Silkscreen: board name | tak | 1 |

Nadruk: 10 opisów złączy, 10 znaczników pinu 1, 4 opisów pól pomiarowych; oznaczenia footprintów ukryte (opis złącza zawiera oznaczenie).

Oględziny PDF: wpis ręczny w README (sekcja „PCB”); render stron w output/previews/pcb-*.png.
