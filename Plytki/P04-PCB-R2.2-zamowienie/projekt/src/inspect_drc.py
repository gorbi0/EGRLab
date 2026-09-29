import json,collections,sys
from pathlib import Path
P=Path(__file__).resolve().parents[1]
d=json.loads((P/(sys.argv[1] if len(sys.argv)>1 else 'routing/critical-drc.json')).read_text(encoding='utf-8'))
print(collections.Counter(x['type'] for x in d['violations']),'unconnected',len(d.get('unconnected_items',[])))
for v in d['violations']:
 if v['type'] not in ['silk_overlap','silk_over_copper','lib_footprint_mismatch','lib_footprint_issues']:
  print(v['type'],v['description'],[i['description'] for i in v.get('items',[])])
