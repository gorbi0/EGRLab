# P02-R3 — dobór zakupowy i zmiany względem R1

*R3 (Claude, 26.09.2026): zamknięte F2/F3/F4 (P2-01), R16 470 Ω (P2-08), przywrócone spacje w liczbach i kodach (P2-06). Pozostałe pozycje jak w R2.*

Pełna lista elektroniczna: `BOM.csv` (referencje, MPN, ilości, footprinty i źródła). Stare zestawienie zapasów z 24.09 zachowano wyłącznie w `reference/R1-docs/ZAKUPY-P02.md` — nie jest to bieżący stan magazynu.

| Pozycja | Ilość | Wybrana część |
|---|---:|---|
| R5 | 1 | MF0207FTE-330R — 330 Ω, 1 % |
| R6 | 1 | MBB0207VD3012BC100 — 30,1 kΩ, 0,1 %, 25 ppm/K |
| R7, R10 | 2 | MBB0207VD1002BC100 — 10 kΩ, 0,1 %, 25 ppm/K |
| R9 | 1 | MBB0207VD3832BC100 — 38,3 kΩ, 0,1 %, 25 ppm/K |
| R8, R11 | 2 | MF0207FTE-1M — 1 MΩ, 1 % |
| R18, R19 | 2 | MF0207FTE-10K — 10 kΩ, 1 % |
| **R16 (R3)** | 1 | MF0207FTE-470R — 470 Ω, 1 % (w R2: 1 kΩ) |
| R20 | 1 | PR02000201001JA100 — 1 kΩ, 2 W, 5 % |
| C14, C15 | 2 | K103K15X7RF53H5 — 10 nF X7R, raster 5 mm |
| C16 (na adapterze U5) | 1 | GRM21BR71H104KA01L — 100 nF, 50 V, X7R, 0805 |
| F1 — wkładka | 1 | Schurter 0001.2507 — T2A, 5 × 20 mm, 250 VAC / 300 VDC, UL 1500 A przy 300 VDC |
| **F2, F3 — wkładki (R3)** | 2 | Schurter 0001.2504 — T1A, ta sama seria SPT, 300 VDC |
| **F4 — wkładka (R3)** | 1 | Schurter 0001.2501 — T0,5A, ta sama seria SPT, 300 VDC |
| Oprawki F1–F4 | 4 | Stelvio-Kontek PTF78 (istniejące footprinty) |
| J3–J10 | 8 | Molex 39-29-6048 — 4p, pionowe, złocone, bez kołków PCB |
| J11 | 1 | Molex 39-29-6148 — 14p, pionowe, złocone, bez kołków PCB |
| Wtyki LV | 8 | Molex 39-01-2040 — 4p; klucze potwierdzić przy przymiarce |
| Wtyk VSENSE | 1 | Molex 39-01-2140 — 14p; obsadzone tylko 1/2 |
| Styki do tych 9 wtyków | 34 + zapas | Molex 39-00-0074, Au, AWG18–24; użyć AWG22/24 o izolacji zgodnej z kartą |
| Wtyk VMOTOR | 1 | Phoenix GMSTB 2,5/3-ST-7,62 (1767012); zakup wiązki P07 wstrzymany |
| Wiązka SUPPLY | 1 | 2 × 2,5 mm² / 200 mm; P02 lutowane, P01 wtyk MSTB 1757022 |
| Wiązka PSUOK | 1 | taśma 6 × AWG28 / 150 mm; P02 lutowana, P04 IDC6 klucz 5 |
| Wiązka R17 | 1 | 2 × AWG20 / 200 mm; oba końce lutowane do właściwych zacisków |
| Obejmy banku + podstawa/osłona | 3 + 1 | izolujące, dopasowane do puszek Ø35 mm i obudowy; poza PCB |

**Rezystory 0,1 %.** Kody MBB użyto zgodnie z tabelą zamówieniową producenta. Nie oznacza to potwierdzenia dostępności pojedynczych sztuk. Zamiennik musi zachować 0,1 % i ≤ 25 ppm/K oraz pasujący korpus; nie zamieniać na 1 % bez powtórzenia analizy progów.

**Bezpieczniki (R3).** Seria Schurter SPT 5 × 20 (ceramiczna, zwłoczna) ma dla 0,5–3,15 A napięcie 250 VAC / 300 VDC i wg UL zdolność wyłączania 1500 A przy 300 VDC (karta HTML producenta, tabela wariantów). F2/F3 są zwłoczne, bo TRACO zaleca przed TSR2 bezpiecznik zwłoczny (`reference/TRACO_TSR2.txt`: 24 Vin — 3,15 A slow blow). 1 A wystarcza przy budżecie 6 W na VLOG_RES: najwyżej ok. 0,86 A przy 7 V. F4 zabezpiecza tylko przewód VSENSE: P05 przyjmuje go na R31 499 kΩ, więc płynie ok. 25 µA. T0,5A to najmniejsza wkładka tej serii z parametrem DC. Baza v6.1 miała tu F100mA, bez wskazanej wkładki DC.

**Otwarte przy zakupie.** Selektywność F1 (T2A) względem F2/F3 (T1A), stosunek 2:1 w tej samej serii: porównać I²t z karty PDF Schurtera (całkowite I²t T1A < I²t topienia T2A; tej karty nie oglądałem). Dostępność 26.09: TME ma 0001.2504 (ok. 6600 szt.) i 0001.2507 (ok. 7000 szt.); 0001.2501 nie występuje w katalogu TME — sprawdzić Mouser. Molex 39-29-6048: według listy dystrybutorów Molexa TME 0 szt., Mouser 489 szt.

Źródła: [Schurter SPT 5×20](https://www.schurter.com/en/datasheet/SPT_5x20), [Molex 4p](https://www.molex.com/en-us/products/part-detail/39296048), [Molex 14p](https://www.molex.com/en-us/products/part-detail/39296148), [styki Au](https://www.molex.com/en-us/products/part-detail/39000074), [Vishay MBB](https://www.vishay.com/doc?28767=). Wymiarowa zgodność gniazd z lokalnym footprintem jest do fizycznej przymiarki; nie zamawiać wariantów z dodatkowymi kołkami zatrzaskowymi.
