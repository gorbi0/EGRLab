# Recenzja P05-R1 (DAQ)

27.09.2026 · Claude. Przedmiot: `Plytki/P05-R1-review` Astry (25.09.2026). Pakiet nietknięty: 151/151 plików zgodnych z manifestem, pracowałem na kopii. Zakres: poprawność, wykonalność, zgodność z interfejsami i kartami katalogowymi, bez oceny zasadności.

**Uzupełnienie 28.09.2026:** kartę AD7606B Rev. B dostarczył użytkownik (kopia: `zrodla/AD7606B-RevB.pdf`, SHA256 `c4b8a6bd…a8288`). Zamyka to P5-04: wszystkie 64 piny i odsprzęganie są zgodne z kartą. P5-02 przeliczyłem na prądzie AVCC z karty. Mój szacunek z 27.09 (25–35 mA przez R1) był zawyżony; teraz uwzględniam też dryft temperaturowy TSR. P5-01 uzupełniłem o wytyczne layoutu z karty.

## Werdykt

**Logika, połączenia i wyprowadzenia są poprawne.** Łańcuch DAQ_OK, bramkowanie cewek, bufory Ioff, przekaźniki (wyprowadzenia, biegunowość cewki), AUX i interfejsy z P03-R4, P04-R2.1 i P02-R3 zgadzają się z netlistą i kartami. Wszystkie 64 piny AD7606B odpowiadają karcie Rev. B dla trybu programowego z interfejsem szeregowym. Świeże ERC, DRC i eksport netlisty są czyste i zgodne z pakietem.

**Przed zamówieniem PCB trzeba poprawić dwie rzeczy:**

- **P5-01 (layout):** kondensatory odsprzęgające AD7606B po prawej stronie układu stoją 7–21 mm drogi od pinów, na ścieżkach 0,20–0,25 mm. Dotyczy REFCAP, REFIN/REFOUT, obu REGCAP i AVCC 37/38/48. Karta każe stawiać je bezpośrednio przy pinach. Tuż przy tych pinach jest wolne miejsce. Dodatkowo wyjście DOUT biegnie po B.Cu pod lewym rzędem pinów układu.
- **P5-02 (progi):** okno DAQ_OK jest węższe, niż pozwala tolerancja TSR 2-2450 (±2 % plus dryft temperaturowy). W upale sprawna przetwornica na granicy tolerancji może dać DAQ_OK = 0. Poprawka to dwie wartości: R5 5,90 kΩ → 6,04 kΩ i R7 5,23 kΩ → 5,11 kΩ. Okno pozostaje wewnątrz 4,75–5,25 V.

Pozostałe punkty to kontrole odbiorcze, drobne zmiany wartości i dokumentacja.

## Co sprawdziłem

| Kontrola | Wynik |
|---|---|
| Integralność pakietu | 151/151 plików zgodnych z `release-manifest.json`, brak plików spoza manifestu |
| ERC / netlista (świeży eksport z kopii) | 0 naruszeń, 8 arkuszy; 110 części, 421 pinów — identyczne z `verification/P05.xml` |
| DRC (świeży, wszystkie ważności, zgodność ze schematem, wypełnienie stref) | 0 / 0 / 0 |
| Netlista pin po pinie | Wszystkie 421 piny: DAQ_OK, MEAS_PERMIT, bufory, domyślne stany, przekaźniki, AUX, B2B, LV05, DAQOK, VSENSE |
| AD7606B Rev. B | Tab. 9 (s. 13–15, funkcje pinów), tab. 22 (s. 34, piny danych według trybu), referencja (s. 26), tryby i reset (s. 27), czasy (s. 8), maksymalne wartości (s. 12), zasilanie (s. 7), wejścia analogowe (s. 24), kalibracja (s. 31–32), layout (s. 52) |
| Inne karty | G6K (Omron: tabela cewek, rysunek wyprowadzeń G6K-2P-Y, wykresy temperaturowe), TBD62083A (Toshiba 2026-05-13, s. 1, 4, 5), MCP120 (DS11184D), MCP1700 (DS20001826F), TLV1702-Q1 (SLOS890C), 74LVC125A (Nexperia Rev. 12, s. 6), TRACO TSR 2 |
| Geometria | Drogi po miedzi od pinów U1 do kondensatorów, przelotki GND przy masach U1, sąsiedztwo torów analogowych i cyfrowych na tej samej warstwie, płaszczyzna B.Cu pod ADC |
| Interfejsy | P03-R4 J1 (B2B, pin w pin — sprawdzone w wydaniu P03-R4), P04-R2.1 J5 (DAQ_OK: 74LVC125A z Ioff i 10 kΩ do GND), P02-R3 LV05 (5V_SYS wprost z TSR 2-2450) |
| Oględziny | 8 arkuszy schematu, 4 strony PCB, render warstw wokół U1 (`dowody/`) |

Skrypty w `skrypty/`. Pliki `*_U1.py` i `sasiedztwo_*.py` uruchamiać Pythonem KiCada z katalogu kopii `P05-R1-review`. Pozostałe działają w zwykłym Pythonie.

## Uwagi

| ID | Waga | Temat | Propozycja |
|---|---|---|---|
| P5-01 | **przed PCB** | Odsprzęganie AD7606B daleko od pinów; DOUT pod U1 — oba wbrew wytycznym karty | Przestawić C5–C7, C9–C13 przy prawej krawędzi U1; osobne przelotki mas; DOUT poza obrysem; limity drogi w `verify_pcb.py` |
| P5-02 | **przed PCB** | Okno DAQ_OK ciaśniejsze niż tolerancja TSR 2-2450 | R5 = 6,04 kΩ, R7 = 5,11 kΩ (0,1 %, 25 ppm); kryterium 5V_SYS w ODBIOR |
| P5-03 | odbiór | Zadziałanie przekaźników w upale bez gwarancji z karty | Pomiar napięcia zadziałania każdej sztuki (≤ 3,9 V przy ok. 23 °C) i VDS U4 |
| P5-04 | zamknięte | Piny AD7606B i kondensator REFIN/REFOUT | Zgodne z kartą Rev. B, bez zmian (szczegóły niżej) |
| P5-05 | drobna | Zasilanie wsteczne 3V3_DAQ przez R13 | R13 10 kΩ → 47 kΩ |
| P5-06 | opcja | VDRIVE > AVCC + 0,3 V przy twardym zwarciu 5V_SYS | Bilans poniżej; 1N5817 tylko jeśli chcesz zamknąć punkt |
| P5-07 | system | Pojemność na 5V_SYS blisko limitu TSR 2-2450 | Budżet w dokumentacji P02/integracji, próba rozruchu całości |
| P5-08 | dokumenty | Arkusz ADC, ODBIOR, INTEGRACJA, rejestr zakupów | Poprawki opisów |
| P5-09 | przyjęte | Okno bez histerezy | Bez zmian, uzasadnienie niżej |

### P5-01 — odsprzęganie AD7606B (layout)

Drogi po miedzi od pinu do pola kondensatora (`skrypty/odsprzeganie_U1.py`):

| Pin U1 | Funkcja | Kondensator | Droga | Uwagi |
|---|---|---|---:|---|
| 1 | AVCC | C4 100 nF | 2,4 mm | dobrze |
| 23 | VDRIVE | C8 100 nF | 3,6 mm | dobrze |
| 48 | AVCC | C7 100 nF | 7,5 mm | |
| 37 / 38 | AVCC | C5 / C6 100 nF | 11,3 / 14,8 mm | najbliższy kondensator AVCC dla tej pary to C5 |
| 36 | REGCAP (analog) | C9 1 µF | 9,3 mm | wyjście wewnętrznego LDO 1,9 V |
| 39 | REGCAP (cyfr.) | C10 1 µF | 14,3 mm | wyjście wewnętrznego LDO 1,9 V |
| 44 / 45 | REFCAPA/B | C13 22 µF 1210 | 12,2 / 11,7 mm | wyjście bufora referencji (4,4 V) |
| 42 | REFIN/REFOUT | C11 100 nF / C12 22 µF | 14,5 / 21,2 mm | TP13 jeszcze dalej |

Karta (s. 52) wymaga czegoś innego:

- kondensatory zasilania przy pinach zasilania i ich masach, najlepiej bezpośrednio przy nich;
- kondensatory REFIN/REFOUT i REFCAPA/B jak najbliżej pinów, po tej samej stronie płytki;
- osobne przelotki (jedna lub kilka) dla każdego pinu masy;
- możliwie szerokie ścieżki do AVCC i VDRIVE.

Karta dopuszcza też jeden 100 nF wspólny dla pinów 37 i 38, jeśli stoi blisko.

Ścieżki P05 mają 0,20–0,25 mm i biegną nad płaszczyzną B.Cu oddaloną o 1,5 mm. To ok. 0,9 nH/mm, więc 12 mm daje ok. 10 nH: 0,6 Ω przy 10 MHz i 3 Ω przy 50 MHz. Kondensator 22 µF X7R 1210 sam ma kilka mΩ i ok. 1 nH. Przy częstotliwościach pracy przetwornika SAR kondensator jest więc praktycznie odcięty przez ścieżkę. `verify_pcb.py` sprawdza tylko „≤ 15 mm” i dlatego to przepuszcza.

Obszar tuż na prawo od U1 (x 115–121 mm, y 38–50 mm) zajmują dziś tylko te długie ścieżki. Pod nim leży chroniona płaszczyzna B.Cu (`ANALOG_GND_PLANE_*`), więc przelotki GND trafiają prosto w nienaruszoną masę.

Propozycja dla R2:

- C13 (REFCAP), C11 i C12 (REFIN/REFOUT), C10, C9 oraz jeden 100 nF dla pary AVCC 37/38 i jeden dla 48 postawić przy pinach w dwóch kolumnach: 0603/0805 bliżej, 1210 dalej. Cel: droga ≤ 3 mm dla 0603/0805 i ≤ 6 mm dla 1210, ścieżki ≥ 0,4 mm. Doprowadzenie 5VA do pinów AVCC ≥ 0,5 mm albo lokalna wylewka.
- Każde pole GND tych kondensatorów dostaje własną przelotkę do płaszczyzny B.Cu. Własne przelotki dostają też piny mas po prawej stronie: REFGND 43/46 oraz AGND 40/41/47.
- Między polami kondensatorów a końcami padów U1 zostawić ≥ 1 mm na grot przy lutowaniu LQFP 0,5 mm.
- TP13–TP16 przenieść do ich kondensatorów, zamiast na końce długich ścieżek. Dziś przedłużają anteny na najczulszych węzłach.
- W `verify_pcb.py` zastąpić „≤ 15 mm” limitami dla każdego pinu. Dodać próbę ujemną, np. C13 przesunięty o 5 mm.

**Linia cyfrowa pod U1.** AD_DOUT_LOCAL (pin 24, wyjście danych szeregowych) schodzi przelotką na B.Cu i biegnie pod lewym rzędem pinów U1 (x 102,85 mm, y 45–48 mm), razem ok. 30 mm po B.Cu do U11 (`skrypty/trasa_DOUT.py`, `skrypty/pod_U1.py`). Tnie przy tym płaszczyznę masy pod rogiem układu. Karta (s. 52) zaleca nie prowadzić linii cyfrowych pod układem. Strefa `ANALOG_GND_PLANE_CORE` zaczyna się od x = 104 mm, więc lewy pas U1 nie jest chroniony. Propozycja: poprowadzić DOUT poza obrysem U1 i rozszerzyć strefę na cały obrys układu (x ≥ 101 mm). Poza tą linią pod U1 są tylko masy i przelotki GND.

Reszta rozmieszczenia wokół ADC jest dobra. Masy U1 mają przelotki do płaszczyzny w odległości 1,2–3,1 mm (`skrypty/masy_U1.py`). Kondensatory 220 pF na wejściach stoją nad pinami 49–64. Linie SPI nigdzie nie biegną na tej samej warstwie w odległości < 0,6 mm od torów analogowych (`skrypty/sasiedztwo_analog_cyfra.py`). Jedyne takie sąsiedztwo to TAP_P3/TAP_P4 wzdłuż linii cewek (21 i 12 mm na B.Cu), która w czasie pomiaru stoi w miejscu.

### P5-02 — okno DAQ_OK a tolerancja 5V_SYS

5V_SYS pochodzi wprost z TRACO TSR 2-2450 na P02. Dokładność ustawienia wynosi ±2 %, współczynnik temperaturowy ±0,02 %/K (przy 60 °C ±0,7 %). Do tego dochodzi regulacja: do 1 % obciążeniowej i 0,5 % liniowej.

5VA_P05 jest mniejsze o spadek na R1 1 Ω. AD7606B pobiera z AVCC (s. 7) 7,5 mA typowo w spoczynku (maks. 9,5 mA) i 8 mA przy 10 kSPS (maks. 10 mA). Przy nadpróbkowaniu ×8 i 10 kSPS na wyjściu wychodzi ok. 11 mA. Z LDO 3V3_DAQ (4–6 mA) daje to I(R1) ≈ 12–20 mA.

Narożniki progów liczę tym samym modelem co `verify_electrical.py` (`skrypty/okno_DAQ_OK.py`):

| Próg | Nominalny | Narożniki |
|---|---:|---:|
| Dolny, R5 = 5,90 kΩ (R1) | 4,826 V | 4,779–4,874 V |
| **Dolny, R5 = 6,04 kΩ (propozycja)** | **4,800 V** | **4,753–4,848 V** |
| Górny, R7 = 5,23 kΩ (R1) | 5,165 V | 5,118–5,213 V |
| **Górny, R7 = 5,11 kΩ (propozycja)** | **5,186 V** | **5,138–5,234 V** |

Zapas między 5VA a narożnikiem progu (dodatni = DAQ_OK pewne):

| Warunek | 5VA | R1 | Propozycja |
|---|---:|---:|---:|
| TSR −2 %, 25 °C, I(R1) 12–20 mA | 4,880–4,888 V | +6…+14 mV | +32…+40 mV |
| TSR −2 %, 60 °C (−0,7 %) | 4,846–4,854 V | −28…−20 mV | −2…+6 mV |
| TSR +2 %, 25 °C, 12 mA | 5,088 V | +30 mV | +50 mV |
| TSR +2 %, 60 °C (+0,7 %) | 5,124 V | −6 mV | +15 mV |

W R1 w upale sprawna przetwornica na granicy tolerancji może wyłączyć DAQ_OK. Przekaźniki się wtedy nie włączą i nie będzie pomiaru, a właśnie w upale pojawia się usterka EGR.

Proponowane wartości (E96, ta sama seria MBB0207 0,1 % 25 ppm) dają najszersze okno, które nadal spełnia regułę autorki: narożniki 4,753 V i 5,234 V leżą wewnątrz AVCC 4,75–5,25 V, więc reguła z `verify_electrical.py` przechodzi. Pełnej tolerancji TSR (±2 % i dryf) oba warunki razem nie pokryją. Zostaje przypadek przetwornicy na samej granicy ±2 % w upale. Dlatego w odbiorze trzeba zmierzyć rzeczywiste 5V_SYS: 4,93–5,07 V w temperaturze pokojowej daje w 60 °C zapas ≥ 25 mV po obu stronach.

Rezystory 0,1 % dla P05 nie są jeszcze kupione (`Zamowione/ZAMOWIONE.md`).

W `docs/ODBIOR.md`:

- **Krok 3:** zamiast „5VA 4,90–5,10 V” (sprzeczne ze specyfikacją TSR) wpisać „5V_SYS na P05 4,93–5,07 V przy ok. 23 °C; 5VA = 5V_SYS − I·1 Ω (12–20 mV)”.
- **Krok 5:** nowe narożniki.

### P5-03 — zadziałanie przekaźników w upale (odbiór)

Dane z kart:

- **G6K-2P-Y DC5:** 21,1 mA, 237 Ω; napięcie zadziałania ≤ 80 % (4,0 V) przy 23 °C. Na wykresie Omron (10 sztuk) najgorsza sztuka potrzebuje ok. 70 % przy 23 °C i ok. 79 % przy 60 °C, czyli wzrost ×1,13. Katalogowe 80 % przeskalowane tak samo daje ok. 90 % (4,5 V) przy 60 °C.
- **Dostępne napięcie cewki:** 5V_SYS minus VDS U4 przy 63 mA. Przy sterowaniu 5 V karta TBD62083A podaje RON ≤ 3,25 Ω. Dla 3,3 V z HC08 gwarantuje tylko VOUT ≤ 2 V przy 100 mA. Szacuję 0,2–0,3 V, więc na cewce 4,5–4,7 V przy 5V_SYS 4,8–4,9 V.

Typowo zapas jest duży: 4,5–4,7 V wobec ok. 4 V potrzebnych przy 60 °C. Z samej karty gwarancji jednak nie ma, a usterka EGR pojawia się właśnie w upale. Proponuję nie zmieniać projektu, tylko dodać do `ODBIOR.md` dwie kontrole:

- napięcie zadziałania każdego przekaźnika zasilanego wprost z zasilacza, przy ok. 23 °C: ≤ 3,9 V (co daje ≤ 4,4 V przy 60 °C);
- VDS na U4.18 przy trzech włączonych cewkach: ≤ 0,3 V.

Sztuki powyżej limitu wymienić; o innym wariancie cewki decydować dopiero po pomiarze. Połączenia przekaźników sprawdziłem: „+” cewki na pinie 1 (5V_SYS), „−” na 8 (OUT1), COM 3/6 do ADC, NO 4/5 do odczepów, NC 2/7 wolne. Diody D1–D3 mają katodę na 5V_SYS, COM U4 idzie na 5V_SYS, IN2–IN8 są na GND.

### P5-04 — AD7606B: piny i odsprzęganie (zamknięte kartą Rev. B)

Tryb programowy z interfejsem szeregowym (OS2–OS0 = 111, PAR/SER SEL = 1) — P05 jest zgodne z kartą:

| Pin | P05 | Karta Rev. B |
|---|---|---|
| 3–5 OS0–OS2 | wysoki | 111 = tryb programowy (tab. 13, s. 27; s. 34) |
| 6 PAR/SER SEL | wysoki | interfejs szeregowy |
| 7 STBY | wysoki | w trybie programowym ignorowany, zalecany stan wysoki |
| 8 RANGE | wysoki | ignorowany, ale musi być podłączony |
| 10 WR | wysoki (VDRIVE) | aktywny L zapis rejestrów tylko przez interfejs równoległy |
| 16–22, 30–33 DB0–DB6, DB12–DB15 | GND | w trybie szeregowym nieużywane: do AGND (tab. 22) |
| 24 DOUTA | U11A | wyjście danych szeregowych |
| 25/27/28 DOUTB/C/D | wolne | używane tylko przy 2 lub 4 liniach DOUT w CONFIG, inaczej niepodłączone (tab. 22) |
| 29 DB11/SDI | SDI z bufora | wejście szeregowe w trybie rejestrów |
| 34 REF SELECT | wysoki | referencja wewnętrzna |
| 36/39 REGCAP | osobno po 1 µF | osobno po 1 µF do AGND |
| 44/45 REFCAPA/B | zwarte, 22 µF X7R (Ceff ≥ 10 µF) | zwarte, ceramiczny 10 µF o niskim ESR |

Firmware v6.1 zapisuje CONFIG = 0x00 (jedna linia DOUT) i używa SPI w trybie 2. To zgodne z połączeniami P05 i z wiązaniem sterownika Linux `adi,ad7606`.

**REFIN/REFOUT (pin 42):** karta jest tu niespójna. Tab. 9 (s. 14) podaje 100 nF dla obu wariantów referencji. Rozdział „Reference” (s. 26) dla referencji wewnętrznej wymaga ceramicznego 10 µF. P05 ma oba (C11 100 nF + C12 22 µF z Ceff ≥ 10 µF), więc spełnia ostrzejszy wymóg. Zostawić. Umieszczenie: P5-01.

**Czasy (s. 8, 27):**

- pełny reset ≥ 3 µs, gotowość po 253 µs;
- między stabilnym AVCC/VDRIVE a resetem ≥ 10 ms;
- przy pierwszym resecie po włączeniu suma czasu ustalania i czasu od włączenia > 2 s — zgodnie z 2100 ms z `INTEGRACJA.md`.

Maksymalne wartości (s. 12): VDRIVE i wejścia cyfrowe ≤ AVCC + 0,3 V / VDRIVE + 0,3 V, wejścia analogowe ±21 V, prąd pinu niezasilającego ±10 mA. To podstawa P5-05 i P5-06.

W wersji z 27.09 pisałem, że pin 33 to „DB15/BYTE SEL” (nazwa z symbolu starszego AD7606). W AD7606B to po prostu DB15, w trybie szeregowym do AGND — P05 ma to dobrze.

### P5-05 — zasilanie wsteczne 3V3_DAQ przez R13

R13 10 kΩ podciąga linię ADC_CS od strony B2B do 3V3_DAQ. Przy P03 włączonym i P05 wyłączonym P03 trzyma CS w H, a R13 i R2 1 kΩ tworzą dzielnik: 3V3_DAQ ≈ 3,3 V · 1/11 = 0,30 V przy AVCC ≈ 0. To dokładnie granica „VDRIVE ≤ AVCC + 0,3 V” z karty. Krok 7 `ODBIOR.md` to wykaże.

Przy R13 = 47 kΩ zostaje 0,07 V. Gdy P03 jest wyłączony, wejście U9 nadal jest pewne: przy najgorszych upływach (74LVC125A: II ±5 µA, IOFF P03 ±10 µA do 85 °C) CS ≥ 2,6 V wobec VIH 2,0 V. Inne linie B2B mają rezystory do GND, więc nie tworzą takiej drogi.

### P5-06 — twarde zwarcie 5V_SYS: bilans (odpowiedź na pytanie 2 z `DLA-RECENZENTA.md`)

Model z jawnymi założeniami jest w `skrypty/zwarcie_5V_VDRIVE.py`: C1 rozładowuje się przez R1, MCP1700 bez ochrony przed prądem wstecznym (karta jej nie opisuje), 3V3_DAQ ok. 3 µF. Granica z karty AD7606B: VDRIVE ≤ AVCC + 0,3 V.

| Wariant | Maks. VDRIVE − AVCC | Kiedy | Ładunek przez diodę |
|---|---:|---|---:|
| Bez diody (R1) | 0,58 V | ok. 0,65 ms, AVCC ok. 1,2 V | — |
| BAT85 3V3_DAQ → 5VA | 0,36 V | ok. 0,54 ms | 2,8 µC |
| 1N5817 3V3_DAQ → 5VA | 0,19 V | ok. 0,46 ms | 3,9 µC |

Bez diody przekroczenie wynosi ok. 0,3 V ponad dopuszczalne, przez ułamek milisekundy, gdy AVCC ma już ok. 1,2 V, a ładunek to kilka µC z kondensatorów 3V3_DAQ. Ryzyko uszkodzenia oceniam jako małe.

Jeśli chcesz zamknąć ten punkt, wystarczy 1N5817 (DO-41, THT) z anodą na 3V3_DAQ i katodą na 5VA_P05 przy U12. W normalnej pracy dioda ma 1,7 V w kierunku zaporowym. Jej upływ płynie do 3V3_DAQ, a to obciążenie wynosi ≥ 6 mA (sam R2 3,3 mA), więc szyna nie rośnie. Z BAT85 zostaje 0,36 V. Decyzja należy do Ciebie.

### P5-07 — pojemność na 5V_SYS (system)

TSR 2-2450 dopuszcza 600 µF obciążenia pojemnościowego (modele 5 V). Suma kondensatorów na szynach 5 V w najnowszych pakietach P00–P11 to ok. 538 µF (`skrypty/pojemnosc_5V.py`). Nie obejmuje P01 (pakiet bez `parts.json`) ani kondensatorów samego modułu Waveshare. Z tego 470 µF to C1 w P05.

R1 1 Ω i miękki start TSR ograniczają prąd ładowania C1 (ok. 0,5 A przy narastaniu 5 V w 5 ms), więc rozruch prawdopodobnie przejdzie. Budżet warto jednak zapisać w dokumentacji P02/integracji i sprawdzić przy pierwszym uruchomieniu kompletu: 5V_SYS narasta bez restartów czkawkowych.

Nie podłączać LV05 pod napięciem. Przy 5 V na C1 przez 1 Ω udar ma do 5 A i obniża 5V_SYS pozostałym płytkom.

### P5-08 — dokumenty i spójność

- **Arkusz 3/8 (ADC):** kondensatory C4–C13 stoją w siatce z samymi etykietami sieci. Dopisać „Cx przy U1.nn”, jak na arkuszu 1 („C14 przy U2” …). Bez tego z samego schematu nie da się sprawdzić, który kondensator należy do którego pinu.
- **`docs/ODBIOR.md`:**
  - kroki 3 i 5 według P5-02;
  - nowe kontrole z P5-03;
  - krok 7: oczekiwane 3V3_DAQ ≈ 0,07 V po zmianie R13 (0,30 V przy R1).
- **`docs/INTEGRACJA.md`:**
  - dopisać z karty „≥ 10 ms od stabilnego AVCC/VDRIVE do resetu”;
  - kalibrację offsetu i wzmocnienia prowadzić w firmware, nie w rejestrach AD7606B. CHx_OFFSET obejmuje tylko ±128 LSB, a kompensacja wzmocnienia rezystory szeregowe do 65 kΩ (s. 31–32). Przewidywane w `PROJEKT.md` offsety przekraczają ±128 LSB na zakresach ±5 i ±2,5 V, a zastępcze rezystancje źródeł P05 (75–100 kΩ: 300k∥100k, 100k, 499k∥100k) przekraczają 65 kΩ.
  - Karta (s. 24) proponuje też kasowanie offsetu rezystorem o tej samej wartości na VxGND. Przy odczepach w adapterach i AUX przełączanym SW1 nie daje to stałego dopasowania, więc kalibracja programowa z `PROJEKT.md` jest właściwa.
- **`Zamowione/ZAMOWIONE.md`:** dla P05 wpisano „Samtec TSW-108-07-G-D”, a BOM P05-R1 wymaga TSW-108-08-G-D-NA (wariant do połączenia koplanarnego z SSW-RA). Kupować według BOM po zatwierdzeniu przekroju B2B.

### P5-09 — okno bez histerezy (przyjęte)

TLV1702 nie ma histerezy, a autorka świadomie jej nie dodała. Przy wspólnym wyjściu OC obu komparatorów prosta dodatnia pętla i tak by nie zadziałała, bo zwalniałaby drugi próg. Filtr R1/C1 (339 Hz) tłumi tętnienia TSR (75 mVp-p) o rzędy wielkości. Drgania DAQ_OK są więc możliwe tylko przy powolnym przejściu 5VA przez próg, czyli w stanie awarii zasilania. Zostawiam bez zmian.

## Co jest dobrze

- Łańcuch DAQ_OK: okno na 5VA (U2 ADR4525, U3 TLV1702, wspólne wyjście OC), MCP120-300 na 3V3_DAQ i MCP120-450 na 5V_SYS przez U8 (wejście 5 V tolerowane).
  - MCP1700 daje ≥ 3,20 V (±3 %), a MCP120-300 wyzwala najwyżej przy 3,0 V.
  - MCP120 opóźnia zwolnienie o 150–700 ms.
- MEAS_PERMIT = MEAS_EN ∧ DAQ_OK w sprzęcie. Bez zasilania P05 styki NO są rozwarte, więc stan bezpieczny nie zależy od programu.
- Bufory 74LVC125A zasilane z VDRIVE: wejścia AD7606B nie przekroczą VDRIVE + 0,3 V. DOUT jest włączany tylko przy CS = L, więc wspólny MISO na P03 jest wolny. BUSY idzie przez bufor z Ioff, stany domyślne są po obu stronach buforów.
- Wszystkie piny AD7606B zgodne z kartą Rev. B, łącznie z odsprzęganiem REFIN/REFOUT według ostrzejszego z dwóch wymogów karty.
- Wejścia sygnałowe (CH1–CH5, CH7, CH8) mają ≥ 100 kΩ szeregowo, więc zacisk ±21 V jest zabezpieczony zgodnie z kartą. Wszystkie 8 kanałów jest używanych (CH6 przez 10 kΩ do GND).
- DAQ_OK do P04: wyjście HC08 3,3 V, po stronie P04 74LVC125A z Ioff i 10 kΩ do GND. Nie ma zasilania wstecznego w żadnym kierunku.
- Płaszczyzna B.Cu pod rdzeniem ADC, referencją i wejściami jest chroniona regułami (poza lewym pasem U1, P5-01). Masy U1 mają krótkie przelotki. Wejścia analogowe nie sąsiadują z liniami SPI.
- Odtwarzalność: pełny łańcuch skryptów, proweniencja DRC, próby ujemne. Świeże ERC, DRC i netlista zgodne z pakietem.

## Otwarte bez zmian (z pakietu)

- Przekrój mechaniczny i test ciągłości pary B2B P03–P05.
- Wariant SW1.
- Ceff C12/C13 pod napięciem.
- Sekwencja startowa firmware (2100 ms) i obsługa zaniku zasilania P05.
- Odbiór sprzętu: NIE ZBADANO.

## Kolejność dla R2

1. P5-02 i P5-05: R5 6,04 kΩ, R7 5,11 kΩ, R13 47 kΩ; tabele, `verify_electrical.py` (nowe narożniki) i ODBIOR.
2. P5-01: przestawić odsprzęganie i przelotki mas przy U1, poszerzyć doprowadzenie 5VA, wyprowadzić DOUT spod U1 i rozszerzyć strefę płaszczyzny, dodać limity i próbę ujemną w `verify_pcb.py`, uruchomić pełny łańcuch i oględziny.
3. P5-03, P5-07, P5-08: dokumenty. P5-06 według Twojej decyzji.
