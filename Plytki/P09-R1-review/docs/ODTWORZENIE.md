# Odtworzenie pakietu

Referencyjnie użyto KiCad 10.0.6 oraz jego Python 3.11 z `pcbnew`, NumPy i Pillow. PDF montażu opakowuje ReportLab. Biblioteki części są lokalne w `eda/libraries`; otwarcie projektu nie wymaga generowania plików. Budowa schematu wymaga pełnych standardowych bibliotek KiCad wskazanych przez `KICAD_LIBRARY_ROOT`.

Zmienne: `KICAD_LIBRARY_ROOT` = katalog `share/kicad`; `KICAD_CONFIG_HOME` = zapisywalny katalog konfiguracji; `KICAD_CLI` = program kicad-cli; `EGRLAB_DOC_PYTHON` = Python z ReportLab. Skrypty uruchamiać interpreterem mającym `pcbnew`.

```text
python src/run_release.py --rebuild
python src/package_manifest.py --create
python src/package_manifest.py --check
```

`--rebuild` tworzy schemat i PCB od nowa, odtwarzając zatwierdzony `routing/P09.ses`. Nie wymaga internetu ani Freerouting. Projekt `.kicad_pro` powstaje przed ERC. Skrypt przeprowadza eksport natywnej netlisty, ERC, porównania pinów, niezależne testy elektryczne, odtwarza ścieżki krytyczne i SES, kontroluje PCB i spójność wylewek, uruchamia świeży DRC z porównaniem PCB/schemat, zapisuje odcisk geometrii i oba PDF. `--no-pdf` pomija tylko dokumenty.

Nowe trasowanie: `python src/run_layout.py` bez `--reuse-ses`, z `EGRLAB_FREEROUTING` wskazującym Freerouting 2.1.0 i JRE21. Jest to generator kandydata; wymaga ponownej kontroli całej płytki. Nie porównywać nowego routingu tylko liczbą przelotek. Odtwarzanie przejrzanego SES jest stabilniejsze od kolejnego losowego trasowania.

Raporty: `schematic-check.json`, `electrical-checks.json`, `pcb-checks.json`, `ground-islands.json`, `drc.json`, `drc.provenance.json`, `geometry-fingerprint.json`. Kontrole negatywne zmieniają kopie danych w pamięci, nigdy pliki finalnej PCB.

Po zmianach trzeba obejrzeć każdą stronę obu PDF. Ewentualna odbudowa może zmienić techniczne UUID; geometria, połączenia, opisy i wartości muszą się zgadzać. `board_fingerprint.py` porównuje semantykę płytki. `package_manifest.py` kontroluje hash każdego pliku oraz niedozwolone nazwy Windows.

Gerbery nie są częścią pakietu do recenzji. Powstają z zaakceptowanej PCB po sprawdzeniu dopasowania rzeczywistych części do wydruku 1:1.

Dodatkowo EGRLAB_TCC wskazuje kompilator TinyCC do testu rzeczywistej funkcji temperatury. Hostowy nagłówek matematyczny w teście jest minimalny z uwagi na ograniczenia Windows TCC. Test nie podmienia logiki funkcji produkcyjnej.
