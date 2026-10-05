# Przewody P08-R2

Wiązki W1 LV08, W2 SENSOR i W3 SFAULT z R1 znikają: ich sieci idą przez J_BP (krawędź A) i taśmę IDC 2×8 do płytki połączeń P12 (`docs/J_BP.csv`). Zostaje jeden przewód.

| Przewód | P08 | Drugi koniec | Przewód | Uwagi |
|---|---|---|---|---|
| W4 TSENSOR | J4 (pole PTH, 2 pola Ø1,1 mm, raster 3,5 mm) | port TEST na panelu (x = 0) | 2 × AWG22 skręcone | kotwa opaski 12 mm przed rzędem lutów, od strony krawędzi x = 0 (jak J4/J6 w P05 R3); numeracja z R1 bez zmian |

| Pin J4 | Sieć | Uwagi |
|---|---|---|
| 1 | 5V_SENSOR | wyjście za stykiem K1 NO_A |
| 2 | AGND_SENSOR | powrót czujnika, rozłączany stykiem K1 NO_B; nie łączyć z GND, ekranem ani masą oscyloskopu |

Pomiar wyjścia (E01, E02, E04, E05, E09): różnicowo lub izolowanym miernikiem między J4.1 i J4.2, na porcie TEST. Długość pary i wtyk portu TEST — z makiety panelu S1 (otwarte).
