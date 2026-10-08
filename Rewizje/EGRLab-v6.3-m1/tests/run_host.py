"""Reproducible host checks; requires Python 3 and GCC or TinyCC on PATH."""
import argparse,json,subprocess,sys
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--cc',default='gcc');a=p.parse_args()
r=Path(__file__).resolve().parents[1];out=r/'verification';main=r/'firmware/main'
tiny='tcc' in Path(a.cc).name
extra=['-I',str(out/'host-tcc-include')] if tiny else []
results=[]
for name,sources in [('test_control',['control.c']),('test_runtime',['control.c','profile.c','jsonlog.c','measure.c','trigger.c']),('test_health',['control.c']),('test_obd',['obd.c'])]:
    exe=out/(name+'.exe')
    cmd=[a.cc,'-std=c11','-DHAS_IO_GUARD',*extra,'-I',str(main),str(r/'tests'/(name+'.c'))]+[str(main/s) for s in sources]
    subprocess.run(cmd+([] if tiny else ['-lm'])+['-o',str(exe)],check=True)
    run=subprocess.run([str(exe)],capture_output=True,text=True,check=True)
    for line in run.stdout.splitlines():
        if line.startswith('{'):json.loads(line,parse_constant=lambda x:(_ for _ in ()).throw(ValueError(x)))
    (out/(name+'-results.txt')).write_text(run.stdout,encoding='utf-8');results.append(run.stdout.splitlines()[-1])
for probe in ['probe_adc','probe_storage','probe_drive','probe_review_m1']:   # 6.3.1-m1: regresje recenzji M1-R1   # 6.3-m1: probe_current (MCP3201) -> probe_drive (M-05..M-07)
    run=subprocess.run([sys.executable,str(r/'tests'/(probe+'.py')),'--cc',a.cc,'--out',str(out)],capture_output=True,text=True)
    if run.returncode:sys.exit(run.stdout+run.stderr)
    results.append(run.stdout.splitlines()[-1])
print('\n'.join(results))
