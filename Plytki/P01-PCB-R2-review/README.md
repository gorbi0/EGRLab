# EGRLab P01 - PCB R2, do recenzji

Druga rewizja layoutu P01: **dwie warstwy, 160 × 120 mm**, zamrożony schemat P01-R3.
R2 poprawia uwagi PCB1-01…06 z recenzji PCB R1 (`Plytki/P01-PCB-R1-recenzja/`).
Przygotował Claude 24.09.2026, recenzuje Astra.
Status: **LAYOUT SPRAWDZONY; PRZYMIARKA I SPRZĘT NIE ZBADANE**.

## Od czego zacząć recenzję

- `docs/ZMIANY-R2.md` — każda uwaga R1 → zmiana → dowód, liczby R1/R2 i lista punktów
  do krytycznego sprawdzenia (tam są decyzje sporne).
- `output/pdf/P01-PCB-R2-dokumentacja.pdf` — podsumowanie, montaż 1:1, F.Cu 1:1 z obszarami
  bez miedzi pod radiatorami, B.Cu 1:1.
- `eda/P01.kicad_pro` — projekt KiCad 10; schemat i PCB z lokalnymi bibliotekami.
- `verification/QA.md` — wyniki kontroli i komendy do powtórzenia.
- `docs/LAYOUT.md`, `docs/MECHANIKA.md` — stan R2 w całości (decyzje, tor mocy, przymiarka).
- `docs/ZAKUPIONE-CZESCI.md` — części już zamówione a footprinty R2; odchyłka R8.
- `docs/BOM.csv`, `docs/BOM-MECHANIKA.csv` — BOM R3 bez zmian.

Schemat, wartości, footprinty i pady R3 nie zostały zmienione. Wymiar, otwory M3,
radiatory, D2/Q1, złącza mocy i LK1 stoją jak w R1, więc przymiarka obudowy z R1
obowiązuje dalej. Zmieniło się rozmieszczenie drobnych elementów, C6 (teraz we wnęce
HS2) i kierunek wyjścia wiązki J5.

## Następny krok przy stole

Wydrukuj stronę 2 PDF w skali **100%, bez dopasowania**, zmierz belkę 100 mm i przyłóż
rzeczywiste radiatory, Q1/D2, C6, J6 oraz przewody z opaskami. Szczególnie: C6 i dojście
sondy do TP1/TP2 we wnęce HS2. Wynik wpisz w `docs/MECHANIKA.md`. Po przymiarce
i recenzji R2 można wykonać eksport produkcyjny. **W tym pakiecie nie ma Gerberów**,
zgodnie z bramką przymiarki z R3.

Części do P01 są już zamówione (TME, Mouser; rejestr w `Zamowione/`). Nie zamówiono PCB.

Potem montaż i niezależny odbiór P01 według `reference/R3-docs/ODBIOR.md` oraz
`METROLOGIA.md`; dopiero następnie integracja P02-HOLD. Czysty DRC nie potwierdza
SOA, termiki, dynamiki zabezpieczenia ani odporności na impulsy samochodowe.

## Granice pakietu

Pliki w `reference/` dokumentują R3; ich stare 160 × 100 mm i status „layout niewykonany”
nie opisują tej PCB. Dokumentacja bieżąca jest w `docs/`. P01-R3 i firmware nie są zmieniane.
**P07 nadal HOLD do sprawdzenia fizycznego modułu BTS7960.**

Końcowym źródłem PCB jest `eda/P01.kicad_pcb`. Skrypty w `src/` zapisują przebieg pracy;
kolejność przebiegu R2 jest w `verification/QA.md`. Skrypty R1, których R2 nie uruchamia,
zostały jako odniesienie: `build_board.py`, `pack_placement.py`, `nudge_placement.py`,
`placement.json`, `route_critical.py`, `repair_kelvin.py`, `add_legends.py`, `make_pdf.py`,
`normalize_svg.py`, `simplify_outlines.py`, `prepare_libraries.py`.
