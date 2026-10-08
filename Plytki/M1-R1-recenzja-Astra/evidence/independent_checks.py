from pathlib import Path
import hashlib,json,shutil,subprocess,sys,urllib.request

E=Path(__file__).resolve().parent; R=E.parent
S=Path('C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-do-recenzji')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
P=S/'Plytki/M1-R1-review'; C=S/'Plytki/M1-PCB-R1-zamowienie/projekt'
diff=[]
for p in P.rglob('*'):
    if p.is_file():
        q=C/p.relative_to(P)
        if not q.exists() or sha(p)!=sha(q):diff.append(p.relative_to(P).as_posix())
extra=[p.relative_to(C).as_posix() for p in C.rglob('*') if p.is_file() and not (P/p.relative_to(C)).exists()]
(E/'source-copy-check.json').write_text(json.dumps({'different_or_missing':diff,'extra_in_production':extra},indent=2))
print('Production copy differences:',diff,'extra:',extra)
D=E/'datasheets';D.mkdir(exist_ok=True)
urls={
 'waveshare.pdf':'https://files.waveshare.com/wiki/ESP32-S3-DEV-KIT-N8R8/ESP32-S3-DEV-KIT-N8R8-schematic.pdf',
 'tps2553.pdf':'https://www.ti.com/lit/ds/symlink/tps2553.pdf',
 'wsk2512.pdf':'https://www.vishay.com/docs/30108/wsk2512.pdf',
}
for name,url in urls.items():
    if not (D/name).exists():
        try: urllib.request.urlretrieve(url,D/name)
        except Exception as ex:print('Download failed',name,ex)
Q=R/'regen';
if not Q.exists():shutil.copytree(P,Q)
pro=Q/'eda/M1.kicad_pro'; before=json.loads(pro.read_text())
command=[sys.executable,str(Q/'src/build_schematic.py')]
run=subprocess.run(command,capture_output=True,text=True)
(E/'schematic-regeneration.log').write_text(run.stdout+run.stderr)
after=json.loads(pro.read_text())
result={'command':command,'returncode':run.returncode,'keys_before':list(before),'keys_after':list(after),
        'board_design_settings_lost':'board' in before and 'board' not in after,
        'net_settings_lost':'net_settings' in before and 'net_settings' not in after,
        'source_unchanged':sha(P/'eda/M1.kicad_pro')==sha(C/'eda/M1.kicad_pro')}
(E/'project-rules-regeneration.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result))
