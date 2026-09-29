"""Porównanie wyników odtworzenia pakietu (chmura, Linux) z plikami w repozytorium (Windows).

Użycie (w obrazie egrlab-kicad, bo PNG/PDF wymagają Pillow/numpy/pdftoppm):
  python3 scripts/chmura/porownaj_wyniki.py <katalog-repo> <katalog-odtworzony> [--json raport.json]

Nic nie zapisuje do żadnego z katalogów. Klasy wyniku dla każdego pliku różniącego się bajtowo:
  CRLF      — identyczny po zamianie CRLF -> LF (Python na Windows zapisuje CRLF)
  ZNACZNIKI — identyczny po usunięciu dat, znaczników czasu i ścieżek bezwzględnych
  KOLEJNOŚĆ — JSON równy po posortowaniu list (Windows sortuje ścieżki bez rozróżniania wielkości liter)
  SKRÓTY    — JSON różni się tylko skrótami SHA-256 plików, które same są w klasach wyżej
  RASTER    — PNG: ten sam rozmiar, podany odsetek różniących się pikseli
  PDF       — ta sama liczba stron i te same słowa (pdftotext, multizbiór), różnice w strumieniach
  GERBER    — Gerber równy semantycznie (gerber_equiv z P00-R3: apertury i kolejność bez znaczenia)
  GERBER~   — Gerber równy z tolerancją 10 nm wierzchołków (porownaj_gerbery.py; podana maks. odchyłka)
  RÓŻNICA   — rzeczywista różnica treści (wymaga oceny)
  LOG       — dziennik narzędzia; różnice oczekiwane, nie oceniane
"""
import hashlib, json, re, subprocess, sys
from pathlib import Path

VOLATILE_KEYS = {'date', 'created_utc', 'generated', 'generated_utc', 'timestamp', 'time', 'started', 'finished',
                 'created', 'utc', 'datetime', 'elapsed_s', 'elapsed', 'duration_s'}
TS = re.compile(r'\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(\.\d+)?([+-]\d{2}:\d{2}|Z)?')
WINPATH = re.compile(r'[A-Za-z]:[\\/](?:[^\s"<>|]*[\\/])?')
GERBER_SUFFIXES = {'.gtl', '.gbl', '.gts', '.gbs', '.gto', '.gbo', '.gtp', '.gbp', '.gm1', '.gbr', '.g1', '.g2'}
POSIXABS = re.compile(r'/(?:tmp|home|repo|root)/[^\s"<>]*/')


def text_norm(b):
    s = b.decode('utf-8', 'replace').replace('\r\n', '\n')
    s = TS.sub('<TS>', s)
    s = WINPATH.sub('<ABS>/', s)
    s = POSIXABS.sub('<ABS>/', s)
    return s.replace('\\', '/')


def json_norm(x, sort_lists=False):
    if isinstance(x, dict):
        return {k: ('<V>' if k in VOLATILE_KEYS else json_norm(v, sort_lists)) for k, v in sorted(x.items())}
    if isinstance(x, list):
        v = [json_norm(i, sort_lists) for i in x]
        return sorted(v, key=lambda i: json.dumps(i, sort_keys=True, ensure_ascii=False).casefold()) if sort_lists else v
    if isinstance(x, str):
        return text_norm(x.encode())
    return x


def json_diff(a, b, path='', out=None):
    out = [] if out is None else out
    if type(a) is not type(b):
        out.append((path, a, b))
    elif isinstance(a, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                out.append((path + '/' + k, a.get(k, '<brak>'), b.get(k, '<brak>')))
            else:
                json_diff(a[k], b[k], path + '/' + k, out)
    elif isinstance(a, list):
        if len(a) != len(b):
            out.append((path, f'len {len(a)}', f'len {len(b)}'))
        for i, (x, y) in enumerate(zip(a, b)):
            json_diff(x, y, f'{path}[{i}]', out)
    elif a != b:
        out.append((path, a, b))
    return out


def png_diff(fa, fb):
    from PIL import Image, ImageChops
    import numpy as np
    A = Image.open(fa).convert('RGB'); B = Image.open(fb).convert('RGB')
    if A.size != B.size:
        return None, f'rozmiar {A.size} vs {B.size}'
    d = np.asarray(ImageChops.difference(A, B)).max(axis=2)
    return float((d > 32).mean()) * 100, f'{A.size[0]}x{A.size[1]}'


def pdf_info(f):
    txt = subprocess.run(['pdftotext', '-layout', str(f), '-'], capture_output=True, text=True).stdout
    pages = subprocess.run(['pdfinfo', str(f)], capture_output=True, text=True).stdout
    m = re.search(r'Pages:\s+(\d+)', pages)
    # multizbiór słów: pdftotext układa tekst wg położenia, a to różni się o ułamki punktu między systemami
    return (int(m.group(1)) if m else None), sorted(TS.sub('<TS>', txt).split())


def sha(b):
    return hashlib.sha256(b).hexdigest()


def classify(rel, a, b, benign_hashes):
    ba, bb = a.read_bytes(), b.read_bytes()
    if ba == bb:
        return 'IDENTYCZNY', ''
    if ba.replace(b'\r\n', b'\n') == bb.replace(b'\r\n', b'\n'):
        return 'CRLF', ''
    suf = a.suffix.lower()
    if suf == '.log':
        return 'LOG', ''
    if suf == '.png':
        pct, info = png_diff(a, b)
        return ('RASTER', f'{info}, {pct:.3f} % pikseli') if pct is not None else ('RÓŻNICA', info)
    if suf in GERBER_SUFFIXES:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from porownaj_gerbery import compare, verdict
        r = compare(str(a), str(b)); v = verdict(r)
        if v == 'EQUAL':
            return 'GERBER', f"{r['objects'][0]} obiektów"
        if v == 'EQUAL~':
            return 'GERBER~', f"{r['objects'][0]} obiektów, {r['paired_within_tol']} w tolerancji, maks. {r['max_dev_nm']:.1f} nm"
        return 'RÓŻNICA', f"Gerber: obiekty {r['objects']}, bez pary {r['unpaired']}"
    if suf == '.pdf':
        (pa, ta), (pb, tb) = pdf_info(a), pdf_info(b)
        if pa == pb and ta == tb:
            return 'PDF', f'{pa} str., te same słowa ({len(ta)})'
        return 'RÓŻNICA', f'strony {pa}/{pb}, tekst {"identyczny" if ta == tb else "różny"}'
    if suf == '.json':
        try:
            ja, jb = json.loads(ba), json.loads(bb)
        except ValueError:
            ja = jb = None
        if ja is not None:
            if json_norm(ja) == json_norm(jb):
                return 'ZNACZNIKI', ''
            if json_norm(ja, True) == json_norm(jb, True):
                return 'KOLEJNOŚĆ', ''
            d = json_diff(json_norm(ja, True), json_norm(jb, True))
            hexre = re.compile(r'^[0-9a-f]{64}$')
            if all(isinstance(x, str) and isinstance(y, str) and hexre.match(x) and hexre.match(y) for _, x, y in d):
                if all(y in benign_hashes for _, x, y in d):
                    return 'SKRÓTY', '; '.join(p for p, _, _ in d)[:300]
            return 'RÓŻNICA', '; '.join(f'{p}: {str(x)[:60]} -> {str(y)[:60]}' for p, x, y in d[:6]) + (f' (+{len(d) - 6})' if len(d) > 6 else '')
    if text_norm(ba) == text_norm(bb):
        return 'ZNACZNIKI', ''
    la, lb = text_norm(ba).splitlines(), text_norm(bb).splitlines()
    n = sum(1 for x, y in zip(la, lb) if x != y) + abs(len(la) - len(lb))
    return 'RÓŻNICA', f'{n} linii różnych z {max(len(la), len(lb))}'


def main():
    ra, rb = Path(sys.argv[1]), Path(sys.argv[2])
    out_json = sys.argv[sys.argv.index('--json') + 1] if '--json' in sys.argv else None
    fa = {p.relative_to(ra).as_posix() for p in ra.rglob('*') if p.is_file()}
    fb = {p.relative_to(rb).as_posix() for p in rb.rglob('*') if p.is_file()}
    rows = []
    # Skróty plików odtworzonych, które okazały się tylko CRLF/ZNACZNIKI — różnice w manifestach JSON z nich wynikają
    benign = set()
    order = sorted(fa & fb, key=lambda r: (r.endswith('.json'), r))
    for rel in order:
        cls, info = classify(rel, ra / rel, rb / rel, benign)
        if cls in ('IDENTYCZNY', 'CRLF', 'ZNACZNIKI', 'KOLEJNOŚĆ', 'SKRÓTY', 'RASTER', 'PDF', 'LOG', 'GERBER', 'GERBER~'):
            benign.add(sha((rb / rel).read_bytes()))
        rows.append((rel, cls, info))
    for rel in sorted(fa - fb):
        rows.append((rel, 'TYLKO-W-REPO', ''))
    for rel in sorted(fb - fa):
        rows.append((rel, 'TYLKO-NOWY', ''))
    counts = {}
    for _, c, _ in rows:
        counts[c] = counts.get(c, 0) + 1
    print('Podsumowanie:', ', '.join(f'{k} {v}' for k, v in sorted(counts.items())))
    for rel, c, info in rows:
        if c not in ('IDENTYCZNY', 'CRLF', 'LOG'):
            print(f'{c:12} {rel}  {info}')
    if out_json:
        Path(out_json).write_text(json.dumps({'counts': counts, 'files': [dict(path=r, cls=c, info=i) for r, c, i in rows]},
                                             ensure_ascii=False, indent=1), encoding='utf-8')


if __name__ == '__main__':
    main()
