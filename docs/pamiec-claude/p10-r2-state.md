---
name: p10-r2-state
description: "P10 R2 (CAN w S1, klasa 1/3, slot S3 poziomu 4 wg S1-3): PCB scalona 1.10 (PCB 24/24, próby 26/26); wszystkie części od góry, J3 z kotwą przy ścianie wejść"
metadata:
  node_type: memory
  type: project
  originSessionId: cb9bcc34-135b-58ad-be17-9604396c28c1
  modified: 2026-10-01T12:00:00.000Z
---

Stan 1.10.2026: scalona do `main` po poprawkach z recenzji (nadruk, linie CAN przez pola D1, pierścień 1 mm wokół pól J3) i odtworzeniu wydania; szczegóły: README pakietu `Plytki/P10-R2-review`, sekcja „PCB”.

- PCB: DRC 0 niepołączonych / 0 niezgodności / 0 innych naruszeń (2 przyjęte `lib_footprint_mismatch` J1/J2), `verify_pcb.py` 21/21, próby ujemne 18/18; router w pierwszej próbie, bez tras planera. PDF `output/pdf/P10-R2-PCB.pdf` (5 stron obejrzanych). Odtwarzanie: `run_release.py`, ok. 3 min.
- Slot S3 poziomu 4 (S1-3; schemat R2 zakładał S1 poziomu 1): wszystkie części od góry, więc zakaz SOIC od spodu nic nie zmienia; w schemacie zmieniły się tylko teksty (opis arkusza, tytuł, noty J1/J2).
- J3 (koniec W3) obrócony o 270°: kotwa opaski w stronę ściany wejść, pas pod przewodem bez części, pola Ø6 bez miedzi wokół otworów kotwy; D1 3,2 mm od pól J3.
- Sporne: pin 1 J2 od większego x (jak P09/P03; nota BOM i ODBIOR poprawione).

**Why:** trzecia płytka zrobiona na komputerze 24/7 łańcuchem sparametryzowanym przy P09.
**How to apply:** recenzję zaczynać od README „PCB”. Zob. [[p09-r2-state]], [[format-s1]], [[ubuntu-24-7]].
