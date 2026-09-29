# P04 SAFE — R2.2

28.09.2026. Korekta integracji z P03-R5 po recenzji P03-R4.
**R17: 100 kΩ -> 10 kΩ / 1%, MFR-25FRF52-10K.** To jedyna zmiana elektryczna P04 względem R2.1. Piny, footprinty, miedź i wiercenia zachowane; numer nadruku R2.2. Nie trzeba zmieniać PCB już wykonanej według R2 — wystarczy zastosować nową wartość R17.

Start: [zmiany R2.2](docs/ZMIANY-R2.2.md), [kontrakt resetu](docs/KONTRAKT-RESET.md), [odbiór](docs/ODBIOR.md). BOM: `docs/BOM.csv`. Projekt: `eda/P04.kicad_sch`, `eda/P04.kicad_pcb`.

PDF: `output/pdf/P04-R2.2-schemat.pdf` (6 arkuszy), `output/pdf/P04-R2.2-PCB.pdf` (4 strony). Wyniki: `verification/QA.md`. Odtworzenie: `docs/ODTWARZANIE-R2.2.md`.

Korekta generuje nowe CAD/PDF i kontrole, nie zmienia oryginalnego R2.1. Historia wcześniejszego zamknięcia w `docs/ZAMKNIECIE-P04.md`; obecnie obowiązują R2.2 i rozszerzone próby resetu. Przymiarka M01 i próby na stole nadal NIE ZBADANO. Brak CAM do zamówienia. P07 HOLD.
