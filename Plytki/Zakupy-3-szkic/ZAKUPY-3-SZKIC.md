# Lista zakupowa 3 — SZKIC (płytki S1: P02 R4, P03 R6, P09 R2, P10 R2, P05 R3, P06 R2)

*1.10.2026, plik generowany przez `src/szkic.py`. Nie zamawiać: P09 R2, P10 R2 i P03 R6 scalone lokalnie 1.10, P05 R3 i P06 R2 z PCB na gałęziach (czekają na scalenie), P11 czeka na rewizję S1; ceny i stany TME są z listy 2 (28.09) i trzeba je sprawdzić w przeglądarce.*

Pozycji: 131; do wyboru typu: 8; do kupienia: 77; częściowo z rejestru: 4; z rejestru: 41. Cena z 28.09 jest tylko dla 18 pozycji do kupienia (razem 77.64 zł netto, bez minimów i wysyłki) — reszta to nowe części S1 bez ceny.

| Pozycja | P02 R4 | P03 R6 | P09 R2 | P10 R2 | P05 R3 | P06 R2 | Razem | Wniosek | TME 28.09 | Oznaczenia |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| 100DP1T1B4M6RE (E-Switch 100, DPDT ON-ON, M6 right angle, gold; code to confirm) |  |  |  |  | 1 |  | 1 | kupić 1 — SW1 P05: E-Switch 100 DPDT ON-ON, kątowy M6 (decyzja 1.10); kod tulei (B4 bez gwintu / B3 z gwintem + H) i dostępność do potwierdzenia (Mouser) |  | P05 R3: SW1 |
| BYPASS-DPDT-10A — przełącznik BYPASS na panelu (w BOM P06 poza płytką) |  |  |  |  |  | 1 | 1 | kupić 1 — SW1 P06 (panel, poza PCB): DPDT ON-ON >= 10 A DC 12-30 V, oczka lutownicze, tuleja z nakrętką; MPN do wyboru (P06 docs/ZAKUPY.md), NKK S6A nie kupować |  | P06 R2: SW1 |
| listwa goldpin 1×13 kątowa (listwa serwisowa) | 2 | 3 | 1 |  | 2 | 1 | 9 | kupić 9 — typ do wyboru: kątowy goldpin 1×13 (posiadany 1×40 jest prosty); można ciąć z kątowego 1×40 |  | P02 R4: J_SV1, J_SV2; P03 R6: J_SV1, J_SV2, J_SV3; P09 R2: J2; P05 R3: J_SV1, J_SV2; P06 R2: J_SV2 |
| listwa goldpin 1×7 kątowa (listwa serwisowa) |  |  |  |  |  | 1 | 1 | kupić 1 — typ do wyboru: kątowy goldpin 1×7 (P06 J_SV1); można ciąć z kątowego 1×40 |  | P06 R2: J_SV1 |
| listwa goldpin 1×9 kątowa (listwa serwisowa) |  |  |  | 1 |  |  | 1 | kupić 1 — typ do wyboru: kątowy goldpin 1×9 (jak wyżej) |  | P10 R2: J2 |
| złącze IDC 2×10 kątowe obudowane, Au (J_BP) | 1 | 3 |  |  | 1 |  | 5 | kupić 5 — typ do wyboru: kątowe obudowane IDC 2×10, złocone (TME nie prowadzi Würtha; w liście 2 były proste Amphenol T821) |  | P02 R4: J_BP; P03 R6: J_BP1, J_BP2, J_BP3; P05 R3: J_BP2 |
| złącze IDC 2×5 kątowe obudowane, Au (J_BP) |  |  |  | 1 | 1 |  | 2 | kupić 2 — typ do wyboru: kątowe obudowane IDC 2×5, złocone |  | P10 R2: J1; P05 R3: J_BP1 |
| złącze IDC 2×8 kątowe obudowane, Au (J_BP) |  |  | 1 |  |  | 1 | 2 | kupić 2 — typ do wyboru: kątowe obudowane IDC 2×8, złocone |  | P09 R2: J1; P06 R2: J_BP |
| 1N5819 |  |  |  |  |  | 1 | 1 | kupić 1 |  | P06 R2: D1 |
| 5KP24A (Littelfuse) | 1 |  |  |  |  |  | 1 | kupić 1 |  | P02 R4: D3 |
| 5 pairs AWG24 |  |  |  |  | 1 |  | 1 | kupić 1 |  | P05 R3: J4 |
| AD7606BBSTZ |  |  |  |  | 1 |  | 1 | kupić 1 |  | P05 R3: U1 |
| Adafruit 4682 microSD (gniazdo 1×9 i dystanse — pozycje niżej) |  | 1 |  |  |  |  | 1 | kupić 1 | Mouser 485-4682: 13,24 zł (lista 2) | P03 R6: SD1 |
| AO3401A |  | 1 |  |  |  |  | 1 | kupić 1 | AO3401A: 1.2860 zł (stan 39078) | P03 R6: Q1 |
| BAT85,133 (Nexperia) |  |  |  |  |  | 1 | 1 | kupić 1 |  | P06 R2: D2 |
| kondensator 1206 X7R 100n | 2 | 13 |  |  | 15 | 11 | 41 | kupić 41 | C1206C104K5RAC: 0.4073 zł (stan 146336) | P02 R4: C27, C28; P03 R6: C2, C1, C3, C4, C5, C6, C7, C8, C9, C10, C11, C12, C15; P05 R3: C4, C5, C6, C7, C8, C11, C14, C15, C16, C17, C18, C19, C20, C21, C22; P06 R2: C16, C6, C7, C8, C9, C10, C11, C12, C13, C14, C15 |
| kondensator 1206 X7R 10n | 1 |  |  |  | 2 |  | 3 | kupić 3 |  | P02 R4: C13; P05 R3: C25, C26 |
| kondensator 1206 X7R 10u |  | 1 |  |  |  |  | 1 | kupić 1 | GRM31CR71C106KA12L: 1.3358 zł (stan 19711) | P03 R6: C14 |
| kondensator 1206 X7R 1u |  | 1 | 2 |  | 5 |  | 8 | kupić 8 | C3216X7R1H105KAB: 0.4292 zł (stan 3220) | P03 R6: C13; P09 R2: C6, C7; P05 R3: C2, C9, C10, C23, C24 |
| kondensator 1206 X7R 2u2 |  |  |  |  | 1 |  | 1 | kupić 1 |  | P05 R3: C3 |
| kondensator 1206 X7R 470n |  |  |  |  |  | 1 | 1 | kupić 1 |  | P06 R2: C1 |
| kondensator 1206 X7R 4u7 |  |  | 2 | 2 |  | 2 | 6 | kupić 6 |  | P09 R2: C4, C5; P10 R2: C4, C5; P06 R2: C4, C5 |
| C3225X7R1E226M250AB |  |  |  |  | 2 |  | 2 | kupić 2 |  | P05 R3: C12, C13 |
| EEUFR1C220 | 2 |  |  |  |  |  | 2 | kupić 2 |  | P02 R4: C22, C24 |
| EEUFR1C221 |  |  |  |  | 1 | 1 | 2 | kupić 2 |  | P05 R3: C1; P06 R2: C3 |
| EEUFR1H100 | 2 |  |  |  |  |  | 2 | kupić 2 | EEUFR1H100: 1.2160 zł (stan 25398) | P02 R4: C21, C23 |
| EEUFR1V222 (16x25, P7.5) or equivalent low-ESR 105 C | 1 |  |  |  |  |  | 1 | kupić 1 |  | P02 R4: C12 |
| ERJ-P08F1001V | 1 |  |  |  |  |  | 1 | kupić 1 |  | P02 R4: R5 |
| Fusible flameproof 22R 2W (MPN to confirm, R4E1-05) | 1 |  |  |  |  |  | 1 | kupić 1 |  | P02 R4: R40 |
| G6K-2P-Y DC5 |  |  |  |  | 3 |  | 3 | kupić 3 |  | P05 R3: K1, K2, K3 |
| insulated panel BNC + RG174 50mm |  |  |  |  | 1 |  | 1 | kupić 1 |  | P05 R3: J6 |
| KNP01U-1R (1R 1W wirewound, body 3x9mm) |  |  |  |  | 1 | 1 | 2 | kupić 2 | KNP01U-1R: 0.3575 zł (stan 300) | P05 R3: R1; P06 R2: R6 |
| Littelfuse 0297001.WXNV + Keystone 3568 | 2 |  |  |  |  |  | 2 | kupić 2 |  | P02 R4: F2, F3 |
| Littelfuse 0297005.WXNV + Keystone 3568 | 1 |  |  |  |  |  | 1 | kupić 1 |  | P02 R4: F1 |
| LTC4412IS6#TRPBF |  | 1 |  |  |  |  | 1 | kupić 1 |  | P03 R6: U5 |
| MCP1700-3302E/TO |  |  |  |  | 1 |  | 1 | kupić 1 | MCP1700-3302E/TO: 1.8240 zł (stan 1591) | P05 R3: U12 |
| P6KE24CA | 1 |  |  |  |  |  | 1 | kupić 1 |  | P02 R4: D13 |
| PCB test pad |  |  |  |  | 5 |  | 5 | kupić 5 |  | P05 R3: TP1, TP2, TP3, TP4, TP5 |
| PESD2CAN,215 Nexperia |  |  |  | 1 |  |  | 1 | kupić 1 |  | P10 R2: D1 |
| Phoenix GMSTBA 2,5/3-G-7,62 (1766246) | 1 |  |  |  |  |  | 1 | kupić 1 |  | P02 R4: J2 |
| PR02000203909JA100 (Vishay PR02 39R 5% 2W, lying; code by analogy with the owned PR02000201009JA100, to confirm) |  |  |  |  |  | 1 | 1 | kupić 1 |  | P06 R2: R21 |
| rezystor 1206 1 % 100K |  | 1 |  |  |  | 3 | 4 | kupić 4 |  | P03 R6: R43; P06 R2: R8, R10, R23 |
| rezystor 1206 1 % 100R |  |  | 2 | 1 |  | 1 | 4 | kupić 4 |  | P09 R2: R11, R12; P10 R2: R1; P06 R2: R19 |
| rezystor 1206 1 % 10K | 8 | 36 |  |  | 23 | 15 | 82 | kupić 82 |  | P02 R4: R36, R38, R53, R51, R52, R63, R59, R64; P03 R6: R1, R13, R11, R5, R2, R3, R6, R7, R8, R15, R16, R17, R18, R19, R20, R21, R22, R23, R24, R25, R26, R27, R28, R29, R30, R31, R32, R33, R35, R50, R53, R56, R64, R69, R70, R76; P05 R3: R9, R10, R11, R12, R14, R15, R16, R17, R18, R19, R20, R21, R22, R23, R24, R25, R30, R39, R40, R41, R42, R53, R54; P06 R2: R7, R9, R13, R14, R15, R16, R17, R18, R20, R25, R26, R27, R28, R33, R34 |
| rezystor 1206 1 % 150K | 1 |  |  |  |  |  | 1 | kupić 1 |  | P02 R4: R7 |
| rezystor 1206 1 % 1K | 11 | 29 | 11 | 5 | 14 | 10 | 80 | kupić 80 |  | P02 R4: R37, R55, R60, R71, R57, R58, R54, R50, R56, R70, R69; P03 R6: R4, R14, R42, R44, R45, R46, R47, R48, R49, R51, R52, R54, R55, R57, R58, R59, R60, R61, R62, R63, R65, R66, R67, R68, R71, R72, R73, R74, R75; P09 R2: R20, R21, R22, R23, R24, R25, R26, R27, R28, R29, R30; P10 R2: R3, R4, R5, R6, R7; P05 R3: R2, R36, R37, R38, R44, R45, R46, R47, R48, R49, R50, R51, R52, R55; P06 R2: R22, R24, R29, R30, R31, R32, R35, R36, R37, R38 |
| rezystor 1206 1 % 220R |  | 2 |  |  |  |  | 2 | kupić 2 | RC1206FR-07220R: 0.1120 zł (stan 36988) | P03 R6: R34, R41 |
| rezystor 1206 1 % 22K | 1 |  |  |  |  |  | 1 | kupić 1 |  | P02 R4: R23 |
| rezystor 1206 1 % 330R |  | 1 |  |  |  |  | 1 | kupić 1 |  | P03 R6: R12 |
| rezystor 1206 1 % 33R |  | 5 |  |  | 2 |  | 7 | kupić 7 |  | P03 R6: R36, R37, R38, R39, R40; P05 R3: R26, R27 |
| rezystor 1206 1 % 41K2 | 1 |  |  |  |  |  | 1 | kupić 1 |  | P02 R4: R9 |
| rezystor 1206 1 % 464K | 1 |  |  |  |  |  | 1 | kupić 1 |  | P02 R4: R11 |
| rezystor 1206 1 % 47R | 1 |  | 4 |  |  | 2 | 7 | kupić 7 |  | P02 R4: R1; P09 R2: R14, R15, R16, R17; P06 R2: R5, R12 |
| rezystor 1206 1 % 4K7 | 6 | 2 |  |  |  |  | 8 | kupić 8 |  | P02 R4: R66, R61, R62, R65, R68, R67; P03 R6: R9, R10 |
| REF5025IDR |  |  |  |  | 1 |  | 1 | kupić 1 |  | P05 R3: U2 |
| RT1206BRB0710KL |  |  |  |  | 1 |  | 1 | kupić 1 |  | P05 R3: R4 |
| RT1206BRB0715KL |  |  |  |  | 1 |  | 1 | kupić 1 |  | P05 R3: R3 |
| RT1206BRB0720KL |  |  |  |  | 1 |  | 1 | kupić 1 |  | P05 R3: R6 |
| RT1206BRB0724K9L |  |  |  |  | 1 |  | 1 | kupić 1 |  | P05 R3: R8 |
| RT1206BRB075K11L |  |  |  |  | 1 |  | 1 | kupić 1 |  | P05 R3: R7 |
| RT1206BRB076K04L |  |  |  |  | 1 |  | 1 | kupić 1 |  | P05 R3: R5 |
| RT1206BRD07100KL |  |  |  |  | 5 |  | 5 | kupić 5 |  | P05 R3: R28, R29, R32, R34, R35 |
| RT1206BRD0710RL |  |  |  |  |  | 2 | 2 | kupić 2 |  | P06 R2: R1, R2 |
| RT1206BRD07300KL |  |  |  |  | 1 |  | 1 | kupić 1 |  | P05 R3: R33 |
| RT1206BRD07499KL |  |  |  |  | 1 |  | 1 | kupić 1 |  | P05 R3: R31 |
| RT1206BRD075K11L |  |  |  |  |  | 2 | 2 | kupić 2 |  | P06 R2: R3, R4 |
| SMD 1206 C0G 50V 5% 220p |  |  |  |  | 7 |  | 7 | kupić 7 |  | P05 R3: C27, C28, C29, C30, C31, C33, C34 |
| SMD 1206 C0G 50V 5% 470p |  |  |  |  |  | 1 | 1 | kupić 1 |  | P06 R2: C2 |
| SN74LVC1G17DBVR |  | 1 |  |  |  |  | 1 | kupić 1 | SN74LVC1G17DBVR: 0.5333 zł (stan 12830) | P03 R6: U6 |
| SN74LVC1G37DBVR |  | 1 |  |  |  |  | 1 | kupić 1 |  | P03 R6: U4 |
| TBD62083APG |  |  |  |  | 1 |  | 1 | kupić 1 |  | P05 R3: U4 |
| TCAN1051VDRQ1 |  |  |  | 1 |  |  | 1 | kupić 1 | TCAN1051VDRQ1: 8.1800 zł (stan 138) | P10 R2: U1 |
| TFF-M2.5X12/DR182 — dystans poliamidowy M2,5 12 mm |  | 2 |  |  |  |  | 2 | kupić 2 | TFF-M2.5X12/DR182: 2.7210 zł (stan 500) | P03 R6: SD1 |
| TLV1702AQDGKRQ1 |  |  |  |  | 1 |  | 1 | kupić 1 |  | P05 R3: U3 |
| WSK25125L000FEA (Vishay WSK2512, 5 mOhm 1%, 1 W at 70 C, TCR +-35 ppm/K, 4-terminal; alt. Bourns CSS2H-2512K-5L00F - footprint differs) |  |  |  |  |  | 1 | 1 | kupić 1 |  | P06 R2: RSH1 |
| ZL262-40SG — gniazdo żeńskie 1×40 złocone, ciąć na 1×22 (M1 na dwóch rzędach) |  | 2 |  |  |  |  | 2 | kupić 2 | ZL262-40SG: 1.4980 zł (stan 11696) | P03 R6: M1 |
| ZL262-9SG — gniazdo żeńskie 1×9 złocone |  | 1 |  |  |  |  | 1 | kupić 1 | ZL262-9SG: 0.4455 zł (stan 1380) | P03 R6: SD1 |
| kondensator 100n X7R 50 V radialny 5 mm (K104) | 6 |  | 3 | 3 |  |  | 12 | rejestr 5 szt. (P01); dokupić co najmniej 7 | K104K15X7RF5TH5: 0.3767 zł (stan 9890) | P02 R4: C8, C10, C11, C25, C26, C29; P09 R2: C1, C2, C3; P10 R2: C1, C2, C3 |
| rezystor THT MF0207 100K (na stojąco) | 6 |  | 7 |  |  |  | 13 | rejestr 7 szt. (P01); dokupić co najmniej 6 | MF0207FTE-100K: 0.1964 zł (stan 18879) | P02 R4: R35, R21, R24, R6, R15, R31; P09 R2: R3, R4, R7, R8, R9, R10, R13 |
| rezystor THT MF0207 10K (na stojąco) | 7 |  | 6 | 3 |  |  | 16 | rejestr 7 szt. (P01); dokupić co najmniej 9 | MF0207FTE-10K: 0.1173 zł (stan 237855) | P02 R4: R26, R41, R16, R30, R32, R42, R43; P09 R2: R1, R2, R5, R6, R18, R19; P10 R2: R2, R8, R9 |
| SN74HC139N |  | 1 | 1 |  |  |  | 2 | rejestr 1 szt. (P03); dokupić co najmniej 1 | SN74HC139N: 4.9500 zł (stan 829) | P03 R6: U2; P09 R2: U3 |
| 1N4148 |  |  |  |  | 3 |  | 3 | z rejestru (10 szt., kupione dla: P05, P08) — sprawdzić przydział z innymi płytkami |  | P05 R3: D1, D2, D3 |
| 1N4148-TAP | 4 |  |  |  |  |  | 4 | z rejestru (5 szt., kupione dla: P01) — sprawdzić przydział z innymi płytkami |  | P02 R4: D11, D12, D7, D8 |
| 2N5401YBU | 1 |  |  |  |  |  | 1 | z rejestru (3 szt., kupione dla: P01) — sprawdzić przydział z innymi płytkami |  | P02 R4: Q4 |
| 2N5551G | 5 |  |  |  |  |  | 5 | z rejestru (7 szt., kupione dla: P01) — sprawdzić przydział z innymi płytkami |  | P02 R4: Q3, Q5, Q6, Q7, Q8 |
| 74LVC125AD,118 (Nexperia) | 1 | 7 | 2 | 1 | 4 | 2 | 17 | z rejestru (25 szt., kupione dla: P02, P03, P04, P05, P06, P08, P09, P10) — sprawdzić przydział z innymi płytkami |  | P02 R4: U9; P03 R6: U11, U12, U13, U14, U21, U22, U23; P09 R2: U1, U2; P10 R2: U2; P05 R3: U8, U9, U10, U11; P06 R2: U5, U6 |
| B32529C1103J289 | 1 |  |  |  |  |  | 1 | z rejestru (2 szt., kupione dla: P01) — sprawdzić przydział z innymi płytkami |  | P02 R4: C5 |
| B32529C1104J000 | 2 |  |  |  |  |  | 2 | z rejestru (3 szt., kupione dla: P01) — sprawdzić przydział z innymi płytkami |  | P02 R4: C2, C4 |
| BZX55C15-TAP | 3 |  |  |  |  |  | 3 | z rejestru (4 szt., kupione dla: P01) — sprawdzić przydział z innymi płytkami |  | P02 R4: D10, D4, D9 |
| C320C102J1G5TA (KEMET C0G 1n, owned; lead pitch to check on the 1:1 print) |  |  |  |  | 1 |  | 1 | z rejestru (2 szt., kupione dla: P01) — sprawdzić przydział z innymi płytkami |  | P05 R3: C32 |
| EEU-EB1J100SH | 1 |  |  |  |  |  | 1 | z rejestru (2 szt., kupione dla: P01) — sprawdzić przydział z innymi płytkami |  | P02 R4: C1 |
| EEUFR1H220 | 2 |  |  |  |  |  | 2 | z rejestru (2 szt., kupione dla: P01) — sprawdzić przydział z innymi płytkami | EEUFR1H220: 1.4660 zł (stan 5947) | P02 R4: C20, C7 |
| EEUFR1H470 | 2 |  |  |  |  |  | 2 | z rejestru (2 szt., kupione dla: P01) — sprawdzić przydział z innymi płytkami |  | P02 R4: C3, C9 |
| INA240A2EDRQ1 |  |  |  |  |  | 1 | 1 | z rejestru (2 szt., kupione dla: P06, P07) — sprawdzić przydział z innymi płytkami |  | P06 R2: U1 |
| JUMPER-KPL — zworka 2,54 (JP1/JP2; początkowo bez zwory) |  |  | 2 |  |  |  | 2 | z rejestru (20 szt., kupione dla: P01) — sprawdzić przydział z innymi płytkami |  | P09 R2: JP1, JP2 |
| L-934GD | 1 | 1 |  |  |  |  | 2 | z rejestru (2 szt., kupione dla: P01) — sprawdzić przydział z innymi płytkami | L-934GD: 0.3280 zł (stan 83929) | P02 R4: LED1; P03 R6: LED1 |
| LM2903P | 1 |  |  |  |  |  | 1 | z rejestru (2 szt., kupione dla: P01) — sprawdzić przydział z innymi płytkami |  | P02 R4: U2 |
| LM2936Z-5.0/NOPB | 1 |  |  |  |  |  | 1 | z rejestru (2 szt., kupione dla: P01) — sprawdzić przydział z innymi płytkami |  | P02 R4: U1 |
| MCP120-300DI/TO | 1 |  |  |  | 1 | 1 | 3 | z rejestru (4 szt., kupione dla: P02, P05, P06, P08) — sprawdzić przydział z innymi płytkami |  | P02 R4: U7; P05 R3: U6; P06 R2: U8 |
| MCP120-450DI/TO | 2 |  |  |  | 1 | 1 | 4 | z rejestru (5 szt., kupione dla: P01, P02, P05, P06, P08) — sprawdzić przydział z innymi płytkami |  | P02 R4: U4, U8; P05 R3: U7; P06 R2: U9 |
| MCP1525-I/TO |  |  |  |  |  | 1 | 1 | z rejestru (1 szt., kupione dla: P06) — sprawdzić przydział z innymi płytkami |  | P06 R2: U10 |
| MCP1702-3302E/TO |  |  |  |  |  | 1 | 1 | z rejestru (1 szt., kupione dla: P06) — sprawdzić przydział z innymi płytkami |  | P06 R2: U4 |
| MCP23017-E/SP |  | 1 |  |  |  |  | 1 | z rejestru (1 szt., kupione dla: P03) — sprawdzić przydział z innymi płytkami |  | P03 R6: U1 |
| MCP3201-BI/P |  |  |  |  |  | 1 | 1 | z rejestru (2 szt., kupione dla: P06, P07) — sprawdzić przydział z innymi płytkami |  | P06 R2: U3 |
| MCP6022-I/P |  |  |  |  |  | 1 | 1 | z rejestru (1 szt., kupione dla: P06) — sprawdzić przydział z innymi płytkami |  | P06 R2: U2 |
| MF0204FTE52-6K8 | 1 |  |  |  |  |  | 1 | z rejestru (2 szt., kupione dla: P01) — sprawdzić przydział z innymi płytkami |  | P02 R4: R29 |
| rezystor THT MF0207 1R (na stojąco) | 1 |  |  |  |  |  | 1 | z rejestru (2 szt., kupione dla: P01) — sprawdzić przydział z innymi płytkami |  | P02 R4: R2 |
| rezystor THT MF0207 2K2 (na stojąco) | 1 |  |  |  |  |  | 1 | z rejestru (2 szt., kupione dla: P01) — sprawdzić przydział z innymi płytkami |  | P02 R4: R13 |
| rezystor THT MF0207 470K (na stojąco) | 1 |  |  |  |  |  | 1 | z rejestru (2 szt., kupione dla: P01) — sprawdzić przydział z innymi płytkami |  | P02 R4: R22 |
| rezystor THT MF0207 47K (na stojąco) | 4 |  |  |  | 1 | 1 | 6 | z rejestru (6 szt., kupione dla: P01) — sprawdzić przydział z innymi płytkami | MF0207FTE-47K: 0.3242 zł (stan 21437) | P02 R4: R18, R25, R20, R33; P05 R3: R13; P06 R2: R11 |
| rezystor THT MF0207 4K7 (na stojąco) | 3 |  |  |  | 1 |  | 4 | z rejestru (6 szt., kupione dla: P01) — sprawdzić przydział z innymi płytkami | MF0207FTE-4K7: 0.3194 zł (stan 7099) | P02 R4: R17, R19, R14; P05 R3: R43 |
| rezystor THT MF0207 820R (na stojąco) | 1 |  |  |  |  |  | 1 | z rejestru (2 szt., kupione dla: P01) — sprawdzić przydział z innymi płytkami |  | P02 R4: R3 |
| MKS2D041001K00JO00 | 1 |  |  |  |  |  | 1 | z rejestru (2 szt., kupione dla: P01) — sprawdzić przydział z innymi płytkami |  | P02 R4: C6 |
| PR02000201009JA100 | 1 |  |  |  |  |  | 1 | z rejestru (2 szt., kupione dla: P01) — sprawdzić przydział z innymi płytkami |  | P02 R4: R27 |
| SN74HC08N | 1 |  |  |  | 1 | 1 | 3 | z rejestru (8 szt., kupione dla: P02, P04, P05, P06, P08) — sprawdzić przydział z innymi płytkami |  | P02 R4: U10; P05 R3: U5; P06 R2: U7 |
| STPS20100CT | 2 |  |  |  |  |  | 2 | z rejestru (2 szt., kupione dla: P01) — sprawdzić przydział z innymi płytkami |  | P02 R4: D1, D2 |
| SUP53P06-20-E3 | 3 |  |  |  |  |  | 3 | z rejestru (3 szt., kupione dla: P01) — sprawdzić przydział z innymi płytkami |  | P02 R4: Q9, Q1, Q2 |
| TL431BILP | 1 |  |  |  |  |  | 1 | z rejestru (2 szt., kupione dla: P01) — sprawdzić przydział z innymi płytkami |  | P02 R4: U3 |
| TPS3808G33DBVR |  | 1 |  |  |  |  | 1 | z rejestru (2 szt., kupione dla: P03) — sprawdzić przydział z innymi płytkami |  | P03 R6: U3 |
| TSR 2-2433 | 1 |  |  |  |  |  | 1 | z rejestru (1 szt., kupione dla: P02) — sprawdzić przydział z innymi płytkami |  | P02 R4: U6 |
| TSR 2-2450 | 1 |  |  |  |  |  | 1 | z rejestru (1 szt., kupione dla: P02) — sprawdzić przydział z innymi płytkami |  | P02 R4: U5 |
| YR1B10KCC | 4 |  |  |  |  |  | 4 | z rejestru (4 szt., kupione dla: P01) — sprawdzić przydział z innymi płytkami |  | P02 R4: R4, R10, R12, R44 |
| goldpin 1×3 prosty (JP1/JP2; zworki — pozycja JUMPER-KPL) |  |  | 2 |  |  |  | 2 | z posiadanej prostej listwy 1×40 (rejestr: Kamami 1207864, przydział z adapterami) |  | P09 R2: JP1, JP2 |
| owned (Waveshare ESP32-S3-DEV-KIT-N32R16V) on 2x 1x22 female headers |  | 1 |  |  |  |  | 1 | posiadane (opis w BOM) |  | P03 R6: M1 |
| Owned MAX31856 XU module, soldered directly by its 1x9 header (no socket) |  |  | 2 |  |  |  | 2 | posiadane (opis w BOM) |  | P09 R2: J3, J4 |
| PCB termination; 1 x AWG22 | 1 |  |  |  |  |  | 1 | przewód lub zakończenie lutowane — poza listą części (wiązki, `docs/` płytki) |  | P02 R4: J15 |
| PCB termination; 2 x 1.5 mm2 to XT60 (wall) | 1 |  |  |  |  |  | 1 | przewód lub zakończenie lutowane — poza listą części (wiązki, `docs/` płytki) |  | P02 R4: J1 |
| PCB termination; 2 x AWG22 to panel switch | 1 |  |  |  |  |  | 1 | przewód lub zakończenie lutowane — poza listą części (wiązki, `docs/` płytki) |  | P02 R4: J14 |
| Soldered 120ohm twisted pair |  |  |  | 1 |  |  | 1 | przewód lub zakończenie lutowane — poza listą części (wiązki, `docs/` płytki) |  | P10 R2: J3 |
| Soldered harness |  |  |  |  |  | 3 | 3 | przewód lub zakończenie lutowane — poza listą części (wiązki, `docs/` płytki) |  | P06 R2: J3, J4, J5 |
| Tinned copper wire 0.6 mm | 1 |  |  |  |  |  | 1 | przewód lub zakończenie lutowane — poza listą części (wiązki, `docs/` płytki) |  | P02 R4: R34 |

## Uwagi

- „z rejestru” znaczy tylko, że w rejestrze jest tyle sztuk tej części. Część z nich mogła być przewidziana dla płytek spoza szkicu (P04, P05, P06, P08 — kolumna „kupione dla”); przydział ustalić przy liście wiążącej.
- Rezystory i kondensatory 1206 bez MPN w BOM (P09/P10: „SMD 1206 …”) zgrupowane z tymi samymi wartościami P02/P03 (Yageo RC1206FR-07…, Murata GRM31).
- Poza szkicem: P00 R3 i P04 R2.2 (bez zmian względem listy 2), P08 i P11 (rewizje S1), przewody i drobne mechaniczne (P06: końce wiązek J3 / J4 / J5 w docs/WIAZKI.md).
