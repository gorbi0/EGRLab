"""P11-R2 contract with P12 (S1 8), independent of the generator: the exported netlist and docs/J_P12.csv against
reference/P03-R6-J_BP.csv (P03 R6 J_BP1), reference/P04-R2.1-parts.json (PANELSAFE J8), reference/P06-R2-J_BP.csv (3V3_IO) and
reference/P12-kontrakty.json (nets waiting for P11). Each mutation names its target check; the last trial is a null control."""
from pathlib import Path
import csv, json, copy
import xml.etree.ElementTree as ET
P = Path(__file__).resolve().parents[1]
def read_net(path):
    root = ET.parse(path).getroot(); c = {x.get('ref'): {} for x in root.findall('./components/comp')}
    for n in root.findall('./nets/net'):
        name = n.get('name').split('/')[-1]
        for x in n.findall('node'): c[x.get('ref')][x.get('pin')] = 'NC' if name.startswith('unconnected-') else name
    return c
def read_csv(path): return list(csv.DictReader(path.open(encoding='utf-8-sig'), delimiter=';'))
P03 = {(r['zlacze'], int(r['pin'])): r for r in read_csv(P / 'reference/P03-R6-J_BP.csv')}
P06 = {int(r['pin']): r['siec'] for r in read_csv(P / 'reference/P06-R2-J_BP.csv')}
J8 = json.loads((P / 'reference/P04-R2.1-parts.json').read_text())['J8']['pins']
KON = json.loads((P / 'reference/P12-kontrakty.json').read_text(encoding='utf-8'))['sieci']
CORE5 = ['N_J_SCOPE_HOT', 'MARK', 'TEST_KEY', 'LOGGER_CLEAR', 'TEST_PRESENT']
ODD_EXC = {13, 15}                                  # MARK, LOGGER_CLEAR: same positions and exception as P03 R6 J_BP1
def neighbours(k): return {x for x in (k - 2, k - 1, k + 1, k + 2) if 1 <= x <= 20}   # ribbon order +-1, same header row +-2
def check(net, rows):
    out = []
    def ok(k, v, note=''): out.append({'id': k, 'pass': bool(v), 'note': note})
    j = {int(p): n for p, n in net.get('J_P12', {}).items()}
    ok('J_P12-20-PINS', sorted(j) == list(range(1, 21)))
    pos = {n: [p for p, m in j.items() if m == n] for n in set(j.values())}
    for n in CORE5:
        src = [k for k, r in P03.items() if r['siec'] == n]
        ok('P03-POS-' + n, len(src) == 1 and src[0][0] == 'J_BP1' and pos.get(n) == [src[0][1]], f'P03 R6 {src} / P11 {pos.get(n)}')
        if src:
            d = P03[src[0]]['kierunek']
            mine = next((r['kierunek'] for r in rows if r['siec'] == n), None)
            ok('DIR-' + n, {'in': 'out', 'out': 'in'}[d] == mine, f'P03 {d}, P11 {mine}')
    waiting = sorted(n for n, v in KON.items() if 'P11' in v.get('czeka_na', []))
    ok('P12-WAITING-COVERED', waiting and all(len(pos.get(n, [])) == 1 for n in waiting), f'{waiting}')
    safe = sorted({n for n in J8.values() if n not in ('GND', 'NC')})
    ok('PANELSAFE-NETS', all(len(pos.get(n, [])) == 1 for n in safe), f'P04-R2.1 J8: {safe}')
    ok('3V3_IO-ONE-PIN', len(pos.get('3V3_IO', [])) == 1 and '3V3_IO' in P06.values() and any('ZRODLO' in e for e in KON['3V3_IO']['konce']),
       '3V3_IO exists on P12 (P02 R4 source, P06 R2 J_BP.14)')
    allowed = set(CORE5) | set(safe) | {'3V3_IO', 'GND'}
    ok('NO-FOREIGN-NETS', set(j.values()) <= allowed, f'{sorted(set(j.values()) - allowed)}')
    ok('ODD-GND', all(j.get(p) == 'GND' for p in range(1, 20, 2) if p not in ODD_EXC), 'odd pins GND except 13 / 15')
    ok('GND-COUNT', sum(1 for n in j.values() if n == 'GND') >= 9)
    v3, pv = pos.get('3V3_IO', [0])[0], pos.get('PANEL_3V3', [0])[0]
    ok('3V3_IO-NOT-NEXT-TO-PANEL_3V3', v3 and pv and pv not in neighbours(v3), f'3V3_IO {v3}, PANEL_3V3 {pv}')
    sc = pos.get('N_J_SCOPE_HOT', [0])[0]
    ok('SCOPE-BETWEEN-GND', sc and j.get(sc - 1) == 'GND' and j.get(sc + 1) == 'GND', 'edge signal shielded in the ribbon')
    # every signal of J_P12 is used on P11 (no pin without a destination on the board), 3V3_IO only via R1
    used = {n for r, v in net.items() if r != 'J_P12' for n in v.values()}
    ok('ALL-USED-ON-P11', all(n in used for n in j.values()), f'{sorted(n for n in set(j.values()) if n not in used)}')
    ok('CSV-EQUALS-NETLIST', [(r['zlacze'], int(r['pin']), r['siec']) for r in rows] == [('J_P12', p, j.get(p)) for p in range(1, 21)])
    ok('CSV-KIND', all(r['kierunek'] == ('gnd' if r['siec'] == 'GND' else r['kierunek']) for r in rows) and
       all(r['kierunek'] in ('gnd', 'in', 'out', 'pwr') for r in rows))
    return out
if __name__ == '__main__':
    net = read_net(P / 'verification/P11.xml'); rows = read_csv(P / 'docs/J_P12.csv'); base = check(net, rows); neg = []
    def trial(name, target, fn=None, fr=None):
        nn, rr = copy.deepcopy(net), copy.deepcopy(rows)
        if fn: fn(nn)
        if fr: fr(rr)
        bad = [x['id'] for x in check(nn, rr) if not x['pass']]
        neg.append({'mutation': name, 'target': target, 'detected': (target in bad) if target else bool(bad), 'by': bad})
    def swap(a, b):
        def f(n): n['J_P12'][a], n['J_P12'][b] = n['J_P12'][b], n['J_P12'][a]
        return f
    def setp(p, v): return lambda n: n['J_P12'].__setitem__(p, v)
    trial('MARK <-> TEST_KEY (13/14)', 'P03-POS-MARK', swap('13', '14'))
    trial('N_J_SCOPE_HOT na 12', 'P03-POS-N_J_SCOPE_HOT', swap('10', '12'))
    trial('TEST_PRESENT <-> LOGGER_CLEAR (16/15)', 'P03-POS-TEST_PRESENT', swap('15', '16'))
    trial('3V3_IO na 4 (obok PANEL_3V3)', '3V3_IO-NOT-NEXT-TO-PANEL_3V3', swap('4', '20'))
    trial('pin 9 GND -> STOP_NC_OUT (dubel)', 'ODD-GND', setp('9', 'STOP_NC_OUT'))
    trial('brak PANEL_3V3 (pin 2 -> GND)', 'PANELSAFE-NETS', setp('2', 'GND'))
    trial('brak ARM_CONTACT (pin 8 -> GND)', 'PANELSAFE-NETS', setp('8', 'GND'))
    trial('brak 3V3_IO (pin 20 -> GND)', '3V3_IO-ONE-PIN', setp('20', 'GND'))
    trial('obca siec 5V_SYS na 18', 'NO-FOREIGN-NETS', setp('18', '5V_SYS'))
    trial('GND obok SCOPE zabrany (11 -> MECH_OK)', 'SCOPE-BETWEEN-GND', setp('11', 'MECH_OK'))
    trial('CSV: pin 14 opisany jako MARK', 'CSV-EQUALS-NETLIST', fr=lambda r: r[13].__setitem__('siec', 'MARK'))
    trial('CSV: kierunek TEST_KEY = in', 'DIR-TEST_KEY', fr=lambda r: r[13].__setitem__('kierunek', 'in'))
    trial('MARK nieuzywany na P11 (J11.16 i X14.2 -> NC)', 'ALL-USED-ON-P11', lambda n: (n['J11'].__setitem__('16', 'NC'), n['X14'].__setitem__('2', 'NC')))
    trial('proba zerowa (bez zmian)', None)
    rep = {'checks': base, 'negative_controls': neg}
    (P / 'verification/p12-checks.json').write_text(json.dumps(rep, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    npass = sum(x['pass'] for x in base); caught = sum(t['detected'] for t in neg[:-1])
    print('P12 contract', npass, '/', len(base), '; mutations', caught, '/', len(neg) - 1, '; null control', 'clean' if not neg[-1]['detected'] else 'DIRTY')
    for x in base:
        if not x['pass']: print('FAIL', x)
    for t in neg[:-1]:
        if not t['detected']: print('MISSED', t)
    raise SystemExit(0 if npass == len(base) and caught == len(neg) - 1 and not neg[-1]['detected'] else 1)
