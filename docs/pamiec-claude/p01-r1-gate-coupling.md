---
name: p01-r1-gate-coupling
description: P01-R1 review (2026-09-23) found Q1 gate dV/dt turn-on; fix values to verify in P01-R2
metadata:
  type: project
---

P01-R1-review (EGRLab P01 PROTECT, baza 6.1-rc1) — recenzja 2026-09-23: jedyny błąd blokujący PCB to sprzężenie bramki Q1 (SUP53P06-20). C5=220 nF (G–D) jest większy niż C6=47 nF (G–S), więc szybkie narastanie VS przy wyłączonym Q1 (wpięcie zasilania, skok w stanie OVP-OFF) ciągnie VSG do 6–10 V i Q1 przewodzi: model z 50 mΩ źródła daje 46–80 A przy 14 V i 120–190 A przy 24 V. Zalecane wartości: C5=22 nF, C6=680 nF, R21=47 kΩ, R27=33 Ω (w modelu: VSG ≤0,75 V przy 24 V/1 µs, start 1,8 A do 220 µF, wyłączenie OVP <2 V po ~44 µs, Q2 ~380 mA). Szeregowy R z C5 NIE działa — psuje kształtowanie startu (60–80 A).

**Why:** Pakiet przeszedł ERC, porównanie z bazą i testy mutacyjne; tego błędu żadne z nich nie wykryje, bo to własność dynamiczna. Próba „szybkiego podłączenia” w ODBIOR przejdzie fałszywie, jeśli użyć rampy zasilacza zamiast styku mechanicznego.

**How to apply:** Przy przeglądzie P01-R2 sprawdź, czy wartości C5/C6/R21/R27 zmieniono (i footprint C6, bo 680 nF ma inny obrys), czy zaktualizowano PROJEKT.md i czy ODBIOR wymaga podłączenia stykiem. Recenzja i model: `P01-R1-recenzja/RECENZJA-P01-R1.md` oraz `P01-R1-recenzja/model/model_bramki_Q1.py`. Poza tym P01-R1 elektrycznie czysta — zob. [[egrlab-review-rules]].
