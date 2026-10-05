"""P04 R3 PCB (format S1, class L, slots S1-S3 of level 6; builder of P05 R3 / P10 R2) from the exported netlist and src/placement.json. Builder taken over from
P03 R6 via P09 R2 (30.09.2026; outline, M3 holes and standoff zones from Plytki/Format-S1/format-s1.json), board values from board.py.
Rules as P02 R3 / R4 (clearance 0.25, track 0.3), 2 x 35 um copper, annular ring >= 0.25 mm (S1 section 3).
Rule areas on both copper layers: M3 H1..H4 standoff zones D7 (S1 section 4), also no footprints.
"""

from pathlib import Path
import pcbnew as p, json, re, math, xml.etree.ElementTree as ET
P = Path(__file__).resolve().parents[1]; E = P / 'eda'
S1 = json.loads((P.parents[0] / 'Format-S1/format-s1.json').read_text(encoding='utf-8'))
mm = p.FromMM
from board import NAME, REV, TITLE, CLASS, SLOTS, SUPPORT_KEEPOUT, DATE
import board as _board
PAD_KEEPOUT = getattr(_board, 'PAD_KEEPOUT', {})
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


def fp2board(f, x, y):
    """Footprint-local (x, y) in mm -> board mm (KiCad: orientation counter-clockwise on screen, y down)."""
    a = math.radians(f.GetOrientationDegrees()); c = f.GetPosition()
    return (p.ToMM(c.x) + x * math.cos(a) + y * math.sin(a), p.ToMM(c.y) - x * math.sin(a) + y * math.cos(a))


def antenna_rect(f):
    """ANTENNA M1 rule area in board mm (x0, y0, x1, y1): antenna end + 3 mm sides + 8 mm beyond the module end."""
    q = [fp2board(f, x, y) for x, y in [(-1.32 - 3, -1.5), (24.18 + 3, -1.5), (24.18 + 3, -8.0 - 8), (-1.32 - 3, -8.0 - 8)]]
    return (min(a for a, _ in q), min(b for _, b in q), max(a for a, _ in q), max(b for _, b in q))


def fab_circle(b, x, y, r):
    """Board-level F.Fab circle of a keepout (30.09: the fit print said "circles D7 around the M3 holes" but showed only the holes)."""
    g = p.PCB_SHAPE(b); g.SetShape(p.SHAPE_T_CIRCLE); g.SetCenter(xy(x, y)); g.SetEnd(xy(x + r, y)); g.SetLayer(p.F_Fab); g.SetWidth(mm(.1)); b.Add(g)


def rule_area(b, name, pts, footprints=False, warstwy=(p.F_Cu, p.B_Cu)):
    z = p.ZONE(b); z.SetIsRuleArea(True); z.SetLayerSet(layers(*warstwy)); z.SetDoNotAllowTracks(True)
    z.SetDoNotAllowVias(True); z.SetDoNotAllowZoneFills(True); z.SetDoNotAllowPads(False); z.SetDoNotAllowFootprints(footprints)
    z.SetZoneName(name)
    o = z.Outline(); o.NewOutline()
    for x, y in pts:
        o.Append(mm(x), mm(y))
    b.Add(z)


def circle(x, y, r, n=48):
    return [(x + r * math.cos(k * math.tau / n), y + r * math.sin(k * math.tau / n)) for k in range(n)]


if __name__ == '__main__':
    parts = json.loads((P / 'docs/parts.json').read_text(encoding='utf-8'))
    root = ET.parse(P / f'verification/{NAME}.xml').getroot()
    b = p.BOARD(); b.SetFileName(str(E / f'{NAME}.kicad_pcb')); b.SetCopperLayerCount(2)
    s = b.GetDesignSettings(); s.SetBoardThickness(mm(S1['obrys']['grubosc_pcb'])); s.m_MinClearance = mm(.25); s.m_TrackMinWidth = mm(.2)
    s.m_CopperEdgeClearance = mm(S1['obrys']['odstep_miedzi_od_krawedzi']); s.m_HoleToHoleMin = mm(.3); s.m_HoleClearance = mm(.25)
    s.m_ViasMinSize = mm(.9); s.m_MinThroughDrill = mm(.4); s.m_ViasMinAnnularWidth = mm(.25)
    s.m_SilkClearance = mm(.15); s.m_MinSilkTextHeight = mm(.8); s.m_MinSilkTextThickness = mm(.12)
    s.m_SolderMaskMinWidth = mm(.1); s.m_MinResolvedSpokes = 2
    pin = {}
    for n in root.findall('./nets/net'):
        nm = n.get('name')
        if nm.startswith('unconnected-('):   # P05 R3: a pin name with '/' (U2 'Trim/NR') is '{slash}' in the schematic (DRC parity)
            nm = nm.replace('/', '{slash}')
        v = p.NETINFO_ITEM(b, nm, int(n.get('code'))); b.Add(v)
        for q in n.findall('node'):
            pin[q.get('ref'), q.get('pin')] = v
    pos = {k: tuple(v) for k, v in json.loads((P / 'src/placement.json').read_text()).items() if not k.startswith('_')}
    fmap = {}
    schroot = re.search(r'\(uuid "?([0-9a-f-]+)', (E / f'{NAME}.kicad_sch').read_text()).group(1)
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
        rule_area(b, f'M3 H{i} standoff D7', circle(x, y, rz), footprints=True); fab_circle(b, x, y, rz)
    if 'M1' in fmap:   # P03 only
        x0, y0, x1, y1 = antenna_rect(fmap['M1'])
        rule_area(b, 'ANTENNA M1', [(x0, y0), (x1, y0), (x1, y1), (x0, y1)])
    for k, a in enumerate(sorted((a for a in (fmap['SD1'].Pads() if 'SD1' in fmap else []) if a.GetAttribute() == p.PAD_ATTRIB_NPTH), key=lambda a: a.GetPosition().x), 1):
        rule_area(b, f'SD1 M2.5 {k}', circle(p.ToMM(a.GetPosition().x), p.ToMM(a.GetPosition().y), 3))
    for ref, rk in SUPPORT_KEEPOUT.items():   # NPTH holes of board.SUPPORT_KEEPOUT parts (P10: J3 cable-tie anchor), as P03 R6 SD1 M2.5
        for k, a in enumerate(sorted((a for a in fmap[ref].Pads() if a.GetAttribute() == p.PAD_ATTRIB_NPTH), key=lambda a: a.GetPosition().y), 1):
            rule_area(b, f'{ref} support {k}', circle(p.ToMM(a.GetPosition().x), p.ToMM(a.GetPosition().y), rk))
            fab_circle(b, p.ToMM(a.GetPosition().x), p.ToMM(a.GetPosition().y), rk)
    for ref, d in PAD_KEEPOUT.items():   # P10 (1.10): ring of width d around a vertical pair of soldered-wire pads, no copper of any
        # net in it; only a channel of SIGNAL_W + 2 x 0.25 mm towards -x per pad, where the locked line of that pad leaves for D1
        from board import SIGNAL_W
        pp = sorted((a for a in fmap[ref].Pads() if a.GetNumber()), key=lambda a: a.GetPosition().y)
        assert len(pp) == 2 and pp[0].GetPosition().x == pp[1].GetPosition().x, ref
        x = p.ToMM(pp[0].GetPosition().x); h = max(p.ToMM(pp[0].GetSize().x), p.ToMM(pp[0].GetSize().y)) / 2
        y1, y2 = p.ToMM(pp[0].GetPosition().y), p.ToMM(pp[1].GetPosition().y); cw = SIGNAL_W / 2 + .25
        xl, xp, xr = x - h - d, x - h, x + h
        obie = (p.F_Cu, p.B_Cu)   # kanały tylko na F.Cu (tam idą linie do D1); na B.Cu pełny pierścień (1.10: wylewka GND weszła w kanał od spodu)
        prost = [((xl, y1 - h - d, xr + d, y1 - h), obie), ((xr, y1 - h, xr + d, y2 + h), obie), ((xl, y1 + h, xr, y2 - h), obie),
                 ((xl, y2 + h, xr + d, y2 + h + d), obie), ((xl, y1 - h, xp, y1 - cw), (p.F_Cu,)), ((xl, y1 + cw, xp, y1 + h), (p.F_Cu,)),
                 ((xl, y2 - h, xp, y2 - cw), (p.F_Cu,)), ((xl, y2 + cw, xp, y2 + h), (p.F_Cu,)), ((xl, y1 - h, xp, y1 + h), (p.B_Cu,)),
                 ((xl, y2 - h, xp, y2 + h), (p.B_Cu,))]
        for k, ((a0, b0, a1, b1), ww) in enumerate(prost, 1):
            rule_area(b, f'{ref} pola {d} mm {k}', [(a0, b0), (a1, b0), (a1, b1), (a0, b1)], warstwy=ww)
    # outline with R1 corners
    segs = [((R, 0), (W - R, 0)), ((W, R), (W, Hh - R)), ((W - R, Hh), (R, Hh)), ((0, Hh - R), (0, R))]
    for a, c in segs:
        g = p.PCB_SHAPE(); g.SetShape(p.SHAPE_T_SEGMENT); g.SetStart(xy(*a)); g.SetEnd(xy(*c)); g.SetWidth(mm(.05)); g.SetLayer(p.Edge_Cuts); b.Add(g)
    for cx, cy, a0 in [(R, R, 180), (W - R, R, 270), (W - R, Hh - R, 0), (R, Hh - R, 90)]:
        g = p.PCB_SHAPE(); g.SetShape(p.SHAPE_T_ARC); g.SetCenter(xy(cx, cy))
        g.SetStart(xy(cx + R * math.cos(math.radians(a0)), cy + R * math.sin(math.radians(a0))))
        g.SetArcAngleAndEnd(p.EDA_ANGLE(90, p.DEGREES_T), True); g.SetWidth(mm(.05)); g.SetLayer(p.Edge_Cuts); b.Add(g)
    tb = p.TITLE_BLOCK(); tb.SetTitle(TITLE); tb.SetRevision(REV.replace(' ', '-') + ' PCB'); tb.SetDate(DATE)
    tb.SetComment(0, 'Layout lokalny; recenzja i przymiarka 1:1 przed zamowieniem'); b.SetTitleBlock(tb)
    b.BuildConnectivity(); p.SaveBoard(str(E / f'{NAME}.kicad_pcb'), b)
    print(f'Created {NAME} board:', len(fmap), 'footprints +', len(holes()), 'M3 holes; outline', W, 'x', Hh, '; rule areas:',
          ', '.join(z.GetZoneName() for z in b.Zones() if not z.GetZoneName().startswith('M3')))
