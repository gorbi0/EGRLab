"""Rysunek koncepcji kasety R1: PDF A3 (widoki 1:2, tabele, obrys 1:1) oraz dane układu i wiązek.
Uruchomienie: Python z reportlab (runtime Codexa) z katalogu Plytki/Kaseta-R1:  python src/rysunek.py
"""
import csv, json, os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import model as M
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A3, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# EGRLAB_FONT_DIR (Linux/chmura): katalog czcionek Liberation, metrycznie zgodnych z Arial/Arial Narrow.
# Bez zmiennej jak dotąd: czcionki Windows, więc wynik na Windows się nie zmienia (docs/CHMURA.md).
FONT_DIR = os.environ.get('EGRLAB_FONT_DIR')
LIBERATION = {'arial.ttf': 'LiberationSans-Regular.ttf', 'arialbd.ttf': 'LiberationSans-Bold.ttf',
              'ARIALN.TTF': 'LiberationSansNarrow-Regular.ttf', 'ARIALNB.TTF': 'LiberationSansNarrow-Bold.ttf'}
for n, f in (('A', 'arial.ttf'), ('AB', 'arialbd.ttf'), ('AN', 'ARIALN.TTF'), ('ANB', 'ARIALNB.TTF')):
    pdfmetrics.registerFont(TTFont(n, os.path.join(FONT_DIR, LIBERATION[f]) if FONT_DIR else f'C:/Windows/Fonts/{f}'))
R = M.R
PW, PH = landscape(A3)
DATE = '29.09.2026'
C_PCB, C_ENV, C_CAR = (0.10, 0.45, 0.20), (0.84, 0.93, 0.85), (0.62, 0.62, 0.66)
C_HS, C_CAP, C_P11, C_P11E = (0.30, 0.30, 0.36), (0.22, 0.30, 0.60), (0.60, 0.28, 0.10), (0.97, 0.88, 0.80)
C_PANEL, C_WALL, C_ROD, C_RED, C_GREY = (0.93, 0.83, 0.58), (0.72, 0.72, 0.72), (0.45, 0.45, 0.45), (0.80, 0.08, 0.08), (0.4, 0.4, 0.4)
NAMES = {'P01': 'P01 PROTECT', 'P02': 'P02 PSU+HOLD', 'P03': 'P03 CORE', 'P04': 'P04 SAFE', 'P05': 'P05 DAQ',
         'P06': 'P06 I-LOGGER', 'P07': 'P07 DRIVE (rezerwa)', 'P08': 'P08 SENSOR', 'P09': 'P09 TEMP', 'P10': 'P10 CAN',
         'P11': 'P11 PANEL'}


class View:
    """Rzut: (h, v) w mm rzeczywistych -> strona; s = skala (mm papieru na mm rzeczywisty)."""
    def __init__(self, c, ox, oy, s):
        self.c, self.ox, self.oy, self.s = c, ox, oy, s

    def P(self, h, v):
        return (self.ox + h * self.s) * mm, (self.oy + v * self.s) * mm

    def rect(self, h0, v0, h1, v1, fill=None, stroke=(0, 0, 0), lw=0.25, dash=None):
        c = self.c
        (x0, y0), (x1, y1) = self.P(min(h0, h1), min(v0, v1)), self.P(max(h0, h1), max(v0, v1))
        c.saveState()
        c.setLineWidth(lw)
        if dash:
            c.setDash(*dash)
        if fill:
            c.setFillColorRGB(*fill)
        if stroke:
            c.setStrokeColorRGB(*stroke)
        c.rect(x0, y0, x1 - x0, y1 - y0, stroke=1 if stroke else 0, fill=1 if fill else 0)
        c.restoreState()

    def line(self, h0, v0, h1, v1, color=(0, 0, 0), lw=0.25, dash=None):
        c = self.c
        c.saveState()
        c.setLineWidth(lw); c.setStrokeColorRGB(*color)
        if dash:
            c.setDash(*dash)
        c.line(*self.P(h0, v0), *self.P(h1, v1))
        c.restoreState()

    def circle(self, h, v, d, fill=None, stroke=(0, 0, 0), lw=0.25):
        c = self.c
        c.saveState(); c.setLineWidth(lw)
        if fill:
            c.setFillColorRGB(*fill)
        c.setStrokeColorRGB(*stroke)
        x, y = self.P(h, v)
        c.circle(x, y, d / 2 * self.s * mm, stroke=1, fill=1 if fill else 0)
        c.restoreState()

    def text(self, h, v, s, size=6.5, font='AN', color=(0, 0, 0), anchor='c', angle=0):
        c = self.c
        x, y = self.P(h, v)
        c.saveState(); c.setFillColorRGB(*color); c.setFont(font, size)
        c.translate(x, y); c.rotate(angle)
        f = {'c': c.drawCentredString, 'l': c.drawString, 'r': c.drawRightString}[anchor]
        f(0, -size * 0.35, s)
        c.restoreState()

    def dim(self, h0, v0, h1, v1, label, off, size=7):
        """Linia wymiarowa między punktami, przesunięta o off (mm rzeczywiste) prostopadle."""
        horiz = abs(v1 - v0) < 1e-6
        if horiz:
            vv = v0 + off
            self.line(h0, v0, h0, vv, C_GREY, 0.2); self.line(h1, v1, h1, vv, C_GREY, 0.2)
            self.line(h0, vv, h1, vv, (0, 0, 0), 0.3)
            for hh, d in ((h0, 1), (h1, -1)):
                self.line(hh, vv, hh + d * 4 / self.s * 0.5, vv + 1.2 / self.s * 0.5, (0, 0, 0), 0.3)
                self.line(hh, vv, hh + d * 4 / self.s * 0.5, vv - 1.2 / self.s * 0.5, (0, 0, 0), 0.3)
            self.text((h0 + h1) / 2, vv + 2.2 / self.s, label, size, 'A')
        else:
            hh = h0 + off
            self.line(h0, v0, hh, v0, C_GREY, 0.2); self.line(h1, v1, hh, v1, C_GREY, 0.2)
            self.line(hh, v0, hh, v1, (0, 0, 0), 0.3)
            for vv, d in ((v0, 1), (v1, -1)):
                self.line(hh, vv, hh + 1.2 / self.s * 0.5, vv + d * 4 / self.s * 0.5, (0, 0, 0), 0.3)
                self.line(hh, vv, hh - 1.2 / self.s * 0.5, vv + d * 4 / self.s * 0.5, (0, 0, 0), 0.3)
            self.text(hh - 2.4 / self.s, (v0 + v1) / 2, label, size, 'A', angle=90)


def part_range(L, b, ref):
    """Zakres X i Z (widok od tyłu) obrysu elementu po obrocie płytki."""
    q = M.part(b, ref)['box']
    pts = [L.board_point(b, x, y) for x in (q[0], q[2]) for y in (q[1], q[3])]
    xs, zs = [p[0] for p in pts], [p[1] for p in pts]
    return min(xs), max(xs), min(zs), max(zs)


def tall_parts(L):
    """Najwyższe elementy do pokazania w rzutach: (płytka, zakres X, zakres Z, wysokość, kolor)."""
    out = []
    if 'P01' in L.place:
        h = 25.4 if L.cfg['low_hs'] else 63.5
        for ref in ('HS1', 'HS2'):
            x0, x1, z0, z1 = part_range(L, 'P01', ref)
            out.append(('P01', x0, x1, z0, z1, h, C_HS))
    if 'P02' in L.place:
        for ref in ('C1', 'C2', 'C3'):
            x0, x1, z0, z1 = part_range(L, 'P02', ref)
            out.append(('P02', x0, x1, z0, z1, 48.0, C_CAP))
    return out


def draw_top(c, L, ox, oy, s, labels=True, edge_labels=True):
    V = View(c, ox, oy, s)
    W, D, H = L.inner
    X1, Yw = L.X1, L.Yw
    hx = lambda X: X1 - X
    vy = lambda Y: Y - Yw
    V.rect(-M.WALL, -M.WALL, W + M.WALL, D + M.WALL, fill=C_WALL, stroke=(0, 0, 0), lw=0.4)
    V.rect(0, 0, W, D, fill=(1, 1, 1), stroke=(0, 0, 0), lw=0.3)
    # panel: części przed kolumną P03, P11 przed kolumną P05
    V.rect(hx(M.COL_X['L'] + 160), 0, hx(L.X0), M.PANEL_DEPTH, fill=(0.98, 0.95, 0.88), stroke=C_GREY, lw=0.15)
    for key in ('DT_L1', 'DT_L2', 'DT_TEST'):
        X, Z, w, h, d, lab = M.PANEL[key]
        V.rect(hx(X + w / 2), 0, hx(X - w / 2), d, fill=C_PANEL, lw=0.2)
        if labels:
            V.text(hx(X), d / 2, lab, 5.8 if s < 0.9 else 8, 'AN')
    V.rect(hx(M.COL_X['R'] + 160), vy(L.p11_Ys - M.T), hx(M.COL_X['R']), vy(L.p11_Ys), fill=C_P11, lw=0.2)
    V.rect(hx(M.COL_X['R'] + 160), vy(L.p11_Ys), hx(M.COL_X['R']), vy(L.p11_Ys + M.ENV['P11']), fill=C_P11E, lw=0.15)
    # płaszczyzny
    for (col, k), p in sorted(L.planes.items()):
        cx0 = M.COL_X[col]
        if p['carrier']:
            yplate = p['Ys'] - M.T - 6.0
            V.rect(hx(cx0 + 160), vy(yplate - 2.0), hx(cx0), vy(yplate), fill=C_CAR, lw=0.15)
        for b in p['boards']:
            q = L.place[b]
            V.rect(hx(q['x0'] + q['w']), vy(p['Ys']), hx(q['x0']), vy(p['Ys'] + L.env[b]), fill=C_ENV, lw=0.15)
            V.rect(hx(q['x0'] + q['w']), vy(p['Ys'] - M.T), hx(q['x0']), vy(p['Ys']), fill=C_PCB, stroke=None)
    for b, x0, x1, z0, z1, h, col in tall_parts(L):
        Ys = L.place[b]['Ys']
        V.rect(hx(x1), vy(Ys), hx(x0), vy(Ys + h), fill=col, stroke=None)
    # pręty M3
    for col in ('L', 'R'):
        ks = [k for (cc, k) in L.planes if cc == col]
        y0 = L.planes[(col, 0)]['Ys'] - M.T - M.SOLDER
        y1 = L.planes[(col, max(ks))]['Ys']
        for xr in (5.0, 155.0):
            V.line(hx(M.COL_X[col] + xr), vy(y0), hx(M.COL_X[col] + xr), vy(y1), C_ROD, 0.35, (2, 1.5))
    # BNC AUX na ścianie bocznej i przepusty na ścianie tylnej
    V.rect(hx(M.COL_X['R'] + 160 + 20), vy(4), hx(M.COL_X['R'] + 160), vy(20), fill=C_PANEL, lw=0.2)
    for key, (X, Z, lab) in M.BACKWALL.items():
        V.rect(hx(X + 8), D - 8, hx(X - 8), D, fill=C_PANEL, lw=0.2)
        if labels:
            V.text(hx(X), D - 12, lab, 5 if s < 0.9 else 7.5, 'AN', C_GREY)
    if labels:
        for (col, k), p in sorted(L.planes.items()):
            for b in p['boards']:
                q = L.place[b]
                V.text(hx(q['x0'] + q['w'] / 2), vy(p['Ys'] + L.env[b] / 2), NAMES[b], 6.2 if s < 0.9 else 9, 'ANB')
        V.text(hx(M.COL_X['R'] + 80), vy(L.p11_Ys + 15), 'P11 PANEL (PCB za ścianą)', 6 if s < 0.9 else 8.5, 'ANB', C_P11)
        V.text(hx(80), M.PANEL_DEPTH - 5, 'strefa części panelu (45 mm): DT, przełączniki, BNC', 5.6 if s < 0.9 else 8, 'AN')
        V.text(10, vy(12), 'BNC AUX', 5.5 if s < 0.9 else 8, 'AN', angle=90)
        if edge_labels:
            V.text(W / 2, -M.WALL - 5 / s * 0.5 - 3, 'PRZÓD — ściana panelu (DEUTSCH, przełączniki, BNC)', 7 if s < 0.9 else 10, 'AB')
            V.text(W / 2, D + M.WALL + 4, 'TYŁ — przepusty BAT i OBD', 7 if s < 0.9 else 10, 'AB')
    return V


def draw_front(c, L, ox, oy, s):
    V = View(c, ox, oy, s)
    W, D, H = L.inner
    hx = lambda X: L.X1 - X
    vz = lambda Z: Z - L.Z0
    V.rect(-M.WALL, -M.WALL, W + M.WALL, H + M.WALL, fill=C_WALL, lw=0.4)
    V.rect(0, 0, W, H, fill=(1, 1, 1), lw=0.3)
    for col in ('L', 'R'):
        V.rect(hx(M.COL_X[col] + 160), vz(0), hx(M.COL_X[col]), vz(120), stroke=C_PCB, lw=0.3, dash=(2, 1.5))
    V.text(hx(130), vz(3), 'P03 (za panelem)', 5.8, 'AN', C_PCB)
    V.text(hx(M.COL_X['R'] + 80), vz(3), 'P05 (za P11)', 5.8, 'AN', C_PCB)
    q = L.place['P11']
    V.rect(hx(q['x0'] + 160), vz(q['ztop'] - 110), hx(q['x0']), vz(q['ztop']), stroke=C_P11, lw=0.45, dash=(3, 1.5))
    V.text(hx(q['x0'] + 80), vz(q['ztop'] - 55), 'P11 PANEL — PCB 160 × 110', 6.5, 'ANB', C_P11)
    V.text(hx(q['x0'] + 80), vz(q['ztop'] - 63), 'na dystansach 10 mm za ścianą', 5.8, 'AN', C_P11)
    X, Z = L.taps_target()
    V.circle(hx(X), vz(Z), 6, fill=C_RED, stroke=C_RED)
    V.text(hx(X), vz(Z) - 7, 'J7 TAPS przenieść tutaj', 5.6, 'ANB', C_RED)
    for key, (X, Z, w, h, d, lab) in M.PANEL.items():
        if w <= 0:
            continue
        if key.startswith('DT'):
            V.rect(hx(X + w / 2), vz(Z - h / 2), hx(X - w / 2), vz(Z + h / 2), fill=C_PANEL, lw=0.25)
        else:
            V.circle(hx(X), vz(Z), w, fill=C_PANEL)
        V.text(hx(X), vz(Z - h / 2) - 3.5, lab, 5.5, 'AN')
    V.circle(8, vz(M.AUX_Z), 10, fill=C_PANEL)
    V.text(8, vz(M.AUX_Z) + 8, 'AUX', 5.2, 'AN')
    V.text(W / 2, H + M.WALL + 4, 'Widok od przodu (panel) — rozmieszczenie części panelu szkicowe', 7, 'AB')
    V.dim(0, 0, W, 0, f'{W:.0f} (wewn.)', -9)
    V.dim(W, 0, W, H, f'{H:.0f} (wewn.)', 16)
    return V


def draw_side(c, L, ox, oy, s):
    V = View(c, ox, oy, s)
    W, D, H = L.inner
    hy = lambda Y: Y - L.Yw
    vz = lambda Z: Z - L.Z0
    V.rect(-M.WALL, -M.WALL, D + M.WALL, H + M.WALL, fill=C_WALL, lw=0.4)
    V.rect(0, 0, D, H, fill=(1, 1, 1), lw=0.3)
    V.rect(0, vz(-10), M.PANEL_DEPTH, vz(135), fill=(0.98, 0.95, 0.88), stroke=None)
    V.text(M.PANEL_DEPTH / 2, vz(-5), 'panel', 5.5, 'AN')
    q = L.place['P11']
    V.rect(hy(q['Ys'] - M.T), vz(q['ztop'] - 110), hy(q['Ys']), vz(q['ztop']), stroke=C_P11, lw=0.4, dash=(2, 1.2))
    V.text(hy(q['Ys']) + 5, vz(q['ztop'] - 55), 'P11', 5.8, 'AN', C_P11, angle=90)
    for near in (False, True):             # najpierw dalsza kolumna (P05) przerywaną, potem bliższa (P03)
        col = 'L' if near else 'R'
        for (cc, k), p in sorted(L.planes.items()):
            if cc != col:
                continue
            if p['carrier']:
                yplate = p['Ys'] - M.T - 6.0
                V.rect(hy(yplate - 2), vz(0), hy(yplate), vz(120), fill=C_CAR if near else None,
                       stroke=(0, 0, 0) if near else C_GREY, lw=0.15, dash=None if near else (1.5, 1))
            for b in p['boards']:
                pb = L.place[b]
                z0, z1 = pb['ztop'] - pb['h'], pb['ztop']
                if near:
                    V.rect(hy(p['Ys']), vz(z0), hy(p['Ys'] + L.env[b]), vz(z1), fill=C_ENV, lw=0.12)
                    V.rect(hy(p['Ys'] - M.T), vz(z0), hy(p['Ys']), vz(z1), fill=C_PCB, stroke=None)
                    if b == p['boards'][-1]:
                        V.text(hy(p['Ys'] + L.env[b] / 2), vz(60), '+'.join(p['boards']), 6.2, 'ANB', angle=90)
                else:
                    V.rect(hy(p['Ys'] - M.T), vz(z0), hy(p['Ys'] + L.env[b]), vz(z1), stroke=C_GREY, lw=0.25, dash=(1.5, 1))
                    V.text(hy(p['Ys'] + L.env[b] / 2), vz(z1) + 3, b, 5.5, 'AN', C_GREY)
    V.text(D / 2, vz(128), f'kanał wiązek {M.M_TOP:.0f} mm', 5.5, 'AN', C_GREY)
    V.text(D / 2, vz(-5), f'kanał wiązek {M.M_BOTTOM:.0f} mm', 5.5, 'AN', C_GREY)
    V.text(D / 2, H + M.WALL + 4, 'Widok z boku od strony P03 (P05 przerywaną)', 7, 'AB')
    V.text(3, H + M.WALL + 4, 'PRZÓD', 6, 'A', anchor='l')
    V.text(D - 3, H + M.WALL + 4, 'TYŁ', 6, 'A', anchor='r')
    V.dim(0, 0, D, 0, f'{D:.0f} (wewn.)', -9)
    return V


def table(c, x, y, cols, rows, size=6.3, lh=3.15, head_font='ANB', colors=None):
    """Prosta tabela: cols = [(nagłówek, szerokość mm, wyrównanie)]; y = górna krawędź [mm]."""
    c.setFont(head_font, size)
    xx = x
    for h, w, a in cols:
        c.drawString(xx * mm, (y - lh) * mm, h)
        xx += w
    c.setLineWidth(0.3); c.line(x * mm, (y - lh - 0.8) * mm, xx * mm, (y - lh - 0.8) * mm)
    for i, row in enumerate(rows):
        yy = y - lh * (i + 2)
        xx = x
        col = colors[i] if colors else (0, 0, 0)
        c.setFillColorRGB(*col)
        for (h, w, a), val in zip(cols, row):
            c.setFont('AN', size)
            if a == 'r':
                c.drawRightString((xx + w - 2) * mm, yy * mm, str(val))
            else:
                c.drawString(xx * mm, yy * mm, str(val))
            xx += w
        c.setFillColorRGB(0, 0, 0)
    return y - lh * (len(rows) + 1) - 2


def text_block(c, x, y, lines, size=7, lh=3.4, font='A', width=None):
    for ln in lines:
        f, s_ = (font, ln)
        if isinstance(ln, tuple):
            f, s_ = ln
        c.setFont(f, size)
        c.drawString(x * mm, y * mm, s_)
        y -= lh
    return y


def title(c, s1, s2):
    c.setFont('AB', 13); c.drawString(15 * mm, 287 * mm, s1)
    c.setFont('A', 8.5); c.drawString(15 * mm, 282 * mm, s2)
    c.setFont('A', 7.5)
    c.drawRightString(405 * mm, 287 * mm, f'EGRLab — Plytki/Kaseta-R1 — {DATE}')
    c.drawRightString(405 * mm, 282 * mm, 'KONCEPCJA do przymiarki — nie rysunek wykonawczy')
    c.setLineWidth(0.5); c.rect(10 * mm, 10 * mm, 400 * mm, 267 * mm)


def scale_bar(c, x, y, s, length=100):
    c.setLineWidth(0.4)
    for i in range(int(length / 10) + 1):
        xx = (x + i * 10 * s) * mm
        c.line(xx, y * mm, xx, (y + (2.5 if i % 5 == 0 else 1.5)) * mm)
    c.line(x * mm, y * mm, (x + length * s) * mm, y * mm)
    c.setFont('A', 7)
    c.drawString(x * mm, (y + 3.5) * mm, f'belka {length} mm w skali — zmierz po wydruku')


def summary_lines(L):
    W, D, H = L.inner
    Wo, Do, Ho = L.outer
    vol_i, vol_o = W * D * H / 1e6, Wo * Do * Ho / 1e6
    return [('AB', f'Wymiary wewnętrzne: {W:.0f} × {D:.0f} × {H:.0f} mm (szer. × gł. × wys.) — {vol_i:.1f} l'),
            ('AB', f'Z dwiema ściankami {M.WALL:.0f} mm: {Wo:.0f} × {Do:.0f} × {Ho:.0f} mm — {vol_o:.1f} l'),
            ('A', f'Makieta z kartonu: {Wo:.0f} × {Do:.0f} × {Ho:.0f} mm; z przodu dolicz ok. 70 mm na wtyki DEUTSCH z przewodami,'),
            ('A', 'z tyłu ok. 40 mm na przewód BAT i OBD; z boku P05 ok. 30 mm na wtyk BNC AUX.')]


def planes_rows(L):
    rows = []
    for (col, k), p in sorted(L.planes.items(), key=lambda t: (t[0][0], t[0][1])):
        kol = 'P03' if col == 'L' else 'P05'
        for b in p['boards']:
            q = L.place[b]
            rows.append([f'{kol} / {k + 1}', NAMES[b], f"{B_W(b)}", f"{p['Ys']:.0f}", f'{L.env[b]:.0f}',
                         'płyta nośna' if p['carrier'] else 'na prętach', f"{q['r']}°"])
    return rows


def B_W(b):
    return f"{M.B[b]['W']:.0f} × {M.B[b]['H']:.0f}"


def variant_page(c, L, notes):
    cfg = L.cfg
    title(c, f'Kaseta R1 — wariant {cfg["title"]}', 'Płytki pionowo na prętach M3 (otwory 150 × 110 mm), strona elementów do tyłu; '
          'P03|P05 w pierwszej płaszczyźnie (B2B); widoki w skali 1:2 (A3)')
    s = 0.5
    W, D, H = L.inner
    draw_front(c, L, 25, 272 - H * s - 8, s)
    draw_top(c, L, 25, 22, s)
    V = View(c, 25, 22, s)
    V.dim(0, 0, 0, D, f'{D:.0f} (wewn.)', -10)
    V.dim(0, D, W, D, f'{W:.0f} (wewn.)', 12)
    c.setFont('AB', 7); c.drawString(25 * mm, (22 + D * s + 14) * mm, 'Widok z góry (pokrywa zdjęta)')
    sx = 25 + W * s + 22
    draw_side(c, L, sx, 272 - H * s - 8, s)
    y = 272 - H * s - 20
    y = text_block(c, sx, y, summary_lines(L), 7.2, 3.6)
    y -= 2
    c.setFont('AB', 7.5); c.drawString(sx * mm, y * mm, 'Płaszczyzny (od przodu; Y = odległość od powierzchni elementów P03|P05)')
    y = table(c, sx, y - 1, [('kolumna / nr', 22, 'l'), ('płytka', 34, 'l'), ('PCB [mm]', 20, 'l'), ('Y [mm]', 14, 'r'),
                             ('wys. zajęta', 18, 'r'), ('mocowanie', 22, 'l'), ('obrót', 12, 'r')], planes_rows(L))
    y -= 2
    text_block(c, sx, y, notes, 6.8, 3.3)


def harness_page(c, layouts):
    title(c, 'Kaseta R1 — wiązki: długość z projektu v6.1 a szacunek w kasecie',
          'Szacunek = wyjścia złączy + trasa wokół krawędzi płytek przez kanały + 10 mm łuku; dokładność ok. ±20 mm — rozstrzyga makieta')
    x = 15
    for L in layouts:
        rows, colors = [], []
        for r in L.check():
            st = 'OK' if r['ok'] else f"wydłużyć do {r['need']}"
            if r['name'] == 'TAPS':
                st += ' (J7 przeniesiony)'
            rows.append([r['name'], f"{r['a']} – {r['b']}".replace('WALL.', 'ściana ').replace('BACKWALL.', 'tył '),
                         r['plan'], f"{r['est']:.0f}", st])
            colors.append((0, 0.35, 0) if r['ok'] else ((0.8, 0.08, 0.08) if r['w'] >= 3 else (0, 0, 0)))
        c.setFont('AB', 9); c.drawString(x * mm, 272 * mm, f'Wariant {L.v}')
        yb = table(c, x, 270, [('wiązka', 20, 'l'), ('od – do', 58, 'l'), ('projekt', 14, 'r'), ('kaseta', 14, 'r'),
                                ('uwaga', 86, 'l')], rows, 6.6, 3.35, colors=colors)
        t = L.harness('TAPS', ('P05', 'J4', 'pth'), ('P11', 'J7', 'mf'))[0]
        text_block(c, x, yb - 1, [f'TAPS z J7 w obecnym miejscu P11-R1: ok. {t:.0f} mm (limit 50 mm) — stąd propozycja przeniesienia J7.'], 6.8)
        x += 200
    notes = [
        ('AB', 'Jak czytać'),
        'Długości z projektu (interfejsy.csv v6.1, WIAZKI P11) liczono pod płaski nośnik z płytkami obok siebie. W kasecie przewody obchodzą krawędzie',
        'kolejnych płytek, więc większość wiązek wychodzi dłuższa. Wiązek jeszcze nie wykonano — ich długości to pozycje BOM, nie zmiana PCB.',
        ('AB', 'Czerwone = elektrycznie wrażliwe, wymagają decyzji przed wydłużeniem'),
        'TAPS (tor analogowy, maks. 50 mm): mieści się tylko po przeniesieniu J7 na P11 dokładnie przed J4 P05 (P11-R1 nie jest zamknięta).',
        'Ogonki DT W5–W7 niosą ten sam tor analogowy: w kasecie ok. 200–340 mm zamiast 150 mm.',
        'SAFE (reset P03→P04, zbocze liczone dla taśmy 150 mm: 5,5 ns/V wobec 10 ns/V): ok. 180 mm — przeliczyć przed wykonaniem.',
        'ILOG, TEMP, ITEST (SPI, 100 mm): 110–320 mm — sprawdzić przebiegi SPI na dłuższej taśmie albo zmienić kolejność płaszczyzn.',
    ]
    text_block(c, 15, 60, notes, 7.2, 3.6)


def footprint_page(c, L):
    """Widok z góry 1:1 bez ramki — obudowa wariantu pełnego ma 265 mm głębokości przy 297 mm wysokości A3."""
    W, D, H = L.inner
    Wo, Do, Ho = L.outer
    c.setFont('AB', 10.5)
    c.drawString(12 * mm, 290 * mm, f'Kaseta R1 — wariant {L.v}: widok z góry 1:1 — wnętrze {W:.0f} × {D:.0f} mm, '
                                    f'z ściankami {Wo:.0f} × {Do:.0f} mm; wysokość {H:.0f} / {Ho:.0f} mm')
    c.setFont('A', 7.2)
    c.drawString(12 * mm, 285.8 * mm, 'Drukuj na A3 w skali 100 % (bez dopasowania do strony); przy A4 w Adobe Reader „Plakat”, skala 100 %. '
                                      'Zielony — PCB, jasnozielony — przestrzeń elementów, szary — płyty nośne, ciemne — radiatory P01 i puszki P02,')
    c.drawString(12 * mm, 282.6 * mm, f'brązowy — P11, piaskowy — części panelu i przepusty. KONCEPCJA do przymiarki — Plytki/Kaseta-R1, {DATE}.')
    ox = (420 - W) / 2
    oy = 14 + (266 - (D + 2 * M.WALL)) / 2 + M.WALL
    V = draw_top(c, L, ox, oy, 1.0, labels=True, edge_labels=False)
    for v, lab in ((0, 'PRZÓD (panel)'), (D, 'TYŁ')):
        V.text(-M.WALL - 7, v + (18 if v == 0 else -10), lab, 9, 'AB', angle=90)
    # pionowa belka 100 mm na prawym marginesie
    x = 412
    c.setLineWidth(0.5)
    c.line(x * mm, 30 * mm, x * mm, 130 * mm)
    for i in range(11):
        c.line(x * mm, (30 + i * 10) * mm, (x - (3 if i % 5 == 0 else 1.8)) * mm, (30 + i * 10) * mm)
    c.saveState(); c.translate((x + 3.5) * mm, 80 * mm); c.rotate(90)
    c.setFont('A', 7); c.drawCentredString(0, 0, 'belka 100 mm — zmierz po wydruku'); c.restoreState()


def main():
    layouts = [M.optimise(v) for v in M.VARIANTS]
    notes = {
        'LOGGER': [('AB', 'Założenia i sprawy otwarte'),
                   '• Bez P04, P07, P08 (tylko tryb TEST). Do potwierdzenia: firmware CORE pracuje bez podłączonej P04 (H_SAFE).',
                   '• P01 z radiatorami SK129 25,4 STS (ten sam footprint i otwór TO-220 co 63,5); przy prądzie rejestratora < 1 A.',
                   '• Małe płytki na płytach nośnych 160 × 120 (2 mm) na dystansach 6 mm; pręty M3 z tulejami o długości podziałki.',
                   '• J7 (TAPS) na P11 do przeniesienia przed J4 P05 — inaczej wiązka TAPS ok. 190 mm zamiast 50 mm.',
                   '• Dostęp do karty SD i USB modułu CORE — do rozstrzygnięcia (P03 stoi zaraz za panelem, elementami do tyłu).',
                   '• Temperatura projektu płytek 0–50 °C: obudowa w kabinie, nie w komorze silnika.'],
        'PELNY': [('AB', 'Założenia i sprawy otwarte'),
                  '• P01 z SK129 63,5 STS (5 A dla P07); P07 bez PCB — rezerwa 120 × 100 mm, wys. 35 mm.',
                  '• P08 i P10 obok siebie na jednej płycie nośnej (obie obrócone o 90°).',
                  '• SAFE P03→P04 ok. 180 mm zamiast 150 mm — przeliczyć zbocze resetu (P03-R4: 5,5 ns/V przy 150 mm).',
                  '• Pracy P01 i P07 przy 5 A w zamkniętej kasecie nie oceniono cieplnie — potrzebna wentylacja przy radiatorach.',
                  '• Pozostałe jak w wariancie LOGGER (J7 TAPS, SD/USB, kabina).'],
    }
    pdf = R/'KASETA-R1.pdf'
    c = canvas.Canvas(str(pdf), pagesize=(PW, PH))
    c.setTitle('EGRLab — kaseta R1, koncepcja rozmieszczenia płytek'); c.setAuthor('Claude (EGRLab)')
    for L in layouts:
        variant_page(c, L, notes[L.v]); c.showPage()
    harness_page(c, layouts); c.showPage()
    for L in layouts:
        footprint_page(c, L); c.showPage()
    c.save()
    for L in layouts:
        data = {'wariant': L.v, 'opis': L.cfg['title'], 'wewnatrz_mm': [round(x, 1) for x in L.inner],
                'zewnatrz_mm': [round(x, 1) for x in L.outer], 'objetosc_wewn_l': round(L.inner[0] * L.inner[1] * L.inner[2] / 1e6, 2),
                'plaszczyzny': [{'kolumna': 'P03' if col == 'L' else 'P05', 'nr': k + 1, 'plytki': p['boards'], 'Y_mm': round(p['Ys'], 1),
                                 'wys_zajeta_mm': p['env'], 'plyta_nosna': p['carrier']} for (col, k), p in sorted(L.planes.items())],
                'polozenia': {b: {'obrot': q['r'], 'x0_w_kolumnie': round(q['x0'] - M.COL_X[q['col']], 1), 'gorna_krawedz_Z': q['ztop']}
                              for b, q in L.place.items()},
                'zrodla_plytek': {b: {'plik': M.B[b].get('source'), 'sha256': M.B[b].get('sha256')} for b in L.place}}
        (R/'dane'/f'uklad-{L.v}.json').write_text(json.dumps(data, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
        with open(R/'dane'/f'wiazki-{L.v}.csv', 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f, delimiter=';')
            w.writerow(['wiazka', 'od', 'do', 'dlugosc_projekt_mm', 'szacunek_kaseta_mm', 'wymagana_mm', 'miesci_sie'])
            for r in L.check():
                w.writerow([r['name'], r['a'], r['b'], r['plan'], round(r['est']), r['need'], 'tak' if r['ok'] else 'nie'])
        print(L.v, [round(x) for x in L.inner], [round(x) for x in L.outer])
    print('zapisano', pdf)


if __name__ == '__main__':
    main()
