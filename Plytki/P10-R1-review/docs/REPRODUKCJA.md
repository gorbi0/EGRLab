# Odtworzenie i znaczenie kontroli

Wymagane: KiCad10.0.6 z python/pcbnew i bibliotekami, Python zPIL/numpy;
drugi Python zreportlab/pypdf dla opakowaniaPDF. Windows/Arial. Freerouting2.1.0
i Java21 tylko do nowego trasowania. Do odtworzenia użyć zapisanej `routing/P10.ses`.

Zmienne: KICAD_LIBRARY_ROOT wskazuje katalog KiCad/share/kicad;
KICAD_CONFIG_HOME wskazuje zapisywalny katalog konfiguracji;
EGRLAB_DOC_PYTHON wskazuje Python zreportlab. Opcjonalnie KICAD_CLI.

Uruchomić z katalogu pakietu przez Python KiCad:

```text
python src/run_release.py --rebuild
python src/package_manifest.py
python src/package_manifest.py --check
```

Pierwsza komenda przebudowuje schematy, części/BOM, PCB, importujeSES, kontroluje
połączenia, wypełniaGND i dodaje opisy. Zatrzymuje się na niezgodności. Nie używa
starego wyniku DRC. `--no-pdf` pomija tylko renderPDF. Po zmianie topologii/położeń
SES może być nieaktualna; nowe trasowanie przez `run_layout.py` bez`--reuse-ses`,
z EGRLAB_FREEROUTING ustawionym na katalogjar iJRE. Potem obowiązkowy przegląd.

Źródłowe założenia: `parts.py`, `build_schematic.py`, `placement.json`,
`route_critical.py`, lokalne footprinty/symbole. Niezależne wymagania:
`verify_electrical.py`, `verify_pcb.py` i snapshoty sąsiednich płytek.
`prepare_routing.py` sprawdza reguły w rzeczywistym DSN:0,30/0,25 i via0,8/0,4 mm.
To zapobiega niezauważonemu użyciu domyślnych reguł eksportera Python.

Odtworzenie czyste: do nowego katalogu skopiować wyłącznie src,input,reference,
requirements i routing/P10.ses + completion-routes.json. Utworzyć puste eda,docs,
verification,output/pdf,routing. Uruchomić `run_release.py --rebuild --no-pdf`.
Porównać oba pliki kicad_sch bajtowo i geometry-fingerprint.json semantycznie.
UUID PCB są losowe; zgodność pliku PCB bajt w bajt nie jest właściwym kryterium.

Po nowymPDF wyrenderować wszystkie strony Popplerem i obejrzeć schemat, ramkę,
oznaczenia złączy, miedź, rozmieszczenie i skalę. `drc.provenance.json` wiąże DRC
ze skrótami użytych źródeł, a manifest obejmuje cały wydany pakiet.
Manifest tworzyć po końcowych raportach; nie włączać go do własnego haszowania.

Testy mutacji operują na modelu odczytanym z XML/PCB. Sprawdzają, czy walidator wykrywa
określone regresje, nie zastępują analizy datasheet ani testu dowolnego uszkodzenia.
Domyślne pomijane kategorie KiCad są ujawnione w DRC/ignored_checks. Projekt nie
zawiera wyłączeń pojedynczych naruszeń. Wynik0 nie jest dowodem odporności EMC.
