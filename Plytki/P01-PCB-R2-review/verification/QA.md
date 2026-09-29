# Odbiór plików P01-PCB-R2

Data: 2026-09-24. Narzędzie końcowego odbioru: **KiCad 10.0.6**.
Stan: **layout do recenzji; sprzęt i przymiarka NIE ZBADANE**.

| Kontrola | Wynik |
|---|---|
| Native DRC: naruszenia / niepołączone / zgodność schematu | **0 / 0 / 0** |
| Kontrole gotowej PCB i geometrii (`pcb-checks.json`) | **24/24 PASS** (17 z R1 + 7 dla uwag PCB1-01…06) |
| Próbne usterki w kopiach (`negative-controls.json`) | **6/6 wykryte** |
| Schematu R3 nie zmieniono | 3 pliki zgodne SHA256 z manifestem R3 |
| Komponenty | 89 elektrycznych + HS1/HS2 + 4 mocowania = 95 footprintów |
| Fizyczne pady elektryczne | 195; zawierają dwa dodatkowe odczepy Kelvin LK1 |
| Format / warstwy / miedź | 160×120 mm / 2 / 70 µm na stronę |
| Referencyjne ścieżki i przelotki mocy/pomiaru | wszystkie 61 zachowane (szyna VS podzielona na odcinki) |
| TP1 SOURCE / TP2 GATE | 4,71 / 4,85 mm ścieżki do Q1 |
| Kotwy wiązek J5/J7 | 12,5 mm od rzędu lutów |
| Miedź F.Cu pod profilami HS1/HS2 | brak: ścieżek, przelotek, padów sieciowych i wypełnionej wylewki |
| Wypełnione wylewki zapisane w pliku | aktualne: ponowne wypełnienie daje te same obszary |
| PDF | 4 strony obejrzane jako obrazy; montaż i miedź 1:1 z belką 100 mm |

`pcb-checks.json` wiąże wynik z SHA256 gotowej PCB. `release-manifest.json` wiąże pliki
pakietu. **Po każdej zmianie miedzi, pada, footprintu albo reguły wynik trzeba uzyskać
ponownie**; nie wystarczy zachować starego raportu.

## Kontrole R2 (nowe)

| Kontrola | Co sprawdza |
|---|---|
| R2/PCB1-01 (2) | brak miedzi F.Cu w obrysie metalu HS1/HS2 (ścieżki, przelotki, pady z siecią, wypełniona wylewka jako przecięcie wielokątów); obszary reguł pokrywają oba obrysy, wnęka otwarta |
| R2/PCB1-02 | gruba (≥ 0,35 mm) linia nadruku po stronie taba Q1, Q2, D2; napis `TAB` ≤ 4 mm od linii Q2 |
| R2/PCB1-03 | długość po trasowaniu: OV_REF ≤ 20, OV_SENSE/UV_SENSE ≤ 40, REF ≤ 70 mm; ≥ 5 mm od ścieżek mocy na obu warstwach |
| R2/PCB1-03,05,06 | sąsiedztwo funkcjonalne (pad–pad): C6–Q1, D9–Q2, R21–Q3, R7/R8–U2.3, bufor wokół Q6, R11–U2.5, R13–U4.1, **C10–U2.8 i C11–U4.2 ≤ 8 mm** |
| R2/PCB1-04 | J5: kotwa poniżej rzędu padów, ≤ 8 mm od dolnej krawędzi, brak courtyardów w pasie wiązki |
| R2/PCB1-06 | napisy sieci przy J1, J2, J4, J8 (obrys tekstu ≤ 3 mm od środka pada) |

## Próby ujemne

1. `probe_open`: zmiana szerokości odcinka do TP2 — wykryta przez kontrolę zachowania tras krytycznych.
2. `mount_shift`: przesunięcie H3 — wykryte przez zapisane współrzędne otworów.
3. `lk1_bypass`: ścieżka zwierająca LK1 — wykryta przez natywny DRC jako `shorting_items`.
4. `hs_copper`: ścieżka F.Cu pod żebrami HS1 — wykryta przez R2/PCB1-01.
5. `q2_tab_marker`: pogrubiona linia taba Q2 zwężona do 0,15 mm — wykryta przez R2/PCB1-02.
6. `ovref_near_rail`: koniec odcinka OV_REF przeciągnięty pod szynę VS — wykryty przez R2/PCB1-03.

Pliki w `negative-controls/` są wynikami prób błędów, nie wersjami do produkcji.
Skrypt tworzy robocze kopie i nie zmienia `eda/P01.kicad_pcb`.

## Przebieg R2 (kolejność faktycznie wykonana)

Z katalogu pakietu, Pythonem z KiCada (moduł `pcbnew`):

1. `src/r2_to220_silk.py` — nadruk TO-220 w lokalnej bibliotece (idempotentny).
2. `src/r2_build_board.py` — płytka z netlisty R3 i `src/placement_r2.json`, obszary reguł HS.
3. `src/set_stackup.py`
4. `src/r2_route_critical.py` — trasy mocy, bramki, Kelvin i sond (zablokowane); eksport DSN.
5. `kicad-cli pcb drc … -o routing/critical-drc.json eda/P01.kicad_pcb`
6. `src/prepare_routing.py` — klasa GND w DSN, kopia `routing/prerouted.kicad_pcb`.
7. Freerouting 2.1.0 w `routing/`: `java -jar freerouting-2.1.0.jar -de P01.dsn -do P01.ses -mp 100 -da --gui.enabled=false` (log: `routing/freerouting-stdout.log`; 999 przebiegów, 1 połączenie domknięte później wylewką).
8. `src/import_routing.py` — import SES, wylewki GND.
9. `src/set_rules.py` — **zaraz po imporcie**, bo import nadpisuje `P01.kicad_pro` regułami domyślnymi.
10. DRC → `routing/postroute-drc.json`
11. `src/r2_cleanup.py` — usuwa łańcuchy VS dublujące zablokowaną miedź (tu: 2 odcinki przy C6.2); DRC → `routing/postclean-drc.json`
12. `src/finish_silkscreen.py`, `src/r2_legends.py`, `src/r2_refs.py`, `src/r2_legends.py` (drugi raz: napisy omijają przestawione oznaczenia)
13. `src/set_rules.py`
14. Końcowy DRC → `routing/postsilk-drc.json` = `verification/drc.json`
15. `src/verify_pcb.py`, `src/negative_controls.py`
16. `kicad-cli pcb render --side top|bottom --width 2400 --height 1800 --quality basic -o output/previews/render-<strona>.png eda/P01.kicad_pcb`
17. `src/r2_make_pdf.py`

Powtórzenie samego odbioru:

```powershell
kicad-cli pcb drc --format json --severity-all --schematic-parity --all-track-errors --refill-zones -o verification/drc.json eda/P01.kicad_pcb
# Python dołączony do KiCada, z modułem pcbnew:
python src/verify_pcb.py
python src/negative_controls.py
```

Odbiór w tym wydaniu robiono bez `--save-board`: plik PCB nie był zapisywany przez DRC.
Wylewki w pliku są aktualne (sprawdzone ponownym wypełnieniem w pamięci).

## Reguły

Wymagany odstęp sieci 0,30 mm (minimum globalne 0,25), minimum ścieżki 0,30, via Ø0,8,
annulus 0,20, Cu–krawędź 0,50, otwór–otwór 0,30 i nadruk 0,15 mm. Tablica wyłączeń jest
pusta; nie wyłączano naruszeń, aby otrzymać PASS.

## Znane zachowania narzędzi

- Import SES przez API KiCad 10 zwraca False bez diagnostyki; `import_routing.py` czyta
  ściśle kontrolowany podzbiór SES (jak w R1). W R2 dodał 345 odcinków i 0 przelotek.
- Nowa ścieżka dodana skryptem do wczytanej płytki potrafi zapisać się z siecią GND;
  próby ujemne przestawiają istniejące odcinki zamiast dodawać nowe.
- `Remove()` na elementach graficznych płytki wywraca pcbnew; `r2_legends.py` usuwa własne
  napisy na poziomie pliku przed wczytaniem płytki.

## Pozostałe otwarte warunki

Przymiarka radiatorów, C6 we wnęce, dostęp do TP1/TP2, izolacja, złącza, przewody i obudowa;
kwalifikacja lutów PTH mocy; pomiary termiczne i SOA Q1; dynamika pełnego układu;
metrologia VGS/prądu; odporność na impulsy; integracja z P02-HOLD. Żadnego nie oznaczono PASS.
Gerber/Excellon są następnym eksportem po przymiarce i recenzji R2. P07 pozostaje HOLD.
