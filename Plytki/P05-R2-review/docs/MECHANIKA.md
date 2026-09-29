# Mechanika, złącza i montaż P05

PCB 160×120mm, FR4 1,6mm, miedź 35µm na obu stronach. M3: otwory NPTH3,2mm w (5,5), (155,5), (5,115), (155,115). Płaszczyzna masy pod rdzeniem ADC, końcowym rozprowadzeniem wejść i referencją ma zakaz prowadzenia ścieżek B.Cu. Tory od przekaźników do filtrów mogą korzystać z B.Cu powyżej y=35,5mm. Nie ma podziału GND na osobne, połączone wąskim mostkiem wyspy analogowe/cyfrowe. Lokalne pola masy obu stron łączą przelotki, również przy komparatorze i buforach.

Minimalny prześwit 0,15mm jest potrzebny przy LQFP/VSSOP. Domyślna ścieżka0,20mm, via0,60/0,30mm; odbiór sprawdza natywne DRC, nie komunikat autoroutera. Małe pady SMD masy mogą mieć połączenie pełne; złącza i końce lutowanych wiązek zachowują termiki. Obszary pod opaskami i podkładkami M3 są bez miedzi na obu stronach.

## CORE–DAQ

Przyjęto **P05 obok P03, na tej samej wysokości**, zgodnie z przechwyconą wersją P03. Nie jest to pionowy stos z pierwotnej tabeli v6.1. Obie płytki mają własne dystanse, złącze nie przenosi obciążenia mechanicznego.

- P03: gniazdo kątowe, wariant przewidziany SSW-108-02-G-D-RA. P03 ma w kopii generyczny footprint KiCad, więc jego zgodność z konkretnym gniazdem wymaga przymiarki.
- P05: TSW-108-08-G-D-NA, dedykowany footprint. Samtec wskazuje wariant **NA** do koplanarnego łączenia z SSW-RA. Nie zastępować go zwykłym RA bez sprawdzenia wysokości obu rzędów.
- Wstępny dystans krawędzi PCB:1mm. Obrys P03 kończy się na x160; początek P05 w układzie wspólnym x161. Przewidywane wsunięcie postów wynosi około4mm; sprawdzić z rzeczywistymi częściami, bez wymuszania pozycji śrubami.
- P05 ma pin logiczny1 w (6,50;31), pin2 w (3,96;31), piny3/4 przy y28,46 i kolejne co2,54mm do15/16 przy y13,22. Pad1 jest prostokątny. **Numery logiczne footprintu nie są wystarczającą informacją o numerach katalogowych na dwóch przeciwnie skierowanych złączach.**
- P03 w zapisanej kopii: logiczny1=(147;31),2=(149,54;31); kolejne pary mają te same y jak P05. Skontrolować oba poziomy kontaktów. Nie zakładać zgodności na podstawie samego widoku z góry.

**Punkt zatrzymania przed zamówieniem PCB:** przymierzyć wskazaną parę złączy na wydruku1:1 i w prostym przyrządzie z rastrem2,54mm, a następnie potwierdzić tabelę poniżej miernikiem. Numerację kolumn footprintu ustalono na potrzeby dopasowania do P03, ale fizycznego matingu nie zbadano. Jeśli rzeczywiste styki łączą inne kolumny, poprawić footprint przed wydaniem Gerberów, ponowić DRC i testy; nie przekrosowywać „na pamięć”.

| Pin logiczny obu PCB | Sygnał | Kontrola ciągłości |
|---:|---|---|
|1|ADC_SCLK|NIE ZBADANO|
|2|klucz, NC|NIE ZBADANO|
|3|ADC_SDI|NIE ZBADANO|
|4|GND|NIE ZBADANO|
|5|ADC_DOUTA|NIE ZBADANO|
|6|GND|NIE ZBADANO|
|7|ADC_CS|NIE ZBADANO|
|8|GND|NIE ZBADANO|
|9|ADC_CONVST|NIE ZBADANO|
|10|GND|NIE ZBADANO|
|11|ADC_BUSY|NIE ZBADANO|
|12|GND|NIE ZBADANO|
|13|ADC_RESET|NIE ZBADANO|
|14|GND|NIE ZBADANO|
|15|MEAS_EN|NIE ZBADANO|
|16|GND|NIE ZBADANO|

Dopiero po potwierdzeniu dopasowania usunąć kontakt męski odpowiadający **logicznemu2** i zaślepić pasujący otwór gniazda. Nie usuwać styku według niezweryfikowanego numeru producenta. P05 nie dostarcza zasilania przez B2B; połączenie mas jest wielokrotne.

Źródła geometrii: [TSW rysunek](https://suddendocs.samtec.com/prints/tsw-xxx-xx-xxx-x-xx-xxx-mkt.pdf), [SSW rysunek](https://suddendocs.samtec.com/prints/ssw-1xx-xx-xxx-x-xx-xxx-xx-mkt.pdf), [TSW katalog — opcja NA](https://suddendocs.samtec.com/catalog_english/tsw_th.pdf). Kopie rysunków i PCB P03 są w `reference/`.

## Wiązki

| Ref | Wiązka | Długość od PTH do wtyku | Drugi koniec |
|---|---|---:|---|
|J2|LV05, 4 żyły AWG22|200mm|Mini-Fit Jr żeńskie4p Au do P02|
|J3|DAQOK, taśma6 żył AWG28, raster1,27mm|150mm|IDC żeńskie6p Au z odciążką, KEY4, do P04/J5|
|J4|TAPS, 5 par sygnał/GND AWG24|50mm|Mini-Fit Jr żeńskie12p Au do P11,11/12 NC|
|J5|VSENSE, para AWG22|150mm|Mini-Fit Jr żeńskie14p Au do P02, tylko1/2|
|J6|AUX, RG174|50mm|BNC panelowe izolowane mechanicznie od obudowy|

PTH po stronie P05: otwory1,1mm, pady2,2mm dla przewodów pojedynczych; J3 otwory0,8mm, pady1,8mm. Dwa otwory kotwy3,2mm wyznaczają linię11,5mm od pierwszego rzędu: drugi rząd jest od niej15mm lub14,04mm dla IDC. Opaska2,5mm obejmuje izolację z miękką podkładką. Nie ściskać odizolowanych żył. Zachować łuk bez naprężenia i nie zalewać cyną całego odcinka do kotwy.

Numerację PTH sprawdzać na rysunku od strony elementów i w `pinout.csv`; orientacje J2/J3/J5 są inne niż J4/J6. Nie przenosić intuicyjnie kolejności kolorów z czoła wtyku na widok lutów. Wszystkie sygnały niskoprądowe: styki Au. Ekran AUX łączy się z GND na J6; nie daje to izolacji galwanicznej. Wtyki Mini-Fit muszą pasować do konkretnych, zatwierdzonych odpowiedników P02/P11 — różne liczby pozycji rozróżniają funkcje.

## Elementy wymagające szczególnej kontroli

- U1: AD7606BBSTZ LQFP64 10×10mm, pitch0,5mm. Pin1 według oznaczenia producenta; nie według kierunku napisu na dowolnym zdjęciu.
- U3: TLV1702AQDGKRQ1 VSSOP8 pitch0,65mm, bez adaptera. U2 i U8–U11: SOIC/SO14 bezpośrednio na P05.
- U6/U7 MCP120 **bondout D**:1RESET,2VDD,3GND. U12 MCP1700:1GND,2VIN,3VOUT. Obudowy wyglądają podobnie, mają inne funkcje pinów.
- C1 EEUFR1C471: Ø8×11,5mm, raster3,5mm,470µF16V. [Karta Panasonic](https://industrial.panasonic.com/sa/products/pt/aluminum-cap-lead/models/EEUFR1C471).
- SW1 C&K7201SYCBE: C oznacza terminale PCB; pady4,70×4,83mm, otwory1,85mm. Korpus zarezerwowano11,43×12,70mm. Nie kupować odmiany Z z szerokimi oczkami do lutowania przewodów. [Rysunek C&K](https://www.ckswitches.com/media/1394/7000toggle.pdf). Sprawdzić pozycje omomierzem: HI=2–1/5–4, LO=2–3/5–6. Na obudowie opisać dopiero po tym pomiarze.
- K1–K3 G6K-2P-Y DC5: THT, raster i polaryzacja cewki według footprintu. Do testów cewki nie potrzeba EGR.

Nad PCB pozostawić miejsce na sondę, przewody oraz dźwignię SW1. Dźwigni nie obciążać przez wiązkę; jeśli wychodzi przez panel, ustalić otwór po przymiarce. Testpady są dostępne od góry. Wydruk montażowy ma belkę100mm — drukować100%, bez dopasowania.

Oznaczenia C27–C34 są na B.SilkS, bezpośrednio pod odpowiednimi kondensatorami. Na rysunku montażowym są powtórzone na niebiesko w widoku od góry. Pozostałe oznaczenia są na F.SilkS. Lokalna kopia footprintu DIN0207 ma krawędzie obrysu sitodruku zwężone o 0,02mm; pady, korpus i obrys montażowy nie uległy zmianie.
