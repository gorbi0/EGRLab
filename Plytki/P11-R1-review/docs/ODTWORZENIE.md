# Odtworzenie i sprawdzenie pakietu

Narzędzia użyte: KiCad10.0.6 z Pythonem `pcbnew`,NumPy,Pillow;Python z reportlab
i pypdf doPDF. `KICAD_LIBRARY_ROOT` wskazuje katalog `share/kicad` tej wersji.
`KICAD_CONFIG_HOME` powinien wskazywać lokalny zapisywalny katalog konfiguracji.
`EGRLAB_DOC_PYTHON` wskazuje interpreter zreportlab. Nie zmieniać w ciemno wersji
bibliotek footprintów; sprawdzić ich różnice przed ponownym generowaniem.

W katalogu pakietu, Pythonem KiCad:

```text
python src/run_release.py --rebuild --no-pdf
python src/board_fingerprint.py
```

`--rebuild` odtwarza schemat i PCB z generatorów oraz zapisanej sesji trasowania
`routing/P11.ses`. Nie wymaga ponownego uruchamiania autoroutera. Wyjście z błędem
zatrzymuje proces. Brak `--no-pdf` tworzy również dwa PDF-y; po każdej zmianie
trzeba je wyrenderować i obejrzeć. Sama poprawność kodu wyjścia nie sprawdza layoutu.

Pełna czysta odbudowa: do pustego katalogu skopiować tylko `src`, `input`,
`reference`, `requirements`, `routing/P11.ses`, `routing/completion-routes.json`.
Utworzyć puste `eda`, `docs`, `verification`, `output/pdf`, `output/previews`.
Uruchomić powyższe polecenie. Porównać `geometry-fingerprint.json` i SHA256
czterech plików schematu z pakietem. Raporty muszą powstać na nowo.
Dokumenty opisowe nie są automatycznie odtwarzane przez generator CAD.

Regeneracja kandydackiego trasowania wymaga Freerouting2.1.0/JRE21 i zmiennej
`EGRLAB_FREEROUTING`. Jest pomocą do prowadzenia sygnałów, nie etapem zatwierdzenia.
Przy tworzeniu R1 przesunięto J1 z66 do70 mm,aby opisy nie kolidowały z polami.
Zaadaptowano wcześniejszą sesję sygnałową i ponownie wygenerowano krótkie tory
mocy. Końcową geometrię sprawdzono natywnym DRC,parity i kontrolami niezależnymi.
Nie zmniejszano wymaganego odstępu ani szerokości ścieżek w celu ukrycia kolizji.

Wynik wydania: `verification/drc.json` i `drc.provenance.json`, a nie raporty
pośrednie w `routing`. Manifest SHA256 obejmuje pliki dostarczone. Zmiana źródła,
biblioteki,pinoutu,wiązki lub PCB wymaga odświeżenia kontroli i manifestu.
