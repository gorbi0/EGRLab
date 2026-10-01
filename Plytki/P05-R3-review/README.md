# P05 DAQ — R3, schemat w formacie S1

*1.10.2026. Pakiet na kopii łańcucha `P05-R2-review/src` według `Plytki/Format-S1/zadania/ZADANIE-P05-S1.md` (decyzja użytkownika 1.10.2026: dwa złącza J_BP, wariant B). Zamknięty pakiet R2 bez zmian.*

**Status: schemat R3 gotowy do recenzji. PCB w tym pakiecie nie ma** — layout robi sesja lokalna (`docs/CHMURA.md`, zasada 6). Sprzętu nie zmontowano ani nie zmierzono.

Obwód R2 zostaje: okno DAQ_OK z REF5025IDR (R5 6,04 kΩ, R7 5,11 kΩ), R13 47 kΩ, CH7 = VBAT_SENSE, przekaźniki K1–K3, tor AUX. Zmieniają się złącza do innych płytek, punkty pomiarowe i typy części. `verify_s1.py` sprawdza na eksportowanej netliście, że poza wymienionymi złączami i świadomym lustrzeniem bieguna B w SW1 każdy pin obwodu R2 ma tę samą sieć co w R2 (`reference/P05-R2.xml`).

## Zmiany R2 → R3

| Punkt | R2 | R3 |
|---|---|---|
| Płytka | obrys R1 160 × 120 mm (layout niedokończony) | klasa 2/3, 106,5 × 100 mm, sloty S1–S2 poziomu 3, dystanse 20 mm |
| DAQ do P03 | J1 B2B TSW-108-08-G-D-NA (P05 obok P03) | **J_BP2** IDC 2×10 kątowe, slot S2 (x = 80,0 mm); DAQ na tych samych pinach co P03 R6 J_BP2; 16 i 20 GND (rezerwa) |
| Zasilanie, DAQ_OK, VBAT | J2 LV05 (Mini-Fit 4p), J3 DAQOK (IDC 6p), J5 VSENSE (Mini-Fit 14p) | **J_BP1** IDC 2×5 kątowe, slot S1 (x = 26,5 mm): 5V_SYS na 2 i 4, DAQ_OK na 6, GND na 8 (rezerwa), VBAT_SENSE na 10 |
| 3V3_IO | LV05.3 → TP5 (tylko punkt kontrolny) | **nie wchodzi na P05**; wyjątek od S1 §5 („3V3_IO na ≥ 1 pinie”): logika P05 ma własne 3V3_DAQ z U12, więc zewnętrzne 3V3 nie miałoby odbiornika |
| Przewody | 5 wiązek + B2B | zostają J4 TAPS i J6 AUX (S1 §5), przy brzegu x = 0 |
| Punkty pomiarowe | TP1–TP16 | **J_SV1** 1×11 (S1: zasilania, okno, VBAT, U4.18) i **J_SV2** 1×13 (S2: sygnały DAQ i nadzór) — 20 kołków przez rezystory przy węźle R36–R55; TP1–TP5 tylko przy U1 (GND, ADC_REF, REGCAP_A/D, REFCAP) |
| R i C | THT MBB0207/metal film, 0603/0805/1210 | nowe **SMD 1206**; posiadane THT z rejestru tam, gdzie zostaje zapas (`docs/ZAKUPY.md`) |
| Rezystory precyzyjne R3–R8 | MBB0207 0,1 %, 25 ppm/K | **1206 0,1 %, 10 ppm/K** (propozycja Yageo RT1206BRB07…) — patrz „Okno DAQ_OK” |
| Rezystory precyzyjne R28, R29, R31–R35 | MBB0207 0,1 % | 1206 0,1 %, 25 ppm/K (RT1206BRD07…) |
| SW1 | C&K 7201SYCBE (dźwignia), HI = 2-1 + 5-4 | **C&K JS202011AQN** (suwak DPDT ON-ON, kątowy), footprint KiCad z rysunku C&K; HI = 2-1 + 5-6, LO = 2-3 + 5-4 (pin 4 wolny) |
| Arkusze | 8 | 9 (nowy `SERWIS`: listwy) |

**Wyjątki od „nowe = SMD 1206”:** R1 1 Ω (KNP01U-1R, 1 W leżący — udar ładowania C1 ok. 6 mJ, posiadane MF0207 1R mają 0,6 W); C1 470 µF elektrolit radialny; C12/C13 22 µF w 1210 (1206 22 µF przy 4,4 V nie daje pewnie Ceff ≥ 10 µF z kroku 11 ODBIOR); diody i układy scalone bez zmian obudów.

**Posiadane części THT w P05:** R13 47k i R43 4,7k (MF0207 na stojąco), C25/C26 MKT 10 n, C16–C18 MKT 100 n (U5 DIP, U6/U7 TO-92 — nie przy AD7606B), C2/C23 WIMA MKS2 1 µF (wejścia U12 i U2), C32 KEMET C0G 1 n, D1–D3 1N4148, U5–U11 z przydziału. 10 k i 100 k MF0207 oraz K104K15 100 n nie mają zapasu po P09 R2 i P10 R2 — bilans w `docs/ZAKUPY.md`.

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

- ERC **0** na 9 arkuszach; netlista **464/464** pinów zgodnych z `parts.py`, 119 części, 111 sieci (R2: 421/421, 110 części).
- `verify_electrical.py` (obwód R2 dostosowany do S1): **21/21**, mutacje **12/12** — m.in. brak 3V3_IO, VBAT_SENSE na J_BP1.10, SW1 sprawdzany z geometrii footprintu (suwak łączy wspólny z polem po tej samej stronie), okno z klasą TCR z MPN.
- `verify_s1.py` (kontrakt S1, niezależny od generatora): **24/24**, mutacje **29/29** wykryte przez kontrolę docelową, próba zerowa czysta. Pinout J_BP1/J_BP2 dokładnie jak w zadaniu; DAQ na pinach P03 R6 J_BP2 (`reference/P03-R6-J_BP.csv` z gałęzi `p03-r6-pcb`, b094fa7); każda sieć dawnych J1/J2/J3/J5 na J_BP dokładnie raz (5V_SYS dwa razy, 3V3_IO wcale); nieparzyste piny GND; GND po obu stronach ADC_SCLK i MEAS_EN w taśmie; TAPS i AUX poza J_BP; listwy ≤ 13 kołków, GND na końcach i tylko tam, rezystor przy węźle w klasie z S1 §6, pokrycie listy z ODBIOR; `J_BP.csv`/`SERWIS.csv` zgodne z netlistą; źródła i obudowy części; obwód R2 bez zmian.

## Wymagania dla layoutu (sesja lokalna)

- J4 (TAPS), J6 (AUX) i SW1 od strony x = 0; suwak SW1 dostępny przez panel albo od strony B (do rozstrzygnięcia na makiecie).
- J_BP1 w slocie S1 (środek x = 26,5 mm), J_BP2 w slocie S2 (x = 80,0 mm), pin 1 od strony mniejszego x. J_SV1 w x = 10–43 mm, J_SV2 w x = 63,5–96,5 mm; rezystory R36–R55 przy węzłach (mogą być od spodu). Przestawienie kołków zmienia tylko `SERWIS.csv` — po zmianie ponowić `verify_s1.py`.
- Odsprzęganie U1 według `Plytki/P05-R2-review/wip-layout-obrys-R1/` (opisy „Cx przy U1.nn” w arkuszu ADC zostają); kondensatory są teraz 1206 — wzór trzeba dopasować, dozwolone od spodu pod U1. DOUT nie pod U1 po B.Cu (P5-01).
- Od spodu tylko SMD ≤ 1,5 mm, bez SOIC; C1 (11,5 mm) to najwyższy element.
- Szczegóły: `docs/MECHANIKA.md`.

## Otwarte punkty

- **MPN SW1:** C&K JS202011AQN — propozycja; dostępność w TME, złocenie styków i obciążalność (C&K JS: 0,3 A / 6 V DC przy przełączaniu; AUX_IN w zakresie HI do ok. 16 V, przełączanie tylko bez napięcia) do potwierdzenia z kartą przed zakupem. Karta C&K niedostępna w chmurze.
- **MPN rezystorów precyzyjnych:** RT1206BRB07… (okno) i RT1206BRD07… (dzielniki) — dostępność wartości 6,04k, 5,11k, 24,9k, 300k, 499k w TME i rzeczywisty dryft przy lutowaniu z karty Yageo RT.
- **Zapas z rejestru:** bilans w `docs/ZAKUPY.md`; 10 k MF0207 przekroczone już przez P09/P10/P03, P05 bierze 10 k jako nowe 1206.
- R1 KNP01U-1R: odporność na impuls ok. 6 mJ z karty.

## Pliki

- `eda/` — schemat KiCad 10 (9 arkuszy A3) i biblioteki; bez PCB.
- `output/pdf/P05-R3-schemat.pdf`, `output/previews/sch-*.png`.
- `docs/` — `J_BP.csv` i `SERWIS.csv` (kontrakty dla P12 i listew), BOM, `ZAKUPY.md`, `zakupy.csv`, `pinout.csv`, `interfejsy.csv`/`wiazki-BOM.csv` (TAPS, AUX), ODBIOR R3, MECHANIKA R3, INTEGRACJA, PROJEKT.
- `verification/` — ERC, netlista, `schematic-check.json`, `electrical-checks.json`, `s1-checks.json`, `QA.md`, logi, manifest.
- `reference/` — `P05-R2.xml` (eksport R2 do porównania), `P03-R6-J_BP.csv`, `baseline.json`, karty.
