# Odtwarzanie P06-R1

KiCad 10.0.6, Python 3.11 z `pcbnew`, NumPy i Pillow. Drugi interpreter dla dokumentów: Python z ReportLab. Poppler `pdftoppm` do kontroli wyglądu. Wymagana standardowa biblioteka symboli/footprintów KiCad podczas przebudowy; samo otwieranie projektu używa bibliotek skopiowanych do `eda/libraries`.

Zmienne środowiskowe:

```powershell
$env:KICAD_LIBRARY_ROOT = 'C:/Program Files/KiCad/10.0/share/kicad'
$env:KICAD_CLI = 'C:/Program Files/KiCad/10.0/bin/kicad-cli.exe'
$env:EGRLAB_DOC_PYTHON = 'C:/sciezka/do/python-z-reportlab.exe'
$env:PDFTOPPM = 'C:/sciezka/do/pdftoppm.exe'
```

Uruchomić Pythonem z `pcbnew`:

```powershell
python src/run_release.py --rebuild
```

Powstaje schemat, XML, PCB, sprawdzenia i dwa PDF. Używany jest **zapisany** `routing/P06.ses`; router nie uruchamia się ponownie. SES, zablokowane trasy i zapis uzupełnień stanowią część źródeł projektu. Nowe losowe trasowanie może dać inną geometrię i nie zastępuje odtwarzania zatwierdzonej wersji. Nie podmieniać SES z innego rozmieszczenia.

`python src/run_release.py` odświeża eksport XML, ERC, testy, natywne DRC i PDF bieżącego projektu bez generowania obwodu od nowa. `python src/package_manifest.py --check` wykrywa zmianę lub brak pliku w zamrożonym wydaniu. Celowa edycja wymaga ponownej walidacji i utworzenia nowego manifestu; stare QA nie dotyczy zmienionych plików.

Raporty przed ostatecznym DRC w `routing/` dokumentują proces trasowania; nie są werdyktem wydania. Aktualny wynik to `verification/drc.json`, związany z wejściami przez `drc.provenance.json`. Sprawdzenia nie wyłączają pojedynczych naruszeń i nie stosują listy wyjątków DRC. Domyślnie nieaktywne reguły KiCad są jawne w `ignored_checks` raportu.

PDF schematu jest wektorowy, natywnie eksportowany z KiCad. PDF PCB zawiera wierne rastry CAD 600 dpi w skali 1:1. Po generacji obejrzeć wszystkie strony obu PDF. Warstwa B.Cu jest prześwietleniem od góry, bez odbicia lustrzanego. Podczas drukowania wyłączyć dopasowanie do strony.

Test odtworzenia wykonywany na kopii katalogu przebudowuje źródła, uruchamia świeże sprawdzenia i porównuje semantyczny odcisk geometrii. Odcisk pomija losowe UUID, obejmuje pozycje/nazwy/pady, ścieżki, via, napisy, obrysy stref i oznaczenia referencji. Nie zastępuje ERC/DRC ani sprawdzenia fizycznych części.
