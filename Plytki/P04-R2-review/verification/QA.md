# P04-R2 — kontrola wydania

26.09.2026 · Claude. Status: DO NIEZALEŻNEJ RECENZJI; przymiarka i sprzęt NIE ZBADANO. Zmiany względem R1: `docs/ZMIANY-R2.md`.

| Sprawdzenie | Wynik |
|---|---|
| Native ERC, sześć arkuszy | 0 naruszeń |
| Eksport XML vs specyfikacja generatora | 98 komponentów, 355 przypisań pinów, 92 sieci, 0 różnic |
| Native DRC, wszystkie poziomy + pełne błędy ścieżek + parity | 0 naruszeń / 0 brakujących połączeń / 0 różnic schematu |
| Kontrole PCB, łącznie z native DRC | 26/26 PASS (R1: 20) |
| Kontrole elektryczne z niezależnie odczytanej netlisty | 22/22 PASS (R1: 19), w tym pojedyncze uszkodzenie: rozwarty Q1 |
| Tablice prawdy | 131 072 kombinacji, sześć obserwowanych wyjść; liczba stanów H zapisana w JSON |
| Sekwencje ARM/reset/powrót sygnałów | PASS w modelu idealnej logiki; brak fizycznego pomiaru |
| Celowe mutacje połączeń | 14/14 wykrytych przez wskazaną kontrolę |
| Celowe mutacje PCB | 11/11 wykrytych; błąd wykonania skryptu nie liczy się jako wykrycie |
| Zakres interfejsów | Wszystkie piny zachowane; jedyne zmiany sieci: J7.1 → PG_3V3 i J8.1 → PANEL_3V3 (udokumentowane, R4-03); SENSOR +2 NC i jawne pady kluczy jak w R1 |
| Baza v6.1-rc1 | Pliki bazy i ich kopie w `reference/` zgodne z hashami (`baseline-unchanged.json`, sprawdzone ponownie w R2) |
| Odtworzenie z czystych źródeł | Identyczna geometria semantyczna PCB; szczegóły w `clean-rebuild.json` |
| PDF | 6 stron A3 schematu + 4 strony A4 PCB, rasteryzacja obejrzana w całości; hash w `visual-qa.json` |

Raport native DRC uruchamia się od nowa, usuwa poprzedni wynik i zapisuje w `drc.provenance.json` hash wszystkich wejść oraz wynikowego raportu. Nie ma wyłączeń DRC. Plik manifestu wydania wiąże wszystkie dostarczone pliki; ZIP sprawdzony bajt po bajcie.

Biblioteka pcbnew zapisując PCB może zresetować reguły projektu. Dlatego kolejność końcowa jest obowiązkowa: `silkscreen.py` → `set_rules.py` → `verify_pcb.py`. Sam zielony raport sporządzony przed przywróceniem reguł nie kwalifikuje projektu.

## Odtworzenie

Narzędzia: KiCad 10.0.6 z Pythonem pcbnew, jego biblioteki symboli/footprintów, Python z ReportLab/Pillow oraz Poppler. Freerouting nie jest potrzebny do odtworzenia zatwierdzonej geometrii: pakiet ma SES (`routing/P04.ses`) i jawne ścieżki uzupełniające (`routing/completion-routes.json`). Czyszczenie, pełne połączenia padów i zszycie GND wynikają z nich deterministycznie. Pliki `input/footprints` są zahashowane. Nie trzeba mieć katalogów P00/P02 ani kopii całego EGRLab.

W PowerShell ustawić ścieżki do posiadanych narzędzi, a następnie z katalogu pakietu wykonać:

```powershell
$env:KICAD_LIBRARY_ROOT = 'C:/Program Files/KiCad/10.0/share/kicad'
$env:KICAD_CLI = 'C:/sciezka/do/kicad-cli.exe'
$env:EGRLAB_DOC_PYTHON = 'C:/sciezka/do/python-z-reportlab.exe'
$env:PDFTOPPM = 'C:/sciezka/do/pdftoppm.exe'
& 'C:/sciezka/do/python-pcbnew.exe' src/run_release.py --no-package
& 'C:/sciezka/do/python-pcbnew.exe' src/clean_rebuild.py
```

`--no-package` odtwarza schemat, PCB, sprawdzenia i PDF. Po zmianie PDF trzeba ponownie wykonać kontrolę wzrokową; nie kopiować starego wpisu PASS. `package_release.py` odmawia pakowania bez aktualnej kontroli, czystego odtworzenia i zgodnych hashów PDF.

Nowy routing (`run_release.py --new-route`, wymaga `EGRLAB_FREEROUTING`) jest eksperymentem wymagającym ponownej recenzji, nie trybem odtworzenia. Freerouting 2.1.0 nie jest deterministyczny; liczba zgłaszanych przez niego połączeń nie zastępuje KiCad. Narzucono limit czasu 180 s i sterty 4 GiB. Pętla w `run_layout.py` robi do 6 prób. Nową próbę wymusza luka trasowania (brak ścieżki uzupełniającej, luka po czyszczeniu) albo pad złącza bez termika. Ścieżki uzupełniające planuje raster na podstawie natywnego DRC i podlegają one końcowemu DRC.

Fingerprint geometrii ignoruje losowe UUID. Obejmuje położenia/pady/połączenia/ścieżki/przelotki/obrysy wylewek i teksty płytki. Nie jest zamiennikiem DRC ani pomiaru fizycznego.

## Otwarte pozycje

Pełne rysunki konkretnych złączy i przymiarka (MECHANIKA, w tym wtyki Mini-Fit przy grzebieniu R41/R42/R4 i przy R39), pomiar czasu HC123 przy 3,3 V, przycisk ARM, zaniki zasilania, zakłócenia, współpraca z P01/P03/P08 i przyszłym P07. Potwierdzenie progu MCP100-300 w karcie DS11187F przy zamówieniu (w R2 wartości z tabeli MCP1X0 w DS11184D). Ich obecność jest przyczyną statusu „do recenzji”, a nie deklaracją zaliczenia sprzętu.
