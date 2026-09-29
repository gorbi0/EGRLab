# P02-R2 — montaż, obwiednie i osłony

Płytka 160×120 mm, otwory M3 Ø3,2 w (5,5), (155,5), (5,115), (155,115) mm. P02 najlepiej umieścić na górze stosu albo obok pozostałych modułów. Modele 3D są lokalnymi **obwiedniami gabarytowymi**, nie pomiarem dopasowania części.

| Element | Obwiednia / wymaganie |
|---|---|
| C1–C3 | Ø35×45 mm, raster10; co najmniej3 mm wolnego miejsca nad zaworami; korpusy od siebie4 mm |
| U1/U2 | TSR2, katalogowa wysokość10,1 mm; tolerancja gabarytu z rysunku producenta |
| J3–J11 | gniazdo12,8 mm; model ze wtykiem do27,2 mm, dodatkowo miejsce na wygięcie przewodów; praktyczny zapas wysokości35 mm |
| U5 | adapter18×18 mm, rzędy15,24; wysokość zależy od kołków i ewentualnych gniazd |
| R20 | PR02 korpus10×3,9 mm, raster17,78; montować1 mm nad laminatem |
| D1/D2 | pionowe TO-220; tab D1=VLOG_RES, D2=HOLD_FUSED; nie łączyć metalowych tabów |

Bank wymaga podparcia w obudowie: trzy izolujące obejmy do puszek35 mm, mocowane do wspornika obudowy, **bez nowych otworów wierconych w PCB**. Obejma obejmuje boczną część puszki, nie dociska zaworu ani plastikowej koszulki ostrą krawędzią. Pod lutami banku zamontować sztywną izolującą osłonę z dystansem co najmniej3 mm od końcówek; po ucięciu wyprowadzeń skontrolować prześwit. Mocowanie i osłona pozostają do fizycznej przymiarki.

R17 HSA2547RJ poza PCB na osobnej blaszce według warunków chłodzenia TE, z dala od kondensatorów. Przy tolerancji−5% granica bez uwzględnienia spadku D2 wynosi7,26 W przy18 V i22,94 W przy32 V. Nie wolno zakładać25 W bez wymaganej powierzchni chłodzącej.

Wiązki: J1 2×2,5 mm² /200 mm do P01 J6 (MSTB1757022); J13 2×AWG20 /200 mm do R17; J12 taśma6×AWG28 /150 mm do P04 (IDC6, klucz5). Na P02 przewody lutowane w metalizowanych otworach, kotwy12,5 mm od lutów. Moduły kupne i CORE–DAQ pozostają poza zakresem tej płytki.

TP3 przeniesiono do (46,5;3,5) mm; napis BANK/1k. To pole za R20, nie surowy bank. Puszki i F1 nie zasłaniają dostępu od góry. Surowe luty banku nadal wymagają osłony. Energia maks.40,55 J; bleeder do1 V w ok.22 min. Przed serwisem mierzyć.

Kolejność: niskie THT i podstawki → U5 z C16 na adapterze → małe elektrolity/LED → przetwornice/diody/oprawki → złącza i wiązki → pierwszy test bez banku → C1–C3 i ich podparcie. C16 0805 lutować lokalnie na adapterze do szyn bezpośrednio przy pinach14/7 układu; krótkie izolowane połączenia, bez kolizji z kołkami. C11 pozostaje na P02.

Weryfikacja rzeczywistych gabarytów, zatrzasków, wtyków i podparcia: NIE ZBADANO; formularz w verification/ODBIOR.md.
