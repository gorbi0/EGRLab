---
name: p09-r2-state
description: "P09 R2 (TEMP w S1, klasa 1/3, slot S3 poziomu 3): PCB scalona 1.10 — moduły MAX31856 lutowane wprost (decyzja użytkownika), PCB 25/25, próby 22/22; pin 1 J2 od większego x"
metadata:
  node_type: memory
  type: project
  originSessionId: cb9bcc34-135b-58ad-be17-9604396c28c1
  modified: 2026-10-01T12:00:00.000Z
---

Stan 1.10.2026: scalona do `main` (szczegóły: README pakietu `Plytki/P09-R2-review`, sekcja „PCB”).

- PCB: DRC bez naruszeń poza 2 przyjętymi `lib_footprint_mismatch` (J1/J2), `verify_pcb.py` 25/25, próby ujemne 22/22; nowe trasowanie 1.10 (56 przelotek, bez tras planera). Rozmieszczenie (`src/placement.py`) uruchamia się osobno przed `--new-route`.
- Decyzja 1.10: moduły J3/J4 lutowane wprost fabryczną listwą (footprint `P09:MAX31856_XU` bez otworów podparcia); wysokość szacunek górny 14,1 mm — potwierdzić pomiarem modułu przed zamówieniem.
- Łańcuch layoutu z P03 R6 sparametryzowany: wartości płytki w `src/board.py` (NAME, CLASS, SLOTS, JBP, JSV, SIGNAL_W, SUPPORT_KEEPOUT, PIN_MARKS); wspólny z P10 R2.
- Lekcja 1.10: w próbach ujemnych nie usuwać elementów przez `b.Remove()` (psuje SWIG kolejnych `LoadBoard`) — usuwać w pliku (sexpr).

**Why:** druga płytka zrobiona na komputerze 24/7; sparametryzowany łańcuch skraca kolejne płytki klasy 1/3.
**How to apply:** recenzję zaczynać od README „PCB”; nie trasować od nowa bez potrzeby. Zob. [[p03-r6-state]], [[ubuntu-24-7]], [[format-s1]].
