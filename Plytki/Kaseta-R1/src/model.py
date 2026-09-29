"""Kaseta R1 — model rozmieszczenia płytek EGRLab (koncepcja, nie projekt wykonawczy).

Płytki stoją pionowo, równolegle, stroną elementów do tyłu, na prętach M3 przez narożne otwory
(rozstaw 150 × 110 mm, wspólny dla P01–P05). Dwie kolumny: L (za P03) i R (za P05); P03|P05 w pierwszej
płaszczyźnie (złącze B2B). Małe płytki na płytach nośnych 160 × 120 z tym samym rozstawem otworów.
Panel (DT, przełączniki, BNC) na ścianie przedniej, P11 w strefie panelu przed kolumną R.

Współrzędne robocze („widok od strony elementów”, od tyłu): X w prawo (0 = lewa krawędź P03),
Y do tyłu (0 = powierzchnia elementów płaszczyzny 1), Z w górę (0 = dolna krawędź płytek 160 × 120).
Rysunek przelicza X na widok od przodu.
"""
import json, itertools, math
from pathlib import Path

R = Path(__file__).resolve().parents[1]
B = json.loads((R/'dane'/'plytki.json').read_text(encoding='utf-8'))
B['P07'] = {'W': 120.0, 'H': 100.0, 'parts': [], 'holes': [], 'source': 'brak PCB (HOLD) — rezerwa obrysu v6.1',
            'sha256': ''}

T, SOLDER, GAP = 1.6, 3.0, 1.0          # laminat, wystające wyprowadzenia THT od spodu, luz
CARRIER = 2.0 + 2.0 + 6.0               # łby śrub + płyta nośna 2 mm + dystanse 6 mm
COL_X = {'L': 0.0, 'R': 165.0}          # szczelina 5 mm między P03 i P05 (B2B do przymiarki)
COL_W, COL_H = 160.0, 120.0
M_LEFT, M_RIGHT, M_BOTTOM, M_TOP = 10.0, 20.0, 10.0, 15.0  # kanały wiązek; z prawej także BNC AUX
PANEL_DEPTH = 45.0                      # części panelu (tył DT, przełączniki, BNC) od ściany przedniej
P11_STANDOFF, BACK = 10.0, 5.0
WALL = 3.0
SLACK = 10.0                            # łuk odciążający i zapas na trasę

# Wysokość zajęta nad stroną elementów [mm] i jej źródło
ENV = {'P01': 65.0, 'P02': 50.0, 'P03': 30.0, 'P04': 35.0, 'P05': 30.0, 'P06': 30.0, 'P07': 35.0,
       'P08': 25.0, 'P09': 30.0, 'P10': 20.0, 'P11': 30.0}
ENV_LOW_HS = 30.0                       # P01 z SK129 25,4 STS (ten sam footprint, otwór TO-220 na 13,5 mm)
ENV_SRC = {
    'P01': 'SK129 63,5 mm (MECHANIKA R3.1); wariant LOGGER: SK129 25,4 mm → ok. 30 mm (C6 13 mm, wtyk J6)',
    'P02': 'puszki Ø35 × 45 mm + 3 mm nad zaworem; wtyki Mini-Fit 35 mm (MECHANIKA R3)',
    'P03': 'moduł Waveshare na listwach, wtyki IDC i Mini-Fit z przewodami — szacunek',
    'P04': 'Mini-Fit J7/J8 z wtykiem i łukiem przewodu — jak P02',
    'P05': 'podstawki DIP, przekaźniki G6K, wiązki PTH — szacunek',
    'P06': 'PBV pionowo, rezerwa ≥ 25 mm pod pokrywą (MECHANIKA P06)',
    'P07': 'brak PCB (HOLD); nośnik VNH5019 — szacunek',
    'P08': 'DIP, G6K, Mini-Fit 2p — szacunek',
    'P09': 'moduły MAX31856 w gniazdach + zaciski termopar — szacunek',
    'P10': 'SOIC, wiązki PTH — szacunek',
    'P11': '≥ 30 mm wolnej wysokości nad PCB (WIAZKI.md P11)'}

# Warianty: kolejność płaszczyzn w kolumnach (od przodu). '+' = kilka płytek na jednej płycie nośnej.
VARIANTS = {
    'LOGGER': {'title': 'LOGGER — bez P04, P07, P08; P01 z radiatorami SK129 25,4 mm',
               'low_hs': True, 'cols': {'L': ['P03', 'P06', 'P09', 'P10'], 'R': ['P05', 'P02', 'P01']}},
    'PELNY': {'title': 'PEŁNY — wszystkie płytki, P01 z radiatorami SK129 63,5 mm, P07 jako rezerwa 120 × 100',
              'low_hs': False, 'cols': {'L': ['P03', 'P04', 'P06', 'P09', 'P08+P10'], 'R': ['P05', 'P02', 'P01', 'P07']}},
}
PCB_SLOT = {'P01', 'P02', 'P03', 'P04', 'P05'}   # płytki 160 × 120 bezpośrednio na prętach

# Wiązki: (nazwa, (płytka, ref, typ), (płytka, ref, typ), długość z projektu [mm], waga)
# typ: idc / mf (Mini-Fit, MSTB pionowe) / pth (lutowane przewody) / edge (złącze poziome) / any (P07) / wall
HARNESS = [
    ('TAPS', ('P05', 'J4', 'pth'), ('P11', 'J7', 'mf'), 50, 10),
    ('AUX', ('P05', 'J6', 'pth'), ('WALL', 'AUX_BNC', 'wall'), 50, 10),
    ('SAFE', ('P03', 'J4', 'idc'), ('P04', 'J2', 'pth'), 150, 10),
    ('ILOG', ('P03', 'J2', 'idc'), ('P06', 'J2', 'pth'), 100, 3),
    ('TEMP', ('P03', 'J7', 'idc'), ('P09', 'J2', 'pth'), 100, 3),
    ('ITEST', ('P03', 'J3', 'idc'), ('P07', '*', 'any'), 100, 3),
    ('CAN', ('P03', 'J8', 'idc'), ('P10', 'J2', 'pth'), 150, 1),
    ('DIR', ('P03', 'J5', 'idc'), ('P07', '*', 'any'), 150, 1),
    ('SFAULT', ('P03', 'J6', 'idc'), ('P08', 'J3', 'pth'), 150, 1),
    ('PANELCORE', ('P03', 'J9', 'mf'), ('P11', 'J4', 'pth'), 300, 1),
    ('DAQOK', ('P05', 'J3', 'pth'), ('P04', 'J5', 'idc'), 150, 1),
    ('VSENSE', ('P02', 'J11', 'mf'), ('P05', 'J5', 'pth'), 150, 1),
    ('LV03', ('P02', 'J3', 'mf'), ('P03', 'J10', 'pth'), 200, 1),
    ('LV04', ('P02', 'J4', 'mf'), ('P04', 'J1', 'pth'), 200, 1),
    ('LV05', ('P02', 'J5', 'mf'), ('P05', 'J2', 'pth'), 200, 1),
    ('LV06', ('P02', 'J6', 'mf'), ('P06', 'J1', 'pth'), 200, 1),
    ('LV07', ('P02', 'J7', 'mf'), ('P07', '*', 'any'), 200, 1),
    ('LV08', ('P02', 'J8', 'mf'), ('P08', 'J1', 'pth'), 200, 1),
    ('LV09', ('P02', 'J9', 'mf'), ('P09', 'J1', 'pth'), 200, 1),
    ('LV10', ('P02', 'J10', 'mf'), ('P10', 'J1', 'pth'), 200, 1),
    ('PSUOK', ('P02', 'J12', 'pth'), ('P04', 'J6', 'idc'), 150, 1),
    ('SUPPLY', ('P01', 'J6', 'edge'), ('P02', 'J1', 'pth'), 200, 1),
    ('PG', ('P01', 'J5', 'pth'), ('P04', 'J7', 'mf'), 200, 1),
    ('SENSOR', ('P04', 'J4', 'idc'), ('P08', 'J2', 'pth'), 150, 1),
    ('DRIVE', ('P04', 'J3', 'idc'), ('P07', '*', 'any'), 150, 1),
    ('PANELSAFE', ('P04', 'J8', 'mf'), ('P11', 'J5', 'pth'), 300, 1),
    ('VMOTOR', ('P02', 'J2', 'edge'), ('P07', '*', 'any'), 200, 1),
    ('ISERIES', ('P06', 'J3', 'pth'), ('P11', 'J1', 'mf'), 150, 1),
    ('TMOTOR', ('P07', '*', 'any'), ('P11', 'J9', 'pth'), 150, 1),
    ('TSENSOR', ('P08', 'J4', 'mf'), ('P11', 'J10', 'pth'), 150, 1),
    ('W5 DT L1', ('P11', 'J2', 'pth'), ('WALL', 'DT_L1', 'wall'), 150, 1),
    ('W6 DT L2', ('P11', 'J3', 'pth'), ('WALL', 'DT_L2', 'wall'), 150, 1),
    ('W7 DT TEST', ('P11', 'J8', 'pth'), ('WALL', 'DT_TEST', 'wall'), 150, 1),
    ('W8 styki', ('P11', 'J11', 'pth'), ('WALL', 'SW_MID', 'wall'), 200, 1),
    ('W9 SCOPE', ('P11', 'J6', 'pth'), ('WALL', 'BNC_SCOPE', 'wall'), 100, 1),
    ('BAT', ('P01', 'J7', 'pth'), ('BACKWALL', 'BAT', 'wall'), 200, 1),
]
EXIT = {'idc': 20.0, 'mf': 25.0, 'pth': 8.0, 'edge': 20.0, 'any': 20.0, 'wall': 0.0}

# Panel przedni (widok od tyłu, X jak płytki): części przed kolumną L, P11 przed kolumną R.
# (X, Z, szer., wys., głębokość do wnętrza, opis)
PANEL = {
    'DT_L1': (22.0, 98.0, 36, 30, 30, 'DT L1'), 'DT_L2': (65.0, 98.0, 36, 30, 30, 'DT L2'),
    'DT_TEST': (108.0, 98.0, 36, 30, 30, 'DT TEST'), 'BNC_SCOPE': (148.0, 98.0, 16, 16, 20, 'SCOPE'),
    'SW_ARM': (20.0, 52.0, 22, 22, 30, 'ARM'), 'SW_STOP': (50.0, 52.0, 22, 22, 35, 'STOP'),
    'SW_MARK': (80.0, 52.0, 22, 22, 30, 'MARK'), 'SW_KEY': (110.0, 52.0, 22, 22, 35, 'KEY TEST'),
    'SW_BYPASS': (140.0, 52.0, 16, 16, 25, 'BYPASS'), 'SW_MID': (65.0, 52.0, 0, 0, 30, ''),
    'TC1': (40.0, 22.0, 18, 14, 15, 'TC1'), 'TC2': (70.0, 22.0, 18, 14, 15, 'TC2'),
}
# Przepusty na ścianie tylnej w kanałach nad i pod płytkami (X, Z w widoku od tyłu)
BACKWALL = {'BAT': (184.0, 128.0, 'BAT 2×2,5 mm² (kanał górny)'), 'OBD': (12.0, -5.0, 'OBD (kanał dolny)')}
# BNC AUX na ścianie po stronie P05 (X za prawą krawędzią P05), na wysokości J6 P05
AUX_Z = 120.0 - 83.0


def rot_xy(x, y, W, H, r):
    """Współrzędne punktu płytki (x w prawo, y w dół, widok od strony elementów) po obrocie r."""
    if r == 0:
        return x, y, W, H
    if r == 180:
        return W - x, H - y, W, H
    if r == 90:
        return H - y, x, H, W
    if r == 270:
        return y, W - x, H, W
    raise ValueError(r)


def part(board, ref):
    for p in B[board]['parts']:
        if p['ref'] == ref:
            return p
    raise KeyError(f'{board}.{ref}')


class Layout:
    def __init__(self, variant, opts):
        self.v, self.opts = variant, opts
        self.cfg = VARIANTS[variant]
        self.env = dict(ENV)
        if self.cfg['low_hs']:
            self.env['P01'] = ENV_LOW_HS
        self.place = {}      # płytka -> dict(col, k, x0, ztop, r, w, h, Ys, carrier)
        self.planes = {}     # (col, k) -> dict(Ys, env, carrier, boards)
        for col, seq in self.cfg['cols'].items():
            Y = 0.0
            prev_env = None
            for k, item in enumerate(seq):
                boards = item.split('+')
                carrier = not (len(boards) == 1 and boards[0] in PCB_SLOT)
                if k > 0:
                    Y = Y + prev_env + GAP + (CARRIER + T if carrier else SOLDER + T)
                env = max(self.env[b] for b in boards)
                self.planes[(col, k)] = {'Ys': Y, 'env': env, 'carrier': carrier, 'boards': boards}
                for b in boards:
                    r, x0, zt = opts.get(b, (0, 0.0, COL_H))
                    W, H = B[b]['W'], B[b]['H']
                    _, _, w, h = rot_xy(0, 0, W, H, r)
                    self.place[b] = {'col': col, 'k': k, 'x0': COL_X[col] + x0, 'ztop': zt, 'r': r, 'w': w, 'h': h,
                                     'Ys': Y, 'carrier': carrier}
                prev_env = env
        self.depth_cols = {c: max(p['Ys'] + p['env'] for (cc, k), p in self.planes.items() if cc == c) for c in COL_X}
        self.stack = max(self.depth_cols.values())
        self.front = PANEL_DEPTH + GAP + SOLDER + T                  # od ściany przedniej do Y = 0
        self.Yw = -self.front
        self.p11_Ys = self.Yw + P11_STANDOFF + T
        r11 = opts.get('P11', (180, 0.0, 118.0))
        self.place['P11'] = {'col': 'R', 'k': -1, 'x0': COL_X['R'], 'ztop': r11[2], 'r': r11[0], 'w': 160.0, 'h': 110.0,
                             'Ys': self.p11_Ys, 'carrier': False}
        self.X0, self.X1 = -M_LEFT, COL_X['R'] + COL_W + M_RIGHT
        self.Z0, self.Z1 = -M_BOTTOM, COL_H + M_TOP
        self.Y1 = self.stack + BACK
        self.inner = (self.X1 - self.X0, self.Y1 - self.Yw, self.Z1 - self.Z0)
        self.outer = tuple(d + 2 * WALL for d in self.inner)

    def board_point(self, b, x, y):
        p = self.place[b]
        xr, yr, _, _ = rot_xy(x, y, B[b]['W'], B[b]['H'], p['r'])
        return p['x0'] + xr, p['ztop'] - yr

    def region(self, b, side):
        """Obszar, w którym leży wyjście przewodu: 'front', ('gap', col, k) albo 'back'."""
        p = self.place[b]
        if b == 'P11':
            return 'front'
        if side < 0:                       # strona lutowania: tylko płaszczyzna 1 ma przed sobą strefę panelu
            return 'front' if p['k'] == 0 else None
        seq = self.cfg['cols'][p['col']]
        return 'back' if p['k'] == len(seq) - 1 else ('gap', p['col'], p['k'])

    def endpoint(self, b, ref, kind):
        """Lista możliwych wyjść: (X, Y, Z, obszar, długość wyjścia, kanał wymuszony)."""
        if b == 'BACKWALL':
            X, Z, _ = BACKWALL[ref]
            return [(X, self.Y1 - 15.0, Z, 'back', 0.0, None)]
        if b == 'WALL':
            if ref == 'AUX_BNC':
                return [(COL_X['R'] + COL_W + 2.0, 12.0, AUX_Z, 'right', 0.0, None)]
            X, Z, w, h, d, _ = PANEL[ref]
            return [(X, self.Yw + d, Z, 'front', 0.0, None)]
        p = self.place[b]
        if kind == 'any':                  # P07 bez PCB: złącze w dowolnym miejscu obrysu
            out = []
            for i, j in itertools.product(range(5), range(5)):
                X = p['x0'] + p['w'] * (0.1 + 0.2 * i)
                Z = p['ztop'] - p['h'] * (0.1 + 0.2 * j)
                out.append((X, p['Ys'] + EXIT['any'], Z, self.region(b, +1), EXIT['any'], None))
            return out
        q = part(b, ref)
        bx = q['box']
        cx, cy = (bx[0] + bx[2]) / 2, (bx[1] + bx[3]) / 2
        X, Z = self.board_point(b, cx, cy)
        if kind == 'edge':
            # złącze poziome: przewód wychodzi za najbliższą krawędź płytki
            xs = [X - p['x0'], p['x0'] + p['w'] - X, p['ztop'] - Z, Z - (p['ztop'] - p['h'])]
            e = xs.index(min(xs))
            if e == 0:
                pt, ch = (p['x0'] - EXIT['edge'], p['Ys'] + 5, Z), 'left'
            elif e == 1:
                pt, ch = (p['x0'] + p['w'] + EXIT['edge'], p['Ys'] + 5, Z), 'right'
            elif e == 2:
                pt, ch = (X, p['Ys'] + 5, p['ztop'] + EXIT['edge']), 'top'
            else:
                pt, ch = (X, p['Ys'] + 5, p['ztop'] - p['h'] - EXIT['edge']), 'bottom'
            # wyjście w stronę drugiej kolumny = kolizja
            if (p['col'] == 'L' and ch == 'right') or (p['col'] == 'R' and ch == 'left'):
                return [(pt[0], pt[1], pt[2], 'blocked', EXIT['edge'] + min(xs), ch)]
            return [(pt[0], pt[1], pt[2], ch, EXIT['edge'] + min(xs), ch)]
        outs = []
        for side in ((+1, -1) if kind == 'pth' else (+1,)):
            reg = self.region(b, side)
            if reg is None:
                continue
            Ys = p['Ys'] if side > 0 else p['Ys'] - T - SOLDER
            outs.append((X, Ys + side * EXIT[kind], Z, reg, EXIT[kind], None))
        return outs

    def route(self, a, b):
        """Długość trasy między wyjściami (bez długości wyjść) — przez ten sam obszar albo kanał."""
        (xa, ya, za, ra, _, fa), (xb, yb, zb, rb, _, fb) = a, b
        if 'blocked' in (ra, rb):
            return 1e4
        if ra == rb and ra not in ('left', 'right', 'top', 'bottom'):
            return abs(xa - xb) + abs(ya - yb) + abs(za - zb)
        best = 1e9
        chans = {'top': COL_H + 2, 'bottom': -2.0, 'left': -2.0, 'right': COL_X['R'] + COL_W + 2}
        for ch, c in chans.items():
            # ze szczeliny w kolumnie L nie ma przejścia do kanału po stronie P05 i odwrotnie
            if any(isinstance(r, tuple) and ((ch == 'left' and r[1] != 'L') or (ch == 'right' and r[1] != 'R'))
                   for r in (ra, rb)):
                continue
            if ch in ('top', 'bottom'):
                d = abs(za - c) + abs(zb - c) + abs(xa - xb) + abs(ya - yb)
            else:
                d = abs(xa - c) + abs(xb - c) + abs(za - zb) + abs(ya - yb)
            best = min(best, d)
        return best

    def harness(self, name, A, Bn):
        ext = ('WALL', 'BACKWALL')
        if (A[0] not in self.place and A[0] not in ext) or (Bn[0] not in self.place and Bn[0] not in ext):
            return None
        best = None
        for ea in self.endpoint(*A):
            for eb in self.endpoint(*Bn):
                L = ea[4] + eb[4] + self.route(ea, eb) + SLACK
                if best is None or L < best[0]:
                    best = (L, ea, eb)
        return best

    def check(self, relocate_j7=True):
        rows = []
        for name, A, Bn, plan, wgt in HARNESS:
            if name == 'TAPS' and relocate_j7:
                h = self.harness_taps_relocated()
            else:
                h = self.harness(name, A, Bn)
            if h is None:
                continue
            L = h[0]
            rows.append({'name': name, 'a': f'{A[0]}.{A[1]}', 'b': f'{Bn[0]}.{Bn[1]}', 'plan': plan,
                         'est': L, 'need': int(math.ceil(L / 10.0) * 10), 'ok': L <= plan, 'w': wgt})
        return rows

    def taps_target(self):
        """Położenie J7 (TAPS) na P11 dokładnie przed J4 P05 — do przeniesienia w następnej rewizji P11."""
        q = part('P05', 'J4')['box']
        X, Z = self.board_point('P05', (q[0] + q[2]) / 2, (q[1] + q[3]) / 2)
        return X, Z

    def harness_taps_relocated(self):
        X, Z = self.taps_target()
        a = [e for e in self.endpoint('P05', 'J4', 'pth') if e[3] == 'front'][0]
        b = (X, self.p11_Ys + EXIT['mf'], Z, 'front', EXIT['mf'], None)
        return (a[4] + b[4] + self.route(a, b) + SLACK, a, b)

    def cost(self):
        c = 0.0
        for r in self.check():
            c += r['w'] * max(0.0, r['est'] - r['plan']) + 0.01 * r['est']
        return c


def options_for(b, variant):
    """Możliwe położenia płytki w jej płaszczyźnie: (obrót, x0 w kolumnie, górna krawędź Z)."""
    W, H = B[b]['W'], B[b]['H']
    if b in ('P03', 'P05'):
        return [(0, 0.0, COL_H)]
    if b in PCB_SLOT:
        return [(0, 0.0, COL_H), (180, 0.0, COL_H)]
    if b == 'P11':
        return [(0, 0.0, 118.0), (180, 0.0, 118.0)]
    out = []
    for r in (0, 90, 180, 270):
        _, _, w, h = rot_xy(0, 0, W, H, r)
        if w > COL_W - 2 or h > COL_H:
            continue
        for x0 in sorted({2.0, round((COL_W - w) / 2, 1), COL_W - 2 - w}):
            for zt in sorted({COL_H, round(COL_H / 2 + h / 2, 1), h}):
                out.append((r, x0, zt))
    return out


def pair_options(variant):
    """P08 i P10 na jednej płycie nośnej: obie obrócone o 90/270, obok siebie."""
    out = []
    for r8, r10 in itertools.product((90, 270), (90, 270)):
        for z8, z10 in itertools.product((COL_H, 100.0), (COL_H, 80.0)):
            out.append({'P08': (r8, 2.0, z8), 'P10': (r10, 87.0, z10)})
    return out


def optimise(variant, passes=4):
    cfg = VARIANTS[variant]
    boards = [b for seq in cfg['cols'].values() for item in seq for b in item.split('+')] + ['P11']
    paired = any('P08+P10' in s for s in cfg['cols'].values())
    opts = {b: options_for(b, variant)[0] for b in boards if not (paired and b in ('P08', 'P10'))}
    if paired:
        opts.update(pair_options(variant)[0])
    best = Layout(variant, opts).cost()
    for _ in range(passes):
        changed = False
        for b in boards:
            if paired and b in ('P08', 'P10'):
                continue
            for o in options_for(b, variant):
                trial = dict(opts); trial[b] = o
                c = Layout(variant, trial).cost()
                if c < best - 1e-9:
                    best, opts, changed = c, trial, True
        if paired:
            for po in pair_options(variant):
                trial = dict(opts); trial.update(po)
                c = Layout(variant, trial).cost()
                if c < best - 1e-9:
                    best, opts, changed = c, trial, True
        if not changed:
            break
    return Layout(variant, opts)


if __name__ == '__main__':
    for v in VARIANTS:
        L = optimise(v)
        print(v, 'wnętrze', [round(d) for d in L.inner], 'zewn.', [round(d) for d in L.outer],
              'objętość wewn. %.1f l' % (L.inner[0] * L.inner[1] * L.inner[2] / 1e6), 'stos', {k: round(x, 1) for k, x in L.depth_cols.items()})
        for (col, k), p in sorted(L.planes.items()):
            print('  ', col, k, p['boards'], 'Y=%.1f env=%.0f' % (p['Ys'], p['env']), 'nośnik' if p['carrier'] else '')
        print('   położenia:', {b: (p['r'], round(p['x0'] - COL_X[p['col']], 1), p['ztop']) for b, p in L.place.items()})
        for r in L.check():
            print('   %-11s %-9s %-10s plan %3d  szac. %5.0f  %s' % (r['name'], r['a'], r['b'], r['plan'], r['est'], 'OK' if r['ok'] else f"→ {r['need']}"))
        t = L.harness('TAPS', ('P05', 'J4', 'pth'), ('P11', 'J7', 'mf'))
        print('   TAPS z J7 w obecnym miejscu P11: %.0f mm' % t[0])
