"""P05-R1 explicit circuit. All connector numbers preserve v6.1 / P03-R1 snapshot."""
from cadlib import *
import shutil,csv
import make_custom_footprints
FP=P/'eda/libraries/P05.pretty';FP.mkdir(parents=True,exist_ok=True);PARTS={}
URL={k:v['url'] for k,v in json.loads((P/'reference/datasheets/sources.json').read_text()).items()}
G='GND';V='3V3_DAQ';A5='5VA_P05';S5='5V_SYS'
def copyfp(lib,name):
 src=K/'footprints'/(lib+'.pretty')/(name+'.kicad_mod');assert src.exists(),src
 dest=P/'eda/libraries'/(lib+'.pretty');dest.mkdir(parents=True,exist_ok=True);target=dest/src.name
 shutil.copy2(src,target)
 if name=='R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal':
  # Local artwork only: 0.02 mm inset on each long silk edge gives >=0.15 mm
  # silk clearance between R10/R18. Pads, courtyard and body geometry unchanged.
  fp=parse(target.read_text())
  for g in subs(fp,'fp_rect'):
   if one(g,'layer')[1]=='F.SilkS':one(g,'start')[2]=A('-1.35');one(g,'end')[2]=A('1.35')
  target.write_text(dump(fp)+'\n')
 return lib+':'+name
def localfp(name):
 shutil.copy2(P/'input/footprints'/(name+'.kicad_mod'),FP/(name+'.kicad_mod'));return 'P05:'+name
def pigtail(name,n,ribbon=False):
 pts=[(i+1,(i//2)*2.54,(i%2)*2.54) for i in range(n)] if ribbon else [(i+1,(i//2)*3.5,(i%2)*3.5) for i in range(n)]
 xmax=max(x for _,x,_ in pts);ymax=max(y for _,_,y in pts);hole,pad=(.8,1.8) if ribbon else (1.1,2.2)
 s=f'(footprint "{name}" (version 20240108) (generator "pcbnew") (layer "F.Cu") (attr through_hole)'
 for i,x,y in pts:s+=f'(pad "{i}" thru_hole {"rect" if i==1 else "circle"} (at {x} {y}) (size {pad} {pad}) (drill {hole}) (layers "*.Cu" "*.Mask"))'
 for x in (-3.3,xmax+3.3):s+=f'(pad "" np_thru_hole circle (at {x} -11.5) (size 3.2 3.2) (drill 3.2) (layers "*.Cu" "*.Mask"))'
 s+=f'(fp_rect (start -5.3 -14) (end {xmax+5.3} {ymax+1.6}) (stroke (width .05) (type default)) (fill none) (layer "F.CrtYd"))'
 s+=f'(fp_text reference "REF**" (at {xmax/2} {ymax+3}) (layer "F.SilkS") (effects (font (size 1 1) (thickness .15)))))'
 (FP/(name+'.kicad_mod')).write_text(s);return 'P05:'+name
def custom(name,units):
 # rows: (pin,name,electrical type) left/right. Explicit function symbols, not fake connectors.
 s=f'(symbol "P05:{name}" (pin_names (offset 1.016)) (in_bom yes) (on_board yes)'
 for u,(left,right) in enumerate(units,1):
  h=max(len(left),len(right))+1;half=12.7
  s+=f'(symbol "{name}_{u}_1" (rectangle (start {-half} {h*1.27}) (end {half} {-h*1.27}) (stroke (width .254) (type default)) (fill (type background))))'
  s+=f'(symbol "{name}_{u}_0"'
  for side,items in [(-1,left),(1,right)]:
   for j,(n,label,typ) in enumerate(items):
    s+=f'(pin {typ} line (at {side*(half+5.08)} {(h-2-j*2)*1.27} {0 if side==-1 else 180}) (length 5.08) (name {q(label)} (effects (font (size 1.0 1.0)))) (number "{n}" (effects (font (size 1 1)))))'
  s+=')'
 return parse(s+')')
RFP=copyfp('Resistor_THT','R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal')
RPOWER=copyfp('Resistor_THT','R_Axial_DIN0411_L9.9mm_D3.6mm_P15.24mm_Horizontal')
C0603=copyfp('Capacitor_SMD','C_0603_1608Metric');C0805=copyfp('Capacitor_SMD','C_0805_2012Metric');C1210=copyfp('Capacitor_SMD','C_1210_3225Metric')
R0805=copyfp('Resistor_SMD','R_0805_2012Metric')
QFP=copyfp('Package_QFP','LQFP-64_10x10mm_P0.5mm');SO8=copyfp('Package_SO','SOIC-8_3.9x4.9mm_P1.27mm')
SO14=copyfp('Package_SO','SOIC-14_3.9x8.7mm_P1.27mm');VSSOP8=copyfp('Package_SO','VSSOP-8_3x3mm_P0.65mm')
DIP14=copyfp('Package_DIP','DIP-14_W7.62mm');DIP18=copyfp('Package_DIP','DIP-18_W7.62mm')
TO92=copyfp('Package_TO_SOT_THT','TO-92_Inline_Wide');DIO=copyfp('Diode_THT','D_DO-35_SOD27_P7.62mm_Horizontal')
CP=copyfp('Capacitor_THT','CP_Radial_D8.0mm_P3.50mm');RELAY=copyfp('Relay_THT','Relay_DPDT_Omron_G6K-2P-Y')
TPFP=localfp('TestPad_1')
SR=symbol('Device','R');SC=symbol('Device','C');SCP=symbol('Device','C_Polarized')
def add(ref,src,sym,fp,value,mpn,pins,sheet,url='',note='',**extra):
 PARTS[ref]=dict(ref=ref,source_ref=src,symbol=sym,footprint=fp,display=value,value=value,mpn=mpn,pins={str(k):v for k,v in pins.items()},sheet=sheet,url=url,note=note,qty=1,on_board=True,**extra)
def res(ref,src,value,ohms,a,b,sheet,tol=.01,smd=False,power=False):
 mpn=('MBB0207 precision metal film' if tol==.001 else 'metal film resistor')+f' {value} '+('0.1%' if tol==.001 else '1%')
 if smd:mpn='0805 1% 0.125W '+value
 add(ref,src,SR,R0805 if smd else RPOWER if power else RFP,value,mpn,{1:a,2:b},sheet,note=('1W minimum; pulse energy at turn-on >=6mJ. ' if power else '')+'One full-value resistor, no series substitution. Precision parts TCR <=25ppm/K.',ohms=ohms,tolerance=tol)
def cap(ref,src,value,farads,a,b,sheet,large=False,small=False):
 fp=C0603 if small else C1210 if large else C0805
 add(ref,src,SC,fp,value,('C0G 50V 5% ' if farads<1e-9 else 'X7R 25V 10% ')+value,{1:a,2:b},sheet,farads=farads,note='1210: effective capacitance >=10uF at 4.4V required' if large else '')
B=json.loads((P/'reference/baseline.json').read_text())
def bp(src):return {k:(V if n=='3V3_IO' else n) for k,n in B[src]['pins'].items()}
# ADC symbol specialised for hard-strapped serial software mode.
di=[(i,n,'input') for i,n in [(3,'OS0'),(4,'OS1'),(5,'OS2'),(6,'SER'),(7,'STBY'),(8,'RANGE'),(9,'CONVST'),(10,'WR'),(11,'RESET'),(12,'SCLK'),(13,'CS_N'),(29,'SDI')]]
do=[(14,'BUSY','output'),(15,'FRSTDATA','output'),(24,'DOUTA','tri_state'),(25,'DOUTB','tri_state'),(27,'DOUTC','tri_state'),(28,'DOUTD','tri_state')]
unused=[(i,'DB'+str({**{x:x-16 for x in range(16,23)},30:12,31:13,32:14,33:15}[i])+'_SER_GND','passive') for i in [16,17,18,19,20,21,22,30,31,32,33]]
ap=[(49+2*i,'V'+str(i+1),'input') for i in range(8)]
ag=[(50+2*i,'V'+str(i+1)+'GND','input') for i in range(8)]
pl=[(1,'AVCC1','power_in'),(37,'AVCC37','power_in'),(38,'AVCC38','power_in'),(48,'AVCC48','power_in'),(23,'VDRIVE','power_in'),(34,'REF_SEL','input'),(42,'REFIN_OUT','passive'),(36,'REGCAP_A','passive'),(39,'REGCAP_D','passive'),(44,'REFCAPA','passive'),(45,'REFCAPB','passive')]
pr=[(i,'AGND','power_in') for i in [2,26,35,40,41,47]]+[(43,'REFGND','power_in'),(46,'REFGND','power_in')]
adc=custom('AD7606BBSTZ_SERIAL',[(di,do+unused),(ap,ag),(pl,pr)])
pins=bp('U1');pins['14']='AD_BUSY_LOCAL'
add('U1','U1',adc,QFP,'AD7606BBSTZ','AD7606BBSTZ',pins,'ADC',URL['AD7606B.pdf'],'OS=111 serial software; REF_SELECT high = internal reference. Grounded DB pins per serial-mode data sheet.')
add('U2','U13',symbol('Reference_Voltage','ADR4525'),SO8,'ADR4525BRZ','ADR4525BRZ',bp('U13'),'READY',URL['ADR4525.pdf'],'Reference for rail window only; NOT ADC reference.')
cmp=custom('TLV1702AQDGKRQ1',[([(3,'+A','input'),(2,'-A','input')],[(1,'OUT_A','open_collector')]), ([(5,'+B','input'),(6,'-B','input')],[(7,'OUT_B','open_collector')]), ([(8,'VCC','power_in')],[(4,'GND','power_in')])])
add('U3','U6',cmp,VSSOP8,'TLV1702-Q1','TLV1702AQDGKRQ1',bp('U6'),'READY',URL['TLV1702-Q1.pdf'])
drv=custom('TBD62083APG',[( [(i,'IN'+str(i),'input') for i in range(1,9)]+[(9,'GND','power_in')],[(19-i,'OUT'+str(i),'open_collector') for i in range(1,9)]+[(10,'COM','passive')])])
dp=bp('U18');dp['1']='MEAS_PERMIT';dp['10']=S5
add('U4','U18',drv,DIP18,'TBD62083APG','TBD62083APG',dp,'TAPS','https://toshiba.semicon-storage.com/us/semiconductor/product/linear-ics/transistor-arrays/detail.TBD62083APG.html','COM to coil supply. Inputs 2..8 tied low. Local diodes at coils.')
hp=bp('U_READY');hp.update({'9':'MEAS_EN_P05','10':'DAQ_OK','8':'MEAS_PERMIT'})
add('U5','U_READY',symbol('74xx','74LS08','SN74HC08N'),DIP14,'SN74HC08N','SN74HC08N',hp,'READY','https://www.ti.com/lit/ds/symlink/sn74hc08.pdf')
sup=custom('MCP120_D_TO',[([(2,'VDD','power_in')],[(1,'RESET_N','open_collector'),(3,'VSS','power_in')])])
for r,src,mpn in [('U6','U_SUP3','MCP120-300DI/TO'),('U7','U_SUP5','MCP120-450DI/TO')]:add(r,src,sup,TO92,mpn,mpn,bp(src),'READY',URL['MCP120.pdf'],'D bondout 1 reset, 2 VDD, 3 GND. Open drain.')
lvc=symbol('74xx','74LVC125','74LVC125AD')
for ref,src,sh in [('U8','U_SUPBUF','READY'),('U9','U_RX1','DIG'),('U10','U_RX2','DIG'),('U11','U_TX','DIG')]:
 pp=bp(src)
 if ref=='U11':pp.update({'4':G,'5':'AD_BUSY_LOCAL','6':'ADC_BUSY'})
 add(ref,src,lvc,SO14,'74LVC125AD','74LVC125AD,118',pp,sh,URL['LVC125.pdf'],'Nexperia Ioff, soldered directly; no adapter.')
add('U12','ADDED_LOCAL_LDO',symbol('Regulator_Linear','MCP1700x-330xxTO'),TO92,'MCP1700-3302E/TO','MCP1700-3302E/TO',{1:G,2:A5,3:V},'P05',URL['MCP1700.pdf'],'Local logic supply derived from ADC AVCC. LV05.3 is test point only.')
# Supplies and reference; 470uF supports controlled switch-off, not a guarantee under hard shorts.
res('R1','R_FILT','1R',1,S5,A5,'P05',power=True)
add('C1','C_A',SCP,CP,'470u / 16V','EEUFR1C471',{1:A5,2:G},'P05',farads=470e-6,note='Panasonic FR, D8 x 11.5mm, pitch 3.5mm; 20%.')
cap('C2','ADDED_LDO_IN','1u',1e-6,A5,G,'P05');cap('C3','ADDED_LDO_OUT','2.2u',2.2e-6,V,G,'P05')
res('R2','ADDED_LDO_BLEED','1K',1000,V,G,'P05')
for i,pin in enumerate([1,37,38,48,23],4):cap(f'C{i}',f'C_DEC_U1_{pin}','100n',1e-7,V if pin==23 else A5,G,'ADC',small=True)
cap('C9','C_REGCAP_A','1u',1e-6,'REGCAP_A',G,'ADC');cap('C10','C_REGCAP_D','1u',1e-6,'REGCAP_D',G,'ADC')
cap('C11','C_ADC_REF','100n',1e-7,'ADC_REF',G,'ADC',small=True)
cap('C12','ADDED_INTERNAL_REF_BULK','22u',22e-6,'ADC_REF',G,'ADC',large=True)
cap('C13','C_REFCAP','22u',22e-6,'REFCAP',G,'ADC',large=True)
for rr in ['C12','C13']:
 PARTS[rr].update(mpn='C3225X7R1E226M250AB',url='https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=C3225X7R1E226M250AB',note='22uF 25V X7R 20%, 1210. Ceff >=10uF including bias/tolerance/temperature: procurement acceptance, not yet measured.')
for idx,(ref,net) in enumerate([('U2',S5),('U3',S5),('U5',V),('U6',V),('U7',S5),('U8',V),('U9',V),('U10',V),('U11',V)],14):cap(f'C{idx}','C_DEC_'+ref,'100n',1e-7,net,G,'P05')
cap('C23','C_REF_IN','1u',1e-6,S5,G,'READY');cap('C24','C_REF_OUT','1u',1e-6,'REF_2V5',G,'READY')
cap('C25','C_RAIL_LOW','10n',1e-8,'RAIL_LOW',G,'READY');cap('C26','C_RAIL_HIGH','10n',1e-8,'RAIL_HIGH',G,'READY')
for i,(src,val,n,a,b) in enumerate([
 ('R_RAIL_T','15K',15000,A5,'RAIL_SENSE'),('R_RAIL_B','10K',10000,'RAIL_SENSE',G),
 ('R_RAIL_LT','5.90K',5900,'REF_2V5','RAIL_LOW'),('R_RAIL_LB','20K',20000,'RAIL_LOW',G),
 ('R_RAIL_HT','5.23K',5230,'REF_2V5','RAIL_HIGH'),('R_RAIL_HB','24.9K',24900,'RAIL_HIGH',G)],3):res('R'+str(i),src,val,n,a,b,'READY',tol=.001)
for i,(src,a,b) in enumerate([('R_RAIL_PULL','DAQ_RAIL_N',V),('R_U_SUP3','P05_SUP3_N',V),('R_SUP5_RAW','P05_SUP5_RAW',S5),('R_READY_PD','DAQ_OK',G)],9):res('R'+str(i),src,'10K',10000,a,b,'READY')
# Digital defaults on both sides, remove baseline duplicate CS/MEAS pull resistors.
for i,net in enumerate(['ADC_CS','ADC_SCLK','ADC_SDI','ADC_CONVST','ADC_RESET','MEAS_EN'],13):res('R'+str(i),'R_EXT_'+net,'10K',10000,net,V if net=='ADC_CS' else G,'DIG')
for i,net in enumerate(['ADC_CS_P05','ADC_SCLK_P05','ADC_SDI_P05','ADC_CONVST_P05','ADC_RESET_P05','MEAS_EN_P05'],19):res('R'+str(i),'R_LOCAL_'+net,'10K',10000,net,V if net=='ADC_CS_P05' else G,'DIG')
res('R25','ADDED_MEAS_PERMIT_PD','10K',10000,'MEAS_PERMIT',G,'TAPS')
# Outputs: source resistors suppress fast edge ringing on B2B; resistor before bus tri-state stays local.
PARTS['U11']['pins']['3']='DOUT_SER';PARTS['U11']['pins']['6']='BUSY_SER'
res('R26','ADDED_DOUT_DAMP','33R',33,'DOUT_SER','ADC_DOUTA','DIG',smd=True)
res('R27','ADDED_BUSY_DAMP','33R',33,'BUSY_SER','ADC_BUSY','DIG',smd=True)
for i in range(1,4):
 add(f'K{i}',f'KMEAS{i}',symbol('Relay','G6K-2'),RELAY,'G6K-2P-Y DC5','G6K-2P-Y DC5',bp(f'KMEAS{i}'),'TAPS',URL['G6K.pdf'],'THT replacement of same electrical G6K-2F-Y; contacts 3/6 common, 4/5 NO. 5V coil.')
 add(f'D{i}',f'D{i+3}',symbol('Device','D'),DIO,'1N4148','1N4148',{1:S5,2:'MEAS_COIL_LOW'},'TAPS','https://www.vishay.com/docs/81857/1n4148.pdf')
for i in range(1,6):cap(f'C{i+26}',f'CF{i}','220p',220e-12,f'ADC_CH{i}',G,'TAPS')
for r,src,net in [('R28','RB1','ADC_CH1'),('R29','RB2','ADC_CH2')]:res(r,src,'100K',100000,net,G,'TAPS',tol=.001)
res('R30','R_CH6_ZERO','10K',10000,'ADC_CH6',G,'AUX');cap('C32','CI_ADC','1n',1e-9,'ADC_CH6',G,'AUX')
res('R31','RV1','499K',499000,'VPROT_SENSE','ADC_CH7','AUX',tol=.001)
res('R32','RB3','100K',100000,'ADC_CH7',G,'AUX',tol=.001);cap('C33','CF6','220p',220e-12,'ADC_CH7',G,'AUX')
res('R33','RA1','300K',300000,'AUX_HI','ADC_CH8','AUX',tol=.001)
res('R34','RA3','100K',100000,'AUX_LO','ADC_CH8','AUX',tol=.001)
res('R35','RB4','100K',100000,'ADC_CH8','AUX_SHUNT','AUX',tol=.001);cap('C34','CF7','220p',220e-12,'ADC_CH8',G,'AUX')
# AUX range: gold DPDT switch, HI 2-1/5-4, LO 2-3/5-6; software profile selected separately.
sw=symbol('Switch','SW_DPDT_x2','CK7201_DPDT')
add('SW1','JP_AUX',sw,'P05:CK_7201SYCBE','AUX HI / LO','7201SYCBE',{1:'AUX_HI',2:'AUX_IN',3:'AUX_LO',4:G,5:'AUX_SHUNT',6:'NC'},'AUX','https://www.ckswitches.com/media/1394/7000toggle.pdf',note='DPDT gold contacts; manufacturer common 2/5. HI 2-1 + 5-4; LO 2-3 + 5-6. No live switching.')
# Coax solder termination (panel BNC), anchors maintained. No high-frequency ground split.
add('J6','J_AUX',symbol('Connector_Generic','Conn_01x02'),pigtail('PTH_AUX_2',2),'AUX / coax 50mm','insulated panel BNC + RG174 50mm',{1:'AUX_IN',2:G},'AUX',note='Panel BNC shell must connect to circuit GND; not an isolated differential input.')
connectors=[('J1','J_DAQB',16,'P05:DAQ_TSW_NA_2x8','DAQ / B2B','TSW-108-08-G-D-NA'),
 ('J2','J_LV05B',4,pigtail('PTH_LV05_4',4),'LV05 / PTH','harness AWG22'),
 ('J3','J_DAQOKB',6,pigtail('PTH_DAQOK_6',6,True),'DAQOK / PTH','ribbon AWG28'),
 ('J4','J_TAPSB',12,pigtail('PTH_TAPS_12',12),'TAPS / PTH','5 pairs AWG24'),
 ('J5','J_VSENSEB',14,pigtail('PTH_VSENSE_14',14),'VSENSE / PTH','AWG22 pair, only positions 1/2 populated')]
for r,src,n,fp,value,mpn in connectors:
 pp={str(i):B[src]['pins'].get(str(i),'NC') for i in range(1,n+1)}
 add(r,src,symbol('Connector_Generic',f'Conn_01x{n:02d}'),fp,value,mpn,pp,'CON',note='DAQ pin 2 removed. Pigtails soldered into PTH, tie at 11.5..15mm. LV05.3 not tied to local 3V3_DAQ.')
for i,net in enumerate([G,S5,A5,V,'3V3_IO','REF_2V5','RAIL_SENSE','RAIL_LOW','RAIL_HIGH','DAQ_OK','MEAS_PERMIT','AD_BUSY_LOCAL','ADC_REF','REGCAP_A','REGCAP_D','REFCAP'],1):
 add(f'TP{i}','ADDED_TESTPAD',symbol('Connector','TestPoint'),TPFP,net,'PCB test pad',{1:net},'P05')
def write_tables():
 clean={r:{k:v for k,v in v.items() if k!='symbol'} for r,v in PARTS.items()}
 (P/'docs/parts.json').write_text(json.dumps(clean,indent=2,ensure_ascii=False),encoding='utf-8')
 with (P/'docs/BOM.csv').open('w',newline='',encoding='utf-8-sig') as f:
  w=csv.DictWriter(f,['ref','source_ref','display','mpn','qty','footprint','on_board','url','note'],delimiter=';',extrasaction='ignore');w.writeheader();w.writerows(PARTS.values())
 libs={v['symbol'][1]:v['symbol'] for v in PARTS.values()};libs[PRJ+':PWR_FLAG']=symbol('power','PWR_FLAG')
 (P/'eda/libraries/P05.kicad_sym').write_text('(kicad_symbol_lib (version 20231120) (generator "kicad_symbol_editor")'+''.join(dump([s[0],s[1].split(':')[1]]+s[2:]) for s in libs.values())+')',encoding='utf-8')
 (P/'eda/sym-lib-table').write_text('(sym_lib_table (lib (name "P05") (type "KiCad") (uri "${KIPRJMOD}/libraries/P05.kicad_sym") (options "") (descr "P05 local symbols")))')
 flibs=sorted({p['footprint'].split(':')[0] for p in PARTS.values()})
 (P/'eda/fp-lib-table').write_text('(fp_lib_table '+''.join(f'(lib (name "{l}") (type "KiCad") (uri "${{KIPRJMOD}}/libraries/{l}.pretty") (options "") (descr "P05 library"))' for l in flibs)+')')
if __name__=='__main__':write_tables();print('P05',len(PARTS),'parts')
