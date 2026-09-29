"""Package checked results; does not rerun tests or approve physical hardware."""
from pathlib import Path
import argparse, difflib, hashlib, json, platform, zipfile
from pypdf import PdfReader

P=Path(__file__).resolve().parents[1]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads((P/p).read_text(encoding='utf-8-sig'))
def write(p,s): (P/p).write_text(s,encoding='utf-8')

ap=argparse.ArgumentParser()
ap.add_argument('--history-root',type=Path,required=True,help='Existing EGRLab/Plytki; read only')
args=ap.parse_args()
history=[]
for rev in ['P01-R1-review','P01-R2-review']:
    old=args.history_root/rev
    manifest=json.loads((old/'release-manifest.json').read_text(encoding='utf-8-sig'))
    mismatches=[r for r,h in manifest['files'].items() if not (old/r).is_file() or sha(old/r)!=h]
    known_settings_change=(rev=='P01-R1-review' and mismatches==['eda/P01.kicad_pro']
        and sha(old/'eda/P01.kicad_pro')=='22e7d071b4da09e562dedfc02bcbd2e0f4181ddc7521be5d9e274a6f851f43d0')
    assert not mismatches or known_settings_change,(rev,mismatches)
    archive=args.history_root/(rev+'.zip')
    expected=(args.history_root/(rev+'.zip.sha256')).read_text(encoding='utf-8-sig').split()[0].lower()
    assert sha(archive)==expected,(rev,'archive SHA mismatch')
    if known_settings_change:
        with zipfile.ZipFile(archive) as z:
            name=next(n for n in z.namelist() if n.endswith('eda/P01.kicad_pro'))
            before=z.read(name).decode();after=(old/'eda/P01.kicad_pro').read_text()
        write('verification/R1-project-settings.diff',''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='R1 released archive',tofile='R1 current settings; preserved')))
    history.append({'release':rev,'files_verified':len(manifest['files'])-len(mismatches),'files_in_manifest':len(manifest['files']),
                    'mismatches':mismatches,'known_settings_change':known_settings_change,
                    'archive_sha256':expected,'archive_pass':True,'all_files_match_manifest':not mismatches})
write('verification/history-preserved.json',json.dumps(history,indent=2)+'\n')

counts={}
for name in ['package-checks','release-checks','r3-checks','dynamics','recovery']:
    d=read('verification/'+name+'.json')
    assert d['pass'] and all(c['pass'] for c in d['checks']),name
    counts[name]=len(d['checks'])
erc=read('verification/erc.json')
violations=[v for s in erc['sheets'] for v in s['violations']]
assert not violations,violations
connect=read('verification/connectivity.json');assert not connect['errors']
rec=read('verification/recovery.json');dyn=read('verification/dynamics.json')
assert rec['xml_sha256']==sha(P/'verification/P01.xml')
assert rec['contract_sha256']==sha(P/'integration/P02-HOLD/contract.json')
assert read('verification/hold-budget.json')['pass']
assert all(c['pass'] for c in read('verification/bounds.json')['checks'])
pdfs={}
for fn,n in [('P01-R3-schemat.pdf',3),('P02-HOLD-C1-polaczenia.pdf',1)]:
    f=P/'output/pdf'/fn;r=PdfReader(f)
    assert len(r.pages)==n
    assert all(len(p.extract_text())>300 for p in r.pages)
    pdfs[fn]={'pages':n,'sha256':sha(f)}
cold=next(r for r in rec['results'] if r['cold_start'])
hb=read('verification/hold-budget.json')
write('verification/QA.md',f'''# Raport wydania P01-R3-review

23.09.2026. Schemat i dokumentacja przed layoutem; sprzęt NIE ZBADANO.

| Kontrola | Wynik |
|---|---|
| Eksport CAD | {connect['components']} elementów, {connect['terminals']} końcówki, {connect['nets']} sieci; zgodny z bazą i jawną deltą |
| ERC KiCad 10.0.6 | 0 naruszeń w raporcie; nie rozszerzano listy domyślnie pomijanych kategorii |
| Kontrole pakietu | {counts['package-checks']} PASS, w tym 11 celowo wprowadzonych błędów wykrytych |
| Spójność wydania | {counts['release-checks']} PASS |
| Delta R2, mechanika i kontrakt HOLD | {counts['r3-checks']} PASS, w tym 4 błędne topologie HOLD odrzucone |
| Dynamika | {counts['dynamics']} kontroli PASS: 26 scenariuszy, wykrycie błędu R1, 3 porównania kroku |
| Powrót, seria, rezerwa, zimny start | {counts['recovery']} kontroli PASS, w tym oczekiwane wykrycie zaniku bez rezerwy i jej wyczerpania |
| Granice algebraiczne | 2 kontrole PASS; Cgd≤2nF jest założeniem, nie gwarantowaną granicą części |
| Podtrzymanie | Warunkowe obliczenie {hb['hold_lower_bound_ms']:.2f} ms wobec wymaganych 50 ms |
| PDF | 3 strony schematu P01 i 1 strona obwodu HOLD; kontrola wizualna w VISUAL-QA.md |

Zimny start modelu przy 11,5 V / 6 W: napięcie banku po 15 s
{cold['hold_at_15s_V']:.3f} V, szczyt prądu kanału Q1 {cold['peak_Q1_channel_A']:.3f} A.
Zerowe napięcie na początku tej próby jest oczekiwane; nie jest testem już
naładowanej rezerwy. C bezpośrednio obciążające P01 to 198+22=220 µF.

Najważniejsze ograniczenia: modele MOS są przybliżone, odbiornik jest modelem
stałej mocy z założonym odcięciem 6,5 V. Nie potwierdzono SOA, termiki, pełnego
toru detektora OVP, odporności automotive, działania przetwornic ani zapisu SD.
P02-HOLD jest obwodem i kontraktem do włączenia w przyszłą P02. Dobór końcowy
bezpiecznika, kodowanie opcjonalnej wiązki, nadzór rezerwy i firmware są zadaniami
etapu P02/CORE. Nie są zamknięte samym raportem PASS.

W pierwszej wersji testu powrotu błędnie oczekiwano zaniku poniżej 7 V dla każdego
Vth. Zachowano wynik w recovery-initial-expectation.json. Test obecny wymaga
wykrycia zaniku w konkretnych przypadkach; nie twierdzi, że każdy egzemplarz
zrestartuje logikę. Kryteriów ciągłości z HOLD nie obniżono.

Logi zawierają ostrzeżenia o niedostępnym profilu/rejestrze KiCad, cache fontów
oraz pliku inicjalizacji ngspice. Eksporty powstały, symulacje zakończyły się,
wektory i końcowe renderowanie zostały sprawdzone. Talii nie oparto na zewnętrznym
spinit. Szczegóły wykonania są w plikach *-run.txt.

Kontrola historii: {history[0]['files_verified']}/{history[0]['files_in_manifest']} plików R1 oraz
{history[1]['files_verified']}/{history[1]['files_in_manifest']} plików R2 zgodnych z manifestami;
oba archiwa zgodne z opublikowanymi SHA256. W obecnym R1 plik P01.kicad_pro
różni się od archiwalnego pustego {{}}: zawiera ustawienia projektu KiCad.
Zachowano jego bieżącą treść; różnica w R1-project-settings.diff. To jedyna
wykryta rozbieżność historii, nie poprawka schematu wykonana w R3. Ten proces
nie zapisuje do R1/R2 ani do recenzji.

Następny etap: layout P01 2L według MECHANIKA/METROLOGIA, kontrola wydruku 1:1
oraz DRC. Do produkcji potrzebna jest osobna kontrola gotowej PCB. P07: HOLD.
''')
write('verification/toolchain.json',json.dumps({'python':platform.python_version(),'kicad':erc['kicad_version'],'ngspice':'46 shared library','pdfs':pdfs,'scope':'Versions observed in this release execution; no bundled runtimes.'},indent=2)+'\n')
files={str(f.relative_to(P)).replace('\\','/'):sha(f) for f in sorted(P.rglob('*')) if f.is_file() and f.name!='release-manifest.json' and f.suffix!='.kicad_prl' and '__pycache__' not in f.parts}
manifest={'release':P.name,'date':'2026-09-23','status':'SCHEMATIC_REVIEW_ONLY_HARDWARE_UNTESTED','files':files}
write('release-manifest.json',json.dumps(manifest,indent=2)+'\n')
archive=P.with_suffix('.zip')
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for rel in list(files)+['release-manifest.json']:z.write(P/rel,P.name+'/'+rel)
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    for rel,h in files.items():assert hashlib.sha256(z.read(P.name+'/'+rel)).hexdigest()==h,rel
archive.with_suffix('.zip.sha256').write_text(sha(archive)+'  '+archive.name+'\n',encoding='ascii')
print(json.dumps({'files':len(files),'archive':str(archive),'archive_sha256':sha(archive),'history':history,'checks':counts,'pdfs':pdfs},indent=2))
