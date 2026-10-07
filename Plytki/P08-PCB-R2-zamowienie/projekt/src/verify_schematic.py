"""Schematic netlist (kicad-cli export) must match parts.py pin-by-pin; ERC must be empty."""
from pathlib import Path
import json, sys, xml.etree.ElementTree as ET
P = Path(__file__).resolve().parents[1]
parts = json.loads((P / 'docs/parts.json').read_text(encoding='utf-8'))
root = ET.parse(P / 'verification/P08.xml').getroot()
got = {}
for n in root.findall('./nets/net'):
    name = n.get('name').split('/')[-1]  # hierarchical prefix removed
    for node in n.findall('node'):
        got[(node.get('ref'), node.get('pin'))] = name
errors = []
comps = {c.get('ref'): c for c in root.findall('./components/comp')}
for ref, p in parts.items():
    if ref not in comps: errors.append(('missing component', ref)); continue
    fp = comps[ref].findtext('footprint') or ''
    if fp != p['footprint']: errors.append(('footprint', ref, fp, p['footprint']))
    for pin, net in p['pins'].items():
        g = got.get((ref, pin))
        ok = (g is not None and g.startswith('unconnected-')) if net == 'NC' else g == net
        if not ok: errors.append(('net', ref, pin, net, g))
extra = sorted(set(comps) - set(parts)); erc = json.loads((P / 'verification/erc.json').read_text())
viol = [v for s in erc['sheets'] for v in s['violations']]
res = {'components': len(comps), 'parts': len(parts), 'pin_checks': sum(len(p['pins']) for p in parts.values()), 'errors': errors, 'extra': extra,
       'erc_sheets': len(erc['sheets']), 'erc_violations': len(viol), 'nets': len(root.findall('./nets/net'))}
(P / 'verification/schematic-check.json').write_text(json.dumps(res, indent=2) + '\n')
print(json.dumps({k: v for k, v in res.items() if k != 'errors'}), 'errors', len(errors)); [print(' ', e) for e in errors[:20]]
sys.exit(1 if errors or extra or viol else 0)
