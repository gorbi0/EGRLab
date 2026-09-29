"""Order-independent comparison of two Gerber X2 files (P00 R3).

KiCad numbers apertures and writes objects in board-file order, which follows random UUIDs, so two exports of the
same geometry differ byte by byte. This reduces a file to a multiset of flashes, strokes and region contours with
the aperture definition written out (aperture macros compared by body), and ignores attributes, dates and comments.
usage: python gerber_equiv.py A.gbr B.gbr  -> prints EQUAL / DIFFERENT and the object counts; exit 0 when equal
"""
import collections, re, sys


def normalize(path):
    text = open(path, encoding='ascii', errors='replace').read().replace('\r', '').replace('\n', '')
    ap, macros, fmt = {}, {}, None
    cur, pol, mode, region, contour = None, 'D', 'G01', False, []
    x = y = 0; items = collections.Counter()

    def canonical(contour):
        """Region contour without exactly collinear intermediate vertices (the zone filler may keep or drop them)."""
        if any(len(e) != 2 for e in contour):
            return frozenset(frozenset(e[:2]) if len(e) == 2 else e for e in contour)
        pts = [e[0] for e in contour]
        changed = True
        while changed and len(pts) > 3:
            changed = False
            for i in range(len(pts)):
                a, b, c = pts[i - 1], pts[i], pts[(i + 1) % len(pts)]
                cross = (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])
                dot = (b[0] - a[0]) * (c[0] - b[0]) + (b[1] - a[1]) * (c[1] - b[1])
                if cross == 0 and dot > 0:
                    del pts[i]; changed = True; break
        return frozenset(frozenset((pts[i - 1], pts[i])) for i in range(len(pts)))

    def command(s):
        nonlocal cur, mode, region, contour, x, y
        if not s or s.startswith('G04') or s == 'M02':
            return
        if s in ('G36', 'G37'):
            if s == 'G37' and contour:
                items[('R', pol, canonical(contour))] += 1
            region, contour = s == 'G36', []; return
        if s in ('G01', 'G02', 'G03', 'G74', 'G75'):
            if s in ('G01', 'G02', 'G03'):
                mode = s
            return
        m = re.fullmatch(r'(G0[123])?(?:X(-?\d+))?(?:Y(-?\d+))?(?:I(-?\d+))?(?:J(-?\d+))?D0([123])', s)
        if m:
            if m[1]:
                mode = m[1]
            nx = int(m[2]) if m[2] is not None else x; ny = int(m[3]) if m[3] is not None else y
            if m[6] == '1':
                seg = ((x, y), (nx, ny)) if mode == 'G01' else ((x, y), (nx, ny), mode, m[4], m[5])
                if region:
                    contour.append(seg)
                elif mode == 'G01':
                    items[('S', ap[cur], pol, frozenset(seg))] += 1
                else:
                    items[('A', ap[cur], pol) + seg] += 1
            elif m[6] == '3':
                items[('F', ap[cur], pol, (nx, ny))] += 1
            x, y = nx, ny; return
        m = re.fullmatch(r'(?:G54)?D(\d+)', s)
        if m and int(m[1]) >= 10:
            cur = m[1]; return
        raise ValueError(f'{path}: unhandled command {s[:40]}')

    for part in re.split(r'(%[^%]*%)', text):
        if part.startswith('%'):
            stmts = [t for t in part.strip('%').split('*') if t]
            if not stmts:
                continue
            if stmts[0].startswith('AM'):
                macros[stmts[0][2:]] = tuple(t for t in stmts[1:] if not t.startswith('0 '))  # drop macro comments
                continue
            for s in stmts:
                if s.startswith('FS'):
                    fmt = s
                elif s.startswith('AD'):
                    m = re.match(r'ADD(\d+)(.*)', s); name = re.match(r'[A-Za-z_$][\w.$]*', m[2])
                    ap[m[1]] = (m[2], macros.get(name[0]) if name and name[0] in macros else None)
                elif s.startswith('LP'):
                    pol = s[2]
                # TF/TA/TO/TD attributes, MO, LN: ignored
        else:
            for s in part.split('*'):
                command(s.strip())
    return fmt, items


def equal(a, b):
    fa, ia = normalize(a); fb, ib = normalize(b)
    return fa == fb and ia == ib, sum(ia.values()), sum(ib.values())


if __name__ == '__main__':
    ok, na, nb = equal(sys.argv[1], sys.argv[2])
    print('EQUAL' if ok else 'DIFFERENT', na, nb)
    sys.exit(0 if ok else 1)
