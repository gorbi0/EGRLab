---
name: format-s1
description: "Format S1 (29.09): stos płytek 160×100 z tercjami, płytka połączeń P12, listwy serwisowe na krawędzi B (wymaganie użytkownika); LOGGER ok. 3,2 l; specyfikacja S1-3 (P02 R4 w klasie L, P10 na poziomie 4 S3)"
metadata:
  node_type: memory
  type: project
  originSessionId: 1bdb3685-394a-4886-bbc7-14b9957d5ea4
  modified: 2026-09-29T11:58:18.259Z
---

**Kontekst.** 29.09.2026 użytkownik chce jak najmniejszego urządzenia. Zaproponował stos: jednakowe duże płytki skręcone dystansami, a mniejsze (1/2 albo 1/3 dużej) skręcone do większych. Większe płytki mają być raczej prostokątne niż kwadratowe. Poprosił o zbadanie tematu przed projektem PCB.

**Wymaganie użytkownika (trwałe):** punkty pomiarowe potrzebne do odbioru płytki mają być w każdej płytce po tej samej stronie. Po skręceniu stosu mają zostać dostępne bez obracania całości. Wystarczą zwykłe kołki (goldpin).

**Wynik studium** (`Plytki/Format-S1/STUDIUM-FORMATU-S1.md`, `src/powierzchnie.py`, rysunek `porownanie-S1-kaseta.svg`):
- Części zajmują 21–53 % powierzchni płytek R1–R5.
- Format L ≈ 160 × 100 mm oraz 2/3 i 1/3 długości. Tercje zamiast połówek, bo wariant pełny wychodzi wtedy 5 poziomów zamiast 6.
- Krawędź A: płytka połączeń (sieci v6.1 na miedzi, jedno IDC na płytkę). Krawędź B: listwa serwisowa z kołkami kątowymi. Krótkie boki: panel P11 oraz XT60/OBD/VBAT.
- Poziomy LOGGER: P02 R4 + P10 | P03 | P05 + P09 | P06. Obudowa ok. 231 × 133 × 105 mm (3,2 l zamiast 11,4 l); pełny ok. 231 × 133 × 127 mm (3,9 l zamiast 14,5 l); pierwsze wydanie studium podawało 95 mm i 2,9 l.
- P02 R4 przy obecnej technice (MFR-50 leżące na 15,24 mm, 8 × Mini-Fit LV) potrzebuje ok. 155 cm² wobec celu 98 cm². Etap 2 wstrzymany do decyzji.

**Decyzje użytkownika (29.09):**
- format S1: tak;
- płytka połączeń P12 zamiast wiązek: tak;
- **posiadane rezystory THT zostają (montaż na stojąco), nowe kupujemy w SMD 1206.** Użytkownik nie chce drugi raz płacić za części, a w kabinie praktycznie nie ma drgań; moje ostrzeżenie o pękaniu nóżek odrzucone;
- wszystkie płytki z fabryki w Chinach (JLCPCB), bez płytek uniwersalnych.

**Specyfikacja:** `Plytki/Format-S1/SPECYFIKACJA-FORMATU-S1.md` i `format-s1.json` (S1-1):
- sloty S1/S2/S3 po 53,0 mm, krok 53,5 mm; otwory M3 w slocie x = 4/49, y = 14/86;
- dystanse 20 mm, 25 mm pod P02 R4;
- krawędź A: IDC kątowe 2×5…2×10, środek x = 26,5 mm w slocie, osobny pinout dla każdej płytki (P12 = wiązki v6.1 na miedzi);
- krawędź B: kątowe kołki, x = 10–43 mm w slocie, GND na końcach;
- pinout J_BP płytki P02 R4 jest ustalony.

Wstrzymane: stary etap 2 P02 R4, layout P05 R2, zamówienie PCB P04. Następny krok: pilot P02 R4 w S1 w chmurze.

**S1-2 (29.09):** SMD od spodu dozwolone (SOIC tylko na poziomie 1).
**S1-3 (29.09 wieczorem, commit 1c94235 na main):** P02 R4 w klasie L (cały poziom 1; w 2/3 trasowanie się nie domykało), P10 na poziom 4, slot S3 (J3 OBD przy ścianie wejść; od spodu bez SOIC, góra ≤ 16,5 mm; P10 R2 zakładał S1 poziomu 1). Wariant pełny: na poziomie 4 zostaje tylko S2, więc P04 potrzebuje 6. poziomu (albo P10) — do decyzji przy wariancie pełnym.

**Why:** w kasecie R1 z płytkami 160 × 120 urządzenie było za duże (obawa użytkownika z 29.09).
**How to apply:** projektując każdą płytkę, trzymać format S1 i listwę serwisową na krawędzi B. Zob. [[kaseta-r1]], [[p02-r4-state]], [[egrlab-review-rules]].
