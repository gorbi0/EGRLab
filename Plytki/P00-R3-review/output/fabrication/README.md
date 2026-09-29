# P00-R3 — pliki produkcyjne

Gerber X2: F.Cu, B.Cu, F.SilkS, B.SilkS, F.Mask, B.Mask i Edge.Cuts. Excellon: osobne wiercenia PTH i NPTH, w mm, bez lustrzanego odbicia. Dwie warstwy miedzi po 35 µm, FR4 1,6 mm, obrys 115 × 70 mm. Montaż THT we własnym zakresie.

Eksport z KiCad 10.0.6 po świeżym DRC 0/0/0. Względem R2 miedź, maski, obrys i wiercenia są identyczne (porównanie `src/gerber_equiv.py`, `verification/clean-rebuild.json`). Zmienił się tylko nadruk: „+VIN 6-15V” pod J10, „ZA D1” przy TP3 i linia tytułowa „PCB R3”. Przed zamówieniem: przymiarka 1:1 z częściami i podgląd u producenta. Nie zamawiano produkcji.
