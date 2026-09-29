"""PCB R2: native KiCad PCB from frozen R3 XML with the R2 placement.
Run with KiCad's Python (pcbnew). Never modifies the R3 package.

Changes against build_board.py (R1), see docs/ZMIANY-R2.md:
- placement from src/placement_r2.json (functional blocks; PCB1-03/04/05/06),
- F.Cu rule area under the metal envelope of HS1/HS2, bay left open (PCB1-01),
- TO-220 footprint keeps a silkscreen body outline with a thick tab-side line (PCB1-02),
- R2 titles.
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


root = ET.parse(P / 'reference/R3-P01.xml').getroot()
b = p.BOARD(); b.SetFileName(str(E / 'P01.kicad_pcb')); b.SetCopperLayerCount(2)
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
pos = {k: tuple(v) for k, v in json.loads((P / 'src/placement_r2.json').read_text()).items()}
fmap = {}
schroot = re.search(r'\(uuid "?([0-9a-f-]+)', (E / 'P01.kicad_sch').read_text()).group(1)
for c in root.findall('./components/comp'):
    ref = c.get('ref'); lib, name = c.findtext('footprint').split(':')
    f = p.FootprintLoad(str(E / 'libraries' / (lib + '.pretty')), name); assert f, ref
    f.SetReference(ref); f.SetValue(c.findtext('value')); f.SetFPIDAsString(c.findtext('footprint'))
    path = '/' + schroot + c.find('sheetpath').get('tstamps') + c.findtext('tstamps').split()[0]
    f.SetPath(p.KIID_PATH(path))
    f.GetField(p.FIELD_T_DATASHEET).SetText(c.findtext('datasheet') or '')
    for field in c.findall('./fields/field'):
        name2 = field.get('name')
        if name2 in ['MPN', 'BaselineRef']:
            ff = p.PCB_FIELD(f, p.FIELD_T_USER, name2); ff.SetText(field.text or ''); ff.SetVisible(False); f.Add(ff)
    for pad in f.Pads():
        if pad.GetNumber():
            pad.SetNet(pin[ref, pad.GetNumber()])
    b.Add(f); fmap[ref] = f
for ref in ['HS1', 'HS2']:
    f = p.FootprintLoad(str(E / 'libraries/P01.pretty'), 'HS_Fischer_SK129_63.5_STS_D2.8')
    f.SetReference(ref); f.SetValue('SK129-63STS'); f.SetFPIDAsString('P01:HS_Fischer_SK129_63.5_STS_D2.8')
    f.SetAttributes(p.FP_THROUGH_HOLE | p.FP_BOARD_ONLY | p.FP_EXCLUDE_FROM_POS_FILES)
    b.Add(f); fmap[ref] = f
for ref, f in fmap.items():
    x, y, ang = pos[ref]; f.SetPosition(xy(x, y)); f.SetOrientationDegrees(ang)
    f.Value().SetVisible(False); f.Reference().SetTextSize(xy(1, 1)); f.Reference().SetTextThickness(mm(.15))
    f.Reference().SetTextAngle(p.EDA_ANGLE(0, p.DEGREES_T))
    bb = f.GetLayerBoundingBox(layers(p.F_CrtYd))
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
# PCB1-01: no F.Cu under the heatsink metal. The rule area follows the profile
# envelope (SK129 cross-section, courtyard +-21.3 x +-12.8 mm) grown by 0.5 mm,
# with the TO-220 bay (|x| < 8.0 mm, y > +1.5 mm from the plate axis) left open.
# B.Cu stays usable: the laminate insulates it from the profile.
HS_KEEP = [(-21.8, -13.3), (21.8, -13.3), (21.8, 13.3), (8.0, 13.3), (8.0, 1.5), (-8.0, 1.5), (-8.0, 13.3), (-21.8, 13.3)]
for ref in ['HS1', 'HS2']:
    hx, hy, _ = pos[ref]
    z = p.ZONE(b); z.SetIsRuleArea(True); z.SetLayerSet(layers(p.F_Cu)); z.SetDoNotAllowTracks(True)
    z.SetDoNotAllowVias(True); z.SetDoNotAllowZoneFills(True); z.SetDoNotAllowPads(False); z.SetDoNotAllowFootprints(False)
    z.SetZoneName(f'{ref} F.Cu keepout')
    o = z.Outline(); o.NewOutline()
    for dx, dy in HS_KEEP:
        o.Append(mm(hx + dx), mm(hy + dy))
    b.Add(z)
for a, c in [((0, 0), (160, 0)), ((160, 0), (160, 120)), ((160, 120), (0, 120)), ((0, 120), (0, 0))]:
    line = p.PCB_SHAPE(); line.SetShape(p.SHAPE_T_SEGMENT); line.SetStart(xy(*a)); line.SetEnd(xy(*c)); line.SetWidth(mm(.05)); line.SetLayer(p.Edge_Cuts); b.Add(line)


def txt(t, x, y, size=1, layer=p.F_SilkS):
    a = p.PCB_TEXT(b); a.SetText(t); a.SetPosition(xy(x, y)); a.SetTextSize(xy(size, size)); a.SetTextThickness(mm(.15)); a.SetLayer(layer); b.Add(a)


txt('EGRLab P01 / PCB R2', 81, 5, 1.1)
txt('Cu 70um / 2L / 1.6mm', 79, 117, 1, p.Dwgs_User)
tb = p.TITLE_BLOCK(); tb.SetTitle('EGRLab P01 PROTECT / PCB R2'); tb.SetRevision('PCB-R2 / SCH-R3'); tb.SetDate('2026-09-24')
tb.SetComment(0, 'Review / physical fit and bench acceptance pending'); tb.SetComment(1, 'R2: fixes PCB1-01..06 of the PCB R1 review')
b.SetTitleBlock(tb)
b.BuildConnectivity(); p.SaveBoard(str(E / 'P01.kicad_pcb'), b)
summary = []
for ref, f in fmap.items():
    bb = f.GetLayerBoundingBox(layers(p.F_CrtYd))
    summary.append({'ref': ref, 'x': p.ToMM(f.GetPosition().x), 'y': p.ToMM(f.GetPosition().y), 'deg': f.GetOrientationDegrees(),
                    'courtyard': [p.ToMM(bb.GetLeft()), p.ToMM(bb.GetTop()), p.ToMM(bb.GetRight()), p.ToMM(bb.GetBottom())],
                    'pads': [{'n': pad.GetNumber(), 'xy': [p.ToMM(pad.GetPosition().x), p.ToMM(pad.GetPosition().y)], 'net': pad.GetNetname()} for pad in f.Pads()]})
(P / 'verification/placement.json').write_text(json.dumps(summary, indent=2))
print('Created R2 board', len(fmap), 'electrical/mechanical footprints, 4 M3 holes, 2 heatsink F.Cu keepouts.')
