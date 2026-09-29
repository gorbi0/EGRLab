---
name: kaseta-r1
description: "Obudowa EGRLab (29.09.2026): koncepcja kasety Plytki/Kaseta-R1 — LOGGER 361×209×151 mm, pełny 361×265×151; wiązki v6.1 pod płaski nośnik nie mieszczą się; J7 TAPS na P11 do przeniesienia; obudowa w kabinie"
metadata:
  node_type: memory
  type: project
  originSessionId: 1bdb3685-394a-4886-bbc7-14b9957d5ea4
  modified: 2026-09-29T01:30:57.944Z
---

28.09 użytkownik zorientował się, że komplet płytek będzie duży („nie zmieści się pod maską”). Projekt od v4.1 zakłada elektronikę w kabinie, a pod maską tylko adaptery AL1/AL2/AT na 1 m DEUTSCH i termopary. P01/P02 są liczone na 0–50 °C.

Płytki wyszły średnio 2,06× większe niż rezerwy obrysów z kart v6.1: 1492 cm² wobec 724 cm². Pięć płytek ma 160 × 120 mm, ze wspólnymi otworami M3 150 × 110 mm (5 mm od krawędzi); P03 ma dodatkowy H5.

**Kaseta R1** (`Plytki/Kaseta-R1/`, 29.09):
- **Układ:** płytki pionowo na prętach M3, strona elementów do tyłu; dwie kolumny, za P03 i za P05; małe płytki na płytach nośnych 160 × 120; panel z przodu; P11 za panelem przed P05.
- **Wymiary:** LOGGER (bez P04/P07/P08, SK129 25,4) ma wnętrze 355 × 203 × 145 mm (11,4 l ze ściankami). Wariant pełny ma 355 × 259 × 145 mm (14,5 l).
- **Wcześniejszy szacunek był zaniżony:** 7,3 i 11,2 l, bo pominął strefę panelu z P11, kanały wiązek i płyty nośne. Przyznane w README.
- **Skrypty:** `src/model.py` (układ, trasy wiązek, dobór obrotów) i `src/rysunek.py` (reportlab z runtime Codexa, PDF A3). Skalę 1:1 sprawdzono pomiarem rastra (360,7 × 209,0 mm).
- **Wiązki:** długości v6.1 zaprojektowano pod płaski nośnik. W kasecie mieści się 5 z 20 (LOGGER) i 6 z 36 (pełny).
- **Wiązki wrażliwe:** TAPS (maks. 50 mm) mieści się tylko po przeniesieniu J7 na P11 przed J4 P05 (P11-R1 nie ma recenzji); ogonki DT i VSENSE to tor analogowy; SAFE wymaga ok. 180 mm (przeliczyć zbocze resetu z P03-R4); SPI (ILOG/TEMP/ITEST) wymaga 110–320 mm.

Opcje miniaturyzacji przedstawione 28.09: a) kaseta, b) SK129 25,4 (ten sam footprint, rysunek Fischera 001020452), c) etap tylko LOGGER, d) mniejszy bank P02 (50 ms × 6 W ≈ 0,3 J), e) gęstszy THT, f) SMD + JLC PCBA. Przed 23.10 realne są a + b + c. Użytkownik jeszcze nie wybrał.

**Why:** termin 23.10.2026; użytkownik chce przymierzyć miejsce w aucie.
**How to apply:** przy P11-R2, tabeli wiązek i obudowie wychodzić z Kaseta-R1. Po zmianie rewizji płytki uruchomić ponownie `wyciag_plytek.py` i `rysunek.py`. Nie oceniać zasadności projektu. Zob. [[pcb-fab-satland]], [[p03-r1-state]], [[p04-r2-state]], [[kicad-pipeline-quirks]].
