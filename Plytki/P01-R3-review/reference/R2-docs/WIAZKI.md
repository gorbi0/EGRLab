# P01 — wiązki i punkty dostępu

Wymiar 200 mm oznacza długość gotowego odcinka od rzędu lutów PCB do czoła wtyku,
z tolerancją montażową ±10 mm. Materiał przyciąć z zapasem do obróbki. Żyły numerować
na obu końcach; kierować się numerami komór producenta, nie widokiem „od lewej”.

## H_PG: 1 komplet na P01

Sześć żył AWG22 (około 0,34 mm²), izolacja OD 1,3–2,0 mm, 200 mm.
P01/J5: lut do sześciu PTH w rastrze 2,54 mm; brak gniazda na P01.
P04: obudowa Mini-Fit Jr 6p Molex **39-01-2060**, sześć styków żeńskich Au
**39-00-0429**, dobranych do AWG22. Materiały i zakres AWG:
[Molex](https://www.molex.com/en-us/products/part-detail/39000429).

| Pin J5 / komora wtyku PG | Sieć |
|---:|---|
| 1 | 3V3_IO — z odbiornika, nie z AUX5 |
| 2 | SAFE_N — otwarty kolektor Q7 |
| 3 | GND |
| 4 | PG_SEND |
| 5 | PG_LINK |
| 6 | GND |

Opaska 2,5 mm przechodzi przez dwa otwory NPTH Ø3,2 mm, 12,5 mm od rzędu lutów.
Otwory PTH Ø1,1 mm. Przewody prowadzić bez ostrych zgięć, opaska obejmuje izolację,
nie odizolowaną żyłę. Nie dociągać opaski tak, aby przeciąć izolację. Nie prowadzić
tej wiązki razem z przewodami silnika. Styków we wtyku nie zalewać cyną po zacisku.
Można zamówić gotowe przewody z tymi stykami, przyciąć i polutować koniec P01.

## H_BAT: 1 komplet na P01

Dwie żyły linki miedzianej 2,5 mm², po 200 mm, plus czerwony, masa czarna.
P01/J7: lut do PTH Ø3,2 mm w rastrze 7,62 mm. Kotwa 12,5 mm od rzędu lutów,
dwa NPTH Ø4,2 mm, opaska 3,6 mm. Rozstaw kotew 13,62 mm; środek wiązki między nimi.
Na drugim końcu wtyk Phoenix **1757019**, MSTB 2,5/2-ST-5,08, z tulejkami
2,5 mm² dopasowanymi długością do zacisku. Nie cynować linki do zacisku śrubowego.
Pin 1=BAT_FUSED, pin 2=GND. Bezpiecznik 5 A jest **przed** H_BAT, blisko źródła.

## SUPPLY: wiązka po stronie P02

Na P01/J6 zamontować Phoenix **1757255**, MSTBA 2,5/3-G-5,08.
Wtyk przewodu P02: **1757022**, MSTB 2,5/3-ST-5,08. Pin 1=VPROT, 2=GND, 3=NC.
Nie mostkować pinu 3. Oznakowanie BAT/PG/SUPPLY zachować również na obudowie.
W BOM P01 nie liczyć ponownie wiązki SUPPLY ani gniazda PG na P04.

## Pomiar i serwis

J1: BAT_FUSED/GND; J2: VPROT/GND; J4: 3V3_IO/SAFE_N/GND;
J8: PG_SEND/PG_LINK. Są to pola pomiarowe, nie dodatkowe kupowane złącza.
J3 jest rzeczywistą listwą 2p 2,54 mm: zwarcie wymusza OFF, normalnie otwarte.
TP1 VS, TP2 GATE, TP3 AUX_IN, TP4 AUX5, TP5 REF, TP6 OK, TP7 ENABLE,
TP8 OV_SENSE, TP9 UV_SENSE, TP10 GND. Każdy punkt oznaczyć na silkscreenie.

Przed podłączeniem P04/P02 sprawdzić każdą żyłę miernikiem i próbą poruszenia
wiązki. Obecność modułu: ciągłość PG_SEND–R34–PG_LINK, brak zwarcia do SAFE_N.


## R2: komplet BAT

EXT/J_BATA = **Phoenix1786174 IC2,5/2-ST-5,08**, styki męskie, zaciski śrubowe,
po stronie źródła ZA bezpiecznikiem5A. H_BAT ma żeńskie1757019.
[Producent1757019 wymienia1786174 jako mate](https://www.phoenixcontact.com/en-us/products/pcb-plug-mstb-25-2-st-508-1757019).
Stronę źródła osłonić i zamocować w obudowie, nie pozostawiać luźnych odsłoniętych
pinów. Rozłączać/montować bez zasilania (złącze nie jest łącznikiem mocy).
Pin1=plus po F1,2=GND; sprawdzić numery komór obu części, nie widok od lewej.
Dwie tulejki EXT są osobne od tulejek H_BAT, ujęte raz w BOM-MECHANIKA.
J7: padØ6mm/otwórØ3,2mm; przed PCB próbka rzeczywistej linki i kupon. Nie obcinać
drutów, żeby weszły; po lutowaniu sprawdzić zwilżenie. Kotwy pozostają12,5mm.
