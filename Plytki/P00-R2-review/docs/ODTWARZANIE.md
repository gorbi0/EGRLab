# P00-R2 - samodzielne odtwarzanie

Pakiet nie wymaga żadnej innej płytki EGRLab. Wymaga Windows, KiCad 10.0.6 z Pythonem `pcbnew`, Pillow i numpy; osobnego lub tego samego Pythona z ReportLab i Pillow. Arial pochodzi z Windows. Opcjonalny Poppler generuje PNG kontrolne. Nie wprowadzać zmian w zainstalowanym toolchainie.

Ustawić zmienne na lokalne ścieżki:

- `KICAD_LIBRARY_ROOT`: katalog `share/kicad` z bibliotekami KiCad 10.
- `KICAD10_3DMODEL_DIR`: opcjonalnie inny katalog modeli; domyślnie `3dmodels` pod `KICAD_LIBRARY_ROOT`. Korpusy i kolory są poglądowe; przełączniki i ceramika nie mają modeli w tym podglądzie.
- `KICAD_CLI`: `kicad-cli.exe`; domyślnie obok użytego Pythona KiCad.
- `KICAD_CONFIG_HOME`: zapisywalny katalog konfiguracji KiCad.
- `EGRLAB_DOC_PYTHON`: Python z ReportLab i Pillow.
- `PDFTOPPM`: opcjonalna ścieżka Poppler `pdftoppm.exe`.
- `EGRLAB_FREEROUTING`: tylko dla `--new-route`, katalog z `freerouting-2.1.0.jar` i `jdk-21.0.12.1+1-jre/bin/java.exe`.

Uruchomić Pythonem KiCad z katalogu pakietu:

```text
python src/run_release.py
```

Domyślnie importuje zapisany `routing/P00.ses`, aby zachować kontrolowane trasy. `--new-route` ponownie wyznacza trasy i może dać inną geometrię; wymaga nowej kontroli wizualnej. `--no-package` wykonuje generowanie, kontrole i eksporty bez ZIP.

Kolejność: schemat → ERC → eksport netlisty → kontrola pinów i warunków pracy → PCB → routing → nadruk → DRC i kontrole PCB → mutacje → PDF i widoki → Gerbery/wiercenia → manifest/ZIP. Kontrole są wiązane hashami z wejściami. Po edycji źródeł odtworzyć pakiet; nie dopisywać samego PASS do raportu.

Footprinty niestandardowe pochodzą z P01/P02, ale są dostarczone w `input/footprints` i sprawdzane przez `input/footprints-sha256.json`. Generator nie czyta sąsiedniego P02. Standardowe footprinty i symbole pochodzą z zadeklarowanego KiCad 10.0.6.

Pełny test czystego odtworzenia polega na rozpakowaniu ZIP bez sąsiednich projektów, usunięciu WYŁĄCZNIE w tej roboczej kopii wygenerowanych EDA/raportów/output oraz przebudowie. Porównać `geometry-fingerprint.json` i wyniki kontroli. Daty raportów oraz losowe UUID nie muszą mieć identycznych bajtów. `verification/clean-rebuild.json` dokumentuje wykonany test wydania.
