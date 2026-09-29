"""Assembly A1 overlay; preserves nominal SCH-R3 values and pin-net contract."""
from pathlib import Path
import csv,json,re
P=Path(__file__).resolve().parents[1]
stock=list(csv.DictReader((P/'reference/purchases-2026-09-24.csv').open(encoding='utf-8-sig'),delimiter=';'))
nominal=list(csv.DictReader((P/'docs/BOM.csv').open(encoding='utf-8-sig'),delimiter=';'))
out=[];changes=[]
skip=('tulejka','podkładka','śruba','nakrętka','podstawka','zworka')
for row in nominal:
 ref=row['ref'];found=[a for a in stock if 'P01' in a['modul'] and ref in [q.strip() for q in a['pozycje'].split(',')] and not any(s in a['opis'].lower() for s in skip)]
 assert len(found)<=1,(ref,found)
 a=found[0] if found else None
 mpn=(a['mpn_producent'] or a['symbol_dostawcy']) if a else row['mpn']
 value='221k / 0.1% / 15ppm' if ref=='R8' else row['display']
 if ref in ('R1','R23','R27'):value+=' / 5%'
 entry={'ref':ref,'qty':row['qty'],'nominal_sch_r3':row['display'],'assembly_a1':value,'nominal_mpn':row['mpn'],
  'assembly_mpn_or_supplier_code':mpn,'supplier':a['dostawca'] if a else '',
  'supplier_code':a['symbol_dostawcy'] if a else '', 'footprint':row['footprint'],
  'source':'purchases-2026-09-24.csv' if a else 'BOM R3 / PCB pads or local wire',
  'notes':(a['uwagi'] if a else row['note'])}
 out.append(entry)
 if a and (row['mpn'] not in mpn or ref in ('R8','R1','R23','R27')):changes.append(entry)
path=P/'docs/BOM-MONTAZOWY-A1.csv'
with path.open('w',encoding='utf-8-sig',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=list(out[0]),delimiter=';');writer.writeheader();writer.writerows(out)
(P/'verification/assembly-overlay.json').write_text(json.dumps({'variant':'A1','rows':len(out),'changes':changes},indent=2,ensure_ascii=False)+'\n')
if __name__=='__main__':
 import pcbnew as p
 b=p.LoadBoard(str(P/'eda/P01.kicad_pcb'));rows={r['ref']:r for r in out}
 for fp in b.GetFootprints():
  if fp.GetReference() not in rows:continue
  r=rows[fp.GetReference()]
  for key,value in [('AssemblyVariant','A1'),('AssemblyMPN',r['assembly_mpn_or_supplier_code']),('AssemblyValue',r['assembly_a1'])]:
   fld=next((f for f in fp.GetFields() if f.GetName()==key),None)
   if fld is None:fld=p.PCB_FIELD(fp,p.FIELD_T_USER,key);fp.Add(fld)
   fld.SetText(value);fld.SetVisible(False)
 p.SaveBoard(str(P/'eda/P01.kicad_pcb'),b,True)
 print('Assembly A1 BOM and hidden PCB fields:',len(out),'electrical entries.')
