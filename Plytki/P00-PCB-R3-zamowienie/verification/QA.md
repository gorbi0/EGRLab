# Kontrola wydania do wykonania P00 — 28.09.2026

Źródło: P00-R3-review. SHA-256 płytki: `cf39f545a7b62be48802057be33b82b9f97b4e2d6216e24155f17a824b2bf63a` (bajtowo zgodna z wydaniem; `source-snapshot.json`, `source-unchanged.json`).

## Wyniki

- DRC KiCad 10.0.6 z `--refill-zones --schematic-parity --severity-all`: 0 naruszeń, 0 niepołączonych, 0 rozbieżności (`drc.json`, `drc-counts.json`).
- Eksport `kicad-cli` z opcjami jak dla P01 (Gerber X2 4.6 mm, `--subtract-soldermask`, `--disable-aperture-macros`, `--check-zones`; Excellon mm, PTH/NPTH osobno); hashe plików projektu identyczne przed i po (`export-receipt.json`, logi).
- Kontrola CAM własnym parserem (`src/check_cam.py`, bez KiCada): 20/20 (`cam-checks.json`). Porównanie położenia i średnicy każdego z 150 otworów, położenia i sieci każdego pola na obu warstwach miedzi, otwarcia maski nad każdym polem, obrysu 115 × 70 mm, liczby konturów wylewek (1 góra, 1 dół) oraz atrybutów X2 i formatu.
- Próby ujemne kontroli CAM (`src/cam_negative_controls.py`, `cam-negative-controls.json`): 7 celowych usterek w kopiach plików (usunięte pole, przesunięty otwór, zmienione wiertło, brak otwarcia maski, zmieniony obrys, zła sieć, usunięta wylewka) — wszystkie wykryte właściwą kontrolą; próba zerowa przechodzi. Sumy w kopii pokwitowania są przeliczane, więc wykrycie nie wynika z porównania bajtów.
- Oględziny podglądów z plików CAM (`visual-review.json`).
- Porównanie z Gerberami wydania R3: wiercenia, maski, ścieżki, obrys i wylewki identyczne; położenie i sieci pól identyczne; różnica wyłącznie w zapisie 5 pól RoundRect (makro w R3, region tutaj) i w odjęciu maski od opisu (`porownanie-z-wydaniem-R3.json`).

## Interpretacja

Dolny opis (B.SilkS) w projekcie nie zawiera żadnego drukowanego elementu; eksport KiCada dawałby plik z samymi odejmowanymi otworami maski. Dlatego warstwy nie ma w paczce, a zamówienie obejmuje opis tylko na górze.
`P00-job.gbrjob` zostaje w verification (obwiednia kreski obrysu 115,05 × 70,05 mm), poza ZIP-em. Podglądy PNG nie służą do wykonania ani do przymiarki 1:1.

Przymiarka części, elektryka i termika: **NIE ZBADANO**.

## Odtworzenie

1. Python KiCada 10.0.6: `src/export_production.py` (DRC, eksport, dane płytki).
2. Python z Pillow: `src/check_cam.py`, potem `src/cam_negative_controls.py`.
3. Oględziny podglądów, `visual-review.json`; `src/write_docs.py`; `src/seal_package.py` (ZIP, suma, status, manifest).

Po dowolnej zmianie CAD potrzebny jest cały nowy odbiór.
