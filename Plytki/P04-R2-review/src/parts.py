"""Explicit P04-R2 circuit (R1 by Astra + review changes R4-01..R4-07). Never infer electrical wiring from placement or rendered graphics."""
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
 'res':'https://yageogroup.com/content/Resource%20Library/Datasheet/YAGEO-MFR_DATASHEET.pdf',
 'film':'https://www.wima.de/wp-content/uploads/media/e_WIMA_MKS_2.pdf',
 'cer':'https://www.vishay.com/docs/45171/kseries.pdf'}
def copyfp(lib,name):
 src=K/'footprints'/(lib+'.pretty')/(name+'.kicad_mod');assert src.exists(),src
 dest=P/'eda/libraries'/(lib+'.pretty');dest.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest/src.name)
 return lib+':'+name
def localfp(name):
 src=P/'input/footprints'/(name+'.kicad_mod')
 assert hashlib.sha256(src.read_bytes()).hexdigest()==json.loads((P/'input/footprints-sha256.json').read_text())[src.name]
 shutil.copy2(src,FP/src.name);return 'P04:'+name
def pigtail(name,n,ribbon):
 pads=[]
 for i in range(n):
  x,y=(i//2*2.54,i%2*2.54) if ribbon else (i*3.5,0)
  pads.append((i+1,x,y))
 maxx=max(x for _,x,_ in pads);maxy=max(y for _,_,y in pads)
 drill,pad=(.8,1.8) if ribbon else (1.1,2.1)
 s=f'(footprint {q(name)} (version 20240108) (generator "pcbnew") (layer "F.Cu") (attr through_hole)'
 for num,x,y in pads:s+=f'(pad "{num}" thru_hole {"rect" if num==1 else "circle"} (at {x} {y}) (size {pad} {pad}) (drill {drill}) (layers "*.Cu" "*.Mask"))'
 for x in (-3.3,maxx+3.3):s+=f'(pad "" np_thru_hole circle (at {x} -12) (size 3.2 3.2) (drill 3.2) (layers "*.Cu" "*.Mask"))'
 s+=f'(fp_rect (start -5.3 -14) (end {maxx+5.3} {maxy+1.6}) (stroke (width .05) (type default)) (fill none) (layer "F.CrtYd"))'
 s+=f'(fp_text user "KOTWA 12 mm" (at {maxx/2} -15.5) (layer "F.Fab") (effects (font (size 1 1) (thickness .15))))'
 for num,x,y in pads:s+=f'(fp_text user "{num}" (at {x} {y-2.2 if y==0 else y+2.2}) (layer "F.Fab") (effects (font (size .8 .8) (thickness .12))))'
 s+=f'(fp_text reference "REF**" (at {maxx/2} {maxy+3.2}) (layer "F.SilkS") (effects (font (size 1 1) (thickness .15))))'
 (FP/(name+'.kicad_mod')).write_text(s+')',encoding='utf-8');return 'P04:'+name
RFP=copyfp('Resistor_THT','R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal')
C100=localfp('C_Vishay_K15_H5_P5');TPFP=localfp('TestPad_1')
ADP=localfp('Adapter_SO14_DIP14_W15.24_Kamami575068')
DIP14=copyfp('Package_DIP','DIP-14_W7.62mm');DIP16=copyfp('Package_DIP','DIP-16_W7.62mm')
TO92=copyfp('Package_TO_SOT_THT','TO-92_Inline_Wide')
CP5=copyfp('Capacitor_THT','CP_Radial_D5.0mm_P2.00mm')
CFILM=copyfp('Capacitor_THT','C_Rect_L7.2mm_W5.0mm_P5.00mm')
LED=copyfp('LED_THT','LED_D3.0mm')
MF6=copyfp('Connector_Molex','Molex_Mini-Fit_Jr_5566-06A2_2x03_P4.20mm_Vertical')
MF10=copyfp('Connector_Molex','Molex_Mini-Fit_Jr_5566-10A2_2x05_P4.20mm_Vertical')
def idcfp(n):
 # Wurth WR-BHD: maximum square lead diagonal 1.117 mm; recommended hole 1.1 +/-0.15.
 # Use 1.2 mm finished drill and 1.9 mm pad, rather than generic 1.0 mm drill.
 src=K/'footprints/Connector_IDC.pretty'/f'IDC-Header_2x{n//2:02d}_P2.54mm_Vertical.kicad_mod'
 t=parse(src.read_text(encoding='utf-8'));name=f'IDC_{n}p_Wurth_Drill1.2';t[1]=name
 for pad in subs(t,'pad'):
  if pad[1]:one(pad,'drill')[1]=A('1.2');one(pad,'size')[1:]=[A('1.9'),A('1.9')]
 (FP/(name+'.kicad_mod')).write_text(dump(t),encoding='utf-8');return 'P04:'+name
IDC6=idcfp(6);IDC10=idcfp(10)
LV=pigtail('PTH_LV04_4p_AWG22',4,False);SAFE=pigtail('PTH_SAFE_16p_AWG28',16,True)
S_R=symbol('Device','R');S_C=symbol('Device','C');S_CP=symbol('Device','C_Polarized');S_TP=symbol('Connector','TestPoint')
S_HC123=symbol('74xx','74HC123','CD74HC123E');S_HC14=symbol('74xx','74HC14','SN74HC14N')
S_HC74=symbol('74xx','74HC74','SN74HC74N');S_HC08=symbol('74xx','74LS08','SN74HC08N')
S_LVC=symbol('74xx','74LVC125','74LVC125AD');S_SUP=symbol('Power_Supervisor','MCP100-300D','MCP100-300DI_TO')
S_NPN=symbol('Transistor_BJT','2N3904');S_LED=symbol('Device','LED')
def add(ref,src,sym,fp,value,mpn,pins,sheet,url='',note='',on_board=True):
 PARTS[ref]={'ref':ref,'source_ref':src,'symbol':sym,'footprint':fp,'display':value,'value':value,'mpn':mpn,
 'pins':{str(k):v for k,v in pins.items()},'sheet':sheet,'url':url,'note':note,'qty':1,'on_board':on_board}
def res(ref,src,v,a,b,sheet,note=''):
 add(ref,src,S_R,RFP,v+' / 1%', 'MFR-25FRF52-'+v,{1:a,2:b},sheet,URL['res'],note)
def cap(ref,src,v,a,b,sheet,film=False,on_board=True):
 add(ref,src,S_C,CFILM if film else C100,v,'MKS2C041001F00KSSD' if film else 'K104K15X7RF53H5',{1:a,2:b},sheet,URL['film' if film else 'cer'],
 'PET 1uF / 63V / 10%; L7.2 W5 H10 P5 mm' if film else ('100nF at IC supply pins; assembly mounted on SO14 adapter' if not on_board else '100nF local decoupling'),on_board)
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
 add(f'U{i}',f'U_RX{i-7}',S_LVC,ADP,'74LVC125AD / adapter','74LVC125AD,118 (Nexperia)',pins,'RX',URL['lvc125'],'Kamami 575068 SO14 to DIP14 adapter, 18x18 mm, rows 15.24 mm; local 100nF C15..17 on adapter.')
add('U11','ADDED_LOCAL_SUPERVISOR',S_SUP,TO92,'MCP100-300DI/TO','MCP100-300DI/TO',{1:'LOCAL_SUP_N',2:V,3:G},'P04',URL['mcp100'],'D bondout: 1=/RESET, 2=VDD, 3=VSS. Do not substitute H variant. 2.85..3.00V trip, reset delay 150..700 ms (MCP1X0 -300). R2: -315 (release up to 3.20 V) was above the 3.18 V worst-case 3V3_IO of TSR 2-2433 (review R4-01).')
res('R1','R_WD','220K',V,'WD_RC','WD')
res('R2','R_ARM_PU','10K',V,'ARM_BUTTON_N','WD')
res('R3','R_ARM_SER','1K','ARM_BUTTON_N','ARM_CONTACT','WD','Was 100R; with C2=1u gives about 10ms release RC and limits discharge current.')
res('R4','R_SAFE_PU','10K','STOP_NC_OUT','SAFE_N','WD','Only pull-up of the shared SAFE_N net; supply through physical STOP NC.')
res('R5','R_SAFE_PD','100K','SAFE_N',G,'WD')
for i,n in enumerate(['WD_BAD','SUP_BAD','ILK_BAD'],1):
 res(f'R{i+5}',f'ADDED_Q{i}_BASE','10K',n,f'Q{i}_B','WD')
 res(f'R{i+8}',f'Q{i}_PD','100K',f'Q{i}_B',G,'WD')
 add(f'Q{i}',['Q8','Q9','Q10'][i-1],S_NPN,TO92,'2N3904','2N3904BU',{1:G,2:f'Q{i}_B',3:'SAFE_N'},'WD',URL['npn'],'Open collector sink replaces SOT23 2N7002. TO92 pins 1 E,2 B,3 C; 10k series base resistor.')
for i,s in enumerate(signals,12):res(f'R{i}','R_EXT_'+s,'100K' if s=='SUP_N' else '10K',s,G,'RX','Connector-side default LOW.')
res('R23','R_PD_TEST_KEY','10K','TEST_KEY_P04',G,'ILK','Gate side of R41: an open R41 leaves the gate LOW.')
res('R24','R_LINK_MECH_OK','10K','MECH_OK_P04',G,'ILK','One 10k replaces the two parallel 10k in v6.1; gate side of R42.')
for i,s in enumerate(signals,25):
 v='47K' if s in ['HEARTBEAT','MCU_ARM'] else ('100K' if s in ['SUP_N','SENSOR_ENABLE'] else '10K')
 res(f'R{i}','R_LOCAL_'+s,v,s+'_P04',G,'RX','Default LOW after removable adapter; no floating gate if adapter absent.')
res('R36','R_LINK_INTERLOCK','10K','INTERLOCK',G,'ILK')
res('R37','ADDED_POWER_LED','1K',V,'LED_PWR','P04')
res('R38','W_SEND','1K',V,'PG_SEND','CON','R2: was 0R. Limits a PG_SEND short in the PG harness to 3.3 mA; PG_LINK = 3.0 V with R22 10k (P01 loop R34 0R).')
res('R39','ADDED_PG_3V3_LIMIT','1K',V,'PG_3V3','CON','R2 (R4-03): 3V3_IO to P01 (J7.1, bias of P01 Q7 via its R30 10k) through 1k; a harness short no longer collapses 3V3_IO.')
res('R40','ADDED_PANEL_3V3_LIMIT','100R',V,'PANEL_3V3','CON','R2 (R4-03): 3V3_IO to the panel contacts (J8.1: STOP, KEY, MECH) through 100R; short-circuit current 33 mA.')
res('R41','ADDED_TEST_KEY_SER','1K','TEST_KEY','TEST_KEY_P04','ILK','R2 (R4-07): series resistor between the 300 mm panel line and the HC08 inputs.')
res('R42','ADDED_MECH_OK_SER','1K','MECH_OK','MECH_OK_P04','ILK','R2 (R4-07): series resistor between the 300 mm panel line and the HC08 input.')
add('C18','ADDED_SAFE_N_FILTER',S_C,C100,'1n / C0G','K102J15C0GF53H5',{1:'SAFE_N',2:G},'WD',URL['cer'],'R2 (R4-04): 1 nF C0G at the Schmitt input; rise tau 10 us, STOP-open fall to the HC14 threshold ~55-160 us; no DC change.')
cap('C1','C_WD','1u / PET','WD_RC','WD_C','WD',True)
cap('C2','C_ARM','1u / PET','ARM_BUTTON_N',G,'WD',True)
add('C3','ADDED_BULK',S_CP,CP5,'10u / 50V','EEUFR1H100',{1:V,2:G},'P04','https://industrial.panasonic.com/ww/products/pt/aluminum-cap-lead/models/EEUFR1H100')
for i in range(1,12):cap(f'C{i+3}',f'C_DEC_U{i}','100n / X7R',V,G,'P04')
for i in range(15,18):cap(f'C{i}',f'ADAPTER_U{i-7}','100n / X7R',V,G,'P04',on_board=False)
add('LED1','ADDED_POWER_LED',S_LED,LED,'POWER / green','L-934GD',{1:G,2:'LED_PWR'},'P04','https://www.kingbrightusa.com/images/catalog/SPEC/L-934GD.pdf')
baseline=json.loads((P/'reference/baseline.json').read_text())
connectors=[('J1','J_LV04B',4,LV,'LV04 / PTH','PCB soldered harness',None),
 ('J2','J_SAFEB',16,SAFE,'SAFE / PTH','PCB soldered harness',4),
 ('J3','J_DRIVEA',10,IDC10,'DRIVE / IDC10','61201021621',2),
 ('J4','J_SENSORA',6,IDC6,'SENSOR / IDC6 M2.2','61200621621',2),
 ('J5','J_DAQOKA',6,IDC6,'DAQOK / IDC6','61200621621',4),
 ('J6','J_PSUOKA',6,IDC6,'PSUOK / IDC6','61200621621',5),
 ('J7','J_PGA',6,MF6,'PG / Mini-Fit 6','39-29-9069',None),
 ('J8','J_PANELSAFEA',10,MF10,'PANELSAFE / Mini-Fit 10','39-29-9109',None)]
for ref,src,count,fp,v,mpn,key in connectors:
 pins={str(i):baseline[src]['pins'].get(str(i),'NC') for i in range(1,count+1)}
 url='https://www.we-online.com/components/products/datasheet/'+mpn+'.pdf' if mpn.startswith('612') else ('https://www.molex.com/en-us/products/part-detail/'+mpn.replace('-','') if mpn.startswith('39-') else '')
 add(ref,src,symbol('Connector_Generic',f'Conn_01x{count:02d}'),fp,v,mpn,pins,'CON',url,
     ('Key '+str(key)+': remove header pin / block matching socket position, leave PCB pad electrically NC. ' if key else '')+
     ('SENSOR expands 4 to 6 positions; original signals 1..4 unchanged; 5/6 NC. Matching P08 harness must be 6-way M2.2.' if ref=='J4' else ''))
PARTS['J7']['pins']['1']='PG_3V3';PARTS['J8']['pins']['1']='PANEL_3V3'  # R2 (R4-03): 3V3 leaves the board through R39 / R40
for i,n in enumerate([V,G,'LOCAL_SUP_N','SUP_OK','WD_Q','SAFE_N','SAFE_OK','ARM_CLK','HW_ARMED','INTERLOCK','MOTOR_PERMIT','SENSOR_PERMIT','5V_SYS','SAFE_WD','Q1_B'],1):  # R2: TP14 SAFE_WD, TP15 Q1_B (proof test of the watchdog path)
 add(f'TP{i}','ADDED_TESTPAD',S_TP,TPFP,n,'PCB test pad',{1:n},'P04',note='Probe pad, no separately purchased part.')
def write_tables():
 clean={r:{k:v for k,v in p.items() if k!='symbol'} for r,p in PARTS.items()}
 (P/'docs/parts.json').write_text(json.dumps(clean,indent=2,ensure_ascii=False),encoding='utf-8')
 with (P/'docs/BOM.csv').open('w',newline='',encoding='utf-8-sig') as f:
  w=csv.DictWriter(f,['ref','source_ref','display','mpn','qty','footprint','on_board','url','note'],delimiter=';',extrasaction='ignore');w.writeheader();w.writerows(PARTS.values())
 libs={p['symbol'][1]:p['symbol'] for p in PARTS.values()};libs[PRJ+':PWR_FLAG']=symbol('power','PWR_FLAG')
 (P/'eda/libraries/P04.kicad_sym').write_text('(kicad_symbol_lib (version 20231120) (generator "kicad_symbol_editor")'+''.join(dump([s[0],s[1].split(':')[1]]+s[2:]) for s in libs.values())+')',encoding='utf-8')
 (P/'eda/sym-lib-table').write_text('(sym_lib_table (lib (name "P04") (type "KiCad") (uri "${KIPRJMOD}/libraries/P04.kicad_sym") (options "") (descr "P04 symbols")))')
 flibs=sorted({p['footprint'].split(':')[0] for p in PARTS.values()})
 (P/'eda/fp-lib-table').write_text('(fp_lib_table '+''.join(f'(lib (name {q(l)}) (type "KiCad") (uri "${{KIPRJMOD}}/libraries/{l}.pretty") (options "") (descr "P04 local library"))' for l in flibs)+')')
if __name__=='__main__':write_tables();print('P04:',len(PARTS),'components;',sum(p['on_board'] for p in PARTS.values()),'on main PCB')
