"""Read actual KiCad-exported nets, compare physical pad-to-net assignments."""
import argparse, collections, json, os, subprocess, xml.etree.ElementTree as ET
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def verify(cli=None):
    C=json.loads((R/'hardware/components.json').read_text(encoding='utf-8'))
    mapping=json.loads((R/'eda/migration-map.json').read_text(encoding='utf-8'));report=[]
    for board in sorted({m['board'] for m in mapping}):
        folder=R/'eda'/board;sch=folder/(board+'.kicad_sch');xml=folder/(board+'.xml');erc=folder/'erc.json'
        if cli:
            for args in [['sch','export','netlist','--format','kicadxml','-o',str(xml),str(sch)],['sch','erc','--format','json','-o',str(erc),str(sch)],['sch','export','svg','-o',str(folder/'preview'),str(sch)]]:
                run=subprocess.run([str(cli),*args],capture_output=True,text=True,encoding='utf-8',errors='replace')
                if run.returncode:raise RuntimeError(run.stdout+run.stderr)
        tree=ET.parse(xml).getroot();by={m['eda_ref']:m for m in mapping if m['board']==board}
        actual={};actual_sets={}
        for net in tree.findall('./nets/net'):
            group=set()
            for node in net.findall('node'):
                ref=node.attrib['ref']
                if ref not in by:continue # only declared non-BOM PWR_FLAGs
                m=by[ref];logical={v:k for k,v in m['pads'].items()}
                pin=logical[node.attrib['pin']];key=(m['component'],pin)
                assert key not in actual,(board,'duplicate',key)
                actual[key]=net.attrib['name'].lstrip('/');group.add(key)
            for key in group:actual_sets[key]=group
        count=0
        for m in by.values():
            for pin,net in C[m['component']]['pins'].items():
                key=(m['component'],pin)
                if net=='NC':assert not actual_sets.get(key,set())-{key},(board,'NC shorted',key)
                else:
                    assert actual.get(key)==net,(board,key,net,actual.get(key));count+=1
        e=json.loads(erc.read_text(encoding='utf-8'));violations=[v for sheet in e['sheets'] for v in sheet['violations']]
        report.append(dict(board=board,components=len(by),connected_pins_checked=count,netlist='MATCH',erc= dict(collections.Counter(v['type'] for v in violations)),erc_errors=sum(v['severity']=='error' for v in violations),erc_warnings=sum(v['severity']=='warning' for v in violations)))
        print(board,'netlist MATCH',len(violations),'ERC findings',flush=True)
    (R/'stabilizacja/evidence/eda-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    return report
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--cli',type=Path);a=p.parse_args();verify(a.cli)
