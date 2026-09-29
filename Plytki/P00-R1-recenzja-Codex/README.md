# Recenzja P00-R1

Pełna ocena: **RECENZJA-P00-R1.md**. To pakiet recenzji, nie poprawiona PCB R2 ani pliki produkcyjne.

Werdykt: zachować layout, poprawić warunki pracy LM2937 i dobór C6 przed zamówieniem. Przed testami P04 domknąć mapę wiązki i procedurę pomiarów. Naprawić zależność generatora od katalogu P02-R1.

Odtworzone kontrole gotowych artefaktów: ERC 0, DRC 0/0/0, 141/141 pinów, 22/22 sprawdzeń PCB, 8/8 wykrytych mutacji. Sprzętu nie mierzono. Pierwszy krok regeneracji bez sąsiedniej P02-R1 kończy się błędem; nie deklarujemy pełnej regeneracji wydania.

- `evidence/`: nowe raporty z uruchomienia kontroli na kopii, świeża netlista oraz wersje/hashes wejść w raporcie provenance.
- `analyse_operating_points.py`: niezależny od generatora odczyt netlisty i obliczenia; uruchomienie: `python analyse_operating_points.py`.
- `operating-points.json`: wynik obliczeń z jawnymi założeniami; nie symulacja ani pomiary.
- `P04-contract.json`: odczyt elementów i pinów P04 v6.1-rc1 użyty do sprawdzenia interfejsu.
- `rebuild-probe.log`: odtworzony błąd pierwszego kroku generatora w izolowanym katalogu.
- `manifest-check.json`: zgodność 84 plików oryginalnego wydania z jego manifestem.
- `source-sha256.json`, `original-integrity.json`: kontrola 134 plików oryginału przed i po recenzji, bez zmian.
- `review-manifest.json`: hashe tego pakietu recenzji, osobne od manifestu projektu.

Numery linii w recenzji odnoszą się do niezmienionego P00-R1-review z 25.09.2026. Dokument zawiera linki do źródeł producentów i rozdziela wymagane poprawki od punktów odbioru sprzętu.
