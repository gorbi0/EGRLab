"""Read-only, independent P02 review: original manifest, baseline and HOLD thresholds.

Run with ordinary Python. The original package is never modified.
DC calculations are analytical examples, not measurements or a SPICE simulation.
"""
from pathlib import Path
import hashlib
import itertools
import json
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
SOURCE = Path('C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/P02-R1-review')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

parts = json.loads((SOURCE / 'docs/parts.json').read_text(encoding='utf-8'))
manifest = json.loads((SOURCE / 'release-manifest.json').read_text(encoding='utf-8'))
bad_files = [r for r, h in manifest['files'].items() if not (SOURCE/r).exists() or sha(SOURCE/r) != h]
snapshot = json.loads((HERE / 'original-sha256.json').read_text())
current = {f.relative_to(SOURCE).as_posix(): sha(f) for f in SOURCE.rglob('*') if f.is_file()}
changed = [r for r in set(snapshot) | set(current) if snapshot.get(r) != current.get(r)]

old = ET.parse(SOURCE/'reference/v6.1-P02-import.xml').getroot()
refs = {c.get('ref'): c.find("./property[@name='SourceRef']").get('value')
        for c in old.findall('./components/comp')}
oldpins = {(refs[n.get('ref')], n.get('pin')): net.get('name').split('/')[-1]
           for net in old.findall('./nets/net') for n in net.findall('node')}

def old_pin(source_ref, pin):
    if source_ref in ('F2', 'F3'): return {'1':'IN', '2':'OUT'}[pin]
    if source_ref in ('M3', 'M4'): return {'1':'VIN','2':'GND','3':'VOUT'}[pin]
    return pin

def normalise_net(net):
    if net is None or net.startswith('unconnected-') or net == 'NC': return 'NC'
    return {'VIN_DC5':'P02_VIN_DC5', 'VIN_DC33':'P02_VIN_DC33'}.get(net, net)

expected_changes = {
    ('F2','1'): ('VPROT','VLOG_RES'), ('F3','1'): ('VPROT','VLOG_RES'),
    ('U6','4'): ('GND','P02_BANK_OK'), ('U6','5'): ('GND','P02_VPROT_OK'),
    ('U6','6'): ('NC','P02_HOLD_QUAL'), ('U6','8'): ('NC','P02_HOLD_READY_INT'),
    ('U6','9'): ('GND','P02_HOLD_QUAL'), ('U6','10'): ('GND','PSU_OK'),
    ('J12','3'): ('NC','HOLD_READY'),
}
actual_changes = {}; checked = 0
for ref, part in parts.items():
    sr = part['source_ref']
    if sr not in refs.values(): continue
    for pin, net in part['pins'].items():
        before = normalise_net(oldpins.get((sr, old_pin(sr, pin))))
        after = normalise_net(net); checked += 1
        if before != after: actual_changes[ref,pin] = (before,after)

contract = json.loads((SOURCE/'reference/contract.json').read_text())
by_source = {q['source_ref']:q for q in parts.values()}
hold_changes = {}
for ref, q in contract['connections'].items():
    want = {k:v for k,v in q.items() if k not in ('MPN','value')}
    if by_source[ref]['pins'] != want: hold_changes[ref] = [want, by_source[ref]['pins']]

def resistance(ref):
    # Explicitly support the values present in this circuit, including 2M2.
    return {'267K':267000.,'348K':348000.,'100K':100000.,'2M2':2200000.,'10K':10000.}[parts[ref]['display'].split(' /')[0]]

def trip(rt, rb, rf, ref=2.495, high=False, rp=10000., supply=3.3, vol=.150):
    vo = (supply/rp + ref/rf)/(1/rp + 1/rf) if high else vol
    return (ref*(1/rt + 1/rb + 1/rf) - vo/rf)*rt

thresholds = {}
for name, rr in [('bank',('R6','R7','R8','R12')), ('vprot',('R9','R10','R11','R13'))]:
    rt,rb,rf,rp = [resistance(r) for r in rr]
    thresholds[name] = {}
    for high in (False, True):
        values = [trip(rt*a, rb*b, rf*c, 2.495*d, high, rp*e)
                  for a,b,c,d,e in itertools.product([.99,1.01],[.99,1.01],[.99,1.01],[.995,1.005],[.99,1.01])]
        thresholds[name]['falling' if high else 'rising'] = {
            'nominal_V':trip(rt,rb,rf,high=high,rp=rp),
            'min_V_R1percent_REF05percent_only':min(values),
            'max_V_R1percent_REF05percent_only':max(values),
        }
    thresholds[name]['RC_ms'] = 1000/(1/rt+1/rb+1/rf)*100e-9

result = {
    'manifest_mismatches':bad_files,
    'original_files_changed':changed,
    'baseline_mapped_components':len(set(refs.values())),
    'baseline_checked_pins':checked,
    'baseline_changes_expected':actual_changes == expected_changes,
    'baseline_changes':[{ 'ref':k[0], 'pin':k[1], 'before':v[0], 'after':v[1] } for k,v in actual_changes.items()],
    'missing_baseline_components':sorted(set(refs.values())-set(by_source)),
    'HOLD_contract_connection_mismatches':hold_changes,
    'thresholds':thresholds,
    'counterexample':{
        'description':'HOLD_READY was asserted, bank now at 8.9 V, VPROT and PSU_OK high. With a permitted tolerance corner BANK_OK remains high.',
        'C_F':.0528,'drop_V':1.2,'Vout_min_V':7.,'load_plus_reserve_W':6.15,
        'hold_ms':1000*.0528*((8.9-1.2)**2-7**2)/(2*6.15),
        'limits':'Illustrative constant-drop model only. Comparator offset, bias current and temperature deliberately omitted; not a complete worst-case analysis or a hardware measurement. Local indication does not control motor ARM.',
    },
}
(HERE/'independent-review-checks.json').write_text(json.dumps(result,indent=2)+'\n')
assert not bad_files and not changed and actual_changes == expected_changes and not hold_changes
assert not result['missing_baseline_components']
print(json.dumps(result,indent=2))
