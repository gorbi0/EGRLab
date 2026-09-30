---
name: p03-r6-state
description: "P03 R6 (CORE w S1, klasa L, poziom 2): poprawki schematu po PR #6 zrobione; layout na gałęzi p03-r6-pcb w toku — trasowanie niedomknięte (13 połączeń + masa przy SOIC); przeniesione na Ubuntu 24/7"
metadata:
  node_type: memory
  type: project
  originSessionId: 1bdb3685-394a-4886-bbc7-14b9957d5ea4
  modified: 2026-09-30T15:22:08.975Z
---

Stan 30.09.2026 (szczegóły: `Plytki/P03-R6-review/STAN-PRAC.md`, gałąź `p03-r6-pcb`).

- Schemat: R43 100k, trzecia żyła 5V_SYS na J_BP2.17 (PFAIL_N → 16, ADC_RESET → 18), wszystkie R/C SMD 1206, kołki listew serwisowych pogrupowane według położenia węzłów (J_SV1 = S1, J_SV2 = S2, J_SV3 = S3). `src/run_schematic.py` PASS; `src/run_release.py` = pełny łańcuch jak P02 R4.
- Layout: M1 w S2 (USB-C 6,2 mm przed krawędzią B, bo moduł 26 mm > przerwa 19,4 mm między listwami J_SV — sporne), SD1 w S3, U22 w S1 (sporne wobec README), tor 5 V zablokowany 1,5 mm po B.Cu (route_critical.py, budżet 50 mΩ).
- Lekcje routera: 3V3_CORE musi mieć 0,3 mm — 0,5 mm nie przechodzi między pinami w rastrze 2,54 (szczelina 0,84 mm) i router obchodził M1 (48 → 13 niepołączonych). GND poza routerem → ok. 60 pól GND (piny SOIC 1/4/7/10/13) bez połączenia z wylewkami; następnie: GND z powrotem do routera albo przelotki GND przy pinach.
- silkscreen/verify_pcb/negative_controls/make_pdf napisane, NIEURUCHOMIONE.

**Why:** użytkownik chce, żeby długie zadania szły na komputerze 24/7 ([[ubuntu-24-7]]); ta sesja na laptopie tylko przekazuje.
**How to apply:** zaczynać od STAN-PRAC.md; wynik na `p03-r6-pcb`, PR, scalenie po „scal”. Wzorce: [[p02-r4-state]], [[kicad-pipeline-quirks]], [[format-s1]].
