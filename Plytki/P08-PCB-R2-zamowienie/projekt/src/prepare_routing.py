"""Prepare the Specctra DSN for Freerouting and freeze the pre-routed board (run once per DSN export, after route_critical.py).
P03 R6 has no power pours before routing (GND pours come after the import), so unlike P02 R4 nothing is turned from 'plane'
into a keepout: the locked 5 V copper is exported as fixed wiring and the router only adds the missing connections.
GND pins leave the net list (their pads stay obstacles): with GND in the list (the P02 R4 way) Freerouting routed ~120 GND pins
as tracks, a pass took up to 4 minutes and 48 signal connections stayed open after 15 passes (30.09, first run). GND is made
by the two pours after the import, the stitching vias and the completion planner (stitch.py stage 3, complete_routes.py).
30.09 evening (Ubuntu): GND plane mode (default). The DSN gets a GND plane on B.Cu and keeps the GND pins, so the router joins
each SMD GND pin to the plane with a short stub and a via placed where it finds room (Freerouting's plane handling), instead
of the pours reaching the pads after the routing. Trials: with GND out of the list 16-29 open signal connections plus 7-25
GND pads cut off after every run; with the plane 1-2 open after 20 passes. The real B.Cu pour is cut by the B.Cu tracks,
so stitch.py and the completion planner still tie the islands; cleanup.py keeps the fan-out vias that sit in the pour.
Router-only keepouts 0.4 mm wide along the board edges (Freerouting does not know the copper-to-edge
clearance, P03 R2 lesson). The rule areas (M3 zones and the board's own from build_board.py; P03 R6: ANTENNA M1, SD1 M2.5) are exported by KiCad as keepouts.
Review 2.10: board.ISOLATE nets get their own DSN class clearance (isolate below).
"""
from pathlib import Path
import shutil, subprocess, sys, json, re
P = Path(__file__).resolve().parents[1]; sys_path = __import__('sys').path.insert(0, str(Path(__file__).resolve().parent))
from board import NAME, CLASS, GND_INNER, ROUTER_KEEPOUT, ISOLATE
f = P / f'routing/{NAME}.dsn'; d = f.read_text()
assert 'EDGE_STRIP' not in d, 'DSN already prepared; re-run route_critical.py first'
assert '(plane ' not in d, 'unexpected plane in the DSN'
import os
GND_MODE = os.environ.get('EGRLAB_GND_MODE', 'plane')   # 'plane' (default since 30.09) or 'out' (GND pins out of the net list)
# P05 R3: the GND pins of U1 (LQFP-64, 0.5 mm) are tied inwards to the F.Cu pour inside the pad ring and its 4 vias
# (route_critical.py); the router cannot reach them with S1 widths, so they leave the GND net list (pads stay obstacles).
m_ = re.search(r'(\(net GND\s*\n\s*\(pins )([^)]*)\)', d); assert m_
kept = [q for q in m_.group(2).split() if not any(q.startswith(r + '-') for r in GND_INNER)]
d = d[:m_.start(2)] + ' '.join(kept) + d[m_.end(2):]
if GND_MODE == 'out':
    d, ng = re.subn(r'(\(net GND\s*\n\s*)\(pins [^)]*\)', r'\1(pins)', d); assert ng == 1, ng
S1 = json.loads((P.parents[0] / 'Format-S1/format-s1.json').read_text(encoding='utf-8')); W, H = S1['klasy'][CLASS]['W'], S1['klasy'][CLASS]['H']
e = .4; strips = [(0, 0, W, e), (0, H - e, W, H), (0, 0, e, H), (W - e, 0, W, H)]
add = ''.join(f'    (keepout "EDGE_STRIP" (polygon {L} 0  {x0 * 1000:.0f} {-y0 * 1000:.0f}  {x1 * 1000:.0f} {-y0 * 1000:.0f}  {x1 * 1000:.0f} {-y1 * 1000:.0f}  {x0 * 1000:.0f} {-y1 * 1000:.0f}))\n'
              for L in ('F.Cu', 'B.Cu') for x0, y0, x1, y1 in strips)
add += ''.join(f'    (keepout "ANALOG_GND" (polygon {L} 0  {x0 * 1000:.0f} {-y0 * 1000:.0f}  {x1 * 1000:.0f} {-y0 * 1000:.0f}  {x1 * 1000:.0f} {-y1 * 1000:.0f}  {x0 * 1000:.0f} {-y1 * 1000:.0f}))\n'
               for L, x0, y0, x1, y1 in ROUTER_KEEPOUT)   # P05 R3: the analog ground stays one piece (U1 inner pour -> vias -> B.Cu plane)
i = d.index('(keepout'); d = d[:i] + add.lstrip() + '    ' + d[i:]
if GND_MODE == 'plane':   # the router joins every GND pin to this B.Cu plane (SMD pins: short stub + via where it finds room)
    m = .5; pl = f'    (plane GND (polygon B.Cu 0  {m * 1000:.0f} {-m * 1000:.0f}  {(W - m) * 1000:.0f} {-m * 1000:.0f}  {(W - m) * 1000:.0f} {-(H - m) * 1000:.0f}  {m * 1000:.0f} {-(H - m) * 1000:.0f}))\n'
    i = d.index('(keepout'); d = d[:i] + pl.lstrip() + '    ' + d[i:]


def isolate(d):
    """Review 2.10 (MINOR-2): each net of board.ISOLATE leaves its DSN class for its own class with the given clearance (Freerouting
    keeps that distance from all other copper; KiCad DRC keeps the S1 rules, verify_pcb.py measures the distance to the TAP_* nets)."""
    i0 = d.index('    (class '); i1 = d.index('  (wiring')
    out = ''; moved = {}
    for name, nets, body in re.findall(r'    \(class (\S+)((?:\s+(?:"[^"]*"|[^\s()]+))*)\s*\n(.*?)\n    \)\n', d[i0:i1], re.S):
        toks = re.findall(r'"[^"]*"|[^\s()]+', nets); sel = [t for t in toks if t.strip('"').split('/')[-1] in ISOLATE]
        out += f'    (class {name} ' + ' '.join(t for t in toks if t not in sel) + '\n' + body + '\n    )\n'
        for t in sel:
            c = ISOLATE[t.strip('"').split('/')[-1]]; b2 = re.sub(r'\(clearance [0-9.]+\)', f'(clearance {c * 1000:.0f})', body)
            assert b2 != body, body
            out += f'    (class ISO_{len(moved)} {t}\n' + b2 + '\n    )\n'; moved[t] = c
    assert sorted(k.strip('"').split('/')[-1] for k in moved) == sorted(ISOLATE), (moved, ISOLATE)
    return d[:i0] + out + '  )\n' + d[i1:], moved


d, iso = isolate(d) if ISOLATE else (d, {})
f.write_text(d)
nk = d.count('(keepout ')
(P / 'routing/router-exclusions.json').write_text(json.dumps({'gnd_pins_inner_pour': GND_INNER, 'router_keepouts': ROUTER_KEEPOUT, 'keepouts_in_dsn': nk, 'edge_strips': len(strips) * 2, 'gnd_pins_removed': GND_MODE == 'out', 'gnd_mode': GND_MODE, 'isolated_nets_mm': iso}, indent=1) + '\n')
shutil.copy2(P / f'eda/{NAME}.kicad_pcb', P / 'routing/prerouted.kicad_pcb')
subprocess.run([sys.executable, str(P / 'src/set_rules.py')], check=True)
print('DSN:', nk, 'keepouts (rule areas + edge strips);', len(iso), 'nets with their own clearance; pre-routed board frozen.')
