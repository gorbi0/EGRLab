"""P04-R3 explicit circuit (format S1, class L, level 6). Circuit as P04-R2.2 (closed package Plytki/P04-R2.2-review, R1 by Astra +
review changes R4-01..R4-07, R17 10k in R2.2). Changed in R3 (task Plytki/Format-S1/zadania/ZADANIE-P04-S1.md, decisions 5.10.2026):
connectors to other boards on edge A (J_BP1..J_BP3, angled shrouded IDC via P12), service strips on edge B (J_SV1..J_SV3 with series
resistors at the node) instead of TP1..TP15, part types per S1 (owned THT where the register has a surplus, new R/C as SMD 1206),
74LVC125AD soldered directly (SOIC-14) instead of Kamami adapters. Two nets renamed to the P12 names: SUP_N -> SUP_N_OUT (P03 R6
J_BP3.12), PG_3V3 -> P04_3V3 (P02 R4 J_BP.15). Never infer electrical wiring from placement or rendered graphics."""
from cadlib import *
import shutil,csv,hashlib
FP=P/'eda/libraries/P04.pretty';FP.mkdir(parents=True,exist_ok=True)
PARTS={}
URL={
 'hc123':'https://www.ti.com/lit/ds/symlink/cd74hc123.pdf',
 'hc14':'https://www.ti.com/lit/ds/symlink/sn74hc14.pdf',
 'hc74':'https://www.ti.com/lit/ds/symlink/sn74hc74.pdf',
 'hc08':'https://www.ti.com/lit/ds/symlink/sn74hc08.pdf',
 'lvc125':'https://assets.nexperia.com/documents/data-sheet/74LVC125A.pdf',
 'mcp100':'https://ww1.microchip.com/downloads/en/DeviceDoc/11187f.pdf',
 'npn':'https://www.onsemi.com/pdf/datasheet/2n3903-d.pdf',
 'res':'https://www.yageo.com/upload/media/product/productsearch/datasheet/rchip/PYu-RC_Group_51_RoHS_L_12.pdf',
 'film':'https://www.wima.de/wp-content/uploads/media/e_WIMA_MKS_2.pdf',
 'cer':'https://www.kemet.com/content/dam/kemet/lightning/documents/ec-content/datasheets/KEM_C1002_X7R_SMD.pdf',
 'c0g':'https://www.kemet.com/content/dam/kemet/lightning/documents/ec-content/datasheets/KEM_C1015_GOLDMAX_300_C0G.pdf'}
REG='rejestr';NEW='nowe'
def copyfp(lib,name):
 src=K/'footprints'/(lib+'.pretty')/(name+'.kicad_mod');assert src.exists(),src
 dest=P/'eda/libraries'/(lib+'.pretty');dest.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest/src.name)
 return lib+':'+name
def localfp(name):
 src=P/'input/footprints'/(name+'.kicad_mod')
 assert hashlib.sha256(src.read_bytes()).hexdigest()==json.loads((P/'input/footprints-sha256.json').read_text())[src.name]
 shutil.copy2(src,FP/src.name);return 'P04:'+name
# S1 1/9: new resistors and ceramic capacitors SMD 1206; owned THT only where the register keeps a surplus after P02 R4, P03 R6, P05 R3,
# P06 R2, P09 R2, P10 R2 (docs/ZAKUPY.md): C1 WIMA MKS2 1u/100V, C3 EEU-EB1J100SH, C18 C320C102J1G5TA. No owned resistor value fits.
R1206=copyfp('Resistor_SMD','R_1206_3216Metric_Pad1.30x1.75mm_HandSolder');C1206=copyfp('Capacitor_SMD','C_1206_3216Metric_Pad1.33x1.80mm_HandSolder')
MKS2_100V=localfp('C_WIMA_MKS2_1u100V_L7.2_W7.2_P5')   # from P02 R4 (owned part, body 7.2 x 7.2 mm)
CFILM=copyfp('Capacitor_THT','C_Rect_L7.2mm_W5.0mm_P5.00mm')
CDISC=copyfp('Capacitor_THT','C_Disc_D5.0mm_W2.5mm_P5.00mm')   # as P05 R3 C32 (same owned KEMET part)
DIP14=copyfp('Package_DIP','DIP-14_W7.62mm');DIP16=copyfp('Package_DIP','DIP-16_W7.62mm')
SO14=copyfp('Package_SO','SOIC-14_3.9x8.7mm_P1.27mm')
TO92=copyfp('Package_TO_SOT_THT','TO-92_Inline_Wide')
CP5=copyfp('Capacitor_THT','CP_Radial_D5.0mm_P2.00mm')
LED=copyfp('LED_THT','LED_D3.0mm')
S_R=symbol('Device','R');S_C=symbol('Device','C');S_CP=symbol('Device','C_Polarized')
S_HC123=symbol('74xx','74HC123','CD74HC123E');S_HC14=symbol('74xx','74HC14','SN74HC14N')
S_HC74=symbol('74xx','74HC74','SN74HC74N');S_HC08=symbol('74xx','74LS08','SN74HC08N')
S_LVC=symbol('74xx','74LVC125','74LVC125AD');S_SUP=symbol('Power_Supervisor','MCP100-300D','MCP100-300DI_TO')
S_NPN=symbol('Transistor_BJT','2N3904');S_LED=symbol('Device','LED')
def add(ref,src,sym,fp,value,mpn,pins,sheet,url='',note='',on_board=True,zrodlo=NEW,**extra):
 PARTS[ref]={'ref':ref,'source_ref':src,'symbol':sym,'footprint':fp,'display':value,'value':value,'mpn':mpn,
 'pins':{str(k):v for k,v in pins.items()},'sheet':sheet,'url':url,'note':note,'qty':1,'on_board':on_board,'zrodlo':zrodlo,**extra}
def res(ref,src,v,a,b,sheet,note=''):
 add(ref,src,S_R,R1206,v+' / 1%','RC1206FR-07'+v+'L',{1:a,2:b},sheet,URL['res'],note)
def cap(ref,src,v,a,b,sheet,note='100nF local decoupling'):
 add(ref,src,S_C,C1206,v,'SMD 1206 X7R 50V 10% 100n',{1:a,2:b},sheet,URL['cer'],note)
V='3V3_IO';G='GND'
# Watchdog, reset conditioning, manual edge latch.
add('U1','U7',S_HC123,DIP16,'CD74HC123E','CD74HC123E',{1:G,2:'HEARTBEAT_P04',3:'SUP_OK',4:'NC',5:'NC',6:'NC',7:'NC',8:G,9:G,10:G,11:G,12:'NC',13:'WD_Q',14:'WD_C',15:'WD_RC',16:V},'WD',URL['hc123'])
add('U2','U8',S_HC14,DIP14,'SN74HC14N','SN74HC14N',{1:'WD_Q',2:'WD_BAD',3:'ARM_BUTTON_N',4:'ARM_CLK',5:'SUP_OK',6:'SUP_BAD',7:G,8:'ILK_BAD',9:'INTERLOCK',10:'SAFE_OK_N',11:'SAFE_N',12:'SAFE_OK',13:'SAFE_OK_N',14:V},'WD',URL['hc14'],'Two spare Schmitt gates regenerate SAFE_N before HC74 CLR and permit logic.')
add('U3','U9',S_HC74,DIP14,'SN74HC74N','SN74HC74N',{1:'SAFE_WD',2:V,3:'ARM_CLK',4:V,5:'HW_ARMED',6:'NC',7:G,8:'NC',9:'NC',10:V,11:G,12:G,13:G,14:V},'WD',URL['hc74'])
def gates(ref,src,gs,sheet):
 pins={7:G,14:V}
 for (a,b,y),(na,nb,ny) in zip([(1,2,3),(4,5,6),(9,10,8),(12,13,11)],gs):pins.update({a:na,b:nb,y:ny})
 add(ref,src,S_HC08,DIP14,'SN74HC08N','SN74HC08N',pins,sheet,URL['hc08'])
gates('U4','U10',[
 ('HW_ARMED','MCU_ARM_P04','ARM_BOTH'),('ARM_BOTH','INTERLOCK','MOTOR_REQ'),('PWM_P04','MOTOR_PERMIT','PWM_OUT'),('SENSOR_ENABLE_P04','TEST_KEY_P04','SENSOR_KEY')],'OUT')
gates('U5','U12',[
 ('SENSOR_KEY','INTERLOCK','SENSOR_INTERLOCK'),('SENSOR_INTERLOCK','SAFE_WD','SENSOR_PERMIT'),('SUP_N_P04','LOCAL_SUP_N','SUP_OK'),('MOTOR_REQ','SAFE_WD','MOTOR_PERMIT')],'OUT')
gates('U6','U_LINK',[
 ('PSU_OK_P04','DAQ_OK_P04','OK_A'),('DRIVE_OK_P04','SENSOR_OK_P04','OK_B'),('CORE_LINK_P04','PG_LINK_P04','OK_C'),('OK_A','OK_B','OK_AB')],'ILK')
gates('U7','U_LINK2',[
 ('OK_AB','OK_C','MODULES_OK'),('MODULES_OK','MECH_KEY','INTERLOCK'),('MECH_OK_P04','TEST_KEY_P04','MECH_KEY'),('SAFE_OK','WD_Q','SAFE_WD')],'ILK')
groups=[['PWM','HEARTBEAT','MCU_ARM','SENSOR_ENABLE'],['CORE_LINK','SUP_N','PSU_OK','DAQ_OK'],['DRIVE_OK','SENSOR_OK','PG_LINK',None]]
signals=[]
for i,group in enumerate(groups,8):
 pins={7:G,14:V}
 for signal,(oe,a,y) in zip(group,[(1,2,3),(4,5,6),(10,9,8),(13,12,11)]):
  pins.update({oe:G if signal else V,a:signal or G,y:signal+'_P04' if signal else 'NC'})
  if signal:signals.append(signal)
 add(f'U{i}',f'U_RX{i-7}',S_LVC,SO14,'74LVC125AD','74LVC125AD,118 (Nexperia)',pins,'RX',URL['lvc125'],'Owned (register, P04 allocation). R3: SOIC-14 soldered directly on the factory PCB (S1 9), top side; the three Kamami adapters stay unused. Ioff required: never HC125.',zrodlo=REG)
add('U11','ADDED_LOCAL_SUPERVISOR',S_SUP,TO92,'MCP100-300DI/TO','MCP100-300DI/TO',{1:'LOCAL_SUP_N',2:V,3:G},'P04',URL['mcp100'],'D bondout: 1=/RESET, 2=VDD, 3=VSS. Do not substitute H variant. 2.85..3.00V trip, reset delay 150..700 ms (MCP1X0 -300). R2 replaces -315 to improve supply margin (review R4-01). Release estimates use 50 mV TYP hysteresis, not a guaranteed maximum; verify at minimum supply.')
res('R1','R_WD','220K',V,'WD_RC','WD')
res('R2','R_ARM_PU','10K',V,'ARM_BUTTON_N','WD')
res('R3','R_ARM_SER','1K','ARM_BUTTON_N','ARM_CONTACT','WD','Was 100R; with C2=1u gives about 10ms release RC and limits discharge current.')
res('R4','R_SAFE_PU','10K','STOP_NC_OUT','SAFE_N','WD','Only pull-up of the shared SAFE_N net; supply through physical STOP NC.')
res('R5','R_SAFE_PD','100K','SAFE_N',G,'WD')
for i,n in enumerate(['WD_BAD','SUP_BAD','ILK_BAD'],1):
 res(f'R{i+5}',f'ADDED_Q{i}_BASE','10K',n,f'Q{i}_B','WD')
 res(f'R{i+8}',f'Q{i}_PD','100K',f'Q{i}_B',G,'WD')
 add(f'Q{i}',['Q8','Q9','Q10'][i-1],S_NPN,TO92,'2N3904','2N3904BU',{1:G,2:f'Q{i}_B',3:'SAFE_N'},'WD',URL['npn'],'Open collector sink replaces SOT23 2N7002. TO92 pins 1 E,2 B,3 C; 10k series base resistor.')
for i,s in enumerate(signals,12):res(f'R{i}','R_EXT_'+s,'10K',s,G,'RX','Connector-side default LOW.')
res('R23','R_PD_TEST_KEY','10K','TEST_KEY_P04',G,'ILK','Gate side of R41: an open R41 leaves the gate LOW.')
res('R24','R_LINK_MECH_OK','10K','MECH_OK_P04',G,'ILK','One 10k replaces the two parallel 10k in v6.1; gate side of R42.')
for i,s in enumerate(signals,25):
 v='47K' if s in ['HEARTBEAT','MCU_ARM'] else ('100K' if s in ['SUP_N','SENSOR_ENABLE'] else '10K')
 res(f'R{i}','R_LOCAL_'+s,v,s+'_P04',G,'RX','Default LOW after removable adapter; no floating gate if adapter absent.')
res('R36','R_LINK_INTERLOCK','10K','INTERLOCK',G,'ILK')
res('R37','ADDED_POWER_LED','1K',V,'LED_PWR','P04')
res('R38','W_SEND','1K',V,'PG_SEND','ZLACZA','R2: was 0R. Limits a PG_SEND short in the PG harness to 3.3 mA; PG_LINK = 3.0 V with R22 10k (P01 loop R34 0R).')
res('R39','ADDED_PG_3V3_LIMIT','1K',V,'P04_3V3','ZLACZA','R2 (R4-03): 3V3_IO to the PG open collector (R3: P02 R4 Q7 via J_BP2.14 -> P12 -> P02 J_BP.15; R2.2: P01 J7.1) through 1k; net renamed PG_3V3 -> P04_3V3 (P12 name).')
res('R40','ADDED_PANEL_3V3_LIMIT','100R',V,'PANEL_3V3','ZLACZA','R2 (R4-03): 3V3_IO to the panel contacts (J8.1: STOP, KEY, MECH) through 100R; short-circuit current 33 mA.')
res('R41','ADDED_TEST_KEY_SER','1K','TEST_KEY','TEST_KEY_P04','ILK','R2 (R4-07): series resistor between the 300 mm panel line and the HC08 inputs.')
res('R42','ADDED_MECH_OK_SER','1K','MECH_OK','MECH_OK_P04','ILK','R2 (R4-07): series resistor between the 300 mm panel line and the HC08 input.')
add('C18','ADDED_SAFE_N_FILTER',S_C,CDISC,'1n / C0G','C320C102J1G5TA (KEMET C0G 1n, owned; lead pitch to check on the 1:1 print)',{1:'SAFE_N',2:G},'WD',URL['c0g'],zrodlo=REG,note='R2 (R4-04): 1 nF C0G at the Schmitt input; rise tau 10 us, STOP-open fall to the HC14 threshold ~55-160 us; no DC change. R3: owned KEMET (register: last piece after P05 R3), as already noted for R2.2.')
add('C1','C_WD',S_C,MKS2_100V,'1u / PET','MKS2D041001K00JO00',{1:'WD_RC',2:'WD_C'},'WD',URL['film'],'Owned (register: last piece after P02 R4). WIMA MKS2 PET 1uF / 100V / 10%, L7.2 W7.2 P5 mm. Watchdog timing: never X7R or electrolytic.',zrodlo=REG)
add('C2','C_ARM',S_C,CFILM,'1u / PET','MKS2C041001F00KSSD',{1:'ARM_BUTTON_N',2:G},'WD',URL['film'],'New, as R2.2: WIMA MKS2 PET 1uF / 63V / 10%, L7.2 W5 H10 P5 mm (S1 9 names ceramics as 1206; a 1uF film part has no 1206 equivalent).')
add('C3','ADDED_BULK',S_CP,CP5,'10u / 63V','EEU-EB1J100SH',{1:V,2:G},'P04','https://industrial.panasonic.com/ww/products/pt/aluminum-cap-lead/models/EEUEB1J100SH','Owned (register: one left after P02 R4). R2.2 had EEUFR1H100 10u/50V; same size D5 P2.',zrodlo=REG)
for i in range(1,12):cap(f'C{i+3}',f'C_DEC_U{i}','100n / X7R',V,G,'P04')
for i in range(15,18):cap(f'C{i}',f'ADAPTER_U{i-7}','100n / X7R',V,G,'P04','R3: second 100nF of U{} (was on the SO14 adapter in R2.2); SOIC soldered directly, place at pins 14/7 opposite C{}. Kept for circuit identity; may be DNP after review.'.format(i-7,i-4))
add('LED1','ADDED_POWER_LED',S_LED,LED,'POWER / green','L-934GD',{1:G,2:'LED_PWR'},'P04','https://www.kingbrightusa.com/images/catalog/SPEC/L-934GD.pdf')
# R3: external reset net takes the P12 name of P03 R6 J_BP3.12 (internal SUP_N_P04 after the buffer unchanged).
for _p in PARTS.values():_p['pins']={k:('SUP_N_OUT' if v=='SUP_N' else v) for k,v in _p['pins'].items()}
# Owned ICs (register: P04 allocation 74HC08 x4 with DIP14 sockets x4, DIP16 socket for U1); HC123/HC14/HC74 not bought yet.
for r in ['U4','U5','U6','U7']:PARTS[r]['zrodlo']=REG;PARTS[r]['note']='Owned (register, P04 allocation) with owned precision DIP14 socket (Kamami 648).'
PARTS['U1']['note']='New part; owned precision DIP16 socket (Kamami 649, P04 allocation).'
# R3 (S1 5): edge A, three angled shrouded IDC connectors to P12, one per slot (centres x = 26.5 / 80.0 / 133.5 mm), pin 1 towards
# smaller x, every odd pin GND. Pins of a net shared with a counterpart already on P12 follow that counterpart where possible:
# J_BP1 2/4/6/8/14 = P11 R2 J_P12, J_BP2 12/16/18 = P02 R4 J_BP, J_BP3 12/14/16/18/20 = P03 R6 J_BP3. Nets to P07 / P08 keep the
# R2.2 names (DRIVE J3, SENSOR J4); P12 joins by name.
JBP={'J_BP1':{2:'PANEL_3V3',4:'MECH_OK',6:'STOP_NC_OUT',8:'ARM_CONTACT',10:'SENSOR_PERMIT',12:'SENSOR_OK',14:'TEST_KEY',16:'DAQ_OK'},
 'J_BP2':{2:'MOTOR_PERMIT',4:'PWM_OUT',6:'ARM_CLK',8:'DRIVE_OK',10:V,12:'PSU_OK',14:'P04_3V3',16:'SAFE_N',18:'PG_LINK',20:'PG_SEND'},
 'J_BP3':{2:'SENSOR_ENABLE',4:'CORE_LINK',6:'HW_ARMED',8:'5V_SYS',10:V,12:'SUP_N_OUT',14:'PWM',16:'HEARTBEAT',18:'MCU_ARM',20:'INTERLOCK'}}
SLOT={'J_BP1':('S1',26.5),'J_BP2':('S2',80.0),'J_BP3':('S3',133.5)}
for j,pins in JBP.items():
 n=max(pins);pins.update({i:G for i in range(1,n,2)})
 add(j,'J_LV04B+J_SAFEB+J3..J8 (R2.2)',symbol('Connector_Generic',f'Conn_02x{n//2:02d}_Odd_Even'),copyfp('Connector_IDC',f'IDC-Header_2x{n//2:02d}_P2.54mm_Horizontal'),
     f'{j} / IDC 2x{n//2}',f'IDC header 2x{n//2} 2.54mm angled shrouded, Au',pins,'ZLACZA',
     note=f'Edge A, slot {SLOT[j][0]} (centre x={SLOT[j][1]} mm), pin 1 towards smaller x, mating side flush with the edge. Odd pins GND. Ribbon ~30 mm to P12.')
# R3 (S1 6): service strips on edge B, angled goldpin, GND first and last, every other pin through a series resistor at the node.
# Classes: 1K rails, limited outputs and gate-driven logic; 10K the passive high-impedance nodes SAFE_N (R4 10k / R5 100k) and
# ARM_BUTTON_N (R2 10k). Exception Q1_B 1K: E21 shorts the pin to GND and must hold the base below VBE (10K: 1.57 V, Q1 still on;
# 1K: 0.30 V). Neighbour rules (verify_s1.py): SAFE_N and ARM_BUTTON_N only next to GND (a probe bridging a rail would lift SAFE_N
# past an open STOP or fake an ARM edge); rails only next to GND or another rail.
SV1=[(None,),('SAFE_N',10000,'wspolny SAFE_N: H >= 2,7 V (nominalnie 2,94 V za R40), L <= 0,25 V (E05, E10, E21, I01)'),(None,),
 ('ARM_BUTTON_N',10000,'styk ARM za R3: H 3,3 V, nacisniety ok. 0,30 V (E15)'),(None,),('ARM_CLK',1000,'zbocze zegara zatrzasku U2B (E15)'),
 ('HW_ARMED',1000,'zatrzask U3A (E06, E07, E14)'),('SAFE_OK',1000,'SAFE_N po U2E/U2F (E05)'),('SAFE_WD',1000,'SAFE_OK & WD_Q, U7D (E05, E11, E21)'),
 ('WD_Q',1000,'watchdog U1A (E05, E11-E13)'),('Q1_B',1000,'baza Q1; E21: zwarcie kolka z GND (1k: baza ok. 0,30 V)'),('LOCAL_SUP_N',1000,'MCP100 U11, push-pull (E02, E16)'),(None,)]
SV2=[(None,),('SUP_OK',1000,'SUP_N_OUT & LOCAL_SUP_N, U5C (E12, E16)'),('INTERLOCK',1000,'U7B (E05, E09)'),('MOTOR_PERMIT',1000,'U5D (E06-E09)'),
 ('PWM_OUT',1000,'U4C (E06, E19)'),('SENSOR_PERMIT',1000,'U5B (E08)'),(None,)]
SV3=[(None,),('5V_SYS',1000,'5V_SYS z J_BP3.8 (bez odbiorcy na P04, jak J1.1 -> TP13 w R2.2)'),('3V3_IO',1000,'zasilanie P04 (E01, E03, E22)'),
 ('PANEL_3V3',1000,'za R40 100R do stykow panelu (E05, E22)'),('P04_3V3',1000,'za R39 1k do Q7 P02 (E22)'),('PG_SEND',1000,'za R38 1k, petla PG (E22)'),(None,)]
SERVICE={};nr=43
for jref,rows,src,slot in [('J_SV1',SV1,'SERVICE_S1','10..43 mm (slot S1)'),('J_SV2',SV2,'SERVICE_S2','63.5..96.5 mm (slot S2)'),('J_SV3',SV3,'SERVICE_S3','117..150 mm (slot S3)')]:
 n=len(rows);pp={}
 for k,row in enumerate(rows,1):
  if row[0] is None:pp[k]=G;continue
  net,ohm,why=row;r='R'+str(nr);nr+=1;pp[k]='SRV_'+net;SERVICE[net]=(jref,k,r,ohm,why)
  res(r,'ADDED_'+src,{1000:'1K',10000:'10K'}[ohm],net,'SRV_'+net,'SERWIS','Service pin series resistor at the node (S1 6): a slipped probe cannot damage anything. SMD, may sit on the bottom side.')
 add(jref,src,symbol('Connector_Generic',f'Conn_01x{n:02d}'),copyfp('Connector_PinHeader_2.54mm',f'PinHeader_1x{n:02d}_P2.54mm_Horizontal'),f'{jref} SERWIS 1x{n}',f'Pin header 1x{n}, 2.54 mm, right angle, Au',pp,'SERWIS',
     note='Edge B, x='+slot+'; pins ~6 mm beyond the edge. Numbering always from pin 1 (angled strip seen from the top has pin 1 at LARGER x).')
def write_tables():
 clean={r:{k:v for k,v in p.items() if k!='symbol'} for r,p in PARTS.items()}
 (P/'docs/parts.json').write_text(json.dumps(clean,indent=2,ensure_ascii=False),encoding='utf-8')
 with (P/'docs/BOM.csv').open('w',newline='',encoding='utf-8-sig') as f:
  w=csv.DictWriter(f,['ref','source_ref','display','mpn','qty','footprint','on_board','zrodlo','url','note'],delimiter=';',extrasaction='ignore');w.writeheader();w.writerows(PARTS.values())
 libs={p['symbol'][1]:p['symbol'] for p in PARTS.values()};libs[PRJ+':PWR_FLAG']=symbol('power','PWR_FLAG')
 (P/'eda/libraries/P04.kicad_sym').write_text('(kicad_symbol_lib (version 20231120) (generator "kicad_symbol_editor")'+''.join(dump([s[0],s[1].split(':')[1]]+s[2:]) for s in libs.values())+')',encoding='utf-8')
 (P/'eda/sym-lib-table').write_text('(sym_lib_table (lib (name "P04") (type "KiCad") (uri "${KIPRJMOD}/libraries/P04.kicad_sym") (options "") (descr "P04 symbols")))')
 flibs=sorted({p['footprint'].split(':')[0] for p in PARTS.values()})
 (P/'eda/fp-lib-table').write_text('(fp_lib_table '+''.join(f'(lib (name {q(l)}) (type "KiCad") (uri "${{KIPRJMOD}}/libraries/{l}.pretty") (options "") (descr "P04 local library"))' for l in flibs)+')')
if __name__=='__main__':write_tables();print('P04:',len(PARTS),'components;',sum(p['on_board'] for p in PARTS.values()),'on main PCB')
