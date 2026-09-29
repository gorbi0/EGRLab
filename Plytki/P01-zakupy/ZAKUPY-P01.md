# Zakupy P01 (PCB R1 / schemat R3) — TME + Farnell albo Mouser łączony z P02/P03

Stany i ceny netto sprawdzone 24.09.2026, bezpośrednio w TME (zapytanie `product/data` po symbolu), na stronach produktów Farnell oraz w Mouserze (strony produktów; później przez agregator findchips, bo Mouser blokował zapytania). Stan magazynowy nie jest rezerwacją.

**Wysyłka:** Mouser wysyła wszystko FedExem z USA i przesyłka jest darmowa dopiero od 300 zł. Przy zamówieniu za 73 zł opłata za wysyłkę wyniosła ok. 105 zł. W Farnellu wysyłka poniżej 200 zł kosztuje 29,99 zł, od 200 zł jest darmowa. Stąd dwa warianty dla siedmiu pozycji, których TME nie ma na stanie (D1, U3, R5–R11):

- **Wariant A — Farnell:** 6 pozycji z Farnella, D1 osobno (Farnell go nie ma). **Nie wykorzystany.**
- **Wariant B — Mouser łączony — ZAMÓWIONY 24.09 (22 pozycje, 65 szt.):** wszystkie 7 pozycji P01 plus części P02/P03, **bez 910-PA0003** (adaptery SO14 z innego źródła). Do progu 300 zł dobrane części P04–P10 (`MOUSER-dobor-P04-P10-wklej.txt`). Szczegóły na końcu pliku.

Stan faktycznie zamówionych części: `Zamowione/ZAMOWIONE.md` w katalogu głównym projektu.

Pliki do wklejenia:
- `TME-wklej.txt` — 49 pozycji, ok. 258 zł netto, format `symbol ilość` (**zamówione**);
- `TME-opcjonalne-wklej.txt` — śruby, nakrętki i podkładki M3 w paczkach po 100 oraz podstawka DIP-8, ok. 24 zł (pomiń, jeśli masz je w warsztacie);
- `FARNELL-wklej.csv` — wariant A (niewykorzystany): 6 pozycji, ok. 106 zł netto + 29,99 zł wysyłki; format `kod_Farnell,ilość` (przecinek, bez spacji), do pola „Szybkie zamówienie → Wklej listę”;
- `MOUSER-wklej.txt` — wariant A (niewykorzystany): tylko D1;
- `MOUSER-P01-P03-wklej.txt` — wariant B: 17 pozycji, format `nr_Mouser ilość` (**zamówione bez 910-PA0003**);
- `MOUSER-dobor-P04-P10-wklej.txt` — dobór do progu, 9 pozycji, ilości dodatkowe (**zamówione**).

**Zasada ilości:** BOM + zapas na tanich elementach, zaokrąglone w górę do minimum i wielokrotności TME. Kolumna „BOM” podaje ilość wymaganą przez projekt.

## TME

| Symbol TME | Zam. | BOM | Pozycje | Uwagi |
|---|---:|---:|---|---|
| SUP53P06-20-E3 | 3 | 2 | Q1, Q2 | oryginał; 123 szt. na stanie |
| STPS20100CT | 2 | 1 | D2 | oryginał; **tylko 2 szt. na stanie** |
| 5KP18A-DIO | 2 | 1 | D3 | Diotec 5KP18A zamiast Littelfuse 5KP18A-B; 5 kW, 18 V, P600; końcówka serii |
| 1.5KE18A-E3/54 | 2 | 1 | D5 | oryginał |
| BZX55C15-TAP | 4 | 2 | D4, D9 | oryginał |
| 1N4148-TAP | 5 | 3 | D6–D8 | oryginał |
| 2N5551TA | 7 | 5 | Q3, Q5–Q8 | onsemi, E-B-C; nóżki uformowane pod raster 2,54 (zamiast 2N5551G) |
| 2N5401YBU | 3 | 1 | Q4 | oryginał |
| LM2936Z-5.0/NOPB | 2 | 1 | U1 | oryginał (opis „0,5 A” w TME to błąd katalogu; układ ma 50 mA) |
| LM2903P | 2 | 1 | U2 | oryginał, TI |
| MCP120-450DI/TO | 2 | 1 | U4 | oryginał, wyprowadzenia D |
| L-934GD | 2 | 1 | LED1 | oryginał |
| EEUEB1J100SH | 2 | 1 | C1 | Panasonic 10 µF / 63 V, Ø5×11, raster 2 mm, niska impedancja (zamiast UPW1J100MDD) |
| B32529C1104J000 | 3 | 2 | C2, C4 | oryginał |
| EEUFR1H101 | 2 | 1 | C3 | oryginał |
| B32529C1103J289 | 2 | 1 | C5 | TDK, ta sama seria i ±5%, inny kod wyprowadzeń (zamiast …J000) |
| MKS2-1U/100-5%-R | 2 | 1 | C6 | oryginał WIMA MKS2D041001K00JO00 (minimum 2 szt.) |
| EEUFR1H220 | 2 | 1 | C7 | oryginał |
| K104K15X7RF5TH5 | 5 | 3 | C8, C10, C11 | Vishay K, ta sama seria, wersja taśmowana (zamiast …F53H5) |
| EEUFR1H470 | 2 | 1 | C9 | oryginał; 32 szt. na stanie |
| RDE5C1H101J0M1H03A | 2 | 1 | C12 | Murata 100 pF, C0G, ±5%, raster 5 mm (zamiast Vishay K101…) |
| C320C102J1G5TA | 2 | 1 | C13 | KEMET 1 nF, C0G, ±5%, raster 5,08 mm (zamiast Vishay K102…) |
| PR02-150R | 2 | 1 | R1 | Vishay PR02, ±5% zamiast ±1% — bez znaczenia dla R1 |
| PR02-2K2 | 2 | 1 | R23 | Vishay PR02, ±5% |
| PR02000201009JA100 | 2 | 1 | R27 | Vishay PR02, ±5% |
| MF0207FTE-1R | 2 | 1 | R2 | Yageo MF0207 0,6 W 1% (zamiast MFR-50) |
| MF0207FTE-820R | 2 | 1 | R3 | j.w. |
| MF0207FTE-10K | 7 | 5 | R4, R16, R26, R30, R32 | j.w. |
| MF0207FTE-100K | 7 | 5 | R12, R15, R21, R24, R31 | j.w. |
| MF0207FTE-2K2 | 2 | 1 | R13 | j.w. |
| MF0207FTE-4K7 | 6 | 4 | R14, R17, R19, R28 | j.w. |
| MF0207FTE-47K | 6 | 4 | R18, R20, R25, R33 | j.w. |
| MF0207FTE-470K | 2 | 1 | R22 | j.w. |
| MF0204FTE52-6K8 | 2 | 1 | R29 | Yageo 0204, 0,4 W, 1% — wersja 0207 ma zerowy stan; R29 traci < 40 mW |
| 3296W-1-502LF | 1 | 1 | RV1 | oryginał |
| MSTBA2.5/3G5.08 | 1 | 1 | J6 | Phoenix 1757255 |
| IC2.5/2-ST-5.08 | 1 | 1 | H_BAT (P01) | Phoenix 1786174, męski |
| MSTB2.5/2-ST-5.08 | 1 | 1 | EXT przy źródle | Phoenix 1757019, żeński |
| MX-5557-06R | 1 | 1 | H_PG | Molex 39-01-2060 |
| MX-5556GSL7F | 10 | 6 | H_PG | Molex 39-00-0429, złocone (wielokrotność 10) |
| SK129-63STS | 2 | 2 | HS1, HS2 | Fischer |
| ZL201-02G | 50 | 1 | J3 | listwa kołkowa 1×2 (minimum 50 szt.) |
| JUMPER-KPL | 20 | 1 | J3 | zworka 2,54 (minimum 20 szt.) |
| IB-6 | 4 | 2 | Q1, D2 | tulejka izolacyjna TO-220, Fischer |
| SMICA-TO220 | 10 | 2 | Q1, D2 | podkładka silikonowa TO-220, bez pasty (minimum 10) |
| TFF-M3X10/DR185 | 10 | 4 | mocowanie PCB | dystans M3×10, poliamid (izolacyjny wg BOM; minimum 10) |
| FIX-2.5X100-ST/BK | 100 | 1 | kotwa J5 | opaska 2,5×100 |
| FIX-3.6X150-ST/BK | 100 | 1 | kotwa J7 | opaska 3,6×150 |
| 216-206 | 6 | 4 | H_BAT + EXT | WAGO, tulejka izolowana 2,5 mm², 8 mm |

**Opcjonalnie:**
- M3X10/D7985B — śruby do TO-220;
- M3X6/D7985B — śruby do dystansów;
- B3/BN117 — nakrętki;
- B3/BN1074 — podkładki poliamidowe;
- 1-2199298-2 — podstawka DIP-8 pod U2.

## Farnell

| Nr Farnell | MPN | Zam. | BOM | Pozycje | Stan 24.09 | Netto | Uwagi |
|---|---|---:|---:|---|---|---:|---|
| 2845263 | TL431BILPRAG (onsemi) | 5 | 1 | U3 | 1998 szt. | 8,80 zł | zamiast TI TL431BILP; ±0,4% (TI: ±0,5%), −40…85 °C; minimum 5 szt. |
| 1083441 | YR1B54K9CC (TE) | 5 | 1 | R5 | 601 szt. | 18,70 zł | 0,1%, 15 ppm/°C, Ø2,3 × 6,3 mm (zamiast H4); minimum 5 szt. |
| 1083362 | YR1B10KCC (TE) | 5 | 3 | R6, R7, R10 | 59 280 szt. | 16,60 zł | j.w. |
| 1083506 | YR1B221KCC (TE) | 5 | 1 | R8 | 999 szt. | 20,55 zł | **221 kΩ zamiast 220 kΩ** — 220k nie ma w szeregu 0,1% (w Farnellu też brak); próg OVP przesuwa się o ok. 3 mV, a kalibracja RV1 to wyrównuje |
| 9501371 | RC55Y-26K1BI (Welwyn) | 1 | 1 | R9 | **brak; dostawy od 7.10.2026** | 18,53 zł | 0,1%, 15 ppm/°C, 250 mW, Ø2,5 × 7,2 mm; YR1B 26k1 Farnell nie prowadzi, H8 wycofany, innego przewlekanego 26k1 0,1% na stanie nie ma |
| 1083513 | YR1B249KCC (TE) | 5 | 1 | R11 | 833 szt. | 22,80 zł | 0,1%, 15 ppm/°C; minimum 5 szt. |

Razem ok. 106 zł netto + 29,99 zł wysyłki (Farnell podaje ceny bez VAT). Wszystkie pozycje, które są na stanie, wychodzą z magazynu europejskiego z dostawą w 1–2 dni. Nie ma tu pozycji z magazynu w USA, za które Farnell dolicza 110 zł. Przy R9 w zamówieniu zaległym Farnell daje wybór: wysłać wszystko razem albo od razu to, co jest na stanie. Strona dostaw nie mówi, czy druga paczka kosztuje dodatkowo. Wybór „wszystko razem” daje pewność jednej opłaty; wtedy zamówienie przyjdzie po 7.10.

**U3 od onsemi zamiast TI:** producenci różnie numerują skrajne piny TO-92 (katoda i REF). W P01 nie ma to znaczenia, bo piny 1 i 3 są zwarte (praca jako referencja 2,5 V), a anoda jest w środku u wszystkich producentów. RAG to wersja z taśmy, więc nóżki są zwykle już odgięte na raster 2,54 mm pod footprint `TO-92_Inline_Wide`. Jeśli przyjdą proste, odegnij skrajne jak przy każdym TO-92.

## D1 (15KPA24CA) — osobno

| Źródło | Stan 24.09 | Uwagi |
|---|---|---|
| Mouser 576-15KPA24CA | 1181 szt., 35,24 zł netto | Sam D1 zapłaci pełną opłatę FedEx (ok. 105 zł). Wysyłka jest darmowa od 300 zł, więc najlepiej dołączyć go do większego zamówienia, np. na części kolejnych modułów |
| TME 15KPA24CA-B (Littelfuse) | 0 szt., 10–18 tygodni | zamówienie zaległe |
| TME 15KPA24CATR-SMC (SMC Diode Solutions) | 0 szt., ok. 14 tygodni, 11,34 zł | te same parametry: 15 kW, dwukierunkowa, VBR 26,81–29,35 V, 371 A, P600 |
| Farnell | brak | ma tylko jednokierunkową 15KPA24A (24 tygodnie) — nie jest zamiennikiem |
| RS Components PL | brak | brak w katalogu |

Wszystkie zamienniki mieszczą się w istniejących footprintach PCB R1 (rastry, otwory, obrysy). Zmiany MPN (U3, R5–R11) i wartość R8 trzeba wpisać do BOM oraz do rejestru zmian przed montażem.

## Kupić lokalnie albo z zapasów

- **Przewód 2,5 mm², czerwony i czarny, po ok. 0,5 m (H_BAT).** TME sprzedaje LgY 2,5 wyłącznie na metry, minimum 10 m na kolor.
- **Przewód AWG22, 6 × 0,23 m (H_PG).** W TME tylko szpule 30 m.
- **Drut Cu 2,5 mm², ok. 3 cm (LK1).** Odcinek przewodu instalacyjnego z drutem, np. H07V-U / DY.
- **R34.** Odcięta nóżka rezystora albo drut 0,6 mm.
- **Bezpiecznik 5 A z oprawką przewodową przy źródle**, jeśli go jeszcze nie masz. W TME nie ma sensownej oprawki przewodowej na sztuki.
- **Zaciskarka do styków Mini-Fit Jr 4,2 mm**, jeśli jej nie masz. W TME gotowe przewody z zaciśniętym stykiem Mini-Fit są tylko w wersji męskiej, a wiązka H_PG wymaga żeńskich.

## Wariant B — Mouser łączony z P02/P03

Ceny Mousera w USD z findchips (24.09.2026), przeliczone po kursie NBP 3,857 zł/USD i zaokrąglone. Dokładne kwoty w złotych pokaże koszyk, który po przekroczeniu progu wyświetla „DARMOWA wysyłka”. P02 i P03 mają w bazie v6.1-rc1 status „schemat do recenzji”. Dlatego są tu tylko pozycje z konkretnym MPN w BOM, które recenzja najpewniej zostawi. Moduł ESP32-S3 i przetwornik AD użytkownik już ma.

| Nr Mouser | Szt. | Pozycje | ok. netto | Uwagi |
|---|---:|---|---:|---|
| 7 pozycji P01 (jak w `MOUSER-wklej.txt` z 24.09 rano) | — | P01: D1, U3, R5–R11 | 73 zł | D1 Littelfuse, U3 TI TL431BILP, R5–R11 TE YR1B (R8 = 221k) |
| 495-TSR2-2450 | 1 | P02 M3 | 47 zł | w TME ok. 45 zł |
| 495-TSR2-2433 | 1 | P02 M4 | 47 zł | w TME ok. 44 zł |
| 579-MCP120-300DI/TO | 1 | P02 U_SUP3 | 2 zł | U_SUP5 (MCP120-450) = zapasowa sztuka z zamówienia TME |
| 595-SN74HC08N | 1 | P02 U_READY | 3 zł | |
| 579-MCP23017-E/SP | 1 | P03 U17 | 7 zł | |
| 595-SN74HC139N | 1 | P03 U_CS | 6 zł | |
| 771-74LVC125AD-T | 10 | P02 U_SUPBUF; P03 U_IN1–4, U_OUT1–3; 2 zapasu | 10 zł | Nexperia 74LVC125AD,118; **w TME 0 szt.** |
| 595-TPS3808G33DBVR | 2 | P03 U5 + 1 zapasu | 14 zł | SOT23-6 |
| ~~910-PA0003~~ | ~~8~~ | adaptery SO14→DIP14: P02 1, P03 7 | — | **usunięty z koszyka 24.09** — adaptery z innego źródła, np. Kamami „Adapter PCB SOP14 na DIP14” |
| 910-PA0085 | 1 | adapter SOT23-6→DIP-6 dla P03 U5 | 10 zł | Chip Quik |

Razem ok. 326 zł netto, czyli powyżej progu 300 zł. Części, które TME też ma, są w Mouserze droższe łącznie o ok. 8 zł. Jeśli koszyk pokaże mniej niż 300 zł, można dołożyć jedną z tych pozycji (w TME obu brak na stanie):

| Nr Mouser | Szt. | Pozycje | ok. netto | Ryzyko |
|---|---:|---|---:|---|
| 200-SSW10801GD | 1 | P03 J_DAQA (Samtec SSW-108-01-G-D) | 10 zł | złącze do pary z P05, której jeszcze nie zaprojektowano |
| 651-1804807 | 1 | P02 J_VMOTORA (Phoenix PC 4/3-G-7,62) | 22 zł | VMOTOR prowadzi do P07, a P07 jest wstrzymany |

**Adaptery zamiast DIP:** 74LVC125A nie występuje w obudowie DIP u żadnego producenta (TI SN74LVC125ANS to też SMD). Odpowiedniki DIP (74HC125, 74AHC125) nie mają Ioff, na którym opiera się projekt: `docs/02-interfejsy.md` v6.1-rc1 zakazuje automatycznej zamiany buforów. TPS3808 ma tylko obudowy SOT-23 i SON. Sam adapter to zwykła płytka: Kamami sprzedaje „Adapter PCB SOP14 na DIP14” po 1,50 zł, bez pinów, wysyłka 8,90–14,90 zł. PA0003 jest na liście tylko dlatego, że dobija Mousera do progu. Bez niego zamówienie spada do ok. 219 zł i wraca opłata ok. 105 zł, więc zamiana na tańsze adaptery wychodzi mniej więcej na zero. Adapter SOT23 z Kamami nie ma w opisie wersji 6-pinowej, więc dla U5 zostaje PA0085.

Świadomie pominięte:
- STPS20100CT ×2 do P02-HOLD — w Mouserze 0 szt.;
- HSA2547RJ (R_CHARGE P02-HOLD) — w Mouserze ok. 31 zł, w TME ok. 14 zł;
- złącza Mini-Fit Jr i gniazda IDC z P02/P03 — w BOM nie mają MPN, najpierw decyzja projektowa;
- bank HOLD (Samwha HC1V229M35045HA) — w TME.

**Przy zakupach P02/P03:** części z tej tabeli są już kupione z wyprzedzeniem — odjąć je od list tych modułów.

### Dobór do progu z P04–P10 (24.09)

Bez PA0003 koszyk ma ok. 219 zł netto. Dobrane zostały części z konkretnym MPN w BOM v6.1-rc1, potrzebne w kilku modułach albo nieosiągalne w TME. Lista do wklejenia: `MOUSER-dobor-P04-P10-wklej.txt`. Ilości są **dodatkowe**, ponad to, co już jest w koszyku.

| Nr Mouser | +Szt. | Pozycje | ok. netto | Uwagi |
|---|---:|---|---:|---|
| 595-INA240A2EDRQ1 | 2 | P06 U3; P07 U2 albo zapas | 35 zł | **TME 0 szt., Mouser tylko 23 szt.**; według EGRLab-AKTYWNE tor INA240/MCP3201 w P07 zostaje |
| 579-MCP3201-BI/P | 2 | P06 U_ADC; P07 U_ADC albo zapas | 29 zł | DIP8 |
| 579-MCP6022IP | 1 | P06 U_BUF | 7 zł | DIP8 |
| 579-MCP1525ITO | 1 | P06 U_REF | 4 zł | TO-92 |
| 579-MCP1702-3302E/TO | 1 | P06 U_LDO | 3 zł | TO-92 |
| 771-74LVC125AD-T | 15 | P04 3, P05 4, P06 2, P08 2, P09 2, P10 1 + 1 zapasu | 15 zł | **TME 0 szt.**; razem w koszyku 25 szt.; P07 (4 szt.) pominięta |
| 595-SN74HC08N | 7 | P04 U10, U12, U_LINK, U_LINK2; P05, P06, P08 U_READY | 21 zł | razem w koszyku 8 szt. |
| 579-MCP120-300DI/TO | 3 | P05, P06, P08 U_SUP3 | 7 zł | razem w koszyku 4 szt. |
| 579-MCP120-450DI/TO | 3 | P05, P06, P08 U_SUP5 | 7 zł | P02 U_SUP5 = zapas z TME |

Razem ok. 129 zł, cały koszyk ok. 347 zł netto. Ceny to wartości za 1 szt. z findchips w USD × 3,857, więc przy większych ilościach koszyk wyjdzie raczej taniej. Jeśli chcesz mniej, najpierw zdejmij 74HC08 i MCP120, bo TME też je ma. Pierwsze pięć pozycji plus 74LVC125AD daje ok. 312 zł.

Pominięte w doborze: P07 (wstrzymany) poza INA240/MCP3201; ADR4525BRZ (brak danych o stanie w Mouserze, w TME 0 szt.); TBD62083APG (jest tylko w TME); TPS2553DBVR (Mouser ma tylko wersję „-1”, inną niż w BOM); przekaźniki G6K-2F-Y (wersja SMD, do wyjaśnienia w recenzji); moduły MAX31856 i złącza bez MPN.

**Adaptery do dokupienia gdzie indziej (stan BOM v6.1-rc1, bez P07):** SO14→DIP ×18 (P02 1, P03 7, P04 3, P06 2, P08 2, P09 2, P10 1), SOIC8→DIP ×2 (P06, P10), SOT23-6→DIP ×1 (P08; P03 ma PA0085 w koszyku), SOT23→DIP ×1 (P10).

**Zamówione w Kamami 24.09.2026** (adaptery, goldpiny, podstawki, 1N4148; rejestr w `Zamowione/ZAMOWIONE.md`) — poza SOT23-6 dla P08: Kamami ma tylko 3-pinowy adapter SOT23.
