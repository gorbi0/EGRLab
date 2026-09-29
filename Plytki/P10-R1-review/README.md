# EGRLab P10 CAN / R1 — pakiet do recenzji

Pasywny odbiornik CAN dla EGRLab: TCAN1051VDRQ1 + PESD2CAN + bufor RX z Ioff.
PCB 80×70 mm, dwie warstwy, FR4 1,6 mm, Cu35 µm. **Sprzęt NIE ZBADANO.**

Zacznij od `docs/DLA-RECENZENTA.md`. Schemat natywny: `eda/P10.kicad_pro` (KiCad10.0.6),
główny arkusz `P10.kicad_sch`, drugi `CORE.kicad_sch`. PCB: `eda/P10.kicad_pcb`.
PDF: `output/pdf/P10-R1-schemat.pdf` i `P10-R1-PCB.pdf` (montaż i obie warstwy1:1).

Układ służy obserwacji ramek. Nie nadaje, nie potwierdza ACK i nie wysyła zapytań OBD.
Obroty silnika wymagają potwierdzonego źródła danych. Nie ma terminatora120 Ω.
P10 nie jest izolowana galwanicznie. Masa przez główne zasilanie EGRLab; W3 zawiera H/L.

Zakupy i wiązki: `docs/ZAKUPY.md`, `docs/WIAZKI.md`, `docs/interfejsy.csv`.
Budowa i odbiór: `docs/MONTAZ.md`, `verification/ODBIOR.md`.
Zależności firmware: `docs/INTEGRACJA.md`.
Regeneracja: `docs/REPRODUKCJA.md`. Wyniki: `verification/QA.md`.

Ta rewizja nie zmienia wcześniejszych płytek ani wspólnego firmware. P07 pozostaje HOLD
dla alternatywnego modułu BTS7960. Gerberów nie wydano; wydanie produkcyjne po recenzji
i przymiarce wiązek/obudów. Testy CAD nie zastępują prób elektrycznych.
