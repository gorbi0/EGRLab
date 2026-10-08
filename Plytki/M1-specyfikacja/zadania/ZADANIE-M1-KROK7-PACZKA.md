# Zadanie M1, krok 7 — paczka do zamówienia PCB (sesja w chmurze)

*8.10.2026. Źródło: `Plytki/M1-R1-review` na gałęzi `m1` (commit z tym plikiem). Gałąź zadania: `m1-paczka` (od `m1`), PR do `m1`.*

## Cel

Pakiet `Plytki/M1-PCB-R1-zamowienie/` gotowy do wgrania u producenta (JLCPCB), zbudowany tak samo jak `Plytki/P07-PCB-S1-zamowienie/` (ten sam łańcuch skryptów, ta sama struktura katalogów i dokumentów):

`src/copy_source.py` → `src/export_production.py` → `src/check_cam.py` → `src/cam_negative_controls.py` → oględziny (`verification/visual-review.json`) → `src/write_docs.py` → `src/seal_package.py`.

Wynik: `DO-ZAMOWIENIA_M1-PCB-R1.zip` (+ `.sha256`), `gerber/`, `podglad/`, `projekt/` (kopia źródła), `SPECYFIKACJA-DLA-PRODUCENTA.txt`, `README.md`, `verification/QA.md`, `MANIFEST.sha256.json`.

## Dane płytki (z `Plytki/M1-R1-review`, nie zmieniać)

- 150 × 80 mm, narożniki R1, 4 warstwy, stos JLC04161H-7628 (zewnętrzne 35 µm, wewnętrzne 15,2 µm), 1,6 mm, HASL bezołowiowy, maska zielona, opis biały.
- Warstwy: F.Cu / In1.Cu (ciągła masa) / In2.Cu (sygnały) / B.Cu.
- Reguły: ścieżka 0,2 mm; odstęp 0,25 mm. Wyjątek: 0,15 mm tylko w obrysie U3, LQFP-64 0,5 mm — reguły `eda/M1.kicad_dru` jak P05 R3. Przelotki 0,6 / 0,3 (moc 0,9 / 0,4).
- Od spodu 4 kondensatory 1206 (C8, C9, C10, C13 pod AD7606B) — opis dolny wg rzeczywistej zawartości B.SilkS.
- Część DNP: R25, R27 (0R) — w BOM i dokumentach jako „nie montować”.
- Kontrole wydania PCB (`verification/QA-PCB.md`): DRC 0 / 0 / 0, kontrole PCB 11/11, próby ujemne 13/13.

## Wymagania

1. Plik płytki w `projekt/` bajtowo zgodny z `Plytki/M1-R1-review/eda/M1.kicad_pcb`. `copy_source.py` to sprawdza.
2. DRC KiCad 10.0.6 na kopii: świeże wypełnienie stref, zgodność ze schematem. Wymagane 0 naruszeń, 0 niepołączonych, 0 rozbieżności. Przyjęte wyjątki (np. `lib_footprint_mismatch` po przycięciu nadruku) tylko z listą w `drc-accepted.json`.
3. Kontrola CAM własnym parserem: każdy otwór, każde pole z siecią na wszystkich 4 warstwach miedzi, otwarcia maski, obrys, liczba konturów wylewek, atrybuty X2, rozszerzenia warstw wewnętrznych z faktycznych plików (.g1 / .g2). Próby ujemne CAM wykryte w całości, próba zerowa czysta.
4. **Popraw `src/write_docs.py`:** w P07 tabela w README ma na sztywno „Warstwy | 2” i „35 µm na każdej stronie”. Specyfikacja dla producenta w P07 jest poprawna (4 warstwy), ale README nie. W M1 te wartości mają pochodzić z konfiguracji (liczba warstw, miedź zewnętrzna / wewnętrzna). Paczki P07 nie zmieniaj (jest zapieczętowana na `main`). Błąd P07 opisz w PR.
5. Oględziny: obejrzyj podglądy wygenerowane z samych plików CAM (góra, dół, zestawienie warstw) i zapisz w `visual-review.json` **tylko warstwy faktycznie obejrzane** oraz co sprawdzono: antena bez miedzi, pola X1, wylewki toru 7,5 A, otwory M3.
6. `SPECYFIKACJA-DLA-PRODUCENTA.txt`: linia JLCPCB (Layers 4, 150 x 80 mm, JLC04161H-7628, Outer 1 oz, Inner 0.5 oz, HASL lead free, bez PCBA i szablonu) oraz uwagi dla Satlandu, jak w P07.
7. README pakietu po polsku, jak P07. Status: **przymiarka 1:1 i odbiór sprzętu: NIE ZBADANO**.

## Zasady (docs/CHMURA.md)

- Bez layoutu i trasowania (zasada 6). Jeśli kontrola wykaże błąd w PCB, nie poprawiaj płytki. Zapisz stan, wypchnij i opisz błąd w PR; poprawkę zrobi sesja lokalna.
- Narzędzia z obrazu Docker (`scripts/setup-chmura.sh`, `scripts/egrlab-docker`). Bez procesów dłuższych niż ok. 15 min. Długie wyjścia do pliku, pokazuj koniec.
- Po każdym etapie commit i push na `m1-paczka`. Dwie nieudane próby czegoś = zapisz stan i opisz w PR (zasada 9).
- Nie zmieniaj plików wspólnych: `EGRLab-AKTYWNE.md`, `docs/`, `scripts/`, `Plytki/Format-S1/`, `.gitignore`, `Plytki/M1-R1-review/`, `Plytki/M1-specyfikacja/`.
- Zakończ PR-em do `m1` po polsku. Opis: wyniki kontroli, co obejrzano, pytania. Nie włączaj śledzenia PR.
