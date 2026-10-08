# Kontrola wydania do wykonania M1 — 08.10.2026

Źródło: M1-R1-review. SHA-256 płytki: `2b39a9ef6a1859437d935b1c7fb7464b49a346cf886a65b2d6c3c769a95a4c8b` (bajtowo zgodna z wydaniem; `source-snapshot.json`, `source-unchanged.json`).

## Wyniki

- DRC KiCad 10.0.6 z `--refill-zones --schematic-parity --severity-all`: 0 naruszeń, 0 niepołączonych, 0 rozbieżności (`drc.json`, `drc-counts.json`).
- Eksport `kicad-cli` z opcjami jak dla P01 (Gerber X2 4.6 mm, `--subtract-soldermask`, `--disable-aperture-macros`, `--check-zones`; Excellon mm, PTH/NPTH osobno); hashe plików projektu identyczne przed i po (`export-receipt.json`, logi).
- Kontrola CAM własnym parserem (`src/check_cam.py`, bez KiCada): 24/24 (`cam-checks.json`). Porównanie położenia i średnicy każdego z 269 otworów, położenia i sieci każdego pola na wszystkich warstwach miedzi (4), otwarcia maski nad każdym polem, obrysu 150 × 80 mm, liczby konturów wylewek (30 F.Cu, 1 In1.Cu, 0 In2.Cu, 18 B.Cu) oraz atrybutów X2 i formatu.
- Próby ujemne kontroli CAM (`src/cam_negative_controls.py`, `cam-negative-controls.json`): 9 celowych usterek w kopiach plików (usunięte pole, otwór przesunięty o 0,1 mm i o 5 µm, zmienione wiertło, brak otwarcia maski, zmieniony obrys, zła sieć, usunięta wylewka) — wszystkie wykryte właściwą kontrolą; próba zerowa przechodzi. Sumy w kopii pokwitowania są przeliczane, więc wykrycie nie wynika z porównania bajtów.
- Oględziny podglądów z plików CAM (`visual-review.json`).
- 4 otwory leżą dokładnie na połówce mikrometra; KiCad zaokrągla je w Excellonie (rozdzielczość 0,001 mm) w drugą stronę niż kontrola, więc są parowane z tolerancją 0,001 mm i tą samą średnicą (lista w `cam-checks.json`); próba ujemna z przesunięciem 5 µm jest wykrywana.

## Interpretacja

Opis na obu stronach: od spodu oznaczenia części montowanych od spodu (C8, C9, C10, C13 pod AD7606B).
`M1-job.gbrjob` zostaje w verification (obwiednia kreski obrysu 150,05 × 80,05 mm), poza ZIP-em. Podglądy PNG nie służą do wykonania ani do przymiarki 1:1.

Przymiarka części, elektryka i termika: **NIE ZBADANO**.

## Odtworzenie

1. Python KiCada 10.0.6: `src/export_production.py` (DRC, eksport, dane płytki).
2. Python z Pillow: `src/check_cam.py`, potem `src/cam_negative_controls.py`.
3. Oględziny podglądów, `visual-review.json`; `src/write_docs.py`; `src/seal_package.py` (ZIP, suma, status, manifest).

Po dowolnej zmianie CAD potrzebny jest cały nowy odbiór.
