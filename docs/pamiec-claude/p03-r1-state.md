---
name: p03-r1-state
description: "P03 CORE: R1 (Claude 25.09) → R2 Astry → moja recenzja + R3 zamykająca (miedź = R2) → R4 (Claude 27.09, bufor Schmitta U6 do P04, miedź = R3 + zmiana przy J4, zip 36d73f76); czeka na recenzję layoutu"
metadata:
  node_type: memory
  type: project
  originSessionId: 1bdb3685-394a-4886-bbc7-14b9957d5ea4
  modified: 2026-09-27T15:44:43.440Z
---

R1 mój (`Plytki/P03-R1-review`: ESP32-S3 Waveshare N32R16V, 4682, MCP23017, HC139, TPS3808 na PA0085, 7 × LVC125A na SO14; decyzje użytkownika 25.09: listwy 22,86 mm, P05 obok z kątowym B2B J1, CAN IDC 2×3). Astra zrecenzowała (P03-01…07) i zrobiła R2: stany domyślne R15–R33, wspólny reset TPS3808→SN74LVC1G07(OD)→R34 220R→SUP_N = EN modułu + RESET MCP + P04, blokada USB LTC4412+AO3401A, R36–R40 33R.

27.09: moja końcowa recenzja R2 (`Plytki/P03-R2-recenzja/RECENZJA-P03-R2.md`, bez blokera) i **R3 zamykająca** (`Plytki/P03-R3-review`, zip 8f25ac8f…): tylko R14 0R→1K, kontrole złączy vs zamrożeni sąsiedzi, próby ujemne z próbą zerową.

**27.09: R4 na decyzję użytkownika** („Dodaj bufor Schmitta SN74LVC1G17 i wygeneruj nową rewizję”): `Plytki/P03-R4-review` (+ zip SHA256 36d73f76…, 170 plików). U6 LVC1G17 (A = SUP_N, VCC 3V3_CORE) → R41 220R 1206 → SUP_N_OUT = J4.15; C15 100 nF. Taśma H_SAFE 150 mm (≈ 20 pF) → ≤ 5,5 ns/V na P04 (limit 10 ns/V do ≈ 36 pF). PCB bez nowego trasowania: miedź R3 z `routing/P03-R3.ses` zasiana jako zablokowana (`seed_r3.py`), zmiana przy J4 ręcznie w `route_critical.py`; −3 odcinki R3, +25 elementów, HW_ARMED_CORE obchodzi U6 po B.Cu (2 przelotki). R41 w szczelinie J4–U12 → wyjątek GAP dla oznaczenia. Kontrole: ERC 0, DRC 0/0/0, PCB 30/30, funkcje 53/53, mutacje 43/43, próby 18/18 + zerowa, R3→R4 13/13, czyste odtworzenie PASS (kopia w scratchpadzie).

Otwarte: recenzja layoutu R4 przy J4, przekrój B2B P03–P05, antena, LDO, pomiary ODBIOR (zbocze SUP_N_OUT, prąd zwarcia J4.15 11–16 mA).

**Why:** schemat pracy Claude ↔ Astra ([[user-pcb-background]]); mój kod negative_controls z R1 miał błąd DRC-baseline (ten sam w P00-R2).
**28.09:** w `Plytki/` są już P03-R5 i P04-R2.2 (sekcja w EGRLab-AKTYWNE.md, autora nie ustalałem): U4 SN74LVC1G37DBVR (Schmitt + OD) zamiast 1G07, P04 R17 100k → 10k; do recenzji, B2B nadal otwarte (`P03-R5-review/docs/B2B-STATUS.md`). SN74LVC1G37DBVR: TME 0 szt. 28.09.

**How to apply:** skryptu `verification/rebuild-compare.py` z R2 NIE uruchamiać z wydaniem jako 1. argumentem (R2 pisał raport do arg1); od R3 pisze do arg2. Przy kolejnej lokalnej zmianie P03 powtórzyć schemat R4 (zasianie SES poprzedniej rewizji + ręczna zmiana). Zob. [[kicad-pipeline-quirks]], [[p04-r2-state]], [[p00-r1-state]].
