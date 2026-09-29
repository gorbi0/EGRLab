---
name: user-pcb-background
description: "User's PCB design background and why Claude now designs boards that Astra reviews"
metadata:
  node_type: memory
  type: user
  originSessionId: 1bdb3685-394a-4886-bbc7-14b9957d5ea4
  modified: 2026-09-24T20:08:20.781Z
---

Użytkownik projektował PCB, wrócił do tego po ok. 20 latach przerwy. Sam zrobił płytkę P01; w porównaniu z pracą Astry (drugi model AI) wypadła gorzej. Potem odwrócił proces: Claude miał się sam zmierzyć z projektem PCB (P01 R2), a Astra recenzuje pracę Claude'a. Zauważa błędy w PCB samodzielnie i ocenia, czy Claude je wyłapuje; wytknął, że Claude krytykował Astrę, a sam popełnia „szkolne błędy”.

Astra to model Codex. Użytkownik nie wie, czy o Astrze pisać „on” czy „ona” — w tekstach po polsku używać form neutralnych (czas teraźniejszy, rzeczowniki: „Astra proponuje”, „R3 Astry”, „recenzja Astry”), bez rodzaju w czasownikach przeszłych.

**Why:** kontekst oceny — liczy się uczciwe wyłapywanie własnych błędów, nie obrona pracy.
**How to apply:** traktuj własne layouty tak samo surowo jak cudze; przed oddaniem sprawdź każde twierdzenie w dokumentach ze źródłami i przyznawaj błędy wprost. Zob. [[p01-pcb-r2-state]], [[egrlab-review-rules]].
