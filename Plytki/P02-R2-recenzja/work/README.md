# P02 PSU + HOLD — rewizja R2 do recenzji Opusa

25.09.2026. R2 przygotował Codex na podstawie P02-R1-review Opusa i recenzji `reference/RECENZJA-P02-R1.md`. Oryginalny katalog R1 pozostaje bez zmian. **Status: do recenzji; przymiarka i pomiary sprzętu NIE ZBADANE.**

P02 rozdziela zasilanie EGRLab, wytwarza 5V_SYS i 3V3_IO oraz podtrzymuje elektronikę bankiem 3 × 22 mF / 35 V. Budżet: 50 ms przy poborze najwyżej 6 W z VLOG_RES, łącznie ze stratami przetwornic. VMOTOR pozostaje bez podtrzymania. HOLD_READY jest lokalnym wskaźnikiem napięcia; ręczne 15 s kwalifikuje operator. J12.3 nadal nie jest obsługiwany przez P04/CORE.

## Najważniejsze zmiany

1. Progi HOLD_READY: nowe rezystory i analiza 1024 kombinacji tolerancji dla każdego komparatora. Nominalnie bank: załączenie 10,170 V, wyłączenie 9,949 V; VPROT: 12,254 V / 11,982 V. Pełne obwiednie w `docs/HOLD-ANALIZA.md`.
2. Filtry: C14/C15 = 10 nF przed R18/R19 = 10 kΩ; dodatnie sprzężenie R8/R11 za tymi rezystorami, przy wejściu komparatora.
3. TP3: pomiar banku przez R20 = 1 kΩ / 2 W. Zwarcie TP3 przy 32 V ograniczone obliczeniowo do 33,91 mA i 1,085 W. Surowe luty banku nadal wymagają osłony.
4. Cztery czytelne arkusze A3; aktualizacja BOM, modeli gabarytowych, formularza odbioru i kontroli różnic względem R1.

**Mapa uwag, zmian i dowodów dla Opusa: `docs/ODPOWIEDZ-NA-RECENZJE.md`.**

## Wyniki kontroli plików

| Kontrola | Wynik |
|---|---|
| ERC, wszystkie ważności / arkusze | 0 / 4 |
| Netlista vs jawny kontrakt części | 208/208 pinów; 74 części; 47 sieci |
| DRC: naruszenia / niepołączone / zgodność ze schematem | 0 / 0 / 0 |
| Dodatkowe kontrole gotowej PCB | 29/29 PASS |
| Kontrole elektryczne / zgodność zakresu zmian R1→R2 | 8/8 / 4/4 PASS |
| Celowe usterki PCB / netlisty i wartości | 10/10 / 5/5 wykryte |
| Inspekcja finalnych PDF | 4 strony schematu + 5 stron PCB; SHA w `verification/visual-review.json` |

Szczegóły: `verification/QA.md`. Wyniki obliczeń i DRC nie zastępują pomiaru stabilności komparatorów, czasu podtrzymania, termiki, zwarć ani przymiarki rzeczywistych części.

## Zawartość

| Ścieżka | Zawartość |
|---|---|
| `eda/P02.kicad_pro` | Projekt KiCad 10, cztery arkusze schematu, PCB, lokalne biblioteki |
| `output/pdf/P02-R2-schemat.pdf` | Natywny schemat KiCad, 4 × A3 |
| `output/pdf/P02-R2-PCB.pdf` | Przegląd 3D, montaż i spód 1:1, F.Cu i B.Cu 1:1; belka 100 mm |
| `output/previews/`, `output/svg/` | Rendery i natywne eksporty warstw |
| `docs/BOM.csv`, `docs/parts.json` | Wartości, MPN, footprinty, połączenia i uwagi montażowe |
| `docs/ZAKUPY-P02.md` | Części i otwarte pozycje zakupowe |
| `docs/HOLD-ANALIZA.md` | Progi, tolerancje, RC, energia, TP3, źródła producentów |
| `docs/LAYOUT.md`, `docs/MECHANIKA.md` | Geometria, kotwy wiązek, montaż, serwis |
| `verification/ODBIOR.md` | Niewypełniony formularz pomiarów i przymiarki |
| `verification/` | Raporty, logi, próby ujemne i powiązanie kontroli z plikami |
| `src/`, `routing/` | Generatory, kontrole, DSN i zapisany wynik routera SES |
| `reference/` | Zamrożone dane wejściowe, recenzja R1 i manifest oryginału |
| `release-manifest.json` | SHA256 plików zawartych w archiwum |

PCB: 160 × 120 mm, FR4 1,6 mm, dwie warstwy miedzi po 70 µm. 72 części na PCB i cztery otwory M3. R17 jest poza płytką, C16 na adapterze U5. Modele 3D są obwiedniami gabarytowymi, nie dokładnymi modelami producentów.

## Odtworzenie

Uruchamiać Pythonem KiCad 10 z modułem `pcbnew`:

```text
python src/run_release.py
```

Domyślnie sprawdza istniejące CAD i odświeża eksporty. `--rebuild` regeneruje schemat i PCB z zapisanym SES; `--new-route` dodatkowo uruchamia router. Nowy routing może dać inną geometrię, wymagającą nowej inspekcji. Identyfikatory KiCada i metadane PDF mogą zmienić hash także przy tej samej geometrii.

Narzędzia: KiCad 10.0.6, Python z ReportLab/Pillow, Node z Sharp, Poppler `pdftoppm`; przy nowym routingu Freerouting 2.1.0 i Java 21. Ścieżki domyślne: `src/release_r2.py`, `src/run_layout.py`; nadpisania: `KICAD_LIBRARY_ROOT`, `EGRLAB_PDF_PYTHON`, `EGRLAB_NODE`, `EGRLAB_SHARP`, `PDFTOPPM`, `EGRLAB_FREEROUTING`.

Po inspekcji wszystkich nowych stron PDF aktualizuje się `verification/visual-review.json`, następnie uruchamia `python src/package_review.py`. Skrypt wymaga świeżego raportu DRC z hashami wejść i inspekcji dokładnie tych PDF, które pakuje.

## Pozycje otwarte

**F2/F3/F4:** wartości i obudowy są ustalone wstępnie, brakuje zatwierdzonych MPN z parametrami DC. F1: Schurter 0001.2507. Dobór pozostałych wkładek i przymiarkę trzeba domknąć przed zatwierdzeniem PCB do wykonania.

Pomiary banku, strat HOLD, komparatorów, termiki i zwarć pozostają do wykonania na sprzęcie. Pakiet nie zawiera Gerberów. P03/P04 nie zmieniono; P07 nadal czeka na ocenę rzeczywistego modułu BTS7960.
