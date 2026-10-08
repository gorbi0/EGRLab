from pathlib import Path
import difflib,re,json,math
out=Path(__file__).parent
orig=Path(r'C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-do-recenzji/Plytki/M1-PCB-R1-zamowienie/gerber')
normalize=lambda s:[x for x in s.splitlines() if not any(k in x for k in ['TF.CreationDate','Creation date','Created by KiCad','TF.ProjectId','; DRILL file'])]
coord=re.compile(r'X(-?\d+)Y(-?\d+)D01\*')
def pts(lines):
 r=[]
 for line in lines:
  m=coord.fullmatch(line)
  if not m: raise ValueError(line)
  r.append(tuple(int(x)/1e6 for x in m.groups()))
 return r

def dseg(p,a,b):
 dx,dy=b[0]-a[0],b[1]-a[1]; den=dx*dx+dy*dy
 t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/den)) if den else 0
 return math.dist(p,(a[0]+t*dx,a[1]+t*dy))

def direc(a,b): return max(min(dseg(p,x,y) for x,y in zip(b,b[1:])) for p in a)
report={}
for name in ['M1-F_Cu.gtl','M1-B_Cu.gbl']:
 a=normalize((orig/name).read_text());b=normalize((out/'fresh-cam'/name).read_text())
 hunks=[]
 for tag,i,j,k,l in difflib.SequenceMatcher(None,a,b,autojunk=False).get_opcodes():
  if tag=='equal':continue
  aa,bb=pts(a[i-1:j+1]),pts(b[k-1:l+1])
  d=max(direc(aa,bb),direc(bb,aa))
  hunks.append({'old_line':i+1,'new_line':k+1,'max_vertex_polyline_distance_mm':d})
 report[name]={'hunks':hunks,'max_mm':max(x['max_vertex_polyline_distance_mm'] for x in hunks)}
print(json.dumps(report,indent=2)); (out/'cam-geometric-diffs.json').write_text(json.dumps(report,indent=2))
