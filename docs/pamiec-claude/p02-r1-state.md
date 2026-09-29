---
name: p02-r1-state
description: "P02 PSU+HOLD: R1 (Claude 25.09) → R2 (Astra) → moja recenzja R2 + R3 zamykająca (Claude 26.09, zip 215d7e53); decyzje i otwarte pozycje"
metadata:
  node_type: memory
  type: project
  originSessionId: 1bdb3685-394a-4886-bbc7-14b9957d5ea4
  modified: 2026-09-27T06:08:19.981Z
---

`Plytki/P02-R1-review`: mój pierwszy schemat i PCB (25.09). Astra zrobiła R2 (`P02-R2-review`: progi HOLD_READY z obwiednią 1024 narożników, R18/R19 oddzielające filtr od sprzężenia, TP3 za R20 1k/2W, 4 arkusze A3, 2 × 70 µm).

**26.09: moja recenzja R2** (`Plytki/P02-R2-recenzja/RECENZJA-P02-R2.md`, własny model `skrypty/progi_hold.py` — obwiednie zgodne co do mV). **Użytkownik: „po twojej iteracji zamykamy tę płytkę”** → zrobiłem **R3 zamykającą** `Plytki/P02-R3-review` (+ zip SHA256 215d7e53…): miedź/rozmieszczenie identyczne z R2 (kontrola R2→R3). F2/F3 Schurter SPT 0001.2504 T1A, F4 0001.2501 T0,5A (seria SPT 250 VAC/300 VDC, UL 1500 A @ 300 VDC; TRACO zaleca slow blow), F1 0001.2507 T2A; R16 470 Ω; `--rebuild` naprawiony (SES w pakiecie, zagłodzone termiki po UUID — R2 parsowało angielski opis DRC); etykiety globalne na końcu poziomych szyn; czarna belka 100 mm. Wyniki: ERC 0, 208/208, DRC 0/0/0, PCB 29/29, elektr. 11/11, R2→R3 8/8, mutacje 10/10 + 8/8.

Otwarte: przymiarka 1:1, 0001.2501 poza TME (Mouser), Mini-Fit 39-29-6048 TME 0 szt., I²t F1:F2 z karty PDF Schurtera (nie oglądana), ODBIOR, Gerbery po przymiarce. VPROT_OK próg ~12,25 V — przy zgaszonym silniku kwalifikacja ręczna TP1 ≥ 11,6 V, TP3 ≥ 9,7 V.

**Why:** schemat pracy Claude ↔ Astra ([[user-pcb-background]]); P02 jest już zamknięta — nie proponować kolejnych iteracji bez konkretnej niezgodności.
**How to apply:** linki do kart Schurtera: używać stron HTML (`/en/datasheet/SPT_5x20`), bo link `.pdf` wywołuje pobieranie. Zob. [[kicad-pipeline-quirks]], [[p04-r2-state]].
