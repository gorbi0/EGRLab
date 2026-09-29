"""P04 R2 PCB from the exported schematic netlist (verification/P04.xml) and src/placement.json.
Taken over from the P02 R1 builder; outline W x H and the four M3 holes are parameters (bench fixture,
not in the module stack), 2 x 35 um copper (see set_stackup.py).
"""
from pathlib import Path
import pcbnew as p, json, re, math, xml.etree.ElementTree as ET
P = Path(__file__).resolve().parents[1]; E = P / 'eda'
mm = p.FromMM


def xy(x, y):
    return p.VECTOR2I(mm(x), mm(y))


def layers(*ids):
    ls = p.LSET()
    for n in ids:
        ls.AddLayer(n)
    return ls


parts = json.loads((P / 'docs/parts.json').read_text(encoding='utf-8'))
root = ET.parse(P / 'verification/P04.xml').getroot()
W, H = 160, 120; HOLES = [(5, 5), (W - 5, 5), (5, H - 5), (W - 5, H - 5)]
b = p.BOARD(); b.SetFileName(str(E / 'P04.kicad_pcb')); b.SetCopperLayerCount(2)
s = b.GetDesignSettings(); s.SetBoardThickness(mm(1.6)); s.m_MinClearance = mm(.25); s.m_TrackMinWidth = mm(.3)
s.m_CopperEdgeClearance = mm(.5); s.m_HoleToHoleMin = mm(.3); s.m_HoleClearance = mm(.25)
s.m_ViasMinSize = mm(.8); s.m_MinThroughDrill = mm(.4); s.m_ViasMinAnnularWidth = mm(.2)
s.m_SilkClearance = mm(.15); s.m_MinSilkTextHeight = mm(.8); s.m_MinSilkTextThickness = mm(.12)
s.m_SolderMaskMinWidth = mm(.1); s.m_MinResolvedSpokes = 2
pin = {}
for n in root.findall('./nets/net'):
    v = p.NETINFO_ITEM(b, n.get('name'), int(n.get('code'))); b.Add(v)
    for q in n.findall('node'):
        pin[q.get('ref'), q.get('pin')] = v
pos = {k: tuple(v) for k, v in json.loads((P / 'src/placement.json').read_text()).items()}
fmap = {}
schroot = re.search(r'\(uuid "?([0-9a-f-]+)', (E / 'P04.kicad_sch').read_text()).group(1)
for c in root.findall('./components/comp'):
    ref = c.get('ref')
    if not parts[ref].get('on_board', True):
        continue
    lib, name = c.findtext('footprint').split(':')
    f = p.FootprintLoad(str(E / 'libraries' / (lib + '.pretty')), name); assert f, ref
    f.SetReference(ref); f.SetValue(c.findtext('value')); f.SetFPIDAsString(c.findtext('footprint'))
    path = '/' + schroot + c.find('sheetpath').get('tstamps') + c.findtext('tstamps').split()[0]
    f.SetPath(p.KIID_PATH(path))
    f.GetField(p.FIELD_T_DATASHEET).SetText(c.findtext('datasheet') or '')
    for field in c.findall('./fields/field'):
        if field.get('name') in ['MPN', 'BaselineRef']:
            ff = p.PCB_FIELD(f, p.FIELD_T_USER, field.get('name')); ff.SetText(field.text or ''); ff.SetVisible(False); f.Add(ff)
    for pad in f.Pads():
        if pad.GetNumber():
            pad.SetNet(pin[ref, pad.GetNumber()])
    b.Add(f); fmap[ref] = f
missing = sorted(set(fmap) - set(pos)); assert not missing, missing
for ref, f in fmap.items():
    x, y, ang = pos[ref][:3]
    f.SetPosition(xy(x, y)); f.SetOrientationDegrees(ang)
    if len(pos[ref]) > 3 and pos[ref][3] == 'B':
        f.Flip(f.GetPosition(), False)
    f.Value().SetVisible(False); f.Reference().SetTextSize(xy(1, 1)); f.Reference().SetTextThickness(mm(.15))
    f.Reference().SetTextAngle(p.EDA_ANGLE(0, p.DEGREES_T))
    bb = f.GetLayerBoundingBox(layers(p.F_CrtYd))
    if bb.GetWidth():
        f.Reference().SetPosition(xy((p.ToMM(bb.GetLeft()) + p.ToMM(bb.GetRight())) / 2, p.ToMM(bb.GetTop()) - 1.1))
for i, (x, y) in enumerate(HOLES, 1):
    f = p.FOOTPRINT(b); f.SetReference('H' + str(i)); f.SetValue('M3 NPTH')
    f.SetAttributes(p.FP_BOARD_ONLY | p.FP_EXCLUDE_FROM_BOM | p.FP_EXCLUDE_FROM_POS_FILES)
    pad = p.PAD(f); pad.SetAttribute(p.PAD_ATTRIB_NPTH); pad.SetShape(p.PAD_SHAPE_CIRCLE); pad.SetSize(xy(3.2, 3.2))
    pad.SetDrillSize(xy(3.2, 3.2)); pad.SetLayerSet(p.LSET.AllCuMask()); f.Add(pad)
    f.SetPosition(xy(x, y)); f.Reference().SetVisible(False); f.Value().SetVisible(False); f.SetAllowMissingCourtyard(True); b.Add(f)
    z = p.ZONE(b); z.SetIsRuleArea(True); z.SetLayerSet(layers(p.F_Cu, p.B_Cu)); z.SetDoNotAllowTracks(True)
    z.SetDoNotAllowVias(True); z.SetDoNotAllowZoneFills(True); z.SetDoNotAllowPads(False); z.SetDoNotAllowFootprints(False)
    z.SetZoneName(f'M3 H{i}')
    o = z.Outline(); o.NewOutline()
    for k in range(48):
        o.Append(mm(x + 4 * math.cos(k * math.tau / 48)), mm(y + 4 * math.sin(k * math.tau / 48)))
    b.Add(z)
for ref in ['J1','J2']:
    holes=[a.GetPosition() for a in fmap[ref].Pads() if not a.GetNumber()]
    xs=[p.ToMM(q.x) for q in holes];ys=[p.ToMM(q.y) for q in holes]
    z=p.ZONE(b);z.SetIsRuleArea(True);z.SetLayerSet(layers(p.F_Cu,p.B_Cu))
    z.SetDoNotAllowTracks(True);z.SetDoNotAllowVias(True);z.SetDoNotAllowZoneFills(True)
    z.SetDoNotAllowPads(False);z.SetDoNotAllowFootprints(False);z.SetZoneName('TIE '+ref)
    o=z.Outline();o.NewOutline()
    for x,y in [(min(xs)-2,min(ys)-2),(max(xs)+2,min(ys)-2),(max(xs)+2,max(ys)+2),(min(xs)-2,max(ys)+2)]:o.Append(mm(x),mm(y))
    b.Add(z)
# R2: band under the GND row of the SAFE/CORE harness J2 (pads 2, 6..16) where tracks and vias are not allowed but
# the GND pour is: every harness GND pad keeps its thermal spokes into the main pour on both layers. In R1 this
# depended on the router (a PWM track wrapped around J2 can leave J2.2 on an isolated fill island).
gp = [a.GetPosition() for a in fmap['J2'].Pads() if a.GetNumber() and int(a.GetNumber()) % 2 == 0]
gx = [p.ToMM(q.x) for q in gp]; gy = max(p.ToMM(q.y) for q in gp)
z = p.ZONE(b); z.SetIsRuleArea(True); z.SetLayerSet(layers(p.F_Cu, p.B_Cu)); z.SetDoNotAllowTracks(True); z.SetDoNotAllowVias(True)
z.SetDoNotAllowZoneFills(False); z.SetDoNotAllowPads(False); z.SetDoNotAllowFootprints(False); z.SetZoneName('GND ROW J2')
o = z.Outline(); o.NewOutline()
for x, y in [(min(gx) - 2.4, gy + 1.25), (max(gx) + 2.4, gy + 1.25), (max(gx) + 2.4, gy + 3.75), (min(gx) - 2.4, gy + 3.75)]:
    o.Append(mm(x), mm(y))
b.Add(z)
for a, c in [((0, 0), (W, 0)), ((W, 0), (W, H)), ((W, H), (0, H)), ((0, H), (0, 0))]:
    line = p.PCB_SHAPE(); line.SetShape(p.SHAPE_T_SEGMENT); line.SetStart(xy(*a)); line.SetEnd(xy(*c)); line.SetWidth(mm(.05)); line.SetLayer(p.Edge_Cuts); b.Add(line)


def txt(t, x, y, size=1, layer=p.F_SilkS):
    a = p.PCB_TEXT(b); a.SetText(t); a.SetPosition(xy(x, y)); a.SetTextSize(xy(size, size)); a.SetTextThickness(mm(.15)); a.SetLayer(layer); b.Add(a)


tb = p.TITLE_BLOCK(); tb.SetTitle('EGRLab P04 SAFE / PCB R2.2'); tb.SetRevision('PCB-R2.2 / SCH-P04-R2.2'); tb.SetDate('2026-09-28')
tb.SetComment(0, 'Review / physical fit and bench acceptance pending'); tb.SetComment(1, 'R2.2: R17 10k; same copper and pinout as R2.1')
b.SetTitleBlock(tb)
b.BuildConnectivity(); p.SaveBoard(str(E / 'P04.kicad_pcb'), b)
print('Created P04 board:', len(fmap), 'footprints + 4 M3 holes')
