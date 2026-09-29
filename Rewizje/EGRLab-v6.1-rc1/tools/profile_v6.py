"""Validate three independent profile files and generate reviewable console commands.
No device I/O. Unmeasured calibration values are rejected. Never emits TEST/ARM/qualify.
"""
import argparse,json,math,re
from pathlib import Path

def ident(x):
    if not isinstance(x,str) or not re.fullmatch('[A-Za-z0-9_-]{1,23}',x):raise ValueError('ID: 1..23 ASCII letters/digits/_/-')
    return x
def number(x,lo,hi):
    if isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(x) or not lo<=x<=hi:raise ValueError(f'Measured number required: {lo}..{hi}')
    return x
def commands(hw,valve,session):
    if hw.get('schema')!=6 or valve.get('schema')!=6 or session.get('schema')!=6:raise ValueError('schema 6 required')
    if any(x.get('synthetic') for x in [hw,valve,session]):raise ValueError('Synthetic profiles cannot commission hardware')
    if valve.get('drive_class')!='dc12_analog5' or hw.get('current_driver')!='mcp3201_ina240':raise ValueError('Unsupported hardware/valve driver')
    for module,serial in [('P05',hw['daq_module']),('P06',hw['current'][0]['module_id']),('P07',hw['current'][1]['module_id'])]:
        if hw['modules'][module]['serial']!=serial:raise ValueError(f'{module}: module serial does not match calibration identity')
    lines=['stop',f"bind {ident(valve['valve_id'])} {ident(valve['adapter_id'])}",f"daqmodule {ident(hw['daq_module'])}",f"session {ident(session['vehicle_id'])} {ident(session['test_id'])}"]
    for bank in [0,1]:
        v=hw['voltage'][bank]
        if v.get('accepted') is not True:raise ValueError(f'Voltage bank {bank}: acceptance missing')
        if len(v['gain'])!=8 or len(v['offset'])!=8:raise ValueError('8 voltage channels required')
        for j,(gain,offset) in enumerate(zip(v['gain'],v['offset'])):
            lines.append(f'cal {bank} {j} {number(gain,.1,20):.9g} {number(offset,-2,2):.9g}')
    for pos in [0,1]:
        aux=hw['aux'][pos]
        lines.append(f"auxcal {pos} {number(aux['gain'],.1,20):.9g} {number(aux['offset'],-2,2):.9g}")
    # Calibration edits invalidate acceptance; mark it only after the complete group.
    lines+=['vcalok 0 1','vcalok 1 1']
    for bank in [0,1]:
        c=hw['current'][bank]
        if c.get('accepted') is not True:raise ValueError(f'Current bank {bank}: acceptance missing')
        lines += [f"imodule {bank} {ident(c['module_id'])}",
                  f"iscal {bank} {number(c['adc_gain'],.0001,.01):.9g} {number(c['adc_offset'],-.5,.5):.9g} {number(c['volts_per_amp'],.05,2):.9g}",
                  f"currentcal {bank} {number(c['zero'],1,4):.9g}",f'icalok {bank} 1']
    lim=valve['limits']
    lines += [f"limits {number(lim['duty'],.001,.35):.9g} {number(lim['current_a'],.01,3.5):.9g} {number(lim['temperature_c'],10,60):.9g}",
              f"metric {int(hw.get('current_window_accepted') is True)}",'save','profile']
    return '\n'.join(lines)+'\n'
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('hardware',type=Path);p.add_argument('valve',type=Path);p.add_argument('session',type=Path);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    try:
        objects=[json.loads(x.read_text(encoding='utf-8-sig')) for x in [a.hardware,a.valve,a.session]]
        out=commands(*objects)
        a.out.write_text(out,encoding='ascii')
        a.out.with_suffix('.manifest.json').write_text(json.dumps(dict(hardware=objects[0],valve=objects[1],session=objects[2]),indent=2,ensure_ascii=False),encoding='utf-8')
    except (ValueError,KeyError,TypeError,IndexError) as e:p.exit(2,str(e)+'\n')
if __name__=='__main__':main()
