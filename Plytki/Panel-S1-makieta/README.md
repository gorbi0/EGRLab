# Makieta panelu S1 (wariant LOGGER) — 4.10.2026

Decyzja użytkownika 4.10 (P11-6): rysunek makiety 1:1. Obudowa nie jest jeszcze wybrana (użytkownik kupi ją na końcu, po wymiarach całego pakietu), więc makieta wychodzi z geometrii stosu S1, a nie z obudowy.

**Do druku:** `MAKIETA-PANELU-S1.pdf`, A4 poziomo, skala 100 %:
1. panel od zewnątrz 1:1 — obrysy zajętego miejsca i środki otworów (3 × AT04, STOP, kluczyk, ARM, MARK, 2 × BNC, AUX HI/LO, BYPASS, PWR + LED), rzut płytek stosu i oś SW1 P05, belka 100 mm;
2. widoki stosu z góry i z boku 1:2 ze strefą panelu 50 mm, P12 i wyjściami przewodów z P05 / P06;
3. wniosek i założenia.

Odtworzenie: `python3 Plytki/Panel-S1-makieta/src/makieta.py` (matplotlib).

## Wniosek — do decyzji użytkownika

Tuleja SW1 na P05 (E-Switch 100 M6, 7,1 mm) wystaje za krawędź płytki tylko ok. 3,7 mm. Żeby przechodziła przez panel, panel musiałby stać ≤ 1 mm od stosu. Wtedy za panelem nie ma miejsca na porty, przyciski, kluczyk ani P11, przewody z P05 / P06 nie mają kanału, a tuleja B3 nie zmieści nakrętki.

**Rekomendacja:** SW1 jako przełącznik na panelu (ten sam DPDT ON-ON, wersja z oczkami), 5 przewodów do otworów footprintu SW1 na P05 (1, 2, 3, 5, 4 = GND; pin 6 wolny). Płytka P05 i jej paczka zamówieniowa bez zmian. Panel 50 mm przed stosem (strefa P11, przycisków i przewodów).

## Założenia

- Stos LOGGER z `Plytki/Format-S1/format-s1.json`: płytki na z = 8,0 / 34,6 / 56,2 / 77,8 mm, wnętrze ok. 99 mm wysokości.
- Szerokość wnętrza 140 mm: ściana A 30 mm przed krawędzią A (P12 + taśmy), ściana B 10 mm za krawędzią B.
- Obrysy i otwory elementów są typowe dla klasy części; po wyborze kodów (zadanie Zakupy-4) podmienić w `src/makieta.py`.
- **NIE ZBADANO:** przymiarka z częściami, długości wiązek, ciepło.
