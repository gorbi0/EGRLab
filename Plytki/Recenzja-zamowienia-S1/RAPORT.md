# Recenzja paczek produkcyjnych S1 przed wspólnym zamówieniem w JLCPCB

*4.10.2026, sesja w chmurze, gałąź `recenzja-zamowienia-s1` (baza `origin/zamowienie-s1`). Zadanie: `Plytki/Format-S1/zadania/ZADANIE-RECENZJA-ZAMOWIENIA-S1.md`. Recenzja tylko do odczytu: paczek nie zmieniałem, skrypty pracowały na kopiach w scratchpad.*

## Rekomendacja

| Płytka | Decyzja | Powód w jednym zdaniu |
|---|---|---|
| **P02 PCB R4** | **zamawiać** | Bez blokera i bez MAJOR; dwie uwagi serwisowe (MINOR). |
| **P03 PCB R6** | **zamawiać** | Bez blokera; wysokość M1 na listwach wychodzi ok. 15,9 mm, nie 13,8 mm — mieści się w 16,5 mm, ale z zapasem 0,6 mm. |
| **P05 PCB R3** | **wstrzymać do jednej decyzji (MAJOR-1)** | Tuleja SW1 kończy się ok. 3,5 mm za krawędzią x = 0, a strefa panelu w S1 ma ok. 50 mm: dźwignia nie dojdzie do panelu, a nakrętki B3 nie da się założyć. Jeżeli wybierzesz przełącznik na panelu na przewodach (wariant A niżej), płytkę można zamówić bez zmian. |
| **P06 PCB R2** | **zamawiać** | Bez blokera; footprint WSK2512 jest spójny z biblioteką KiCada, ale nie udało mi się go porównać z kartą Vishay (strona zablokowana) — sprawdzić wydruk 1:1 z bocznikiem. |
| **P09 PCB R2** | **wstrzymana (jak w zadaniu)** | W plikach nie znalazłem błędu; zamówienie zależy od pomiaru modułu MAX31856 (lista pomiarów w sekcji P09). |
| **P10 PCB R2** | **zamawiać** | Bez uwag poza wspólnymi. |

**BLOCKER: brak.** W plikach nie znalazłem niczego, co robi z płytki złom albo wymaga poprawek lutownicą. Jedyny MAJOR (P05 SW1) jest problemem mechaniki obudowy, nie produkcji. Ma jednak wyjście bez zmiany PCB.

## Co zrobiłem i czym (dowody)

- **Integralność paczek.** ZIP = `gerber/` (diff katalogów) dla wszystkich sześciu. Sumy `.zip.sha256` się zgadzają. Manifesty `MANIFEST.sha256.json`: 203/204/239/227/192/192 plików zgodnych, 0 niezgodnych.
- **Wiercenia z Excellonu** (`src/drills.py`). Obejmuje otwory NPTH, narzędzia, najmniejszy odstęp otwór–otwór liczony krawędź–krawędź i sloty: żadnych slotów.
- **Geometria z plików `.kicad_pcb`** (`src/dump_board.py`, pcbnew 10.0.6 w obrazie Docker, tylko odczyt). Zrzut obejmuje footprinty, pola z sieciami, otwory, przelotki, ścieżki i strefy. Na tych zrzutach `src/stack_checks.py` sprawdza strefy Ø7, części od spodu i otwory M3. Kolejne skrypty ad hoc sprawdzały J_BP, polaryzacje i wyprowadzenia, odległość miedzi od krawędzi oraz pierścienie.
- **Karty.** Pinouty TO-92 (MCP120, MCP1525, MCP1700, MCP1702) i INA240 sprawdziłem w lokalnych wyciągach kart (`P06-R2-review/reference/datasheets`, `P05-R3-review/reference/datasheets`). E-Switch 100 sprawdziłem na rysunku z karty (s. 5, 6, 11, wyrenderowane i obejrzane). EEU-FR1C221 potwierdziłem w źródłach dystrybutorów: 6,3 × 11,2 mm, raster 2,5 mm ([TME](https://www.tme.com/us/en-us/details/eeufr1c221/tht-electrolytic-capacitors/panasonic/), [RS](https://us.rs-online.com/product/panasonic-electronic-components/eeu-fr1c221/70257659/), [Octopart](https://octopart.com/part/panasonic/EEU-FR1C221)).
- **Oględziny** `podglad/CAM-top.png` P02, P03, P05, P06, P09.
- **Czego nie zrobiłem.** Nie powtarzałem DRC ani kontroli CAM (wyniki są w `verification/` paczek, a zasada 3 każe nie powtarzać kontroli bez zmian). Nie porównałem footprintu WSK2512 z kartą Vishay: `vishay.com` i `datasheet.octopart.com` są zablokowane przez politykę sieci (403).

## 1. Stos S1 (wspólne dla wszystkich płytek)

| Sprawdzenie | Wynik |
|---|---|
| Otwory M3 Ø3,2 NPTH | Wszystkie płytki mają otwory każdego zajmowanego slotu w x = 4 / 49 (+53,5 na slot), y = 14 / 86: L 12, 2/3 8, 1/3 4. Współrzędne z Excellonu co do 0,01 mm. Otwory pokrywają się między poziomami 1–4. |
| Strefy Ø7 wokół M3 | Brak obrysu części, ścieżki ani przelotki w strefie (`stack_checks.py`, obrysy courtyard, wszystkie warstwy). |
| J_BP (krawędź A) | Środki: P02 133,5 (S3); P03 26,5 / 80,0 / 133,5; P05 26,5 / 80,0; P06 80,0 (S2); P09 26,5; P10 26,5 mm w układzie płytki. Pin 1 zawsze od mniejszego x (trójkąt i „1” na nadruku). Obrys korpusu dochodzi do y = −0,49 (courtyard z marginesem 0,5), więc czoło jest równo z krawędzią. Rząd parzysty bliżej krawędzi. |
| Listwy serwisowe (krawędź B) | Wszystkie w pasie x = 10–43 mm slotu, kołki za krawędzią (courtyard do y = 106,5). Pin 1 przy większym x, zgodnie z opisem w MECHANIKA. |
| Części poza obrysem | Tylko zamierzone: kołki J_SV (krawędź B), wtyki J_BP (krawędź A, −0,5 mm), dźwignia SW1 P05 (x < 0), wtyk J2 P02 (x > 160, ściana wejść). Nic nie wchodzi w szczelinę 0,5 mm między P05 i P09 ani między P06 i P10. |
| Części od spodu | Tylko SMD. SOIC od spodu tylko w P02 (U9, poziom 1 — dozwolone). P03 i P10 nie mają części od spodu, co zgadza się z brakiem dolnego nadruku w ZIP. Odległość od pól THT ≥ 1 mm wszędzie poza R26 w P06: obrys courtyard 0,99 mm od pola U3.1. Obrys ma margines 0,25 mm, więc korpus stoi ok. 1,2 mm od pola — bez znaczenia. |
| Wysokości | Najwyższe na poziomach 2–4: M1 P03 ok. 15,9 mm (szacunek niżej), P09 moduły 14,1 mm (szacunek pakietu), P05 SW1 11,4 mm (karta: 11,43) i C1 11,2 mm, P06 R21 3–5 mm nad laminatem. P02 (limit 21,5 mm): TO-220 na stojąco ok. 19 mm, C12 leżący Ø16 ok. 16,5 mm. Bilans szczeliny 20 mm: 16,5 (góra) + 1,5 (SMD/końcówki od spodu wyższej płytki) = 18 mm. |

**Uwaga do P12 (MINOR, nie dotyczy zamówienia):** na tych samych pinach P03 J_BP2 ma 16 = PFAIL_N i 17/19/20 = 5V_SYS, a P05 J_BP2 ma tam GND. Pakiet P05 to opisuje (`docs/J_BP.csv`: „P12 nie łączy”). Jednak przy „torach P12 pionowo” jeden wspólny pas dla całego złącza zwarłby 5V_SYS z GND. P12 musi prowadzić z J_BP2 obu płytek tylko piny 2–14 i 18. Proponuję wpisać to wprost do zadania P12.

## 2. P05 PCB R3

### MAJOR-1 — SW1 nie sięga panelu; tuleja B3 z nakrętką się nie zmieści

**Dowód.** Footprint `P05:ESW_100DP_M6` na płytce (obrót 180°):
- otwory wspornika w x = 3,9 mm (y = 63,96 / 69,04);
- biegun A w x = 16,6, biegun B w x = 20,41;
- czoło wspornika ok. x = 3,65 (wspornik 0,5 mm, karta s. 11).

Karta s. 6 (Bushing Options) podaje długość tulei mierzoną od wspornika: **B3 / B4 = 7,10 mm**, B1 = 8,89, B5 / B9 = 7,52. Tuleja B3 kończy się więc w x ≈ 3,65 − 7,10 = **−3,45 mm**, czyli 3,45 mm za krawędzią płytki. Dźwignia T1 ma 10,41 + 1,78 mm (s. 5, dopisek dla B3 / B4), więc jej koniec leży w x ≈ −15,6 mm.

S1 rezerwuje na panel ok. 50 mm (`STUDIUM-FORMATU-S1.md`, w. 86: „50 mm panelu + 160 mm stosu + 15 mm wejść”), bo stoi tam P11 i wtyki DT. Obudowa nie jest zaprojektowana, ale panel nie będzie tuż przy krawędzi x = 0. Nawet z panelem przyłożonym do samej krawędzi zostaje 3,45 mm gwintu. To za mało na ściankę ≥ 1,5 mm i nakrętkę 1/4-40 (zwykle 2,4–3,2 mm). Decyzja z 4.10 („B3 z gwintem i nakrętką na panel”) jest więc na tej płytce niewykonalna, a położenia przełącznika po zamówieniu nie da się zmienić.

**Propozycje (do wyboru):**
- **A (bez zmiany PCB, zalecam).** Przełącznik na panelu (dowolny DPDT ON-ON z tuleją z gwintem, obwód „suchy”, więc złocone styki) połączony przewodami z polami SW1: 1, 2, 3, 4 (GND), 5 i 6 według netlisty. Otwory Ø1,85 przyjmą przewód AWG24–20. Oprawę przełącznika łączyć z GND przez pole wspornika (decyzja ESD z 2.10 zostaje). P05 można wtedy zamówić od razu. Kod E-Switch w BOM / ZAKUPY przestaje wtedy obowiązywać.
- **B (R4 płytki).** Przesunąć SW1 możliwie do krawędzi: środek otworu wspornika ok. x = 1,9 (pierścień 0,45 mm i prześwit miedzi 0,5 mm). Tuleja B3 wystaje wtedy ok. 5,2 mm, co wystarcza na panel 1,5 mm z nakrętką tylko wtedy, gdy panel dotyka krawędzi płytki. To kłóci się z 50 mm strefy panelu, więc B ma sens tylko po zmianie koncepcji panelu.
- **C.** Przełącznik zostaje na płytce jako ustawiany serwisowo przez otwór w panelu (dźwignia nie wystaje). Wymaga makiety.

**Przy okazji (MINOR, dokumenty):** BOM i `ZAKUPY.md` nadal podają kod **100DP1T1B4M6RE** (tuleja B4 bez gwintu), a decyzja 4.10 mówi B3. Przy wariancie A kod E-Switch znika. Przy B lub C — 100DP1T1**B3**M6RE**H**: „H” to nakrętki, dostępne tylko z tuleją gwintowaną (karta s. 2).

### Sprawdzone bez uwag

- **SW1 względem rysunku M6-DP** (s. 11):
  - kolumny w rastrze 4,70 (3 otwory na 9,40);
  - odstęp kolumn 3,81;
  - wspornik 12,70 przed biegunem A, 2 otwory co 5,08, symetrycznie wobec środkowego rzędu;
  - otwory Ø1,85 jak w karcie (wyprowadzenie 1,27 × 0,76, przekątna 1,48, luz 0,37);
  - pole 2,8 (pierścień 0,475).

  Biegun A (1-2-3) jest bliżej dźwigni, B (4-5-6) dalej, zgodnie z widokiem z boku (pin 3 12,75 od wspornika, pin 6 o 3,81 dalej). Wspólne 2 i 5 leżą w środku rzędu. Ewentualne lustro numeracji 1↔3, 4↔6 zamienia tylko nazwę pozycji HI / LO, a tę i tak ustala ODBIOR 13. Nóżki wspornika = pad 4 = GND (zmiana z 2.10 obecna).
- **C1 EEUFR1C221.** Footprint CP_Radial_D6.3mm_P2.50mm, otwór 0,8 przy wyprowadzeniu Ø0,5, pad 1 (+) = 5VA_P05, nadruk „+” i półksiężyc po stronie „−” poprawne.
- **C35** (2.10): 1206 w BOM i na płytce, 5VA_P05 / GND, przy C6 — zgodne.
- **Reguła 0,15 mm** (wylewka–pola w pierścieniu U1 / U3): JLCPCB dla 2 warstw i 1 oz dopuszcza 0,127 mm (5 mil), więc 0,15 przechodzi. Maska bez powiększenia (`pad_to_mask_clearance 0`) daje między polami LQFP 0,5 mm mostek ok. 0,2 mm, wobec 0,1 mm minimum dla zielonej maski.
- **Diody i układy.** Diody D1–D3 1N4148: katoda (pad 1) do 5V_SYS, anoda do cewek — gaszenie. MCP120 (bondout D: 1 RST, 2 VDD, 3 VSS) i MCP1700 (1 GND, 2 VIN, 3 VOUT) zgodne z kartami.

## 3. P06 PCB R2

### MINOR-1 — footprint WSK2512 niezweryfikowany z kartą

**Dowód.** `R_Shunt_Vishay_WSK2512_T1.19mm_SenseE1.70`:
- pola prądowe 2,29 × 2,03 w (±2,985; ∓0,635) — jak w bibliotece KiCada;
- pola pomiarowe 1,70 × 0,76 w (±3,28; ±1,27) — biblioteka ma 1,40 w ±3,13.

Wewnętrzna krawędź pól pomiarowych (2,43 mm od środka) zostaje jak w bibliotece, przedłużenie idzie tylko na zewnątrz (koniec 4,13 mm, część kończy się w 3,175). Lutowności to nie pogarsza. Para Kelvina jest poprawna: pad 2 (K_PLUS) po stronie pada 1 (ECU_P1), pad 3 (K_MINUS) po stronie pada 4 (EGR_P1). INA240 (SOIC-8, karta: IN− = 1, IN+ = 8, REF2 = 3, REF1 = 7) jest podłączony zgodnie: R2 do pinu 1, R1 do pinu 8.

**Czego nie potwierdziłem.** Liczby 1,70 mm z karty Vishay 30108 (strona zablokowana). Wynik wyszukiwarki podaje dla WSK2512 wymiar E = 1,75 mm, ale bez kontekstu. **Proponuję:** przed wysłaniem położyć bocznik (albo jego rysunek z karty) na wydruku 1:1 strony montażowej. Ryzyko jest małe, bo zmiana tylko wydłuża pole na zewnątrz.

### MINOR-2 — kotwy opasek przy x = 0

Otwory NPTH Ø3,2 w x = 3,0 dają 1,4 mm laminatu do krawędzi. Kotwa J3 (y = 20,0) stoi 6,1 mm od środka M3 (4; 14). Strefa Ø7 jest wolna, ale opaska obejmująca kotwę przejdzie ok. 1 mm od dystansu. To uwaga F6 z recenzji 2.10 — bez zmian, sprawdzić przy przymiarce. Produkcyjnie bez znaczenia.

### Sprawdzone bez uwag

- **Tor prądowy** ECU_P1 / EGR_P1: wylewki na F.Cu i B.Cu, ≥ 4 mm na całej drodze J3–J4 (pcb-checks pakietu). Według IPC-2152 dla 35 µm na zewnątrz 10 A przy ΔT ≈ 20 °C wymaga ok. 4–4,5 mm na jednej warstwie, a tu są dwie warstwy równolegle. 6 A pracy to duży zapas. Najwęższe miejsce to pole prądowe bocznika (2,03 mm), krótkie i dociśnięte do części — akceptowalne.
- **J3 / J4:** otwór 2,4 mm (pole 4,5) pod przewód 2,5 mm² (żyła ok. 2,0 mm). `zone_connect 1` (szprychy) obecne na obu polach każdego złącza — zmiana z 2.10.
- **C17** (2.10): 1206 100 nF w BOM, na płytce przy J5.1, 5VA_P06 / GND — zgodne.
- **C3 EEUFR1C221:** jak C1 P05.
- **D1, D2:** D1 1N5819 — katoda 5VA, anoda 3V3 (zabezpieczenie LDO); D2 BAT85 — katoda 3V3, anoda REF25. Kierunki poprawne, nadruk „K” przy katodach.
- **TO-92:** MCP1525 (TO-92: 1 VSS, 2 VOUT, 3 VIN wg tabeli 3-1 karty), MCP1702 (1 GND, 2 VIN, 3 VOUT), MCP120 (D) — zgodne z netlistą.

## 4. P02 PCB R4

**MINOR-1 — bezpieczniki F1–F3 przy krawędzi A.** Oprawki Keystone 3568 stoją w y ≈ 0,6–6 mm (x ≈ 9–45 mm). Między nimi a P12 (ok. 18 mm od krawędzi A), pod P03 w odstępie 25 mm, wymiana bezpiecznika wymaga zdjęcia P12 albo rozkręcenia stosu. Elektrycznie bez uwag. Do decyzji przy obudowie; może wystarczy zapisać w instrukcji serwisowej.

**MINOR-2 — J1 (przewody do XT60).** Footprint nazywa się „2×2,5 mm²”, a MPN w BOM mówi „2 × 1,5 mm² to XT60”. Otwór 3,2 mm (pole 6,0) przyjmie oba przekroje, ale przy 1,5 mm² (żyła ok. 1,6 mm) lut wypełnia duży luz. Bez wpływu na zamówienie — ujednolicić opis.

**Sprawdzone bez uwag:**
- TO-220 (STPS20100CT: A1 / K / A2; SUP53P06: G / D / S) zgodne z netlistą: D1 to OR do VLOG, D2 to anody równolegle, Q1 / Q9 przeciwsobnie ze wspólnym źródłem.
- TO-92: 2N5551 / 2N5401 E-B-C, LM2936Z (1 OUT, 2 GND, 3 IN), TL431 LP (1 REF, 2 A, 3 K), MCP120 D.
- Diody Zenera BZX55: katoda do źródła P-MOS.
- Elektrolity pad 1 = +, LED pad 1 = katoda = GND.
- Otwory dużych THT: oprawki 1,78, P600 1,6, DO-15 1,2, TSR2 1,1, Phoenix GMSTBA 1,4 — wszystkie z zapasem 0,2–0,4 mm wobec wyprowadzeń.
- Miedź ≥ 1,0 mm od krawędzi (najbliżej D13), przelotki 0,9 / 0,4, ścieżki ≥ 0,3 mm, tor 5 A ≥ 4,1 mm (pakiet). Według IPC-2152 dla 5 A przy 35 µm i ΔT 10 °C potrzeba ok. 2–2,5 mm — zapas jest.

## 5. P03 PCB R6

**MINOR-1 — wysokość M1 zaniżona w dokumentach.** MECHANIKA podaje szacunek 13,8 mm. Licząc ze standardowych części wychodzi więcej:
- gniazdo żeńskie 8,5 mm;
- plastik listwy męskiej modułu 2,5 mm;
- płytka modułu 1,6 mm;
- najwyższy element modułu (USB-C 3,26 albo ekran WROOM ok. 3,1).

Razem ok. **15,9 mm**: w limicie 16,5, ale z zapasem 0,6 mm. Przy gniazdach 11 mm („high”) limit zostanie przekroczony. Nad M1 leży P05 (od spodu SMD ≤ 1,5 mm), więc fizycznie zostaje ok. 2,6 mm. **Proponuję** kupić gniazda o wysokości 8,5 mm i zmierzyć zestaw przed montażem. PCB tego nie zmienia.

**Sprawdzone bez uwag:**
- LTC4412 (1 VIN, 2 GND, 3 CTL = GND, 5 GATE, 6 SENSE) i AO3401A (S do 5V_M1, D do 5V_SYS — dioda podłożowa od zasilania do obciążenia).
- TPS3808 (MR i SENSE do 3V3_CORE) i LVC1G17 (1 NC, 2 A, 3 GND, 4 Y, 5 VCC).
- NPTH Ø2,7 pod dystanse SD1.
- Ścieżki 0,2 mm (JLCPCB 0,127), najbliższa miedź 0,74 mm od krawędzi.

## 6. P09 PCB R2 (wstrzymana — co zmierzyć przed zamówieniem)

Footprint `P09:MAX31856_XU`: 9 pól w rzędzie, raster **2,54 mm**, otwory **1,0 mm**, pola 1,7 × 2,0, pin 1 (VIN) kwadratowy, na górze rzędu, od krawędzi A. Obrys modułu w footprincie: rząd na jednym brzegu, płytka modułu ok. **19 mm** w stronę x = 53 i **2,0 mm** zapasu za skrajnymi pinami (rząd wyśrodkowany na boku 24,3 mm). Courtyard sięga x = 50,05 przy obrysie 53, a strefy Ø7 są wolne o 2,5 mm. Typowe moduły MAX31856 (Adafruit 3263 i klony) mają złącze 1 × 9 w rastrze 2,54 przy jednym boku i terminal przy przeciwnym, więc footprint jest zgodny z typową budową. „XU” nie ma rysunku, dlatego pomiar jest konieczny.

Do zmierzenia na obu egzemplarzach (suwmiarką, przed zamówieniem):
1. Raster listwy (8 odstępów = 20,32 mm) i średnica kołka (otwór 1,0 przyjmie kołek 0,64 mm kwadrat).
2. Odległość osi rzędu od brzegu modułu po stronie listwy oraz długość modułu w stronę terminala — ma wyjść ≤ ok. 19,5 mm, inaczej terminal wejdzie za x = 50,05.
3. Położenie rzędu wzdłuż boku modułu: odległość pinu VIN i pinu DRDY od bocznych brzegów (footprint zakłada po ok. 2 mm, symetrycznie).
4. Wysokość: plastik listwy, płytka, terminal — szacunek pakietu 14,1 mm wobec limitu 16,5.
5. Kolejność pinów od VIN do DRDY na obu egzemplarzach (napis, nie zdjęcie).

Poza tym bez uwag: U1 i U2 (SOIC) od góry, rezystory serwisowe od spodu poza strefami, JP1 i JP2 pionowe, nadruk obu stron.

## 7. P10 PCB R2

Bez uwag:
- J1 IDC 2×5 w x = 26,5, pin 1 od mniejszego x;
- J3 (OBD) z kotwą (NPTH 47; 51,5 / 62) poza strefą M3;
- PESD2CAN (1 / 2 linie, 3 GND);
- brak części od spodu, zgodnie z brakiem dolnego nadruku;
- miedź ≥ 1,97 mm od krawędzi.

## 8. Możliwości JLCPCB (2 warstwy, 1 oz) — wszystkie płytki

| Parametr | JLCPCB (standard) | Najgorszy przypadek w paczkach | Wynik |
|---|---|---|---|
| Ścieżka | 0,127 mm | 0,2 mm (P03, P05) | OK |
| Odstęp miedzi | 0,127 mm | 0,15 mm (P05 przy U1 / U3) | OK |
| Przelotka (otwór / pole) | 0,3 / 0,6 (pierścień ≥ 0,13) | 0,4 / 0,9 (pierścień 0,25) na wszystkich | OK |
| Najmniejszy otwór PTH | 0,3 mm | 0,4 mm | OK |
| Pierścień pól THT | ≥ 0,15–0,25 mm | 0,30 mm (P02 U5), reszta ≥ 0,35 | OK |
| Odstęp otwór–otwór (krawędź–krawędź) | 0,5 mm (różne sieci) | 0,69 mm (P05, przelotki przy U1) | OK |
| Miedź–krawędź | 0,3 mm | 0,74 mm (P03 ścieżka) | OK |
| Sloty, frezowanie wewnętrzne | — | brak | OK |
| Maska między polami (zielona) | 0,1 mm | ok. 0,2 mm (LQFP 0,5 mm, maska bez powiększenia) | OK |
| Nadruk | wysokość ≥ 1,0 mm, linia ≥ 0,153 mm | 1,0 / 0,15 mm | **NIT:** linia 0,15 jest 3 µm pod 0,153 z tabeli JLCPCB. W praktyce drukuje się poprawnie; najwyżej cienkie znaki będą słabsze. Bez zmiany. |

## 9. Podsumowanie ustaleń

| # | Płytka | Waga | Ustalenie | Propozycja |
|---|---|---|---|---|
| 1 | P05 | MAJOR | Tuleja SW1 (B3, 7,10 mm od wspornika) kończy się 3,45 mm za krawędzią, dźwignia ok. 15,6 mm; strefa panelu ok. 50 mm; nakrętka się nie zmieści | Wariant A: przełącznik na panelu na przewodach do pól SW1, zamówić bez zmian; albo R4 / makieta |
| 2 | P05 | MINOR | BOM / ZAKUPY: kod B4 wobec decyzji B3 | Ujednolicić po wyborze wariantu |
| 3 | P06 | MINOR | WSK2512: pola pomiarowe 1,70 mm niezweryfikowane z kartą (zmiana tylko na zewnątrz) | Wydruk 1:1 z bocznikiem przed wysyłką |
| 4 | P06 | MINOR | Kotwy opasek 1,4 mm od krawędzi, opaska ok. 1 mm od dystansu M3 | Przymiarka (F6 z 2.10) |
| 5 | P02 | MINOR | F1–F3 przy krawędzi A, za P12 | Decyzja serwisowa przy obudowie |
| 6 | P02 | MINOR | J1: nazwa 2,5 mm² wobec 1,5 mm² w BOM | Ujednolicić opis |
| 7 | P03 | MINOR | M1 ok. 15,9 mm, nie 13,8 (zapas 0,6 mm) | Gniazda 8,5 mm, pomiar przed montażem |
| 8 | P12 | MINOR | P03 J_BP2.16/17/19/20 (PFAIL_N, 5V_SYS) wobec GND na P05 J_BP2 | Zapisać w zadaniu P12: łączyć tylko 2–14 i 18 |
| 9 | wszystkie | NIT | Linia nadruku 0,15 wobec 0,153 mm | Bez zmiany |

## Skrypty

- `src/dump_board.py` — zrzut geometrii płytki do JSON (pcbnew, tylko odczyt; współrzędne względem rogu obrysu z linią 0,05 mm, w analizie odejmowane 0,025 mm).
- `src/drills.py` — Excellon: narzędzia, NPTH, najmniejszy odstęp otwór–otwór, sloty.
- `src/stack_checks.py` — strefy Ø7, części od spodu, otwory M3.

Uruchomienie: `scripts/egrlab-docker python3 Plytki/Recenzja-zamowienia-S1/src/dump_board.py <kopia>/Pxx.kicad_pcb <wyjście>.json` (na kopii katalogu `projekt/eda` w scratchpad, `EGRLAB_EXTRA_MOUNTS`), potem `python3 src/stack_checks.py Plytki/Format-S1/format-s1.json <katalog z JSON>` i `python3 src/drills.py <paczki…>`.
