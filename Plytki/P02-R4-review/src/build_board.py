"""P02 R4 PCB (format S1, class L, slots S1-S3 of level 1) from the exported netlist (verification/P02.xml) and src/placement.json.
Adapted from the P02 R3 builder. Outline, M3 holes and standoff zones come from Plytki/Format-S1/format-s1.json (S1-1);
board coordinates: x along the long side (0 = panel side of the board, 160 = input wall), y across (0 = edge A, 100 = edge B).
Rules as P02 R3 (clearance 0.25, track 0.3, 1.6 mm), copper 35 um, annular ring >= 0.25 mm for PTH and vias (S1 section 3).
Parts on the bottom (S1-2): only SMD marked 'B' in placement.json (U9 SOIC and its capacitors).
"""
from pathlib import Path
import pcbnew as p, json, re, math, xml.etree.ElementTree as ET
P = Path(__file__).resolve().parents[1]; E = P / 'eda'
S1 = json.loads((P.parents[0] / 'Format-S1/format-s1.json').read_text(encoding='utf-8'))
mm = p.FromMM
CLASS, SLOTS = 'L', ['S1', 'S2', 'S3']
W, Hh = S1['klasy'][CLASS]['W'], S1['klasy'][CLASS]['H']; R = S1['obrys']['promien_naroza']


def xy(x, y):
    return p.VECTOR2I(mm(x), mm(y))


def layers(*ids):
    ls = p.LSET()
    for n in ids:
        ls.AddLayer(n)
    return ls


def holes():
    """M3 centres in board coordinates: x_w_slocie + 53.5 x (slot index on the board), y from the JSON."""
    return [(x + S1['rozstaw_slotow'] * k, y) for k in range(len(SLOTS)) for x in S1['otwory_M3']['x_w_slocie'] for y in S1['otwory_M3']['y']]


if __name__ == '__main__':
    parts = json.loads((P / 'docs/parts.json').read_text(encoding='utf-8'))
    root = ET.parse(P / 'verification/P02.xml').getroot()
    b = p.BOARD(); b.SetFileName(str(E / 'P02.kicad_pcb')); b.SetCopperLayerCount(2)
    s = b.GetDesignSettings(); s.SetBoardThickness(mm(S1['obrys']['grubosc_pcb'])); s.m_MinClearance = mm(.25); s.m_TrackMinWidth = mm(.3)
    s.m_CopperEdgeClearance = mm(S1['obrys']['odstep_miedzi_od_krawedzi']); s.m_HoleToHoleMin = mm(.3); s.m_HoleClearance = mm(.25)
    s.m_ViasMinSize = mm(.9); s.m_MinThroughDrill = mm(.4); s.m_ViasMinAnnularWidth = mm(.25)
    s.m_SilkClearance = mm(.15); s.m_MinSilkTextHeight = mm(.8); s.m_MinSilkTextThickness = mm(.12)
    s.m_SolderMaskMinWidth = mm(.1); s.m_MinResolvedSpokes = 2
    pin = {}
    for n in root.findall('./nets/net'):
        v = p.NETINFO_ITEM(b, n.get('name'), int(n.get('code'))); b.Add(v)
        for q in n.findall('node'):
            pin[q.get('ref'), q.get('pin')] = v
    pos = {k: tuple(v) for k, v in json.loads((P / 'src/placement.json').read_text()).items() if not k.startswith('_')}
    fmap = {}
    schroot = re.search(r'\(uuid "?([0-9a-f-]+)', (E / 'P02.kicad_sch').read_text()).group(1)
    for c in root.findall('./components/comp'):
        ref = c.get('ref')
        if not parts[ref].get('on_board', True):
            continue
        lib, name = c.findtext('footprint').split(':')
        f = p.FootprintLoad(str(E / 'libraries' / (lib + '.pretty')), name); assert f, ref
        f.SetReference(ref); f.SetValue(c.findtext('value')); f.SetFPIDAsString(c.findtext('footprint'))
        f.SetPath(p.KIID_PATH('/' + schroot + c.find('sheetpath').get('tstamps') + c.findtext('tstamps').split()[0]))
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
        if len(pos[ref]) > 3 and pos[ref][3] == 'B':   # S1-2: SMD on the bottom (mirrored top/bottom about its own position)
            f.Flip(f.GetPosition(), p.FLIP_DIRECTION_TOP_BOTTOM if hasattr(p, 'FLIP_DIRECTION_TOP_BOTTOM') else False)
        f.Value().SetVisible(False); f.Reference().SetTextSize(xy(1, 1)); f.Reference().SetTextThickness(mm(.15))
        f.Reference().SetTextAngle(p.EDA_ANGLE(0, p.DEGREES_T))
        bb = f.GetLayerBoundingBox(layers(p.B_CrtYd if f.IsFlipped() else p.F_CrtYd))
        if bb.GetWidth():
            f.Reference().SetPosition(xy((p.ToMM(bb.GetLeft()) + p.ToMM(bb.GetRight())) / 2, p.ToMM(bb.GetTop()) - 1.1))
    rz = S1['otwory_M3']['strefa_dystansu_srednica'] / 2; dh = S1['otwory_M3']['srednica']
    for i, (x, y) in enumerate(holes(), 1):
        f = p.FOOTPRINT(b); f.SetReference('H' + str(i)); f.SetValue('M3 NPTH')
        f.SetAttributes(p.FP_BOARD_ONLY | p.FP_EXCLUDE_FROM_BOM | p.FP_EXCLUDE_FROM_POS_FILES)
        pad = p.PAD(f); pad.SetAttribute(p.PAD_ATTRIB_NPTH); pad.SetShape(p.PAD_SHAPE_CIRCLE); pad.SetSize(xy(dh, dh))
        pad.SetDrillSize(xy(dh, dh)); pad.SetLayerSet(p.LSET.AllCuMask()); f.Add(pad)
        f.SetPosition(xy(x, y)); f.Reference().SetVisible(False); f.Value().SetVisible(False); f.SetAllowMissingCourtyard(True); b.Add(f)
        z = p.ZONE(b); z.SetIsRuleArea(True); z.SetLayerSet(layers(p.F_Cu, p.B_Cu)); z.SetDoNotAllowTracks(True)
        z.SetDoNotAllowVias(True); z.SetDoNotAllowZoneFills(True); z.SetDoNotAllowPads(False); z.SetDoNotAllowFootprints(True)
        z.SetZoneName(f'M3 H{i} standoff D7')
        o = z.Outline(); o.NewOutline()
        for k in range(48):
            o.Append(mm(x + rz * math.cos(k * math.tau / 48)), mm(y + rz * math.sin(k * math.tau / 48)))
        b.Add(z)
    # outline with R1 corners
    segs = [((R, 0), (W - R, 0)), ((W, R), (W, Hh - R)), ((W - R, Hh), (R, Hh)), ((0, Hh - R), (0, R))]
    for a, c in segs:
        g = p.PCB_SHAPE(); g.SetShape(p.SHAPE_T_SEGMENT); g.SetStart(xy(*a)); g.SetEnd(xy(*c)); g.SetWidth(mm(.05)); g.SetLayer(p.Edge_Cuts); b.Add(g)
    for cx, cy, a0 in [(R, R, 180), (W - R, R, 270), (W - R, Hh - R, 0), (R, Hh - R, 90)]:
        g = p.PCB_SHAPE(); g.SetShape(p.SHAPE_T_ARC); g.SetCenter(xy(cx, cy))
        g.SetStart(xy(cx + R * math.cos(math.radians(a0)), cy + R * math.sin(math.radians(a0))))
        g.SetArcAngleAndEnd(p.EDA_ANGLE(90, p.DEGREES_T), True); g.SetWidth(mm(.05)); g.SetLayer(p.Edge_Cuts); b.Add(g)
    tb = p.TITLE_BLOCK(); tb.SetTitle('EGRLab P02 R4 / format S1, klasa L (S1-S3)'); tb.SetRevision('P02-R4 etap 2'); tb.SetDate('2026-09-29')
    tb.SetComment(0, 'Pilot formatu S1; recenzja lokalna i przymiarka 1:1 przed zamowieniem'); b.SetTitleBlock(tb)
    b.BuildConnectivity(); p.SaveBoard(str(E / 'P02.kicad_pcb'), b)
    print('Created P02 R4 board:', len(fmap), 'footprints +', len(holes()), 'M3 holes; outline', W, 'x', Hh)
