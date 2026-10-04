# P11-R2 — przewody (stan schematu, 4.10.2026)

Tabele generuje `src/make_tables.py`: `lista-przewodow.csv` (pola J11 / J8 / J6 na P11 → elementy panelu), `PORTY.csv` (komory portów AT04-12 → płytki docelowe), `BOM.csv` (kolumna `przewod`).

## Na P11

| Pole | Przewody | Drugi koniec |
|---|---|---|
| J_P12 | taśma IDC 2×10, 1,27 mm (AWG28); długość z makiety (szacunek 150–250 mm) | P12 |
| J11 (18 pól) | AWG24 0,25 mm², linka | styki X11–X17 (numery funkcyjne jak R1) |
| J8 (2 pola) | AWG24 | port TEST, komory 10 (LOOP_OUT) i 11 (MECH_OK) |
| J6 (2 pola) | RG174 ok. 100 mm | BNC SCOPE X6 (izolowany) |

## Poza P11 (P11-4, P11-5)

Pozostałe komory portów idą przewodami wprost do płytek — `PORTY.csv`. Prąd silnika (L1.1/L1.2 → P06 J3, TEST.1/TEST.2 → P07) przewodem ≥ 1,0 mm², styki AT 13 A. TAPy trzech portów (L1.3–7, L2.1–5, TEST.5–9) i masa L1.12/L2.12 łączą się przy portach (mostki między miseczkami/zaciskami) i dochodzą jedną wiązką do lutowanych końcówek P05 J4. Dopuszczony jeden adapter naraz (jak w R1).

**Otwarte:** P06 R2 J3 ma 2 × 2,5 mm², a styki AT wielkości 16 przyjmują typowo do 1,0–2,0 mm² (zależnie od styku) — patrz pytania w README.
