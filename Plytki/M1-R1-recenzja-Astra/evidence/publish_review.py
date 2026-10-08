from pathlib import Path
import hashlib,json,shutil,re
R=Path(__file__).resolve().parent; E=R/'evidence'; W=R/'work'
S=Path('C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-do-recenzji')
O=S.parent/'M1-R1-recenzja-Astra'
assert O.parent==S.parent and O.name=='M1-R1-recenzja-Astra'
if O.exists() and list(O.iterdir()):raise SystemExit('Destination already nonempty: preserve existing review')
O.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((S/'MANIFEST-RECENZJI.json').read_text(encoding='utf-8'))
bad=[name for name,h in manifest['sha256'].items() if sha(S/name)!=h]
assert not bad
(E/'manifest-source-check.json').write_text(json.dumps({'entries':len(manifest['sha256']),'different':bad,'commit':manifest['commit']},indent=2))
firmware_diff=[]
for p in (S/'Rewizje/EGRLab-v6.3-m1/firmware/main').rglob('*'):
    if p.is_file() and p.read_bytes()!=(W/p.relative_to(S)).read_bytes():firmware_diff.append(p.relative_to(S).as_posix())
assert not firmware_diff
(E/'firmware-source-unchanged.json').write_text(json.dumps({'different_main_files':firmware_diff},indent=2))
mapping={'SRC':S,'HW':S/'Plytki/M1-R1-review','FW':S/'Rewizje/EGRLab-v6.3-m1','SPEC':S/'Plytki/M1-specyfikacja','OUT':O}
for name in ['RECENZJA-M1-R1.md','ODTWORZENIE.md']:
    text=(R/name).read_text(encoding='utf-8')
    for k,v in mapping.items():text=text.replace('{'+k+'}',v.as_posix())
    (O/name).write_text(text,encoding='utf-8')
def cp(src,rel):
    target=O/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,target)
for f in E.iterdir():
    if f.is_file() and f.suffix in ['.json','.txt','.log','.py','.c','.cmd','.ps1']:
        cp(f,Path('evidence')/f.name)
H=W/'Plytki/M1-R1-review'
for name in ['erc.json','drc.json','schematic-check.json','m1-checks.json','pcb-checks.json','negative-controls.json','pcb-snapshot.json']:
    cp(H/'verification'/name,Path('evidence/hardware')/name)
cp(H/'routing/return-check.json','evidence/hardware/return-check.json')
C=W/'Plytki/M1-PCB-R1-zamowienie'
for name in ['cam-checks.json','cam-negative-controls.json','drc.json','drc-counts.json','drc-accepted.json','board-fabrication-data.json','export-receipt.json','drill-report.txt']:
    cp(C/'verification'/name,Path('evidence/cam')/name)
F=W/'Rewizje/EGRLab-v6.3-m1'
for f in (F/'verification').glob('*results.txt'):cp(f,Path('evidence/firmware')/f.name)
cp(F/'verification/host-tcc-include/math.h','evidence/firmware/host-tcc-include/math.h')
summary=[]
for v in ['test','logger','core','minimal','wifi']:
    log=(E/f'build-{v}.log').read_text(encoding='utf-8-sig',errors='replace')
    assert 'Project build complete.' in log,v
    config=F/'firmware'/f'sdkconfig.review-{v}'
    cp(config,Path('evidence/firmware')/config.name)
    binary=F/'firmware'/f'build-review-{v}/egrlab_v6.bin'
    summary.append({'variant':v,'exit_code':0,'binary_bytes':binary.stat().st_size,'binary_sha256':sha(binary),'sdkconfig_sha256':sha(config)})
(O/'evidence/firmware/build-summary.json').write_text(json.dumps({'idf':'5.4.3','target':'esp32s3','variants':summary},indent=2))
for name in ['drc.json','erc.json','pcb-checks.json','negative-controls.json','run-layout.log','run-pcb-check.log','QA-PCB.md']:
    cp(R/'regen/verification'/name,Path('evidence/rebuild')/name)
cp(R/'publish_review.py','evidence/publish_review.py')
broken=[]
for name in ['RECENZJA-M1-R1.md','ODTWORZENIE.md']:
    t=(O/name).read_text(encoding='utf-8')
    for link in re.findall(r'\]\((C:/[^)]+)\)',t):
        path=re.sub(r':\d+$','',link)
        if not Path(path).exists():broken.append((name,link))
assert not broken,broken
(O/'evidence/report-validation.json').write_text(json.dumps({'local_links_ok':True,'main_findings':7,'severity_important':6,'severity_minor':1,'source_not_modified':True},indent=2))
files={p.relative_to(O).as_posix():sha(p) for p in O.rglob('*') if p.is_file()}
(O/'MANIFEST-RECENZJI-CODEX.json').write_text(json.dumps({'source_commit':manifest['commit'],'reviewer':'Codex','files':files},indent=2,ensure_ascii=False))
print(json.dumps({'published':str(O),'files':len(files)+1,'report_sha256':sha(O/'RECENZJA-M1-R1.md'),'broken_links':broken},ensure_ascii=False))
