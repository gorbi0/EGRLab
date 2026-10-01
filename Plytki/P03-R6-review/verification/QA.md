# P03-R6 — wyniki weryfikacji 30.09.2026 (etap schematu, po poprawkach z recenzji PR #6)

Status: schemat do recenzji lokalnej. **Bez PCB, bez CAM, sprzęt NIE ZBADANO.** Łańcuch: `src/run_schematic.py` (KiCad 10.0.6; 29.09 obraz Docker w chmurze, 30.09 lokalnie po zmianach: R43 100 kΩ, trzecia żyła 5V_SYS na J_BP2.17, PFAIL_N na 16, ADC_RESET na 18, wszystkie R i C w 1206).

| Sprawdzenie | Wynik | Raport |
|---|---|---|
| ERC | 0 naruszeń, 6 arkuszy | erc.json |
| Netlista pin po pinie z `parts.py` | 122 części, 511/511 pinów, 152 sieci | schematic-check.json |
| Mapa v6.1 | 310 pinów; 8 różnic udokumentowanych (R2/R4), 0 nieoczekiwanych | v61-compare.json |
| Funkcje, stany domyślne, zasilanie, reset | 53/53; mutacje 44/44 | function-checks.json, function-mutations.json |
| Budżet resetu P03/P04 + szacunek zbocza R6 | 8/8; mutacje 4/4 | reset-budget.json |
| J_BP (C0–C5), PFAIL_N (C6–C7), listwy serwisowe (C8–C11) | 12/12; 24/24 próby ujemne + próba zerowa | jbp-checks.json, jbp-negative-controls.json |
| Tabele: BOM, zakupy, netlista, J_BP.csv, SERWIS.csv, reguła montażu (wszystkie R i C w 1206, jeden kod 100 nF) | PASS | table-checks.json |

Kolejność recenzji: README (przesunięcia grup, PFAIL_N, zbocze SUP_N_OUT) → `docs/J_BP.csv` → arkusze LINKS i SERWIS w PDF → `jbp-checks.json` → ODBIOR.
