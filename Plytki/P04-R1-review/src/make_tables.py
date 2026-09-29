"""Generate purchasing lists and the P04-only interface contract. No edits to other boards."""
from pathlib import Path
import json,csv,collections
P=Path(__file__).resolve().parents[1];parts=json.loads((P/'docs/parts.json').read_text())
def write(name,fields,rows):
 with (P/'docs'/name).open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fields,delimiter=';',extrasaction='ignore');w.writeheader();w.writerows(rows)
rows=[];groups={}
for ref,v in parts.items():
 for pin,net in v['pins'].items():
  if ref.startswith('J'):rows.append({'ref':ref,'nazwa_bazowa':v['source_ref'],'pin':pin,'net':net,'uwaga':v['note']})
 if ref.startswith('TP') or ref in ['J1','J2']:continue
 k=v['mpn'];d=groups.setdefault(k,{'nazwa':v['display'],'MPN':k,'ilosc':0,'jednostka':'szt.','referencje':[],'uwaga':v['note']});d['ilosc']+=1;d['referencje'].append(ref)
for d in groups.values():d['referencje']=', '.join(d['referencje'])
extra=[('PCB P04-R1 160x120 2L 35um','wg KiCad po recenzji',1,'Nie zamawiać przed przymiarką'),
 ('Podstawka DIP14 7.62 mm','precyzyjna / złocone styki',6,'U2-U7; sprawdzić gabaryt'),('Podstawka DIP16 7.62 mm','precyzyjna / złocone styki',1,'U1'),
 ('Adapter SO14 / 15.24mm','Kamami 575068',3,'U8-U10; 18x18mm; przymiarka wymagana'),('Listwa męska 1x7 2.54 mm','złocona, prosta',6,'Ogonki adapterów; dobrać do listew żeńskich'),
 ('Listwa żeńska 1x7 2.54 mm','złocona, prosta',6,'U8-U10; nie standardowa wąska podstawka DIP14'),
 ('Obudowa wtyku LV04 4p','Molex 39-01-2040',1,'H_LV04, druga strona wtyku do P02'),('Styk żeński Au AWG18-24','Molex 39-00-0074',4,'H_LV04 AWG22; zapas osobno'),
 ('Wtyk żeński IDC16 Au','Würth 61201623021',1,'H_SAFE; zaślepka pozycji 4; mechanika odciążki do sprawdzenia'),
 ('Zaślepka klucza IDC','dopasowana do gniazda',1,'H_SAFE pin 4'),('Opaska kablowa 2.5 mm','nylon + miękka podkładka',2,'Kotwy J1/J2'),
 ('Dystans i śruba M3','nylon lub metal z izolacyjną podkładką',4,'Minimum 8 mm prześwitu pod PCB; pod opaską musi zostać miejsce')]
for name,mpn,n,note in extra:groups['EXTRA/'+name]={'nazwa':name,'MPN':mpn,'ilosc':n,'jednostka':'szt.','referencje':'montaż','uwaga':note}
groups['wire']={'nazwa':'Linka AWG22 / izolacja odpowiednia do Mini-Fit','MPN':'4 kolory lub oznaczniki','ilosc':0.8,'jednostka':'m','referencje':'H_LV04','uwaga':'4 x 200 mm długości gotowej; zakupić z zapasem na obróbkę'}
groups['ribbon']={'nazwa':'Taśma 16 żył AWG28, raster 1.27 mm','MPN':'czerwony znacznik żyły 1','ilosc':0.15,'jednostka':'m','referencje':'H_SAFE','uwaga':'150 mm długości gotowej; zakupić z zapasem'}
write('ZAKUPY.csv',['nazwa','MPN','ilosc','jednostka','referencje','uwaga'],groups.values())
write('pinout.csv',['ref','nazwa_bazowa','pin','net','uwaga'],rows)
with (P/'reference/interfejsy.csv').open(encoding='utf-8-sig') as f:rd=csv.DictReader(f,delimiter=';');fields=rd.fieldnames;inter=list(rd)
mapping={v['source_ref']:r for r,v in parts.items() if r.startswith('J')};out=[]
for row in inter:
 if not any('P04/' in row[k] for k in ['koniec_A','koniec_B']):continue
 for k in ['koniec_A','koniec_B','koniec_lutowany']:
  for old,new in mapping.items():row[k]=row[k].replace('P04/'+old,'P04/'+new)
 if row['lacze']=='SENSOR':row.update(pozycje='6',wersja='M2.2',przewod='taśma 6 żył AWG28, raster 1.27mm',typ_wtyku='IDC żeński 6p Au, KEY 2; styki 5/6 NC')
 if row['lacze'] in ['SAFE','LV04']:row['kotwa_mm']='12 (SAFE drugi rząd 14.54)'
 out.append(row)
write('interfejsy.csv',fields,out)
write('WIAZKI-BOM.csv',['nazwa','ilosc','dlugosc_mm','przewod','koniec_lutowany','typ_wtyku','wlasciciel','uwaga'],[
 {'nazwa':'H_'+r['lacze'],'ilosc':1,'dlugosc_mm':r['dlugosc_mm'],'przewod':r['przewod'],'koniec_lutowany':r['koniec_lutowany'],'typ_wtyku':r['typ_wtyku'],'wlasciciel':r['wlasciciel_wiazki'],'uwaga':'W BOM zakupowym P04' if r['wlasciciel_wiazki']=='P04' else 'Informacja kontraktowa; zakup przypisany innemu modułowi, nie dublować'} for r in out])
baseline=json.loads((P/'reference/baseline.json').read_text());scope=[]
for r,v in parts.items():
 if not r.startswith('J'):continue
 orig=baseline[v['source_ref']]['pins'];ok=all(v['pins'].get(k)==n for k,n in orig.items())
 added={k:n for k,n in v['pins'].items() if k not in orig}
 scope.append({'connector':r,'baseline_name':v['source_ref'],'original_pins_unchanged':ok,'added':added})
assert all(r['original_pins_unchanged'] for r in scope)
assert {r['connector']:r['added'] for r in scope if r['added']}=={'J2':{'4':'NC'},'J3':{'2':'NC'},'J4':{'2':'NC','5':'NC','6':'NC'},'J5':{'4':'NC'},'J6':{'5':'NC'}}
(P/'verification/interface-scope.json').write_text(json.dumps(scope,indent=2))
print('BOM, harnesses, pinout and interface scope generated.')
