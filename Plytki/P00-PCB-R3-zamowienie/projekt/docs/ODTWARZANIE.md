# P00-R3 — samodzielne odtwarzanie

Pakiet nie wymaga żadnej innej płytki EGRLab. Potrzebne są: Windows, KiCad 10.0.6 z Pythonem `pcbnew`, Pillow i numpy oraz Python z ReportLab i Pillow (może być ten sam). Czcionka Arial pochodzi z Windows. Poppler (`pdftoppm`) jest opcjonalny i generuje PNG kontrolne. Nie zmieniać zainstalowanego toolchainu.

Zmienne środowiskowe (ścieżki lokalne):

- `KICAD_LIBRARY_ROOT`: katalog `share/kicad` z bibliotekami KiCad 10.
- `KICAD10_3DMODEL_DIR`: opcjonalny inny katalog modeli; domyślnie `3dmodels` pod `KICAD_LIBRARY_ROOT`. Korpusy i kolory są poglądowe.
- `KICAD_CLI`: `kicad-cli.exe`; domyślnie obok użytego Pythona KiCad.
- `EGRLAB_DOC_PYTHON`: Python z ReportLab i Pillow.
- `PDFTOPPM`: opcjonalna ścieżka do `pdftoppm.exe`.
- `EGRLAB_FREEROUTING`: tylko dla `--new-route`; katalog z `freerouting-2.1.0.jar` i `jdk-21.0.12.1+1-jre/bin/java.exe`.

Uruchomić Pythonem KiCad z katalogu pakietu:

```text
python src/run_release.py --no-package
python src/package_release.py
```

Domyślnie importowany jest zapisany `routing/P00.ses` (ten sam co w R2), więc trasy zostają kontrolowane. `--new-route` wyznacza trasy od nowa i może dać inną geometrię; to wymaga nowej recenzji layoutu. Pakowanie odmawia pracy, jeśli `verification/pdf-visual-review.json` nie wskazuje dokładnie tych PDF (SHA256), które mają trafić do archiwum. Kontrolę wzrokową trzeba więc zrobić po wygenerowaniu PDF.

Kolejność: schemat → ERC → eksport netlisty → kontrola pinów → warunki pracy (`verify_electrical.py`) → wiązka do P04-R2.1 (`check_harness.py`) → PCB z SES → nadruk → DRC i kontrole PCB → próby ujemne (z próbą zerową) → odcisk geometrii → zakres R2 → R3 (`check_revision.py`) → PDF i widoki → Gerbery i wiercenia → manifest i ZIP.

Zagłodzone termiki rozpoznaje się po UUID z raportu DRC, więc wynik nie zależy od języka interfejsu KiCada. W R2 skrypt szukał polskich słów („Pole PTH”); P00 i tak nie ma zagłodzonych termików. Kopie w próbach ujemnych dostają tabelę bibliotek wskazującą biblioteki wydania, dlatego ich DRC jest czysty, dopóki nie zepsuje go sama wada.

Footprinty niestandardowe są w `input/footprints`, sprawdzane przez `input/footprints-sha256.json`. Standardowe footprinty i symbole pochodzą z KiCad 10.0.6. `check_revision.py` porównuje płytkę z zamrożonym `reference/R2.kicad_pcb`. Jeśli obok leży pakiet `P00-R2-review`, sprawdza też, że jest nienaruszony.

Test czystego odtworzenia: skopiować pakiet bez wygenerowanych EDA, raportów i `output/` do innego katalogu i uruchomić `run_release.py --no-package`. Porównać `verification/geometry-fingerprint.json` i wyniki kontroli. Daty raportów i losowe UUID nie muszą mieć identycznych bajtów. `verification/clean-rebuild.json` dokumentuje test wykonany dla tego wydania.
