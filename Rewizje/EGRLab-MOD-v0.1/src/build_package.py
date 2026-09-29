from pathlib import Path
import csv, json, hashlib, re, zipfile

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT.parent
SOURCE = BASE / 'EGRLab-v4.1'
PG = BASE / 'EGRLab-PWR-THT-v1'
(ROOT/'verification').mkdir(exist_ok=True)

def table(path, prefix):
    text = path.read_text(encoding='utf-8')
    block = text[text.index(prefix):].split('\n\n', 1)[0]
    rows = [[c.strip() for c in line.strip().strip('|').split('|')] for line in block.splitlines() if line.startswith('|')]
    return [rows[0], *rows[2:]]

def csvout(name, rows):
    with (ROOT/name).open('w', encoding='utf-8-sig', newline='') as f:
        csv.writer(f, delimiter=';').writerows(rows)

mods = table(ROOT/'README.md', '| PCB |')
links = table(ROOT/'INTERFEJSY.md', '| Wiązka |')
stages = table(ROOT/'KOLEJNOSC.md', '| Etap |')
csvout('moduly.csv', mods)
csvout('interfejsy.csv', links)
csvout('odbior.csv', [stages[0]+['Wynik pomiaru','Status','Data / egzemplarz'], *[r+['','NIE ZBADANO',''] for r in stages[1:]]])

owners = {
 'U1':'P05','U2':'P07','U3':'P06','U4':'P07','U5':'P04','U6':'P05',
 'U7':'P04','U8':'P04','U9':'P04','U10':'P04','U11':'P08','U12':'P04',
 'U13':'P05','U16':'P10','U17':'P03','U18':'P05 + P07 + P08',
 'M1':'P03','M2':'P07','M3':'P02','M4':'P02',
 'RSH_T':'P07','RSH_L':'P06','KCUR':'P05','KSENSOR':'P08','KPWR':'P07',
 'SD1':'P03','TC1':'P09','TC2':'P09','J_BYPASS':'P06',
 'J_TEST':'PANEL','J_L1':'PANEL','J_L2':'PANEL','J_SCOPE':'PANEL',
 'J_AUX':'P05 / PANEL','JP_AUX':'P05','J_OBD':'P10 / PANEL',
 'J_PWR':'WIAZKA ZASILANIA','F1':'WIAZKA ZASILANIA',
 'JP4':'AT','JP5':'AT','JP6':'AT','JT_LOOP':'AT','OEM_T':'AT',
 'OEM_L1':'AL1','OEM_ECU':'AL1','OEM_L2':'AL2',
 'R_FILT':'P05','C_A':'P05',
 'RC1':'P07','RC2':'P07','RC3':'P06','RC4':'P06','RO1':'P07','RO2':'P06',
 'CI_ADC':'P05','R_IFILT':'P07','C_IFILT':'P07',
 'C_CAN_VIO':'P10','R_SCOPE':'P03','R_MARK':'P03','C_MARK':'P03',
 'D2':'P07','D3':'P10','D4':'P05','D5':'P05','D6':'P05','D7':'P05',
 'D8':'P08','D11':'P07','D12':'P07',
 'R_PD_TEST_KEY':'P04','R_PD_INTERLOCK':'P04','R_PD_LOGGER_CLEAR':'P03',
 'R_PD_TEST_PRESENT':'P03','R_PD_STOP_PRESSED':'P03','R_MCU_PD':'P04',
 'R_HW_PD':'P03','R_HEART_PD':'P04',
 'R_DEFAULT_MEAS_EN':'P05','R_DEFAULT_MEAS_BANK':'P05',
 'R_DEFAULT_SENSOR_PERMIT':'P08','R_DEFAULT_MOTOR_PERMIT':'P07',
 'R_DEFAULT_SENSOR_ENABLE':'P04','R_DEFAULT_MOTOR_INA':'P07','R_DEFAULT_MOTOR_INB':'P07',
 'R_PU_ADC_CS':'P05','R_PU_SD_CS':'P03','R_PU_TC1_CS':'P09','R_PU_TC2_CS':'P09',
 'R_PU_SENSOR_FAULT_N':'P03','R_PU_I2C_SDA':'P03','R_PU_I2C_SCL':'P03',
}
replaced = {'M5','M5_R8','M5_R3','M5_R4','D1'}

def assign(ref, sheet):
    if ref in replaced: return 'ZASTAPIONE P01', 'Nie przenosic; zastapione przez PWR-THT'
    if ref in owners:
        note = 'Przeniesienie funkcji; patrz zmiany MOD'
        if ref == 'U18': note = 'Rozdzielic na trzy lokalne drivery; nie zachowywac jednej wspolnej kostki'
        if ref in {'J_TEST','J_L1','J_L2'}: note = 'Gniazdo panelowe; moc, odczepy i interlock osobnymi wiazkami, nie przez PCB P11'
        if ref == 'R_PU_SENSOR_FAULT_N': note = 'Pull-up diagnostyczny przy MCP; buforowanie granicy zasilan zgodnie z projektem P03'
        return owners[ref], note
    if ref.startswith('C_DEC_'):
        ic = re.match(r'C_DEC_(U\d+)_', ref).group(1)
        return owners[ic], 'Odsprzeganie pozostaje bezposrednio przy swoim ukladzie'
    if ref.startswith('C_DCDC_'): return 'P02', 'Przy odpowiedniej przetwornicy'
    if ref.startswith('SW_'): return 'PANEL / P11', 'Element mechaniczny panelu; P11 tylko opcjonalne rozprowadzenie stykow'
    if ref.startswith('KMEAS'): return 'P05', 'Przekaznik i lokalny driver na DAQ'
    if ref.startswith(('R_OC_', 'C_OC_')): return 'P07', 'Okno nadpradowe lokalnie przy INA TEST'
    if ref.startswith(('R_RAIL_', 'C_RAIL_', 'C_REF_')): return 'P05', 'Nadzor 5V_A przy DAQ; dodatkowy lokalny nadzor na P07 jest nowym obwodem'
    if sheet in {17,18,19}: return {17:'AT',18:'AL1',19:'AL2'}[sheet], 'Rezystory blisko EGR, przed dlugim przewodem'
    if sheet in {4,5}: return 'P04', 'Logika bezpieczenstwa'
    if sheet == 8: return 'P07', 'Tor napedu'
    if sheet == 10: return 'P08', 'Odlaczane zasilanie sensora'
    if sheet in {11,12,13}: return 'P05', 'Tor analogowy lokalnie na DAQ'
    if sheet == 14: return 'P03', 'CORE'
    if sheet == 2 and ref in {'F2','F3'}: return 'P02', 'Bezpieczniki galezi przetwornic'
    raise ValueError(f'Unassigned: {ref} sheet {sheet}')

index = SOURCE/'schemat-S1/dane/indeks-elementow.csv'
with index.open(encoding='utf-8-sig', newline='') as f:
    src = list(csv.DictReader(f, delimiter=';'))
mapped=[]
for c in src:
    target, note=assign(c['ref'],int(c['sheet']))
    mapped.append(['v4.1/S1',c['ref'],c['value'],target,note])
pg=json.loads((PG/'hardware/components.json').read_text(encoding='utf-8'))
for ref,c in pg.items(): mapped.append(['PWR-THT-v1','PG.'+ref,c['value'],'P01','Oznaczenia lokalne PWR-THT; PG.J4 otrzyma dodatkowa petle obecnosci w modularnym zlaczu'])
csvout('mapa-elementow.csv',[['Zrodlo','Oznaczenie','Wartosc','Zespol docelowy','Uwagi'],*mapped])

gpio={}
with (SOURCE/'hardware/pinout.csv').open(encoding='utf-8-sig') as f:
    for row in csv.DictReader(f,delimiter=';'):gpio[row['signal']]=int(row['GPIO'])
adc_expected={'ADC_SCLK':9,'ADC_SDI':2,'ADC_DOUTA':11,'ADC_CS':12,'ADC_CONVST':13,'ADC_BUSY':14}
assert all(gpio[k]==v for k,v in adc_expected.items())
assert len(src)==len({c['ref'] for c in src})
assert len(pg)==72
assert len(mods)-1==11
with (ROOT/'odbior.csv').open(encoding='utf-8-sig',newline='') as f:
    acceptance = list(csv.DictReader(f,delimiter=';'))
assert len(acceptance)==len(stages)-1
assert all(r['Status']=='NIE ZBADANO' and not r['Wynik pomiaru'] for r in acceptance)
source_paths=[index,SOURCE/'hardware/pinout.csv',SOURCE/'hardware/ic-pins.csv',SOURCE/'firmware/main/board.c',SOURCE/'docs/01-projekt.md',SOURCE/'docs/03-uruchomienie.md',SOURCE/'docs/07-polaczenia.md',PG/'hardware/components.json',PG/'README.md']
source_hashes={p.relative_to(BASE).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths}
(ROOT/'verification/zrodla-sha256.json').write_text(json.dumps(source_hashes,ensure_ascii=False,indent=2),encoding='utf-8')
report={'status':'ARCHITECTURE_AND_MAPPING_ONLY','source_S1_positions':len(src),'PWR_THT_positions':len(pg),'mapped_rows':len(mapped),'unassigned_positions':0,'module_rows':len(mods)-1,'interface_groups':len(links)-1,'commissioning_stages':len(stages)-1,'adc_GPIO_crosschecked':adc_expected,'firmware_changes_implemented':False,'PCB_layout_done':False,'ERC_DRC_done':False,'hardware_tested':False}
(ROOT/'verification/podzial.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))

manifest=ROOT/'verification/SHA256SUMS.txt'
files=sorted(p for p in ROOT.rglob('*') if p.is_file() and p!=manifest and '__pycache__' not in p.parts)
manifest.write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(ROOT).as_posix()+'\n' for p in files),encoding='utf-8')
with zipfile.ZipFile(ROOT.parent/(ROOT.name+'.zip'),'w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(ROOT.rglob('*')):
        if p.is_file() and '__pycache__' not in p.parts:z.write(p,ROOT.name+'/'+p.relative_to(ROOT).as_posix())
