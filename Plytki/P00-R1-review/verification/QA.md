# Odbiór plików P00-R1 (schemat + PCB R1)

Data: 2026-09-25. Narzędzia: **KiCad 10.0.6** (Python z `pcbnew`, `kicad-cli`), Freerouting 2.1.0 (JRE 21).
Stan: **schemat i layout do recenzji; sprzęt, przymiarka 1:1 i odbiór NIE ZBADANE**.

| Kontrola | Wynik |
|---|---|
| ERC schematu (1 arkusz A3, wszystkie ważności) | **0** (`erc.json`) |
| Netlista vs lista części, pin po pinie | **141/141**, 64 części, 36 sieci, 0 błędów (`schematic-check.json`) |
| Native DRC: naruszenia / niepołączone / zgodność ze schematem | **0 / 0 / 0**, świeży przebieg w `verify_pcb.py` (`drc.json`, `drc.provenance.json`) |
| Kontrole gotowej PCB (`pcb-checks.json`) | **22/22 PASS** |
| Próby ujemne (`negative-controls.json`) | **8/8 wykryte** |
| Części / format / miedź | 64 + 4 otwory M3 / 115 × 70 mm / 2 × 35 µm |

## Kontrole P00 (poza DRC i netlistą)

| Kontrola | Co sprawdza |
|---|---|
| Przełączniki | we wszystkich 9: pin 1 (środkowy) = COM, pin 2 = 3V3, pin 3 = GND, pin 3 nad pinem 2 — przy „opposite side connection” suwak w górę = H/RUN, jak na nadruku |
| Wyjścia | pin sygnałowy każdej listwy osiągalny tylko przez swój 1 kΩ (sieć OUTn = RSn.2 + Jn.1; HEART = R3.2 + J9.1) |
| Listwy | lewy pin = GND, prawy = sygnał (jak na nadruku), jeden rząd |
| LED | katody na GND; LED kanału zasilana z węzła przełącznika, HB z wyjścia 555, zasilania z 3V3 |
| Zasilanie | J10.1 → anoda D1, katoda → wejście LM2937; LM2937 GND/OUT |
| Kondensatory | LM2937 wejście/wyjście ≤ 10 mm od pinu, TLC555 VCC/CTRL ≤ 8 mm |
| Złącze J10 | przy lewej krawędzi, wejście przewodu do krawędzi |
| Zablokowana miedź | każdy odcinek i przelotka sprzed autoroutera zachowane (szerokość, warstwa) |
| Nadruk | oznaczenia poza cudzymi obrysami i najbliżej własnej części; opisy poza obrysami; numery kanałów przy właściwych LED; opisy działania obecne |

## Próby ujemne

Kopie płytki w `negative-controls/<nazwa>/` (poza archiwum): `sw_rotated` (SW3 obrócony — suwak w górę dawałby L), `header_flipped` (J4 obrócona — GND z prawej), `mount_shift` (H3 przesunięty), `ref_inside_other` (oznaczenie R4 w obrysie U1), `decap_far` (C3 odsunięty), `label_swap` (zamienione numery 3/4), `thin_supply` (zwężony odcinek zasilania), `dangling_lock` (zablokowana ścieżka kończąca się obok padu J9 — błąd, który zrobiłem w R1 przed poprawką i który wyłapał świeży DRC). Wszystkie wykryte przez właściwą kontrolę.

## Przebieg

Z katalogu pakietu, Pythonem z KiCada: `python src/run_release.py` (importuje zapisany `routing/P00.ses`; `--new-route` puszcza Freerouting od nowa).

1. `build_schematic.py` → ERC → netlista → `verify_schematic.py` → PDF schematu.
2. `run_layout.py --reuse-ses`: `build_board.py`, `set_stackup.py`, `route_critical.py` (zasilanie, szyna 3V3 i kolumny kanałów zablokowane; eksport DSN), `prepare_routing.py` (GND poza listą routera), import `routing/P00.ses`, `set_rules.py`, `cleanup.py`, DRC.
3. `silkscreen.py`, `set_rules.py`.
4. `verify_pcb.py`, `negative_controls.py`.
5. Rendery 3D, `make_pdf.py`, manifest i archiwum.

Po każdej zmianie miedzi, pada, footprintu albo reguły wynik trzeba uzyskać ponownie.
