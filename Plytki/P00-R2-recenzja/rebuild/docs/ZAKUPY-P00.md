# P00-R2 - wykaz części

Ilości na jeden egzemplarz, bez zapasu. To pełny BOM zakupowy, bez potrącania stanu magazynu. Szczegóły oznaczeń na schemacie: `BOM.csv`. Już kupione rezystory MF0207 1% o tych samych wartościach i wymiarach można wykorzystać; kody MFR poniżej są konkretną rodziną odniesienia.

| Nazwa / typ | Ilość szt. |
|---|---:|
| PCB P00-R2, 115 x 70 mm, 2 warstwy | 1 |
| TLC555CP, DIP8 | 1 |
| Podstawka DIP8, raster między rzędami 7,62 mm | 1 |
| LM2937ET-3.3/NOPB, TO-220 | 1 |
| 1N5819, DO-41 | 1 |
| Würth 450301014042, SPDT ON-ON | 9 |
| Listwa goldpin 1x02, 2,54 mm (lub odcinki listwy 1x40) | 9 |
| Phoenix 1715721, MKDS 1,5/2-5,08 | 1 |
| LED zielona 3 mm Kingbright L-934GD | 8 |
| LED żółta 3 mm Kingbright L-934YD | 1 |
| LED czerwona 3 mm Kingbright L-934ID | 1 |
| Rezystor 1 kΩ, 1%, 0,25 W, MFR-25FRF52-1K | 19 |
| Rezystor 4,7 kΩ, 1%, 0,25 W, MFR-25FRF52-4K7 | 1 |
| Rezystor 68 kΩ, 1%, 0,25 W, MFR-25FRF52-68K | 1 |
| Rezystor 100 kΩ, 1%, 0,25 W, MFR-25FRF52-100K | 1 |
| Rezystor 560 Ω, 1%, 0,25 W, MFR-25FRF52-560R (R5) | 1 |
| Rezystor 1 Ω, 1%, 0,25 W, MFR-25FRF52-1R (R6) | 1 |
| 100 nF X7R, Vishay K104K15X7RF53H5, P5 | 4 |
| 10 nF X7R, Vishay K103K15X7RF53H5, P5 | 1 |
| 10 µF / 50 V, Panasonic EEUFR1H100, D5 / P2 | 1 |
| 22 µF / 50 V, Panasonic EEUFR1H220, D5 / P2 (C6) | 1 |
| Dystans/nóżka M3 | 4 |
| Śruba M3 i podkładka, dobrane do dystansu | 4 komplety |

TP1-TP3 są polami PCB, nie wymagają kupowania pinów. Nie kupować błędnego C6 EEUFR1C220 z poprzedniej rewizji.

Wiązka do P04 jest oddzielnym wyposażeniem: 9 przewodów sygnałowych i masy, długość do 20 cm, opisane końce Dupont 2,54 mm po stronie P00, adaptery do rzeczywistych złączy P04; trzy rezystory 1 kΩ / 1% / 0,25 W w izolowanych odgałęzieniach H_SUP, H_MCU i H_HB, trzy rozłączalne zworki, przycisk NO ARM oraz styk NC STOP. Konkretne obudowy adapterów dobrać do finalnej PCB P04, zgodnie z `P00-P04-WIAZKA.md`.
