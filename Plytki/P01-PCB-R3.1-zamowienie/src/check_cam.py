"""Read the actual manufacturing files with an independent Gerber/Excellon parser.
Requires gerbonara==1.5.0; does not modify the manufacturing data.
"""
from pathlib import Path
from collections import Counter
import hashlib, json, warnings, re
from gerbonara import LayerStack
from gerbonara.graphic_objects import Flash, Line, Region
from gerbonara.utils import MM

R = Path(__file__).resolve().parents[1]
G = R/'gerber'
V = R/'verification'
D = json.loads((V/'board-fabrication-data.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
def check(name, ok, details=None):
    checks.append({'name':name,'pass':bool(ok),'details':details})
    if not ok: print('FAIL', name, details)
expected={'P01-F_Cu.gtl','P01-B_Cu.gbl','P01-F_Mask.gts','P01-B_Mask.gbs','P01-F_Silkscreen.gto','P01-B_Silkscreen.gbo','P01-Edge_Cuts.gm1','P01-PTH.drl','P01-NPTH.drl'}
check('Exactly seven Gerber layers plus two Excellon files', {f.name for f in G.iterdir()}==expected)
with warnings.catch_warnings(record=True) as ws:
    warnings.simplefilter('always')
    s=LayerStack.open(G)
    parser_warnings=[str(w.message) for w in ws]
check('No unrecognised parser warnings',all('G90 header statement found after end of header' in w for w in parser_warnings),parser_warnings)
check('Layer roles independently recognised',set(s.graphic_layers)=={('top','copper'),('top','mask'),('top','silk'),('bottom','copper'),('bottom','mask'),('bottom','silk'),('mechanical','outline')})
check('Every graphical layer contains data',all(len(l.objects)>0 for l in s.graphic_layers.values()))
edge=s.outline.objects
coords=Counter()
for o in edge:
    if isinstance(o,Line):
        coords[(round(o.x1,6),round(o.y1,6))]+=1
        coords[(round(o.x2,6),round(o.y2,6))]+=1
check('Single closed outline: 160 x 120 mm at absolute origin',len(edge)==4 and all(isinstance(o,Line) for o in edge) and coords==Counter({(0,0):2,(160,0):2,(160,-120):2,(0,-120):2}),dict((str(k),v) for k,v in coords.items()))
for plated,layer,label in [(True,s.drill_pth,'PTH'),(False,s.drill_npth,'NPTH')]:
    found=Counter((round(o.x,3),round(o.y,3),round(o.aperture.diameter,3)) for o in layer.objects if isinstance(o,Flash) and o.unit==MM)
    wanted=Counter((round(o['x'],3),round(o['y'],3),round(o['diameter'],3)) for o in D['holes'] if o['plated']==plated)
    check(label+' complete hit-by-hit comparison with PCB',found==wanted and len(layer.objects)==sum(wanted.values()),{'count':len(layer.objects),'missing':list((wanted-found).elements()),'extra':list((found-wanted).elements())})
    text=(G/f'P01-{label}.drl').read_text()
    check(label+' metric decimal absolute coordinates',all(x in text for x in ['METRIC','G90','absolute / metric / decimal']),None)
    check(label+' explicit plating attribute',('TF.FileFunction,Plated' if plated else 'TF.FileFunction,NonPlated') in text)
pad_wanted=Counter((o['ref'],o['pin'],round(o['x'],6),round(o['y'],6),o['net']) for o in D['pads'] if o['attr']==0)
for side in ('top','bottom'):
    layer=s[(side,'copper')]
    found=Counter()
    # Gerbonara 1.5 retains X2 attributes on flashes but loses them on regions.
    # Read only that metadata from the native stream, retaining Gerbonara's
    # independent region geometry. Every G36 must match one parsed region.
    attrs={}; region_attrs=[]
    text=Path(layer.original_path).read_text()
    for token in re.findall(r'%TO\.[PN],[^%]*?\*%|%TD\*%|G36\*',text):
        if token=='%TD*%': attrs={}
        elif token=='G36*': region_attrs.append(dict(attrs))
        else: attrs['.'+token[4]]=tuple(token[6:-2].split(','))
    regions=[o for o in layer.objects if isinstance(o,Region)]
    check(side+' region metadata count equals independently parsed geometry',len(regions)==len(region_attrs))
    region_iter=iter(region_attrs)
    for o in layer.objects:
        oa=next(region_iter) if isinstance(o,Region) else o.attrs
        if isinstance(oa,dict) and '.P' in oa and isinstance(o,(Flash,Region)):
            ref,pin,*_=oa['.P']
            (x0,y0),(x1,y1)=o.bounding_box(MM)
            x,y=(o.x,o.y) if isinstance(o,Flash) else ((x0+x1)/2,(y0+y1)/2)
            net=oa.get('.N',('',))[0]
            found[(ref,pin,round(x,6),round(y,6),'' if net=='N/C' else net)]+=1
    check(side+' copper: all 199 THT pad positions and nets match',found==pad_wanted,{'pads':sum(found.values()),'missing':list((pad_wanted-found).elements()),'extra':list((found-pad_wanted).elements())})
    for use in ('copper','mask','silk'):
        name=Path(s[(side,use)].original_path).name
        txt=(G/name).read_text()
        check(side+' '+use+' mm / 4.6 / complete end marker',all(x in txt for x in ['%MOMM*%','%FSLAX46Y46*%','M02*']),None)
    mask=(G/('P01-F_Mask.gts' if side=='top' else 'P01-B_Mask.gbs')).read_text()
    check(side+' soldermask opening polarity is Negative','%TF.FilePolarity,Negative*%' in mask)
    mask_centres=[]
    for o in s[(side,'mask')].objects:
        if isinstance(o,(Flash,Region)):
            (x0,y0),(x1,y1)=o.bounding_box(MM)
            mask_centres.append(((x0+x1)/2,(y0+y1)/2))
    missing=[(p['ref'],p['pin']) for p in D['pads'] if p['attr']==0 and not any(abs(x-p['x'])<0.001 and abs(y-p['y'])<0.001 for x,y in mask_centres)]
    check(side+' mask has an opening at every THT solder pad',not missing,missing)
    # No forced coordinates/mirroring are applied to manufacturing files. Only
    # the human-facing bottom-side preview is mirrored by the SVG renderer.
    with warnings.catch_warnings(record=True) as ws:
        warnings.simplefilter('always')
        svg=str(s.to_pretty_svg(side=side,margin=1,force_bounds=((0,-120),(160,0)),use=False))
        check(side+' preview: no warning except intentionally absent paste',all('paste' in str(w.message) and 'not found' in str(w.message) for w in ws))
    (R/'podglad'/f'CAM-{side}.svg').write_text(svg,encoding='utf-8')
    for use in ('copper','mask','silk'):
        svg=str(s[(side,use)].to_svg(force_bounds=((0,-120),(160,0)),margin=0))
        (R/'podglad'/f'CAM-{side}-{use}.svg').write_text(svg,encoding='utf-8')
(R/'podglad/CAM-outline.svg').write_text(str(s.outline.to_svg(force_bounds=((0,-120),(160,0)),margin=1)),encoding='utf-8')
receipt=json.loads((V/'export-receipt.json').read_text())
check('CAM bytes unchanged since export',receipt['files']=={f.name:sha(f) for f in G.iterdir()})
report={'pass':all(c['pass'] for c in checks),'parser':'gerbonara 1.5.0','checks':checks,'board_sha256':D['board_sha256'],'files':receipt['files'],'notes':['Parser warns about KiCad G90 after Excellon header; complete drill coordinates and diameters independently match all PCB holes.','Gerber coordinates are not mirrored; bottom preview is viewed from the bottom.','This is CAM content validation, not an independent electrical DRC.']}
(V/'cam-checks.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'pass':report['pass'],'checks':len(checks),'PTH':len(s.drill_pth.objects),'NPTH':len(s.drill_npth.objects)}))
if not report['pass']: raise SystemExit(1)
