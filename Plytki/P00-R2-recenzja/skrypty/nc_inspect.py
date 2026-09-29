import json, pathlib
base = pathlib.Path('verification')
r = json.load(open(base / 'negative-controls.json', encoding='utf-8'))
for x in r:
    print(x['control'], '|', [c[:45] for c in x['failed_checks']])
for f in sorted((base / 'negative-controls').glob('*/drc.json')):
    d = json.load(open(f, encoding='utf-8'))
    print(f.parent.name, len(d['violations']), len(d['unconnected_items']), len(d['schematic_parity']),
          sorted({v['type'] for v in d['violations']})[:6], [v['description'][:70] for v in d['schematic_parity']][:2])
