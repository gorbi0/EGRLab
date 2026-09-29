# Kontrola bibliotek — zakres i źródła

Wszystkie użyte footprinty i symbole są w paczce. `verification/footprint-pads.csv`
zawiera rzeczywiste numery padów i średnice z tych plików, a nie nazwę oczekiwanej
obudowy. Pozwala to recenzentowi odnieść konkretny otwór do konkretnego wyprowadzenia.

| Grupa | Dobór / kontrola |
|---|---|
| R ogólne | Yageo MFR-50, 0,5 W, 1%; obrys10,2×4mm, raster15,24, otwór1mm. Nie miniaturowe MFR-50S. |
| R5–R11 | HOLCO H4, 0,5W, 0,1%, 15ppm/K; wspólny większy footprint15,24mm. Dokładne MPN dostępnościowo do zamknięcia w B-01. |
| R1/R23/R27 | Vishay PR02, 2W, raster17,78, otwór1,1mm. |
| D1/D3 | Duże obudowy P600, raster20,32, otwór1,6mm; D3 katoda pad1, D1 dwukierunkowy bez polaryzacji. Nie footprint DO-201 dla tych dwóch transili. |
| D5 | DO-201, raster15,24; katoda pad1. D4/D6–D9 DO-35, raster10,16. |
| C2/C4/C5 | TDK B32529, obrys7,3×2,5mm, P5. |
| C6 | B32529D1105J000: obrys7,8×7,8, H13mm, P5. |
| C8/C10/C11/C12/C13 | Vishay K15, wykonanie H5, raster5mm; obrys uwzględnia wygięte końcówki, nie symboliczny dysk. |
| Elektrolity | C1 D5/P2; C3 D8/P3,5; C7 D5/P2; C9 D6,3/P2,5. Wartości i napięcia w BOM. |
| Q1/Q2/D2 | Lokalny TO-220 pionowy, G-D-S / A-K-A, raster2,54, otwory1,4mm, pady2,1×3mm. Maksymalna nóżka Q1 1,01×0,61mm (przekątna1,18mm); standardowe1,1mm za małe. Mocowanie radiatora osobno w M-01. |
| Q3–Q8 | TO-92 wide EBC, Q4 YBU bez -C. Q2 teraz TO-220 GDS. |
| U1 | LM2936 TO-92: OUT1/GND2/IN3. |
| U2 | LM2903P, DIP8; wyjścia1/7, VCC8, GND4; nie zmieniać automatycznie na wariant innego producenta. |
| U3 | TI TL431BILP, K1/A2/REF3. Lokalny symbol poprawiony względem symbolu ogólnego. |
| U4 | MCP120-450DI/TO, bondout D: RESET1/VDD2/GND3. |
| J6 | Phoenix1757255: lokalna kopia footprintu konkretnego modelu, raster5,08mm; pin3 NC. |

Źródła per MPN są w BOM. Dla rezystorów H4 adres reprezentatywnej części rodziny
nie jest potwierdzeniem dostępności wszystkich wartości. Lista źródeł pobranych
automatycznie w `reference/sources.json` jawnie zachowuje również nieudane próby
pobrania; nie należy interpretować HTTP403 jako dowodu przeczytania datasheetu.

Kluczowe źródła kontroli:

- [TL431 TI, LP](https://www.ti.com/lit/ds/symlink/tl431.pdf)
- [LM2936 TI](https://www.ti.com/lit/ds/symlink/lm2936.pdf)
- [2N5401 onsemi, YBU](https://www.onsemi.com/download/data-sheet/pdf/2n5401-d.pdf)
- [2N5550/2N5551 onsemi](https://www.onsemi.com/download/data-sheet/pdf/2n5550-d.pdf)
- [K series Vishay — kod H5](https://www.vishay.com/docs/45171/kseries.pdf)
- [TDK B32520–B32529](https://www.tdk-electronics.tdk.com/inf/20/20/db/fc_2009/B32520_529.pdf)
- [MFR Yageo](https://www.yageogroup.com/content/Resource%20Library/Datasheet/YAGEO-MFR_DATASHEET.pdf)
- [PR02 Vishay](https://www.vishay.com/docs/28729/pr010203.pdf)

Nie skopiowano modeli STEP, więc brak pełnej kontroli kolizji3D. Zamknięcie B-01
oznacza również sprawdzenie największych wymiarów, tolerancji oraz miejsc na lut
i narzędzie; nie tylko dopasowania numerów pinów.

R2:J7 PTH3,2/pad6,0/P7,62; Q2 jak Q1; D9 DO-35 K1/A2.
