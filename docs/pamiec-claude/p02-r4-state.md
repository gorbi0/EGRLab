---
name: p02-r4-state
description: "P02 R4 (zasilanie z pakietu 4S): spec → etap 1 schemat w chmurze (PR #2, scalony 29.09) → moja recenzja i decyzje (D3 5KP24A, C_H 2200, UVLO obwiednia) → etap 2 PCB w chmurze"
metadata:
  node_type: memory
  type: project
  originSessionId: 1bdb3685-394a-4886-bbc7-14b9957d5ea4
  modified: 2026-09-29T11:22:28.750Z
---

P02 R4 zastępuje P01 PROTECT i HOLD z P02 R3 (decyzja 29.09: zasilanie z pakietu 4S, zob. [[zasilanie-ogniwa-18650]]).

**Przebieg:**
- Specyfikacja i STAN-PRAC: `Plytki/P02-R4-specyfikacja/`.
- Etap 1 (schemat) zrobiła sesja w chmurze (Opus 5.5 high, ok. 25 min), pakiet `Plytki/P02-R4-review`:
  - ERC 0, netlista 317/317, 35/35 kontroli elektrycznych, 19/19 prób ujemnych;
  - oznaczenia: Q9 = Q_REV, Q1 = Q_SW, Q2 = Q_OFF, C12 = C_H, R40 = R_ch, D2 = D_ch;
  - PFAIL_N z U2A buforującej OK (odstępstwo od D-06, uzasadnione).
- Moja recenzja: `Plytki/P02-R4-recenzja/RECENZJA-P02-R4-ETAP1.md`. UVLO przeliczone niezależnie (13,53/12,56 V wobec 13,50/12,55 V). PR #2 scalony (merge 4ac375d).

**Decyzje użytkownika po recenzji (29.09, „przyjmuję wszystkie rekomendacje”):**
- D3 5KP18A → 5KP24A: Z-01, bez uszkodzeń do 25 V.
- C_H zostaje 2200 µF. Z-08 przepisane na ≥ 10 ms w najgorszym narożniku (jest 11,1 ms). 3300 µF nie mieści się w limicie wysokości 35 mm.
- UVLO bez zmian. Z-02/O-02 przepisane na obwiednię 12,90–14,08 / 11,98–13,11 V. Moje ±0,34 V w specyfikacji było zaniżone (rezystory 1 %).
- Bezpiecznik przy klemie 1 A.
- Włącznik PWR na P11 ze złoconymi stykami (ok. 0,3 mA, obwód „suchy”).

**Następny krok:** etap 2 (PCB) w chmurze:
- zadanie `Plytki/P02-R4-specyfikacja/ZADANIE-P02-R4-ETAP2.md`, gałąź `p02-r4-pcb`;
- polecenie w `docs/CHMURA.md`;
- najpierw zmiana D3 i J15 w schemacie.

Paczka produkcyjna dopiero po mojej recenzji PCB.

**Why:** płytka zasilania jest na ścieżce krytycznej całego przyrządu. Etapy z recenzją ograniczają koszt sesji w chmurze.
**How to apply:** przy recenzji etapu 2 sprawdzić:
- blaszki TO-220 (dren) tylko na własnej sieci ([[p01-pcb-r1-review]]);
- tory 5 A przy 35 µm;
- odsprzęganie;
- wprowadzenie D3 5KP24A.

Zob. [[repo-chmura]], [[pcb-fab-satland]].
