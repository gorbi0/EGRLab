"""P07-S1 electrical checks on the EXPORTED netlist (verification/P07.xml), independent of parts.py.
Logic: a small netlist simulator (gate models by part value, resistor pulls resolved by the lowest resistance path, open-collector
comparator / supervisors / NPN, 74HC74 with asynchronous PRE/CLR and clock edges) compared with the blocking specification of the task
(ZADANIE-P07-S1, 1): without SAFE_N, without MOTOR_PERMIT, with OC or bad rails -> RPWM, LPWM, R_EN, L_EN all L. Exhaustive table over
inputs and flip-flop states, dead-domain cases, open tapes, latch sequences. Analog: OC window, ITEST scale, shunt / precharge power,
KPWR drive and clamp, TVS, IS diagnostics, ground separation. Every check has a netlist mutation that must make it fail, plus a null control.
Output: verification/electrical-checks.json."""
from pathlib import Path
import xml.etree.ElementTree as ET, json, copy, re, sys, itertools, heapq
P = Path(__file__).resolve().parents[1]
G, PG = 'GND', 'PGND'
RAILS = {'3V3_IO': 1, '3V3A_P07': 1, '5VA_P07': 1, '5V_MOD': 1, '5V_SYS': 1, 'VMOTOR': 1, 'REF25': 1, 'GND': 0, 'PGND': 0}
EXT_IN = ['MOTOR_PERMIT', 'PWM_OUT', 'ARM_CLK', 'MOTOR_INA', 'MOTOR_INB', 'CS_ITEST_N', 'ADC_SCLK']
MOD_IN = ['RPWM', 'LPWM', 'R_EN', 'L_EN']                  # module inputs at J5 (30k pull-downs on the module)
MODULE_PD = 30000; P04_SAFE_PU, P04_SAFE_PD = 10000, 100000
# --- declared assumptions (data sheets / task), used by the analog checks ---
VSYS = (4.90, 5.10)            # TSR 2-2450 output +-2 %
VREF = (2.475, 2.525)          # MCP1525 +-1 %
INA_GAIN_ERR = 0.002; INA_VOS = 25e-6; OPA_VOS = 4.5e-3; CMP_VOS = 2.5e-3   # INA240 0.2 % / 25 uV, MCP6022 +-4.5 mV?, TLV1702 +-2.5 mV (conservative)
INA_SWING = 0.1                # INA240 output within VS - 0.1 V (conservative)
I_RUN, I_OC_LIMIT_MIN = 6.0, 6.9  # task: 6 A work; trip >= 115 % of it
VM_MAX = 16.8; KILIS = (6000, 11000); VT_SCHMITT = (1.3, 2.0)   # BTS7960 kILIS spread (assumed +-30 %), 74LVC2G17 VT+ at 3.0-3.6 V
COIL_MAX_RATIO = 1.5           # G2RL-1-E: maximum coil voltage assumed >= 150 % (to confirm in the data sheet)


def read(path):
    root = ET.parse(path).getroot(); c = {}
    for x in root.findall('./components/comp'):
        f = {a.get('name'): a.text for a in x.findall('./fields/field')}
        c[x.get('ref')] = {'pins': {}, 'value': x.findtext('value') or '', 'mpn': f.get('MPN', '') or '', 'fp': x.findtext('footprint') or ''}
    for n in root.findall('./nets/net'):
        name = n.get('name').split('/')[-1]
        for x in n.findall('node'): c[x.get('ref')]['pins'][x.get('pin')] = 'NC' if name.startswith('unconnected-') else name
    return c


def ohms(v):
    v = v.split()[0].upper()
    m = re.fullmatch(r'(\d+)([RKM])(\d*)', v)
    if m: return float(m[1] + '.' + (m[3] or '0')) * {'R': 1, 'K': 1e3, 'M': 1e6}[m[2]]
    m = re.fullmatch(r'(\d+(?:\.\d+)?)([RKM]?)', v)
    return float(m[1]) * {'': 1, 'R': 1, 'K': 1e3, 'M': 1e6}[m[2]] if m else None


AND4 = [((1, 2), 3), ((4, 5), 6), ((9, 10), 8), ((12, 13), 11)]
INV6 = [(1, 2), (3, 4), (5, 6), (9, 8), (11, 10), (13, 12)]
BUF4 = [(2, 1, 3), (5, 4, 6), (9, 10, 8), (12, 13, 11)]
MODELS = {'SN74HC08D': ('and', AND4, 14, 'HC'), '74LVC14AD': ('not', INV6, 14, 'LVC'), '74LVC125AD': ('oe', BUF4, 14, 'LVC'),
          '74AHCT125D': ('oe', BUF4, 14, 'HC'), '74LVC2G17': ('buf', [(1, 6), (3, 4)], 5, 'LVC'), 'SN74HC74D': ('ff', None, 14, 'HC')}


class Sim:
    def __init__(self, c):
        self.c = c; self.res = []
        for r, x in c.items():
            if re.fullmatch(r'R\d+', r) and len(x['pins']) == 2:
                a, b = x['pins'].get('1'), x['pins'].get('2'); v = ohms(x['value'])
                if a and b and v is not None: self.res.append((a, b, v))
        for n in MOD_IN: self.res.append((n, G, MODULE_PD))
        def mk(rr):
            adj = {}
            for a, b, rv in rr: adj.setdefault(a, []).append((b, rv)); adj.setdefault(b, []).append((a, rv))
            return adj
        self.adj = mk(self.res); self.adj_safe = mk(self.res + [('SAFE_N', '__P04_STOP', P04_SAFE_PU), ('SAFE_N', G, P04_SAFE_PD)])
        self.an = self.analog()

    def pin(self, r, p): return self.c[r]['pins'].get(str(p))

    def run(self, ext, powered, sup_ok, current, ff, safe_ext, force=None, force_check=True):
        """ext: J_BP input net -> 0/1/None (None = open tape); powered: set of rails present; sup_ok: {'3V3A','5VA'} levels OK;
        current: motor current [A]; ff: [q1, q2] (mutated on clock edge); safe_ext: P04 side of SAFE_N (None = tape open)."""
        c = self.c; val = {}
        rails = {n: v for n, v in RAILS.items() if v == 0 or n in powered}
        src_ext = {n: v for n, v in ext.items() if v is not None}
        if safe_ext is not None: src_ext['__P04_STOP'] = safe_ext
        oc = self.oc(current)
        for _ in range(60):
            drv = {}                                            # net -> list of driven values (active outputs)
            def put(n, v):
                if n and n != 'NC' and v is not None: drv.setdefault(n, []).append(v)
            for r, x in c.items():
                m = MODELS.get(x['value'])
                if m:
                    kind, gates, vccp, fam = m; on = self.pin(r, vccp) in powered
                    if not on:
                        if fam == 'HC':                          # unpowered HCMOS output sits at ~0 V through its clamp diodes
                            outs = [g[-1] for g in gates] if gates else [5, 6, 9, 8]
                            for o in outs: put(self.pin(r, o), 0)
                        continue
                    g = lambda p: val.get(self.pin(r, p))
                    if kind == 'and':
                        for (a, b), y in gates:
                            va, vb = g(a), g(b); put(self.pin(r, y), None if None in (va, vb) else va & vb)
                    elif kind == 'not':
                        for a, y in gates: put(self.pin(r, y), None if g(a) is None else 1 - g(a))
                    elif kind == 'buf':
                        for a, y in gates: put(self.pin(r, y), g(a))
                    elif kind == 'oe':
                        for a, oe, y in gates:
                            if g(oe) == 0: put(self.pin(r, y), g(a))
                    elif kind == 'ff':
                        for i, (d, clk, pre, clr, q, qn) in enumerate([(2, 3, 4, 1, 5, 6), (12, 11, 10, 13, 9, 8)]):
                            vp, vc = g(pre), g(clr)
                            if vp == 0 and vc == 0: qq, qb = 1, 1
                            elif vc == 0: qq = 0; qb = 1
                            elif vp == 0: qq = 1; qb = 0
                            else: qq = ff[i]; qb = 1 - qq
                            put(self.pin(r, q), qq); put(self.pin(r, qn), qb)
                elif x['value'].startswith('MCP120-'):
                    rail = self.pin(r, 2); key = '3V3A' if rail == '3V3A_P07' else '5VA'
                    if rail in powered and key not in sup_ok: put(self.pin(r, 1), 0)
                    if rail not in powered: put(self.pin(r, 1), 0)
                elif x['value'].startswith('TLV1702'):
                    if self.pin(r, 8) in powered and oc: put(self.pin(r, 1), 0)
                elif x['value'] == 'MMBT3904':
                    if val.get(self.pin(r, 1)) == 1: put(self.pin(r, 3), 0)
            new = {}
            for n, vs in drv.items(): new[n] = vs[0] if len(set(vs)) == 1 else None
            for n, v in src_ext.items():
                if n in new and new[n] != v: new[n] = 0 if 0 in (new[n], v) and n == 'SAFE_N' else None   # SAFE_N: open collectors win
                else: new.setdefault(n, v)
            for n, v in rails.items(): new.setdefault(n, v)
            for n, v in (force or {}).items(): new[n] = v              # stuck-at fault injection
            # passive nets: value of the driven net reached over the lowest total resistance (multi-source Dijkstra; tie -> undefined)
            adj = self.adj if safe_ext is None else self.adj_safe
            dist = {}; h = [(0.0, n, v) for n, v in new.items()]; heapq.heapify(h); fixed = set(new)
            while h:
                d, u, v = heapq.heappop(h)
                if u in dist:
                    if abs(d - dist[u]) < 1e-9 and new.get(u) != v and u not in fixed: new[u] = None
                    continue
                dist[u] = d
                if u not in fixed: new[u] = v
                for w, rv in adj.get(u, ()):
                    if w not in fixed and w not in dist and not (w.startswith('__') and w not in src_ext): heapq.heappush(h, (d + rv, w, v))
            if new == val: break
            val = new
        else:
            return None
        # asynchronous PRE / CLR change the stored state only after the network has settled (no transient glitches)
        for r, x in c.items():
            if x['value'] == 'SN74HC74D' and self.pin(r, 14) in powered:
                for i, (pre, clr) in enumerate([(4, 1), (10, 13)]):
                    vp, vc = val.get(self.pin(r, pre)), val.get(self.pin(r, clr))
                    if vc == 0 and vp != 0: ff[i] = 0
                    elif vp == 0: ff[i] = 1
        if force_check:
            v2 = self.run(ext, powered, sup_ok, current, list(ff), safe_ext, force, False)
            if v2 != val: return self.run(ext, powered, sup_ok, current, ff, safe_ext, force, True)
        return val

    def oc(self, current):
        hi, lo = self.an['trip_nom']
        return (current > hi or current < -lo) if current else False

    def analog(self):
        c = self.c
        def find(a, b):
            for r, x in c.items():
                if re.fullmatch(r'R\d+', r) and set(x['pins'].values()) == {a, b}: return ohms(x['value'])
            return None
        rf, rg = find('OC_HIGH', 'OC_FB'), find('OC_FB', G); rt, rb = find('REF_BUF', 'OC_LOW'), find('OC_LOW', G)
        sh = {'5m': 0.005, '10m': 0.010}.get(c['RSH1']['value'].split()[0], 1.0)
        gain = 50 if c['U1']['value'] == 'INA240A2' else 20
        if None in (rf, rg, rt, rb): return {'trip_nom': (1e9, -1e9)}
        hi = 2.5 * rf / rg / (gain * sh); lo = 2.5 * (1 - rb / (rt + rb)) / (gain * sh)
        return {'trip_nom': (hi, lo), 'rf': rf, 'rg': rg, 'rt': rt, 'rb': rb, 'sh': sh, 'gain': gain}


ALL = {'3V3_IO', '3V3A_P07', '5VA_P07', '5V_MOD', '5V_SYS', 'VMOTOR', 'REF25'}


def state(sim, ext, powered=ALL, sup=('3V3A', '5VA'), cur=0.0, ff=(1, 1), safe=1, force=None):
    f = list(ff); v = sim.run(ext, set(powered), set(sup), cur, f, safe, force); return v, f


def edge(sim, ext, ff, **kw):
    """Rising edge of ARM_CLK: settle with ARM_CLK = 0, sample D, apply unless PRE/CLR active, settle with ARM_CLK = 1."""
    e0 = dict(ext, ARM_CLK=0); v0, f = state(sim, e0, ff=ff, **kw)
    if v0 is None: return None, ff
    c = sim.c; ffr = next(r for r, x in c.items() if x['value'] == 'SN74HC74D')
    for i, (d, pre, clr) in enumerate([(2, 4, 1), (12, 10, 13)]):
        if v0.get(sim.pin(ffr, pre)) == 1 and v0.get(sim.pin(ffr, clr)) == 1 and v0.get(sim.pin(ffr, d)) in (0, 1): f[i] = v0[sim.pin(ffr, d)]
    return state(sim, dict(ext, ARM_CLK=1), ff=f, **kw)


def checks(c):
    out = []
    def ok(k, v, d=None): out.append({'id': k, 'pass': bool(v), 'note': d if isinstance(d, str) else json.dumps(d, ensure_ascii=False, default=str)[:300] if d is not None else ''})
    sim = Sim(c); an = sim.an
    # ---- exhaustive blocking table ----
    bad = []; blk = []; rows = 0
    for mp, sf, pwm, ina, inb, s3, s5, cur, q1, q2 in itertools.product((0, 1, None), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0.0, 9.0, -9.0), (0, 1), (0, 1)):
        ext = {'MOTOR_PERMIT': mp, 'PWM_OUT': pwm, 'ARM_CLK': 0, 'MOTOR_INA': ina, 'MOTOR_INB': inb, 'CS_ITEST_N': 1, 'ADC_SCLK': 0}
        sup = tuple(k for k, f in (('3V3A', s3), ('5VA', s5)) if f)
        v, f = state(sim, ext, sup=sup, cur=cur, ff=(q1, q2), safe=sf); rows += 1
        rails = s3 and s5; oc = cur != 0
        q1e = 0 if (not rails or oc) else q1; q2e = 1 if not rails else (0 if oc else q2)
        en = int(mp == 1 and sf == 1 and rails and not oc and q1e == 1)
        want = {'RPWM': en & pwm & ina, 'LPWM': en & pwm & inb, 'R_EN': en, 'L_EN': en}
        kp = int(mp == 1 and rails and not oc and q1e == 1)
        if v is None: bad.append(('no-settle', mp, sf, pwm, ina, inb, s3, s5, cur, q1, q2)); continue
        got = {n: v.get(n) for n in MOD_IN}
        if got != want: bad.append(('module', mp, sf, pwm, ina, inb, s3, s5, cur, q1, q2, got, want))
        if (mp != 1 or sf == 0 or oc or not rails) and any(got[n] != 0 for n in MOD_IN): blk.append((mp, sf, s3, s5, cur, q1, got))
        if (v.get('KPWR_COIL_LOW') == 0) != bool(kp): bad.append(('kpwr', mp, sf, s3, s5, cur, q1, v.get('KPWR_COIL_LOW')))
        if v.get('DRIVE_OK') != int(rails and q2e == 1): bad.append(('drive_ok', s3, s5, cur, q2, v.get('DRIVE_OK')))
        if (v.get('SAFE_N') == 0) != (oc or sf == 0): bad.append(('safe_n', sf, cur, v.get('SAFE_N')))
    ok('LOGIC-TABLE', not bad, {'rows': rows, 'bad': bad[:4]})
    ok('LOGIC-BLOCK-ALL-L', not blk and not any(b[0] == 'no-settle' for b in bad), {'rule': 'bez MOTOR_PERMIT / SAFE_N, przy OC lub zlych szynach -> RPWM, LPWM, R_EN, L_EN = L', 'bad': blk[:3]})
    # ---- dead domains and open tapes (inputs from P03 / P04 asserted where present) ----
    hot = {'MOTOR_PERMIT': 1, 'PWM_OUT': 1, 'ARM_CLK': 0, 'MOTOR_INA': 1, 'MOTOR_INB': 0, 'CS_ITEST_N': 1, 'ADC_SCLK': 0}
    res = {}
    for name, kw in [('3V3_IO off', dict(powered=ALL - {'3V3_IO'})), ('3V3A off', dict(powered=ALL - {'3V3A_P07', 'REF25'}, sup=('5VA',))),
                     ('5VA off', dict(powered=ALL - {'5VA_P07'}, sup=('3V3A',))), ('J_BP2 tape open', dict(safe=None)),
                     ('5V_MOD off', dict(powered=ALL - {'5V_MOD'}))]:
        e = dict(hot)
        if name == 'J_BP2 tape open': e.update(MOTOR_PERMIT=None, PWM_OUT=None, ARM_CLK=None)
        v, f = state(sim, e, **kw); res[name] = None if v is None else {n: v.get(n) for n in MOD_IN + ['KPWR_COIL_LOW']}
    good = all(r is not None and all(r[n] in (0, None) and r[n] != 1 for n in MOD_IN) and r['KPWR_COIL_LOW'] != 0 for k, r in res.items() if k != '5V_MOD off')
    good &= res['3V3_IO off'] is not None and all(res['3V3_IO off'][n] == 0 for n in MOD_IN)
    ok('DEAD-DOMAINS-OPEN-TAPE', good, res)
    v, f = state(sim, dict(hot, MOTOR_PERMIT=None, PWM_OUT=None, ARM_CLK=None), safe=None)
    ok('OPEN-TAPE-DEFINED', v is not None and all(v.get(n) in (0, 1) for n in ['PERMIT_P07', 'PWM_P07', 'SAFE_OK', 'ARM_CLK']) and v.get('SAFE_OK') == 0,
       None if v is None else {n: v.get(n) for n in ['PERMIT_P07', 'PWM_P07', 'SAFE_OK', 'ARM_CLK']})
    # ---- single fault: AND gate output stuck H while drive is not permitted -> U16 OE keeps RPWM / LPWM low ----
    st = {}
    for net in ('RPWM_L', 'LPWM_L'):
        v, f = state(sim, dict(hot, MOTOR_PERMIT=0), force={net: 1}); st[net] = None if v is None else {n: v.get(n) for n in MOD_IN}
    ok('OE-BLOCKS-STUCK-GATE', all(r is not None and all(r[n] == 0 for n in MOD_IN) for r in st.values()), st)
    # ---- latch sequences ----
    seq = []; base = {'MOTOR_PERMIT': 0, 'PWM_OUT': 1, 'ARM_CLK': 0, 'MOTOR_INA': 1, 'MOTOR_INB': 0, 'CS_ITEST_N': 1, 'ADC_SCLK': 0}
    v, f = state(sim, base, sup=(), ff=(1, 0)); seq.append(('power-up, rails low', v and v.get('DRIVE_OK') == 0 and v.get('R_EN') == 0 and f == [0, 1]))
    v, f = state(sim, base, ff=f); seq.append(('rails OK, no ARM: DRIVE_OK = 1, drive off', v and v.get('DRIVE_OK') == 1 and v.get('R_EN') == 0))
    v, f = state(sim, dict(base, MOTOR_PERMIT=1), ff=f); seq.append(('MOTOR_PERMIT without ARM: drive off', v and v.get('R_EN') == 0 and v.get('KPWR_COIL_LOW') != 0))
    v, f = edge(sim, base, f); seq.append(('ARM edge with PERMIT = L: armed', v and f[0] == 1))
    v, f = state(sim, dict(base, MOTOR_PERMIT=1), ff=f); seq.append(('PERMIT = H: drive on, KPWR on', v and v.get('R_EN') == 1 and v.get('RPWM') == 1 and v.get('KPWR_COIL_LOW') == 0))
    v, f = state(sim, dict(base, MOTOR_PERMIT=1), ff=f, cur=9.0); seq.append(('OC: drive off, DRIVE_OK = 0, SAFE_N pulled', v and v.get('R_EN') == 0 and v.get('DRIVE_OK') == 0 and v.get('SAFE_N') == 0 and f == [0, 0]))
    v, f = state(sim, dict(base, MOTOR_PERMIT=1), ff=f); seq.append(('OC gone: stays off (latched)', v and v.get('R_EN') == 0 and v.get('DRIVE_OK') == 0))
    v, f = edge(sim, dict(base, MOTOR_PERMIT=1), f); seq.append(('ARM edge with PERMIT = H: no re-arm, DRIVE_OK back', v and f[0] == 0 and v.get('R_EN') == 0 and v.get('DRIVE_OK') == 1))
    v, f = edge(sim, base, f, cur=9.0); seq.append(('ARM edge during OC: stays tripped', v and f == [0, 0]))
    v, f = edge(sim, base, f); v, f = state(sim, dict(base, MOTOR_PERMIT=1), ff=f); seq.append(('ARM with PERMIT = L, then PERMIT: drive on', v and v.get('R_EN') == 1))
    v, f = state(sim, dict(base, MOTOR_PERMIT=1), ff=f, safe=0); seq.append(('SAFE_N = L: drive off at once', v and v.get('R_EN') == 0 and v.get('RPWM') == 0))
    ok('LATCH-SEQUENCES', all(s[1] for s in seq), [s[0] for s in seq if not s[1]])
    # ---- SPI tri-state ----
    v1, _ = state(sim, dict(base, CS_ITEST_N=1)); v0, _ = state(sim, dict(base, CS_ITEST_N=0)); vo, _ = state(sim, dict(base, CS_ITEST_N=None))
    u7 = next((r for r, x in c.items() if x['value'] == '74LVC125AD' and x['pins'].get('9') == 'ADC_DOUT'), None)
    oe_ok = u7 is not None and c[u7]['pins'].get('10') == 'CS_LOCAL_N' and c[u7]['pins'].get('8') == 'DOUT_TX'
    ok('SPI-DOUT-TRISTATE', oe_ok and v1 and v1.get('CS_LOCAL_N') == 1 and v0 and v0.get('CS_LOCAL_N') == 0 and vo and vo.get('CS_LOCAL_N') == 1,
       'DOUT_TX nadaje tylko przy CS_ITEST_N = L; P03 bez zasilania -> CS nieaktywne (R17)')
    # ---- analog ----
    if 'rf' not in an:
        for k in ('OC-WINDOW', 'OC-BELOW-INA-SATURATION'): ok(k, False, 'threshold network not found')
    else:
        g = an['gain'] * an['sh']
        def trip(sign, corner):
            vr = VREF[corner]; ge = 1 + (INA_GAIN_ERR + .01) * (1 if corner else -1)     # gain and shunt tolerance
            k = (1 + 0.001) / (1 - 0.001) if corner else (1 - 0.001) / (1 + 0.001)
            if sign > 0: dv = vr * an['rf'] / an['rg'] * k + (OPA_VOS * (1 + an['rf'] / an['rg']) + CMP_VOS + INA_VOS * an['gain']) * (1 if corner else -1)
            else: dv = vr * (1 - an['rb'] / (an['rt'] + an['rb']) / k) + (OPA_VOS + CMP_VOS + INA_VOS * an['gain']) * (1 if corner else -1)
            return dv / (g * ge)
        hi = (trip(1, 0), trip(1, 1)); lo = (trip(-1, 0), trip(-1, 1))
        ok('OC-WINDOW', min(hi + lo) >= I_OC_LIMIT_MIN and max(hi + lo) <= 9.0, {'plus_A': [round(x, 2) for x in hi], 'minus_A': [round(x, 2) for x in lo], 'nominal': [round(x, 3) for x in an['trip_nom']]})
        vs_min = VSYS[0] - 0.010 * 10 - 0.0                 # R50 10R x ~10 mA
        vout_max = VREF[1] * (1 + .001) + g * (1 + INA_GAIN_ERR + .01) * max(hi + lo)
        vhi_max = VREF[1] * (1 + an['rf'] / an['rg']) * 1.002 + OPA_VOS * 2
        ok('OC-BELOW-INA-SATURATION', vout_max <= vs_min - INA_SWING and vhi_max <= vs_min - 0.025,
           {'INA_out_at_trip_max_V': round(vout_max, 3), 'OC_HIGH_max_V': round(vhi_max, 3), '5VA_min_V': round(vs_min, 3)})
    def rv(ref): return ohms(c[ref]['value']) if ref in c else None
    def rbetween(a, b):
        return [ohms(x['value']) for r, x in c.items() if re.fullmatch(r'R\d+', r) and set(x['pins'].values()) == {a, b}]
    dv = rbetween('I_T_OUT', 'I_DIV') + rbetween('I_DIV', G)
    cdiv = [x for r, x in c.items() if r.startswith('C') and set(x['pins'].values()) == {'I_DIV', G}]
    if len(dv) == 2 and cdiv:
        ratio = dv[1] / (dv[0] + dv[1]); tau = dv[0] * dv[1] / (dv[0] + dv[1]) * 100e-9 if cdiv[0]['value'].startswith('100n') else None
        fs = (VREF[0] - 0.0) / ratio
        ok('ITEST-SCALE', abs(ratio - 0.5) < 1e-3 and tau and 0.1e-3 <= tau <= 0.5e-3 and (fs - 2.5) / (g) >= 9.5 and 2.5 / g >= 9.5,
           {'ratio': ratio, 'tau_ms': tau and round(tau * 1e3, 3), 'range_A': round(2.5 / g, 2)})
    else: ok('ITEST-SCALE', False, 'divider not found')
    shp = 10.0 ** 2 * 0.005 if c['RSH1']['value'].startswith('5m') else 1e9
    ok('SHUNT-POWER-10A', shp <= 0.5 * 1.0 and set(c['RSH1']['pins'].values()) == {'MOD_MP', 'K_PLUS', 'K_MINUS', 'T_EGR_P1'}, {'P10A_W': shp})
    rp = rbetween('VMOTOR', 'MOD_BP'); rbl = rbetween('MOD_BP', PG)
    pw = [x for r, x in c.items() if set(x['pins'].values()) == {'VMOTOR', 'MOD_BP'} and r.startswith('R')]
    pfault = VM_MAX ** 2 / rp[0] if rp else 1e9
    rating = 1.0 if pw and '2512' in pw[0]['fp'] else 0.25
    ok('PRECHARGE-R', bool(rp) and pfault <= 0.5 * rating and VM_MAX / rp[0] <= 0.02 and rbl and 0.85 <= rbl[0] / (rbl[0] + rp[0]) <= 0.95,
       {'R_ohm': rp, 'fault_W': round(pfault, 3), 'rating_W': rating, 'Imotor_open_mA': rp and round(1e3 * VM_MAX / rp[0], 1), 'MOD_BP_open_ratio': rp and rbl and round(rbl[0] / (rbl[0] + rp[0]), 3)})
    # KPWR: base drive, clamp vs VCEO, coil voltage ratio
    k1 = c.get('K1', {}); q1 = next((r for r, x in c.items() if x['value'] == 'MMBT3904' and x['pins'].get('3') == 'KPWR_COIL_LOW'), None)
    z = next((x for r, x in c.items() if x['value'].startswith('BZT52C') and 'KPWR_CLAMP' in x['pins'].values()), None)
    vz = float(z['value'][6:].replace('V', '.')) if z else 99
    rb_ = rbetween('LOCAL_PERMIT', 'KPWR_B'); ib = (2.8 - 0.75) / rb_[0] if rb_ else 0          # HC08 VOH ~2.8 V at 3 mA, 3.3 V supply
    icoil = 12 / 360
    clamp = VM_MAX + vz + 0.7
    ok('KPWR-DRIVE-CLAMP', q1 is not None and c[q1]['pins'].get('2') == PG and k1.get('pins', {}).get('A1') == 'VMOTOR' and ib >= icoil / 15 and clamp <= 0.85 * 40 and VM_MAX / 12 <= COIL_MAX_RATIO,
       {'Ib_mA': round(ib * 1e3, 2), 'Icoil_mA': round(icoil * 1e3, 1), 'clamp_V': clamp, 'coil_ratio': round(VM_MAX / 12, 2)})
    tvs = [x for r, x in c.items() if x['value'].startswith('SMCJ') and set(x['pins'].values()) == {'VMOTOR', PG}]
    ok('TVS-VMOTOR', bool(tvs) and float(re.sub(r'[^\d.]', '', tvs[0]['value'][4:])) >= VM_MAX and tvs[0]['pins'].get('1') == 'VMOTOR', [t['value'] for t in tvs])
    # IS diagnostics: divider loading, threshold band, clamp
    good = True; band = {}
    for isn, div in (('R_IS', 'ISR_DIV'), ('L_IS', 'ISL_DIV')):
        rt_, rb2 = rbetween(isn, div), rbetween(div, G)
        clampd = [x for r, x in c.items() if x['value'] == 'BAT54S' and x['pins'].get('3') == div and x['pins'].get('1') == G and x['pins'].get('2') == '3V3_IO']
        if not (rt_ and rb2 and clampd): good = False; continue
        rl = 1 / (1 / 10000 + 1 / (rt_[0] + rb2[0])); k = rb2[0] / (rt_[0] + rb2[0])
        lo_ = VT_SCHMITT[0] / k * KILIS[0] / rl; hi_ = VT_SCHMITT[1] / k * KILIS[1] / rl
        iclamp = (VM_MAX * k - 3.6) / (rt_[0] * rb2[0] / (rt_[0] + rb2[0]))
        band[isn] = [round(lo_, 2), round(hi_, 2)]; good &= 1.0 <= lo_ and hi_ <= I_RUN and 10000 / rl - 1 <= 0.06 and iclamp <= 1e-3
    ok('IS-DIAG', good, band)
    # ground separation: no part with pins on both GND and PGND; MOD_GND only through >= 4.7 R to GND
    POWER_SIDE = {'VMOTOR', 'MOD_BP', 'MOD_MP', 'T_EGR_P1', 'T_EGR_P3', 'KPWR_COIL_LOW', 'KPWR_CLAMP', 'KPWR_B'}
    both = [r for r, x in c.items() if {G, PG} <= set(x['pins'].values()) or (G in x['pins'].values() and POWER_SIDE & set(x['pins'].values()))]
    mg = [(r, ohms(x['value'])) for r, x in c.items() if 'MOD_GND' in x['pins'].values() and r.startswith('R')]
    direct = [r for r, x in c.items() if 'MOD_GND' in x['pins'].values() and not r.startswith(('R', 'J'))]
    ok('GND-PGND-SEPARATE', not both and len(mg) == 1 and mg[0][1] is not None and 4.7 <= mg[0][1] <= 22 and not direct, {'both': both, 'mod_gnd': mg})
    return out, {'oc': an, 'rows': rows}


def mutate(c, ref, pin=None, net=None, value=None):
    m = copy.deepcopy(c)
    if pin is not None: m[ref]['pins'][str(pin)] = net
    if value is not None: m[ref]['value'] = value
    return m


c = read(P / 'verification/P07.xml')
res, info = checks(c)
MUT = [('SAFE_OK bypassed (U13.2 -> 3V3_IO)', ('U13', 2, '3V3_IO'), 'LOGIC-TABLE'),
       ('OC does not clear the latch (U12.5 -> 3V3_IO)', ('U12', 5, '3V3_IO'), 'LOGIC-TABLE'),
       ('no OE blocking on RPWM (U16.1 -> GND)', ('U16', 1, 'GND'), 'OE-BLOCKS-STUCK-GATE'),
       ('re-arm under PERMIT (U15.2 -> 3V3_IO)', ('U15', 2, '3V3_IO'), 'LATCH-SEQUENCES'),
       ('NO_TRIP not preset at power-up (U15.10 -> 3V3_IO)', ('U15', 10, '3V3_IO'), 'LATCH-SEQUENCES'),
       ('no pull-down on MOTOR_PERMIT (R28 open)', ('R28', 1, 'NC'), 'OPEN-TAPE-DEFINED'),
       ('Q2 collector off SAFE_N', ('Q2', 3, 'NC'), 'LOGIC-TABLE'),
       ('DOUT always driving (U7.10 -> GND)', ('U7', 10, 'GND'), 'SPI-DOUT-TRISTATE'),
       ('OC_HIGH too high (R11 12K)', ('R11', None, None, '12K'), 'OC-WINDOW'),
       ('OC_HIGH saturates INA240 (R11 9.53K)', ('R11', None, None, '9.53K'), 'OC-BELOW-INA-SATURATION'),
       ('ITEST divider unequal (R9 10K)', ('R9', None, None, '10K'), 'ITEST-SCALE'),
       ('precharge 100R', ('R4', None, None, '100R'), 'PRECHARGE-R'),
       ('Zener 27 V', ('D3', None, None, 'BZT52C27'), 'KPWR-DRIVE-CLAMP'),
       ('TVS 15 V', ('D1', None, None, 'SMCJ15A'), 'TVS-VMOTOR'),
       ('IS divider 10K/10K', ('R44', None, None, '10K'), 'IS-DIAG'),
       ('B- tied to GND (R5.2 -> GND)', ('R5', 2, 'GND'), 'GND-PGND-SEPARATE'),
       ('shunt 10 mOhm', ('RSH1', None, None, '10m'), 'SHUNT-POWER-10A'),
       ('LPWM gate without OE (U16.4 -> GND)', ('U16', 4, 'GND'), 'OE-BLOCKS-STUCK-GATE'),
       ('KPWR base resistor 4.7K', ('R2', None, None, '4K7'), 'KPWR-DRIVE-CLAMP')]
neg = []
for name, mt, target in MUT:
    ref = mt[0]; m = mutate(c, ref, *mt[1:3]) if mt[1] is not None else mutate(c, ref, value=mt[3])
    r, _ = checks(m); failed = [x['id'] for x in r if not x['pass']]
    neg.append({'mutation': name, 'target': target, 'caught': target in failed, 'checks': failed})
r0, _ = checks(copy.deepcopy(c)); null_clean = all(x['pass'] for x in r0)
out = {'checks': res, 'negative_controls': neg, 'null_control_clean': null_clean, 'analysis': info}
(P / 'verification/electrical-checks.json').write_text(json.dumps(out, indent=1, ensure_ascii=False, default=str) + '\n', encoding='utf-8')
for x in res: print(('PASS ' if x['pass'] else 'FAIL ') + x['id'], x['note'][:160])
for t in neg: print(('caught ' if t['caught'] else 'MISSED ') + t['mutation'], t['checks'])
print('null control clean:', null_clean)
sys.exit(0 if all(x['pass'] for x in res) and all(t['caught'] for t in neg) and null_clean else 1)
