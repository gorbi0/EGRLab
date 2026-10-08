from pathlib import Path
import csv,json,sys,math,subprocess,os
sys.dont_write_bytecode=True
E=Path(__file__).resolve().parent; R=E.parent
F=Path(os.environ['EGR_REVIEW_SOURCE'])/'Rewizje/EGRLab-v6.3-m1'
sys.path.insert(0,str(F/'tools'))
import egrlog
exe=E/'probe_producer.exe'
producer=subprocess.check_output([str(exe)],text=True)
(E/'producer-and-trigger.txt').write_text(producer,encoding='utf-8')
cfg=json.loads(producer.splitlines()[0])
session=E/'synthetic-m1-session'; session.mkdir(exist_ok=True)
(session/'events_000.ndjson').write_text(json.dumps(cfg)+'\n',encoding='utf-8')
rows=[]; expected=[]
for n,amps in enumerate([-1.0,0.0,1.0]):
    volts=[0,0,5,2.5,0,cfg['current_zero']+amps*cfg['current_volts_per_amp'],13.5,0]
    raw=[round((v-o)/g*32768/fs) for v,o,g,fs in zip(volts,cfg['offset'],cfg['gain'],cfg['full_scale'])]
    expected.append((raw[5]*cfg['full_scale'][5]/32768*cfg['gain'][5]+cfg['offset'][5]-cfg['current_zero'])/cfg['current_volts_per_amp'])
    rows.append((1000+n*500,n,*raw,65535,0,0,2,0,1))
egrlog.write_log(session/'samples_000.egr',rows,version=5,synthetic=True)
inspection=egrlog.inspect(session)
warnings=egrlog.export(session,E/'m1-current-export.csv')
report_warnings=egrlog.report(session,E/'m1-current-report.html',full=True)
with (E/'m1-current-export.csv').open() as f: exported=list(csv.DictReader(f))
result={'synthetic':True,'producer':'unmodified control_build_config + json_config',
        'inspect':inspection,'local_current':cfg['local_current'],'voltage_calibrated':cfg['voltage_calibrated'],
        'current_calibrated':cfg['current_calibrated'],'current_valid':cfg['current_valid'],
        'expected_current_A':expected,'exported_current_A':[x['current_a'] for x in exported],
        'exported_current_out_V':[x['current_out_v'] for x in exported],
        'export_warnings':warnings,'report_warnings':report_warnings}
(E/'m1-reader-repro.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
print(producer.splitlines()[1:])
