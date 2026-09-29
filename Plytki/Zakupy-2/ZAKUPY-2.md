# Lista zakupowa 2 — P00, P02–P06, P08–P11

*28.09.2026. Ceny i stany sprawdzone tego dnia w TME, Kamami, Farnellu, Mouserze i DigiKey. Lista nie jest zamówieniem: po złożeniu zamówienia dopisać pozycje do `Zamowione/ZAMOWIONE.md` i `zamowione.csv`.*

> **29.09.2026 — LISTA DO PRZELICZENIA, nie zamawiać w tej postaci.** Po decyzjach z 29.09 zmieniają się: format płytek (S1, `Plytki/Format-S1/`), P02 R4 zamiast P01 i P02 R3, posiadane rezystory THT zamiast nowych, nowe części w SMD 1206, SW1 P05 → E-Switch 100DP1T1B1M2REH, D3 P02 → 5KP24A. Już poprawione w tej liście: U2 P05 → REF5025ID (klasa wysoka; REF5025AIDR nie spełnia okna DAQ_OK).

Zakres: wszystkie płytki z co najmniej pierwszą rewizją, bez P01 (kompletna 24.09) i bez P07 (wstrzymana), bez PCB. Źródła ilości: najnowsze pakiety P00-R3, P02-R3, P03-R5, P04-R2.2, P05-R1, P06/P08/P09/P10/P11-R1 (BOM, ZAKUPY, wiązki); P03-R5 i P04-R2.2 z 28.09 zmieniają względem R4/R2.1 tylko U4 (SN74LVC1G37 zamiast 1G07) i R17 (10k zamiast 100k). Ilości są netto: odjęte zamówienia z 24.09 i zapas P01 (tabela „Pokryte z zapasu” na końcu). P05 ma wartości z recenzji: R5 6,04k, R7 5,11k, R13 47k, opcjonalna 1N5817. Moduły ESP32-S3 i AD7606B są posiadane; MAX31856 XU ×2 kupione na Allegro (wg `P09-R1-review/docs/MODUL-KWALIFIKACJA.md`) — w `ZAMOWIONE.md` wciąż figurują jako brak.

**Korekta `P00-R3-review/docs/ZAKUPY-P00.md` (mój błąd w R3).** Wiązka stanowiskowa do P04 ma tam dla J2 „gniazdo IDC16” i dla J1 „obudowę żeńską Mini-Fit 4p”. Tymczasem H_SAFE i H_LV04 są przylutowane do P04 i kończą się złączami żeńskimi, a P04 `P00-P04.md` wymaga męskiego IDC16 z usuniętym pinem 4. Ta lista kupuje więc dla P00 męski T821-1-16-S1 (druga sztuka z minimum 2) i męskie gniazdo Mini-Fit 39-29-6048 (dziesiąta sztuka z Farnella), bez żeńskiego IDC16 i bez obudowy 4p ze stykami. J3–J8 bez zmian.

## Podsumowanie

| Dostawca | Plik | Pozycji | Wartość | Uwagi |
|---|---|---:|---:|---|
| TME — części | `TME-wklej.txt` | 106 | 854,96 zł netto | format „SYMBOL ilość”, do okna szybkiego dodawania TME |
| TME — przewody i taśma | `TME-przewody-wklej.txt` | 4 | 347,22 zł netto | szpule 10–25 m i rolka 30,5 m taśmy; potrzeba kilkanaście metrów — do decyzji (TME albo zakup lokalny) |
| Kamami | tabela niżej | 7 | 42,29 zł brutto | + wysyłka 8,90–14,90 zł |
| Farnell | `FARNELL-wklej.txt` | 9 | 246,86 zł netto | powyżej 200 zł wysyłka gratis; format „kod,ilość” (LTC4412 wpisany numerem producenta) |
| Mouser | `MOUSER-wklej.txt` | 20 | 363,68 zł netto | wszystko na stanie; powyżej 300 zł wysyłka gratis |
| Do decyzji | — | 2 | — | bocznik PBV (tylko DigiKey, 163,30 zł), przyciski EAO (panel P11, poza PCB) |

Każda pozycja poza TME i Kamami ma przypisanego jednego dostawcę (kolumna „Kupić w” w tabeli „Uzupełnienie”); Obie paczki przekraczają progi darmowej wysyłki (Farnell 200 zł, Mouser 300 zł), a każda pozycja jest dziś na stanie. Mouser nie sprzedaje do Polski TBD62083APG i ADR4525BRZ, a LTC4412 ma tam status „ograniczona dostępność”, stąd podział na dwa sklepy.

## Zamienniki względem BOM

W TME nie było dokładnego MPN z BOM (brak, zero na stanie albo minimum setki sztuk). Każdy zamiennik ma tę samą funkcję, obudowę i raster; różnice są w kolumnie „Uwagi” tabel TME. Wymagają akceptacji:

| BOM | Kupowane | Co się zmienia |
|---|---|---|
| SN74HC14N | CD74HC14E | nic poza oznaczeniem (TI HC14, DIP14) |
| TLV1702AQDGKRQ1 | TLV1702AIDGKR | wersja przemysłowa zamiast AEC-Q100, ta sama VSSOP-8 |
| BAT85,133 (Nexperia) | BAT85S-TAP (Vishay) | producent |
| K104K15X7RF53H5 / K103 / K102 / K471 | K104K15X7RF5TH5, Murata RDER/RDE5 | kod wyprowadzeń/opakowania i producent; raster 5 mm bez zmian |
| EEUFR1C220, EEUFR1E220 | EEUFR1H220 | 50 V zamiast 16/25 V, ten sam korpus D5×11 |
| EEUFR1H4R7 | EEUEB1H4R7SH | seria EB zamiast FR, D5×11 |
| C3225X7R1E226M250AB, GRM31CR71E105KA12L, GRM31CR71H104KA01L | CL32B226KAJNNNE, C3216X7R1H105KAB, C1206C104K5RAC | producent; 1u 1206 ma 50 V zamiast 25 V |
| MF0207 330R, 33R, 560R | MBB0207 330R/33R, TE LR1F560R | producent |
| 232k 1 % (P08 R1) | YR1B232KCC 0,1 % (Farnell) | lepsza tolerancja; 1 % nie ma nigdzie w detalu |
| SN74LVC1G37DBVR (P03-R5 U4) | SN74LVC1G37DBVRQ1 (Mouser) | wersja AEC-Q100 tego samego układu; DBVR nigdzie na stanie |
| ADR4525BRZ (P05 U2) | REF5025ID (Mouser; klasa wysoka, tuba) | ten sam pinout SOIC-8; 0,05 %, 3 ppm/K; REF5025AIDR (0,1 %) nie spełnia okna DAQ_OK (P05 R2, 29.09) |
| 5,1k 0,1 % (P06 R3, R4) | YR1B5K11CC ×2 | dzielnik zostaje 1:2; wzmocnienie i tak kalibrowane |
| Molex 39-29-9129 (P11 J7) | 39-29-6128 (Mouser) | wersja bez kołków, złocona; otwory na kołki zostają puste |
| MBB0207 300k 0,1 % (P05 R33) | Vishay Dale RN55E3003BB14 | producent i seria; 25 ppm/K wg oznaczenia E |
| 1R 1 W metalizowany (P05 R1, P06 R6) | KNP01U-1R (drutowy, 3×9 mm) | technologia drutowa; energii impulsu ≥ 10 mJ / 0,5 ms z karty nie sprawdzałem |
| PR02 1k 2 W (P02 R20) | PMR2S-1K | producent, korpus 4×11 mm |
| TE HSA2547RJ (poza PCB) | Arcol HS25-47RF | producent, ta sama obudowa 25 W |
| Würth IDC 612…21621 / 612…23021 | Amphenol FCI T821 (złocone) / T812 (gold flash, wariant A101) | TME nie prowadzi Würtha; obrys nagłówków sprawdzić przy wydruku 1:1, odciążkę T812 przy odbiorze |
| Mini-Fit 39-29-6088 (P03 J9) | bez zmian (Mouser); w TME tylko cynowy MX-5566-08A | cynowy nagłówek ze złoconymi stykami wtyku — decyzja |

## TME — części (`TME-wklej.txt`)

Ceny netto przy podanej ilości, stan z 28.09.

### Układy i półprzewodniki

| Symbol TME | Szt. | zł/szt | Stan | Płytki | Uwagi |
|---|---:|---:|---:|---|---|
| TLC555CP | 1 | 4,33 | 2504 | P00 U1 |  |
| LM2937ET-3.3/NOPB | 1 | 8,18 | 95 | P00 U2 |  |
| CD74HC123E | 1 | 3,63 | 2095 | P04 U1 |  |
| CD74HC14E | 1 | 2,58 | 699 | P04 U2 | zamiennik SN74HC14N (TME: 0 szt.): ten sam układ TI HC14, DIP14, identyczny pinout |
| SN74HC74N | 1 | 4,04 | 285 | P04 U3 |  |
| SN74HC139N | 1 | 4,95 | 829 | P09 U3 | P03 ma sztukę z Mousera |
| SN74LVC1G17DBVR | 1 | 0,5333 | 12830 | P03 U6 |  |
| AO3401A | 1 | 1,29 | 39078 | P03 Q1 |  |
| TLV1702AIDGKR | 1 | 5,99 | 973 | P05 U3 | zamiennik TLV1702AQDGKRQ1 (w TME tylko po 2500): wersja przemysłowa -40..125 C, ta sama VSSOP-8 i pinout |
| MCP1700-3302E/TO | 1 | 1,82 | 1591 | P05 U12 |  |
| TPS2553DBVR | 1 | 3,99 | 5 | P08 U1 | w TME tylko 5 szt. |
| TCAN1051VDRQ1 | 1 | 8,18 | 138 | P10 U1 |  |
| PESD2CAN.215 | 1 | 2,21 | 14635 | P10 D1 |  |
| 1N5819-E3/73 | 2 | 1,08 | 1326 | P00 D1, P06 D1 | Vishay DO-41 (1N5819-DIO w TME to obudowa DO-15) |
| 1N5817-E3/73 | 1 | 0,998 | 6855 | P05 (opcja P5-06) | opcjonalne wg recenzji P05 |
| BAT85S-TAP | 1 | 0,6799 | 5949 | P06 D2 | Vishay BAT85S, DO-35, zamiast BAT85,133 (brak w TME) |
| 2N3904BU | 3 | 0,7407 | 7079 | P04 Q1-Q3 |  |
| L-934GD | 10 | 0,328 | 83929 | P00 x8, P02, P03, P04 | 11 minus 1 z zapasu |
| L-934YD | 1 | 1,40 | 15176 | P00 |  |
| L-934ID | 5 | 1,08 | 43370 | P00 | minimum TME 5 szt., potrzebna 1 |

### Rezystory 1 %

| Symbol TME | Szt. | zł/szt | Stan | Płytki | Uwagi |
|---|---:|---:|---:|---|---|
| MF0207FTE-10K | 107 | 0,1173 | 237855 | P02 8, P03 29, P04 26, P05 17, P06 9, P08 13, P09 6, P10 1 | 109 minus 2 z zapasu; P05 R13 = 47k (P5-05), P04-R2.2 R17 = 10k |
| MF0207FTE-1K | 36 | 0,1129 | 117350 | P00 19+5, P02, P03 2, P04 6, P05, P06 2 | P00: 5 szt. do wiązki stanowiskowej |
| MF0207FTE-100K | 15 | 0,1964 | 18879 | P00, P04 6, P06 3, P09 7 | 17 minus 2 z zapasu |
| MF0207FTE-4K7 | 3 | 0,3194 | 7099 | P00, P02, P03 2, P08 | 5 minus 2 z zapasu |
| MF0207FTE-47K | 2 | 0,3242 | 21437 | P04 2, P05 R13, P06 | 4 minus 2 z zapasu |
| MF0207FTE-100R | 7 | 0,1488 | 66981 | P04, P06, P08 2, P09 2, P10 |  |
| MBB02070C3300FCT00 | 2 | 0,2188 | 7796 | P02 R5, P03 R12 | 330R 1 % 0207 Vishay (MF0207FTE-330R: 0 szt.) |
| MF0207FTE-1M | 2 | 0,2004 | 64731 | P02 R8, R11 |  |
| MF0207FTE-470R | 1 | 0,2966 | 32785 | P02 R16 |  |
| MF0207FTE-220R | 1 | 0,1759 | 18904 | P03 R34 |  |
| MBB02070C3309FCT00 | 5 | 0,3325 | 2797 | P03 R36-R40 | 33R 1 % 0207 Vishay (MF0207FTE-33R: 0 szt.) |
| MF0207FTE-47R | 6 | 0,4213 | 41458 | P06 2, P09 4 |  |
| MF0207FTE-220K | 1 | 0,4174 | 1657 | P04 R1 |  |
| MF0207FTE-68K | 1 | 0,3325 | 784 | P00 |  |
| LR1F560R | 1 | 0,3574 | 11978 | P00 R5 | 560R 1 % TE LR1, 6,2x2,3 mm (MF0207FTE-560R: 0 szt.) |
| KNP01U-1R | 20 | 0,3575 | 300 | P05 R1, P06 R6 | 1R 1 W drutowy, korpus 3x9 mm; min. 20 szt.; karty impulsowej nie sprawdzałem (wymóg P06: >= 10 mJ / 0,5 ms) |
| PR02-39R | 1 | 0,8689 | 56 | P06 R21 | 39R 2 W Vishay PR02, 3,9x12 mm |
| PMR2S-1K | 10 | 0,4393 | 900 | P02 R20 | 1k 2 W power metal 4x11 mm, min. 10 (PR02 1k brak w TME) |
| HS25-47RF | 1 | 16,01 | 58 | P02 R17 (R_CHARGE, poza PCB) | Arcol HS25 47R 1 % 25 W zamiast TE HSA2547RJ (w TME min. 26 szt.); ten sam typ obudowy |
| RC1206FR-07220R | 1 | 0,112 | 36988 | P03 R41 |  |
| RC0805FR-0733R | 2 | 0,6112 | 13199 | P05 R26, R27 |  |

### Rezystory 0,1 %

| Symbol TME | Szt. | zł/szt | Stan | Płytki | Uwagi |
|---|---:|---:|---:|---|---|
| MBB0207VD1002BC100 | 3 | 3,55 | 2258 | P02 R7, R10; P05 R4 | 10k 0,1 % 25 ppm |
| MBB0207VD2002BC100 | 1 | 3,82 | 1866 | P05 R6 | 20k 0,1 % |
| MBB0207VD1003BC100 | 5 | 4,55 | 339 | P05 R28, R29, R32, R34, R35 | 100k 0,1 % |
| MRA0207-30K1 | 1 | 4,68 | 182 | P02 R6 | 30,1k 0,1 % 15 ppm |

### Kondensatory THT

| Symbol TME | Szt. | zł/szt | Stan | Płytki | Uwagi |
|---|---:|---:|---:|---|---|
| K104K15X7RF5TH5 | 34 | 0,3767 | 9890 | P00 4, P02 5, P03 11, P04 14 | ten sam kondensator co K104K15X7RF53H5, inny kod wyprowadzeń/opakowania (F53H5 w TME tylko po 5000) |
| RDER71H103K0K1H03B | 3 | 0,9222 | 463 | P00, P02 C14, C15 | 10n X7R 50 V raster 5 mm (K103 brak w TME) |
| RDE5C1H102J0M1H03A | 1 | 1,97 | 4038 | P04 C18 | 1n C0G raster 5 mm (K102 brak w TME) |
| RDE5C1H471J0M1H03A | 1 | 0,9448 | 1945 | P06 C2 | 470p C0G raster 5 mm, obrys 4x2,5 mm |
| EEUFR1H100 | 4 | 1,22 | 25398 | P00, P02 2, P04 |  |
| EEUFR1H220 | 4 | 1,47 | 5947 | P00, P02 x3, P08 C10 | 22u/50 V FR, D5x11, zamiast EEUFR1C220 (P02 x2) i EEUFR1E220 (P08) — brak w TME; 5 minus 1 z zapasu |
| EEUFR1C471 | 2 | 2,15 | 23095 | P05 C1, P06 C3 |  |
| EEUEB1H4R7SH | 2 | 1,36 | 1722 | P06 C4, C5 | 4,7u/50 V Panasonic EB, D5x11 (EEUFR1H4R7: 0 szt.) |
| MKS2-1U/63-R | 2 | 3,78 | 8416 | P04 C1, C2 | WIMA MKS2 1u/63 V 10 %, 5x10x7,2 mm |
| MKS2-470N/63 | 1 | 2,86 | 7391 | P06 C1 | WIMA MKS2C034701C00KSSD |
| HC1V229M35045HA | 3 | 13,87 | 205 | P02 bank HOLD |  |

### Kondensatory SMD

| Symbol TME | Szt. | zł/szt | Stan | Płytki | Uwagi |
|---|---:|---:|---:|---|---|
| GRM21BR71H104KA01L | 33 | 0,1107 | 63651 | P02 C16, P05 9, P06 11, P08 6, P09 3, P10 3 | 100n 0805 50 V pokrywa też miejsca 25 V |
| GCM188R71H104KA57D | 6 | 0,2404 | 133290 | P05 C4-C8, C11 (0603) |  |
| GCM21BR71E105KA56L | 10 | 0,1841 | 7144 | P05 5, P08 3, P09 2 | 1u 0805 25 V |
| GRM21BR71E475KA73L | 10 | 0,949 | 2120 | P09 C4, C5; P10 C4, C5 | 4u7 0805 25 V; min. 10 |
| GCM21BR71E225KA73L | 1 | 0,4983 | 5397 | P05 C3 | 2u2 0805 25 V |
| GRM216R71H103KA01D | 2 | 0,0678 | 8525 | P05 C25, C26 | 10n 0805 |
| C0805C102K5RAC | 1 | 0,2993 | 1074 | P05 C32 | 1n 0805 X7R |
| GRM2165C1H221JA01D | 7 | 0,5736 | 1333 | P05 C27-C34 | 220p C0G 0805 |
| CL32B226KAJNNNE | 2 | 4,33 | 11128 | P05 C12, C13 | 22u 1210 25 V X7R (C3225X7R1E226M250AB w TME tylko po 1000) |
| GRM31CR71C106KA12L | 1 | 1,34 | 19711 | P03 C14 |  |
| C3216X7R1H105KAB | 1 | 0,4292 | 3220 | P03 C13 | 1u 1206 50 V (GRM31CR71E105KA12L brak w TME) |
| C1206C104K5RAC | 2 | 0,4073 | 146336 | P03 C12, C15 | 100n 1206 50 V (GRM31CR71H104KA01L brak w TME) |

### Złącza na płytkach, bezpieczniki, przełączniki

| Symbol TME | Szt. | zł/szt | Stan | Płytki | Uwagi |
|---|---:|---:|---:|---|---|
| MKDS1.5/2-5.08 | 1 | 3,73 | 264 | P00 J10 | Phoenix 1715721 |
| MSTBVA2.5/4G5.0 | 1 | 4,90 | 1470 | P11 J1 | Phoenix 1755752 |
| MX-39-29-6028 | 1 | 4,94 | 213 | P08 J4 | Mini-Fit Jr 2p |
| T821-1-06-S1 | 6 | 3,26 | 34201 | P03 J3, J6, J8; P04 J4-J6 | Amphenol FCI, złocone; zamiast Würth 61200621621 (TME nie prowadzi Würtha) |
| T821-1-08-S1 | 2 | 1,62 | 1613 | P03 J2, J5 | jw., 2x4 |
| T821-1-10-S1 | 2 | 2,59 | 16097 | P03 J7, P04 J3 | jw., 2x5; min. 2 |
| T821-1-16-S1 | 2 | 3,29 | 2557 | P03 J4; P00 wiązka | jw., 2x8; min. 2; druga sztuka: męskie IDC16 z usuniętym pinem 4 do końcówki H_SAFE na stanowisku P00 |
| ZL262-40SG | 2 | 1,50 | 11696 | P03 M1 (2 x 1x22) | gniazdo żeńskie 1x40 złocone, ciąć na 1x22 |
| ZL262-9SG | 10 | 0,4455 | 1380 | P03 SD1, P09 J3, J4 | 1x9 złocone; min. 10 |
| ZL262-7SG | 10 | 0,3552 | 24350 | P04 adaptery U8-U10 (6 szt.) | 1x7 złocone; min. 10 |
| 0001.2507 | 1 | 2,22 | 6962 | P02 F1 | Schurter SPT T2A |
| 0001.2504 | 2 | 3,28 | 6613 | P02 F2, F3 | Schurter SPT T1A |
| 0001.2501 | 1 | 3,22 | 5623 | P02 F4 | Schurter SPT T0,5A — teraz jest w TME |
| ZHL78 | 5 | 1,01 | 25101 | P02 F1-F4 | Stelvio-Kontek PTF/78; min. 5, potrzebne 4 |
| S6A | 1 | 46,77 | 25 | P06 SW1 | NKK S6A |
| BNC-056 | 2 | 4,61 | 1360 | P05 AUX, P11 SCOPE | gniazdo BNC izolowane, lutowane |

### Wiązki: wtyki, styki, przewód CAN

| Symbol TME | Szt. | zł/szt | Stan | Płytki | Uwagi |
|---|---:|---:|---:|---|---|
| MX-5557-04R | 7 | 0,591 | 37718 | LV03-LV10 bez LV07 | Molex 39-01-2040 |
| MX-5557-14R | 1 | 3,15 | 1476 | VSENSE (P05) | 39-01-2140; w ZAKUPY-P02 i P05 ta sama sztuka |
| MX-5557-12R | 1 | 1,68 | 5592 | TAPS (P05) | 39-01-2120 |
| MX-5557-10R | 2 | 0,621 | 18836 | PANELSAFE (P11), P00 J8 | 39-01-2100 |
| MX-5557-08R | 1 | 0,923 | 19650 | PANELCORE (P11) | 39-01-2080 |
| MX-5557-06R | 1 | 1,08 | 5150 | P00 J7 | 39-01-2060 |
| MX-5557-02R | 1 | 0,7481 | 149228 | TSENSOR (P11) | 39-01-2020 |
| MX-39-00-0074 | 80 | 1,37 | 452 | wszystkie wtyki Mini-Fit | potrzeba 72 minus 4 z zapasu = 68, reszta na nieudane zaciśnięcia; 100 szt. kosztuje 121,60 zł (próg 1,216) |
| T812-1-06 | 8 | 2,81 | 8742 | PSUOK, DAQOK, SENSOR, SFAULT, CAN + P00 x3 | FCI, gold flash; wariant A101 — odciążkę sprawdzić przy odbiorze |
| T812-1-08 | 1 | 3,92 | 80 | ILOG (P06) | jw. |
| T812-1-10 | 2 | 2,90 | 5022 | TEMP (P09), P00 J3 | jw. |
| T812-1-16 | 5 | 1,89 | 7671 | SAFE (P04) | jw.; min. 5, potrzebna 1 |
| MSTB2.5/3-ST-5.08 | 1 | 10,11 | 1510 | P02 SUPPLY do P01 J6 | Phoenix 1757022 |
| MSTB2.5/4-ST-5.08 | 1 | 9,54 | 774 | P06 ISERIES | Phoenix 1757035 |
| DT04-12PA | 1 | 12,38 | 413 | P11 X8 TEST | DT04-12PB i -PC: w TME tylko po 32/22 szt., patrz uzupełnienie |
| W12P | 3 | 1,41 | 1133 | P11 |  |
| 04602021631-TEC-0 | 25 | 4,16 | 25 | P11 | TE 0460-202-1631; w TME dokładnie 25 szt., bez zapasu |
| 114017 | 11 | 0,818 | 51440 | P11 |  |
| BUS-CAN-1X2X0.22 | 1 | 8,27 | 1041 | P10 W3 (0,3 m) | LAPP UNITRONIC BUS CAN 120 ohm, ekranowany; sprzedaż na metry |

### Mechanika

| Symbol TME | Szt. | zł/szt | Stan | Płytki | Uwagi |
|---|---:|---:|---:|---|---|
| TFF-M3X10/DR185 | 40 | 1,95 | 20570 | P00, P02-P06, P08-P11 | poliamid jak w P01; 41 minus 6 z zapasu; metalowa TFF-M3X10/DR123 kosztuje 0,52 zł |
| TFF-M2.5X12/DR182 | 10 | 2,72 | 500 | P03 SD1 (2), P09 (4) | poliamid M2,5 12 mm; wysokość do przymiarki z gniazdem ZL262 (8,5 mm) |
| M2.5X6/D7985B | 100 | 0,0653 | 109000 | P03, P09 | min. 100 |

**Razem TME — części: 854,96 zł netto.**

## Przewody i taśma IDC (`TME-przewody-wklej.txt`, do decyzji)

Potrzeba netto: AWG22 ok. 12,4 m, 0,5 mm² ok. 3,6 m, 1,5 mm² 0,6 m, taśma 1,27 mm ok. 1,6 m (16, 10, 8 i 6 żył). TME sprzedaje tylko szpule, stąd koszt. Silikonowe linki w Kamami (22/24/20/16 AWG) są dziś „w oczekiwaniu na dostawę”.

| Symbol TME | Ilość | zł/j. | Stan | Zastosowanie | Uwagi |
|---|---:|---:|---:|---|---|
| LGY0.35/25-BK | 25 m | 2,97 | 825 m | ok. AWG22: 12,4 m łącznie (LV, PANELSAFE/PANELCORE, VSENSE, P00) | szpula 25 m; drugi kolor np. LGY0.35/25-RD |
| LGY0.50/25-BK | 25 m | 3,56 | 500 m | 0,5 mm2: DEUTSCH P11 3,15 m + R_CHARGE P02 0,4 m | szpula 25 m |
| LGY1.5/10-BK | 10 m | 8,90 | 180 m | 1,5 mm2: P11 W5/W7 0,6 m | szpula 10 m |
| DS1057-16A282R | 1 rolka | 94,97 | 258 | wszystkie taśmy IDC | 30,5 m 16× AWG28; taśmę dzieli się na 10/8/6 żył |

Razem 347,22 zł netto. AWG24 (P05 TAPS 0,5 m, P11 W8 3,6 m): w TME tylko szpule 250 m (LIY-0.25); Kamami: silikon 24AWG 4 m — oczekiwanie na dostawę. RG174 0,15 m (P05 AUX, P11 SCOPE) z posiadanego zapasu. 2,5 mm² (P02 SUPPLY, P06 ISERIES/SW1-A, łącznie 0,9 m): w planie P01 jest już zakup lokalny przewodu 2,5 mm² czerwonego i czarnego — dopisać długość (w TME: LGY2.5/10-RD i -BK po 133,50 zł za 10 m).

## Kamami

Ceny brutto ze strony produktu, dostępność z karty produktu 28.09.

| Indeks | Produkt | Szt. | zł/szt brutto | Dostępność | Płytki | Uwagi |
|---|---|---:|---:|---|---|---|
| 1191911 | ZOBD SET ABS — zestaw OBD2 (12 V, typ A) z obudową, Kradex | 1 | 17,02 | Dostępny (5) | P10 W3 | TME ma tylko wersję 24 V; przewody lutowane do pinów 6/14 — sprawdzić przy odbiorze |
| 648 | Podstawka DIP14 precyzyjna | 2 | 0,98 | Dostępny (39) | P04 U2, U3 | 4 szt. dla P04 z 24.09 już są |
| 1207058 | Podstawka precyzyjna DIP-8P, złocone styki | 1 | 5,02 | Dostępny (16) | P00 U1 |  |
| 649 | Podstawka DIP16 precyzyjna | 1 | 0,8 | Dostępny (22) | P09 U3 (opcja) | opcjonalna wg ZAKUPY P09 |
| 204596 | Przewody połączeniowe F-F 17 cm, 40 szt. | 1 | 5,69 | Dostępny (276) | P00 wiązka stanowiskowa | potrzeba ok. 25 |
| 1184699 | Przycisk panelowy monostabilny 16x22 mm, czerwony | 1 | 5,90 | Dostępny (43) | P00 ARM | styk NO sprawdzić przy odbiorze |
| 1184697 | Przycisk panelowy monostabilny 16x22 mm, zielony | 1 | 5,90 | Dostępny (44) | P00 SAFE_N_TEST | jw. |

Razem 42,29 zł brutto + wysyłka. Goldpinów i zworek nie trzeba: P09 JP1/JP2 i wybierak HB w P00 wychodzą z zapasu (listwa 1×40 z Kamami, ZL201-02G i JUMPER-KPL z TME).

## Uzupełnienie — Farnell i Mouser

Pozycje, których TME i Kamami nie mają w detalu. „—” = brak u tego dostawcy (powód w Uwagach). Stany z 28.09.

| Pozycja | Szt. | Płytki | Kupić w | Farnell: kod, zł/szt, kup, stan | Mouser: nr, zł/szt, stan | Uwagi |
|---|---:|---|---|---|---|---|
| MCP100-300DI/TO | 1 | P04 U11 | Farnell | 1332051, 1,54, 1 szt., 1675 | 579-MCP100-300DI/TO, 1,59, 1289 | TME ma tylko wariant H (inny bondout) |
| TBD62083APG | 2 | P05 U4, P08 U2 | Farnell | 4178763, 12,41, 2 szt., 1713 | — | Mouser: „nie sprzedaje tego produktu w Twoim regionie”; TME: DIP tylko po 79 szt. |
| LTC4412IS6#TRPBF | 1 | P03 U5 | Farnell | LTC4412IS6#TRPBF, 21,94, 1 szt., 1986 | — | Mouser: „ograniczona dostępność”; TME 0 szt.; w pliku Farnella numer producenta |
| G6K-2P-Y DC5 | 4 | P05 K1-K3, P08 K1 | Farnell | 4446136, 19,45, 4 szt., 5031 | — | Mouser 0 szt. (dostawa 08.01.2027); TME 0 szt. (tydz. 8/2027) |
| STPS20100CT | 1 | P02 (druga sztuka) | Farnell | 4035972, 11,48, 1 szt., 517 | — | Mouser min. 2000; TME 0 szt. (tydz. 43/2026) |
| Phoenix 1766246 GMSTBA 2,5/3-G-7,62 | 1 | P02 VMOTOR | Farnell | 2671273, 6,92, 1 szt., 308 | — | TME 0 szt., termin do potwierdzenia |
| Molex 39-29-6048 (4p Au, bez kołków) | 9 | P02 J3-J10; P00 wiązka (męskie do H_LV04) | Farnell | 2751659, 6,71, 10 szt., 538 | 538-39-29-6048, 8,32, 489 | 10 szt. po 6,71 taniej niż 9 po 9,87; TME 0 szt., min. 10 |
| Molex 39-29-9069 (6p z kołkami) | 1 | P04 J7 | Farnell | 2612451, 14,31, 1 szt., 23 | 538-39-29-9069, 13,33, 0 (dostawa 23.11.2026) | TME min. 32 |
| YR1B232KCC (232k 0,1 % zamiast 1 %) | 1 | P08 R1 | Farnell | 1083509, 4,19, 5 szt., 1415 | — | 232k 1 %: Mouser i TME bez stanu w detalu; 0,1 % spełnia wymóg 1 %; Farnell min. 5 |
| REF5025ID (zamiast ADR4525BRZ) | 1 | P05 U2 | Mouser | — | 595-REF5025ID, 35,82, 5354 | ADR4525BRZ nigdzie na stanie (DigiKey 33 tyg.); REF5025: ten sam pinout SOIC-8 (2 VIN, 4 GND, 6 VOUT; 3 TEMP i 5 TRIM zostają wolne jak w P05); klasa wysoka 0,05 %, 3 ppm/K — REF5025AIDR (0,1 %) nie spełnia okna DAQ_OK (P05 R2, 29.09); zasila tylko dzielniki okna DAQ_OK |
| SN74LVC1G37DBVRQ1 (zamiast SN74LVC1G37DBVR) | 1 | P03 U4 (R5) | Mouser | — | 595-N74LVC1G37DBVRQ1, 1,10, 1883 | DBVR: TME 0 bez terminu, Mouser niedostępny (16 tyg.), Farnell brak; Q1 = wersja AEC-Q100 tego samego układu, SOT23-5 |
| MCP120-300DI/TO | 1 | P08 U8 | Mouser | — | 579-MCP120-300DI/TO, 2,27, 894 | TME i Farnell: min. 2000 szt. |
| YR1B38K3CC (38,3k 0,1 %) | 1 | P02 R9 | Mouser | 1083424, 3,56, 1 szt., 1239 | 279-YR1B38K3CC, 3,86, 1726 | TE, 15 ppm |
| YR1B15KCC (15k 0,1 %) | 1 | P05 R3 | Mouser | 1083381, 2,40, 5 szt., 7230 | 279-YR1B15KCC, 3,82, 7699 | Farnell min. 5 |
| YR1B6K04CC (6,04k 0,1 %) | 1 | P05 R5 (P5-02) | Mouser | — | 279-YR1B6K04CC, 3,86, 785 | Farnell: brak tej wartości |
| YR1B5K11CC (5,11k 0,1 %) | 3 | P05 R7 (P5-02); P06 R3, R4 | Mouser | 1083330, 2,43, 5 szt., 183 | 279-YR1B5K11CC, 3,82, 1038 | P06: 5k11 zamiast 5k1 — dzielnik R3/R4 zostaje dokładnie 1:2, obciążenie INA240 10,22 kΩ (warunek >= 10 kΩ); 5k1 0,1 % nigdzie w detalu |
| YR1B24K9CC (24,9k 0,1 %) | 1 | P05 R8 | Mouser | 1083404, 3,74, 5 szt., 965 | 279-YR1B24K9CC, 3,86, 2825 | Farnell min. 5 |
| YR1B499KCC (499k 0,1 %) | 1 | P05 R31 | Mouser | 1083547, 1,87, 5 szt., 1194 | 279-YR1B499KCC, 1,93, 5336 | Farnell min. 5 |
| YR1B10RCC (10R 0,1 %) | 2 | P06 R1, R2 | Mouser | 1083036, 2,17, 5 szt., 4468 | 279-YR1B10RCC, 2,35, 2193 | Farnell min. 5 |
| RN55E3003BB14 (300k 0,1 %) | 1 | P05 R33 | Mouser | — | 71-RN55E3003B, 7,44, 661 | Vishay Dale RN55, charakterystyka E = 25 ppm/K (potwierdzić w karcie); YR1B nie ma 300k |
| C&K 7201SYCBE | 1 | P05 SW1 | Mouser | — | 611-7201-054, 57,55, 10 | TME ma tylko 7201SYZBE (końcówki lutownicze); sprawdzić, czy 611-7201-054 to wersja SYCBE |
| Molex 39-29-6148 (14p Au) | 1 | P02 J11 | Mouser | — | 538-39-29-6148, 33,13, 5730 | TME: min. 10 po 36,99 |
| Molex 39-29-6088 (8p Au, bez kołków) | 1 | P03 J9 | Mouser | — | 538-39-29-6088, 15,27, 3962 | BOM P03: 39-28-x08x; TME: min. 23; cynowy MX-5566-08A w TME 1,92 zł — decyzja (styki Au) |
| Molex 39-29-9109 (10p z kołkami) | 1 | P04 J8 | Mouser | — | 538-39-29-9109, 22,79, 404 | TME: min. 21 |
| Molex 39-29-6128 (12p Au, bez kołków) zamiast 39-29-9129 | 1 | P11 J7 | Mouser | — | 538-39-29-6128, 28,25, 2523 | 39-29-9129: Mouser 0 szt. (23.10), TME i Farnell brak; footprint 5566-12A2 przyjmuje wersję bez kołków, otwory na kołki zostają puste |
| Würth 450301014042 (WS-SLTV) | 9 | P00 CH1-CH9 | Mouser | — | 710-450301014042, 8,54, 15537 | TME nie prowadzi Würtha |
| TE DEUTSCH DT04-12PB | 1 | P11 X2 | Mouser | — | 571-DT04-12PB, 17,64, 5888 | TME: 0 szt., min. 32 |
| TE DEUTSCH DT04-12PC | 1 | P11 X3 | Mouser | — | 571-DT04-12PC, 18,83, 2450 | TME: min. 22 |
| Adafruit 4682 (microSD) | 1 | P03 SD1 | Mouser | — | 485-4682, 13,24, 812 | brak w TME i Kamami |

Farnell (`FARNELL-wklej.txt`): 9 pozycji, 246,86 zł netto. Mouser (`MOUSER-wklej.txt`): 20 pozycji, 363,68 zł netto. Rezystory YR1B są w Mouserze, bo tam minimum to 1 szt. (w Farnellu 5). Części dostępne tylko u jednego dostawcy albo w małej ilości — G6K 5 V (Farnell; TME i Mouser dopiero w 2027), TBD62083APG i LTC4412 (Farnell), C&K 7201SYCBE (Mouser, 10 szt.), 39-29-9069 (Farnell, 23 szt.), TPS2553DBVR (TME, 5 szt.), styki DEUTSCH (TME, 25 szt.) — zamówić bez zwłoki.

## Do decyzji

| Pozycja | Szt. | Płytki | Stan sprawdzenia |
|---|---:|---|---|
| PBV-R005-F1-0.5 (Isabellenhütte) | 1 | P06 RSH1 | dostępny tylko w DigiKey: 4423-PBV-R005-F1-0.5-ND, 1498 szt., 163,30 zł netto (wysyłka gratis od 300 zł); w TME, Farnellu i Mouserze brak |
| EAO 14-412.036K, 14-432.036 x2, 14-435.036 x3, 14-473.036 | 7 | P11 (panel, poza PCB) | w TME: 14-473.036 17 szt. (132,48 zł), 14-435.036 2 szt. (77 zł), 14-412.036K 0 (389,55 zł), 14-432.036 0 (130,55 zł); zamiennik z dostępnych przycisków dobrać przy P11 R2 — nie wpływa na PCB |

Na płytkach nie zostaje żadna część z terminem dostawy dłuższym niż kilka dni, o ile przyjmiesz zamienniki z tabeli „Zamienniki”. Bocznik PBV jest na stanie tylko w DigiKey (trzeci dostawca, wysyłka gratis od 300 zł). Przyciski EAO są na panelu, nie na PCB — zamiennik dobierzemy przy P11 R2.

## Wstrzymane i opcjonalne

| Symbol | Szt. | Płytki | Stan / cena | Dlaczego nie ma w plikach |
|---|---:|---|---|---|
| SSW-108-02-G-D-RA | 1 | P03 J1 | TME 9 szt., 13,56 zł | do zatwierdzenia przekroju B2B P03–P05 |
| TSW-108-08-G-D-RA | 1 | P05 J1 | TME 23 szt., 8,93 zł | BOM P05 ma TSW-108-08-G-D-NA; MECHANIKA P03 opisuje wtyk kątowy — do rozstrzygnięcia razem z przekrojem |
| OBJ35 | 3 | P02 bank HOLD | — | TME: obejma poliamidowa do kondensatora Ø35 mm, 11,23 zł, na stanie 1 szt.; mechanika do przymiarki |
| 7J360100020100A000 | 2 | P09 TC1, TC2 | — | TME: termopara K Guenther, PFA, -40..260 C, 1 m, wtyk mini-K, 64,96 zł; spoina izolowana nie jest potwierdzona w parametrach. Tylko jeśli termopary nie przyszły z modułami MAX31856 |
| ICVT-18P | 10 | P05 U4, P08 U2 (opcja) | — | TME: podstawka DIP18 (nie precyzyjna), min. 10, 0,60 zł; w Kamami DIP18 czeka na dostawę |
| DEUTSCH: uchwyty detektorów, przesłona portów, nasadki EAO | — | P11 | — | elementy mechaniczne do wykonania albo dobrania razem z EAO |
| Zaślepka klucza w gnieździe IDC | — | P04 H_SAFE i pozostałe | — | brak osobnej części; zaślepić pozycję ręcznie |

## Pokryte z zapasu i zamówień z 24.09

| Pozycja | Potrzeba | Pokrycie |
|---|---:|---|
| 74LVC125AD,118 | 22 | Mouser 25 szt. (zostają 3) |
| SN74HC08N | 8 | Mouser 8 szt. |
| MCP120-450DI/TO | 4 | Mouser 3 + TME 1 |
| MCP120-300DI/TO | 5 | Mouser 4; piąta w uzupełnieniu |
| SN74HC139N | 2 | Mouser 1 (P03); druga w TME |
| STPS20100CT | 2 | zapas TME 1; druga w uzupełnieniu |
| LM2903P, TL431BILP | 1 + 1 | zapas TME / Mouser |
| TSR 2-2450, TSR 2-2433, MCP23017, TPS3808 + PA0085, INA240, MCP3201, MCP6022, MCP1525, MCP1702 | po 1 | Mouser 24.09 |
| 1N4148 | 4 | Kamami 10 + TME 2 |
| Adaptery SO14 Kamami | 11 (P02 1, P03 7, P04 3) | 18 kupionych; P05, P06, P08–P10 mają SOIC lutowane wprost, więc 7 zostaje |
| Podstawki DIP14 / DIP16 / DIP-8P | P02–P06, P08 / P03, P04 / P06 | Kamami 24.09; dokupione tylko 2× DIP14 dla P04 U2/U3, DIP8 dla P00, opcjonalna DIP16 dla P09 |
| Rezystory 10k, 100k, 4k7, 47k | — | zapas TME po 2 szt. odjęty |
| 1R (P00 R6), 6k8 (P08 R16) | 1 + 1 | zapas TME MF0207FTE-1R i MF0204FTE52-6K8 |
| EEUFR1H220, L-934GD | — | zapas TME po 1 szt. odjęty |
| Styki Mini-Fit Au | 72 | zapas 4 szt. MX-5556GSL7F odjęty |
| Dystanse M3×10 | 41 | zapas 6 szt. odjęty; śruby M3×6 (92), podkładki poliamidowe (98), opaski 2,5 mm (99) i tulejki WAGO 216-206 (2) z zapasu |
| Goldpiny 1×2, zworki | 9 + kilka | ZL201-02G (49) i JUMPER-KPL (19) |
| RG174 | 0,15 m | posiadany przewód |

## Do sprawdzenia przy odbiorze

Wtyki T812 w wariancie A101: czy mają odciążkę. Nagłówki T821 zamiast Würtha: obrys na wydruku 1:1 P03/P04. Przełącznik 611-7201-054 w Mouserze: czy to wersja 7201SYCBE do druku. RN55E3003BB14: TCR 25 ppm/K w karcie. REF5025ID: pinout (2 VIN, 4 GND, 6 VOUT) i klasę wysoką (0,05 %) z kartą TI przed lutowaniem. Farnell zapisuje G6K-2P-Y jako „G6K-2PY DC5”: sprawdzić, że to wersja przewlekana, nie -2F-Y. SN74LVC1G37DBVRQ1: pinout jak w wersji bez Q1. KNP01U-1R: dopuszczalna energia impulsu. Kondensatory 0805 po uwzględnieniu DC bias: P08 C1/C2/C9 ≥ 0,47 µF, P09/P10 C4/C5 ≥ 2,2 µF (wymagania z ZAKUPY tych płytek). Styki DEUTSCH 0460-202-1631: TME ma dokładnie 25 szt., bez zapasu na pomyłkę przy zaciskaniu.
