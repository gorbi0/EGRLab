"""M1-R1 PCB checks after run_layout.py + silkscreen.py (KiCad Python). The board is read once into a snapshot; every check works on the
snapshot, so the negative controls (verification/negative-controls.json) mutate a copy and must make the expected check fail; the null
control (unchanged copy) must pass everything. A fresh DRC (all severities, schematic parity, zones refilled) is part of the snapshot.
Checks: DRC / parity, outline and holes, X1 wire-pad order (docs/X1.csv), board edges (SD slot, thermocouple terminals, USB-C), antenna
area free of copper, force path (pours on both outer layers joining the right pads, stitching), Kelvin pair locked only, router copper
outside the shunt / Kelvin / U3 keepouts (check_intrusion.py), PWR track widths, decoupling returns (return_check.py), silkscreen."""
from pathlib import Path
import pcbnew as p, json, sys, os, subprocess, copy, csv, collections
sys.path.insert(0, str(Path(__file__).resolve().parent))
import board as BD
P = Path(__file__).resolve().parents[1]; PCB = P / f'eda/{BD.NAME}.kicad_pcb'
CLI = os.environ.get('KICAD_CLI', str(Path(sys.executable).with_name('kicad-cli.exe')))
mm = p.ToMM


def snapshot():
    subprocess.run([CLI, 'pcb', 'drc', '--format', 'json', '--severity-all', '--schematic-parity', '--all-track-errors', '--refill-zones',
                    '-o', str(P / 'verification/drc.json'), str(PCB)], check=True, stdout=subprocess.DEVNULL)
    drc = json.loads((P / 'verification/drc.json').read_text())
    b = p.LoadBoard(str(PCB)); b.BuildConnectivity()
    for z in b.Zones():
        if not z.GetIsRuleArea():
            z.UnFill()
    p.ZONE_FILLER(b).Fill(b.Zones())
    S = {'drc': collections.Counter(v['type'] for v in drc['violations']), 'unconnected': len(drc['unconnected_items']), 'parity': len(drc['schematic_parity'])}
    bb = b.GetBoardEdgesBoundingBox(); S['outline'] = [round(mm(bb.GetWidth()), 3), round(mm(bb.GetHeight()), 3)]; S['layers'] = b.GetCopperLayerCount()
    fps = {f.GetReference(): f for f in b.GetFootprints()}
    S['holes'] = sorted((round(mm(f.GetPosition().x), 2), round(mm(f.GetPosition().y), 2)) for r, f in fps.items() if r.startswith('H'))
    S['pads'] = {f'{r}.{a.GetNumber()}': [round(mm(a.GetPosition().x), 3), round(mm(a.GetPosition().y), 3), a.GetNetname().split('/')[-1]]
                 for r, f in fps.items() for a in f.Pads() if a.GetNumber()}
    S['npth'] = {r: [[round(mm(a.GetPosition().x), 2), round(mm(a.GetPosition().y), 2)] for a in f.Pads() if a.GetAttribute() == p.PAD_ATTRIB_NPTH]
                 for r, f in fps.items() if r in BD.TAILS}
    S['courtyard'] = {}
    for r, f in fps.items():
        f.BuildCourtyardCaches(); c = f.GetCourtyard(p.F_CrtYd).BBox() if not f.IsFlipped() else f.GetCourtyard(p.B_CrtYd).BBox()
        S['courtyard'][r] = [round(mm(c.GetLeft()), 2), round(mm(c.GetTop()), 2), round(mm(c.GetRight()), 2), round(mm(c.GetBottom()), 2)]
    fab = {}
    for r in ('SD1', 'M1'):
        ys = [mm(g.GetBoundingBox().GetBottom()) for g in fps[r].GraphicalItems() if g.GetLayer() == p.F_Fab]
        fab[r] = round(max(ys), 2)
    S['fab_bottom'] = fab
    # antenna rule area: copper of any kind inside it
    ant = next(z for z in b.Zones() if z.GetIsRuleArea() and z.GetZoneName() == 'ANTENNA M1')
    hits = 0
    for t in b.GetTracks():
        q = t.GetPosition() if isinstance(t, p.PCB_VIA) else t.GetStart()
        if ant.Outline().Contains(q) or (not isinstance(t, p.PCB_VIA) and ant.Outline().Contains(t.GetEnd())):
            hits += 1
    for z in b.Zones():
        if z.GetIsRuleArea():
            continue
        for L in z.GetLayerSet().Seq():
            fp_ = z.GetFilledPolysList(L)
            if fp_.OutlineCount():
                x = p.SHAPE_POLY_SET(fp_); x.BooleanIntersection(ant.Outline())
                hits += 1 if x.OutlineCount() and x.Area() > 1e6 else 0
    S['antenna_copper'] = hits
    # force pours: filled polygon on F.Cu / B.Cu holding the expected pads; stitching vias
    def poly_of(net, L, ref, num):
        a = next(q for q in fps[ref].Pads() if q.GetNumber() == str(num))
        for z in b.Zones():
            if not z.GetIsRuleArea() and z.GetNetname().split('/')[-1] == net and z.IsOnLayer(L):
                fp_ = p.SHAPE_POLY_SET(z.GetFilledPolysList(L)); fp_.Unfracture()   # P07 lesson: fill polygons come fractured
                r = max(mm(a.GetSize(L).x), mm(a.GetSize(L).y)) / 2 + .8                # thermal gap round a THT pad
                for k in range(fp_.OutlineCount()):
                    o = p.SHAPE_POLY_SET(); o.AddOutline(fp_.Outline(k))
                    if o.Collide(a.GetPosition(), p.FromMM(r)):
                        return k
        return None
    S['force'] = {}
    for net, ends in {'BAT_P': [('J1', 1), ('F1', 1)], 'VBUS': [('F1', 2), ('J2', 1)], 'P1_ECU': [('J5', 1), ('RSH1', 1)], 'P1_EGR': [('RSH1', 4), ('J5', 2)]}.items():
        ks = [poly_of(net, p.F_Cu, *e) for e in ends]
        S['force'][net] = {'f_same_poly': ks[0] is not None and len(set(ks)) == 1,
                           'b_pour': any(not z.GetIsRuleArea() and z.GetNetname().split('/')[-1] == net and z.IsOnLayer(p.B_Cu) and z.GetFilledPolysList(p.B_Cu).OutlineCount() for z in b.Zones()),
                           'vias': sum(1 for t in b.GetTracks() if isinstance(t, p.PCB_VIA) and t.GetNetname().split('/')[-1] == net)}
    S['kelvin_unlocked'] = sum(1 for t in b.GetTracks() if t.GetNetname().split('/')[-1] in BD.KELVIN and not t.IsLocked())
    S['pwr_thin'] = sorted({t.GetNetname().split('/')[-1] for t in b.GetTracks() if not isinstance(t, p.PCB_VIA) and not t.IsLocked()
                            and t.GetNetname().split('/')[-1] in BD.PWR and mm(t.GetWidth()) < BD.PWR_W - 1e-6})
    r = subprocess.run([sys.executable, str(P / 'src/check_intrusion.py')], capture_output=True, text=True); S['intrusion'] = r.returncode
    r = subprocess.run([sys.executable, str(P / 'src/return_check.py')], capture_output=True, text=True); S['returns'] = r.returncode
    silk = json.loads((P / 'routing/silkscreen.json').read_text(encoding='utf-8'))
    S['silk_hidden'] = silk['hidden_references']; S['silk_unplaced'] = silk['unplaced_texts']
    return S


X1 = list(csv.DictReader((P / 'docs/X1.csv').open(encoding='utf-8-sig'), delimiter=';'))


def checks(S):
    out = []
    def add(name, ok, note):
        out.append({'check': name, 'pass': bool(ok), 'note': note})
    allowed = {'lib_footprint_mismatch'}   # footprints whose silk silkscreen.py trimmed (as P07 S1)
    bad = {k: v for k, v in S['drc'].items() if k not in allowed}
    add('DRC: 0 naruszen (poza lib_footprint_mismatch po przycieciu nadruku), 0 niepolaczonych, 0 niezgodnosci ze schematem',
        not bad and S['unconnected'] == 0 and S['parity'] == 0, f"{dict(S['drc'])}, unconnected {S['unconnected']}, parity {S['parity']}")
    add('Obrys 150 x 80 mm, 4 warstwy miedzi, 4 otwory M3 w narozach', all(abs(u - v) < .1 for u, v in zip(S['outline'], (BD.W, BD.H))) and S['layers'] == 4
        and S['holes'] == sorted((round(x, 2), round(y, 2)) for x, y in BD.HOLES), f"{S['outline']}, {S['layers']} warstwy, {S['holes']}")
    rows = [(row['x1'], row['pole_pcb'], row['siec']) for row in X1 if row['pole_pcb'] != '-']
    xs = [S['pads'][pp][0] for _, pp, _ in rows]; ys = {S['pads'][pp][1] for _, pp, _ in rows}
    nets_ok = all(S['pads'][pp][2] == n for _, pp, n in rows)
    anchors_ok = all(all(y < min(S['pads'][k][1] for k in S['pads'] if k.startswith(r + '.')) for _, y in S['npth'][r]) for r in ('J1', 'J2', 'J5', 'J6'))
    add('Pola przewodow X1 w jednym rzedzie przy gornej krawedzi, w kolejnosci zaciskow, sieci jak docs/X1.csv, kotwy opasek nad polami',
        xs == sorted(xs) and len(set(xs)) == len(xs) and len(ys) == 1 and nets_ok and anchors_ok, f'{len(rows)} pol, y {sorted(ys)}, x {xs[0]}..{xs[-1]}')
    cy = S['courtyard']
    edges = {'SD1 (gniazdo karty)': BD.H - S['fab_bottom']['SD1'], 'M1 (USB-C)': BD.H - S['fab_bottom']['M1'],
             'TC1 (zacisk termopary)': BD.H - cy['TC1'][3], 'TC2 (zacisk termopary)': BD.H - cy['TC2'][3]}
    add('Dolna krawedz: gniazdo SD, USB-C modulu i zaciski termopar <= 1,5 mm od krawedzi', all(-.01 <= v <= 1.5 for v in edges.values()),
        ', '.join(f'{k} {v:.2f} mm' for k, v in edges.items()))
    add('Antena ESP32: brak miedzi w strefie ANTENNA M1 (sciezki, przelotki, wylewki)', S['antenna_copper'] == 0, f"{S['antenna_copper']} elementow")
    fo = S['force']
    add('Tor 7,5 A: wylewki F.Cu laczace J1.1-F1.1, F1.2-J2.1, J5.1-RSH1.1, RSH1.4-J5.2; wylewki B.Cu; >= 2 przelotki zszywajace na siec',
        all(v['f_same_poly'] and v['b_pour'] and v['vias'] >= 2 for v in fo.values()), json.dumps(fo))
    add('Para Kelvina tylko z miedzi zablokowanej (route_critical.py)', S['kelvin_unlocked'] == 0, f"{S['kelvin_unlocked']} odcinkow routera")
    add('Brak obcej miedzi routera przy boczniku, parze Kelvina i wewnatrz U3 (check_intrusion.py)', S['intrusion'] == 0, f"kod {S['intrusion']}")
    add(f'Sciezki zasilan (PWR) routera >= {BD.PWR_W} mm', not S['pwr_thin'], f"za cienkie: {S['pwr_thin'] or 'brak'}")
    add('Powroty odsprzegania w limicie (return_check.py)', S['returns'] == 0, f"kod {S['returns']}")
    add('Nadruk: napisy plytki umieszczone; oznaczenia bez miejsca (<= 10 %) na rysunku montazowym z F.Fab', not S['silk_unplaced'] and len(S['silk_hidden']) <= 9,
        f"ukryte {S['silk_hidden'] or 'brak'}, nieumieszczone {S['silk_unplaced'] or 'brak'}")
    return out


def mutate(S, fn):
    T = copy.deepcopy(S); fn(T); return T


def swap_x1(T):
    T['pads']['J6.1'][0], T['pads']['J6.2'][0] = T['pads']['J6.2'][0], T['pads']['J6.1'][0]


NEG = [('DRC: jedno naruszenie clearance', 'DRC', lambda T: T['drc'].update({'clearance': 1})),
       ('Brak otworu M3', 'Obrys', lambda T: T['holes'].pop()),
       ('Pola X1.7 / X1.8 zamienione', 'Pola przewodow', swap_x1),
       ('Gniazdo SD 3 mm od krawedzi', 'Dolna krawedz', lambda T: T['fab_bottom'].update({'SD1': BD.H - 3.0})),
       ('Przelotka w strefie anteny', 'Antena', lambda T: T.update({'antenna_copper': 1})),
       ('P1_EGR rozciete na F.Cu', 'Tor 7,5 A', lambda T: T['force']['P1_EGR'].update({'f_same_poly': False})),
       ('VBUS bez przelotek zszywajacych', 'Tor 7,5 A', lambda T: T['force']['VBUS'].update({'vias': 0})),
       ('Odcinek routera na K_MINUS', 'Para Kelvina', lambda T: T.update({'kelvin_unlocked': 1})),
       ('Obca sciezka przy boczniku', 'Brak obcej miedzi', lambda T: T.update({'intrusion': 4})),
       ('5V sciezka 0,3 mm', 'Sciezki zasilan', lambda T: T.update({'pwr_thin': ['5V']})),
       ('Powrot kondensatora za dlugi', 'Powroty', lambda T: T.update({'returns': 5})),
       ('Napis plytki bez miejsca', 'Nadruk', lambda T: T.update({'silk_unplaced': ['EGRLab M1-R1']}))]
S = snapshot()
base = checks(S)
neg = []
for name, target, fn in NEG:
    failed = [c['check'] for c in checks(mutate(S, fn)) if not c['pass']]
    neg.append({'control': name, 'expected_failing_check': target, 'failed_checks': failed, 'detected': any(f.startswith(target) for f in failed)})
null = [c['check'] for c in checks(copy.deepcopy(S)) if not c['pass']]
neg.append({'control': 'proba zerowa (kopia bez zmian)', 'expected_failing_check': '-', 'failed_checks': null, 'detected': not null})
res = {'checks': base, 'passed': sum(c['pass'] for c in base), 'total': len(base)}
(P / 'verification/pcb-checks.json').write_text(json.dumps(res, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
(P / 'verification/negative-controls.json').write_text(json.dumps(neg, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
(P / 'verification/pcb-snapshot.json').write_text(json.dumps({k: v for k, v in S.items() if k not in ('pads', 'courtyard')}, indent=1, default=dict) + '\n')
for c in base:
    print('PASS' if c['pass'] else 'FAIL', c['check'], '|', c['note'][:160])
print(f"checks {res['passed']}/{res['total']}; negative controls {sum(x['detected'] for x in neg)}/{len(neg)}")
sys.exit(0 if res['passed'] == res['total'] and all(x['detected'] for x in neg) else 1)
