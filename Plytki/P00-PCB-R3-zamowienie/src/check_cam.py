"""Niezależny odczyt plików produkcyjnych (Gerber X2 + Excellon) i porównanie z modelem PCB.
Własny parser (tylko biblioteka standardowa Pythona + Pillow do podglądów); nie korzysta z KiCada.
Nie zmienia plików produkcyjnych. Uruchomienie: python src/check_cam.py
Wejście: gerber/, verification/board-fabrication-data.json, verification/export-receipt.json, src/config.json.
Wyjście: verification/cam-checks.json, podglad/CAM-*.png.
"""
from pathlib import Path
from collections import Counter
import hashlib, json, math, re

R = Path(__file__).resolve().parents[1]
CFG = json.loads((R/'src'/'config.json').read_text(encoding='utf-8'))
NAME, (W, H) = CFG['name'], CFG['board_mm']
G, V, PV = R/'gerber', R/'verification', R/'podglad'
D = json.loads((V/'board-fabrication-data.json').read_text(encoding='utf-8'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
checks = []


def check(name, ok, details=None):
    checks.append({'name': name, 'pass': bool(ok), 'details': details})
    if not ok:
        print('FAIL', name, json.dumps(details, ensure_ascii=False)[:600])


def arc_points(x1, y1, x2, y2, cx, cy, cw, n=24):
    a1, a2 = math.atan2(y1 - cy, x1 - cx), math.atan2(y2 - cy, x2 - cx)
    r = math.hypot(x1 - cx, y1 - cy)
    if cw:
        while a2 >= a1: a2 -= 2 * math.pi
    else:
        while a2 <= a1: a2 += 2 * math.pi
    if abs(x1 - x2) < 1e-9 and abs(y1 - y2) < 1e-9:
        a2 = a1 - 2 * math.pi if cw else a1 + 2 * math.pi
    k = max(2, int(abs(a2 - a1) / (2 * math.pi) * n * 4))
    return [(cx + r * math.cos(a1 + (a2 - a1) * i / k), cy + r * math.sin(a1 + (a2 - a1) * i / k)) for i in range(1, k + 1)]


class Gerber:
    TOK = re.compile(r'%([^%]*)%|([^%*]*)\*', re.S)
    COORD = re.compile(r'^(?:G0?([123]))?(?:X(-?\d+))?(?:Y(-?\d+))?(?:I(-?\d+))?(?:J(-?\d+))?D0?([123])$')

    def __init__(self, path):
        self.path, self.text = path, path.read_text(encoding='ascii')
        self.aps, self.file_attrs = {}, {}
        self.flashes, self.lines, self.regions = [], [], []
        attrs, polarity, interp, cur, x, y = {}, 'D', 1, None, 0.0, 0.0
        region, contours, contour, scale = False, [], [], 1e6
        for ext, word in ((m.group(1), m.group(2)) for m in self.TOK.finditer(self.text)):
            if ext is not None:
                for blk in [b for b in ext.split('*') if b]:
                    if blk.startswith('FSLA'):
                        scale = 10 ** int(blk[-1])
                    elif blk.startswith('TF.'):
                        k, _, v = blk[3:].partition(','); self.file_attrs[k] = v
                    elif blk.startswith('TO.'):
                        k, _, v = blk[3:].partition(','); attrs[k] = tuple(v.split(','))
                    elif blk.startswith('TD'):
                        if blk == 'TD': attrs.clear()
                        else: attrs.pop(blk[3:], None)
                    elif blk.startswith('ADD'):
                        m = re.match(r'ADD(\d+)([A-Za-z_][\w.]*),?(.*)', blk)
                        self.aps[int(m.group(1))] = (m.group(2), [float(t) for t in m.group(3).split('X') if t])
                    elif blk in ('LPD', 'LPC'):
                        polarity = blk[2]
                continue
            w = word.strip()
            if not w or w.startswith('G04') or w == 'M02':
                continue
            if w in ('G01', 'G02', 'G03'):
                interp = int(w[2]); continue
            if w in ('G75', 'G74'):
                continue
            if w == 'G36':
                region, contours, contour = True, [], []; continue
            if w == 'G37':
                if contour: contours.append(contour)
                self.regions.append((contours, dict(attrs), polarity)); region = False; continue
            m = re.match(r'^D(\d{2,})$', w)
            if m and int(m.group(1)) >= 10:
                cur = int(m.group(1)); continue
            m = self.COORD.match(w)
            if not m:
                raise ValueError(f'{self.path.name}: nieobsłużone polecenie {w!r}')
            if m.group(1): interp = int(m.group(1))
            nx = int(m.group(2)) / scale if m.group(2) is not None else x
            ny = int(m.group(3)) / scale if m.group(3) is not None else y
            i = int(m.group(4)) / scale if m.group(4) is not None else 0.0
            j = int(m.group(5)) / scale if m.group(5) is not None else 0.0
            d = int(m.group(6))
            if d == 2:
                if region and contour: contours.append(contour)
                contour = [(nx, ny)] if region else contour
            elif d == 1:
                if interp == 1:
                    seg = [(nx, ny)]
                else:
                    seg = arc_points(x, y, nx, ny, x + i, y + j, interp == 2)
                if region:
                    if not contour: contour = [(x, y)]
                    contour.extend(seg)
                else:
                    self.lines.append(([(x, y)] + seg, cur, polarity))
            elif d == 3:
                self.flashes.append((nx, ny, cur, dict(attrs), polarity))
            x, y = nx, ny

    def objects(self):
        return len(self.flashes) + len(self.lines) + len(self.regions)

    def dark_objects(self):
        return sum(1 for o in self.flashes if o[4] == 'D') + sum(1 for o in self.lines if o[2] == 'D') + sum(1 for o in self.regions if o[2] == 'D')


def inside_poly(px, py, pts):
    c = False
    for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]):
        if (y1 > py) != (y2 > py) and px < (x2 - x1) * (py - y1) / (y2 - y1) + x1:
            c = not c
    return c


def inside_flash(px, py, f, aps):
    x, y, code, _, _ = f
    t, p = aps[code]
    if t == 'C': return math.hypot(px - x, py - y) <= p[0] / 2 + 1e-6
    if t in ('R', 'O'): return abs(px - x) <= p[0] / 2 + 1e-6 and abs(py - y) <= p[1] / 2 + 1e-6
    return False


def bbox_center(contours):
    xs = [p[0] for c in contours for p in c]; ys = [p[1] for c in contours for p in c]
    return (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2


def parse_drill(path):
    text = path.read_text(encoding='ascii'); tools, hits, cur, header, slots = {}, [], None, True, 0
    for line in text.splitlines():
        line = line.strip()
        if header:
            m = re.match(r'T(\d+)C([\d.]+)$', line)
            if m: tools[int(m.group(1))] = float(m.group(2))
            if line == '%': header = False
            continue
        if 'G85' in line: slots += 1
        m = re.match(r'T(\d+)$', line)
        if m: cur = int(m.group(1)); continue
        m = re.match(r'X(-?[\d.]+)Y(-?[\d.]+)$', line)
        if m and cur in tools: hits.append((float(m.group(1)), float(m.group(2)), tools[cur]))
    return text, tools, hits, slots


ALL = {'F.Cu': ('F_Cu', 'gtl'), 'B.Cu': ('B_Cu', 'gbl'), 'F.Mask': ('F_Mask', 'gts'), 'B.Mask': ('B_Mask', 'gbs'),
       'F.SilkS': ('F_Silkscreen', 'gto'), 'B.SilkS': ('B_Silkscreen', 'gbo'), 'Edge.Cuts': ('Edge_Cuts', 'gm1')}
names = dict(ALL[l] for l in CFG['layers'])
expected = {f'{NAME}-{k}.{v}' for k, v in names.items()} | {f'{NAME}-PTH.drl', f'{NAME}-NPTH.drl'}
check(f'Dokładnie {len(names)} warstw Gerber i 2 pliki Excellon', {f.name for f in G.iterdir()} == expected, sorted(f.name for f in G.iterdir()))
L = {k: Gerber(G/f'{NAME}-{k}.{v}') for k, v in names.items()}
functions = {'F_Cu': 'Copper,L1,Top', 'B_Cu': 'Copper,L2,Bot', 'F_Mask': 'Soldermask,Top', 'B_Mask': 'Soldermask,Bot',
             'F_Silkscreen': 'Legend,Top', 'B_Silkscreen': 'Legend,Bot', 'Edge_Cuts': 'Profile,NP'}
check('Funkcje warstw w atrybutach X2', all(L[k].file_attrs.get('FileFunction') == v for k, v in functions.items() if k in L),
      {k: L[k].file_attrs.get('FileFunction') for k in L})
EMPTY_OK = set(CFG.get('empty_layers', []))
dark = {k: L[k].dark_objects() for k in L}
check('Każda warstwa (poza zadeklarowanymi jako puste) drukuje dane', all((dark[k] > 0) != (k in EMPTY_OK) for k in L), dark)
check('Wszystkie Gerbery: mm, format 4.6, znacznik końca',
      all(all(s in L[k].text for s in ('%MOMM*%', '%FSLAX46Y46*%', 'M02*')) for k in L))
check('Maski mają polaryzację Negative', all('%TF.FilePolarity,Negative*%' in L[k].text for k in ('F_Mask', 'B_Mask')))
check('Wspólny początek współrzędnych (TF.SameCoordinates)', all(L[k].file_attrs.get('SameCoordinates') == 'Original' for k in L))

edge = L['Edge_Cuts']
corners = Counter()
for pts, _, _ in edge.lines:
    corners[(round(pts[0][0], 6), round(pts[0][1], 6))] += 1
    corners[(round(pts[-1][0], 6), round(pts[-1][1], 6))] += 1
want = Counter({(0.0, 0.0): 2, (float(W), 0.0): 2, (float(W), float(-H)): 2, (0.0, float(-H)): 2})
check(f'Jeden zamknięty obrys {W} × {H} mm w początku układu', len(edge.lines) == 4 and len(edge.flashes) == 0 and not edge.regions and corners == want,
      {str(k): v for k, v in corners.items()})

drills = {}
for label, plated in (('PTH', True), ('NPTH', False)):
    text, tools, hits, slots = parse_drill(G/f'{NAME}-{label}.drl')
    drills[label] = hits
    found = Counter((round(x, 3), round(y, 3), round(d, 3)) for x, y, d in hits)
    wanted = Counter((round(o['x'], 3), round(o['y'], 3), round(o['diameter'], 3)) for o in D['holes'] if o['plated'] == plated)
    check(f'{label}: każdy otwór zgodny z PCB (położenie i średnica)', found == wanted,
          {'plik': sum(found.values()), 'pcb': sum(wanted.values()), 'brak': list((wanted - found).elements())[:10], 'nadmiar': list((found - wanted).elements())[:10]})
    check(f'{label}: mm, dziesiętnie, współrzędne absolutne, bez szczelin', all(s in text for s in ('METRIC', 'G90', 'absolute / metric / decimal')) and slots == 0)
    check(f'{label}: jawny atrybut metalizacji', ('TF.FileFunction,Plated' if plated else 'TF.FileFunction,NonPlated') in text)

for side, cu, mk in (('góra', 'F_Cu', 'F_Mask'), ('dół', 'B_Cu', 'B_Mask')):
    layer_name = 'F.Cu' if cu == 'F_Cu' else 'B.Cu'
    mask_name = 'F.Mask' if mk == 'F_Mask' else 'B.Mask'
    g = L[cu]
    npth = {(p['ref'], p['pin']) for p in D['pads'] if p['attr'] == 3}
    found = Counter()
    for x, y, code, a, pol in g.flashes:
        if 'P' in a and (a['P'][0], a['P'][1]) not in npth:
            net = a.get('N', ('',))[0]
            found[(a['P'][0], a['P'][1], round(x, 4), round(y, 4), '' if net == 'N/C' else net)] += 1
    for contours, a, pol in g.regions:
        if 'P' in a and (a['P'][0], a['P'][1]) not in npth:
            cx, cy = bbox_center(contours); net = a.get('N', ('',))[0]
            found[(a['P'][0], a['P'][1], round(cx, 4), round(cy, 4), '' if net == 'N/C' else net)] += 1
    wanted = Counter((p['ref'], p['pin'], round(p['x'], 4), round(p['y'], 4), p['net']) for p in D['pads'] if layer_name in p['copper'] and p['attr'] != 3)
    check(f'Miedź {side}: położenie i sieć każdego pola (bez otworów NPTH) zgodne z PCB', found == wanted,
          {'pola': sum(found.values()), 'pcb': sum(wanted.values()), 'brak': list((wanted - found).elements())[:8], 'nadmiar': list((found - wanted).elements())[:8]})
    zone_regions = [r for r in g.regions if 'P' not in r[1] and r[2] == 'D']
    check(f'Miedź {side}: liczba regionów wylewek = liczba konturów wypełnienia w PCB',
          len(zone_regions) == D['zone_outlines'][layer_name], {'gerber': len(zone_regions), 'pcb': D['zone_outlines'][layer_name]})
    m = L[mk]
    missing = []
    for p in D['pads']:
        if mask_name not in p['mask']:
            continue
        ok = any(inside_flash(p['x'], p['y'], f, m.aps) for f in m.flashes) or \
             any(inside_poly(p['x'], p['y'], c) for contours, _, _ in m.regions for c in contours)
        if not ok:
            missing.append((p['ref'], p['pin']))
    check(f'Maska {side}: otwarcie nad każdym polem z maską w PCB', not missing, missing[:10])

receipt = json.loads((V/'export-receipt.json').read_text(encoding='utf-8'))
files_now = {f.name: sha(f) for f in sorted(G.iterdir()) if f.is_file()}
check('Bajty CAM bez zmian od eksportu', receipt['files'] == files_now)

# ---------- podglądy z samych plików CAM ----------
from PIL import Image, ImageDraw, ImageChops, ImageOps, ImageFont
S = 20.0  # px / mm
PW, PH = int(W * S), int(H * S)
T = lambda x, y: (x * S, -y * S)


def render(g):
    img = Image.new('L', (PW, PH), 255); dr = ImageDraw.Draw(img)
    for pts, code, pol in g.lines:
        col = 0 if pol == 'D' else 255
        t, p = g.aps.get(code, ('C', [0.1]))
        w = max(1, int(round((p[0] if t == 'C' else min(p)) * S)))
        xy = [T(*q) for q in pts]
        dr.line(xy, fill=col, width=w)
        for qx, qy in (xy[0], xy[-1]):
            dr.ellipse((qx - w / 2, qy - w / 2, qx + w / 2, qy + w / 2), fill=col)
    for contours, a, pol in g.regions:
        for c in contours:
            if len(c) > 2:
                dr.polygon([T(*q) for q in c], fill=0 if pol == 'D' else 255)
    for x, y, code, a, pol in g.flashes:
        col = 0 if pol == 'D' else 255
        t, p = g.aps[code]; cx, cy = T(x, y)
        if t == 'C':
            r = p[0] * S / 2; dr.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col)
        elif t == 'R':
            dr.rectangle((cx - p[0] * S / 2, cy - p[1] * S / 2, cx + p[0] * S / 2, cy + p[1] * S / 2), fill=col)
        elif t == 'O':
            w, h = p[0] * S, p[1] * S; r = min(w, h) / 2
            dr.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), radius=r, fill=col)
    return img


for k in L:
    if k != 'Edge_Cuts':
        render(L[k]).save(PV/f'CAM-{k}.png')
for side, cu, mk, sk in (('top', 'F_Cu', 'F_Mask', 'F_Silkscreen'), ('bottom', 'B_Cu', 'B_Mask', 'B_Silkscreen')):
    copper, mask = (ImageOps.invert(Image.open(PV/f'CAM-{n}.png')) for n in (cu, mk))
    silk = ImageOps.invert(Image.open(PV/f'CAM-{sk}.png')) if sk in L else Image.new('L', (PW, PH), 0)
    board = Image.new('RGB', (PW, PH), (20, 80, 51))
    board.paste((40, 117, 75), mask=copper)
    board.paste((196, 185, 151), mask=ImageChops.multiply(mask, copper))
    board.paste((249, 248, 226), mask=silk)
    dr = ImageDraw.Draw(board)
    for hits in drills.values():
        for x, y, d in hits:
            cx, cy = T(x, y); r = d * S / 2
            dr.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(24, 25, 28))
    if side == 'bottom':
        board = ImageOps.mirror(board)
    board.save(PV/f'CAM-{side}.png')
font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 26)
tiles = [t for t in ['CAM-top', 'CAM-bottom', 'CAM-F_Cu', 'CAM-B_Cu', 'CAM-F_Mask', 'CAM-B_Mask', 'CAM-F_Silkscreen', 'CAM-B_Silkscreen'] if t[4:] in L or t in ('CAM-top', 'CAM-bottom')]
tw = 790; th = int(tw * H / W)
sheet = Image.new('RGB', (1640, 10 + 4 * (th + 60)), '#eceef0'); dr = ImageDraw.Draw(sheet)
for i, n in enumerate(tiles):
    im = Image.open(PV/f'{n}.png').convert('RGB'); im.thumbnail((tw, th))
    x = 10 + (i % 2) * 820; y = 10 + (i // 2) * (th + 60)
    dr.text((x, y), n + (' (widok od spodu)' if n == 'CAM-bottom' else ''), font=font, fill='black'); sheet.paste(im, (x, y + 36))
sheet.save(PV/'CAM-kontrola-warstw.png')

report = {'pass': all(c['pass'] for c in checks), 'parser': 'własny parser Gerber X2/Excellon (src/check_cam.py), bez KiCada',
          'checks': checks, 'board_sha256': D['board_sha256'], 'files': files_now,
          'notes': ['Współrzędne w plikach nie są odbijane; tylko kolorowy podgląd spodu jest lustrzany (widok od spodu).',
                    'To kontrola zawartości CAM względem modelu PCB, nie niezależny DRC elektryczny.',
                    'Łuki w regionach przybliżone odcinkami wyłącznie do podglądów i testu położenia w masce.']}
(V/'cam-checks.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print(json.dumps({'pass': report['pass'], 'checks': len(checks), 'PTH': len(drills['PTH']), 'NPTH': len(drills['NPTH'])}))
if not report['pass']:
    raise SystemExit(1)
