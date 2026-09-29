# P02-R3 — zmiany względem R2 (rewizja zamykająca)

26.09.2026 · Claude. Podstawa: R2 Astry (`Plytki/P02-R2-review`, bez zmian) i moja recenzja `Plytki/P02-R2-recenzja/RECENZJA-P02-R2.md`. Zgodnie z decyzją użytkownika to ostatnia iteracja projektu P02. **Miedź, rozmieszczenie, strefy i połączenia są identyczne z R2** — sprawdza to `src/check_revision.py` (R2 → R3) na zamrożonych kopiach `reference/R2-parts.json` i `reference/R2.kicad_pcb`.

| Uwaga recenzji | Zmiana w R3 | Gdzie |
|---|---|---|
| P2-01 wkładki F2/F3/F4 bez MPN | F2/F3: Schurter 0001.2504 **T1A** (zwłoczne, jak zaleca TRACO dla TSR2). F4: Schurter 0001.2501 **T0,5A**. Cała seria SPT ma 250 VAC / 300 VDC, UL 1500 A przy 300 VDC. F1 bez zmian (0001.2507, T2A). Nadruk przy oprawkach: T1A, T1A, T500mA | `parts.py`, BOM, nadruk, `ZAKUPY-P02.md` |
| P2-02 `--rebuild` nie odtwarzał płytki | Pakiet zawiera `routing/P02.ses`. `run_layout.py` wybiera zagłodzone pady po UUID z raportu DRC, więc działa niezależnie od języka KiCada | `run_layout.py`, `package_review.py` |
| P2-03 VPROT_OK przy zgaszonym silniku | Progi bez zmian; opisana ręczna kwalifikacja (TP1 ≥ 11,6 V, TP3 ≥ 9,7 V przez 15 s) i punkt odbioru 8a | `HOLD-ANALIZA.md`, `ODBIOR.md` |
| P2-04 przerwany F1 | Opis poprawiony: LED gaśnie po ok. 1–2 min (maks. ok. 115 s). Nowa kontrola elektryczna i mutacja (bleeder 47 kΩ) | `check_electrical.py`, `HOLD-ANALIZA.md`, `ODBIOR.md` pkt 12, arkusz HOLD |
| P2-05 kolizje na arkuszu 1 | Etykiety globalne na poziomych szynach skierowane od szyny (HOLD_STORE, VLOG_RES, GND); pola D1 na lewo od symbolu | `cadlib.py`, `build_schematic_r2.py` |
| P2-06 pogubione spacje | `MECHANIKA.md` i `ZAKUPY-P02.md` napisane od nowa z tą samą treścią | `docs/` |
| P2-07 blada belka 100 mm | Czarna linia 1,2 pt z kreskami końcowymi | `make_pdf_r2.py` |
| P2-08 słaba LED | R16 1 kΩ → **470 Ω** (ok. 1,7–3,2 mA); nowa kontrola i mutacja (R16 1 kΩ) | `parts.py`, `check_electrical.py` |

Poza tym zmieniono tytuły arkuszy i tabliczki (P02-R3), linię tytułową na PCB („PCB R3 / SCH P02-R3 / 2026-09”) oraz nazwy PDF i archiwum. Nazwy skryptów `*_r2.py` zostały bez zmian.

## Czego nie zmieniano

Progi HOLD_READY (obwiednie jak w R2), R6/R7/R9/R10 0,1 %, filtr i sprzężenie, TP3/R20, bank, R17 poza PCB, złącza, kotwy wiązek, górne rezystory dzielników przy źródłach. Brak Gerberów — powstaną po przymiarce 1:1.

## Sporne

- **F2/F3 zwłoczne zamiast szybkich (v6.1: F1A).** Szybka seria 5 × 20 z parametrem DC nie znalazła się w sprawdzonych kartach (Schurter SP i FST — tylko AC). Zwłoczne są zgodne z zaleceniem TRACO. Selektywność F1:F2 = 2:1 w tej samej serii — do potwierdzenia z I²t w karcie PDF przy zakupie.
- **F4 T0,5A zamiast F100mA.** Przewodem VSENSE płynie ok. 25 µA, więc wartość nie wpływa na pomiar. 0,5 A to najmniejsza wkładka z parametrem DC w tej serii i wciąż chroni przewód AWG22.

## Wyniki

Patrz `verification/QA.md`.
