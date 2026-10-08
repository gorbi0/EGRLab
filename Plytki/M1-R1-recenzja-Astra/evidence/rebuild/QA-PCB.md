# M1-R1 — QA PCB (plik generowany przez src/run_release.py)

DRC (świeży, wszystkie poziomy): naruszenia 0, niepołączone 0, niezgodności ze schematem 0 (naruszenia to wyłącznie lib_footprint_mismatch części z przyciętym nadrukiem, przyjęte przez verify_pcb.py; szczegóły w pcb-checks.json).
Kontrole PCB: 11/11. Próby ujemne: 13/13 (w tym próba zerowa).

| Kontrola | Wynik |
|---|---|
| DRC: 0 naruszen (poza lib_footprint_mismatch po przycieciu nadruku), 0 niepolaczonych, 0 niezgodnosci ze schematem | PASS |
| Obrys 150 x 80 mm, 4 warstwy miedzi, 4 otwory M3 w narozach | PASS |
| Pola przewodow X1 w jednym rzedzie przy gornej krawedzi, w kolejnosci zaciskow, sieci jak docs/X1.csv, kotwy opasek nad polami | PASS |
| Dolna krawedz: gniazdo SD, USB-C modulu i zaciski termopar <= 1,5 mm od krawedzi | PASS |
| Antena ESP32: brak miedzi w strefie ANTENNA M1 (sciezki, przelotki, wylewki) | PASS |
| Tor 7,5 A: wylewki F.Cu laczace J1.1-F1.1, F1.2-J2.1, J5.1-RSH1.1, RSH1.4-J5.2; wylewki B.Cu; >= 2 przelotki zszywajace na siec | PASS |
| Para Kelvina tylko z miedzi zablokowanej (route_critical.py) | PASS |
| Brak obcej miedzi routera przy boczniku, parze Kelvina i wewnatrz U3 (check_intrusion.py) | PASS |
| Sciezki zasilan (PWR) routera >= 0.5 mm | PASS |
| Powroty odsprzegania w limicie (return_check.py) | PASS |
| Nadruk: napisy plytki umieszczone; oznaczenia bez miejsca (<= 10 %) na rysunku montazowym z F.Fab | PASS |

## Próby ujemne

| Wada | Oczekiwana kontrola | Wykryta | Zgłoszone |
|---|---|---|---|
| DRC: jedno naruszenie clearance | DRC | tak | 1 |
| Brak otworu M3 | Obrys | tak | 1 |
| Pola X1.7 / X1.8 zamienione | Pola przewodow | tak | 1 |
| Gniazdo SD 3 mm od krawedzi | Dolna krawedz | tak | 1 |
| Przelotka w strefie anteny | Antena | tak | 1 |
| P1_EGR rozciete na F.Cu | Tor 7,5 A | tak | 1 |
| VBUS bez przelotek zszywajacych | Tor 7,5 A | tak | 1 |
| Odcinek routera na K_MINUS | Para Kelvina | tak | 1 |
| Obca sciezka przy boczniku | Brak obcej miedzi | tak | 1 |
| 5V sciezka 0,3 mm | Sciezki zasilan | tak | 1 |
| Powrot kondensatora za dlugi | Powroty | tak | 1 |
| Napis plytki bez miejsca | Nadruk | tak | 1 |
| proba zerowa (kopia bez zmian) | - | tak | 0 |

Nadruk: ukryte oznaczenia (brak miejsca): R32, C12, C29, C14; nieumieszczone napisy: brak.

Oględziny PDF: wpis ręczny w README (sekcja „PCB”); render stron w output/previews/pcb-*.png.
