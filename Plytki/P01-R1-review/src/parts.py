from cadlib import *
import shutil,json,csv
BASE=json.loads((P/'baseline/components.json').read_text(encoding='utf-8'))
PARTS={}
REFMAP={'J_PGB':'J5','J_SUPPLYA':'J6','J_BATB':'J7','J_PRES':'J8','W_PRES':'R34'}
URLS={x['id']:x['url'] for x in json.loads((P/'reference/sources.json').read_text())}
FP=P/'eda/libraries/P01.pretty';FP.mkdir(exist_ok=True)
def axial(name,L,D,pitch,drill,pad,diode=False):
 s=f'(footprint {q(name)} (version 20240108) (generator "pcbnew") (layer "F.Cu") (attr through_hole) (descr "EGRLab P01; source dimensions in footprint-audit.csv")'
 x=(pitch-L)/2
 s+=f'(fp_rect (start {x} {-D/2}) (end {x+L} {D/2}) (stroke (width 0.12) (type default)) (fill none) (layer "F.SilkS"))'
 s+=f'(fp_rect (start -2.5 {-D/2-0.8}) (end {pitch+2.5} {D/2+0.8}) (stroke (width 0.05) (type default)) (fill none) (layer "F.CrtYd"))'
 s+=f'(fp_rect (start {x} {-D/2}) (end {x+L} {D/2}) (stroke (width 0.1) (type default)) (fill none) (layer "F.Fab"))'
 if diode:s+=f'(fp_line (start {x+1} {-D/2}) (end {x+1} {D/2}) (stroke (width 0.4) (type default)) (layer "F.SilkS"))'
 for i,px in [(1,0),(2,pitch)]:s+=f'(pad "{i}" thru_hole {"rect" if i==1 else "circle"} (at {px} 0) (size {pad} {pad}) (drill {drill}) (layers "*.Cu" "*.Mask"))'
 s+='(fp_text reference "REF**" (at 0 -6) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))'
 (FP/(name+'.kicad_mod')).write_text(s+')',encoding='utf-8');return 'P01:'+name
RFP=axial('R_MFR50_H4_P15.24',10.2,4.0,15.24,1,2)
PFP=axial('R_PR02_P17.78',10,3.9,17.78,1.1,2.3)
DFP=axial('TVS_P600_P20.32',9.1,9.1,20.32,1.6,3.8,True)
BFP=axial('TVS_P600_BIDIR_P20.32',9.1,9.1,20.32,1.6,3.8)
def copyfp(lib,name):
 src=K/'footprints'/(lib+'.pretty')/(name+'.kicad_mod');assert src.exists(),src
 dest=P/'eda/libraries'/(lib+'.pretty');dest.mkdir(exist_ok=True);shutil.copy2(src,dest/src.name)
 return lib+':'+name
TO92=copyfp('Package_TO_SOT_THT','TO-92_Inline_Wide');TO220=copyfp('Package_TO_SOT_THT','TO-220-3_Vertical')
# SUP53P06-20 b(max)=1.01 and c(max)=0.61 mm: rectangular lead diagonal 1.18 mm.
# A generic 1.1 mm hole is insufficient at the dimensional corner.
t220=parse((P/'eda/libraries/Package_TO_SOT_THT.pretty/TO-220-3_Vertical.kicad_mod').read_text(encoding='utf-8'))
t220[1]='TO220_3_P2.54_Drill1.4'
for pad in subs(t220,'pad'):
 one(pad,'drill')[1]=A('1.4');one(pad,'size')[1:]=[A('2.1'),A('3.0')]
(FP/'TO220_3_P2.54_Drill1.4.kicad_mod').write_text(dump(t220),encoding='utf-8')
TO220='P01:TO220_3_P2.54_Drill1.4'
D35=copyfp('Diode_THT','D_DO-35_SOD27_P10.16mm_Horizontal')
D41=copyfp('Diode_THT','D_DO-41_SOD81_P10.16mm_Horizontal')
D201=copyfp('Diode_THT','D_DO-201_P15.24mm_Horizontal')
DIP=copyfp('Package_DIP','DIP-8_W7.62mm');TRIM=copyfp('Potentiometer_THT','Potentiometer_Bourns_3296W_Vertical')
def simplepads(name,count,pitch,drill,pad,anchor=False):
 s=f'(footprint {q(name)} (version 20240108) (generator "pcbnew") (layer "F.Cu") (attr through_hole)'
 for i in range(count):s+=f'(pad "{i+1}" thru_hole {"rect" if i==0 else "circle"} (at {i*pitch} 0) (size {pad} {pad}) (drill {drill}) (layers "*.Cu" "*.Mask"))'
 if anchor:
  # 12.5 mm between wire solder row and strain-relief line.
  hole=4.2 if drill>2 else 3.2
  for px in [-3,(count-1)*pitch+3]:s+=f'(pad "" np_thru_hole circle (at {px} -12.5) (size {hole} {hole}) (drill {hole}) (layers "*.Cu" "*.Mask"))'
  s+=f'(fp_text user "TIE / 12.5 mm" (at {(count-1)*pitch/2} -16) (layer "F.SilkS") (effects (font (size 1 1) (thickness .15))))'
 x0=-6 if anchor else -pad/2-0.5;x1=(count-1)*pitch-x0
 y0=-15.5 if anchor else -pad/2-0.5;y1=pad/2+0.5
 s+=f'(fp_rect (start {x0} {y0}) (end {x1} {y1}) (stroke (width 0.05) (type default)) (fill none) (layer "F.CrtYd"))'
 s+=f'(fp_text reference "REF**" (at {(count-1)*pitch/2} 5) (layer "F.SilkS") (effects (font (size 1 1) (thickness .15))))'
 (FP/(name+'.kicad_mod')).write_text(s+')',encoding='utf-8');return 'P01:'+name

def caprect(name,L,W,pitch):
 s=f'(footprint {q(name)} (version 20240108) (generator "pcbnew") (layer "F.Cu") (attr through_hole)'
 for layer,margin,width in [('F.Fab',0,0.1),('F.SilkS',0.1,0.12),('F.CrtYd',0.5,0.05)]:
  s+=f'(fp_rect (start {(pitch-L)/2-margin} {-W/2-margin}) (end {(pitch+L)/2+margin} {W/2+margin}) (stroke (width {width}) (type default)) (fill none) (layer "{layer}"))'
 for n,x in [(1,0),(2,pitch)]:s+=f'(pad "{n}" thru_hole circle (at {x} 0) (size 1.8 1.8) (drill 0.9) (layers "*.Cu" "*.Mask"))'
 s+=f'(fp_text reference "REF**" (at {pitch/2} {-W/2-1.5}) (layer "F.SilkS") (effects (font (size 1 1) (thickness .15))))'
 (FP/(name+'.kicad_mod')).write_text(s+')',encoding='utf-8');return 'P01:'+name
BAT=simplepads('Pigtail_PWR_2x2.5mm2',2,7.62,2.4,5.2,True)
PG=simplepads('Pigtail_PG_6xAWG22',6,2.54,1.1,2,True)
TP2=simplepads('TestPads_2',2,5.08,1,2);TP3=simplepads('TestPads_3',3,5.08,1,2)
TP1=simplepads('TestPad_1',1,0,1,2)
# Header body: manufacturer drawing must be checked before layout approval.
MSTB=copyfp('Connector_Phoenix_MSTB','PhoenixContact_MSTBA_2,5_3-G-5,08_1x03_P5.08mm_Horizontal')
polar={'C1':('10u / 63V','UPW1J100MDD',5,2,'https://www.nichicon.co.jp/products/pdfs/upw.pdf'),
 'C3':('100u / 50V','EEUFR1H101',8,3.5,'https://industrial.panasonic.com/sa/products/pt/aluminum-cap-lead/models/EEUFR1H101'),
 'C7':('22u / 50V','EEUFR1H220',5,2,'https://industrial.panasonic.com/sa/products/pt/aluminum-cap-lead/models/EEUFR1H220'),
 'C9':('47u / 50V','EEUFR1H470',6.3,2.5,'https://industrial.panasonic.com/sa/products/pt/aluminum-cap-lead/models/EEUFR1H470')}
for key,c in BASE.items():
 if c['board']!='P01':continue
 p=copy.deepcopy(c);p['source_ref']=c['ref'];r=p['ref']=REFMAP.get(c['ref'],c['ref']);p['pins']={('1' if n=='K' else '2' if n=='A' else n):v for n,v in c['pins'].items()};p['mpn']='';p['url']='';p['display']=c['value'];p['footprint']='';p['note']=c['note'];p['qty']=1
 if r.startswith('R') and r!='RV1':
  p['symbol']=symbol('Device','R');p['footprint']=RFP
  if r=='R34':p['display']='0R / link';p['mpn']='Tinned copper wire 0.6 mm';p['note']='Presence link. No resistor tolerance.'
  else:
   v=int(c['value'].split()[0]);val=(str(v//1000)+'K' if v%1000==0 else (str(v/1000).rstrip('0').rstrip('.').replace('.','K') if v>=1000 else str(v)+'R'))
   p['display']=val+' / 0.5W';p['mpn']='MFR-50FTE52-'+val;p['url']=URLS['mfr']
   if 5<=int(r[1:])<=11:
    t={54900:'54K9',10000:'10K',220000:'220K',26100:'26K1',249000:'249K'}[v]
    p['mpn']='H4'+t+'BYA';p['display']=t+' / 0.1%';p['url']='https://www.te.com/en/product-9-1879659-1.html';p['note']+=' Selected HOLCO H4 0.5 W, 0.1%, 15 ppm/K; 10 x 3.7 mm.'
   if r in ['R1','R23','R27']:
    code={150:'1500',2200:'2201',47:'4709'}[v];p['mpn']='PR0200020'+code+'FR500';p['display']=val+' / 2W';p['footprint']=PFP;p['url']=URLS['pr02']
 if r.startswith('C'):
  p['symbol']=symbol('Device','C')
  if r in polar:
   disp,mpn,d,pitch,url=polar[r];p.update(display=disp,mpn=mpn,url=url,symbol=symbol('Device','C_Polarized'))
   p['footprint']=copyfp('Capacitor_THT',f'CP_Radial_D{d:.1f}mm_P{pitch:.2f}mm')
  elif r in ['C2','C4','C5','C6']:
   code={'C2':'1104','C4':'1104','C5':'1224','C6':'1473'}[r];p['mpn']='B32529C'+code+'J000';p['display']=c['value'].replace(' ','')+' / 100V';p['url']='https://www.tdk-electronics.tdk.com/inf/20/20/db/fc_2009/B32520_529.pdf'
   width=3.5 if r=='C5' else 2.5
   p['footprint']=caprect(f'C_TDK_B32529_L7.3_W{width}_P5',7.3,width,5)
  else:
   p['mpn']={'C8':'K104K15X7RF53H5','C10':'K104K15X7RF53H5','C11':'K104K15X7RF53H5','C12':'K101J15C0GF53H5','C13':'K102J15C0GF53H5'}[r]
   p['display']=c['value'].replace(' ','')+(' / C0G' if r in ['C12','C13'] else ' / X7R')
   p['url']='https://www.vishay.com/docs/45171/kseries.pdf';p['footprint']=caprect('C_Vishay_K15_H5_P5',6.2,2.6,5)
 if r.startswith('D') or r=='LED1':
  p['symbol']=symbol('Device','D_Zener' if r in ['D3','D4','D5'] else 'D_TVS' if r=='D1' else 'D_Schottky_Dual_CommonCathode_AKA' if r=='D2' else 'LED' if r=='LED1' else 'D')
  p['footprint']=D35;p['mpn']=c['value'];p['url']=URLS['4148']
  if r=='D1':p.update(footprint=BFP,mpn='15KPA24CA-B',url=URLS['15kpa'])
  if r=='D2':p.update(footprint=TO220,url=URLS['diode'])
  if r=='D3':p.update(footprint=DFP,mpn='5KP18A-B',url='https://www.littelfuse.com/assetdocs/tvs-diodes-5kp-datasheet?assetguid=b1ddd6a2-fccb-4327-bea1-7d77c0793479')
  if r=='D4':p.update(footprint=D35,mpn='BZX55C15-TAP',url=URLS['zener'])
  if r=='D5':p.update(footprint=D201,url=URLS['1_5ke'])
  if r in ['D6','D7','D8']:p['mpn']='1N4148-TAP'
  if r=='LED1':p.update(footprint=copyfp('LED_THT','LED_D3.0mm'),mpn='L-934GD',display='GREEN 3mm',url='https://www.kingbrightusa.com/images/catalog/SPEC/L-934GD.pdf')
 if r.startswith('Q'):
  p['symbol']=symbol('Transistor_FET','Q_PMOS_GDS') if r=='Q1' else symbol('Transistor_BJT','Q_PNP_EBC' if r in ['Q2','Q4'] else 'Q_NPN_EBC')
  p['mpn']=c['value'];p['footprint']=TO220 if r=='Q1' else TO92;p['url']=URLS['mos' if r=='Q1' else 'pnp' if r in ['Q2','Q4'] else 'npn']
  if r in ['Q2','Q4']:
   p['url']='https://www.onsemi.com/download/data-sheet/pdf/2n5401-d.pdf'
   p['mpn']='2N5401YBU';p['display']='2N5401YBU'
   p['note']+=' R1 procurement selection: onsemi 2N5401YBU, E-B-C, replaces legacy 2N5401G; validate turn-off timing on bench. Never use -C bondout.'
 if r.startswith('U'):
  lib,nm={'U1':('Regulator_Linear','LM2936-5.0_TO92'),'U2':('Comparator','LM2903'),'U3':('Reference_Voltage','TL431LP'),'U4':('Power_Supervisor','MCP120-xxxDxTO')}[r]
  p['symbol']=symbol(lib,nm);p['footprint']=DIP if r=='U2' else TO92;p['mpn']=c['value'];p['display']=c['value'].replace('/NOPB','');p['url']=URLS[{'U1':'lm2936','U2':'lm2903','U3':'tl431','U4':'supervisor'}[r]]
  if r=='U3':
   # TI LP differs from the generic KiCad TL431LP symbol: K=1, A=2, REF=3.
   for pin in pin_defs(p['symbol']).values():
    n=one(pin,'number');n[1]={'1':'3','3':'1'}.get(n[1],n[1])
 if r=='RV1':p.update(symbol=symbol('Device','R_Potentiometer'),footprint=TRIM,display='5K / 3296W',mpn='3296W-1-502LF',url=URLS['trim'])
 if r.startswith('J'):
  count=len(p['pins']);p['symbol']=symbol('Connector_Generic','Conn_01x0'+str(count));p['footprint']=TP3 if count==3 else TP2;p['display']='TEST PADS';p['mpn']='PCB pads (no purchased connector)'
  if r=='J3':p.update(display='INHIBIT / SHORT=OFF',mpn='M20-9990245',footprint=copyfp('Connector_PinHeader_2.54mm','PinHeader_1x02_P2.54mm_Vertical'),url='https://www.harwin.com/products/M20-9990245')
  if r=='J5':p.update(footprint=PG,display='PG / soldered harness',mpn='PCB termination; H_PG')
  if r=='J6':p.update(footprint=MSTB,display='SUPPLY / MSTBA 3p',mpn='1757255',url='https://www.phoenixcontact.com/en-us/products/pcb-header-mstba-25-3-g-508-1757255')
  if r=='J7':p.update(footprint=BAT,display='BAT / soldered wires',mpn='PCB termination; H_BAT')
 assert p['footprint'] and p['mpn'],p
 PARTS[r]=p
for idx,net in enumerate(['P01_VS','P01_GATE','P01_AUX_IN','P01_AUX5','P01_REF','P01_OK','P01_ENABLE','P01_OV_SENSE','P01_UV_SENSE','GND'],1):
 r='TP'+str(idx);PARTS[r]={'ref':r,'source_ref':'ADDED_TESTPAD','value':net,'display':net.replace('P01_',''),'pins':{'1':net},'symbol':symbol('Connector','TestPoint'),'footprint':TP1,'mpn':'PCB test pad','qty':1,'url':'','note':'Additional probe access; no new circuit function.'}
def write_tables():
 clean={r:{k:v for k,v in p.items() if k!='symbol'} for r,p in PARTS.items()}
 (P/'docs/parts.json').write_text(json.dumps(clean,ensure_ascii=False,indent=2),encoding='utf-8')
 fields=['ref','source_ref','display','mpn','qty','footprint','url','note']
 with (P/'docs/BOM.csv').open('w',newline='',encoding='utf-8-sig') as f:
  w=csv.DictWriter(f,fields,delimiter=';',extrasaction='ignore');w.writeheader();w.writerows(PARTS.values())
 libs={p['symbol'][1]:p['symbol'] for p in PARTS.values()};libs['P01:PWR_FLAG']=symbol('power','PWR_FLAG')
 for v in libs.values():v=copy.deepcopy(v);v[1]=v[1].split(':')[1]
 (P/'eda/libraries/P01.kicad_sym').write_text('(kicad_symbol_lib (version 20231120) (generator "kicad_symbol_editor")'+''.join(dump([s[0],s[1].split(':')[1]]+s[2:]) for s in libs.values())+')',encoding='utf-8')
 (P/'eda/sym-lib-table').write_text('(sym_lib_table (lib (name "P01") (type "KiCad") (uri "${KIPRJMOD}/libraries/P01.kicad_sym") (options "") (descr "Reviewed P01 symbols")))',encoding='utf-8')
 flibs=sorted({p['footprint'].split(':')[0] for p in PARTS.values()})
 (P/'eda/fp-lib-table').write_text('(fp_lib_table '+''.join(f'(lib (name {q(l)}) (type "KiCad") (uri "${{KIPRJMOD}}/libraries/{l}.pretty") (options "") (descr "P01 selected footprint"))' for l in flibs)+')',encoding='utf-8')
