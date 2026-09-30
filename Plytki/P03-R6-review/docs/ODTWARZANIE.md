# Odtwarzanie pakietu (P03-R6: schemat i PCB)

Wymagane: KiCad 10.0.6 (`kicad-cli`, biblioteki symboli/footprintów), Python KiCada, Poppler (`pdftoppm`) do podglądów, do PDF-u PCB `reportlab`, do rastrów `node` z `sharp` (zmienne `EGRLAB_PDF_PYTHON`, `EGRLAB_NODE`, `EGRLAB_SHARP`, `PDFTOPPM` jak w P02 R4). Nowe trasowanie: Freerouting 2.1.0 (`EGRLAB_FREEROUTING`).

- `src/run_schematic.py` — etap schematu: schemat, ERC, netlista, kontrole (`verify_schematic`, `compare_v61`, `verify_function`, `verify_reset`, `verify_jbp`), tabele (`write_tables.py`), kontrola krzyżowa tabel, PDF schematu. W chmurze: `../../scripts/egrlab-docker python3 src/run_schematic.py` (ok. 30 s).
- `src/run_release.py` — całość (lokalnie): etap schematu, layout (`run_layout.py`, domyślnie odtwarza zapisany wynik routera `routing/P03.ses` i trasy dokańczające `routing/completion-routes.json`), nadruk, kontrole PCB (`verify_pcb.py`), próby ujemne, widoki, PDF PCB, `verification/QA-PCB.md`, manifest. `--new-route` uruchamia Freerouting od nowa (wynik za każdym razem inny).

Łańcuch layoutu (`run_layout.py`): `placement.py` (osobno, zapisuje `src/placement.json`) → `build_board.py` → `set_stackup.py` → `set_rules.py` → `route_critical.py` (zablokowany tor 5 V, eksport DSN) → `prepare_routing.py` (paski przy krawędziach, GND poza listą sieci routera) → Freerouting → `import_routing.py` (+ wylewki GND) → `stitch.py` → `complete_routes.py` → `cleanup.py` → DRC.

Pinout krawędzi A zmienia się tylko w `src/jbp_pinout.py`, listwy serwisowe w `src/serwis_pinout.py`. Kontrola `verify_jbp.py` ma własne klasy sygnałów, listę wyjątków i zakazanych pinów modułu — po świadomej zmianie pinoutu trzeba je poprawić osobno (to celowe). Kontrole PCB (`verify_pcb.py`) czytają kontrakty `docs/J_BP.csv` i `docs/SERWIS.csv`, nie skrypty rozmieszczenia.
