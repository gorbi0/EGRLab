# P02 PSU + HOLD — rewizja R3 (zamykająca)

26.09.2026. R3 przygotował Claude na podstawie R2 Astry i własnej recenzji `Plytki/P02-R2-recenzja/RECENZJA-P02-R2.md`. Zgodnie z decyzją użytkownika jest to ostatnia iteracja projektu P02. Pakiety R1 i R2 pozostają bez zmian. **Status: projekt zamknięty; przymiarka 1:1, zakup i odbiór sprzętu NIE ZBADANE; Gerbery powstaną po przymiarce.**

P02 rozdziela zasilanie EGRLab, wytwarza 5V_SYS i 3V3_IO oraz podtrzymuje elektronikę bankiem 3 × 22 mF / 35 V. Budżet: 50 ms przy poborze najwyżej 6 W z VLOG_RES, łącznie ze stratami przetwornic. VMOTOR pozostaje bez podtrzymania. HOLD_READY jest lokalnym wskaźnikiem napięciowym. 15 s kwalifikuje operator, a przy zgaszonym silniku — pomiar TP1/TP3. J12.3 nadal nie jest obsługiwany przez P04/CORE.

## Co zmienia R3 (miedź i rozmieszczenie jak w R2)

1. Wkładki Schurter SPT 5 × 20, 300 VDC: F1 T2A (bez zmian), **F2/F3 T1A** (zwłoczne, zgodnie z zaleceniem TRACO dla TSR2), **F4 T0,5A**. Otwarta pozycja F2/F3/F4 z R2 jest zamknięta.
2. `--rebuild` odtwarza płytkę: pakiet zawiera SES, a zagłodzone termiki są rozpoznawane po UUID, niezależnie od języka KiCada.
3. R16 470 Ω: LED kwalifikacji ok. 2–3 mA zamiast 1,1 mA.
4. Dokumentacja: praca przy zgaszonym silniku, opóźnione (1–2 min) wykrycie przerwanego F1, czytelniejszy arkusz 1 schematu, czarna belka 100 mm, poprawione spacje w MECHANIKA/ZAKUPY.

Mapa zmian: `docs/ZMIANY-R3.md`. Historia R2: `docs/ODPOWIEDZ-NA-RECENZJE.md`.

## Wyniki kontroli plików

Pełne wyniki: `verification/QA.md`. Obliczenia i DRC nie zastępują pomiaru stabilności komparatorów, czasu podtrzymania, termiki, zwarć ani przymiarki rzeczywistych części.

## Zawartość

| Ścieżka | Zawartość |
|---|---|
| `eda/P02.kicad_pro` | Projekt KiCad 10, cztery arkusze schematu, PCB, lokalne biblioteki |
| `output/pdf/P02-R3-schemat.pdf` | Natywny schemat KiCad, 4 × A3 |
| `output/pdf/P02-R3-PCB.pdf` | Przegląd 3D, montaż i spód 1:1, F.Cu i B.Cu 1:1; belka 100 mm |
| `output/previews/`, `output/svg/` | Rendery i natywne eksporty warstw |
| `docs/BOM.csv`, `docs/parts.json` | Wartości, MPN, footprinty, połączenia i uwagi montażowe |
| `docs/ZAKUPY-P02.md` | Części, bezpieczniki R3 i otwarte pozycje zakupowe |
| `docs/HOLD-ANALIZA.md` | Progi, tolerancje, RC, energia, TP3, zgaszony silnik, F1, LED |
| `docs/LAYOUT.md`, `docs/MECHANIKA.md` | Geometria, kotwy wiązek, montaż, serwis |
| `docs/ZMIANY-R3.md` | Zmiany R3 i ich uzasadnienie |
| `verification/ODBIOR.md` | Niewypełniony formularz pomiarów i przymiarki |
| `verification/` | Raporty, logi, próby ujemne, kontrola zakresu R2 → R3 |
| `src/`, `routing/` | Generatory, kontrole, DSN i zapisany wynik routera (SES) |
| `reference/` | Zamrożone dane wejściowe, recenzja R1, płytki i części R1 oraz R2 |
| `release-manifest.json` | SHA256 plików zawartych w archiwum |

PCB: 160 × 120 mm, FR4 1,6 mm, dwie warstwy miedzi po 70 µm. 72 części na PCB i cztery otwory M3. R17 jest poza płytką, C16 na adapterze U5.

## Odtworzenie

Uruchamiać Pythonem KiCad 10 z modułem `pcbnew`:

```text
python src/run_release.py --rebuild
```

Bez `--rebuild` skrypt sprawdza istniejące CAD i odświeża eksporty. `--rebuild` regeneruje schemat i PCB z zapisanym `routing/P02.ses`. `--new-route` uruchamia router od nowa — to nowa geometria, wymagająca nowej recenzji. Narzędzia: KiCad 10.0.6, Python z ReportLab/Pillow, Node z Sharp, Poppler `pdftoppm`; przy nowym routingu Freerouting 2.1.0 i Java 21. Nadpisania ścieżek: `KICAD_LIBRARY_ROOT`, `EGRLAB_PDF_PYTHON`, `EGRLAB_NODE`, `EGRLAB_SHARP`, `PDFTOPPM`, `EGRLAB_FREEROUTING`.

Po inspekcji wszystkich nowych stron PDF aktualizuje się `verification/visual-review.json`, a następnie uruchamia `python src/package_review.py`.

## Pozycje otwarte

Przymiarka 1:1 (złącza, oprawki, adapter, bank i jego obejmy), zakup (dostępność 0001.2501 i Mini-Fit w `ZAKUPY-P02.md`), potwierdzenie I²t F1:F2 z karty PDF Schurtera, pomiary według `ODBIOR.md`. P03/P04 bez zmian; P07 nadal czeka na ocenę rzeczywistego modułu BTS7960.
