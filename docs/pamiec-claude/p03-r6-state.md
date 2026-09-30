---
name: p03-r6-state
description: "P03 R6 (CORE w S1, klasa L, poziom 2): PCB gotowa do recenzji 30.09 wieczorem (DRC 0/0/0, PCB 25/25, próby 16/16) na p03-r6-pcb; decyzje: sygnały 0,2 mm, zamiana bramek U12→U14; commity lokalnie na Ubuntu 24/7, push czeka na logowanie"
metadata:
  node_type: memory
  type: project
  originSessionId: cb9bcc34-135b-58ad-be17-9604396c28c1
  modified: 2026-09-30T20:00:00.000Z
---

Stan 30.09.2026 wieczorem (szczegóły: README pakietu, sekcja „PCB”, i `Plytki/P03-R6-review/STAN-PRAC.md`; gałąź `p03-r6-pcb`).

- PCB: DRC 0 niepołączonych / 0 niezgodności / 0 innych naruszeń (6 przyjętych `lib_footprint_mismatch` złączy z przyciętym nadrukiem), `verify_pcb.py` 25/25, próby ujemne 16/16, tor 5 V 37,7 mΩ; PDF `output/pdf/P03-R6-PCB.pdf` (5 stron obejrzanych). Odtwarzanie: `run_release.py` (SES + `completion-routes.json`).
- Decyzje użytkownika 30.09: ścieżki sygnałowe 0,2 mm przy odstępie 0,25 (tylko P03 R6; S1 §3 dalej „jak P02-R3”), 3V3_CORE 0,3 mm (klasa CORE3V3); zamiana bramek LOGGER_CURRENT_OK / SENSOR_HEALTHY z U12 ch3/ch4 na U14 ch2/ch3 (10 opisanych różnic w `compare_v61.py` i `verify_function.py`), kołki J_SV1.10 ↔ J_SV3.12; commity i push etapami.
- Rozmieszczenie: S1 rozsunięte (SOIC y 28, U1 y 45, U2 y 66), U21 x 54, C13 obrót 270, węzły serwisowe bliżej listew, R71 stawiany pierwszy.
- Sporne do recenzji: 9 punktów w README (m.in. moduły 6,2 mm przed krawędzią B, U22 przy J_BP1, skróty przy J_SV2/3, 3 pola GND z pełnym połączeniem: J_BP1.7, J_BP2.3, M1.J3-1).
- Otwarte: przymiarka 1:1, wysokość M1, 15 ukrytych oznaczeń, push/PR, paczka produkcyjna po „scal”.

**Why:** pierwsza płytka zrobiona w całości na komputerze 24/7; łańcuch jest wzorem dla P09/P10 R2 ([[kicad-pipeline-quirks]]).
**How to apply:** recenzję zaczynać od README „PCB”; nie trasować od nowa bez potrzeby (wynik routera jest losowy — odtwarzać SES). Zob. [[ubuntu-24-7]], [[format-s1]].
