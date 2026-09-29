# Odtworzenie rysunków

Python 3.10+, Windows z czcionkami Segoe UI oraz pakiet reportlab. Generator używa lokalnej kopii tabel wejściowych V4 w `wejscie/`; nie czyta ani nie zmienia oryginałów projektu.

W katalogu `EGRLab-v4-schemat`:

```text
python -m pip install reportlab
python generator/build.py --out nowy-schemat
```

Zewnętrzne źródło tabel można wskazać przez `--source KATALOG`, gdzie KATALOG zawiera podkatalog `hardware`. Generator tworzy PDF, SVG i tabele połączeń; komentarze w `UWAGI-S1.md` pozostają dokumentacją redakcyjną. Domyślne `--out` wskazuje katalog pakietu, dlatego do eksperymentów podaj inny katalog.

Układ jest rysowany przez ReportLab; SVG używa tych samych współrzędnych. Nie jest to eksport z KiCad, nie wykonuje ERC ani doboru footprintów. Numery pinów przekaźników pochodzą z karty G6K-2F-Y; własne zmiany trzeba ponownie zweryfikować.
