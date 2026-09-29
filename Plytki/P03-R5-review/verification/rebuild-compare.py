"""Compare release and isolated rebuild without using UUIDs, dates or absolute paths.
Run with KiCad Python; arguments are the two package directories: RELEASE first, REBUILT COPY second.
R3: reports are written into the rebuilt copy (second argument). In R2 they went into the first argument, which
overwrote a file of the release when the release was given first (found in the R3 review).
"""
from pathlib import Path
import pcbnew as p, json, hashlib, sys, xml.etree.ElementTree as ET

def signature(folder):
    folder=Path(folder); b=p.LoadBoard(str(folder/'eda/P03.kicad_pcb'))
    def pos(v): return [v.x,v.y]
    def ordered(items): return sorted(items,key=lambda x:json.dumps(x,sort_keys=True))
    def loop(line):
        pts=[pos(line.CPoint(i)) for i in range(line.PointCount())]
        if len(pts)>1 and pts[0]==pts[-1]:pts.pop()
        if not pts:return []
        def rotate(a):
            i=min(range(len(a)),key=a.__getitem__);return a[i:]+a[:i]
        return min(rotate(pts),rotate(list(reversed(pts))))
    def poly(ps):
        return ordered([loop(ps.Outline(i)),ordered(loop(ps.Hole(i,j)) for j in range(ps.HoleCount(i)))] for i in range(ps.OutlineCount()))
    def txt(t):
        return [t.GetText(),pos(t.GetPosition()),pos(t.GetTextSize()),t.GetTextAngle().AsDegrees(),t.GetTextThickness(),t.GetLayer(),t.IsVisible()]
    footprints=[]
    for f in b.GetFootprints():
        pads=ordered([a.GetNumber(),a.GetNetname(),pos(a.GetPosition()),pos(a.GetSize()),pos(a.GetDrillSize()),a.GetShape(),
                      a.GetOrientationDegrees(),list(a.GetLayerSet().Seq()),a.GetLocalZoneConnection()] for a in f.Pads())
        footprints.append([f.GetReference(),f.GetValue(),f.GetFPIDAsString(),pos(f.GetPosition()),f.GetOrientationDegrees(),f.GetLayer(),pads,txt(f.Reference())])
    tracks=[]
    for t in b.GetTracks():
        if isinstance(t,p.PCB_VIA):tracks.append(['via',t.GetNetname(),pos(t.GetPosition()),t.GetWidth(p.F_Cu),t.GetDrill(),t.IsLocked()])
        else:tracks.append(['track',t.GetNetname(),sorted([pos(t.GetStart()),pos(t.GetEnd())]),t.GetWidth(),t.GetLayer(),t.IsLocked()])
    zones=[]
    for z in b.Zones():
        layers=list(z.GetLayerSet().Seq())
        zones.append([z.GetZoneName(),z.GetNetname(),layers,z.GetIsRuleArea(),poly(z.Outline())])
    drawings=[]
    for g in b.GetDrawings():
        if isinstance(g,p.PCB_TEXT):drawings.append(['text',txt(g)])
        elif isinstance(g,p.PCB_SHAPE):drawings.append(['shape',g.GetShape(),g.GetLayer(),pos(g.GetStart()),pos(g.GetEnd()),g.GetWidth()])
        else:raise ValueError(g.GetClass())
    x=ET.parse(folder/'verification/P03.xml').getroot()
    pinmap=ordered([node.get('ref'),node.get('pin'),n.get('name')] for n in x.findall('./nets/net') for node in n.findall('node'))
    return {'footprints_pads_references':ordered(footprints),'tracks_vias':ordered(tracks),'zone_boundaries':ordered(zones),'drawings':ordered(drawings),
            'pinmap':pinmap,'project_rules':json.loads((folder/'eda/P03.kicad_pro').read_text()),
            'schematic_sheets':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted((folder/'eda').glob('*.kicad_sch'))},
            'local_libraries':{f.relative_to(folder/'eda/libraries').as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted((folder/'eda/libraries').rglob('*')) if f.is_file()}}

if __name__=='__main__':
    a,b=map(Path,sys.argv[1:3]);sa,sb=signature(a),signature(b)
    digest=lambda x:hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    checks=[{'category':k,'same':sa[k]==sb[k],'original_sha256':digest(sa[k]),'rebuilt_sha256':digest(sb[k])} for k in sa]
    # Filled polygons can encode the SAME copper with different traversal of touching
    # boundaries and with collinear vertices inserted/removed. Compare geometric XOR,
    # not vertex ordering. Allow only numerical residue <= 1e-8 mm^2 (100nm x 100nm).
    # This is not a relaxation of electrical DRC or of any route/placement constraint.
    ba=p.LoadBoard(str(a/'eda/P03.kicad_pcb'));bb=p.LoadBoard(str(b/'eda/P03.kicad_pcb'))
    fills=[]
    for L in (p.F_Cu,p.B_Cu):
        ca=next(z.GetFilledPolysList(L) for z in ba.Zones() if not z.GetIsRuleArea() and z.IsOnLayer(L))
        cb=next(z.GetFilledPolysList(L) for z in bb.Zones() if not z.GetIsRuleArea() and z.IsOnLayer(L))
        xor=p.SHAPE_POLY_SET();xor.BooleanXor(ca,cb);area=abs(xor.Area())/1e12
        fills.append({'layer':ba.GetLayerName(L),'xor_mm2':area,'limit_mm2':1e-8,'equivalent':area<=1e-8})
    rep={'method':'Fresh package: src, reference, docs and saved SES only; no eda, generated reports or neighbouring P02. Full run_release.py, no network.',
         'packages':[str(a),str(b)],'checks':checks,'filled_copper':fills,'all_equal':all(x['same'] for x in checks) and all(x['equivalent'] for x in fills)}
    (b/'verification/standalone-rebuild.json').write_text(json.dumps(rep,indent=2)+'\n')
    for r in checks:print('PASS' if r['same'] else 'FAIL',r['category'])
    for r in fills:print('PASS' if r['equivalent'] else 'FAIL','filled copper',r)
    for k in sa:
        if sa[k]!=sb[k]:
            (b/f'verification/rebuild-diff-{k}.json').write_text(json.dumps({'original':sa[k],'rebuilt':sb[k]},indent=2))
    assert rep['all_equal'], 'Isolated rebuild differs: inspect reports'
