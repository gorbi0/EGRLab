# Zakupy P08-R2 — ilości na jedną płytkę (S1)

Źródło: **rejestr** = pozycja z `Zamowione/zamowione.csv` (posiadane; przydział P08 z zamówień 24.09 albo zapas po P02 R4, P05 R3, P06 R2, P09 R2, P10 R2); **nowe** = do kupienia. Płytka z JLCPCB (klasa 1/3, 53 × 100 mm, slot S1 poziomu 5). Schemat bez PCB.

| Źródło | Nazwa | Ilość | Referencje / obudowa |
|---|---|---:|---|
| nowe | 2 x AWG22 soldered, tie anchor 12 mm | 1 | J4 / PTH_TSENSOR_2 |
| nowe | EEUFR1E220 | 1 | C10 / CP_Radial_D5.0mm_P2.00mm |
| nowe | G6K-2P-Y DC5 | 1 | K1 / G6K_2P_Y_verified |
| nowe | Goldpin 1x13 2.54mm angled (buy angled strip, owned 1x40 is straight) | 1 | J2 / PinHeader_1x13_P2.54mm_Horizontal |
| nowe | IDC header 2x8 2.54mm angled shrouded, Au (type as P09 R2 J1 in the purchase list) | 1 | J1 / IDC-Header_2x08_P2.54mm_Horizontal |
| nowe | MCP120-300DI/TO | 1 | U8 / TO-92_Inline_Wide |
| nowe | SMD 1206 1% 0.25W 100R | 2 | R11, R13 / R_1206_3216Metric_Pad1.30x1.75mm_HandSolder |
| nowe | SMD 1206 1% 0.25W 10K | 14 | R2, R3, R4, R5, R6, R7, R8, R9, R10, R12, R14, R17, R18, R27 / R_1206_3216Metric_Pad1.30x1.75mm_HandSolder |
| nowe | SMD 1206 1% 0.25W 1K | 10 | R19, R20, R21, R22, R23, R24, R25, R26, R28, R29 / R_1206_3216Metric_Pad1.30x1.75mm_HandSolder |
| nowe | SMD 1206 1% 0.25W 232K | 1 | R1 / R_1206_3216Metric_Pad1.30x1.75mm_HandSolder |
| nowe | SMD 1206 X7R 25V 10% 100n | 6 | C3, C4, C5, C6, C7, C8 / C_1206_3216Metric_Pad1.33x1.80mm_HandSolder |
| nowe | SMD 1206 X7R 25V 10% 1u | 3 | C1, C2, C9 / C_1206_3216Metric_Pad1.33x1.80mm_HandSolder |
| nowe | TBD62083APG | 1 | U2 / DIP-18_W7.62mm |
| nowe | TPS2553DBVR | 1 | U1 / SOT-23-6 |
| rejestr | 1N4148 | 1 | D1 / D_DO-35_SOD27_P7.62mm_Horizontal |
| rejestr | 74LVC125AD,118 (Nexperia) | 2 | U4, U5 / SOIC-14_3.9x8.7mm_P1.27mm |
| rejestr | MCP120-300DI/TO | 1 | U6 / TO-92_Inline_Wide |
| rejestr | MCP120-450DI/TO | 1 | U7 / TO-92_Inline_Wide |
| rejestr | MF0204FTE52-6K8 Yageo 6.8k 1% 0.4W (owned, standing) | 1 | R16 / R_Axial_DIN0204_L3.6mm_D1.6mm_P2.54mm_Vertical |
| rejestr | MF0207FTE-4K7 Yageo 4.7k 1% 0.6W (owned, standing) | 1 | R15 / R_Axial_DIN0207_L6.3mm_D2.5mm_P5.08mm_Vertical |
| rejestr | SN74HC08N | 1 | U3 / DIP-14_W7.62mm |

## Bilans części posiadanych, które bierze P08

| Część z rejestru | Rejestr | Zużycie innych płytek (BOM-y S1) | Zostaje | P08 R2 bierze | Uwagi |
|---|---:|---|---:|---:|---|
| MF0207FTE-4K7 | 6 | P02 R4: 3, P05 R3: 1 | 2 | 1 | R15 (dzielnik EN), na stojąco |
| MF0204FTE52-6K8 | 2 | P02 R4: 1 | 1 | 1 | R16 (dzielnik EN), na stojąco, raster 2,54 mm — ostatnia sztuka |
| MCP120-300DI/TO (Mouser, 4 szt.: P02, P05, P06, P08) | 4 | P02 R4: 1, P05 R3: 1, P06 R2: 1 | 1 | 1 | U6; **U8 (MCP120-300) nowy** — R1 dodała drugi nadzorca 3,3 V, którego zamówienie z 24.09 nie obejmowało |
| MCP120-450DI/TO (TME 2 + Mouser 3) | 5 | P02 R4: 2, P05 R3: 1, P06 R2: 1 | 1 | 1 | U7 |
| SN74HC08N + podstawka DIP14 (Kamami 648) | 8 / 10 | P02 R4, P05 R3, P06 R2: po 1; P04 (R2.2): 4 | 1 | 1 | U3 w podstawce |
| 74LVC125AD,118 (Nexperia) | 25 | 17 (szkic listy 3) + P04: 3 | 5 | 2 | U4, U5; SOIC lutowane wprost od góry (poziom 5: od spodu bez SOIC) |
| 1N4148 (Kamami 1187768) | 10 | P05 R3: 3 | 7 | 1 | D1 |

MF0207 10 k / 100 k i K104K15X7RF5TH5 100 n nie mają zapasu (zużywają je P02 R4, P09 R2, P10 R2), więc wszystkie 10 k i 100 n P08 są nowe 1206. Dwa EEUFR1H220 z rejestru bierze P02 R4 — C10 jest nowy. Bilans wiążący: lista zakupowa 3/4 (przydział także względem równoległej P04 R3).

Uwagi do zakupów:
- U1 TPS2553**DBVR** (aktywny wysoki EN, stałe ograniczenie; TPS2552 i TPS2553-1 nie są zamiennikami), SOT-23-6 od góry. Adapter SOT-23-6 niepotrzebny (płytka z fabryki).
- U2 TBD62083APG (DIP18; nie ULN2803), K1 Omron **G6K-2P-Y DC5** (monostabilny; nie G6KU).
- R1 232 kΩ 1 % 1206 (limit prądu TPS: 99–139 mA obliczeniowo).
- J1 (J_BP): obudowane złącze kątowe IDC 2×8, raster 2,54 mm, styki Au (ten sam typ co J1 P09 R2); taśma IDC 2×8 do P12 (dwa gniazda zaciskowe).
- J2 (SERWIS): goldpin **kątowy** 1×13 (posiadana listwa 1×40 jest prosta).
- J4 (TSENSOR): bez złącza na płytce — 2 × AWG22 lutowane w PTH, opaska nylonowa 2,5 mm na kotwę; długość do portu TEST z makiety panelu.
- Z wersji R1 znikają: Molex 39-29-6028 (Mini-Fit 2p), wiązki W1 LV08 (Mini-Fit 4p), W2 SENSOR i W3 SFAULT (taśmy IDC6), adaptery Kamami SO14/SOT-23 z przydziału P08, rezystory DIN0207 leżące, kondensatory 0805.
