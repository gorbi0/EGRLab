---
name: p00-r1-state
description: "P00 FIXTURE: R1 (Claude 25.09) → R2 (Astra) → moja recenzja R2 + R3 zamykająca (Claude 27.09, zip 97783cea, miedź = R2); co rozstrzyga pomiar"
metadata:
  node_type: memory
  type: project
  originSessionId: 1bdb3685-394a-4886-bbc7-14b9957d5ea4
  modified: 2026-09-28T13:37:46.254Z
---

Przyrząd stołowy (8 źródeł 3V3/GND przez 1 k + heartbeat TLC555 ~102 Hz, SW9 RUN/STOP). R1 mój (25.09); Astra zrobiła R2 (`Plytki/P00-R2-review`: 6–15 V, R5 560 Ω, C6 22 µF + R6 1 Ω). Pułapka Würth WS-SLTV: COM na środkowym pinie, „opposite side connection” — symbol przenumerowany, kierunek potwierdzić omomierzem.

**27.09: moja recenzja R2** (`Plytki/P00-R2-recenzja/RECENZJA-P00-R2.md`, model `skrypty/punkty_pracy.py`): bez blokera PCB. Główny błąd: `P00-P04-WIAZKA.md` opisywał P04 v6.1 (J13–J20). **R3 zamykająca** `Plytki/P00-R3-review` (+ zip SHA256 97783cea…, 138 plików): miedź/rozmieszczenie/wartości/MPN = R2 (`check_revision.py` 10/10; Gerbery vs R2: tylko F.Silkscreen). Wiązka przepisana na P04-R2.1 + `check_harness.py` na zamrożonej netliście P04 (10/10, 12/12 mutacji). Nadruk: „+VIN 6-15V” pod J10, TP3 „ZA D1”. Nowe kontrole: budżet 65 mA ≥ maks. z netlisty 57,1 mA; H heartbeat. Próby ujemne z próbą zerową (w R2 DRC każdej kopii oblewał przez brak biblioteki „P00”). Starved thermals po UUID. Czysta regeneracja PASS (odcisk ba543c4b…).

Rozstrzyga pomiar przy odbiorze: H heartbeat na J9 z 10 kΩ ≥ 2,4 V (narożnik min. VOH TLC555 SLFS043K daje 1,87 V wobec VIH 2,0 V 74LVC125A; środek: RL9 4,7 kΩ) oraz temperatura U2 przy 15 V (plan B 12 V — radiator koliduje z C5/C7). W `P00-R3-review/output/pdf` zostały 2 PDF R2 (nie w zipie) — usunięcie zablokował safety check; użytkownik może skasować ręcznie.

**28.09 — mój błąd w R3 `docs/ZAKUPY-P00.md`:** wiązka stanowiskowa do P04 ma dla J2 „gniazdo IDC16” i dla J1 „obudowę żeńską Mini-Fit 4p”, a H_SAFE i H_LV04 kończą się złączami żeńskimi (P04 `P00-P04.md`: męski IDC16 bez pinu 4). Poprawione tylko w `Plytki/Zakupy-2` (męskie T821-1-16 i 39-29-6048); pakiet R3 i zip nietknięte — przy ewentualnym R3.1 docs poprawić.

**Why:** schemat pracy Claude ↔ Astra ([[user-pcb-background]]); użytkownik nie powiedział wprost „zamykamy P00” — R3 opisane jako „gotowe do zamknięcia”.
**How to apply:** nie proponować kolejnych iteracji P00 bez konkretnej niezgodności. Liczby LM2937 (SNVS015F) niezweryfikowane (Mouser timeout, TI 404). Zob. [[p04-r2-state]], [[kicad-pipeline-quirks]].
