"""P06-R2 (S1): R1 checks adapted to J_BP, Kelvin 2512, 5.11K divider, X7R 1206 and C3 220u.
Independent requirements against the NATIVE exported netlist, including value mutations.
No import of parts.py; expectations come from manufacturers' pin tables and interface contract.
"""
from pathlib import Path
import xml.etree.ElementTree as ET,json,copy,math,itertools,re
P=Path(__file__).resolve().parents[1]
def read():
 root=ET.parse(P/'verification/P06.xml').getroot();c={}
 for x in root.findall('./components/comp'):
  fields={a.get('name'):a.text for a in x.findall('./fields/field')}
  c[x.get('ref')]={'pins':{},'value':x.findtext('value'),'mpn':fields.get('MPN',''),'fp':x.findtext('footprint')}
 for n in root.findall('./nets/net'):
  name=n.get('name').split('/')[-1]
  for x in n.findall('node'):c[x.get('ref')]['pins'][int(x.get('pin'))]='NC' if name.startswith('unconnected-') else name
 return c
def val(c,r):
 s=c[r]['value'].split()[0];m=re.fullmatch(r'(\d+(?:\.\d+)?)([mRrKknup]?)(\d*)',s);assert m,(r,s)
 return float(m[1]+('.'+m[3] if m[3] else ''))*{'':1,'R':1,'r':1,'K':1e3,'k':1e3,'m':1e-3,'u':1e-6,'n':1e-9,'p':1e-12}[m[2]]
def check(c):
 out=[]
 def ok(id,v,note=''):out.append({'id':id,'pass':bool(v),'note':note})
 def pins(r,x):return c[r]['pins']==x
 def pair(r,a,b):return set(c[r]['pins'].values())=={a,b}
 JBP={1:'GND',2:'ADC_SCLK',3:'GND',4:'ADC_DOUTA',5:'GND',6:'CS_ILOG_N',7:'GND',8:'LOGGER_CURRENT_OK',9:'GND',10:'5V_SYS',11:'GND',12:'5V_SYS',13:'GND',14:'3V3_IO',15:'GND',16:'GND'}
 ok('IF-JBP',pins('J_BP',JBP),'R2: J1 LV06 + J2 ILOG -> J_BP (task ZADANIE-P06-S1 2).')
 def at(net):return {(r,p) for r,x in c.items() for p,n in x['pins'].items() if n==net}
 ok('JBP-FUNCTIONS',{('U5',5),('R10',1)}<=at('ADC_SCLK') and {('U5',2),('R8',2)}<=at('CS_ILOG_N') and ('R12',2) in at('ADC_DOUTA')
    and {('R19',2),('R20',1)}<=at('LOGGER_CURRENT_OK') and ('R6',1) in at('5V_SYS'),'Each J_BP signal reaches the same element as R1 J1/J2.')
 ok('IF-ISERIES',pins('J3',{1:'ECU_P1',2:'EGR_P1',3:'NC',4:'NC'}))
 ok('INA-SOIC-PINS',pins('U1',{1:'INA_MINUS',2:'GND',3:'REF_BUF',4:'NC',5:'I_L_OUT',6:'5VA_P06',7:'REF_BUF',8:'INA_PLUS'}))
 ok('INA-GAIN-MPN',c['U1']['mpn']=='INA240A2EDRQ1' and 'SOIC-8' in c['U1']['fp'])
 ok('KELVIN',pins('RSH1',{1:'ECU_P1',2:'K_PLUS',3:'K_MINUS',4:'EGR_P1'}) and pair('R1','K_PLUS','INA_PLUS') and pair('R2','K_MINUS','INA_MINUS'))
 ok('SHUNT-VALUE',abs(val(c,'RSH1')-.005)<1e-10 and c['RSH1']['mpn'].startswith('WSK2512R0050') and 'WSK2512' in c['RSH1']['fp'],'R2: Kelvin SMD 2512 (pads 1/4 force, 2/3 sense; geometry checked in verify_s1.py).')
 ok('INPUT-RESISTORS',val(c,'R1')==val(c,'R2')==10 and all(c[r]['mpn'].startswith('RT1206BR') for r in ['R1','R2']),'Matched 0.1 % thin film (Yageo RT ...BR... = 0.1 %).')
 ok('OPAMP-FEEDBACK',pins('U2',{1:'ADC_BUF',2:'ADC_BUF',3:'I_DIV',4:'GND',5:'REF25',6:'REF_BUF',7:'REF_BUF',8:'3V3_P06'}))
 ok('REF-PINS',pins('U10',{1:'GND',2:'REF25',3:'3V3_P06'}) and c['U10']['mpn']=='MCP1525-I/TO')
 def ceff(r):  # X7R 1206: tolerance 10 %, temperature +/-15 %, DC bias at <=3.3 V assumed -30 % (no data sheet in the cloud)
  v=val(c,r);return (v*.9*.85*.7,v*1.1*1.15) if 'X7R' in c[r]['mpn'] else (v*.8,v*1.2)
 lo,hi=ceff('C5')
 ok('REF-COMPENSATION',pair('C5','REF25','GND') and 1e-6<=lo and hi<=10e-6,f'MCP1525 CL 1..10 uF; C5 effective {lo*1e6:.2f}..{hi*1e6:.2f} uF.')
 lo4,hi4=ceff('C4')
 ok('LDO-OUTPUT-CAP',pair('C4','3V3_P06','GND') and lo4>=1e-6,f'MCP1702 COUT >= 1 uF ceramic; C4 effective >= {lo4*1e6:.2f} uF.')
 ok('ADC-PINS',pins('U3',{1:'REF25',2:'ADC_AIN',3:'GND',4:'GND',5:'CS_LOCAL_N',6:'ADC_DOUT',7:'CLK_LOCAL',8:'3V3_P06'}) and c['U3']['mpn']=='MCP3201-BI/P')
 ok('DIVIDER',pair('R3','I_L_OUT','I_DIV') and pair('R4','I_DIV','GND') and val(c,'R3')==val(c,'R4')==5110 and all(c[r]['mpn'].startswith('RT1206BRD') for r in ['R3','R4']),'R2: 5.11K 0.1 % 25 ppm/K (list 2 replacement 1:1 for 5K1); ratio 1:2 unchanged.')
 ok('INA-LOAD-GE10K',(val(c,'R3')+val(c,'R4'))*.999>=10000,'Swing specification uses 10k load to GND; divider 10.22k (10.21k at -0.1 %).')
 tau=val(c,'C1')*val(c,'R3')*val(c,'R4')/(val(c,'R3')+val(c,'R4'))
 ok('LPF',pair('C1','I_DIV','GND') and 1.07e-3<tau<1.33e-3,f'Nominal tau {tau*1e3:.4f}ms / {1/(2*math.pi*tau):.2f}Hz; not a brick-wall anti-alias filter.')
 ok('ADC-DRIVE',pair('R5','ADC_BUF','ADC_AIN') and val(c,'R5')==47 and pair('C2','ADC_AIN','GND') and val(c,'C2')==470e-12)
 ok('LDO',pins('U4',{1:'GND',2:'5VA_P06',3:'3V3_P06'}) and c['U4']['mpn']=='MCP1702-3302E/TO')
 io={r for r,p in c.items() if '3V3_IO' in p['pins'].values()};sr=[r for r in io if r.startswith('R')]
 ok('NO-PARALLEL-LDO',len(sr)==1 and io=={'J_BP',sr[0]} and set(c[sr[0]]['pins'].values())=={'3V3_IO','SRV_3V3_IO'},'3V3_IO only to J_BP.14 and its service resistor (R1: J1.3 and TP4).')
 ok('C3-220U',pair('C3','5VA_P06','GND') and abs(val(c,'C3')-220e-6)<1e-9,'Decision 1.10: 220 uF (was 470 uF).')
 ok('R6-POWER',pins('R6',{1:'5V_SYS',2:'5VA_P06'}) and val(c,'R6')==1 and '1W' in c['R6']['mpn'],'1 R / 1 W lying; C3 charge pulse ~3 mJ.')
 ok('SUP3',pins('U8',{1:'SUP3_N',2:'3V3_P06',3:'GND'}) and c['U8']['mpn']=='MCP120-300DI/TO' and pair('R14','SUP3_N','3V3_P06'))
 ok('SUP5',pins('U9',{1:'SUP5_RAW',2:'5VA_P06',3:'GND'}) and c['U9']['mpn']=='MCP120-450DI/TO' and pair('R13','SUP5_RAW','5VA_P06'))
 ok('DIODE-DIRECTION',pins('D1',{1:'5VA_P06',2:'3V3_P06'}) and pins('D2',{1:'3V3_P06',2:'REF25'}))
 ok('IOFF-MPN',all(c[r]['mpn']=='74LVC125AD,118 (Nexperia)' for r in ['U5','U6']))
 ok('SPI-TRISTATE',pins('U5',{1:'GND',2:'CS_ILOG_N',3:'CS_LOCAL_N',4:'GND',5:'ADC_SCLK',6:'CLK_LOCAL',7:'GND',8:'DOUT_TX',9:'ADC_DOUT',10:'CS_LOCAL_N',11:'NC',12:'GND',13:'3V3_P06',14:'3V3_P06'}) and pair('R12','DOUT_TX','ADC_DOUTA') and val(c,'R12')==47)
 ok('SPI-IDLE',pair('R7','3V3_P06','CS_LOCAL_N') and val(c,'R7')==10000 and pair('R8','3V3_P06','CS_ILOG_N') and val(c,'R8')==100000 and pair('R9','CLK_LOCAL','GND'))
 ok('READY-LEVEL-TRANSLATION',pins('U6',{1:'GND',2:'SUP5_RAW',3:'SUP5_N',4:'GND',5:'SW_SENSE',6:'SHUNT_ENABLED',7:'GND',8:'LOGGER_OK_TX',9:'LOGGER_OK_LOCAL',10:'GND',11:'NC',12:'GND',13:'3V3_P06',14:'3V3_P06'}))
 ok('READY-PULLDOWNS',all(pair(r,n,'GND') and val(c,r)==10000 for r,n in [('R15','SUP5_N'),('R16','SHUNT_ENABLED'),('R17','RAILS_OK'),('R18','LOGGER_OK_LOCAL'),('R20','LOGGER_CURRENT_OK')]))
 ok('READY-SERIES',pair('R19','LOGGER_OK_TX','LOGGER_CURRENT_OK') and val(c,'R19')==100)
 ok('BYPASS-WIRING',pins('SW1',{1:'NC',2:'ECU_P1',3:'EGR_P1',4:'5VA_P06',5:'SW_RAW',6:'GND'}) and 'DPDT ON-ON' in c['SW1']['mpn'] and '10A' in c['SW1']['mpn'] and pins('J4',{1:'ECU_P1',2:'EGR_P1'}) and pins('J5',{1:'5VA_P06',2:'SW_RAW',3:'GND'}))
 ok('WETTING',pair('R21','SW_RAW','GND') and val(c,'R21')==39 and '2W' in c['R21']['mpn'] and 5.25**2/val(c,'R21')<=.5*2 and pair('R22','SW_RAW','SW_SENSE') and val(c,'R22')==1000)
 # Propagate actual gate pin nets. This fails if an input, output or feedback is changed in the XML.
 truths=[]
 for a,b,s in itertools.product([0,1],repeat=3):
  d={'GND':0,'3V3_P06':1,'SUP3_N':a,'SUP5_RAW':b,'SW_SENSE':s}
  for _ in range(6):
   for r in ['U6']:
    p=c[r]['pins']
    for oe,i,o in [(1,2,3),(4,5,6),(10,9,8)]:
     if d.get(p[oe])==0 and p[i] in d:d[p[o]]=d[p[i]]
   p=c['U7']['pins']
   for i,j,o in [(1,2,3),(4,5,6),(9,10,8),(12,13,11)]:
    if p[i] in d and p[j] in d:d[p[o]]=d[p[i]]&d[p[j]]
  truths.append({'rails':[a,b],'measure':s,'observed':d.get('LOGGER_OK_TX'),'expected':a&b&s})
 ok('READY-TRUTH',all(x['observed']==x['expected'] for x in truths),'Eight combinations from exported gate wiring.')
 lo1,hi1=val(c,'C1')*.9*.85,val(c,'C1')*1.1*1.05;rth=lambda k:val(c,'R3')*val(c,'R4')/(val(c,'R3')+val(c,'R4'))*k
 return out,{'tau_band_us':[rth(.999)*lo1*1e6,rth(1.001)*hi1*1e6],'divider_ratio_worst':[.5*(1-.001-50*25e-6),.5*(1+.001+50*25e-6)],'C3_charge_energy_mJ_at_5V25':.5*val(c,'C3')*5.25**2*1e3,'C3_tau_R6_us':val(c,'R6')*val(c,'C3')*1e6,'R21_power_W':{'5V00':5.0**2/val(c,'R21'),'5V25':5.25**2/val(c,'R21')},'5V_SYS_capacitance_uF':{'P06':sum(val(c,r) for r,x in c.items() if r.startswith('C') and '5VA_P06' in x['pins'].values())*1e6,'P05_R3':265.7,'limit_TSR_2_2450':600,'note':'P05 R3 from Plytki/P12-przygotowanie/wyniki/KONTRAKTY.md (486 uF total)'},'tau_us':tau*1e6,'cutoff_hz':1/(2*math.pi*tau),'ideal_counts_per_amp':4096/2.5*.005*50*.5,'input_resistor_gain_factor':3000/3010,'truth_table':truths}
def main():
 c=read();checks,analysis=check(c);mut=[]
 cases=[('wrong INA package pin','U1','pin',8,'5VA_P06'),('wrong gain','U1','mpn',None,'INA240A1EDRQ1'),('shunt 50m','RSH1','value',None,'50m'),('Kelvin from force','R1','pin',1,'ECU_P1'),('wrong divider','R3','value',None,'51K'),('old 5K1 divider','R4','value',None,'5.1K'),('divider 1 %','R3','mpn',None,'RC1206FR-075K11L'),('old filter cap','C1','value',None,'4.7n'),('REF reversed','U10','pin',1,'3V3_P06'),('REF cap missing compensation','C5','value',None,'100n'),('REF cap too large','C5','value',None,'22u'),('LDO cap too small','C4','value',None,'1u'),('ADC CS/DOUT swapped','U3','pin',5,'ADC_DOUT'),('MISO permanently enabled','U5','pin',10,'GND'),('HC in place of LVC','U6','mpn',None,'74HC125'),('AND ready bypassed','U7','pin',5,'3V3_P06'),('wrong bypass common','SW1','pin',2,'NC'),('wetting 39k','R21','value',None,'39K'),('wetting resistor 1 W 2512','R21','mpn',None,'RC2512 39R 1W'),('strong external CS pullup backpowers rail','R8','value',None,'10K'),('missing ready default','R20','pin',2,'3V3_P06'),('wrong 5V supervisor','U9','mpn',None,'MCP120-300DI/TO'),('wrong LDO pin','U4','pin',1,'5VA_P06'),('discharge diode reversed','D1','pin',1,'3V3_P06'),('C3 back to 470u','C3','value',None,'470u'),('3V3_IO tied to local 3V3','R24','pin',2,'3V3_IO'),('J_BP CS on reserve pin','J_BP','pin',16,'CS_ILOG_N'),('J_BP 5V_SYS lost','J_BP','pin',12,'GND'),('ISERIES pin swap','J3','pin',1,'EGR_P1'),('R6 0.6 W','R6','mpn',None,'MF0207FTE-1R 0.6W')]
 for name,r,typ,pin,v in cases:
  t=copy.deepcopy(c)
  if typ=='pin':t[r]['pins'][pin]=v
  else:t[r][typ]=v
  cc,_=check(t);failed=[x['id'] for x in cc if not x['pass']];mut.append({'mutation':name,'caught':bool(failed),'checks':failed})
 rep={'checks':checks,'negative_controls':mut,'analysis':analysis,'scope':'Static circuit/values only; no claim of measured analog/PWM/thermal performance.'}
 (P/'verification/electrical-checks.json').write_text(json.dumps(rep,indent=2))
 print('Electrical',sum(x['pass'] for x in checks),'/',len(checks),'; mutations',sum(x['caught'] for x in mut),'/',len(mut))
 assert all(x['pass'] for x in checks),[x for x in checks if not x['pass']]
 assert all(x['caught'] for x in mut)
if __name__=='__main__':main()
