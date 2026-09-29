---
name: chmura-limity
description: "Po pilocie P02 R4 (29.09): layoutu i trasowania PCB nie zlecać do chmury — sesja spaliła ok. 30 $/h na własne planery i czekanie, restart kontenera skasował wynik; w chmurze tylko zadania o jasnym końcu, push po każdym etapie, limity prób"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 1bdb3685-394a-4886-bbc7-14b9957d5ea4
  modified: 2026-09-29T15:31:06.439Z
---

**Co się stało.** Pilot P02 R4 w formacie S1 dostał zadanie: schemat i PCB razem z trasowaniem do skutku.
- Sesja w chmurze (Opus 5.5 high) przez kilka godzin pisała własne planery trasowania i puszczała długie przebiegi Freeroutingu w tle.
- W godzinę dojazdu użytkownika zużyła ok. 30 $ kredytu.
- Kontener się zrestartował, a wynik routera przepadł, bo nie był wypchnięty.
- Użytkownik: „trochę słabe to środowisko”. Przyznałem, że layout w chmurze zleciłem ja.

Wcześniej schemat P02 R4 w chmurze zajął 25 min i był dobry.

**Reguła:**
- Layout i trasowanie PCB robi sesja lokalna (KiCad i Freerouting na komputerze użytkownika, z planu Pro, nie z kredytu).
- Do chmury idą tylko zadania o jasnym końcu: schemat, kontrole, dokumenty, paczki.
- W każdym poleceniu dla chmury:
  - commit i push po każdym etapie;
  - bez własnych routerów i planerów;
  - bez procesów dłuższych niż ok. 15 min i bez częstego monitorowania;
  - po dwóch nieudanych próbach zapis stanu i PR.

Zasady 6–9 w `docs/CHMURA.md`, sekcja „Koszty”.

**Why:** kredyt 250 $ jest skończony, a użytkownik pilnuje kosztów. Iteracyjne trasowanie w kontenerze bez GUI jest drogie i kruche.
**How to apply:** projektując zadanie do chmury, sprawdź, czy ma jasny koniec i czy da się je zapisywać etapami. Layout płytek formatu S1 rób lokalnie, a do chmury najwyżej schemat i kontrole. Zob. [[repo-chmura]], [[format-s1]], [[p02-r4-state]].
