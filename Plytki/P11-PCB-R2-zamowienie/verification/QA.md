# Kontrola wydania do wykonania P11 — 04.10.2026

Źródło: P11-R2-review. SHA-256 płytki: `9c6bbba751ef61586f42347b7e726b2aa1a659d75cde4b59aa9da485dfde15f1` (bajtowo zgodna z wydaniem; `source-snapshot.json`, `source-unchanged.json`).

## Wyniki

- DRC KiCad 10.0.6 z `--refill-zones --schematic-parity --severity-all`: 0 naruszeń, 0 niepołączonych, 0 rozbieżności (`drc.json`, `drc-counts.json`); poza tym 1 przyjętych zgłoszeń lib_footprint_mismatch (`drc-accepted.json`, wyjaśnienie niżej).
- Eksport `kicad-cli` z opcjami jak dla P01 (Gerber X2 4.6 mm, `--subtract-soldermask`, `--disable-aperture-macros`, `--check-zones`; Excellon mm, PTH/NPTH osobno); hashe plików projektu identyczne przed i po (`export-receipt.json`, logi).
- Kontrola CAM własnym parserem (`src/check_cam.py`, bez KiCada): 20/20 (`cam-checks.json`). Porównanie położenia i średnicy każdego z 114 otworów, położenia i sieci każdego pola na obu warstwach miedzi, otwarcia maski nad każdym polem, obrysu 36 × 100 mm, liczby konturów wylewek (6 góra, 2 dół) oraz atrybutów X2 i formatu.
- Próby ujemne kontroli CAM (`src/cam_negative_controls.py`, `cam-negative-controls.json`): 8 celowych usterek w kopiach plików (usunięte pole, otwór przesunięty o 0,1 mm i o 5 µm, zmienione wiertło, brak otwarcia maski, zmieniony obrys, zła sieć, usunięta wylewka) — wszystkie wykryte właściwą kontrolą; próba zerowa przechodzi. Sumy w kopii pokwitowania są przeliczane, więc wykrycie nie wynika z porównania bajtów.
- Oględziny podglądów z plików CAM (`visual-review.json`).

## Interpretacja

Dolny opis (B.SilkS) w projekcie nie zawiera żadnego drukowanego elementu; eksport KiCada dawałby plik z samymi odejmowanymi otworami maski. Dlatego warstwy nie ma w paczce, a zamówienie obejmuje opis tylko na górze.
Przyjęte zgłoszenia `lib_footprint_mismatch` (1) dotyczą wyłącznie części, którym skrypt nadruku wydania przyciął linie lub przesunął tekst (`drc-accepted.json`); KiCad porównuje je z nieprzyciętą kopią w bibliotece. Nie wpływa to na miedź ani otwory.
`P11-job.gbrjob` zostaje w verification (obwiednia kreski obrysu 36,05 × 100,05 mm), poza ZIP-em. Podglądy PNG nie służą do wykonania ani do przymiarki 1:1.

Przymiarka części, elektryka i termika: **NIE ZBADANO**.

## Odtworzenie

1. Python KiCada 10.0.6: `src/export_production.py` (DRC, eksport, dane płytki).
2. Python z Pillow: `src/check_cam.py`, potem `src/cam_negative_controls.py`.
3. Oględziny podglądów, `visual-review.json`; `src/write_docs.py`; `src/seal_package.py` (ZIP, suma, status, manifest).

Po dowolnej zmianie CAD potrzebny jest cały nowy odbiór.
