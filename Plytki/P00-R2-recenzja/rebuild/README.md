# P00-R2 - przyrząd stanowiskowy do recenzji

25.09.2026. Rewizja po recenzji P00-R1. Zachowany format 115 x 70 mm i rozmieszczenie kanałów. **Pliki do recenzji; przymiarka i odbiór sprzętu niewykonane.**

P00 daje osiem przełączanych poziomów H/L przez 1 kΩ i heartbeat około 102 Hz. Służy do odbioru pojedynczych modułów, przede wszystkim P04; nie jest częścią zestawu w samochodzie.

## Zmiany R2

- Zasilanie J10 **6-15 V**, zalecane 9-12 V; właściwa karta LM2937-3.3 SNVS015F.
- R5 **560 Ω / 1% / 0,25 W** stale obciąża 3V3 i zapewnia ponad 5 mA także bez TLC555.
- C6 **EEUFR1H220, 22 µF / 50 V, D5, raster 2 mm**. R6 **1 Ω / 1% / 0,25 W** w powrocie C6 zapewnia dolną granicę rezystancji jego gałęzi; nie ogranicza prądu DC zasilania.
- Poprawione etykiety schematu, tytuł, numery katalogowe rezystorów i odnośniki LED.
- Generator używa lokalnych wejściowych footprintów. Nie wymaga katalogu P02.
- Dodane obliczenia warunków pracy, testy regresji tych warunków, mapa wiązki P04 i formularz odbioru.

## Co otworzyć

| Plik | Przeznaczenie |
|---|---|
| `eda/P00.kicad_pro` | Projekt KiCad 10, schemat i PCB |
| `output/pdf/P00-R2-schemat.pdf` | Schemat A3 |
| `output/pdf/P00-R2-PCB.pdf` | Przegląd, montaż i obie warstwy miedzi 1:1 |
| `docs/ZAKUPY-P00.md`, `docs/BOM.csv` | Zestawienie zakupowe i BOM według oznaczeń |
| `docs/ODBIOR-P00-R2.md` | Kolejne kroki uruchomienia, pomiary do wpisania |
| `docs/P00-P04-WIAZKA.md` | Mapowanie wejść P04 v6.1 i tryby testu |
| `docs/ZAMKNIECIE-RECENZJI.md` | Odpowiedź na każdą uwagę R1 |
| `verification/QA.md` | Zakres kontroli i ograniczenia |
| `verification/clean-rebuild.json` | Wynik osobnej regeneracji z czystego katalogu |
| `output/fabrication/` | Gerbery i osobne wiercenia PTH/NPTH, do kontroli przed zamówieniem |

Odtwarzanie: `python src/run_release.py` Pythonem KiCad z `pcbnew`, Pillow i numpy. Wymagania narzędzi opisano w `docs/ODTWARZANIE.md`. Domyślnie używany jest zapisany SES; nowy przebieg routera jest opcjonalny. SHA-256 plików wydania znajduje się w `release-manifest.json`.

Oryginał P00-R1 i jego recenzja pozostają oddzielnymi, niezmienionymi pakietami. P07 pozostaje poza zakresem tej rewizji.
