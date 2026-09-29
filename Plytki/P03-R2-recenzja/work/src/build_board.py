"""P03 R2 PCB from the exported schematic netlist (verification/P03.xml) and src/placement.json.
Taken over from the P00/P02 R1 builders: outline 160 x 120 mm with the four P01/P02 corner holes, plus
H5 next to the DAQ socket (v6.1 10-montaz-wiazek: two fixing points of each PCB close to the B2B contact;
with H2 the pair brackets J1). 2 x 35 um copper (see set_stackup.py).
Rule areas (both copper layers, no tracks / vias / pour):
- M3 H1..H5: 4 mm radius, as P01/P02;
- ANTENNA: the Waveshare PCB antenna end of M1 plus 3 mm at the sides and 8 mm beyond the module end;
- SD1 M2.5: 3 mm radius around both mounting holes of the Adafruit 4682 (stand-off and nut);
- LV03 TIE: the band between the two anchor holes of J10 (v6.1: no copper under the cable tie).
"""
from pathlib import Path
import pcbnew as p, json, re, math, xml.etree.ElementTree as ET
P = Path(__file__).resolve().parents[1]; E = P / 'eda'
mm = p.FromMM
W, H = 160, 120
HOLES = [(5, 5), (W - 5, 5), (5, H - 5), (W - 5, H - 5), (W - 5, 38)]


def xy(x, y):
    return p.VECTOR2I(mm(x), mm(y))


def layers(*ids):
    ls = p.LSET()
    for n in ids:
        ls.AddLayer(n)
    return ls


def fp2board(f, x, y):
    """Footprint-local (x, y) in mm -> board mm (KiCad: orientation counter-clockwise on screen, y down)."""
    a = math.radians(f.GetOrientationDegrees()); c = f.GetPosition()
    return (p.ToMM(c.x) + x * math.cos(a) + y * math.sin(a), p.ToMM(c.y) - x * math.sin(a) + y * math.cos(a))


def keepout(b, name, pts):
    z = p.ZONE(b); z.SetIsRuleArea(True); z.SetLayerSet(layers(p.F_Cu, p.B_Cu)); z.SetDoNotAllowTracks(True)
    z.SetDoNotAllowVias(True); z.SetDoNotAllowZoneFills(True); z.SetDoNotAllowPads(False); z.SetDoNotAllowFootprints(False)
    z.SetZoneName(name)
    o = z.Outline(); o.NewOutline()
    for x, y in pts:
        o.Append(mm(x), mm(y))
    b.Add(z)


def circle(x, y, r, n=48):
    return [(x + r * math.cos(k * math.tau / n), y + r * math.sin(k * math.tau / n)) for k in range(n)]


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


parts = json.loads((P / 'docs/parts.json').read_text(encoding='utf-8'))
root = ET.parse(P / 'verification/P03.xml').getroot()
b = p.BOARD(); b.SetFileName(str(E / 'P03.kicad_pcb')); b.SetCopperLayerCount(2)
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
schroot = re.search(r'\(uuid "?([0-9a-f-]+)', (E / 'P03.kicad_sch').read_text()).group(1)
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
        if field.get('name') in ['MPN', 'BaselineRef', 'SourceRef']:
            ff = p.PCB_FIELD(f, p.FIELD_T_USER, field.get('name')); ff.SetText(field.text or ''); ff.SetVisible(False); f.Add(ff)
    for pad in f.Pads():
        if pad.GetNumber():
            pad.SetNet(pin[ref, pad.GetNumber()])
    b.Add(f); fmap[ref] = f
missing = sorted(set(fmap) - set(pos)); assert not missing, missing
extra = sorted(set(pos) - set(fmap)); assert not extra, extra
for ref, f in fmap.items():
    x, y, ang = pos[ref][:3]
    f.SetPosition(xy(x, y)); f.SetOrientationDegrees(ang)
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
    keepout(b, f'M3 H{i}', circle(x, y, 4))
# antenna end of the Waveshare board (footprint F.Fab 'ANTENNA' rectangle: x -1.32..24.18, y -8.0..-1.5)
m1 = fmap['M1']; ant = [fp2board(m1, x, y) for x, y in [(-1.32 - 3, -1.5), (24.18 + 3, -1.5), (24.18 + 3, -8.0 - 8), (-1.32 - 3, -8.0 - 8)]]
keepout(b, 'ANTENNA M1', rect(min(v[0] for v in ant), min(v[1] for v in ant), max(v[0] for v in ant), max(v[1] for v in ant)))
for k, a in enumerate([a for a in fmap['SD1'].Pads() if a.GetAttribute() == p.PAD_ATTRIB_NPTH], 1):
    keepout(b, f'SD1 M2.5 {k}', circle(p.ToMM(a.GetPosition().x), p.ToMM(a.GetPosition().y), 3))
tie = sorted((p.ToMM(a.GetPosition().x), p.ToMM(a.GetPosition().y)) for a in fmap['J10'].Pads() if a.GetAttribute() == p.PAD_ATTRIB_NPTH)
assert len(tie) == 2 and abs(tie[0][1] - tie[1][1]) < 1e-6
keepout(b, 'LV03 TIE', rect(tie[0][0] - 2.6, tie[0][1] - 2.6, tie[1][0] + 2.6, tie[0][1] + 2.6))
for a, c in [((0, 0), (W, 0)), ((W, 0), (W, H)), ((W, H), (0, H)), ((0, H), (0, 0))]:
    line = p.PCB_SHAPE(); line.SetShape(p.SHAPE_T_SEGMENT); line.SetStart(xy(*a)); line.SetEnd(xy(*c)); line.SetWidth(mm(.05)); line.SetLayer(p.Edge_Cuts); b.Add(line)
tb = p.TITLE_BLOCK(); tb.SetTitle('EGRLab P03 CORE / PCB R2'); tb.SetRevision('PCB-R2 / SCH-P03-R2'); tb.SetDate('2026-09-26')
tb.SetComment(0, 'Review / physical fit and bench acceptance pending'); tb.SetComment(1, 'P03-R2 corrections; independent review required')
b.SetTitleBlock(tb)
b.BuildConnectivity(); p.SaveBoard(str(E / 'P03.kicad_pcb'), b)
print('Created P03 board:', len(fmap), 'footprints +', len(HOLES), 'M3 holes; rule areas:', ', '.join(z.GetZoneName() for z in b.Zones()))
