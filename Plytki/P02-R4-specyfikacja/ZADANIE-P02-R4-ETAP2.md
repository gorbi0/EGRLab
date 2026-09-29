# P02 R4, etap 2 — PCB (zadanie dla sesji w chmurze, 29.09.2026)

**Źródła:**
- pakiet `Plytki/P02-R4-review` (etap 1 scalony w PR #2);
- recenzja `Plytki/P02-R4-recenzja/RECENZJA-P02-R4-ETAP1.md`;
- `SPECYFIKACJA-P02-R4.md`: Z-13, Z-15, sekcja 6 (złącza);
- łańcuch PCB z `Plytki/P02-R3-review/src`: `build_board.py`, `run_layout.py`, `route_critical.py`, `negative_controls.py`, `verify_pcb.py`, `make_pdf_r2.py`, `package_review.py`.

**Pamięć:** `kicad-pipeline-quirks.md`, `p02-r1-state.md`, `p01-pcb-r1-review.md`, `pcb-fab-satland.md`.

**Ustawienia sesji:** Opus 5.5, wysiłek high. Gałąź `p02-r4-pcb`. Pakiet `Plytki/P02-R4-review` pozostaje otwarty do końca etapu 2.

## Praca równoległa

Równolegle działa sesja P05 R2 (gałąź `p05-r2`).

**Nie zmieniać plików wspólnych:**
- `EGRLab-AKTYWNE.md`;
- `docs/01-overview.md`;
- `docs/CHMURA.md`;
- `docs/pamiec-claude/`;
- `scripts/`;
- `.gitignore`.

Wolno zmieniać `Plytki/P02-R4-review/` i `Plytki/P02-R4-specyfikacja/STAN-PRAC.md`. Środowisko przygotować przez `bash scripts/setup-chmura.sh`.

## Zakres

1. **Schemat po recenzji (osobny commit):**
   - D3: 5KP18A → 5KP24A (obudowa P600, footprint bez zmian).
   - J15: w opisie BOM bezpiecznik przy klemie 1 A.
   - Kontrolę T14 rozszerzyć o Z-01: VBR min transila na VSW ≥ 25 V. Dodać próbę ujemną z 5KP18A.
   - Tabelę QA „Zgodność ze specyfikacją” przepisać według nowego brzmienia Z-02 i Z-08 (sekcja 4 specyfikacji).
   - Powtórzyć ERC, netlistę, `check_electrical` i próby ujemne.
2. **PCB:**
   - **Mechanika:** obrys ≤ 115 × 85 mm, 4 × M3 do płyty nośnej, THT, 2 warstwy, miedź 35 µm, wysokość z wtykami ≤ 35 mm (Z-15).
   - **Reguły produkcyjne:** jak P02-R3 (Satland), pierścień PTH i przelotek ≥ 0,25 mm.
   - **Tory 5 A:** J1 → Q9 → SW_COM → Q1 → VSW → F1 → J2 oraz powrót GND. Szerokie ścieżki albo wylewki. Przyrost temperatury przy 5 A ≤ 20 K według IPC-2152 dla 35 µm, liczony w `verify_pcb.py`.
   - **Tranzystory TO-220:** Q1, Q9 i Q2 bez radiatorów (Z-13). Blaszka TO-220 to dren, więc miedź pod blaszką i przy niej tylko z sieci drenu (lekcja z P01 PCB R1). Orientacja tranzystorów na opisie.
   - **Odsprzęganie przy pinach:**
     - C2/C4 przy Q1/Q2;
     - C8/C10 przy U1;
     - C11 przy U2;
     - C13 przy R12/U2;
     - C25–C29 przy U7–U10;
     - C21–C24 przy TSR;
     - C_H, D2 i D1 blisko siebie.
   - **Złącza i punkty testowe:** złącza przy krawędziach, zgodnie z kierunkami wiązek. TP1–TP17 dostępne od góry.
   - **Trasowanie:** tory krytyczne skryptem, resztę przez Freerouting, jak w R3.
3. **Kontrole:**
   - DRC 0/0/0.
   - `verify_pcb.py`: szerokości torów mocy, odległości odsprzęgania, blaszki TO-220 na własnej sieci, otwory M3, wymiary.
   - Próby ujemne z próbą zerową, np. przewężenie toru 5 A, odsunięty kondensator, blaszka Q1 na obcej miedzi.
   - PDF: warstwy, montaż, wydruk 1:1 do przymiarki.
4. **Poza zakresem:** paczka produkcyjna i zamówienie. Zrobi je sesja lokalna po recenzji.

## Wynik

PR po polsku, a w nim:
- wymiary i rozmieszczenie;
- wyniki kontroli z liczbami;
- podgląd płytki;
- lista otwartych punktów.

Pytania wpisać do opisu PR. Nie włączać śledzenia PR.
