"""Contract checks independent of build_hardware; no exemptions for power nets.
Run: python stabilizacja/checks.py --baseline (expected failure), or without it.
These checks inspect connectivity, not component authenticity/physical behaviour.
"""
import argparse, collections, copy, csv, json
from pathlib import Path
R = Path(__file__).resolve().parents[1]

def load(folder):
    c=json.loads((folder/'components.json').read_text(encoding='utf-8'))
    with (folder/'wiring.csv').open(encoding='utf-8-sig') as f:w=list(csv.DictReader(f,delimiter=';'))
    with (folder/'connectors.csv').open(encoding='utf-8-sig') as f:k=list(csv.DictReader(f,delimiter=';'))
    return c,w,k

def disconnected(c,w):
    used=collections.defaultdict(set); result={}
    for item in c.values():
        for net in item['pins'].values():
            if net!='NC':used[net].add(item['board'])
    for net,boards in used.items():
        if len(boards)<2:continue
        reached={sorted(boards)[0]}
        pairs=[(r['from_board'],r['to_board']) for r in w if r['net']==net]
        while True:
            previous=set(reached)
            for a,b in pairs:
                if a in reached or b in reached:reached.update([a,b])
            if previous==reached:break
        if boards-reached:result[net]=sorted(boards-reached)
    return result

def check(c,w,k):
    failures={}
    def require(id,condition,message):
        if not condition:failures.setdefault(id,[]).append(message)
    for row in w:
        for s in ['from','to']:
            key=row[s+'_board']+'_'+row[s+'_ref']
            require('W01',c.get(key,{}).get('pins',{}).get(row[s+'_pin'])==row['net'],str(row))
    missing=disconnected(c,w)
    require('T01',not missing,'Disconnected board graph: '+str(missing))
    # Explicit source -> fuse -> harness -> divider contract; deleting the load
    # to hide an unwired net is itself a failure.
    fuse=c.get('P02_F_VSENSE',{}).get('pins',{})
    require('F01',fuse=={'1':'VPROT','2':'VPROT_SENSE'},'No dedicated fused sense source on P02')
    require('F01',c.get('P05_RV1',{}).get('pins',{}).get('1')=='VPROT_SENSE','RV1 lacks physical sense supply')
    require('F01',any(r['cable']=='VSENSE' and r['from_board']=='P02' and r['to_board']=='P05' and r['net']=='VPROT_SENSE' for r in w),'Sense harness absent')
    lv=[r for r in k if r['compatible_group']=='LV']
    for port in lv:
        require('F01', [r['net'] for r in w if r['cable']==port['cable']]==['5V_SYS','GND','3V3_IO','GND'],port['cable']+' LV compatibility broken')
    p=c.get('P03_R_PD_SENSOR_HEALTHY',{}).get('pins',{})
    require('F02',set(p.values())=={'SENSOR_HEALTHY','GND'},'Receiver needs pull-down')
    require('F02',not any(x['board']=='P03' and x['kind'] in ['res','R'] and 'SENSOR_HEALTHY' in x['pins'].values() and '3V3_CORE' in x['pins'].values() for x in c.values()),'Receiver has pull-up')
    pins=c['P08_U_READY']['pins'];tx=c['P08_U_RX1']['pins']
    require('F02',(pins['9'],pins['10'],pins['8'])==('SENSOR_OK','SENSOR_FAULT_LOCAL_N','SENSOR_HEALTH_LOCAL'),'Fault must qualify health without inverting FAULT_N')
    require('F02',(tx['4'],tx['5'],tx['6'])==('GND','SENSOR_HEALTH_LOCAL','SENSOR_HEALTHY'),'No enabled Ioff transmitter')
    for key in ['P04_J_PANELSAFEA','P11_J_PANELSAFEB']:
        require('F03',all(c[key]['pins'].get(str(p))=='NC' for p in [5,6]),key+' dangling diagnostic copies')
        require('F03',len(c[key]['pins'])==10,'Keep distinct 10-position body')
    a=next(x for x in k if x['cable']=='SUPPLY');b=next(x for x in k if x['cable']=='VMOTOR')
    require('F04',(a['family'],a['positions'],a['key_pin'])!=(b['family'],b['positions'],b['key_pin']),'Power plugs still mechanically identical')
    # Ports consisting only of contacts: pass-through needs >=2 local ends.
    # Four enumerated one-ended exceptions, no exemptions for whole net classes.
    expected={('AL1','GND'):'external shield',('AL2','GND'):'external shield',('P04','5V_SYS'):'unused position of standard LV',('P09','5V_SYS'):'unused position of standard LV'}
    local=collections.defaultdict(list)
    for item in c.values():
        for net in set(item['pins'].values())-{'NC'}:local[(item['board'],net)].append(item)
    for point,items in local.items():
        if all(x['kind'] in ['connector','termination','testpad','J'] for x in items) and len(items)<2:
            require('T02',point in expected,'Unconsumed connector net: '+str(point))
    return failures

def mutations(c,w,k):
    results={}
    cases={
      'remove_VSENSE_wire':lambda a,b,d:b.__setitem__(slice(None),[r for r in b if not(r['cable']=='VSENSE' and r['net']=='VPROT_SENSE')]),
      'isolate_GND_P05':lambda a,b,d:b.__setitem__(slice(None),[r for r in b if not(r['net']=='GND' and 'P05' in [r['from_board'],r['to_board']])]),
      'isolate_5V_P08':lambda a,b,d:b.__setitem__(slice(None),[r for r in b if not(r['net']=='5V_SYS' and r['to_board']=='P08')]),
      'reverse_wire_pin':lambda a,b,d:b[0].update(from_pin='999'),
      'remove_fault_pulldown':lambda a,b,d:a.pop('P03_R_PD_SENSOR_HEALTHY'),
      'invert_fault_gate':lambda a,b,d:a['P08_U_READY']['pins'].update({'10':'GND'}),
      'restore_dead_panel_pin':lambda a,b,d:a['P04_J_PANELSAFEA']['pins'].update({'5':'LOGGER_CLEAR'}),
      'swap_LV_voltage':lambda a,b,d:a['P05_J_LV05B']['pins'].update({'1':'VPROT'}),
      'remove_VBAT_load':lambda a,b,d:a.pop('P05_RV1'),
    }
    for name,mutate in cases.items():
        a,b,d=copy.deepcopy((c,w,k));mutate(a,b,d);failure=check(a,b,d)
        assert failure,'Mutation not detected: '+name
        results[name]=sorted(failure)
    # A membership-only checker misses two internally connected clusters.
    a={f'{i}_R':dict(board=i,pins={'1':'POWER'}) for i in ['A','B','C','D']}
    b=[dict(net='POWER',from_board=x,to_board=y) for x,y in [('A','B'),('C','D')]]
    assert disconnected(a,b)=={'POWER':['C','D']}
    results['two_disconnected_power_clusters']=['T01']
    return results

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--baseline',action='store_true');parser.add_argument('--output');args=parser.parse_args()
    c,w,k=load(R/'stabilizacja/baseline' if args.baseline else R/'hardware')
    failure=check(c,w,k)
    out=dict(target='frozen-V6' if args.baseline else 'working-release',failures=failure,mutations={} if failure else mutations(c,w,k))
    text=json.dumps(out,indent=2,ensure_ascii=False);print(text)
    if args.output:Path(args.output).write_text(text,encoding='utf-8')
    raise SystemExit(bool(failure))
