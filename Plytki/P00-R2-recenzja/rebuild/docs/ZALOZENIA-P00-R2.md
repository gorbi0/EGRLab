# P00-R2 - warunki pracy i połączenia

Przyrząd stołowy, temperatura otoczenia **10-40°C**, zasilacz laboratoryjny 6-15 V z ograniczeniem prądu. Zalecane 9-12 V. Przy 6 V na J10 i przyjętym budżecie spadku D1 0,6 V pozostaje 5,4 V na U2. Punkt TP3 leży za D1; TP1 = 3V3, TP2 = GND.

U2: LM2937ET-3.3/NOPB, TO-220, 1 IN, 2 GND/tab, 3 OUT. D1 chroni także wejściowy elektrolit. C4 10 µF / 50 V i C5 100 nF na wejściu; C7 100 nF bezpośrednio między 3V3 i GND. C6 plus na 3V3, minus przez R6 do GND. R5 bezpośrednio między 3V3 i GND.

## Warunki aplikacji U2

Minimum VIN = 4,75 V na pinie U2. Parametry wyjścia określono od 5 mA. COUT co najmniej 10 µF; projekt stosuje przedział 0,01-3 Ω dla rezystancji szeregowej gałęzi wyjściowego kondensatora, zgodnie z częścią aplikacyjną karty. Źródło: [TI SNVS015F, strony 4-5 i 11-12](https://www.mouser.com/datasheet/2/405/lm2937-3.3-484674.pdf).

R5 560 Ω daje minimum około 5,54 mA przy 3,14 V, tolerancji 1% i TCR 100 ppm/°C w zadeklarowanej temperaturze. Maksymalna moc to około 21,7 mW wobec znamionowych 250 mW. R6 1 Ω nie przewodzi prądu zasilania odbiorników; dodaje rezystancję w gałęzi C6. C6 ma nominalnie 22 µF, po tolerancji -20% pozostaje 17,6 µF.

Panasonic podaje dla EEUFR1H220 impedancję maksymalną 0,340 Ω przy 100 kHz i 20°C. Z R6 daje to około 0,989-1,352 Ω dla gałęzi w warunkach odniesienia. Jest to obliczenie przy wskazanej częstotliwości i temperaturze, nie dowód stabilności całej pętli. [Katalog FR-A, tabela 50 V](https://industrial.panasonic.com/cdbs/www-data/pdf/RDF0000/ABA0000C1259.pdf). Stabilność przy zmianie obciążenia i przy 6/15 V sprawdzić oscyloskopem w odbiorze. Nie zastępować R6 zworką ani C6 kondensatorem polimerowym bez ponownej oceny.

## Sygnały

SW1-SW8: środkowy pin 1 = COM, pin 2 = 3V3, pin 3 = GND. Würth 450301014042 łączy COM z kontaktem przeciwnym do położenia suwaka. Orientacja PCB daje suwak w górę = H. COM przez RSn 1 kΩ na Jn.1; Jn.2 = GND. Zielona LED jest przed RSn i wskazuje stan źródła, a nie odbiornika. Zasilanie P00 i P04 ma wspólną masę, ale ich szyn 3V3 nie łączyć równolegle.

U1 TLC555CP: RA 4,7 kΩ, RB 68 kΩ, C1 100 nF. Nominalnie 102,35 Hz, wypełnienie H około 51,7%. Samo uwzględnienie 1% rezystorów i 10% C daje około 92-115 Hz; próg timera i temperatura dodają odchyłkę. SW9 STOP trzyma RESET w L, czyli daje stałe L na wyjściu; RUN włącza przebieg. J9: 1 = heartbeat przez R3 1 kΩ, 2 = GND. LED9 obciąża wyjście U1 przed R3; amplitudę mierzyć również po R3, z podłączonym odbiornikiem.

Nominalny prąd zwarcia kanału do GND: 3,3 mA; górny szacunek z tolerancjami około 3,51 mA. To ograniczenie w obwodzie logicznym 3,3 V, nie ochrona przed dowolnym obcym napięciem. Przy pulldown 10 kΩ H wynosi nominalnie 3,0 V, a przy 5 kΩ 2,75 V.

## Bilans cieplny

Arkusz obliczeń `verification/electrical-checks.json` używa konserwatywnego budżetu IOUT = 65 mA i założonego IG = 20 mA. Dla 15 V daje około 1,07 W oraz oszacowanie TJ około 123,4°C przy TA = 40°C i RθJA = 77,9 K/W. To blisko granicy i **nie jest gwarancją temperatury fizycznej PCB**; IG i RθJA są jawnie przyjętymi założeniami. Typowe obciążenie jest znacznie mniejsze. Dlatego zalecane jest 9-12 V, a odbiór przy 15 V obejmuje pomiar nagrzewania i napięcia. Nie używać TP1 do zasilania badanej płytki. W razie przekroczenia kryterium odbioru zastosować mały radiator TO-220 lub ograniczyć górne napięcie robocze do 12 V i odnotować to na egzemplarzu.

Sprzęt, tętnienia i temperatura: NIEWYKONANE. Obliczenia są odczytywane z eksportowanej netlisty niezależnie od generatora, patrz `src/verify_electrical.py`.
