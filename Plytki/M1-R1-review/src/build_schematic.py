"""M1-R1 schematic generator: seven A3 sheets (root M1 = supply). Parts come from parts.py (single source); every pin gets a short wire
stub with a net label (cadlib.Sheet.finish), names shared by sheets become global labels. Deterministic row packing (as P07 S1);
verify_schematic.py checks the exported netlist pin by pin."""
from parts import *
import cadlib, collections, copy, math
names = [('M1', 'Zasilanie: pakiet, F1, TSR 5 V / 3,3 V, VMOTOR; arkusze'), ('MCU', 'ESP32-S3 DEV-KIT, karta SD, przycisk, podciagania'),
         ('ADC', 'AD7606B, osiem kanalow'), ('PRAD', 'Bocznik 5 mOhm, Kelvin, INA240A2'), ('TEMP_CAN', '2 x MAX31856, bufor MISO, CAN pasywny'),
         ('NAPED', 'IBT-2 (74AHCT125), zasilanie czujnika TPS2553'), ('LISTWA', 'Pola przewodow do X1, pola testowe')]
S = {n: Sheet(n, t, i, None if i == 1 else uid('M1')) for i, (n, t) in enumerate(names, 1)}
CH = 1.0; STUB = 5.08; W = 405.0; Y0 = 40.0; YMAX = 268.0


def natural(r): return (re.sub(r'\d', '', r), int(re.sub(r'\D', '', r) or 0))


def geometry(part, unit, a):
    pts = []
    for n, p in pin_defs(part['symbol'], unit).items():
        px, py, pa = map(float, one(p, 'at')[1:]); t = math.radians(a)
        dx = px * math.cos(t) - py * math.sin(t); dy = px * math.sin(t) + py * math.cos(t); ang = (pa + a) % 360; rad = math.radians(ang)
        x, y = dx, -dy; ex, ey = x - STUB * math.cos(rad), y + STUB * math.sin(rad); net = part['pins'][n]
        L = 0 if net == 'NC' else len(net) * CH + 4
        pts += [(x, y), (ex, ey - 1.5), (ex, ey + 1.5), ((ex - L) if ang == 0 else (ex + L), ey)]
    pts += [(-6, -6), (6, 6)]
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    return min(xs) - 2, max(xs) + 2, min(ys) - 4, max(ys) + 3


def text_at(part, unit):
    if part['ref'].startswith(('U', 'M', 'SD', 'TC')):
        ys = [float(one(p, 'at')[2]) for p in pin_defs(part['symbol'], unit).values()]; return (-5, -(max(ys) / 2.54 + 3))
    if part['ref'].startswith('J'): return (2, -(len(part['pins']) // 2) - 3)
    return None


def layout(sh, items, width=W, y0=Y0):
    x = 8.0; y = y0; rowh = 0
    for ref, unit in items:
        a = 0; p = copy.copy(PARTS[ref]); p['display'] = p['display'].split(' / ')[0]
        if ref.startswith(('R', 'C', 'F')) and len(p['pins']) == 2: a = 90
        ta = text_at(p, unit)
        if ta: p['text_at'] = ta
        x0, x1, y0_, y1 = geometry(p, unit, a)
        if x + (x1 - x0) > width: x = 8.0; y += rowh + 3; rowh = 0
        if y + (y1 - y0_) > YMAX: raise SystemExit(f'sheet {sh} overflows at {ref}')
        gx = round((x - x0) / 1.27) * 1.27; gy = round((y - y0_) / 1.27) * 1.27
        S[sh].place(p, gx / 2.54, gy / 2.54, a, unit)
        x += x1 - x0 + 4; rowh = max(rowh, y1 - y0_)


SHEETS = collections.defaultdict(list)
for r in sorted(PARTS, key=lambda r: (not r.startswith(('U', 'M', 'SD', 'TC', 'J', 'RSH')), natural(r))):
    units = sorted({int(s[1].split('_')[-2]) for s in subs(PARTS[r]['symbol'], 'symbol')} - {0})
    SHEETS[PARTS[r]['sheet']] += [(r, u) for u in units]
NOTES = {
    'M1': ['Pakiet 4S (za BMS 40 A, przez wylacznik na obudowie) -> X1.1 / X1.2 -> J1 -> F1 MINI 7,5 A -> VBUS: TSR 2-2450 (5V), TSR 2-2433 (3V3), J2 -> X1.3 -> IBT-2 B+.',
           'IBT-2 B- -> X1.4 (mostek do X1.2 na listwie): prad silnika nie przechodzi przez PCB. Jedna masa GND na plytce (minus pakietu).'],
    'MCU': ['ESP32-S3 DEV-KIT z 5V (J1-21); 3V3 modulu niepodlaczone (peryferia z TSR 2-2433). LED stanu = RGB modulu (GPIO38). Zakazane: GPIO0/45/46, 19/20, 33-37, 43/44, 47/48.',
            'Podciagania do GND (R2-R5): mostek i zasilanie czujnika wylaczone w resecie ESP32. SPI2 = AD7606B, SPI3 = SD + 2 x MAX31856.'],
    'ADC': ['AD7606B: OS = 111, tryb szeregowy programowy, zakres +-10 V, wewnetrzne odniesienie (jak P05 R3). AVCC = 5VA przez R7 1R.',
            'CH1 P1_EGR i CH2 P3: 300k / 100k (MOTOR); CH3-5 P4-P6 i CH8 SENS_5V: 100k szeregowo (SENSOR); CH7 VBAT_CAR: 499k / 100k; 220p przy pinie. CH6: INA240 przez 1k / 1n.'],
    'PRAD': ['P1_ECU -> RSH1 5 mOhm (Kelvin) -> P1_EGR. INA240A2 x50, REF1 = 5V, REF2 = GND: OUT = 2,5 V + 0,25 V/A (liniowo ok. +-9 A, powyzej F1 7,5 A). Zero rejestrowane przy wylaczonym silniku.'],
    'TEMP_CAN': ['MAX31856 x 2 (moduly XU wlutowane): VIN = 3V3 przez 0R (opcja 5 V DNP). SDO przez 74LVC125 z OE = CS na wspolne SPI3_MISO (karta SD).',
                 'TCAN1051V tylko odbior: TXD i S na 3V3 (cichy). PESD2CAN na wejsciu magistrali.'],
    'NAPED': ['74AHCT125 (5V): RPWM, LPWM, DRIVE_EN -> R_EN + L_EN modulu IBT-2 (pola J4, przewody lutowane do listwy modulu). Zawsze aktywny; wejscia sciagniete do GND.',
              'TPS2553: SENS_5V dla czujnika w TESTER, EN = GPIO40, FAULT_N -> GPIO42.'],
    'LISTWA': ['Pola przewodow w kolejnosci X1 (docs/X1.csv): J1 X1.1-2, J2 X1.3, J5 X1.5-6, J6 X1.7-16. Termopary osobna mufa wprost do modulow.',
               'Pola testowe TP1-TP10 zamiast listew serwisowych S1.']}
for sh, items in SHEETS.items():
    for k, t in enumerate(NOTES[sh]): S[sh].text(t, 8, 7.6 + k * 2.2, 1.25)
    layout(sh, items, W if sh != 'M1' else 300.0)
for i, n in enumerate([G, VB, A5, 'BAT_P', 'TC1_VIN', 'TC2_VIN'], 1):
    S['M1'].place({'ref': f'#FLG{i}', 'display': 'PWR_FLAG', 'symbol': symbol('power', 'PWR_FLAG'), 'source_ref': 'ERC_SOURCE', 'mpn': '', 'footprint': '', 'pins': {'1': n}}, 4 + i * 7, 92)
ns = collections.defaultdict(set)
for name, sh in S.items():
    for part, pins in sh.parts.values():
        for n in pins: ns[part['pins'][n]].add(name)
cadlib.CROSS = {n for n, v in ns.items() if len(v) > 1 and n != 'NC'}
for sh in S.values(): sh.text(f'{cadlib.REV} / {sh.num:02d}   {sh.title.upper()}', 8, 5, 2)
for i, (name, title) in enumerate(names[1:], 2):
    sh = S[name]; x, y = mm(124), mm(20 + (i - 2) * 9); sid = uid('sheet/' + name)
    S['M1'].items.append(f'(sheet (at {x} {y}) (size 55.88 10.16) (stroke (width .15) (type default)) (fill (color 0 0 0 0)) (uuid {sid}) (property "Sheetname" {q(name)} (at {x} {y - 1.27} 0) (effects (font (size 1 1)) (justify left bottom))) (property "Sheetfile" {q(name + ".kicad_sch")} (at {x} {y + 10.16} 0) (effects (font (size 1 1)) (justify left top))) (instances (project "M1" (path {q("/" + uid("M1"))} (page "{i}")))))')
    old = sh.path; sh.path = '/' + uid('M1') + '/' + sid; sh.items = [t.replace(q(old), q(sh.path)) for t in sh.items]
for sh in S.values(): sh.finish(); sh.save()
write_tables()
# 8.10 (recenzja M1-05): istniejacy projekt tylko uzupelniany - generator ustawia wylacznie swoje pola (meta, sheets); reguly plytki
# (board), klasy sieci (net_settings) i inne sekcje zostaja. Nowy plik powstaje tylko, gdy go nie ma.
pro_path = P / 'eda/M1.kicad_pro'
pro = json.loads(pro_path.read_text()) if pro_path.exists() else {'boards': [], 'libraries': {'pinned_footprint_libs': [], 'pinned_symbol_libs': []},
                                                                  'schematic': {'legacy_lib_dir': '', 'legacy_lib_list': []}, 'text_variables': {}}
pro['meta'] = {**pro.get('meta', {}), 'filename': 'M1.kicad_pro', 'version': pro.get('meta', {}).get('version', 3)}
pro['sheets'] = [[uid(n) if n == 'M1' else uid('sheet/' + n), n] for n, _ in names]
pro_path.write_text(json.dumps(pro, indent=2) + '\n')
(P / 'verification').mkdir(exist_ok=True)
(P / 'verification/sheet-parts.json').write_text(json.dumps({n: list(s.parts) for n, s in S.items()}, indent=2))
print(len(PARTS), 'parts;', len(S), 'sheets')
