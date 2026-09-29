# Odtwarzanie P04-R2.2

KiCad 10.0.6, jego Python z pcbnew/Pillow; Python dokumentów z reportlab. Ustawić KICAD_LIBRARY_ROOT i EGRLAB_DOC_PYTHON, opcjonalnie PDFTOPPM.

1. `python src/run_release.py --no-package` — schemat, BOM, netlista, testy, odtworzenie zapisanych tras, DRC i PDF.
2. `python src/audit_rebuild.py` — niezależny CAD w pustym katalogu, porównanie geometrii. Nie zastępuje oględzin PDF.
3. Obejrzeć wszystkie strony PDF i zapisać rzeczywisty przegląd wraz z hashami w verification/visual-qa.json.
4. `python src/package_release.py` — walidacja aktualności raportów, manifest, ZIP.

reference/reset-peer-parts.json jest zamrożonym kontraktem P03-R5. Przy zmianie P03 porównać go z faktycznym docs/parts.json tej płytki. Oryginalna geometria R2.1 jest w reference/previous-release, nie zależy od obecności katalogów sąsiadów.
