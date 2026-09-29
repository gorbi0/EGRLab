---
name: format-s1
description: "Studium formatu S1 (29.09): stos płytek 160×100 z tercjami zamiast kasety R1, płytka połączeń zamiast wiązek, listwy serwisowe z kołkami na jednej krawędzi (wymaganie użytkownika); LOGGER ok. 2,9 l zamiast 11,4 l; do decyzji"
metadata:
  node_type: memory
  type: project
  originSessionId: 1bdb3685-394a-4886-bbc7-14b9957d5ea4
  modified: 2026-09-29T11:43:02.118Z
---

**Kontekst.** 29.09.2026 użytkownik chce jak najmniejszego urządzenia. Zaproponował stos: jednakowe duże płytki skręcone dystansami, a mniejsze (1/2 albo 1/3 dużej) skręcone do większych. Większe płytki mają być raczej prostokątne niż kwadratowe. Poprosił o zbadanie tematu przed projektem PCB.

**Wymaganie użytkownika (trwałe):** punkty pomiarowe potrzebne do odbioru płytki mają być w każdej płytce po tej samej stronie. Po skręceniu stosu mają zostać dostępne bez obracania całości. Wystarczą zwykłe kołki (goldpin).

**Wynik studium** (`Plytki/Format-S1/STUDIUM-FORMATU-S1.md`, `src/powierzchnie.py`, rysunek `porownanie-S1-kaseta.svg`):
- Części zajmują 21–53 % powierzchni płytek R1–R5.
- Format L ≈ 160 × 100 mm oraz 2/3 i 1/3 długości. Tercje zamiast połówek, bo wariant pełny wychodzi wtedy 5 poziomów zamiast 6.
- Krawędź A: płytka połączeń (sieci v6.1 na miedzi, jedno IDC na płytkę). Krawędź B: listwa serwisowa z kołkami kątowymi. Krótkie boki: panel P11 oraz XT60/OBD/VBAT.
- Poziomy LOGGER: P02 R4 + P10 | P03 | P05 + P09 | P06. Obudowa ok. 231 × 133 × 95 mm (2,9 l zamiast 11,4 l); pełny ok. 231 × 133 × 120 mm (3,7 l zamiast 14,5 l).
- P02 R4 przy obecnej technice (MFR-50 leżące na 15,24 mm, 8 × Mini-Fit LV) potrzebuje ok. 155 cm² wobec celu 98 cm². Etap 2 wstrzymany do decyzji.

**Do decyzji użytkownika:**
1. Czy przejść na format S1.
2. Płytka połączeń czy wiązki.
3. Rezystory stojące THT czy SMD 1206.

Wstrzymać do tego czasu: etap 2 P02 R4, layout P05 R2, zamówienie PCB P04.

**Why:** w kasecie R1 z płytkami 160 × 120 urządzenie było za duże (obawa użytkownika z 29.09).
**How to apply:** projektując każdą płytkę, trzymać format S1 i listwę serwisową na krawędzi B. Zob. [[kaseta-r1]], [[p02-r4-state]], [[egrlab-review-rules]].
