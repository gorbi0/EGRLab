"""Final consistency audit beyond the schematic generator and legacy checks."""
from cadlib import P,parse,subs,one
from dynamics import load,scalar
from pathlib import Path
import json,hashlib,csv
c,pin,v=load(P/'verification/P01.xml');parts=json.loads((P/'docs/parts.json').read_text(encoding='utf-8'))
checks=[]
def check(n,ok):
 checks.append({'id':n,'pass':bool(ok)})
 assert ok,n
for r,expected in [('C5',10e-9),('C6',1e-6),('R21',100e3),('R22',470e3),('R27',10)]:
 check(r+' released numeric value',abs(v[r]-expected)<abs(expected)*1e-9)
for r,mpn,L,W in [('C5','B32529C1103J000',7.3,2.5),('C6','MKS2D041001K00JO00',7.2,7.2)]:
 p=parts[r];lib,name=p['footprint'].split(':');fp=parse((P/'eda/libraries'/(lib+'.pretty')/(name+'.kicad_mod')).read_text(encoding='utf-8'))
 pads=subs(fp,'pad');xs=[float(one(a,'at')[1]) for a in pads]
 fab=next(x for x in subs(fp,'fp_rect') if one(x,'layer')[1]=='F.Fab')
 x1,y1=map(float,one(fab,'start')[1:]);x2,y2=map(float,one(fab,'end')[1:])
 check(r+' manufacturer dimensions and MPN',p['mpn']==mpn and abs(xs[1]-xs[0]-5)<1e-9 and abs(x2-x1-L)<1e-9 and abs(y2-y1-W)<1e-9)
check('Q2 metadata is MOS, not legacy PNP',parts['Q2']['kind']=='PMOS')
for ref in ['Q1','Q2']:check(ref+' manufacturer GDS net functions',[pin(ref,n) for n in [1,2,3]]==(['p01_gate','p01_q1_drain','p01_vs'] if ref=='Q1' else ['p01_off_base','p01_off_col','p01_vs']))
check('D9 clamps gate-source, correct polarity',[pin('D9',n) for n in [1,2]]==['p01_vs','p01_off_base'])
accept=(P/'docs/ODBIOR.md').read_text(encoding='utf-8')
check('acceptance removed old Q2 pinout','E-B-C Q2' not in accept and 'Q2/Q4=2N5401' not in accept)
check('acceptance preserves full OVP measurement boundary','VIN na J1' in accept and '100µs' in accept)
dyn=json.loads((P/'verification/dynamics.json').read_text(encoding='utf-8'))
check('simulation report belongs to actual XML',dyn['xml_sha256']==hashlib.sha256((P/'verification/P01.xml').read_bytes()).hexdigest())
check('all dynamics checks ran, no probe-only report',len(dyn['results'])==26 and len(dyn['checks'])==30 and dyn['pass'])
check('frozen R1 regression has wrong behavior',dyn['R1_regression']['peak_VSG_V']>1)
check('all 3 numerical convergence probes present',len(dyn['convergence'])==3)
buy=list(csv.DictReader((P/'docs/ZAKUPY.csv').open(encoding='utf-8-sig'),delimiter=';'))
check('two main MOSFETs in grouped procurement',next(r for r in buy if r['MPN']=='SUP53P06-20-E3')['Ilosc_szt']=='2')
check('two gate zeners in grouped procurement',next(r for r in buy if r['MPN']=='BZX55C15-TAP')['Ilosc_szt']=='2')
(P/'verification/release-checks.json').write_text(json.dumps({'checks':checks,'pass':True},indent=2),encoding='utf-8')
print(len(checks),'final release checks PASS')
