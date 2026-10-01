"""P05-R3 explicit circuit (format S1). Circuit as P05-R2; connectors to other boards on edge A (J_BP1, J_BP2), service strips on edge B (J_SV1, J_SV2).
R2 header: All connector numbers preserve v6.1 / P03-R1 snapshot.
R2 (review P5-02/P5-05, purchase list 2, P02 R4): R5 6.04K, R7 5.11K, R13 47K; U2 REF5025IDR; CH7 = VBAT_SENSE."""
from cadlib import *
import shutil,csv
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
# R3 (S1 1/4/9): owned THT parts from Zamowione/zamowione.csv where a surplus remains after P02 R4, P09 R2 and P10 R2 (docs/ZAKUPY.md):
# resistors stand upright; everything new is SMD 1206. Exceptions: R1 1 W lying (power), C1 radial electrolytic, C12/C13 1210.
RV=copyfp('Resistor_THT','R_Axial_DIN0207_L6.3mm_D2.5mm_P5.08mm_Vertical')
R1206=copyfp('Resistor_SMD','R_1206_3216Metric_Pad1.30x1.75mm_HandSolder');C1206=copyfp('Capacitor_SMD','C_1206_3216Metric_Pad1.33x1.80mm_HandSolder')
CDISC=copyfp('Capacitor_THT','C_Disc_D5.0mm_W2.5mm_P5.00mm')
RPOWER=copyfp('Resistor_THT','R_Axial_DIN0411_L9.9mm_D3.6mm_P15.24mm_Horizontal')
C1210=copyfp('Capacitor_SMD','C_1210_3225Metric')
QFP=copyfp('Package_QFP','LQFP-64_10x10mm_P0.5mm');SO8=copyfp('Package_SO','SOIC-8_3.9x4.9mm_P1.27mm')
SO14=copyfp('Package_SO','SOIC-14_3.9x8.7mm_P1.27mm');VSSOP8=copyfp('Package_SO','VSSOP-8_3x3mm_P0.65mm')
DIP14=copyfp('Package_DIP','DIP-14_W7.62mm');DIP18=copyfp('Package_DIP','DIP-18_W7.62mm')
TO92=copyfp('Package_TO_SOT_THT','TO-92_Inline_Wide');DIO=copyfp('Diode_THT','D_DO-35_SOD27_P7.62mm_Horizontal')
CP63=copyfp('Capacitor_THT','CP_Radial_D6.3mm_P2.50mm');RELAY=copyfp('Relay_THT','Relay_DPDT_Omron_G6K-2P-Y')
TPFP=localfp('TestPad_1')
SR=symbol('Device','R');SC=symbol('Device','C');SCP=symbol('Device','C_Polarized')
REG='rejestr';NEW='nowe'
def add(ref,src,sym,fp,value,mpn,pins,sheet,url='',note='',zrodlo=NEW,**extra):
 PARTS[ref]=dict(ref=ref,source_ref=src,symbol=sym,footprint=fp,display=value,value=value,mpn=mpn,pins={str(k):v for k,v in pins.items()},sheet=sheet,url=url,note=note,qty=1,on_board=True,zrodlo=zrodlo,**extra)
# Owned MF0207 (register 24.09: 47K x6, 4.7K x6; P01 is obsolete, P09 R2/P10 R2 use only 10K/100K).
OWNED_R={'47K':'MF0207FTE-47K','4.7K':'MF0207FTE-4K7'}
def res(ref,src,value,ohms,a,b,sheet,tol=.01,smd=False,power=False,tcr=None):
 # tol 0.1 %: thin-film 1206. Window divider (tcr=10): Yageo RT1206BRB07 (0.1 %, 10 ppm/K); channel dividers (tcr=25): RT1206BRD07 (0.1 %, 25 ppm/K).
 code=value.replace('.','K',1)[:-1] if value.endswith('K') and '.' in value else value
 if power:add(ref,src,SR,RPOWER,value,'KNP01U-1R (1R 1W wirewound, body 3x9mm)',{1:a,2:b},sheet,note='1W minimum, lying (S1 1: power part); pulse energy at turn-on ~2.8mJ (220uF x 5V, 1.10; was ~6mJ with 470uF): pulse rating to be confirmed from the data sheet.',ohms=ohms,tolerance=tol)
 elif tol==.001:
  tcr=tcr or 25;mpn=('RT1206BRB07' if tcr==10 else 'RT1206BRD07')+code+'L'
  add(ref,src,SR,R1206,value,mpn,{1:a,2:b},sheet,note=f'Thin film 1206, 0.1 %, {tcr} ppm/K (MPN proposal, data sheet/TME to confirm). One full-value resistor.',ohms=ohms,tolerance=tol,tcr_ppm=tcr)
 elif value in OWNED_R:add(ref,src,SR,RV,value,OWNED_R[value]+' (Yageo MF0207 1% 0.6W, owned, standing)',{1:a,2:b},sheet,zrodlo=REG,ohms=ohms,tolerance=tol)
 else:add(ref,src,SR,R1206,value,'RC1206FR-07'+code+'L',{1:a,2:b},sheet,ohms=ohms,tolerance=tol)
# Owned capacitors used where electrically fine (not at AD7606B pins): KEMET C0G 1n. 1.10 (local review): P02 R4 (merged, ordered) also
# draws on the P01 film stock (B32529 10n x1, 100n x2, MKS2 1u x1), so one piece of each is left against 2-3 needed here: C2, C23,
# C16-C18, C25 and C26 are new SMD 1206 like the rest (the cloud task named only P09/P10 for the balance).
OWNED_C={'C32':(CDISC,'C320C102J1G5TA (KEMET C0G 1n, owned; lead pitch to check on the 1:1 print)')}
def cap(ref,src,value,farads,a,b,sheet,large=False,small=False):
 if ref in OWNED_C:fp,mpn=OWNED_C[ref];add(ref,src,SC,fp,value,mpn,{1:a,2:b},sheet,zrodlo=REG,farads=farads);return
 add(ref,src,SC,C1210 if large else C1206,value,('SMD 1206 C0G 50V 5% ' if farads<1e-9 else 'SMD 1206 X7R 25V 10% ')+value,{1:a,2:b},sheet,farads=farads,note='1210 exception: effective capacitance >=10uF at 4.4V (1206 22u does not reach it reliably)' if large else '')
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
# R2: ADR4525BRZ unavailable until 2027 -> TI REF50xx, same SOIC-8 use: 2 VIN, 4 GND, 6 VOUT; 1/8 DNC, 3 TEMP,
# 5 TRIM/NR and 7 NC stay open. HIGH grade (REF5025IDR: 0.05 %, 3 ppm/K) is required by the window budget;
# the standard grade REF5025AIDR (0.1 %, 8 ppm/K) moves the low corner below 4.75 V (verify_electrical.py).
u2={str(i):'NC' for i in range(1,9)};u2.update({'2':S5,'4':G,'6':'REF_2V5'})
add('U2','U13',symbol('Reference_Voltage','REF5025AD'),SO8,'REF5025IDR','REF5025IDR',u2,'READY','https://www.ti.com/lit/ds/symlink/ref5025.pdf','Reference for rail window only; NOT ADC reference. High grade REF5025IDR (0.05 %, 3 ppm/K); REF5025AIDR is NOT equivalent. C24 1uF output (REF50xx: 1..50uF required).')
cmp=custom('TLV1702AQDGKRQ1',[([(3,'+A','input'),(2,'-A','input')],[(1,'OUT_A','open_collector')]), ([(5,'+B','input'),(6,'-B','input')],[(7,'OUT_B','open_collector')]), ([(8,'VCC','power_in')],[(4,'GND','power_in')])])
add('U3','U6',cmp,VSSOP8,'TLV1702-Q1','TLV1702AQDGKRQ1',bp('U6'),'READY',URL['TLV1702-Q1.pdf'])
drv=custom('TBD62083APG',[( [(i,'IN'+str(i),'input') for i in range(1,9)]+[(9,'GND','power_in')],[(19-i,'OUT'+str(i),'open_collector') for i in range(1,9)]+[(10,'COM','passive')])])
dp=bp('U18');dp['1']='MEAS_PERMIT';dp['10']=S5
add('U4','U18',drv,DIP18,'TBD62083APG','TBD62083APG',dp,'TAPS','https://toshiba.semicon-storage.com/us/semiconductor/product/linear-ics/transistor-arrays/detail.TBD62083APG.html','COM to coil supply. Inputs 2..8 tied low. Local diodes at coils.')
hp=bp('U_READY');hp.update({'9':'MEAS_EN_P05','10':'DAQ_OK','8':'MEAS_PERMIT'})
add('U5','U_READY',symbol('74xx','74LS08','SN74HC08N'),DIP14,'SN74HC08N','SN74HC08N',hp,'READY','https://www.ti.com/lit/ds/symlink/sn74hc08.pdf','DIP14 in the owned precision socket (Kamami 648).',zrodlo=REG)
sup=custom('MCP120_D_TO',[([(2,'VDD','power_in')],[(1,'RESET_N','open_collector'),(3,'VSS','power_in')])])
for r,src,mpn in [('U6','U_SUP3','MCP120-300DI/TO'),('U7','U_SUP5','MCP120-450DI/TO')]:add(r,src,sup,TO92,mpn,mpn,bp(src),'READY',URL['MCP120.pdf'],'D bondout 1 reset, 2 VDD, 3 GND. Open drain.',zrodlo=REG)
lvc=symbol('74xx','74LVC125','74LVC125AD')
for ref,src,sh in [('U8','U_SUPBUF','READY'),('U9','U_RX1','DIG'),('U10','U_RX2','DIG'),('U11','U_TX','DIG')]:
 pp=bp(src)
 if ref=='U11':pp.update({'4':G,'5':'AD_BUSY_LOCAL','6':'ADC_BUSY'})
 add(ref,src,lvc,SO14,'74LVC125AD','74LVC125AD,118',pp,sh,URL['LVC125.pdf'],'Nexperia Ioff, soldered directly; no adapter.',zrodlo=REG)
add('U12','ADDED_LOCAL_LDO',symbol('Regulator_Linear','MCP1700x-330xxTO'),TO92,'MCP1700-3302E/TO','MCP1700-3302E/TO',{1:G,2:A5,3:V},'P05',URL['MCP1700.pdf'],'Local logic supply derived from ADC AVCC. R3: 3V3_IO does not enter P05.')
# Supplies and reference; C1 (220uF since 1.10) supports controlled switch-off, not a guarantee under hard shorts.
res('R1','R_FILT','1R',1,S5,A5,'P05',power=True)
add('C1','C_A',SCP,CP63,'220u / 16V','EEUFR1C221',{1:A5,2:G},'P05',farads=220e-6,note='Panasonic FR, D6.3 x 11.2mm, pitch 2.5mm; 20%. 1.10 user decision: 220uF (was 470uF) - with P06 C3 the 5V_SYS load stays under the 600uF of the TSR 2-2450 (about 486uF in all). MPN/size to confirm.')
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
 ('R_RAIL_LT','6.04K',6040,'REF_2V5','RAIL_LOW'),('R_RAIL_LB','20K',20000,'RAIL_LOW',G),
 ('R_RAIL_HT','5.11K',5110,'REF_2V5','RAIL_HIGH'),('R_RAIL_HB','24.9K',24900,'RAIL_HIGH',G)],3):res('R'+str(i),src,val,n,a,b,'READY',tol=.001,tcr=10)
for i,(src,a,b) in enumerate([('R_RAIL_PULL','DAQ_RAIL_N',V),('R_U_SUP3','P05_SUP3_N',V),('R_SUP5_RAW','P05_SUP5_RAW',S5),('R_READY_PD','DAQ_OK',G)],9):res('R'+str(i),src,'10K',10000,a,b,'READY')
# Digital defaults on both sides, remove baseline duplicate CS/MEAS pull resistors.
# R2 (P5-05): R13 47K keeps the back-feed into an unpowered 3V3_DAQ through R13/R2 at ~0.07 V (10K: 0.30 V).
for i,net in enumerate(['ADC_CS','ADC_SCLK','ADC_SDI','ADC_CONVST','ADC_RESET','MEAS_EN'],13):res('R'+str(i),'R_EXT_'+net,'47K' if i==13 else '10K',47000 if i==13 else 10000,net,V if net=='ADC_CS' else G,'DIG')
for i,net in enumerate(['ADC_CS_P05','ADC_SCLK_P05','ADC_SDI_P05','ADC_CONVST_P05','ADC_RESET_P05','MEAS_EN_P05'],19):res('R'+str(i),'R_LOCAL_'+net,'10K',10000,net,V if net=='ADC_CS_P05' else G,'DIG')
res('R25','ADDED_MEAS_PERMIT_PD','10K',10000,'MEAS_PERMIT',G,'TAPS')
# Outputs: source resistors suppress fast edge ringing on B2B; resistor before bus tri-state stays local.
PARTS['U11']['pins']['3']='DOUT_SER';PARTS['U11']['pins']['6']='BUSY_SER'
res('R26','ADDED_DOUT_DAMP','33R',33,'DOUT_SER','ADC_DOUTA','DIG',smd=True)
res('R27','ADDED_BUSY_DAMP','33R',33,'BUSY_SER','ADC_BUSY','DIG',smd=True)
for i in range(1,4):
 add(f'K{i}',f'KMEAS{i}',symbol('Relay','G6K-2'),RELAY,'G6K-2P-Y DC5','G6K-2P-Y DC5',bp(f'KMEAS{i}'),'TAPS',URL['G6K.pdf'],'THT replacement of same electrical G6K-2F-Y; contacts 3/6 common, 4/5 NO. 5V coil.')
 add(f'D{i}',f'D{i+3}',symbol('Device','D'),DIO,'1N4148','1N4148',{1:S5,2:'MEAS_COIL_LOW'},'TAPS','https://www.vishay.com/docs/81857/1n4148.pdf',zrodlo=REG)
for i in range(1,6):cap(f'C{i+26}',f'CF{i}','220p',220e-12,f'ADC_CH{i}',G,'TAPS')
for r,src,net in [('R28','RB1','ADC_CH1'),('R29','RB2','ADC_CH2')]:res(r,src,'100K',100000,net,G,'TAPS',tol=.001)
res('R30','R_CH6_ZERO','10K',10000,'ADC_CH6',G,'AUX');cap('C32','CI_ADC','1n',1e-9,'ADC_CH6',G,'AUX')
res('R31','RV1','499K',499000,'VBAT_SENSE','ADC_CH7','AUX',tol=.001)  # R2: car battery via P02 R4 J11.1 (10K + P6KE24CA)
res('R32','RB3','100K',100000,'ADC_CH7',G,'AUX',tol=.001);cap('C33','CF6','220p',220e-12,'ADC_CH7',G,'AUX')
res('R33','RA1','300K',300000,'AUX_HI','ADC_CH8','AUX',tol=.001)
res('R34','RA3','100K',100000,'AUX_LO','ADC_CH8','AUX',tol=.001)
res('R35','RB4','100K',100000,'ADC_CH8','AUX_SHUNT','AUX',tol=.001);cap('C34','CF7','220p',220e-12,'ADC_CH8',G,'AUX')
# AUX range: 1.10.2026 user decision - E-Switch 100 series in the right-angle version (M6) instead of the vertical 100DP1T1B1M2REH (~28 mm,
# over the 16.5 mm of level 3; the cloud session had proposed the C&K JS202011AQN slide). DPDT ON-NONE-ON (DP1), gold contacts (R), epoxy
# seal; exact order code (bushing B3/B4) to confirm with E-Switch / Mouser. Contacts as R2 (data sheet p. 2): commons 2 / 5, position 3 =
# 2-1 + 5-4 (HI: shunt R35 to GND), position 1 = 2-3 + 5-6 (LO, pin 6 open). Footprint from the M6-DP drawing (p. 11), reference/E-Switch-100-series.pdf.
sw=custom('SW_DPDT_ESW100',[([(2,'COM_A','passive')],[(1,'A_HI','passive'),(3,'A_LO','passive')]),([(5,'COM_B','passive')],[(4,'B_HI','passive'),(6,'B_LO','passive')])])
add('SW1','JP_AUX',sw,localfp('ESW_100DP_M6'),'AUX HI / LO','100DP1T1B4M6RE (E-Switch 100, DPDT ON-ON, M6 right angle, gold; code to confirm)',{1:'AUX_HI',2:'AUX_IN',3:'AUX_LO',4:G,5:'AUX_SHUNT',6:'NC'},'AUX','https://www.e-switch.com/product/100-series-miniature-toggle-switch/',note='E-Switch 100 DP M6: lever through the panel at x = 0; HI = 2-1 + 5-4 (shunt R35 to GND), LO = 2-3 + 5-6 (pin 6 open). Positions to label after the ohmmeter check (ODBIOR 13). No live switching.')
# Coax solder termination (panel BNC), anchors maintained. No high-frequency ground split.
add('J6','J_AUX',symbol('Connector_Generic','Conn_01x02'),pigtail('PTH_AUX_2',2),'AUX / coax 50mm','insulated panel BNC + RG174 50mm',{1:'AUX_IN',2:G},'AUX',note='Panel BNC shell must connect to circuit GND; not an isolated differential input.')
# R3 (format S1, decision 1.10.2026 variant B): J1 B2B DAQ, J2 LV05, J3 DAQOK and J5 VSENSE are replaced by two angled
# shrouded IDC headers on edge A. Nets and functions unchanged; 3V3_IO no longer enters P05 (LV05.3 was a test point only).
# J_BP2 (slot S2): DAQ bus on the SAME pin numbers as P03 R6 J_BP2 (reference/P03-R6-J_BP.csv), so P12 tracks go straight up.
JBP2={2:'ADC_SCLK',4:'ADC_DOUTA',6:'ADC_SDI',8:'ADC_CS',10:'ADC_CONVST',12:'ADC_BUSY',14:'MEAS_EN',16:G,18:'ADC_RESET',20:G}
JBP1={2:S5,4:S5,6:'DAQ_OK',8:G,10:'VBAT_SENSE'}
for jj in (JBP1,JBP2):jj.update({i:G for i in range(1,max(jj)+1,2)})
IDC10=copyfp('Connector_IDC','IDC-Header_2x05_P2.54mm_Horizontal');IDC20=copyfp('Connector_IDC','IDC-Header_2x10_P2.54mm_Horizontal')
add('J_BP1','J_DAQOKB+J_VSENSEB+J_LV05B',symbol('Connector_Generic','Conn_02x05_Odd_Even'),IDC10,'J_BP1 / IDC 2x5','IDC header 2x5 2.54mm angled shrouded, Au',JBP1,'ZLACZA',note='Edge A, slot S1 (centre x=26.5 mm), pin 1 towards smaller x. Odd pins GND; 5V_SYS x2 (S1 5), DAQ_OK (to P04, no consumer in LOGGER), pin 8 GND reserve separating VBAT_SENSE.')
add('J_BP2','J_DAQB',symbol('Connector_Generic','Conn_02x10_Odd_Even'),IDC20,'J_BP2 / IDC 2x10','IDC header 2x10 2.54mm angled shrouded, Au',JBP2,'ZLACZA',note='Edge A, slot S2 (centre x=80.0 mm), pin 1 towards smaller x. DAQ pins = P03 R6 J_BP2; 16 and 20 GND reserve (P03: PFAIL_N, 5V_SYS - P12 must not join them).')
add('J4','J_TAPSB',symbol('Connector_Generic','Conn_01x12'),pigtail('PTH_TAPS_12',12),'TAPS / PTH','5 pairs AWG24',{str(i):B['J_TAPSB']['pins'].get(str(i),'NC') for i in range(1,13)},'ZLACZA',note='Wire, not P12 (S1 5): pairs from P11 soldered into PTH at the x=0 board edge, tie at 11.5..15mm.')
# Service strips on edge B (S1 6): angled goldpin, GND first and last, every other pin through a series resistor placed at the node.
# 1K rails/logic, 4.7K pack-level VBAT_SENSE (to ~16 V), 10K high-impedance nodes (reference, dividers, open-drain pulled nodes).
SV1=[(S5,1000,'5V_SYS na P05 (krok 3: 4,93-5,07 V przy ok. 23 C)'),(A5,1000,'5VA_P05 za R1 (spadek 12-20 mV)'),(V,1000,'3V3_DAQ z U12 (3,20-3,40 V; krok 7: ok. 0,07 V przy wylaczonym P05)'),
 ('REF_2V5',10000,'REF5025 (U2) dla okna DAQ_OK'),('RAIL_SENSE',10000,'dzielnik 5VA R3/R4 na wejsciach U3'),('RAIL_LOW',10000,'prog dolny okna (R5/R6, C25)'),('RAIL_HIGH',10000,'prog gorny okna (R7/R8, C26)'),
 ('VBAT_SENSE',4700,'akumulator auta z P02 R4 (do ok. 16 V), wejscie dzielnika CH7'),('MEAS_COIL_LOW',1000,'U4.18: VDS przy trzech cewkach <= 0,3 V (krok 10b)')]
SV2=[('ADC_CS',1000,'CS po stronie J_BP (start: 1)'),('ADC_CONVST',1000,'CONVST po stronie J_BP (start: 0)'),('ADC_BUSY',1000,'BUSY za U11B/R27'),('ADC_DOUTA',1000,'wspolne MISO za R26: stan Z przy CS=1 (krok 9)'),
 ('ADC_RESET',1000,'RESET po stronie J_BP (start: 0)'),('MEAS_EN',1000,'MEAS_EN po stronie J_BP (start: 0)'),('MEAS_PERMIT',1000,'zgoda na cewki = MEAS_EN i DAQ_OK'),('DAQ_OK',1000,'wyjscie U5B (U5.6) do J_BP1.6'),
 ('DAQ_RAIL_N',10000,'wyjscie okna U3 (OD, 10k R9)'),('P05_SUP3_N',10000,'nadzorca 3V3_DAQ U6 (OD, 10k R10)'),('P05_SUP5_N',1000,'nadzorca 5V_SYS za buforem U8')]
# 1.10 (local review, rule decided for P03 R6): a rail pin only next to GND or another rail, so a slipped probe cannot drive an analog or
# logic node from a rail through 2 kOhm; VBAT_SENSE (pack, to ~16 V) between two GND pins and away from 3V3_DAQ (with P05 unpowered it
# would back-feed VDRIVE). J_SV1 pins given explicitly with interior GND on 3 and 7; the rows keep their order, so R36-R44 keep their nodes.
SV1_PIN={'VBAT_SENSE':2,S5:4,A5:5,V:6,'REF_2V5':8,'RAIL_SENSE':9,'RAIL_LOW':10,'RAIL_HIGH':11,'MEAS_COIL_LOW':12}
SERVICE={};nr=36
for jref,rows,src,pin_of in [('J_SV1',SV1,'SERVICE_S1',SV1_PIN),('J_SV2',SV2,'SERVICE_S2',{})]:
 n=max(pin_of.values())+1 if pin_of else len(rows)+2;pp={k:G for k in range(1,n+1)}
 for k,(net,ohm,why) in enumerate(rows,2):
  k=pin_of.get(net,k);r='R'+str(nr);nr+=1;pp[k]='SRV_'+net;SERVICE[net]=(jref,k,r,ohm,why)
  res(r,'ADDED_'+src,{1000:'1K',4700:'4.7K',10000:'10K'}[ohm],ohm,net,'SRV_'+net,'SERWIS',smd=True)
  PARTS[r]['note']='Service pin series resistor at the node (S1 6): slipped probe cannot damage anything.'
 add(jref,src,symbol('Connector_Generic',f'Conn_01x{n:02d}'),copyfp('Connector_PinHeader_2.54mm',f'PinHeader_1x{n:02d}_P2.54mm_Horizontal'),f'{jref} SERWIS 1x{n}',f'Pin header 1x{n}, 2.54 mm, right angle, Au',pp,'SERWIS',note='Edge B, x=10..43 mm of the slot ('+('S1' if jref=='J_SV1' else 'S2')+'); pins ~6 mm beyond the edge. Numbering always from pin 1 (angled strip seen from the top has pin 1 at LARGER x).')
# Local test pads kept only for the ADC reference/regulator nodes (bench step 11, before stacking): a 10K stub to edge B
# would carry noise into the AD7606B reference. GND pad for the probe ground next to them.
for i,net in enumerate([G,'ADC_REF','REGCAP_A','REGCAP_D','REFCAP'],1):
 add(f'TP{i}','ADDED_TESTPAD',symbol('Connector','TestPoint'),TPFP,net,'PCB test pad',{1:net},'SERV')
def write_tables():
 clean={r:{k:v for k,v in v.items() if k!='symbol'} for r,v in PARTS.items()}
 (P/'docs/parts.json').write_text(json.dumps(clean,indent=2,ensure_ascii=False),encoding='utf-8')
 with (P/'docs/BOM.csv').open('w',newline='',encoding='utf-8-sig') as f:
  w=csv.DictWriter(f,['ref','source_ref','display','mpn','qty','footprint','on_board','zrodlo','url','note'],delimiter=';',extrasaction='ignore');w.writeheader();w.writerows(PARTS.values())
 libs={v['symbol'][1]:v['symbol'] for v in PARTS.values()};libs[PRJ+':PWR_FLAG']=symbol('power','PWR_FLAG')
 (P/'eda/libraries/P05.kicad_sym').write_text('(kicad_symbol_lib (version 20231120) (generator "kicad_symbol_editor")'+''.join(dump([s[0],s[1].split(':')[1]]+s[2:]) for s in libs.values())+')',encoding='utf-8')
 (P/'eda/sym-lib-table').write_text('(sym_lib_table (lib (name "P05") (type "KiCad") (uri "${KIPRJMOD}/libraries/P05.kicad_sym") (options "") (descr "P05 local symbols")))')
 flibs=sorted({p['footprint'].split(':')[0] for p in PARTS.values()})
 (P/'eda/fp-lib-table').write_text('(fp_lib_table '+''.join(f'(lib (name "{l}") (type "KiCad") (uri "${{KIPRJMOD}}/libraries/{l}.pretty") (options "") (descr "P05 library"))' for l in flibs)+')')
if __name__=='__main__':write_tables();print('P05',len(PARTS),'parts')
