# EGRLab P03-R2 — CORE

26.09.2026 · nowa rewizja po recenzji P03-R1. **Pakiet do niezależnej recenzji, bez zatwierdzenia do produkcji.** R1 pozostaje bez zmian.

Start: `docs/ZMIANY-R2.md` (siedem uwag i sposób ich zamknięcia), `docs/ODBIOR.md` (pomiary przed integracją).

- CAD: `eda/P03.kicad_pro`, `eda/P03.kicad_sch` + cztery arkusze podrzędne, `eda/P03.kicad_pcb`.
- PDF: `output/pdf/P03-R2-schemat.pdf` — pięć arkuszy A3; `output/pdf/P03-R2-PCB.pdf` — montaż i obie warstwy 1:1.
- Zakupy: `docs/BOM.csv` (każda pozycja), `docs/zakupy.csv` (ilości), `docs/wiazki-BOM.csv`.
- Połączenia: `docs/netlist-pinowa.csv`, `docs/interfejsy.csv`, `docs/STANY-DOMYSLNE.csv`.
- Sprawdzenia: `verification/QA.md`, raporty JSON, `src/verify_function.py`, `src/verify_pcb.py` oraz próby ujemne.
- Odtwarzanie: `docs/ODTWARZANIE.md`; nie wymaga sąsiedniego P02 ani plików innych rewizji.

Nie wytworzono Gerberów. Przymiarka P03–P05, testy resetu/USB/SD oraz odbiór oscyloskopem pozostają niewykonane. P07 nadal HOLD do sprawdzenia kupionego modułu BTS7960. Problemy integracyjne firmware zgłoszone w P05 (start AD7606B i czas ramki SPI) nie są zamknięte tą rewizją CORE.
