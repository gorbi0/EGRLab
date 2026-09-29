"""Passive panel. No power source, no added pulldowns, no sensor-ground bond."""
from cadlib import *
import csv,shutil
PARTS={};exec((P/'src/helpers.txt').read_text(encoding='utf-8'));import make_footprints
def add(r,src,n,fp,val,mpn,pins,sheet,ob=True,url='',note='',sym=None):
 PARTS[r]=dict(ref=r,source_ref=src,symbol=sym or symbol('Connector_Generic',f'Conn_01x{n:02d}'),footprint=fp,display=val,value=val,mpn=mpn,pins={str(k):v for k,v in pins.items()},sheet=sheet,url=url,note=note,qty=1,on_board=ob)
def pins(*ns):return dict(enumerate(ns,1))
G='GND';V='PANEL_3V3';N='NC'
l1=pins('ECU_P1','EGR_P1','TAP_P1','TAP_P3','TAP_P4','TAP_P5','TAP_P6',N,N,N,N,G)
l2=pins('TAP_P1','TAP_P3','TAP_P4','TAP_P5','TAP_P6',N,N,N,N,N,N,G)
test=pins('T_EGR_P1','T_EGR_P3','5V_SENSOR','AGND_SENSOR','TAP_P1','TAP_P3','TAP_P4','TAP_P5','TAP_P6','LOOP_OUT','MECH_OK',N)
mstb=copyfp('Connector_Phoenix_MSTB','PhoenixContact_MSTBVA_2,5_4-G-5,08_1x04_P5.08mm_Vertical')
mf=copyfp('Connector_Molex','Molex_Mini-Fit_Jr_5566-12A2_2x06_P4.20mm_Vertical')
add('J1','J1',4,mstb,'ISERIES / P06','Phoenix 1755752',pins('ECU_P1','EGR_P1',N,N),'P11',url='https://www.phoenixcontact.com/en-gb/products/1755752')
for r,src,net,sh in [('J2','J2',l1,'P11'),('J3','J3',l2,'TAPS'),('J8','J8',test,'P11')]:
 add(r,src,12,'P11:PTH_DT12',{'J2':'L1 tail','J3':'L2 tail','J8':'TEST tail'}[r],'Soldered PTH harness',net,sh)
for r,mpn,net,sh in [('X2','DT04-12PB',l1,'P11'),('X3','DT04-12PC',l2,'TAPS'),('X8','DT04-12PA',test,'P11')]:
 add(r,r.replace('X','J'),12,'P11:OFFBOARD',mpn,mpn,net,sh,False,'https://www.te.com/en/product-'+mpn+'.html','OFFBOARD: cavity numbers, not pin positions on PTH. Separate harness mapping required.')
add('J4','J4',8,'P11:PTH_CORE8','PANELCORE','Soldered harness',pins(G,'MARK','TEST_KEY','LOGGER_CLEAR','TEST_PRESENT',N,'N_J_SCOPE_HOT',G),'CONTROL')
add('J5','J5',10,'P11:PTH_SAFE10','PANELSAFE','Soldered harness',pins(V,G,'TEST_KEY','MECH_OK',N,N,'STOP_NC_OUT',N,'ARM_CONTACT',G),'CONTROL')
add('J6','J6_TAIL',2,'P11:PTH_PAIR2','SCOPE tail','RG174 100mm',pins('N_J_SCOPE_HOT',G),'CONTROL')
add('X6','J6',2,'P11:OFFBOARD','SCOPE BNC','Insulated panel BNC solder cup',pins('N_J_SCOPE_HOT',G),'CONTROL',False,note='1=center;2=shell. High impedance 1Mohm only. Isolated from metal panel.')
add('J7','J7',12,mf,'TAPS / P05','Molex 39-29-9129',pins('TAP_P1',G,'TAP_P3',G,'TAP_P4',G,'TAP_P5',G,'TAP_P6',G,N,N),'TAPS',url='https://www.molex.com/en-us/products/part-detail/39299129',note='5566-12A2GS-210, pegs, gold. Match with P05 W2 50mm maximum.')
add('J9','J9',5,'P11:PTH_MOTOR5','TMOTOR / HOLD','Soldered 2x2.5mm2 harness',pins('T_EGR_P1','T_EGR_P3',N,N,N),'P11',note='P07 HOLD: unpopulated until purchased H bridge and P07 reviewed. No supply connection here.')
add('J10','J10',2,'P11:PTH_PAIR2','TSENSOR / P08','Soldered harness',pins('5V_SENSOR','AGND_SENSOR'),'P11')
contact=pins(V,'TEST_KEY','TEST_KEY','ILK_L1_L2',V,'DIAG_L1_L2','ILK_L1_L2','LOOP_OUT','DIAG_L1_L2','LOGGER_CLEAR',V,'STOP_NC_OUT',G,'ARM_CONTACT',G,'MARK',V,'TEST_PRESENT',N,N)
add('J11','ADDED_CONTACT_TAIL',20,'P11:PTH_CONTACT20','CONTACTS / panel','Soldered AWG24 harness',contact,'CONTROL',note='Functional contact assignments in WIAZKI.md. Not IDC and no plug-in header.')
spec=[('X11','ARM momentary NO','14-435.036',pins(G,'ARM_CONTACT'),['COM','NO']),('X12','L1 detector 2NC','14-432.036',pins('TEST_KEY','ILK_L1_L2',V,'DIAG_L1_L2'),['COM_A','NC_A','COM_B','NC_B']),('X13','L2 detector 2NC','14-432.036',pins('ILK_L1_L2','LOOP_OUT','DIAG_L1_L2','LOGGER_CLEAR'),['COM_A','NC_A','COM_B','NC_B']),('X14','MARK momentary NO','14-435.036',pins(G,'MARK'),['COM','NO']),('X15','KEY TEST NO','14-412.036K',pins(V,'TEST_KEY',N,N),['COM_NO','TEST_NO','NC_UNUSED_A','NC_UNUSED_B']),('X16','STOP latched NC+NO','14-473.036',pins(V,'STOP_NC_OUT',N,N),['COM_NC','NC','NO_UNUSED_A','NO_UNUSED_B']),('X17','TEST detector NO','14-435.036',pins(V,'TEST_PRESENT'),['COM','NO'])]
for r,val,mpn,pn,labels in spec:
 sy=custom(r+'_CONTACT',[([(i+1,l,'passive') for i,l in enumerate(labels)],[])])
 add(r,r,len(pn),'P11:OFFBOARD',val,'EAO '+mpn+' (reference low-level)',pn,'CONTACTS',False,'https://www.eao.com/component/'+mpn+'/en/actuator','Functional terminal numbers in schematic; identify physical terminals from purchased part and continuity test. EAO reference is not a mandatory footprint. No illumination supply. Fixture and caps required.',sy)
if __name__=='__main__':write_tables()
