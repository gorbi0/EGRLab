"""P02 R2 PCB from the exported schematic netlist (verification/P02.xml) and src/placement.json.
Adapted from the P01 PCB-R2 builder: same outline 160 x 120 mm, same M3 holes and keepouts, 2 x 70 um.
Parts with on_board=False in docs/parts.json (R17 = R_CHARGE, off-board) are not placed.
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
root = ET.parse(P / 'verification/P02.xml').getroot()
b = p.BOARD(); b.SetFileName(str(E / 'P02.kicad_pcb')); b.SetCopperLayerCount(2)
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
schroot = re.search(r'\(uuid "?([0-9a-f-]+)', (E / 'P02.kicad_sch').read_text()).group(1)
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
    for m in list(f.Models()):
        pass
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
for i, (x, y) in enumerate([(5, 5), (155, 5), (5, 115), (155, 115)], 1):
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
for a, c in [((0, 0), (160, 0)), ((160, 0), (160, 120)), ((160, 120), (0, 120)), ((0, 120), (0, 0))]:
    line = p.PCB_SHAPE(); line.SetShape(p.SHAPE_T_SEGMENT); line.SetStart(xy(*a)); line.SetEnd(xy(*c)); line.SetWidth(mm(.05)); line.SetLayer(p.Edge_Cuts); b.Add(line)


def txt(t, x, y, size=1, layer=p.F_SilkS):
    a = p.PCB_TEXT(b); a.SetText(t); a.SetPosition(xy(x, y)); a.SetTextSize(xy(size, size)); a.SetTextThickness(mm(.15)); a.SetLayer(layer); b.Add(a)


txt('EGRLab P02 PSU+HOLD / PCB R2', 104, 117, 1.1)
tb = p.TITLE_BLOCK(); tb.SetTitle('EGRLab P02 PSU + HOLD / PCB R3'); tb.SetRevision('PCB-R3 / SCH-P02-R3'); tb.SetDate('2026-09-26')
tb.SetComment(0, 'Review / physical fit and bench acceptance pending'); tb.SetComment(1, 'Schematic + PCB R2 in one package (Claude); review: Astra')
b.SetTitleBlock(tb)
b.BuildConnectivity(); p.SaveBoard(str(E / 'P02.kicad_pcb'), b)
print('Created P02 board:', len(fmap), 'footprints + 4 M3 holes')
