import pcbnew as p, json, math
from pathlib import Path
src=Path(r'C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-do-recenzji/Plytki/M1-R1-review')
b=p.LoadBoard(str(src/'eda/M1.kicad_pcb'))
mm=p.ToMM
xy=lambda v:[round(mm(v.x),4),round(mm(v.y),4)]
fps={f.GetReference():f for f in b.GetFootprints()}
out={'pads':{},'tracks':[],'vias':[],'zones':[]}
for r,f in fps.items():
 for pad in f.Pads():
  out['pads'][r+'.'+pad.GetNumber()]={'xy':xy(pad.GetPosition()),'size':xy(pad.GetSize()),'layer':b.GetLayerName(pad.GetLayer()),'net':pad.GetNetname(),'angle':pad.GetOrientationDegrees()}
for t in b.GetTracks():
 if isinstance(t,p.PCB_VIA): out['vias'].append({'xy':xy(t.GetPosition()),'net':t.GetNetname(),'dia':mm(t.GetWidth(p.F_Cu)),'drill':mm(t.GetDrillValue())})
 else: out['tracks'].append({'start':xy(t.GetStart()),'end':xy(t.GetEnd()),'net':t.GetNetname(),'layer':b.GetLayerName(t.GetLayer()),'width':mm(t.GetWidth()),'len':mm(t.GetLength())})
for z in b.Zones():
 out['zones'].append({'net':z.GetNetname(),'name':z.GetZoneName(),'rule':z.GetIsRuleArea(),'layers':[b.GetLayerName(L) for L in z.GetLayerSet().Seq()]})
Path(__file__).with_name('geometry.json').write_text(json.dumps(out,indent=2))
for r in ['U3','U4','C5','C6','C7','C8','C9','C10','C11','C12','C13','C14','C15','C24','C25','C28']:
 print(r, {k:v for k,v in out['pads'].items() if k.split('.')[0]==r})
import gndpath
pairs={ 'C6':('U3','1','2'), 'C7':('U3','37','35'), 'C8':('U3','38','40'), 'C9':('U3','48','47'), 'C10':('U3','23','26'), 'C11':('U3','36','35'), 'C12':('U3','39','40'), 'C13':('U3','42','43'), 'C14':('U3','42','43'), 'C15':('U3','44','46'), 'C24':('U4','6','2'), 'C25':('U5','14','7'), 'C28':('U7','14','7') }
results={}
for net in ['GND','5VA','3V3','5V','REGCAP_A','REGCAP_D','ADC_REF','REFCAP']:
 cu,vi=gndpath.copper(b,net,150,80,res=.1)
 for c,(u,n,g) in pairs.items():
  if net=='GND': cp,up=2,g
  else:
   cp,up=1,n
   if out['pads'][c+'.1']['net']!=net: continue
  s=gndpath.pad_point(b,c,cp); t=gndpath.pad_point(b,u,up)
  d=gndpath.distances(cu,vi,s,{'d':t},res=.1,limit_mm=100)['d']
  result={'net':net,'from':f'{c}.{cp}','to':f'{u}.{up}','straight_mm':round(math.dist(s[:2],t[:2]),2),'copper_mm_approx':d}
  results[net+' '+c]=result; print(result,flush=True)
Path(__file__).with_name('paths.json').write_text(json.dumps(results,indent=2))

