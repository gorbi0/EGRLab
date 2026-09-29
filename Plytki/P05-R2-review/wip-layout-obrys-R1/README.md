# P05 R2 — niedokończony layout w obrysie R1 (tylko wzór)

**Niedokończone. Obrys R1 (160 × 120 mm) jest nieaktualny** — płytki przechodzą na format S1 (`Plytki/Format-S1/`). Ten katalog nie jest wydaniem ani częścią łańcucha kontroli R2; skrypty mają ścieżki względne do pakietu i nie uruchomią się stąd bez przeniesienia. Zachowany wyłącznie jako **wzór rozmieszczenia odsprzęgania przy U1 (AD7606B)** dla layoutu w S1 (uwaga P5-01 recenzji).

## Wzór przy U1 (P5-01)

- Kolumna A (0603/0805) zaczyna się 1,0 mm za końcami padów U1 (x 114,45 → 115,45); kolejność kondensatorów = kolejność pinów, bez krzyżowania: C11 (pin 42), C10 (39), C5 (37/38), C9 (36).
- C7 (AVCC 48) w wolnym prawym górnym rogu poza obrysem U1 (obrys U1 ma ścięte narożniki), zasilany z góry przez C6.
- Kolumna B (1210): C13 (REFCAP 44/45) nad kolumną A, zasilany ukośnym torem 0,4 mm między C7 i C11; C12 (REFIN/REFOUT 42) prostym torem 0,4 mm pod C11.
- AVCC 37/38 nie mają wolnego boku (kolumna A trzyma ich kondensator), więc zasila je „kręgosłup” 0,5 mm pod korpusem: pin 1 → 37/38, pod rzędem przelotek mas wejść (y 40) i wewnątrz przelotek mas prawego boku. Pin 2 (AGND) wychodzi wtedy na zewnątrz do własnej przelotki.
- Własne przelotki: każdy pad GND kondensatora oraz REFGND 43/46 i AGND 40/41/47 (do wewnątrz).
- Przewężenie 0,25–0,3 mm tylko w rzędzie padów (x ≤ 114,6), dalej ≥ 0,4 mm.
- TP13 przy C12, TP14 pod C9, TP15 przy C10 (odgałęzienie 0,2 mm między C10 i C5), TP16 przy C13.
- Strefa `ANALOG_GND_PLANE_*` obejmuje cały obrys U1 (x ≥ 101 mm, nowa `OUTLINE` pod dolnym rzędem); DOUT wychodzi przelotką spod pinu 24 i biegnie po B.Cu poza obrysem.

Geometria była bardzo ciasna: C12 5,98 mm przy limicie 6 mm, C9 2,91 mm przy 3 mm, niektóre obrysy stykają się z luzem 5–30 µm, a przelotka GND C10 zachodzi 0,05 mm na własny pad. W S1 warto zostawić więcej miejsca po prawej stronie U1.

## Drogi po miedzi pin → kondensator (`src/decoupling.py`)

| Pin U1 | Kondensator | R1 [mm] | wzór R2 [mm] | limit [mm] |
|---|---|---:|---:|---:|
| 1 AVCC | C4 | 2,35 | 2,35 | 3 |
| 48 AVCC | C7 | 7,51 | 2,68 | 3 |
| 37 / 38 AVCC | C5 | 11,31 / 11,81 | 2,23 / 2,73 | 3 |
| 36 REGCAP | C9 | 9,34 | 2,91 | 3 |
| 39 REGCAP | C10 | 14,31 | 2,55 | 3 |
| 42 REFIN/OUT | C11 | 14,48 | 2,64 | 3 |
| 42 REFIN/OUT | C12 | 21,20 | 5,98 | 6 |
| 44 / 45 REFCAP | C13 | 12,19 / 11,69 | 4,69 / 4,69 | 6 |
| 23 VDRIVE | C8 | 3,55 | 3,55 | (bez zmian) |

Pomiar R2 na `routing/seeded.kicad_pcb` (miedź krytyczna R2 + zasiana miedź R1 + wylewki GND). DRC samej miedzi krytycznej przy U1: 0 naruszeń miedzi. Zrzuty przed/po: `zrzuty/U1-R1-*.png`, `zrzuty/U1-R2-wip-*.png`.

## Stan łańcucha (przerwany)

`src/route_critical.py` (R2) → `src/seed_r1.py` (miedź R1 poza obszarem zmiany, kolizje usuwane według DRC) → `src/complete_r2.py` (planer rastrowy dla przerwanych połączeń, zapis do powtórzenia). Uzupełnianie zatrzymano w trakcie: `routing/completion-routes-r2.json` jest częściowy, `P05-wip.kicad_pcb` ma naruszenia DRC (m.in. zwarcie 5VA/ADC_CH8 z wcześniejszego przebiegu planera). `verify_pcb.py` nie ma jeszcze limitów per pin ani próby „C13 + 5 mm”. Pozostałe skrypty to kopie łańcucha R1 potrzebne temu przebiegowi.
