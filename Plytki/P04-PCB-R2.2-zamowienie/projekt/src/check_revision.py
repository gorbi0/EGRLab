"""Check an explicitly limited assembly revision against frozen previous CAD.
No generation code is imported. Copper, drills, pad geometry and fills must match.
"""
from pathlib import Path
import json, hashlib, pcbnew as p
P=Path(__file__).resolve().parents[1]
ID='P03' if P.name.startswith('P03') else 'P04'
base=P/'reference/previous-release'
old=json.loads((base/'parts.json').read_text(encoding='utf-8'))
new=json.loads((P/'docs/parts.json').read_text(encoding='utf-8'))
def check(name,ok,detail=None):return {'check':name,'pass':bool(ok),'detail':detail}
changes={r:{k:[old[r].get(k),new[r].get(k)] for k in old[r].keys()|new[r].keys() if old[r].get(k)!=new[r].get(k)} for r in old.keys()&new.keys()}
changes={r:v for r,v in changes.items() if v}
allowed={'U4':{'value','display','mpn','url','note'},'R41':{'note'}} if ID=='P03' else {'R17':{'value','display','mpn'}}
expected_ref='U4' if ID=='P03' else 'R17'
expected_mpn='SN74LVC1G37DBVR' if ID=='P03' else 'MFR-25FRF52-10K'
checks=[check('No components added or removed',set(old)==set(new)),
        check('Only authorized BOM fields changed',all(r in allowed and set(c)<=allowed[r] for r,c in changes.items()) and expected_ref in changes,changes),
        check('Exact reviewed replacement MPN',new[expected_ref]['mpn']==expected_mpn),
        check('All component pin maps identical',all(old[r]['pins']==new[r]['pins'] for r in old if r in new))]
def xy(v):return (v.x,v.y)
def ordered(xs):return sorted(xs,key=lambda x:json.dumps(x,sort_keys=True))
def txt(t):return (t.GetText(),xy(t.GetPosition()),xy(t.GetTextSize()),t.GetTextAngle().AsDegrees(),t.GetTextThickness(),t.GetLayer(),t.IsVisible())
def signature(b):
    fp={f.GetReference():(f.GetFPIDAsString(),xy(f.GetPosition()),f.GetOrientationDegrees(),f.GetLayer(),
       ordered((a.GetNumber(),a.GetNetname(),xy(a.GetPosition()),xy(a.GetSize()),xy(a.GetDrillSize()),a.GetShape(),a.GetOrientationDegrees(),
                tuple(a.GetLayerSet().Seq()),a.GetLocalZoneConnection()) for a in f.Pads()),txt(f.Reference())) for f in b.GetFootprints()}
    values={f.GetReference():f.GetValue() for f in b.GetFootprints()}
    copper=ordered(('via',t.GetNetname(),xy(t.GetPosition()),t.GetWidth(p.F_Cu),t.GetDrill(),t.IsLocked()) if isinstance(t,p.PCB_VIA)
                   else ('track',t.GetNetname(),sorted([xy(t.GetStart()),xy(t.GetEnd())]),t.GetWidth(),t.GetLayer(),t.IsLocked()) for t in b.GetTracks())
    def poly(ps):return [[xy(ps.Outline(i).CPoint(j)) for j in range(ps.Outline(i).PointCount())] for i in range(ps.OutlineCount())]
    zones=ordered((z.GetNetname(),z.GetZoneName(),z.GetIsRuleArea(),tuple(z.GetLayerSet().Seq()),poly(z.Outline()),z.GetThermalReliefGap(),z.GetThermalReliefSpokeWidth()) for z in b.Zones())
    drawings=ordered(('text',txt(g)) if isinstance(g,p.PCB_TEXT) else ('shape',g.GetShape(),g.GetLayer(),xy(g.GetStart()),xy(g.GetEnd()),g.GetWidth()) for g in b.GetDrawings())
    return fp,values,copper,zones,drawings
b0=p.LoadBoard(str(base/(ID+'.kicad_pcb')));b1=p.LoadBoard(str(P/'eda'/(ID+'.kicad_pcb')))
s0,s1=signature(b0),signature(b1)
vchanges={r:[s0[1][r],s1[1][r]] for r in s0[1] if s0[1][r]!=s1[1].get(r)}
checks += [check('Footprints, placements, references, pads and drills unchanged',s0[0]==s1[0]),
           check('Only reviewed PCB value changed',vchanges=={'R17':['100K','10K']},vchanges),
           check('All tracks and vias including locks unchanged',s0[2]==s1[2]),
           check('All zone outlines, keepouts and thermal settings unchanged',s0[3]==s1[3])]
oldtitle='EGRLab P03 CORE / PCB R4 / 2026-09' if ID=='P03' else 'EGRLab P04 SAFE / R2 / 2026-09'
newtitle='EGRLab P03 CORE / PCB R5 / 2026-09' if ID=='P03' else 'EGRLab P04 SAFE / R2.2 / 2026-09'
normalized=[]
for d in s1[4]:
    if d[0]=='text' and d[1][0]==newtitle:d=('text',(oldtitle,)+d[1][1:])
    normalized.append(d)
checks.append(check('Only revision title changes in board drawings; outline unchanged',s0[4]==ordered(normalized)))
fills=[]
for L in (p.F_Cu,p.B_Cu):
    def combined(b):
        result=p.SHAPE_POLY_SET()
        for z in b.Zones():
            if not z.GetIsRuleArea() and z.IsOnLayer(L):result.BooleanAdd(z.GetFilledPolysList(L))
        return result
    xor=p.SHAPE_POLY_SET();xor.BooleanXor(combined(b0),combined(b1));area=abs(xor.Area())/1e12
    fills.append({'layer':b0.GetLayerName(L),'xor_mm2':area})
checks.append(check('Filled copper unchanged (geometric XOR <=1e-8 mm2)',all(r['xor_mm2']<=1e-8 for r in fills),fills))
report={'checks':checks,'passed':all(c['pass'] for c in checks),'base_pcb_sha256':hashlib.sha256((base/(ID+'.kicad_pcb')).read_bytes()).hexdigest()}
(P/'verification/revision-checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for c in checks:print('PASS' if c['pass'] else 'FAIL',c['check'])
assert report['passed'],'Unexpected revision delta; inspect revision-checks.json'
