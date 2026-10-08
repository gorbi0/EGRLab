from pathlib import Path
import ast,sys,math,re,json
E=Path(__file__).resolve().parent;R=E.parent
sys.path.insert(0,str(R/'review-deps'))
from shapely.geometry import Polygon,GeometryCollection
from shapely import make_valid
S=Path(json.loads((E/'source-snapshot.json').read_text())['source'])/'Plytki/M1-PCB-R1-zamowienie/gerber'
W=R/'work/Plytki/M1-PCB-R1-zamowienie'
tree=ast.parse((W/'src/check_cam.py').read_text(encoding='utf-8'))
nodes=[n for n in tree.body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in ['Gerber','arc_points']]
ns={'math':math,'re':re};exec(compile(ast.Module(body=nodes,type_ignores=[]),'<project Gerber parser>','exec'),ns)
def poly(contours):
    out=GeometryCollection()
    for ring in contours:
        out=out.symmetric_difference(make_valid(Polygon(ring)))
    return out
result={}
for name in ['M1-F_Cu.gtl','M1-B_Cu.gbl']:
    a=ns['Gerber'](S/name);b=ns['Gerber'](W/'gerber'/name)
    assert len(a.regions)==len(b.regions)
    areas=[];distance=[]
    for i,(r,t) in enumerate(zip(a.regions,b.regions)):
        assert r[1:]==t[1:],(name,i,'attributes or polarity')
        if r[0]==t[0]:areas.append(0);distance.append(0);continue
        u,v=poly(r[0]),poly(t[0]);areas.append(u.symmetric_difference(v).area);distance.append(u.hausdorff_distance(v))
    result[name]={'same_apertures':a.aps==b.aps,'same_flashes':a.flashes==b.flashes,'same_lines':a.lines==b.lines,
                  'region_count':len(a.regions),'sum_region_xor_mm2':sum(areas),'max_region_hausdorff_mm':max(distance),
                  'different_regions':sum(x>0 for x in areas)}
(E/'fresh-cam-region-comparison.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
