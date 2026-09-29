# P04-R1 — kontrola wydania

25.09.2026. Status: DO NIEZALEŻNEJ RECENZJI; przymiarka i sprzęt NIE ZBADANO.

| Sprawdzenie | Wynik |
|---|---|
| Native ERC, sześć arkuszy | 0 naruszeń |
| Eksport XML vs specyfikacja generatora | 91 komponentów, 343 przypisania pinów, 0 różnic |
| Native DRC, wszystkie poziomy + pełne błędy ścieżek + parity | 0 naruszeń / 0 brakujących połączeń / 0 różnic schematu |
| Kontrole PCB, łącznie z native DRC | 20/20 PASS |
| Kontrole elektryczne z niezależnie odczytanej netlisty | 19/19 PASS |
| Tablice prawdy | 131072 kombinacje, sześć obserwowanych wyjść; liczba stanów H zapisana w JSON |
| Sekwencje ARM/reset/powrót sygnałów | PASS w modelu idealnej logiki; brak fizycznego pomiaru |
| Celowe mutacje połączeń | 10/10 wykrytych przez wskazaną kontrolę |
| Celowe mutacje PCB | 5/5 wykrytych; błąd wykonania skryptu nie liczy się jako wykrycie |
| Zakres interfejsów | Wszystkie stare aktywne piny zachowane; SENSOR +2 NC i jawne pady kluczy |
| Odtworzenie z czystych źródeł | Identyczna geometria semantyczna PCB; szczegóły clean-rebuild.json |
| PDF | 6 stron A3 schematu + 4 strony A4 PCB, kontrola rasteryzacji; hash w visual-qa.json |

Raport native DRC uruchamia się od nowa, usuwa poprzedni wynik i zapisuje hash wszystkich wejść oraz wynikowego raportu w `drc.provenance.json`. Nie ma wyłączeń DRC. Plik manifestu wydania wiąże wszystkie dostarczone pliki; ZIP sprawdzony bajt po bajcie.

Biblioteka pcbnew zapisując PCB może zresetować reguły projektu. Dlatego kolejność końcowa jest obowiązkowa: `silkscreen.py` → `set_rules.py` → `verify_pcb.py`. Sam zielony raport sporządzony przed przywróceniem reguł nie kwalifikuje projektu.

## Odtworzenie

Narzędzia: KiCad 10.0.6 z Pythonem pcbnew, jego biblioteki symboli/footprintów, Python z ReportLab/Pillow oraz Poppler. Freerouting nie jest potrzebny do odtworzenia zatwierdzonej geometrii: pakiet ma SES i jawne ścieżki uzupełniające. Pliki `input/footprints` są zahashowane. Nie trzeba mieć katalogów P00/P02 ani kopii całego EGRLab.

W PowerShell ustawić ścieżki do posiadanych narzędzi, a następnie z katalogu pakietu wykonać:

```powershell
$env:KICAD_CONFIG_HOME = 'C:/sciezka/do/zapisywalnego/profilu/kicad'
$env:KICAD_LIBRARY_ROOT = 'C:/Program Files/KiCad/10.0/share/kicad'
$env:KICAD_CLI = 'C:/sciezka/do/kicad-cli.exe'
$env:EGRLAB_DOC_PYTHON = 'C:/sciezka/do/python-z-reportlab.exe'
$env:PDFTOPPM = 'C:/sciezka/do/pdftoppm.exe'
& 'C:/sciezka/do/python-pcbnew.exe' src/run_release.py --no-package
& 'C:/sciezka/do/python-pcbnew.exe' src/clean_rebuild.py
```

`--no-package` odtwarza schemat, PCB, sprawdzenia i PDF. Po zmianie PDF trzeba ponownie wykonać kontrolę wzrokową; nie kopiować starego wpisu PASS. `package_release.py` odmawia pakowania bez aktualnej kontroli, czystego odtworzenia i zgodnych hashów PDF.

Nowy routing jest eksperymentem wymagającym ponownej recenzji, nie trybem odtworzenia. Freerouting 2.1.0 nie jest deterministyczny; liczba zgłaszanych przez niego połączeń nie zastępuje KiCad. Narzucono limit czasu 180 s i sterty 4 GiB. Skrypt ścieżek uzupełniających przechowuje wybrane trasy w JSON i podlega końcowemu DRC.

Fingerprint geometrii ignoruje losowe UUID. Obejmuje położenia/pady/połączenia/ścieżki/przelotki/obrysy wylewek i teksty płytki. Nie jest zamiennikiem DRC ani pomiaru fizycznego.

## Otwarte pozycje

Pełne rysunki konkretnych złączy i przymiarka (MECHANIKA), pomiar czasu HC123 przy 3,3 V, przycisk ARM, zaniki zasilania, zakłócenia, współpraca z P01/P03/P08 i przyszłym P07. Ich obecność jest przyczyną statusu „do recenzji”, a nie deklaracją zaliczenia sprzętu.
