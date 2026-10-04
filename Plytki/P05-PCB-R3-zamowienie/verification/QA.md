# Kontrola wydania do wykonania P05 — 04.10.2026

Źródło: P05-R3-review. SHA-256 płytki: `d7ffbbfba8a86cc1ea40e3d436fecf325754e56af5fa9b69ff4f108dd512e05e` (bajtowo zgodna z wydaniem; `source-snapshot.json`, `source-unchanged.json`).

## Wyniki

- DRC KiCad 10.0.6 z `--refill-zones --schematic-parity --severity-all`: 0 naruszeń, 0 niepołączonych, 0 rozbieżności (`drc.json`, `drc-counts.json`); poza tym 4 przyjętych zgłoszeń lib_footprint_mismatch (`drc-accepted.json`, wyjaśnienie niżej).
- Eksport `kicad-cli` z opcjami jak dla P01 (Gerber X2 4.6 mm, `--subtract-soldermask`, `--disable-aperture-macros`, `--check-zones`; Excellon mm, PTH/NPTH osobno); hashe plików projektu identyczne przed i po (`export-receipt.json`, logi).
- Kontrola CAM własnym parserem (`src/check_cam.py`, bez KiCada): 20/20 (`cam-checks.json`). Porównanie położenia i średnicy każdego z 374 otworów, położenia i sieci każdego pola na obu warstwach miedzi, otwarcia maski nad każdym polem, obrysu 106,5 × 100 mm, liczby konturów wylewek (32 góra, 28 dół) oraz atrybutów X2 i formatu.
- Próby ujemne kontroli CAM (`src/cam_negative_controls.py`, `cam-negative-controls.json`): 8 celowych usterek w kopiach plików (usunięte pole, otwór przesunięty o 0,1 mm i o 5 µm, zmienione wiertło, brak otwarcia maski, zmieniony obrys, zła sieć, usunięta wylewka) — wszystkie wykryte właściwą kontrolą; próba zerowa przechodzi. Sumy w kopii pokwitowania są przeliczane, więc wykrycie nie wynika z porównania bajtów.
- Oględziny podglądów z plików CAM (`visual-review.json`).
- 11 otworów leży dokładnie na połówce mikrometra; KiCad zaokrągla je w Excellonie (rozdzielczość 0,001 mm) w drugą stronę niż kontrola, więc są parowane z tolerancją 0,001 mm i tą samą średnicą (lista w `cam-checks.json`); próba ujemna z przesunięciem 5 µm jest wykrywana.

## Interpretacja

Opis na obu stronach: od spodu oznaczenia części montowanych od spodu (C11, C25, C26, C5, C7, C8, R21, R36, R37, R38, R39, R40, R41, R42, R44, R45, R46, R47, R48, R49, R50, R51, R52, R53, R54, R55, R9).
Przyjęte zgłoszenia `lib_footprint_mismatch` (4) dotyczą wyłącznie części, którym skrypt nadruku wydania przyciął linie lub przesunął tekst (`drc-accepted.json`); KiCad porównuje je z nieprzyciętą kopią w bibliotece. Nie wpływa to na miedź ani otwory.
`P05-job.gbrjob` zostaje w verification (obwiednia kreski obrysu 106,55 × 100,05 mm), poza ZIP-em. Podglądy PNG nie służą do wykonania ani do przymiarki 1:1.

Przymiarka części, elektryka i termika: **NIE ZBADANO**.

## Odtworzenie

1. Python KiCada 10.0.6: `src/export_production.py` (DRC, eksport, dane płytki).
2. Python z Pillow: `src/check_cam.py`, potem `src/cam_negative_controls.py`.
3. Oględziny podglądów, `visual-review.json`; `src/write_docs.py`; `src/seal_package.py` (ZIP, suma, status, manifest).

Po dowolnej zmianie CAD potrzebny jest cały nowy odbiór.
