"""Recenzja P04-R1: tabela pinów każdej części z eksportu KiCad (verification/P04.xml) do ręcznego odtworzenia bramek.
Uruchomienie: python logika_z_netlisty.py ../../P04-R1-review/verification/P04.xml"""
import xml.etree.ElementTree as ET, collections, sys
r = ET.parse(sys.argv[1]).getroot()
pins = collections.defaultdict(dict)
for n in r.findall('./nets/net'):
    for x in n.findall('node'):
        pins[x.get('ref')][x.get('pin')] = n.get('name').split('/')[-1]
for c in sorted(r.findall('./components/comp'), key=lambda c: c.get('ref')):
    ref = c.get('ref'); p = pins.get(ref, {})
    print(f"{ref:5s} {c.findtext('value')[:24]:24s}", ' '.join(f'{k}:{v}' for k, v in sorted(p.items(), key=lambda kv: int(kv[0]) if kv[0].isdigit() else 999)))
