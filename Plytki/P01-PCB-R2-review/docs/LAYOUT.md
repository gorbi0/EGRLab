# P01-PCB-R2 - decyzje i delta względem schematu R3

Zmiany względem PCB R1 i ich dowody: `ZMIANY-R2.md`. Ten plik opisuje stan R2 w całości.

## Mechanika i technologia

PCB 160 × 120 mm, FR4, nominalnie 1,6 mm, dwie warstwy miedzi po 70 µm.
W stackup zapisano Cu0,07/core1,46/Cu0,07 mm; maska jest warstwą dodatkową.
Wykończenie proponowane: bezołowiowy HASL. Wymiar i grubość miedzi trzeba
przekazać wykonawcy; plik sam nie gwarantuje grubości wykonanego laminatu.

M3: NPTH Ø3,2 mm w (5;5), (155;5), (5;115), (155;115) mm, początek w lewym
górnym rogu, X w prawo, Y w dół. Wokół każdego jest keepout Cu Ø8 mm na obu
warstwach. Montaż na izolacyjnych dystansach. Wysokość radiatorów 63,5 mm plus
prześwit; do tego dystanse PCB i miejsce na narzędzie/pokrywę. Bez zmian od R1.

**Radiatory (R2, PCB1-01).** Pod HS1 i HS2 leżą obszary reguł na F.Cu: obrys
metalu profilu SK129 powiększony o 0,5 mm (±21,8 × ±13,3 mm od środka), bez
ścieżek, przelotek i wylewki; pady dozwolone. Wnęka TO-220 (|x| < 8 mm, y > +1,5 mm
od środka) jest otwarta, bo stoją w niej nóżki Q1/D2. Na B.Cu pod profilami zostaje
powrót GND 5 mm (Y = 9,5) i wylewka GND: od aluminium oddziela je laminat 1,6 mm.

## Rozmieszczenie (R2, PCB1-03)

Bloki funkcjonalne, od góry:

| Blok | Elementy | Położenie (punkty odniesienia footprintów) |
|---|---|---|
| Wejście i moc | J7, D1, J1; D2/HS1, Q1/HS2; LK1, D3, C3/C4, J6, J2 | jak w R1: lewa krawędź, góra, prawa krawędź |
| Szyna VS i odsprzęganie | C1, C2, R1, D9, Q2, D4 | pod szyną VS (Y = 34), odczepy pionowo do szyny |
| Zasilanie AUX5 | R1 → D5, C7, C8 → U1 → R2/C9, TP3/TP4 | X 33–61, Y 40–59 |
| Odniesienie i komparator | U3, R3, R4, R5–R12, RV1, U2, C10, C12, C13, TP5, TP8, TP9 | X 6–62, Y 66–111 (lewa dolna ćwiartka) |
| Nadzór i OK | U4, C11, R13, J3, TP6 | X 47–69, Y 66–76 |
| Bufor ENABLE | R14, D7, D8, Q6, R15, R16, TP7, TP10 | X 60–90, Y 80–116 |
| Sterowanie bramką | Q4, Q5, R19, R20, R23–R26 (OFF/RELEASE); R17, R18, R21, R22, Q3, C5 (ON) | X 74–131, Y 44–84 |
| Wyjście | J2, R28, R29, LED1 | X 136–155, Y 58–78 |
| SAFE / PG | Q7, Q8, R30–R34, J4, J8, J5 | X 105–145, Y 87–105 |

C6 stoi we wnęce HS2, między G i S Q1 (PCB1-05). D9 jest przy Q2 (PCB1-06).
C10 stoi przy U2, a C11 przy U4, jak każą uwagi BOM R3. W R1 C11 stał przy U2,
C10 przy U1, a U4 nie miał kondensatora w pobliżu (C11 21 mm od U4.2).

## Tor mocy

BAT/J7 i D1 po lewej; D2/HS1 i Q1/HS2 u góry; LK1 i wyjście J6 po prawej.
D1 powraca odcinkiem 4 mm na B.Cu do J7.2, D3 do okolicy wyjścia.
Silny powrót GND (5 mm, B.Cu) biegnie górą i prawym bokiem, z dala od odniesienia
i komparatora w lewym dolnym rogu. GND jest jedną siecią z wypełnieniem obu warstw,
bez szczeliny dzielącej masę.

| Odcinek | Szerokość | Uwagi |
|---|---|---|
| BAT_FUSED J7 → D1 | 3 mm | + wyspa BAT na obu warstwach przy J7 |
| BAT_FUSED pod HS1 (X 19,5–48,5) | **3 mm** | R1: 5 mm, ale pod metalem radiatora; patrz niżej |
| BAT_FUSED do wnęki HS1 | 2,5 mm, potem 2 mm | mostek do obu anod D2 (pady 1 i 3) |
| VS: D2.K → szyna, szyna → Q1.S | 2 mm (B.Cu) | pionowo we wnękach |
| Szyna VS, Y = 34 | 5 mm F.Cu (X 55–94) + 5 mm B.Cu (X 55–110,5) | przelotki Ø1,2/0,6 mm w X = 55, 70, 94 |
| DRAIN Q1 → LK1 | 2 mm we wnęce, potem 4 mm | |
| VPROT LK1 → J6 / D3 | 5 mm, gałąź do J6 2 mm, gałąź D3 3 mm | jak R1 |

**BAT_FUSED 3 mm (sporne).** Wytyczna R3 mówi o korytarzu mocy „początkowo ≥ 5 mm na obu
warstwach”. W R2 odcinek pod HS1 ma 3 mm na F.Cu, bo od góry ogranicza go strefa radiatora
(PCB1-01), a od dołu pad GND D1.2. Na B.Cu równoległą drogę przecina powrót GND D1 → J7.2.
Uzasadnienie: przy F1 = 5 A i 70 µm to wg IPC-2221 ok. +3 °C, 2,4 mΩ i 12 mV spadku, a 5 mm
wymagałoby miedzi pod radiatorem albo przesunięcia D1, które jest mechanicznie związane z R1.

Rachunek odcinka: R = ρ·L/(w·t), ρ20 = 0,0175 Ω·mm²/m, t = 0,070 mm. 20 mm ścieżki 2 mm daje
ok. 2,5 mΩ (62,5 mW przy 5 A). Przy wzroście temperatury Cu o 80 K rezystancja rośnie
o ok. 31%. To rachunek fragmentów, **nie kwalifikacja obciążalności całej PCB**: nie obejmuje
PTH, termików, lutów, zwory i temperatury obudowy. Próby 0,1/1/3,5/5 A z ODBIOR R3 pozostają
wymagane.

J7 ma termiki 1,2 mm / szczelina 0,3 mm na obu warstwach; kontrola sprawdza wypełnioną miedź
ramion i szczelin, tak jak w R1.

## Pomiar i sterowanie

LK1 jest jedynym projektowanym połączeniem DRAIN z VPROT. Oba duże pola są oddzielnymi
sieciami. Zwora z Cu 2,5 mm² jest montowana po odbiorze ciągłości; przed montażem można
sprawdzić jej rozdzielenie. Nie cynować przestrzeni między polami w sposób tworzący mostek.

Oba odczepy Kelvin mają osobne ścieżki 0,4 mm kończące się w polach sense. Gałąź C5 idzie
do pola siłowego VPROT przy D3 osobną ścieżką 0,6 mm na B.Cu. TP1 do Q1.S: 4,71 mm; TP2 do Q1.G:
4,85 mm. To długości ścieżek na PCB; przewody zewnętrznej sondy trzeba kwalifikować osobno.

Bramka Q1: Q1.G → C6 (we wnęce) → pionowy grzbiet 0,8 mm w X = 105,5 w dół do D4 (Y = 39,5)
i R27 (Y = 48,5). D4 jest ok. 19 mm ścieżki od Q1.G i ok. 34 mm od Q1.S (przez szynę VS);
szybkie zaburzenia G–S bierze C6 we wnęce. Pętla wyłączania Q2 → R27 → GATE → Q1 → VS → Q2.S
ma ok. 18 × 15 mm pod szyną VS i ok. 5 × 12 mm we wnęce. Jej długość wyznacza PR02 R27
(raster 17,78 mm). Oba punkty są w `ZMIANY-R2.md` jako do sprawdzenia (R3: „lokalnie”, „krótka”).

R1 i R23 montować około 3 mm nad laminatem, zgodnie z R3. Oba są daleko od TL431 i dzielników:
R1 ≥ 31 mm, R23 ≥ 29 mm (odległość padów, łącznie z R12). Bliskość na płytce nie zastępuje pomiaru
stabilności AUX5, progów OVP/UVLO i czasu wyłączenia Q1.

## Biblioteki i napisy

Wartości, numery padów, geometria padów i identyfikatory footprintów elektrycznych są zgodne
z R3. Jedyna zmiana biblioteki: lokalny `TO220_3_P2.54_Drill1.4` ma na F.SilkS obrys korpusu
omijający pady i linię 0,4 mm po stronie taba (PCB1-02). Courtyard i F.Fab bez zmian.

Obrysy radiatorów i małych kondensatorów K15 są, jak w R1, tylko na F.Fab (na wydruku
montażowym są widoczne). Napisy: J7 `B+`/`GND`, J6 `OUT+`/`GND`/`NC`, J5 `1`…`6`, J1 `BAT`/`GND`,
J2 `OUT+`/`GND`, J4 `3V3`/`SAFE_N`/`GND`, J8 `S`/`L` (PG_SEND/PG_LINK), `TAB` przy Q2.
Oznaczenia rezystorów leżą w obrysie korpusu, wzdłuż osi.

## Bramki odbioru

1. DRC i zgodność ze schematem: wykonane; raporty w `verification/`.
2. Kontrole geometrii i sześć celowo wprowadzonych usterek w kopiach: wykonane.
3. Przymiarka 1:1 rzeczywistych części i obudowy: **NIE ZBADANO**.
4. Gerbery/wiercenia produkcyjne: **po punkcie 3 i recenzji R2**, nie są częścią tego wydania.
5. Odbiór elektryczny, SOA, termika i impulsy: **NIE ZBADANO**.

Nie zmieniać statusu 3-5 na PASS na podstawie DRC ani samego renderu.
P07 oraz wariant mostka BTS7960 pozostają poza zakresem.
