# Odtwarzanie pakietu (P03-R6, etap schematu)

Wymagane: KiCad 10.0.6 (`kicad-cli`, biblioteki symboli/footprintów), Python KiCada, Poppler (`pdftoppm`) do podglądów. W chmurze: `bash scripts/setup-chmura.sh`, potem w katalogu pakietu `../../scripts/egrlab-docker python3 src/run_release.py`. Lokalnie (Windows): Python KiCada, `python src/run_release.py`; zmienne `KICAD_CLI`, `KICAD_LIBRARY_ROOT`, `PDFTOPPM` jak w R5.

`run_release.py` regeneruje schemat, ERC, netlistę, kontrole (`verify_schematic`, `compare_v61`, `verify_function`, `verify_reset`, `verify_jbp`), tabele (`write_tables.py`), kontrolę krzyżową tabel i PDF. Czas w chmurze ok. 30 s. PCB, manifest i ZIP powstaną w etapie layoutu (sesja lokalna).

Pinout krawędzi A zmienia się tylko w `src/jbp_pinout.py`, listwy serwisowe w `src/serwis_pinout.py`. Kontrola `verify_jbp.py` ma własne klasy sygnałów, listę wyjątków i zakazanych pinów modułu — po świadomej zmianie pinoutu trzeba je poprawić osobno (to celowe).
