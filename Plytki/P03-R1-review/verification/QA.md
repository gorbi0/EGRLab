# Odbiór plików P03-R1 (schemat + PCB R1)

Data: 2026-09-25. Narzędzia: **KiCad 10.0.6** (Python z `pcbnew`, `kicad-cli`), Freerouting 2.1.0 (JRE 21).
Stan: **schemat i layout do recenzji; sprzęt, przymiarka 1:1 i odbiór NIE ZBADANE**.

| Kontrola | Wynik |
|---|---|
| ERC schematu (2 arkusze A3, wszystkie ważności) | **0** (`erc.json`) |
| Netlista vs lista części, pin po pinie | **347/347**, 54 części, 119 sieci, 0 błędów (`schematic-check.json`) |
| Zgodność z importem v6.1 (`v61-compare.json`) | **310 pinów, 0 różnic**; dodane tylko J8 pozycje 5–6 (CAN 2 × 3) i pola TP1–TP6 |
| Native DRC: naruszenia / niepołączone / zgodność ze schematem | **0 / 0 / 0**, świeży przebieg w `verify_pcb.py` (`drc.json`, `drc.provenance.json`) |
| Kontrole gotowej PCB (`pcb-checks.json`) | **26/26 PASS** |
| Próby ujemne (`negative-controls.json`) | **14/14 wykryte** |
| Części / format / miedź | 54 + 5 otworów M3 / 160 × 120 mm / 2 × 35 µm |

## Kontrole P03 (poza DRC i netlistą)

| Kontrola | Co sprawdza |
|---|---|
| Otwory | cztery narożne P01/P02 + H5 (155; 38); strefy bez miedzi; żaden obrys bliżej niż 4,5 mm od środka otworu (odległość od wielokąta, nie od wierzchołków) |
| Reguły | minima płytki jak P01/P02; klasy Default 0,30/0,25 i Power 0,6/0,3 przypisane do 5V_SYS, 3V3_CORE, 3V3_IO; brak wyjątków DRC |
| Zablokowana miedź | 5V_SYS 1,0 mm, odcinki odsprzęgające i przelotki GND kondensatorów zachowane (szerokość, warstwa); najwęższe ścieżki zasilania ≥ 1,0 / 0,6 / 0,6 mm |
| M1 | rzędy 22,86 mm, raster 2,54, rząd J1 od strony płytki, koniec USB-C ≤ 0,5 mm od górnej krawędzi |
| Antena | strefa = koniec anteny M1 + 3 mm po bokach + 8 mm za modułem, obie warstwy; brak ścieżek, przelotek (dokładna geometria odcinków) i wylewki w środku; żadna część w środku |
| J1 DAQ | czoło gniazda 0–0,5 mm przed prawą krawędzią, H2 i H5 po obu stronach ≤ 25 mm od środka, pozycja 2 NC |
| IDC J2–J8, Mini-Fit J9 | przy krawędzi (≤ 0,5 mm), dłuższy bok wzdłuż niej, rząd sygnałowy do środka, pin klucza NC (klucze v6.1) |
| SD1 | koniec karty przy krawędzi, strefy Ø6 mm pod dystanse M2.5 w miejscu otworów |
| J10 LV03 | pinout 5V/GND/3V3_IO/GND, kotwa 12,5 mm od lutów w stronę krawędzi, pas bez miedzi pod opaską, pole TP pod każdym padem z tą samą siecią |
| Odsprzęganie | 10 × 100 nF ≤ 8 mm w linii prostej i ≤ 20 mm po miedzi do pinu zasilania (wynik ≤ 4,9 / ≤ 5,3 mm) |
| Domeny | VCC wszystkich 74LVC125 na 3V3_CORE; 3V3_IO tylko J10.3, TP3 i nieużywane OE# U14 |
| GND | wylewki na obu warstwach, usuwanie wysp bez połączenia, największa wyspa ≥ 75 % wylewki (88 / 81 %), ≥ 40 przelotek zszywających (48) |
| Nadruk | oznaczenia poza cudzymi obrysami i najbliżej własnej części; opisy poza obrysami (wyjątek: obrysy modułów M1/SD1); nazwy złączy przy właściwym złączu; KEY n w linii z pozycją klucza ≤ 1,5 mm, ≤ 3 mm od obudowy; opisy USB-C, antena, microSD |

## Próby ujemne

Kopie płytki w `negative-controls/<nazwa>/` (poza archiwum): `m1_rotated`, `j1_inward`, `hole_shift`, `ref_inside_other`, `decap_far`, `key_swap`, `name_swap`, `thin_supply`, `antenna_track`, `sd_off_edge`, `idc_rotated`, `tp_swap` (TP3 i TP4 zamienione — pod padem 3 LV03 byłby opis GND), `pour_split` (ścieżka przecinająca wylewkę B.Cu), `dangling_lock` (zablokowany odcinek 5V kończący się obok padu). Wszystkie wykryte przez właściwą kontrolę.

## Przebieg

Z katalogu pakietu, Pythonem z KiCada: `python src/run_release.py` (importuje zapisany `routing/P03.ses`; `--new-route` puszcza Freerouting od nowa).

1. `build_schematic.py` → ERC → netlista → `verify_schematic.py` → `compare_v61.py` → PDF schematu.
2. `run_layout.py --reuse-ses`: `build_board.py`, `set_rules.py`, `set_stackup.py`, `route_critical.py` (5V_SYS, odcinki odsprzęgające, przelotki GND kondensatorów; eksport DSN), `prepare_routing.py` (GND poza listą routera), import `routing/P03.ses`, `set_rules.py`, `cleanup.py` (z ponowieniem trasowania, gdy pad GND zostaje odcięty), `stitch.py` (zszycie wylewek), pętla padów z zagłodzoną termiką, DRC.
3. `silkscreen.py`, `set_rules.py`.
4. `verify_pcb.py`, `negative_controls.py`.
5. Rendery 3D, `make_pdf.py`, manifest i archiwum.

Po każdej zmianie miedzi, pada, footprintu albo reguły wynik trzeba uzyskać ponownie.
