"""P12 R1: netlista schematu (kicad-cli, verification/P12.xml) wobec kontraktów krawędzi A — każdy pin każdego złącza.

Wzorce (dwa, niezależne od schematu):
- docs/kontrakt-P12.json (src/kontrakt.py: pinouty płytek pin po pinie, GND jawnie, położenia, typy IDC);
- Plytki/P12-przygotowanie/wyniki/kontrakty.json (raport kontraktów: końce każdej sieci poza GND, typy złączy) — kontrola krzyżowa.
Kontrole K1..K10 (niżej) i próby ujemne: kopie modelu netlisty z jedną wadą każda (zamieniony pin, brak sieci, zwarcie 5V_SYS-GND,
pin w pin P03 J_BP2 / P05 J_BP2, zły typ złącza, ...) plus próba zerowa (bez zmiany). Każda wada musi oblać wskazaną kontrolę,
próba zerowa nie może oblać żadnej. Wynik: verification/electrical-checks.json; kod 1 przy FAIL.
"""
from pathlib import Path
import json, sys, copy, csv, xml.etree.ElementTree as ET
P = Path(__file__).resolve().parents[1]
K12 = json.loads((P / 'docs/kontrakt-P12.json').read_text(encoding='utf-8'))
KON = json.loads((P.parents[0] / 'P12-przygotowanie/wyniki/kontrakty.json').read_text(encoding='utf-8'))
ZL = {z['ref']: z for z in K12['zlacza']}
TPW = {'TP1': 'GND', 'TP2': '5V_SYS', 'TP3': '3V3_IO', 'TP4': 'GND'}
with open(P / 'docs/NIEPODLACZONE.csv', encoding='utf-8-sig') as fh:
    NIEP = {r['pin_P12']: r['siec'] for r in csv.DictReader(fh, delimiter=';')}


def model(xml):
    root = ET.parse(xml).getroot()
    comps = {c.get('ref'): c.findtext('footprint') for c in root.findall('./components/comp')}
    nets = {}
    for n in root.findall('./nets/net'):
        nets[n.get('name').split('/')[-1]] = {f"{q.get('ref')}.{q.get('pin')}" for q in n.findall('node')}
    return {'comps': comps, 'nets': nets}


def sprawdz(m):
    comps, nets = m['comps'], m['nets']; wyn = []
    of = {node: name for name, ns in nets.items() for node in ns}

    def k(i, opis, ok, det=None):
        wyn.append({'id': i, 'opis': opis, 'pass': bool(ok), 'detail': det})
    # K1 typy złączy
    bad = {}
    for r, z in ZL.items():
        n = z['n'] // 2; want = f'Connector_IDC:IDC-Header_2x{n:02d}_P2.54mm_Vertical'
        pins = sorted(int(x.split('.')[1]) for x in of if x.split('.')[0] == r)
        kon = next((q for q in KON['zlacza'] if q['plytka'] == z['plytka'] and q['zlacze'] == z['zlacze']), None)
        if comps.get(r) != want or pins != list(range(1, z['n'] + 1)) or kon is None or kon['typ'] != f'IDC 2×{n}':
            bad[r] = {'footprint': comps.get(r), 'want': want, 'pins': len(pins), 'kontrakty_json': kon and kon['typ']}
    k('K1', 'Złącza J1..J10: footprint prostego IDC o typie z kontraktu (2x5 / 2x8 / 2x10, kontrakty.json) i wszystkie piny w netliście', not bad, bad)
    # K2 pin po pinie
    def zgodny(node, s):
        g = of.get(node)
        return (g or '').startswith('unconnected-') if node in NIEP else g == s
    bad = [f'{r}.{n}: {of.get(f"{r}.{n}")} (kontrakt {s})' for r, z in ZL.items() for n, s in z['piny'].items() if not zgodny(f'{r}.{n}', s)]
    k('K2', 'Każdy pin każdego złącza: sieć = kontrakt-P12.json (pinout płytki, GND jawnie; piny z docs/NIEPODLACZONE.csv bez połączenia)', not bad, bad[:30])
    # K3 grupy połączeń
    want = {}
    for r, z in ZL.items():
        for n, s in z['piny'].items():
            if f'{r}.{n}' not in NIEP:
                want.setdefault(s, set()).add(f'{r}.{n}')
    for t, s in TPW.items():
        want.setdefault(s, set()).add(f'{t}.1')
    bad = {s: {'netlista': sorted(nets.get(s, set())), 'kontrakt': sorted(v)} for s, v in want.items() if nets.get(s) != v}
    bad.update({s: {'netlista': sorted(v), 'kontrakt': None} for s, v in nets.items() if s not in want and not (s.startswith('unconnected-') and len(v) == 1)})
    k('K3', 'Grupy połączeń P12 = grupy z kontraktu (każda sieć dokładnie z pinami tej nazwy, bez sieci dodatkowych)', not bad, bad)
    # K4 kontrola krzyżowa z raportem kontraktów (końce sieci poza GND)
    rmap = {(z['plytka'], z['zlacze']): r for r, z in ZL.items()}; bad = {}
    for s, v in KON['sieci'].items():
        w = set()
        for e in v['konce']:
            pl = ' '.join(e.split()[:2]); zl, pin = e.split()[2].split('.'); w.add(f'{rmap[(pl, zl)]}.{pin}')
        g = {x for x in nets.get(s, set()) if not x.startswith('TP')}
        if len(w) == 1:   # jeden koniec na płytkach LOGGER: pin ma być bez połączenia
            x = next(iter(w)); g = {x} if (of.get(x) or '').startswith('unconnected-') and len(nets.get(of.get(x), ())) == 1 else g
        if g != w:
            bad[s] = {'netlista': sorted(g), 'kontrakty_json': sorted(w)}
    k('K4', 'Kontrola krzyżowa: końce każdej sieci poza GND = P12-przygotowanie/wyniki/kontrakty.json (23 OK + 27 czeka)', not bad, bad)
    # K5 GND / zasilania rozdzielone, P03 J_BP2 / P05 J_BP2 piny 16/17/19/20
    gnd = nets.get('GND', set()); v5 = nets.get('5V_SYS', set()); v3 = nets.get('3V3_IO', set())
    pary = {f'J3.{n}/J6.{n}': (of.get(f'J3.{n}'), of.get(f'J6.{n}')) for n in ('16', '17', '19', '20')}
    ok = (gnd and v5 and v3 and not (gnd & v5) and not (gnd & v3) and not (v5 & v3) and all(a != b for a, b in pary.values())
          and pary['J3.17/J6.17'] == ('5V_SYS', 'GND') and pary['J3.16/J6.16'] == ('PFAIL_N', 'GND'))
    k('K5', 'GND, 5V_SYS i 3V3_IO to osobne sieci; P03 J_BP2 16/17/19/20 (PFAIL_N / 5V_SYS) nie łączą się z P05 J_BP2 16/17/19/20 (GND)', ok,
      {'pary': pary, 'GND': len(gnd), '5V_SYS': len(v5), '3V3_IO': len(v3)})
    # K6 żadna sieć nie łączy pinów o różnych nazwach w kontrakcie (pin w pin)
    exp = {f'{r}.{n}': s for r, z in ZL.items() for n, s in z['piny'].items()}; exp.update({f'{t}.1': s for t, s in TPW.items()})
    bad = {s: sorted({exp.get(x) for x in ns}, key=str) for s, ns in nets.items() if len({exp.get(x) for x in ns}) > 1}
    k('K6', 'Żadna sieć nie łączy pinów, którym kontrakt daje różne sieci (brak połączeń pin w pin)', not bad, bad)
    # K7 zasilanie: źródła P02 i odbiorniki
    w5 = {x for x, s in exp.items() if s == '5V_SYS'}; w3 = {x for x, s in exp.items() if s == '3V3_IO'}
    ok = v5 == w5 and v3 == w3 and {'J1.2', 'J1.4', 'J1.6'} <= v5 and {'J1.8', 'J1.10'} <= v3 and len(v5) == 15 and len(v3) == 8
    k('K7', '5V_SYS: 3 piny źródła P02 + 11 pinów odbiorników + TP2; 3V3_IO: 2 piny źródła + 5 odbiorników + TP3', ok, {'5V_SYS': sorted(v5), '3V3_IO': sorted(v3)})
    # K8 niepodłączone
    single = {next(iter(ns)): exp.get(next(iter(ns))) for s, ns in nets.items() if len(ns) == 1}
    ok = (single == NIEP and all(s.startswith('unconnected-') for s, ns in nets.items() if len(ns) == 1)
          and all(len(KON['sieci'][s]['czeka_na']) and set(KON['sieci'][s]['czeka_na']) <= {'P04', 'P07', 'P08'} for s in NIEP.values()))
    k('K8', 'Piny bez połączenia = docs/NIEPODLACZONE.csv (24 sieci z drugim końcem na P04 / P07 / P08); każda sieć z ≥ 2 końcami LOGGER połączona', ok,
      {'jednopinowe': single, 'oczekiwane': NIEP})
    # K9 pola pomiarowe
    ok = all(of.get(f'{t}.1') == s for t, s in TPW.items()) and all(comps.get(t, '').startswith('TestPoint:') for t in TPW)
    k('K9', 'Pola pomiarowe: TP1 / TP4 GND, TP2 5V_SYS, TP3 3V3_IO', ok, {t: of.get(f'{t}.1') for t in TPW})
    # K10 brak innych części
    ok = set(comps) == set(ZL) | set(TPW)
    k('K10', 'Na schemacie tylko J1..J10 i TP1..TP4 (bez elementów aktywnych i biernych)', ok, sorted(set(comps) ^ (set(ZL) | set(TPW))))
    return wyn


def mut(m, f):
    m = copy.deepcopy(m); f(m); return m


def move(m, node, to):
    for ns in m['nets'].values():
        ns.discard(node)
    m['nets'].setdefault(to, set()).add(node)
    m['nets'] = {s: ns for s, ns in m['nets'].items() if ns}


def swap(m, a, b):
    na = next(s for s, ns in m['nets'].items() if a in ns); nb = next(s for s, ns in m['nets'].items() if b in ns); move(m, a, nb); move(m, b, na)


def merge(m, a, b):
    m['nets'][b] |= m['nets'].pop(a)


PROBY = [('proba_zerowa', lambda m: None, None),
         ('zamieniony_pin_ADC_SCLK_DOUTA', lambda m: swap(m, 'J3.2', 'J3.4'), 'K2'),
         ('zamieniony_pin_P09_MISO_MOSI', lambda m: swap(m, 'J7.8', 'J7.10'), 'K2'),
         ('brak_sieci_ADC_BUSY', lambda m: (move(m, 'J3.12', 'unconnected-(J3-Pin_12-Pad12)'), move(m, 'J6.12', 'unconnected-(J6-Pin_12-Pad12)')), 'K2'),
         ('brak_konca_CAN_RX_P10', lambda m: move(m, 'J9.8', 'unconnected-(J9-Pin_8-Pad8)'), 'K2'),
         ('zwarcie_5V_SYS_GND', lambda m: merge(m, '5V_SYS', 'GND'), 'K5'),
         ('pin_w_pin_J3_17_J6_17', lambda m: move(m, 'J6.17', '5V_SYS'), 'K5'),
         ('pin_w_pin_J3_16_J6_16', lambda m: move(m, 'J6.16', 'PFAIL_N'), 'K6'),
         ('zly_typ_P05_J_BP1_2x8', lambda m: m['comps'].__setitem__('J5', 'Connector_IDC:IDC-Header_2x08_P2.54mm_Vertical'), 'K1'),
         ('zly_typ_katowy_P10', lambda m: m['comps'].__setitem__('J9', 'Connector_IDC:IDC-Header_2x05_P2.54mm_Horizontal'), 'K1'),
         ('P04_3V3_do_3V3_IO', lambda m: move(m, 'J1.15', '3V3_IO'), 'K7'),
         ('PG_SEND_PG_LINK_zmostkowane', lambda m: (move(m, 'J1.17', 'PG_SEND'), move(m, 'J1.18', 'PG_SEND')), 'K8'),
         ('TP2_na_GND', lambda m: move(m, 'TP2.1', 'GND'), 'K9'),
         ('dodatkowa_czesc_R1', lambda m: (m['comps'].__setitem__('R1', 'Resistor_SMD:R_1206'), m['nets'].setdefault('X', set()).add('R1.1')), 'K10')]

if __name__ == '__main__':
    base = model(P / 'verification/P12.xml'); checks = sprawdz(base); neg = []
    for name, f, want in PROBY:
        failed = [c['id'] for c in sprawdz(mut(base, f)) if not c['pass']]
        det = (not failed) if want is None else want in failed
        neg.append({'mutation': name, 'expected': 'clean' if want is None else 'detected', 'expected_check': want, 'failed_checks': failed, 'detected': bool(failed), 'ok': det})
    res = {'checks': checks, 'negative_controls': neg}
    (P / 'verification/electrical-checks.json').write_text(json.dumps(res, indent=1, ensure_ascii=False, default=sorted) + '\n', encoding='utf-8')
    for c in checks:
        print('PASS' if c['pass'] else 'FAIL', c['id'], c['opis'])
    for t in neg:
        print('OK ' if t['ok'] else 'BAD', t['mutation'], '->', t['failed_checks'])
    ok = all(c['pass'] for c in checks) and all(t['ok'] for t in neg)
    print(f"{sum(c['pass'] for c in checks)}/{len(checks)} kontroli, próby ujemne {sum(t['ok'] for t in neg)}/{len(neg)} (z zerową)")
    sys.exit(0 if ok else 1)
