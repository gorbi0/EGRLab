---
name: p01-pcb-r2-state
description: P01 PCB layout history and current state — R1 (Astra) → R2 (Claude) → R3 (Astra) → R3.1 (Claude, fixes from my R3 review, 2026-09-25); use R3.1 for the 1:1 fit
metadata:
  type: project
---

Stan 2026-09-25: do przymiarki i montażu służy **`Plytki/P01-PCB-R3.1-review`** (zip sha `6b4c1044…`), czyli PCB-R3 Astry z poprawkami z mojej recenzji (`Plytki/P01-PCB-R3-recenzja/`). Płytka (miedź, nadruk, wiercenia, 2036 elementów geometrii) identyczna z R3 — napis na PCB nadal „PCB R3”; różni się tylko ukryte pole AssemblyMPN U4. Pakiet R3 Astry nietknięty.

R3.1: kolejność montażu D4 → Q1+HS2 dokręcone → C6 (C6 13 mm zasłania łeb śruby Q1 na 13,5 mm; przy wlutowanym C6 śruba od tyłu kanału); serwis C6/D4 bez zdejmowania HS2; BOM A1: U4 z TME, uwagi BOM R3 (wyprowadzenia, polaryzacja) zachowane + „zakup:”; 31 kontroli (nowa: A1 traced + notes + pola PCB), 5/5 prób, DRC 0/0/0. `--rebuild` daje identyczną geometrię, ale inny hash pliku przy każdym przebiegu.

Wcześniej: R2 (moje) → recenzja Astry (`P01-PCB-R2-recenzja-Codex`: stary drc.json, probe_open, modele, BOM A1 — przyjęte) → R3 (D4 we wnęce, TP od spodu, modele, A1, run_release). Następny krok: wydruk 1:1 i przymiarka, potem Gerber/Excellon z tego samego przebiegu.

**Why:** kolejna sesja zacznie się pewnie od wyników przymiarki albo eksportu produkcyjnego.
**How to apply:** pracuj w R3.1 i jego `run_release.py` (polecenie w [[egrlab-codex-toolchains]]); każda zmiana dokumentów/BOM wymaga ponownego odbioru. Zob. [[user-pcb-background]], [[kicad-pipeline-quirks]], [[egrlab-review-rules]].
