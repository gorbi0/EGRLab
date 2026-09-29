---
name: p01-pcb-r1-review
description: P01 PCB R1 review (2026-09-24) — two DRC-invisible blockers (copper under floating heatsinks, Q2 orientation)
metadata:
  type: project
---

Recenzja `Plytki/P01-PCB-R1-review` (layout Astry, 160×120 mm, 2L 70 µm, schemat R3) zapisana w `Plytki/P01-PCB-R1-recenzja/RECENZJA-P01-PCB-R1.md` (skrypty pcbnew w `skrypty/`, uruchamiać Pythonem z KiCad 10: `/c/Program Files/KiCad/10.0/bin/python.exe`). DRC 0/0/0 i ich 17 kontroli odtworzone.

Blokery: PCB1-01 — radiatory HS1/HS2 (pływające, stoją na F) mają pod krawędziami profilu BAT_FUSED (HS1) oraz GATE/DRAIN (HS2) + GND; izolacja tylko maska. PCB1-02 — Q2 (TO-220 bez radiatora) bez obrysu/znacznika taba na nadruku; odwrotny montaż → dioda strukturalna ściąga GATE przez R27 → Q1 stale ON (OVP/UVLO/INHIBIT martwe); wykrywa ODBIOR krok 2. Jakość: R8 między radiatorami → OV_REF 107 mm przez tor mocy, OK 210 mm; J5 wychodzi w głąb płytki; C6 18 mm od Q1.

**Why:** Kolejna rewizja PCB wróci do recenzji; te dwa typy błędów (mechanika↔miedź, orientacja montażu) nie są w ich kontrolach.

**How to apply:** PCB R2 zrobił Claude i poprawił PCB1-01…06 (+ przeoczone tu C10/C11) — stan w [[p01-pcb-r2-state]]. Zob. [[p01-r2-review]], [[egrlab-review-rules]].
