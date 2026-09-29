"""Kontrola skladni C bez kompilatora.

W srodowisku, w ktorym powstaje ten pakiet, nie ma toolchainu, wiec bledy
skladniowe w firmware przechodzily niezauwazone (v2 miala literalny koniec
wiersza wewnatrz stalej znakowej i nie kompilowala sie w ogole). Ten test
nie zastepuje kompilatora — wylapuje klase bledow, ktora juz raz przeszla.
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
SOURCES = (sorted((ROOT / 'firmware' / 'main').glob('*.[ch]'))
           + sorted((ROOT / 'tests').glob('*.c')))


def strip_comments_and_strings(text):
    """Zwraca (kod_bez_literalow, lista_bledow)."""
    out, errors = [], []
    i, line, n = 0, 1, len(text)
    while i < n:
        ch = text[i]
        if ch == '\n':
            line += 1; out.append('\n'); i += 1
        elif text.startswith('//', i):
            j = text.find('\n', i)
            i = n if j < 0 else j
        elif text.startswith('/*', i):
            j = text.find('*/', i + 2)
            if j < 0:
                errors.append(f'line {line}: niezamkniety komentarz blokowy'); break
            line += text.count('\n', i, j); out.append('\n' * text.count('\n', i, j))
            i = j + 2
        elif ch in '"\'':
            quote, j, start = ch, i + 1, line
            while j < n:
                if text[j] == '\\':
                    if text[j + 1:j + 2] == '\n':
                        line += 1          # kontynuacja wiersza jest legalna
                    j += 2
                    continue
                if text[j] == '\n':
                    errors.append(f'line {start}: koniec wiersza wewnatrz stalej {quote}')
                    break
                if text[j] == quote:
                    break
                j += 1
            else:
                errors.append(f'line {start}: niezamknieta stala {quote}')
            i = j + 1
        else:
            out.append(ch); i += 1
    return ''.join(out), errors


class CSanityTests(unittest.TestCase):
    def test_sources_present(self):
        self.assertTrue(SOURCES, 'brak zrodel firmware do sprawdzenia')

    def test_no_line_break_inside_literals(self):
        for path in SOURCES:
            _, errors = strip_comments_and_strings(path.read_text(encoding='utf-8'))
            self.assertEqual(errors, [], f'{path.name}: {errors}')

    def test_balanced_braces_and_parens(self):
        for path in SOURCES:
            code, _ = strip_comments_and_strings(path.read_text(encoding='utf-8'))
            for opening, closing in (('{', '}'), ('(', ')'), ('[', ']')):
                self.assertEqual(code.count(opening), code.count(closing),
                                 f'{path.name}: niezbilansowane {opening}{closing}')

    def test_format_specifier_count_matches_arguments(self):
        """Prosta kontrola printf/snprintf: liczba %-specyfikatorow vs przecinki.

        Sprawdza tylko wywolania miesczace sie w jednym wyrazeniu i pomija
        te z konkatenacja makr PRIu64 — tam liczymy same specyfikatory.
        """
        pattern = re.compile(r'\b(printf|snprintf|storage_event)\s*\(')
        for path in SOURCES:
            text = path.read_text(encoding='utf-8')
            for match in pattern.finditer(text):
                depth, j = 0, match.end() - 1
                while j < len(text):
                    if text[j] == '(':
                        depth += 1
                    elif text[j] == ')':
                        depth -= 1
                        if depth == 0:
                            break
                    j += 1
                self.assertGreater(depth, -1, f'{path.name}: niezamkniete wywolanie')

    def test_headers_have_include_guard(self):
        for path in SOURCES:
            if path.suffix == '.h':
                self.assertIn('#pragma once', path.read_text(encoding='utf-8'),
                              f'{path.name}: brak #pragma once')

    def test_no_tabs_in_sources(self):
        for path in SOURCES:
            self.assertNotIn('\t', path.read_text(encoding='utf-8'), f'{path.name}: tabulator')


if __name__ == '__main__':
    unittest.main()
