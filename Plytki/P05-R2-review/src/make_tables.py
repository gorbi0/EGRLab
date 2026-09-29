"""Review tables generated from the explicit circuit; wiring dimensions remain specified here."""
from pathlib import Path
import csv,json,collections,hashlib
P=Path(__file__).resolve().parents[1];parts=json.loads((P/'docs/parts.json').read_text())
def table(name,fields,rows):
 with (P/'docs'/name).open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fields,delimiter=';');w.writeheader();w.writerows(rows)
h=[('DAQ','J1','P03/J1','0','B2B','TSW-108-08-G-D-NA / SSW-108-02-G-D-RA','oba zlacza do PCB','2'),
 ('LV05','J2','P02/LV05','200','4 zyly AWG22','Mini-Fit Jr female 4p, Au','P05/J2',''),
 ('DAQOK','J3','P04/J5','150','tasma 6 zyl AWG28 1.27mm','IDC female 6p Au, odciazka, KEY4','P05/J3','4'),
 ('TAPS','J4','P11/TAPS','50','5 par AWG24 sygnal/GND','Mini-Fit Jr female 12p Au, 11/12 NC','P05/J4',''),
 ('VSENSE','J5','P02/VSENSE','150','para AWG22; tylko piny1/2','Mini-Fit Jr female 14p Au, 2 styki','P05/J5',''),
 ('AUX','J6','BNC panel','50','RG174','BNC izolowany od panelu; ekran do GND','P05/J6','')]
fields=['interfejs','P05','drugi_koniec','dlugosc_mm','przewod','wtyk','koniec_lutowany','klucz']
table('interfejsy.csv',fields,[dict(zip(fields,v)) for v in h])
rows=[]
for name,j,peer,length,wire,plug,solder,key in h:
 for pin,net in parts[j]['pins'].items():rows.append(dict(interface=name,connector=j,pin=pin,net=net,key=('YES' if pin==key else ''),length_mm=length,soldered_end=solder))
table('pinout.csv',['interface','connector','pin','net','key','length_mm','soldered_end'],rows)
table('wiazki-BOM.csv',['ref','nazwa','ilosc','dlugosc_mm','przewod','wtyk'],[dict(ref='H_'+a,nazwa='Wiazka '+a,ilosc=1,dlugosc_mm=l,przewod=w,wtyk=c) for a,j,peer,l,w,c,s,k in h if a!='DAQ'])
group=collections.defaultdict(list)
for r,v in parts.items():
 if not r.startswith(('TP','J')):group[(v['mpn'],v['display'],v['footprint'])].append(r)
table('zakupy.csv',['nazwa','ilosc_szt','referencje','wartosc','obudowa'],[dict(nazwa=m,ilosc_szt=len(rr),referencje=', '.join(rr),wartosc=v,obudowa=f) for (m,v,f),rr in group.items()]+[dict(nazwa='TSW-108-08-G-D-NA',ilosc_szt=1,referencje='J1',wartosc='B2B; klucz logiczny2',obudowa='PTH 2.54mm')]+[dict(nazwa='Wiazka '+a+': '+c,ilosc_szt=1,referencje=j,wartosc=l+' mm '+w,obudowa='PTH lutowane na P05') for a,j,peer,l,w,c,s,k in h if a!='DAQ'])
table('netlist-pinowa.csv',['ref','pin','net'],[dict(ref=r,pin=p,net=n) for r,v in parts.items() for p,n in v['pins'].items()])
table('zmiany-v6.1.csv',['nowa_ref','stara_ref','wartosc','uwaga'],[dict(nowa_ref=r,stara_ref=v['source_ref'],wartosc=v['display'],uwaga=v['note']) for r,v in parts.items()])
files={f.relative_to(P/'reference').as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted((P/'reference').rglob('*')) if f.is_file() and f.name!='snapshot-sha256.json'}
(P/'reference/snapshot-sha256.json').write_text(json.dumps(files,indent=2))
print('BOM, harnesses, interfaces, pinout and source snapshot hashes written.')
