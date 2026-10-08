from pathlib import Path
import hashlib,json,difflib,re,zipfile
out=Path(__file__).parent
orig=Path(r'C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-do-recenzji/Plytki/M1-PCB-R1-zamowienie')
result={}
normalize=lambda s:'\n'.join(x for x in s.splitlines() if not any(k in x for k in ['TF.CreationDate','Creation date','Created by KiCad','TF.ProjectId','; DRILL file']))
for f in (orig/'gerber').iterdir():
 fresh=out/'fresh-cam'/f.name
 a,b=normalize(f.read_text()),normalize(fresh.read_text())
 same=a==b
 result[f.name]={'same_except_metadata':same,'sha_old':hashlib.sha256(f.read_bytes()).hexdigest(),'sha_fresh':hashlib.sha256(fresh.read_bytes()).hexdigest()}
 if not same:
  lines=list(difflib.unified_diff(a.splitlines(),b.splitlines(),n=1))
  (out/(f.name+'.diff')).write_text('\n'.join(lines)); print(f.name,'DIFF',len(lines)); print('\n'.join(lines[:16]))
 else: print(f.name,'MATCH')
with zipfile.ZipFile(orig/'DO-ZAMOWIENIA_M1-PCB-R1.zip') as z:
 result['zip_match']={n:z.read(n)==(orig/'gerber'/n).read_bytes() for n in z.namelist()}
 print('ZIP',result['zip_match'])
(out/'cam-comparison.json').write_text(json.dumps(result,indent=2))

