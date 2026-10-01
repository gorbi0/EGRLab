"""P05-R3: R2 checks adapted to format S1 (no B2B/LV05/VSENSE connectors - verify_s1.py checks J_BP/J_SV; 3V3_IO absent; SW1 from the
JS202011AQN footprint geometry; DAQ_OK window budget from the TCR class in the exported MPN plus a soldering/aging allowance).
R2 header: Independent pin-level acceptance of the exported netlist; no import from parts.py.
Pin numbers below are frozen from manufacturers' data sheets. Deliberate mutations
demonstrate that wrong wiring is rejected. Analog budgets are estimates, not SPICE or bench evidence.
"""
from pathlib import Path
import xml.etree.ElementTree as ET,json,itertools,copy,math
P=Path(__file__).resolve().parents[1]
root=ET.parse(P/'verification/P05.xml').getroot();N={}
for nn in root.findall('./nets/net'):
 for n in nn.findall('node'):N[n.get('ref'),n.get('pin')]=nn.get('name').split('/')[-1] if nn.get('name').startswith('/') else nn.get('name')
values={c.get('ref'):c.findtext('value') for c in root.findall('./components/comp')}
MPN={c.get('ref'):next((f.text for f in c.findall('./fields/field') if f.get('name')=='MPN'),'') for c in root.findall('./components/comp')}
def resistance(s):
 s=s.upper().replace('OHM','').strip();return float(s.replace('K','').replace('R',''))*(1000 if 'K' in s else 1)
R={r:resistance(v) for r,v in values.items() if r.startswith('R')}
import re
SWFP=(P/'eda/libraries/Button_Switch_THT.pretty/SW_CK_JS202011AQN_DPDT_Angled.kicad_mod').read_text()
_pads=[(m[1],float(m[2]),float(m[3])) for m in re.finditer(r'\(pad "(\d)"\s+thru_hole\s+\w+\s*\(at ([-\d.]+) ([-\d.]+)',SWFP)]
SWROWS=[sorted([(n,x) for n,x,y in _pads if y==yy],key=lambda q:q[1]) for yy in sorted({y for _,_,y in _pads})]
assert len(_pads)==6 and all(len(r)==3 for r in SWROWS),_pads
def checks(n):
 out=[]
 def ck(name,v,detail=None):out.append(dict(name=name,pass_=bool(v),detail=detail))
 def nn(r,p):return n.get((r,str(p)),'MISSING')
 def pins(r,d):return all(nn(r,k)==v for k,v in d.items())
 def nc(r,p):return nn(r,p).startswith('unconnected-')
 adc={i:'GND' for i in [2,16,17,18,19,20,21,22,26,30,31,32,33,35,40,41,43,46,47]+list(range(50,65,2))}
 adc.update({i:'5VA_P05' for i in [1,37,38,48]});adc.update({i:'3V3_DAQ' for i in [3,4,5,6,7,8,10,23,34]})
 adc.update({9:'ADC_CONVST_P05',11:'ADC_RESET_P05',12:'ADC_SCLK_P05',13:'ADC_CS_P05',14:'AD_BUSY_LOCAL',24:'AD_DOUT_LOCAL',29:'ADC_SDI_P05',36:'REGCAP_A',39:'REGCAP_D',42:'ADC_REF',44:'REFCAP',45:'REFCAP'})
 adc.update({49+2*i:'ADC_CH'+str(i+1) for i in range(8)})
 ck('AD7606B all 64 physical pins',pins('U1',adc) and all(nc('U1',p) for p in [15,25,27,28]))
 ck('Separate REGCAP and reference capacitors',all(pins(r,{1:a,2:'GND'}) for r,a in [('C9','REGCAP_A'),('C10','REGCAP_D'),('C11','ADC_REF'),('C12','ADC_REF'),('C13','REFCAP')]) and values['C9']==values['C10']=='1u' and values['C12']==values['C13']=='22u')
 ck('VDRIVE supplied from local AVCC-derived regulator',pins('U12',{1:'GND',2:'5VA_P05',3:'3V3_DAQ'}) and pins('R1',{1:'5V_SYS',2:'5VA_P05'}) and pins('R2',{1:'3V3_DAQ',2:'GND'}) and not any(net=='3V3_IO' for net in n.values()))
 ck('All digital supply pins share local domain',pins('U5',{7:'GND',14:'3V3_DAQ'}) and all(pins(r,{7:'GND',14:'3V3_DAQ'}) for r in ['U8','U9','U10','U11']))
 ck('Open-collector window and supervisor bondout',pins('U3',{1:'DAQ_RAIL_N',2:'RAIL_LOW',3:'RAIL_SENSE',4:'GND',5:'RAIL_HIGH',6:'RAIL_SENSE',7:'DAQ_RAIL_N',8:'5V_SYS'}) and pins('U6',{1:'P05_SUP3_N',2:'3V3_DAQ',3:'GND'}) and pins('U7',{1:'P05_SUP5_RAW',2:'5V_SYS',3:'GND'}) and pins('U8',{1:'GND',2:'P05_SUP5_RAW',3:'P05_SUP5_N'}))
 # Evaluate ACTUAL HC08 pin connections, with independent expected truth table.
 rows=[]
 for rail,s3,s5,meas in itertools.product([False,True],repeat=4):
  nets={'GND':False,'3V3_DAQ':True,'DAQ_RAIL_N':rail,'P05_SUP3_N':s3,'P05_SUP5_N':s5,'MEAS_EN_P05':meas}
  for _ in range(4):
   for a,b,y in [(1,2,3),(4,5,6),(9,10,8),(12,13,11)]:
    if nn('U5',a) in nets and nn('U5',b) in nets:nets[nn('U5',y)]=nets[nn('U5',a)] and nets[nn('U5',b)]
  rows.append(nets.get('DAQ_OK')==(rail and s3 and s5) and nets.get('MEAS_PERMIT')==(rail and s3 and s5 and meas))
 ck('READY and relay permit: actual HC08 truth table',all(rows),{'rows':len(rows)})
 for r,a,y,sig in [('U9',2,3,'ADC_SCLK'),('U9',5,6,'ADC_SDI'),('U9',9,8,'ADC_CS'),('U9',12,11,'ADC_CONVST'),('U10',2,3,'ADC_RESET'),('U10',5,6,'MEAS_EN')]:
  ck('RX '+sig,pins(r,{a:sig,y:sig+'_P05', {2:1,5:4,9:10,12:13}[a]:'GND'}))
 defaults=['ADC_CS','ADC_SCLK','ADC_SDI','ADC_CONVST','ADC_RESET','MEAS_EN']
 # R2 (P5-05): the B2B-side CS pull-up R13 is 47K, all other defaults 10K.
 ck('Defaults on both sides of RX buffers',all(pins('R'+str(i+offset),{1:s+suffix,2:'3V3_DAQ' if s=='ADC_CS' else 'GND'}) and R['R'+str(i+offset)]==(47000 if i+offset==13 else 10000) for i,s in enumerate(defaults) for offset,suffix in [(13,''),(19,'_P05')]))
 ck('Window reference REF50xx SOIC-8: 2 VIN, 4 GND, 6 VOUT, others open',pins('U2',{2:'5V_SYS',4:'GND',6:'REF_2V5'}) and all(nc('U2',p) for p in [1,3,5,7,8]) and pins('C24',{1:'REF_2V5',2:'GND'}) and values.get('U2')=='REF5025IDR')
 ck('MISO tri-state and BUSY Ioff output',pins('U11',{1:'ADC_CS_P05',2:'AD_DOUT_LOCAL',3:'DOUT_SER',4:'GND',5:'AD_BUSY_LOCAL',6:'BUSY_SER'}) and pins('R26',{1:'DOUT_SER',2:'ADC_DOUTA'}) and pins('R27',{1:'BUSY_SER',2:'ADC_BUSY'}))
 ck('Relay driver input/output/COM and pull-down',pins('U4',{1:'MEAS_PERMIT',9:'GND',10:'5V_SYS',18:'MEAS_COIL_LOW',**{i:'GND' for i in range(2,9)}}) and pins('R25',{1:'MEAS_PERMIT',2:'GND'}))
 contact=[('K1',3,4,'ADC_CH1','TAP_P1'),('K1',6,5,'ADC_CH2','TAP_P3'),('K2',3,4,'ADC_CH3','TAP_P4'),('K2',6,5,'ADC_CH4','TAP_P5'),('K3',3,4,'ADC_CH5','TAP_P6')]
 ck('G6K NO contacts and coil polarity',all(pins(r,{c:a,no:z,1:'5V_SYS',8:'MEAS_COIL_LOW'}) for r,c,no,a,z in contact) and all(nc(r,p) for r in ['K1','K2','K3'] for p in [2,7]) and all(pins('D'+str(i),{1:'5V_SYS',2:'MEAS_COIL_LOW'}) for i in range(1,4)))
 ck('Channel lower arms and grounded current placeholder',pins('R28',{1:'ADC_CH1',2:'GND'}) and pins('R29',{1:'ADC_CH2',2:'GND'}) and pins('R30',{1:'ADC_CH6',2:'GND'}) and pins('R31',{1:'VBAT_SENSE',2:'ADC_CH7'}) and pins('J_BP1',{9:'GND',10:'VBAT_SENSE'}) and pins('R32',{1:'ADC_CH7',2:'GND'}))
 # R3: slide switch. Positions follow the footprint geometry: a slider joins each common (row middle) to the outer pad on ONE side.
 pos={}
 for side in (min,max):
  got={}
  for row in SWROWS:
   com=row[1][0];end=side(row,key=lambda q:q[1])[0];got[nn('SW1',com)]='NC' if nc('SW1',end) else nn('SW1',end)
  pos[side.__name__]=got
 hi={'AUX_IN':'AUX_HI','AUX_SHUNT':'GND'};lo={'AUX_IN':'AUX_LO','AUX_SHUNT':'NC'}
 ck('AUX switch: HI = AUX_HI + shunt, LO = AUX_LO without shunt (JS202011AQN geometry)',sorted([pos['min'],pos['max']],key=str)==sorted([hi,lo],key=str) and pins('R33',{1:'AUX_HI',2:'ADC_CH8'}) and pins('R34',{1:'AUX_LO',2:'ADC_CH8'}) and pins('R35',{1:'ADC_CH8',2:'AUX_SHUNT'}),pos)
 return [dict(name=x['name'],**{'pass':x['pass_']},detail=x['detail']) for x in out]
out=checks(N);neg=[]
for title,r,p,net,target in [
 ('WR wrongly grounded','U1','10','GND','AD7606B all 64 physical pins'),
 ('REGCAPs shorted','C10','1','REGCAP_A','Separate REGCAP and reference capacitors'),
 ('Independent VDRIVE supply','U12','2','3V3_IO','VDRIVE supplied from local AVCC-derived regulator'),
 ('READY bypasses SUP3','U5','2','3V3_DAQ','READY and relay permit: actual HC08 truth table'),
 ('Relay permit bypasses READY','U5','10','3V3_DAQ','READY and relay permit: actual HC08 truth table'),
 ('MISO always enabled','U11','1','GND','MISO tri-state and BUSY Ioff output'),
 ('Relay on NC terminal','K1','4','GND','G6K NO contacts and coil polarity'),
 ('AUX LO still shunted (R2 pole-B mapping)','SW1','4','GND','AUX switch: HI = AUX_HI + shunt, LO = AUX_LO without shunt (JS202011AQN geometry)'),
 ('Missing CS default','R13','2','GND','Defaults on both sides of RX buffers'),
 ('REF TEMP pin loaded','U2','3','REF_2V5','Window reference REF50xx SOIC-8: 2 VIN, 4 GND, 6 VOUT, others open'),
 ('CH7 back on VPROT','R31','1','VPROT_SENSE','Channel lower arms and grounded current placeholder')]:
 m=copy.deepcopy(N);m[r,p]=net;detected=not next(c['pass'] for c in checks(m) if c['name']==target);neg.append(dict(mutation=title,target_check=target,detected=detected))
# Full-temperature resistor tolerance plus independent worst-sign TCR (100 K excursion), per resistor from the exported MPN class.
# R3: thin-film 1206 instead of MBB0207; an extra soldering-heat/aging allowance of 0.1 % per resistor is added (the Yageo RT card could
# not be read from the cloud: allowance is an assumption to confirm). Reference REF5025IDR as in R2: 0.05 % + 3 ppm/K x 100 K + 0.02 %
# solder shift + 0.015 % hysteresis/aging = 0.115 %. Window resistors at 25 ppm/K (RT1206BRD07) must FAIL with this allowance.
REFGRADE={'REF5025IDR':.0005+3e-6*100+.0002+.00015,'REF5025AIDR':.001+8e-6*100+.0002+.00015}
SOLDER=.001;TCR={'RT1206BRB07':10e-6,'RT1206BRD07':25e-6}
def rtol(ref,mpn=None,solder=SOLDER):
 m=(mpn or MPN)[ref];k=next((k for k in TCR if m.startswith(k)),None)
 return None if k is None else .001+TCR[k]*100+solder
referr=REFGRADE[values['U2']];vos=.0055;ib=20e-9
def par(a,b):return 1/(1/a+1/b)
def corner(top,bot,tols,referr=referr):
 vals=[]
 for e in itertools.product([-1,1],repeat=6):
  rt,rb,tt,tb=[r*(1+s*tl) for r,s,tl in zip([R['R3'],R['R4'],R[top],R[bot]],e[:4],tols)]
  sense=rb/(rt+rb);ref=2.5*(1+e[4]*referr)*tb/(tt+tb)
  err=vos+ib*(2*par(rt,rb)+par(tt,tb)) # both sense comparator inputs
  vals.append((ref+e[5]*err)/sense)
 return min(vals),max(vals)
def budget(mpn=None,solder=SOLDER,ref_err=referr):
 tl={r:rtol(r,mpn,solder) for r in ['R3','R4','R5','R6','R7','R8']}
 if None in tl.values():return None
 return {'low_corner_V':corner('R5','R6',[tl['R3'],tl['R4'],tl['R5'],tl['R6']],ref_err),'high_corner_V':corner('R7','R8',[tl['R3'],tl['R4'],tl['R7'],tl['R8']],ref_err),'R_total_error':tl}
def inside(b):return b is not None and b['low_corner_V'][0]>4.75 and b['high_corner_V'][1]<5.25
b=budget()
window={'low_nominal_V':2.5*R['R6']/(R['R5']+R['R6'])*2.5,'high_nominal_V':2.5*R['R8']/(R['R7']+R['R8'])*2.5,**(b or {'low_corner_V':(0,0),'high_corner_V':(9,9)}),'solder_aging_allowance_per_resistor':SOLDER,'reference_allowance_fraction':referr,'Vos_V':vos,'Ib_A':ib,'scope':'Static corner budget, 100 K TCR excursion; not a guaranteed transient response or lifetime bound.'}
out.append({'name':'Rail-window tolerance stays inside ADC static limits','pass':inside(b),'detail':{k:window[k] for k in ('low_corner_V','high_corner_V')}})
# R3 regression: corners for RT1206BRB07 (0.1 %, 10 ppm/K) + 0.1 % allowance, computed when this check was written (+-0.5 mV).
exp={'low_corner_V':(4.7564,4.8445),'high_corner_V':(5.1414,5.2304)}
out.append({'name':'Window corners as computed for R3 (10 ppm/K + 0.1 % allowance)','pass':b is not None and all(abs(window[k][i]-v[i])<=.0005 for k,v in exp.items() for i in (0,1)),'detail':{k:[round(x,4) for x in window[k]] for k in exp}})
w25={r:('RT1206BRD07' if r in ('R3','R4','R5','R6','R7','R8') else '')+'X' for r in MPN}
whatif={'R2_basis_25ppm_no_allowance':budget(w25,0),'25ppm_with_allowance':budget(w25),'10ppm_no_allowance':budget(None,0),'REF5025AIDR':budget(None,SOLDER,REFGRADE['REF5025AIDR'])}
window['what_if']={k:({kk:[round(x,4) for x in v[kk]] for kk in ('low_corner_V','high_corner_V')} | {'inside_4V75_5V25':inside(v)}) for k,v in whatif.items()}
neg.append(dict(mutation='window resistors 25 ppm/K (RT1206BRD07) with 0.1 % allowance',target_check='Rail-window tolerance stays inside ADC static limits',detected=not inside(whatif['25ppm_with_allowance'])))
# R3: with 10 ppm/K window resistors the standard grade REF5025AIDR stays inside 4.75..5.25 V by only 1.6 mV (what_if); U2 stays
# REF5025IDR by decision (29.09) and the pin/value check above, so AIDR is no longer a window negative control.
# 5VA margin against the TSR 2-2450 (review P5-02): 5V_SYS 5.000 V, +-2 % setting, +-0.7 % drift at 60 C, 12..20 mA x 1R.
margin={}
for name,v in [('TSR -2 %, 25 C',5*.98),('TSR -2 %, 60 C',5*(.98-.007)),('TSR +2 %, 25 C',5*1.02),('TSR +2 %, 60 C',5*(1.02+.007))]:
 lo=[v-i for i in (.012,.020)]
 margin[name]={'5VA_V':[round(x,4) for x in lo],'to_low_corner_mV':round((min(lo)-window['low_corner_V'][1])*1000,1),'to_high_corner_mV':round((window['high_corner_V'][0]-max(lo))*1000,1)}
window['tsr_margin']=margin
channels={}
for name,rs,rb,c in [('MOTOR',300e3,100e3,220e-12),('SENSOR',100e3,math.inf,220e-12),('VSENSE',499e3,100e3,220e-12),('AUX_HI',300e3,100e3,220e-12),('AUX_LO',100e3,math.inf,220e-12)]:
 gain=1+rs/rb+rs/5e6
 channels[name]={'source_R_ohm':rs,'shunt_R_ohm':None if math.isinf(rb) else rb,'inverse_gain':gain,'estimated_input_referred_bias_V':rs*2/5e6,'external_RC_pole_Hz':1/(2*math.pi*(1/(1/rs+1/rb+1/5e6))*c),'scope':'5Mohm to approx 2V equivalent input model; final two-point calibration is mandatory.'}
# 1.10 (local review): ratio budget of each divider with the parts chosen (0.1 %, 25 ppm/K, RT1206BRD07) and the same 0.1 % soldering /
# ageing allowance per resistor as the window. k = Rs/Rb/(1+Rs/Rb) is the sensitivity of the gain to opposite resistor errors; the 5 Mohm
# AD7606B input (its own tolerance is a calibration item, ODBIOR step 12) is left out. Report only: the channels are calibrated in two points.
for name,v in channels.items():
 rs,rb=v['source_R_ohm'],v['shunt_R_ohm'];k=0.0 if rb is None else (rs/rb)/(1+rs/rb)
 v['divider_budget']={'sensitivity_k':round(k,4),'tolerance_pct':round(2*.001*k*100,3),'tolerance_plus_allowance_pct':round(2*(.001+SOLDER)*k*100,3),
                      'drift_ppm_per_K':round(2*TCR['RT1206BRD07']*1e6*k,1),'drift_25_to_60C_pct':round(2*TCR['RT1206BRD07']*35*k*100,3),
                      'note':'worst case, opposite errors of the two resistors; single-resistor channels depend on the ADC input impedance only'}
report={'checks':out,'negative_controls':neg,'truth_table_rows':16,'channels':channels,'window':window}
(P/'verification/electrical-checks.json').write_text(json.dumps(report,indent=2)+'\n')
bad=[c['name'] for c in out if not c['pass']];miss=[c['mutation'] for c in neg if not c['detected']]
print('Electrical',len(out)-len(bad),'/',len(out),'mutations',len(neg)-len(miss),'/',len(neg));assert not bad and not miss,(bad,miss)
