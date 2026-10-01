# P05 DAQ — R3, schemat w formacie S1

*1.10.2026. Pakiet na kopii łańcucha `P05-R2-review/src` według `Plytki/Format-S1/zadania/ZADANIE-P05-S1.md` (decyzja użytkownika 1.10.2026: dwa złącza J_BP, wariant B). Zamknięty pakiet R2 bez zmian.*

**1.10.2026 (lokalnie): poprawki po recenzji PR #7** — listwa J_SV1 13 kołków (szyny obok GND i siebie, VBAT_SENSE między GND), bilans posiadanych części z P02 R4 (kondensatory foliowe jako nowe 1206), punkt otwarty o pojemności 5V_SYS, pomiar REF_2V5 w ODBIOR, kontrola kolumny rezystorów w `SERWIS.csv`, poprawki dokumentów. Decyzje użytkownika 1.10: **SW1 = E-Switch 100 kątowy (M6)** i **C1 = 220 µF**.

**Status: schemat R3 gotowy do recenzji. PCB w tym pakiecie nie ma** — layout robi sesja lokalna (`docs/CHMURA.md`, zasada 6). Sprzętu nie zmontowano ani nie zmierzono.

Obwód R2 zostaje: okno DAQ_OK z REF5025IDR (R5 6,04 kΩ, R7 5,11 kΩ), R13 47 kΩ, CH7 = VBAT_SENSE, przekaźniki K1–K3, tor AUX. Zmieniają się złącza do innych płytek, punkty pomiarowe i typy części. `verify_s1.py` sprawdza na eksportowanej netliście, że poza wymienionymi złączami każdy pin obwodu R2 ma tę samą sieć co w R2 (`reference/P05-R2.xml`); od 1.10 także SW1 (E-Switch M6 ma układ styków jak C&K 7201 z R2 — wersja z chmury lustrzyła biegun B pod suwak JS).

## Zmiany R2 → R3

| Punkt | R2 | R3 |
|---|---|---|
| Płytka | obrys R1 160 × 120 mm (layout niedokończony) | klasa 2/3, 106,5 × 100 mm, sloty S1–S2 poziomu 3, dystanse 20 mm |
| DAQ do P03 | J1 B2B TSW-108-08-G-D-NA (P05 obok P03) | **J_BP2** IDC 2×10 kątowe, slot S2 (x = 80,0 mm); DAQ na tych samych pinach co P03 R6 J_BP2; 16 i 20 GND (rezerwa) |
| Zasilanie, DAQ_OK, VBAT | J2 LV05 (Mini-Fit 4p), J3 DAQOK (IDC 6p), J5 VSENSE (Mini-Fit 14p) | **J_BP1** IDC 2×5 kątowe, slot S1 (x = 26,5 mm): 5V_SYS na 2 i 4, DAQ_OK na 6, GND na 8 (rezerwa), VBAT_SENSE na 10 |
| 3V3_IO | LV05.3 → TP5 (tylko punkt kontrolny) | **nie wchodzi na P05**; wyjątek od S1 §5 („3V3_IO na ≥ 1 pinie”): logika P05 ma własne 3V3_DAQ z U12, więc zewnętrzne 3V3 nie miałoby odbiornika |
| Przewody | 5 wiązek + B2B | zostają J4 TAPS i J6 AUX (S1 §5), przy brzegu x = 0 |
| Punkty pomiarowe | TP1–TP16 | **J_SV1** 1×13 (S1: VBAT między GND, zasilania obok siebie i GND, okno, U4.18; GND na 1, 3, 7, 13) i **J_SV2** 1×13 (S2: sygnały DAQ i nadzór) — 20 kołków przez rezystory przy węźle R36–R55; TP1–TP5 tylko przy U1 (GND, ADC_REF, REGCAP_A/D, REFCAP) |
| R i C | THT MBB0207/metal film, 0603/0805/1210 | nowe **SMD 1206**; posiadane THT z rejestru tam, gdzie zostaje zapas (`docs/ZAKUPY.md`) |
| Rezystory precyzyjne R3–R8 | MBB0207 0,1 %, 25 ppm/K | **1206 0,1 %, 10 ppm/K** (propozycja Yageo RT1206BRB07…) — patrz „Okno DAQ_OK” |
| Rezystory precyzyjne R28, R29, R31–R35 | MBB0207 0,1 % | 1206 0,1 %, 25 ppm/K (RT1206BRD07…) |
| SW1 | C&K 7201SYCBE (dźwignia), HI = 2-1 + 5-4 | **E-Switch 100 DPDT ON-ON, kątowy M6** (decyzja 1.10; kod np. 100DP1T1B4M6RE do potwierdzenia), footprint z rysunku M6-DP (karta s. 11); styki jak w R2: HI = 2-1 + 5-4, LO = 2-3 + 5-6 (pin 6 wolny). Wersja z chmury: suwak C&K JS202011AQN |
| C1 | 470 µF / 16 V, D8 | **220 µF / 16 V** (decyzja 1.10: razem z P06 C3 ok. 486 µF na 5 V wobec 600 µF dla TSR 2-2450) |
| Arkusze | 8 | 9 (nowy `SERWIS`: listwy) |

**Wyjątki od „nowe = SMD 1206”:** R1 1 Ω (KNP01U-1R, 1 W leżący — udar ładowania C1 ok. 2,8 mJ przy 220 µF, posiadane MF0207 1R mają 0,6 W); C1 220 µF elektrolit radialny; C12/C13 22 µF w 1210 (1206 22 µF przy 4,4 V nie daje pewnie Ceff ≥ 10 µF z kroku 11 ODBIOR); diody i układy scalone bez zmian obudów.

**Posiadane części THT w P05:** R13 47k i R43 4,7k (MF0207 na stojąco), C32 KEMET C0G 1 n, D1–D3 1N4148, U5–U11 z przydziału. 10 k i 100 k MF0207 oraz K104K15 100 n nie mają zapasu po P02 R4, P09 R2 i P10 R2; kondensatorów foliowych (MKT 10 n / 100 n, WIMA 1 µF) P02 R4 zostawia po jednej sztuce, więc C2, C23, C16–C18, C25 i C26 są nowe 1206 (1.10; pierwsza wersja liczyła tylko P09/P10) — bilans w `docs/ZAKUPY.md`.

## Okno DAQ_OK — dlaczego 10 ppm/K

R2 liczyło okno dla MBB0207 (0,1 % + 25 ppm/K × 100 K) bez dodatku na lutowanie i starzenie rezystorów; dolny narożnik wychodził 4,7524 V przy regule 4,75 V, czyli **2,4 mV zapasu**. Rezystory cienkowarstwowe SMD przesuwają się przy lutowaniu i z czasem; karty Yageo RT nie dało się pobrać w chmurze (proxy), więc `verify_electrical.py` dolicza założone **0,1 % na rezystor** i klasę TCR z MPN w eksporcie:

| Rezystory okna R3–R8 | Dodatek | Dolny narożnik | Górny narożnik | 4,75–5,25 V |
|---|---|---:|---:|---|
| 25 ppm/K (podstawa R2) | 0 | 4,7524 V | 5,2344 V | tak |
| 25 ppm/K | 0,1 % | **4,7445 V** | 5,2425 V | **nie** (próba ujemna) |
| **10 ppm/K (R3)** | **0,1 %** | **4,7564 V** | **5,2304 V** | **tak** |

Zapas 5VA do narożników przy TSR 2-2450 (`electrical-checks.json`, `window.tsr_margin`): −2 %/25 °C +35,5 mV; −2 %/60 °C **+0,5 mV**; +2 %/25 °C +53,4 mV; +2 %/60 °C +18,4 mV. Przypadek −2 % w upale nadal jest na granicy, więc kryterium odbioru 5V_SYS 4,93–5,07 V przy 23 °C zostaje. Przy 10 ppm/K także REF5025AIDR (klasa standardowa) mieściłby się w regule — z zapasem 1,6 mV; U2 zostaje REF5025ID(R) według decyzji z 29.09.

## Kontrole

`python src/run_schematic.py` (Python KiCada; w chmurze `scripts/egrlab-docker python3 src/run_schematic.py`): schemat, tabele, ERC, netlista, trzy zestawy kontroli, PDF, `verification/QA.md`, manifest.

- ERC **0** na 9 arkuszach; netlista **466/466** pinów zgodnych z `parts.py`, 119 części, 111 sieci (R2: 421/421, 110 części).
- `verify_electrical.py` (obwód R2 dostosowany do S1): **21/21**, mutacje **12/12** — m.in. brak 3V3_IO, VBAT_SENSE na J_BP1.10, SW1 sprawdzany z geometrii footprintu (dźwignia łączy wspólne obu biegunów z polami na tym samym końcu), okno z klasą TCR z MPN.
- `verify_s1.py` (kontrakt S1, niezależny od generatora): **26/26**, mutacje **33/33** wykryte przez kontrolę docelową, próba zerowa czysta. Pinout J_BP1/J_BP2 dokładnie jak w zadaniu; DAQ na pinach P03 R6 J_BP2 (`reference/P03-R6-J_BP.csv` z gałęzi `p03-r6-pcb`, b094fa7); każda sieć dawnych J1/J2/J3/J5 na J_BP dokładnie raz (5V_SYS dwa razy, 3V3_IO wcale); nieparzyste piny GND; GND po obu stronach ADC_SCLK i MEAS_EN w taśmie; TAPS i AUX poza J_BP; listwy ≤ 13 kołków, GND na końcach (wewnątrz dozwolone), szyny tylko obok GND albo innej szyny i VBAT_SENSE tylko obok GND (1.10), rezystor przy węźle w klasie z S1 §6, pokrycie listy z ODBIOR; `J_BP.csv`/`SERWIS.csv` zgodne z netlistą; źródła i obudowy części; obwód R2 bez zmian.

## Wymagania dla layoutu (sesja lokalna)

- J4 (TAPS), J6 (AUX) i SW1 od strony x = 0; dźwignia SW1 (E-Switch M6, tuleja i dźwignia równolegle do płytki) przez otwór w panelu przy x = 0 — położenie tak, by tuleja sięgała ścianki (makieta).
- J_BP1 w slocie S1 (środek x = 26,5 mm), J_BP2 w slocie S2 (x = 80,0 mm), pin 1 od strony mniejszego x. J_SV1 w x = 10–43 mm, J_SV2 w x = 63,5–96,5 mm; rezystory R36–R55 przy węzłach (SMD mogą być od spodu; R43 to posiadany MF0207 na stojąco — od góry). Przestawienie kołków: `src/parts.py` (listy SV1/SV2, `SV1_PIN`), potem `run_schematic.py` — `SERWIS.csv`, kontrole i odwołania w ODBIOR idą za nim.
- Odsprzęganie U1 według `Plytki/P05-R2-review/wip-layout-obrys-R1/` (opisy „Cx przy U1.nn” w arkuszu ADC zostają); kondensatory są teraz 1206 — wzór trzeba dopasować, dozwolone od spodu pod U1 tylko do 1,5 mm (100 n 1206; nie C12/C13 1210 o grubości 2,5 mm ani 1–2,2 µF 1206 o grubości do 1,6 mm). DOUT nie pod U1 po B.Cu (P5-01).
- Od spodu tylko SMD ≤ 1,5 mm, bez SOIC; najwyższe: SW1 ok. 11,4 mm (obudowa M6) i C1 ok. 11,2 mm — w limicie 16,5 mm.
- Szczegóły: `docs/MECHANIKA.md`.

## Otwarte punkty

- **SW1 (rozstrzygnięte 1.10):** E-Switch 100 w wersji kątowej M6 zamiast pionowego 100DP1T1B1M2REH (ok. 28 mm, ponad 16,5 mm poziomu 3; karta `reference/E-Switch-100-series.pdf`, s. 2, 6, 8, 11). Do potwierdzenia przy zakupie: dokładny kod (tuleja B4 bez gwintu — standard dla M6, albo B3 z gwintem i nakrętką na panel) i dostępność; footprint z rysunku M6-DP sprawdzić na wydruku 1:1 z próbką.
- **Pojemność 5V_SYS (rozstrzygnięte 1.10):** C1 = 220 µF (P06 C3 też 220 µF w rewizji S1) — razem ok. 486 µF wobec 600 µF dla TSR 2-2450; start kompletu i tak mierzyć na stole. MPN C1 (EEUFR1C221, D6,3 × 11,2 mm) do potwierdzenia. Budżet w `docs/INTEGRACJA.md` (ok. 538 µF) jest sprzed P02 R4 i decyzji.
- **Zapas z rejestru:** bilans w `docs/ZAKUPY.md` (1.10: z P02 R4); 10 k i 100 k MF0207 oraz K104 zużywają P02 R4, P09 R2 i P10 R2, P05 bierze je jako nowe 1206. Budżet dzielników kanałów (0,1 %, 25 ppm/K): `electrical-checks.json`, `channels.*.divider_budget`.
- R1 KNP01U-1R: odporność na impuls ok. 2,8 mJ (C1 220 µF) z karty.

## Pliki

- `eda/` — schemat KiCad 10 (9 arkuszy A3) i biblioteki; bez PCB.
- `output/pdf/P05-R3-schemat.pdf`, `output/previews/sch-*.png`.
- `docs/` — `J_BP.csv` i `SERWIS.csv` (kontrakty dla P12 i listew), BOM, `ZAKUPY.md`, `zakupy.csv`, `pinout.csv`, `interfejsy.csv`/`wiazki-BOM.csv` (TAPS, AUX), ODBIOR R3, MECHANIKA R3, INTEGRACJA, PROJEKT.
- `verification/` — ERC, netlista, `schematic-check.json`, `electrical-checks.json`, `s1-checks.json`, `QA.md`, logi, manifest.
- `reference/` — `P05-R2.xml` (eksport R2 do porównania), `P03-R6-J_BP.csv`, `baseline.json`, karty.
