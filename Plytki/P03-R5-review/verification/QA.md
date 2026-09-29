# P03-R5 — wyniki weryfikacji 28.09.2026

Status: poprawki CAD gotowe do recenzji. **Sprzęt NIE ZBADANO; brak CAM do produkcji.** Poprzednie raporty są wyłącznie w `reference/previous-verification`.

| Sprawdzenie końcowych plików | Wynik | Raport |
|---|---|---|
| ERC; zgodność 91 części / 430 pinów | 0 naruszeń, 0 różnic | schematic-check.json, erc.json |
| Porównanie bazowej mapy v6.1 | 310 pinów, tylko zatwierdzone zmiany | v61-compare.json |
| Funkcje, pinout i stany domyślne | 53/53; 44/44 mutacje wykryte | function-checks.json, function-mutations.json |
| Natywny DRC / niepołączone / zgodność schematu | 0 / 0 / 0, świeży raport z hashami wejść | drc.json, drc.provenance.json |
| PCB | 30/30 | pcb-checks.json |
| Usterki PCB i próba zerowa | 18/18 usterek wykrytych; próba zerowa czysta | negative-controls.json |
| Zakres R4 → R5 | 10/10, tylko U4 i numer nadruku | revision-checks.json |
| Reset P03/P04 | 7/7; 4/4 mutacje wykryte | reset-budget.json |
| BOM / zakup / interfejsy / netlista | PASS, 430 pinów i 83 zamawiane części | table-checks.json |
| Odtworzenie w pustym katalogu | PASS; CAD, połączenia i reguły zgodne | standalone-rebuild.json, standalone-run.log |
| Ponowny eksport schematu | Nie kasuje reguł PCB/netclass | standalone-rebuild.json |
| Końcowe PDF | 5 stron schematu + 4 strony PCB obejrzane | visual-review.json |
| Źródła poprzednich rewizji | 170 plików P03-R4 + 143 P04-R2.1 bez zmian; mapy drugiej PCB zgodne | source-integrity.json |

## Co dokładnie oznacza zachowanie geometrii

Ścieżki, przelotki, pady, wiercenia, położenia i granice stref są zgodne z R4. Porównanie wypełnionych stref wykonano geometrycznie (XOR), a nie przez kolejność wierzchołków. Dla F.Cu wystąpiła pozostałość numeryczna 2,77125e-8 mm² o maksymalnej grubości 0,214 nm; B.Cu 0. Są to prawie współliniowe trójkąty na siatce nanometrowej, nie przesunięcie ścieżki. Weryfikator wymaga jednocześnie pola ≤1e-6 mm² i grubości każdej pozostałości ≤2 nm. Nie zmieniono reguł DRC. Odtworzenie R5 porównane drugim skryptem spełnia także jego limit XOR 1e-8 mm² na warstwę.

## Granice zaliczenia

Budżet resetu: SUP_N LOW przy VDD=3,0 V ≤0,514 V wobec 0,6 V; wejście P04 przy CORE OFF ≤0,303 V wobec 0,8 V; HIGH ≥2,343 V wobec 2,0 V. Są to obliczenia z założeniami zapisanymi w kontrakcie, nie pomiary. Wejście Schmitta U4 zamyka problem wolnego narastania SUP_RAW_N. Zbocza na odbiorniku P04, zanik zasilania, reset USB i ARM wymagają prób z `docs/ODBIOR.md`.

B2B P03–P05 pozostaje otwarte: `docs/B2B-STATUS.md`. P07 nadal HOLD. Odtworzenie z zapisanej trasy SES nie jest ponownym uruchomieniem losowego autoroutera. Oględziny PDF nie zastępują przymiarki rzeczywistych części.

Odtwarzanie pełnego zestawu: `docs/ODTWARZANIE.md`. Pakowanie odmawia przy zmianie źródeł po odtworzeniu/DRC albo PDF po oględzinach. Nowy BOM zakupowy jest generowany i porównywany automatycznie; nie przenosi starego kodu U4 z R4.
