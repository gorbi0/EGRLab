"""Read-only P03 review: independently inspect exported nets and actual PCB.
Run with KiCad Python, from any cwd. No generator imports or source mutations.
"""
from pathlib import Path
import json, hashlib, xml.etree.ElementTree as ET, ast, math, collections, heapq, sys
import pcbnew as p

P = Path(__file__).resolve().parent
S = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else P / 'snapshot'
E = P / 'evidence'
def sha(f): return hashlib.sha256(f.read_bytes()).hexdigest()
manifest = json.loads((S / 'release-manifest.json').read_text(encoding='utf8'))
manifest_bad = [k for k,v in manifest['files'].items() if not (S/k).is_file() or sha(S/k)!=v]
root = ET.parse(E/'fresh-netlist.xml').getroot()
nets = {n.get('name').split('/')[-1]: [(v.get('ref'),v.get('pin')) for v in n.findall('node')] for n in root.findall('./nets/net')}
pin = {t:n for n,ns in nets.items() for t in ns}
parts = json.loads((S/'docs/parts.json').read_text(encoding='utf8'))
def bias(n):
    result=[]
    for r,pp in nets.get(n,[]):
        if r.startswith('R'):
            ends=[x for x,ns in nets.items() if any(ref==r for ref,num in ns)]
            result.append({'ref':r,'value':parts[r]['value'],'nets':ends})
    return result
outputs=['ADC_RESET_SRC','MEAS_EN_SRC','MEAS_BANK','ADC_CS_SRC','ADC_SCLK_SRC','ADC_SDI_SRC','ADC_CONVST_SRC','TC1_CS_SRC','TC2_CS_SRC','SPI3_SCLK_SRC','SPI3_MOSI_SRC','CURRENT_CS_N','SD_CS']
inputs=['INTERLOCK','TEST_KEY','ENA_DIAG','ENB_DIAG','CAN_RX','ADC_BUSY','ADC_DOUTA','SPI3_MISO','HW_ARMED','SENSOR_HEALTHY','LOGGER_CLEAR','TEST_PRESENT']
record={
    'manifest_files':len(manifest['files']), 'manifest_mismatches':manifest_bad,
    'critical_outputs':{n:{'nodes':nets[n],'resistors':bias(n)} for n in outputs},
    'receiver_inputs':{n:{'nodes':nets[n],'resistors':bias(n)} for n in inputs},
    'reset_nodes':nets['SUP_N'], 'M1_reset_header_net':pin.get(('M1','J1-3')),
    'power_5V_nodes':nets['5V_SYS'],
    'fresh_erc_count':sum(len(x['violations']) for x in json.loads((E/'fresh-erc.json').read_text())['sheets']),
    'fresh_drc_counts':{k:len(v) for k,v in json.loads((E/'fresh-drc.json').read_text()).items() if k in ['violations','unconnected_items','schematic_parity']}
}
cross={}
for other,remote,local in [('P04-R1-review','J2','J4'),('P05-R1-review','J1','J1')]:
    q=E/'integration-reference'/f'{other}-parts.json'
    if q.exists():
        dest=json.loads(q.read_text(encoding='utf8'))[remote]['pins']
        cross[other]={'local':local,'remote':remote,'checked_positions':len(dest),
            'mismatches':[(k,parts[local]['pins'].get(k),v) for k,v in dest.items() if parts[local]['pins'].get(k)!=v]}
record['connector_contracts']=cross
# Geometry helper from submitted verifier; crucially call with real VDD pin 6,
# rather than pin 3 used by its DEC list. Does not run submitted verifier.
b=p.LoadBoard(str(S/'eda/P03.kicad_pcb'))
fmap={f.GetReference():f for f in b.GetFootprints()}
source=ast.parse((S/'src/verify_pcb.py').read_text(encoding='utf8'))
names={'pos','xy','net','pad','pxy','route'}
selected=ast.Module(body=[x for x in source.body if isinstance(x,ast.FunctionDef) and x.name in names],type_ignores=[])
exec(compile(selected,'submitted_geometry_helpers','exec'))
record['TPS3808_C3']={
    'VDD_pin':'6', 'tested_pin_in_release':'3 (MR)',
    'straight_to_3_mm':math.dist(pxy('C3','1'),pxy('U3','3')),
    'straight_to_6_mm':math.dist(pxy('C3','1'),pxy('U3','6')),
    'routed_to_3_mm':route('3V3_CORE',('C3','1'),('U3','3')),
    'routed_to_6_mm':route('3V3_CORE',('C3','1'),('U3','6')),
}
(E/'independent-audit.json').write_text(json.dumps(record,indent=2,ensure_ascii=False),encoding='utf8')
print(json.dumps({k:v for k,v in record.items() if k not in ['critical_outputs','receiver_inputs']},indent=2))
