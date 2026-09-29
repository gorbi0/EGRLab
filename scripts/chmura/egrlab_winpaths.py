"""Tłumaczenie ścieżek czcionek Windows na Linux (tylko w obrazie egrlab-kicad).

Zamknięte pakiety mają wpisane na stałe 'C:/Windows/Fonts/arial.ttf' itp. i nie wolno ich
zmieniać. Ten moduł (ładowany przez .pth) podmienia wyłącznie nazwy plików czcionek przy
wczytywaniu przez reportlab TTFont i PIL ImageFont.truetype. Arial -> Liberation Sans
(metrycznie zgodna: te same szerokości znaków, więc układ tekstu w PDF się nie zmienia;
kształt glifów w rastrach tak). Wyłączenie: EGRLAB_WINPATHS=0.
"""
import os, sys

_DIR = os.environ.get('EGRLAB_FONT_DIR', '/usr/share/fonts/truetype/liberation')
_MAP = {
    'arial.ttf': 'LiberationSans-Regular.ttf', 'arialbd.ttf': 'LiberationSans-Bold.ttf',
    'ariali.ttf': 'LiberationSans-Italic.ttf', 'arialbi.ttf': 'LiberationSans-BoldItalic.ttf',
    'arialn.ttf': 'LiberationSansNarrow-Regular.ttf', 'arialnb.ttf': 'LiberationSansNarrow-Bold.ttf',
    'cour.ttf': 'LiberationMono-Regular.ttf', 'courbd.ttf': 'LiberationMono-Bold.ttf',
    'times.ttf': 'LiberationSerif-Regular.ttf', 'timesbd.ttf': 'LiberationSerif-Bold.ttf',
}
LOG = []

def translate(p):
    if not isinstance(p, (str, os.PathLike)):
        return p
    s = os.fspath(p)
    if not isinstance(s, str):
        return p
    n = s.replace('\\', '/')
    if n.lower().startswith('c:/windows/fonts/'):
        base = n.rsplit('/', 1)[1].lower()
        if base in _MAP:
            out = os.path.join(_DIR, _MAP[base])
            if (s, out) not in LOG:
                LOG.append((s, out))
                if os.environ.get('EGRLAB_WINPATHS_VERBOSE'):
                    print(f'[egrlab_winpaths] {s} -> {out}', file=sys.stderr)
            return out
    return p

def _patch(name, m):
    if name == 'reportlab.pdfbase.ttfonts':
        C = m.TTFont; o = C.__init__
        def init(self, name_, filename, *a, **k):
            return o(self, name_, translate(filename), *a, **k)
        C.__init__ = init
    elif name == 'PIL.ImageFont':
        o = m.truetype
        def truetype(font=None, *a, **k):
            return o(translate(font), *a, **k)
        m.truetype = truetype

class _Finder:
    """Po pełnym wykonaniu wskazanego modułu podmienia jego funkcję wczytującą czcionkę."""
    NAMES = ('reportlab.pdfbase.ttfonts', 'PIL.ImageFont')
    def find_spec(self, name, path=None, target=None):
        if name not in self.NAMES:
            return None
        import importlib.machinery
        spec = importlib.machinery.PathFinder.find_spec(name, path)
        if spec is None or spec.loader is None:
            return spec
        loader = spec.loader; orig = loader.exec_module
        def exec_module(module):
            orig(module); _patch(name, module)
        loader.exec_module = exec_module
        return spec

def _install():
    sys.meta_path.insert(0, _Finder())

if os.environ.get('EGRLAB_WINPATHS', '1') != '0':
    _install()
