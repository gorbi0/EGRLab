# Montaż A1 - zakupione części w PCB-R3

Źródło: migawka `reference/purchases-2026-09-24.csv` z rejestru zamówień użytkownika.
`BOM.csv` jest historycznym BOM nominalnego schematu R3. Do montażu używać
`BOM-MONTAZOWY-A1.csv`: po jednym wierszu na każdy z 89 elementów elektrycznych,
z nominalną i montowaną wartością, MPN/kodem dostawcy, footprintem oraz pochodzeniem.
Ilości to zapotrzebowanie modułu, nie liczby zamówione z zapasem.
R3.1: U4 (MCP120-450DI/TO) ma źródło TME; wcześniej wpis rejestru „P01 U4” nie był rozpoznany.
R3.1: kolumna notes zachowuje uwagę BOM R3 (wyprowadzenia, polaryzacja, montaż) i dopisuje uwagę
z rejestru po „zakup:”. W R3 uwaga z rejestru zastępowała uwagę R3 w 70 wierszach.

PCB zachowuje nominalne pole Value dla zgodności z niezmienianym schematem R3.
Pola AssemblyVariant, AssemblyValue i AssemblyMPN podają stan montażu A1.
To jawny wariant montażowy, nie cicha zmiana schematu.

| Różnica | Decyzja dla prototypu i sposób sprawdzenia |
|---|---|
| R8 220 kΩ -> 221 kΩ / 0,1% | Przyjęte dla A1. Zmiana 0,455%. Udział sprzężenia przy R7=10 kΩ zmniejsza się w stosunku 230/231, czyli o 0,433%. Próg skorygować RV1; histerezy RV1 nie koryguje. Obowiązują dotychczasowe kryteria OVP/histerezy z ODBIOR. |
| R27 10 Ω / 1% -> 5% | Przyjęte do prototypu z odbiorem czasu odcięcia. Zakres 9,5-10,5 Ω; sam wkład R27 do stałej RC dla C6=1 uF ±5% wynosi 9,025-11,025 us. To nie jest czas odcięcia całego układu: zachować kryteria 80/100 us i pomiar VGS/SOA. |
| R1 150 Ω i R23 2,2 kΩ / 1% -> 5% | Przyjęte do prototypu, bez zwiększania obciążenia ani luzowania progów. Zakresy 142,5-157,5 Ω i 2,09-2,31 kΩ. Zachować sprawdzenie AUX, startu, odcięcia i temperatur elementów. |
| D3 Littelfuse -> Diotec 5KP18A | Przyjęte jako montowana wersja A1, z osobnym wpisem producenta. Diotec podaje VWM=18 V, VBR=20,0-23,3 V i VC=29,2 V przy 171 A dla zdefiniowanego impulsu; nie zakładać identyczności wszystkich krzywych producentów. OVP nadal ustala komparator, nie TVS. Odbiór impulsów pozostaje pomiarem konkretnego układu. |
| Rezystory MFR-50/H4 -> MF0207/MF0204/YR1B | Zachowano większe footprinty i rastry. Uformować wyprowadzenia; geometria pozostaje zgodna z dokumentacją R2. |
| C1, C5, C8/C10/C11, C12/C13 | W BOM wpisano rzeczywiście zamówione typy. C13 ma raster 5,08 zamiast 5 mm; sprawdzić uformowanie nóżek. |
| Q3/Q5-Q8 2N5551TA | Wersja montażowa z rejestru; sprawdzić E-B-C i uformowanie nóżek przed lutowaniem. |
| J3 | Listwa ZL201-02G; zworka osobno w mechanice. Pozostałe pola TEST PADS nie wymagają kupowania złącz. |

Źródła producentów użyte do rozróżnienia parametrów:
[Vishay PR01/02/03](https://www.vishay.com/docs/28729/pr010203.pdf),
[Diotec 5KP18A](https://diotec.com/de/produkt/5KP18A.html),
[WIMA MKS2](https://www.wima.de/en/our-product-range/metallized-capacitors/mks-2/).
Zgodność obudowy i parametrów nominalnych nie jest wynikiem testu sprzętu.

Elementy mechaniczne, wiązki i izolacja pozostają w BOM-MECHANIKA.csv. Nie liczyć
jednocześnie kompletu wiązki i jego składników jako dwóch kompletów do zakupu.
