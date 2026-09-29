"""One-time migration, retained as a reviewable change record. Do not rerun on R2."""
from pathlib import Path
import json, shutil
P=Path(__file__).resolve().parents[1]
f=P/'src/parts.py';s=f.read_text(encoding='utf-8')
s=s.replace('P02 R1 parts','P02 R2 parts')
s=s.replace("'At U5.'", "'At adapter pins; C16 is additionally fitted directly on the U5 adapter.'")
s=s.replace("'Bleeder; bank <1 V after ~19 min. Measure before service.'", "'Bleeder: up to 22 min from 32 V (C +20%, R +1%). Measure before service.'")
s=s.replace("'P02_BANK_DIV', 4: 'GND', 5: 'P02_VPROT_DIV'", "'P02_BANK_CMP', 4: 'GND', 5: 'P02_VPROT_CMP'")
a=s.index("mon('R5'");b=s.index("mon('R12'",a)
s=s[:a]+'''mon('R5', 'ADDED_HOLD_READY', S_R, RFP, '330R / 1%', 'MF0207FTE-330R', {1: '5V_SYS', 2: 'P02_REF25'}, URL['mf0207'], 'TL431 cathode current about 7.6 mA. No capacitor on REF25.')
mon('R6', 'ADDED_HOLD_READY', S_R, RFP, '30K1 / 0.1%', 'MBB0207VD3012BC100', {1: 'HOLD_STORE', 2: 'P02_BANK_DIV'}, 'https://www.vishay.com/doc?28767', 'Precision 0.1%, 25 ppm/K; required for corner limits.')
mon('R7', 'ADDED_HOLD_READY', S_R, RFP, '10K / 0.1%', 'MBB0207VD1002BC100', {1: 'P02_BANK_DIV', 2: 'GND'}, 'https://www.vishay.com/doc?28767', 'Precision 0.1%, 25 ppm/K.')
mon('R8', 'ADDED_HOLD_READY', S_R, RFP, '1M / 1%', 'MF0207FTE-1M', {1: 'P02_BANK_OK', 2: 'P02_BANK_CMP'}, URL['mf0207'], 'Positive feedback to comparator side of R18; no capacitor here.')
mon('C14', 'ADDED_HOLD_READY', S_C, C100N, '10nF / X7R', 'K103K15X7RF53H5', {1: 'P02_BANK_DIV', 2: 'GND'}, URL['k15'], 'Filter BEFORE R18; tau approx 75 us, not the regeneration node.')
mon('R9', 'ADDED_HOLD_READY', S_R, RFP, '38K3 / 0.1%', 'MBB0207VD3832BC100', {1: 'VPROT', 2: 'P02_VPROT_DIV'}, 'https://www.vishay.com/doc?28767', 'Precision 0.1%, 25 ppm/K; required for corner limits.')
mon('R10', 'ADDED_HOLD_READY', S_R, RFP, '10K / 0.1%', 'MBB0207VD1002BC100', {1: 'P02_VPROT_DIV', 2: 'GND'}, 'https://www.vishay.com/doc?28767', 'Precision 0.1%, 25 ppm/K.')
mon('R11', 'ADDED_HOLD_READY', S_R, RFP, '1M / 1%', 'MF0207FTE-1M', {1: 'P02_VPROT_OK', 2: 'P02_VPROT_CMP'}, URL['mf0207'], 'Feedback to comparator side of R19.')
mon('C15', 'ADDED_HOLD_READY', S_C, C100N, '10nF / X7R', 'K103K15X7RF53H5', {1: 'P02_VPROT_DIV', 2: 'GND'}, URL['k15'], 'Filter BEFORE R19; tau approx 79 us.')
mon('R18', 'R2_FILTER_ISOLATION', S_R, RFP, '10K / 1%', 'MF0207FTE-10K', {1: 'P02_BANK_DIV', 2: 'P02_BANK_CMP'}, URL['mf0207'], 'Separates filter capacitance from positive feedback.')
mon('R19', 'R2_FILTER_ISOLATION', S_R, RFP, '10K / 1%', 'MF0207FTE-10K', {1: 'P02_VPROT_DIV', 2: 'P02_VPROT_CMP'}, URL['mf0207'], 'Separates filter capacitance from positive feedback.')
add('R20', 'R2_PROTECTED_TESTPOINT', S_R, 'P02:R_PR02_P17.78', '1K / 2W / 5%', 'PR02000201001JA100', {1: 'HOLD_STORE', 2: 'HOLD_TP'}, 'https://www.vishay.com/docs/28729/pr010203.pdf', 'Local current limiter before TP3; no raw bank test pad. Short at 32 V <=34 mA, <=1.09 W.')
mon('C16', 'R2_U5_LOCAL_BYPASS', S_C, '', '100nF / adapter U5', 'GRM21BR71H104KA01L (0805)', {1: '3V3_IO', 2: 'GND'}, 'https://www.murata.com', 'Fitted on U5 adapter, short local connections to IC pins 14 and 7; inspect before installing adapter.', on_board=False)
''' + s[b:]
s=s.replace("'On = bank >=9.5 V, VPROT >=11.6 V, PSU_OK.'", "'Local voltage status ONLY. Manual 15 s qualification and load acceptance remain required; not integrated into CORE.'")
s=s.replace("('HOLD_STORE', 'P02')", "('HOLD_TP', 'P02')")
s=s.replace("'Probe access. HOLD_STORE: bank energy >=40 J at 32 V; never short.' if net == 'HOLD_STORE'", "'TP3: protected by R20=1k/2W; DMM >=10 Mohm. Bank energy up to 41 J.' if net == 'HOLD_TP'")
# Explicit electrical data consumed independently by the corner checker.
a=s.index('\n\ndef write_tables():')
s=s[:a]+'''
for r, part in PARTS.items():
    if r.startswith('R'):
        part['tolerance'] = .001 if r in ('R6','R7','R9','R10') else (.05 if r in ('R17','R20') else .01)
        part['tcr_ppm'] = 25 if r in ('R6','R7','R9','R10') else (250 if r=='R20' else 100)
PARTS['F1']['mpn']='Schurter 0001.2507 (T2A) + PTF78 holder'
PARTS['F1']['url']='https://www.schurter.com/en/datasheet/typ_SPT_5x20.pdf'
PARTS['F1']['note']='300 VDC / 1500 A; melting I2t typ 9.2 A2s (not a guaranteed clearing limit). Verify pulse coordination on bench.'

''' + s[a:]
f.write_text(s,encoding='utf-8')
shutil.copy2(Path('C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/P01-R3-review/eda/libraries/P01.pretty/R_PR02_P17.78.kicad_mod'),P/'eda/libraries/P02.pretty/R_PR02_P17.78.kicad_mod')
f=P/'src/placement.json';v=json.loads(f.read_text());v.update(R18=v['R8'],R19=v['R11'],R8=[84,94,0],R11=[126.5,72,270],R20=[40.5,24.5,90],TP3=[40.5,3.5,0]);f.write_text(json.dumps(v,indent=2))
f=P/'src/route_critical.py';s=f.read_text();s=s.replace("tr('HOLD_STORE', [(38, 22.5), (37.5, 28)], 0.8)","tr('HOLD_STORE', [(37.5, 28), (40.5, 24.5)], 0.8)\ntr('HOLD_TP', [(40.5, 6.72), (40.5, 3.5)], 0.5)")
s=s.replace("for cand in (n, '/' + n, '/MON/' + n):", "for cand in (n, '/' + n, '/MON/' + n, '/HOLD/' + n, '/LV/' + n):")
f.write_text(s)
for fn in ['build_board.py','run_layout.py','silkscreen.py','verify_pcb.py','cadlib.py']:
 f=P/'src'/fn;s=f.read_text(encoding='utf-8').replace('P02-R1','P02-R2').replace('P02 R1','P02 R2').replace('PCB R1','PCB R2').replace('PCB-R1','PCB-R2')
 if fn=='build_board.py':s=s.replace('Schematic + PCB R1 in one package (Claude); review: Astra','P02-R2: electrical corrections, review by Opus pending')
 if fn=='cadlib.py':
  s=s.replace("fa=90 if a%180 else 0", "fa=0")
  s=s.replace("value=part['display'];orient=a%180", "value=part.get('sch_value',part['display']);orient=a%180")
  s=s.replace("effects='(effects", "if part.get('fields') is not None:\n   ox,oy=part['fields'];tx,ty=mm(x)+ox,mm(y)+oy\n  effects='(effects")
  s=s.replace("('right' if a in [90,180] else 'left')", "'left'")
 if fn=='silkscreen.py':
  s=s.replace("INSIDE = {", "INSIDE = {'R_PR02_P17.78', ")
  s=s.replace("fid.startswith('R_Axial')", "fid.startswith(('R_Axial','R_PR02'))")
  s=s.replace("('HOLD_STORE 40J', 38.4, 19.7, .8, 0, 1.5), ('NIE ZWIERAC!', 38.3, 24.9, .8, 0, 1)","('BANK/1k', 33.5, 3.5, .8, 0, 2)")
  s=s.replace('BANK >=40 J przy 32 V','BANK do 41 J / 32 V')
 if fn=='verify_pcb.py':
  s=s.replace('69 on-board parts','72 on-board parts').replace('len(onboard) == 69','len(onboard) == 72')
  s=s.replace("'TP3.1'", "'R20.1'")
  a=s.index("flt = {");b=s.index("cv = {",a)
  s=s[:a]+'''flt = {'R18.2-U7.3': route('P02_BANK_CMP', ('R18', '2'), ('U7', '3')), 'R19.2-U7.5': route('P02_VPROT_CMP', ('R19', '2'), ('U7', '5'))}
check('Isolating resistors R18/R19 routed <=15mm to comparator; feedback after resistor', all(v is not None and v<=15 for v in flt.values()) and net(pad('R8','2'))=='P02_BANK_CMP' and net(pad('R11','2'))=='P02_VPROT_CMP', flt)
check('TP3 only after R20; no raw HOLD_STORE test pad', net(pad('TP3','1'))=='HOLD_TP' and net(pad('R20','1'))=='HOLD_STORE' and net(pad('R20','2'))=='HOLD_TP' and not any(net(pad(r,'1'))=='HOLD_STORE' for r in fmap if r.startswith('TP')))
''' +s[b:]
  s=s.replace("'HOLD_STORE 40J': (TPS['TP3'], 6, [pxy('J13', '2'), pxy('D2', '2')]), 'NIE ZWIERAC!': (TPS['TP3'], 6, [pxy('J13', '2'), pxy('D2', '2')]),", "'BANK/1k': (TPS['TP3'], 10, [pxy('J13', '2'), pxy('D2', '2')]),")
  s=s.replace("s.startswith('BANK >=40 J')", "s.startswith('BANK do 41 J')")
 f.write_text(s,encoding='utf-8')
print('R2 migration applied. Parts, topology, placements, guarded TP3, checker updated.')
