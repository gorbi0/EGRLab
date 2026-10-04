# P11-R2 — przewody (stan schematu, 4.10.2026)

Tabele generuje `src/make_tables.py`: `lista-przewodow.csv` (pola J11 / J8 / J6 na P11 → elementy panelu), `PORTY.csv` (komory portów AT04-12 → płytki docelowe), `BOM.csv` (kolumna `przewod`).

## Na P11

| Pole | Przewody | Drugi koniec |
|---|---|---|
| J_P12 | taśma IDC 2×10, 1,27 mm (AWG28) z gniazda kątowego na krawędzi P11 od strony ściany A; długość z makiety | P12 |
| J11 (18 pól) | AWG24 0,25 mm², linka | styki X11–X17 (numery funkcyjne jak R1) |
| J8 (2 pola) | AWG24 | port TEST, komory 10 (LOOP_OUT) i 11 (MECH_OK) |
| J6 (2 pola) | RG174 ok. 100 mm | BNC SCOPE X6 (izolowany) |

## Poza P11 (P11-4, P11-5)

Pozostałe komory portów idą przewodami wprost do płytek — `PORTY.csv`. Prąd silnika (L1.1/L1.2 → P06 J3, TEST.1/TEST.2 → P07): **przewód 2,0 mm² (AWG14) na całej długości**, styki złocone **AT60-215-1631** (pin, w porcie) / **AT62-209-1631** (gniazdo, we wtyku adaptera) — decyzja 4.10. P11 nie przenosi tego prądu. TAPy trzech portów (L1.3–7, L2.1–5, TEST.5–9): odpowiadające sobie TAPy łączą mostki przy portach, dalej **jedna wiązka 5 par do P05 J4**; masa z komory 12 (L1.12/L2.12) do GND na P05 J4 — przyjęte 4.10. Dopuszczony jeden adapter naraz (jak w R1).

Klucze portów jak w R1 (decyzja 4.10): L1 = B, L2 = C, TEST = A (AT04-12PB / PC / PA).

P06 R2 J3 ma pola na 2 × 2,5 mm²; przewód 2,0 mm² lutuje się w nie (pasowanie otworu sprawdzić przy montażu).
