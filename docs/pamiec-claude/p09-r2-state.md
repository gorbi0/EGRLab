---
name: p09-r2-state
description: "P09 R2 (TEMP w S1, klasa 1/3, slot S3 poziomu 3): PCB gotowa do recenzji 30.09 wieczorem (DRC 0/0/0, PCB 22/22, próby 16/16) na p09-r2-pcb; moduły terminalami do ściany wejść; sporne: wysokość gniazda z modułem = limit, pin 1 J2 od większego x"
metadata:
  node_type: memory
  type: project
  originSessionId: cb9bcc34-135b-58ad-be17-9604396c28c1
  modified: 2026-09-30T22:15:00.000Z
---

Stan 30.09.2026 wieczorem (szczegóły: README pakietu `Plytki/P09-R2-review`, sekcja „PCB”; gałąź `p09-r2-pcb`).

- PCB: DRC 0 niepołączonych / 0 niezgodności / 0 innych naruszeń (2 przyjęte `lib_footprint_mismatch` J1/J2), `verify_pcb.py` 22/22, próby ujemne 16/16; router domknął się w pierwszej próbie (ścieżki 0,3 mm). PDF `output/pdf/P09-R2-PCB.pdf` (5 stron obejrzanych). Odtwarzanie: `run_release.py` (SES + `completion-routes.json`), ok. 3 min.
- Łańcuch layoutu z P03 R6 sparametryzowany: wartości płytki w `src/board.py` (NAME, CLASS, SLOTS, JBP, JSV, SIGNAL_W, SUPPORT_KEEPOUT); ten sam zestaw skryptów użyty dla P10 R2.
- Moduły J3/J4 obrócone o 90° (terminal do ściany wejść x = 53, VIN u góry); `MODUL-KWALIFIKACJA.md` opisuje nową orientację. Otwory podparcia Ø6 z polem Ø8 bez miedzi.
- Sporne do recenzji: wysokość gniazda z modułem (szacunek 16,5 = limit poziomu 3), pin 1 J2 od większego x (nota BOM i ODBIOR poprawione), 4 pola z pełnym połączeniem (J1.1, J1.3, J4.3, R10.2), C6/C7 6,0/5,3 mm od VIN (próg 6,5 z uzasadnieniem).

**Why:** druga płytka zrobiona na komputerze 24/7; sparametryzowany łańcuch skraca kolejne płytki klasy 1/3.
**How to apply:** recenzję zaczynać od README „PCB”; nie trasować od nowa bez potrzeby. Zob. [[p03-r6-state]], [[ubuntu-24-7]], [[format-s1]].
