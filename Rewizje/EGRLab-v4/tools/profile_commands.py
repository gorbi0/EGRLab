"""Convert a measured calibration JSON to console commands; never sends commands.
Example: python tools/profile_commands.py measured.json --out measured.txt
"""
import argparse,json,math,re
from pathlib import Path

def commands(p):
    if p.get('schema')!=4: raise ValueError('schema musi wynosic 4')
    def num(v,low,high):
        if not isinstance(v,(int,float)) or isinstance(v,bool) or not math.isfinite(v) or not low<=v<=high:
            raise ValueError(f'niewazna kalibracja: {v!r}; oczekiwano {low}..{high}')
        return format(v,'.9g')
    for key in ('valve_id','adapter_id'):
        if not re.fullmatch(r'[A-Za-z0-9_-]{1,23}',p.get(key,'')) or p[key]=='SET_ME':raise ValueError('Uzupelnij '+key)
    lines=['stop',f'bind {p["valve_id"]} {p["adapter_id"]}']
    for b in range(2):
        if len(p['gain'][b])!=8 or len(p['offset'][b])!=8:raise ValueError('osiem kanalow na bank')
        for j in range(8):lines.append(f'cal {b} {j} {num(p["gain"][b][j],.1,20)} {num(p["offset"][b][j],-2,2)}')
        lines.append(f'currentcal {b} {num(p["current_zero"][b],1,4)}')
        lines.append(f'auxcal {b} {num(p["aux_gain"][b],.1,20)} {num(p["aux_offset"][b],-2,2)}')
    a,i,t=p['limits'];lines.append(f'limits {num(a,.001,.35)} {num(i,.001,3.5)} {num(t,10,60)}')
    if not isinstance(p.get('metric_qualified'),bool):raise ValueError('metric_qualified musi byc bool')
    lines.extend([f'metric {int(p["metric_qualified"])}','save','profile'])
    return '\n'.join(lines)+'\n'

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('json',type=Path);parser.add_argument('--out',type=Path,required=True);a=parser.parse_args()
    try:a.out.write_text(commands(json.loads(a.json.read_text(encoding='utf-8'))),encoding='utf-8')
    except (ValueError,KeyError,TypeError,IndexError) as e:parser.exit(2,str(e)+'\n')
