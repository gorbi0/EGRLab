"""Reproduce review evidence in a NEW scratch directory. Does not fix firmware."""
from pathlib import Path
import argparse, shutil, subprocess, os, sys, json, hashlib

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',type=Path,required=True)
    ap.add_argument('--tcc',type=Path,required=True)
    ap.add_argument('--work',type=Path,required=True)
    a=ap.parse_args()
    evidence=Path(__file__).resolve().parent/'evidence'
    source=a.source.resolve(); work=a.work.resolve(); cc=a.tcc.resolve()
    if work.exists(): raise SystemExit('Choose a NEW --work directory; review evidence is immutable.')
    if not cc.is_file(): raise SystemExit('TinyCC executable does not exist.')
    main_dir=source/'Rewizje/EGRLab-v6.3-m1/firmware/main'
    if not (main_dir/'app_main.c').is_file(): raise SystemExit('Wrong --source directory.')
    snap=json.loads((evidence/'source-snapshot.json').read_text(encoding='utf-8'))
    actual={str(p.relative_to(source)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in source.rglob('*') if p.is_file()}
    if actual != snap['files']: raise SystemExit('Input differs from reviewed 531-file source. Use an explicit new review for changed inputs.')
    work.mkdir(parents=True)
    for name in ('probe_producer.c','probe_reader.py'):
        shutil.copy2(evidence/name,work/name)
    shutil.copytree(evidence/'host-tcc-include',work/'host-tcc-include')
    shutil.copytree(evidence/'firmware',work/'firmware')
    env=dict(os.environ, EGR_REVIEW_SOURCE=str(source), EGR_REVIEW_TCC=str(cc), PYTHONDONTWRITEBYTECODE='1')
    commands=[]; output=[]
    def run(command):
        p=subprocess.run([str(x) for x in command],env=env,capture_output=True,text=True,encoding='utf-8',errors='replace')
        commands.append({'command':[str(x) for x in command],'returncode':p.returncode})
        output.append(p.stdout+p.stderr)
        print(p.stdout+p.stderr,end='')
        if p.returncode: raise RuntimeError(f'Probe failed: {command}')
    try:
        run([cc,'-std=c11','-I',work/'host-tcc-include','-I',main_dir,work/'probe_producer.c',
             main_dir/'control.c',main_dir/'jsonlog.c',main_dir/'trigger.c',main_dir/'profile.c','-o',work/'probe_producer.exe'])
        run([sys.executable,work/'probe_reader.py'])
        run([sys.executable,work/'firmware/probe_independent.py'])
        run([sys.executable,work/'firmware/probe_adc_metadata.py'])
        r=json.loads((work/'m1-reader-repro.json').read_text())
        assert r['exported_current_A']==['','',''] and r['export_warnings']==[]
        assert r['inspect']['records']==3 and r['current_valid'] and r['voltage_calibrated'] and r['current_calibrated']
        t=(work/'producer-and-trigger.txt').read_text()
        for s in ('UNCALIBRATED_VECTOR_MASK=9','REAL_LOW_REF_MASK=1','vcal=0 ical=1 metric=1 qualified=0',
                  'qualify_predicate_without_HARDWARE_ACCEPTED=1','now_I=0.800000A zero_I=0.000000A'):
            assert s in t,s
        t=(work/'firmware/independent_firmware_probe-results.txt').read_text()
        assert 'watchdog_feeds=400 physical_button_reads=0' in t
        t=(work/'firmware/adc_metadata_probe-results.txt').read_text()
        assert 'record[1]: sequence=2 config_id=17 flags=0 SAMPLE_INVALID=0 SAMPLE_GAP=0' in t
        print('All five NEW review findings reproduced on the unchanged R1 source.')
    finally:
        (work/'run.log').write_text('\n'.join(output),encoding='utf-8')
        (work/'run.json').write_text(json.dumps(commands,indent=2),encoding='utf-8')
    after={str(p.relative_to(source)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in source.rglob('*') if p.is_file()}
    assert after==actual,'Source changed during reproduction.'

if __name__=='__main__': main()
