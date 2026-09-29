# EGRLab P01 PROTECT — R2-review

23.09.2026. Rewizja po recenzji Opusa. R1 i baza EGRLab-v6.1-rc1 pozostają niezmienione.
**Schemat do ponownej recenzji, nie do zamówienia PCB.** P07 nadal HOLD.

Tor bramki: C5=10nF, C6=1µF (film ±5%), R21=100kΩ, R22=470kΩ, R27=10Ω/2W.
Q2 jest teraz P-MOS SUP53P06-20-E3 w TO-220; D9=15V chroni jego bramkę.
Nie zakładamy już dużego hFE małego PNP przy setkach mA. Pinout Q2 jest INNY niż w R1.

- `eda/P01.kicad_pro` — KiCad10, trzy arkusze, lokalne biblioteki.
- `output/pdf/P01-R2-schemat.pdf` — trzy arkusze A3.
- `docs/BOM.csv`, `ZAKUPY.csv`, `BOM-MECHANIKA.csv` — części i wiązki.
- `docs/ZMIANY.md` — odpowiedź na R1-01…R1-04.
- `docs/ANALIZA.md` — dobór, wyniki i granice modelu.
- `docs/PROCES.md` — dodatkowe kontrole dla następnych PCB.
- `docs/ODBIOR.md`, `PRZEGLAD.md` — próby oraz otwarte bramki.
- `simulation/decks`, `simulation/results` — talie SPICE i przebiegi CSV.
- `verification/` — rzeczywisty eksport XML, ERC, testy i obliczenia.

88 elementów,191 końcówek,34 sieci. ERC0 uwag przy zapisanych ustawieniach.
203 kontrole pakietu, w tym9 wykrywanych mutacji. Test dynamiki odrzuca znany
błędny wariant R1. R2 przechodzi zdefiniowane kryteria przesiewowe modelu.
Modele tranzystorów są przybliżone, detektor OVP zastępuje jawne opóźnienie.
Nie jest to gwarancja dla wszystkich egzemplarzy i temperatur ani kwalifikacja automotive.

Następnie: recenzja różnicy R1→R2, mocowanie radiatorów i konkretne części, layout2L,
kontrole produkcyjne i prototyp P01. Brak jeszcze PCB, Gerberów, DRC i pomiarów.
SAFE_N oznacza brak wykrytego błędu, nie gotowe VPROT. W integracji przed KPWR
potrzebny jest stabilny pomiar VPROT — szczegóły w ODBIOR, sekcja7.

## Powtórzenie kontroli

KiCad CLI10.0.6, Python3+numpy, biblioteka ngspice (DLL z KiCad w tej sesji).
Ustaw NGSPICE_LIBRARY na własną bibliotekę, gdy domyślna ścieżka autora nie istnieje.
Programów KiCad/ngspice nie dołączono do archiwum; talie.cir można uruchamiać w CLI.
Użyty solver: ngspice46, build14.04.2026. Dane wersji i skróty wejść w verification/.

```text
kicad-cli sch export netlist --format kicadxml -o verification/P01.xml eda/P01.kicad_sch
kicad-cli sch erc --format json -o verification/erc.json eda/P01.kicad_sch
python src/verify.py
python src/check_package.py
python src/bounds.py
python src/dynamics.py
python src/write_r2_docs.py
python src/check_release.py
```

Nie uruchamiać build_schematic.py po ręcznych zmianach w KiCad, by „naprawić” test.
Model czyta faktyczną XML, nie oczekiwany wynik generatora. `baseline/` oraz
`reference/R1-*` są historyczne, nie stanowią aktualnego projektu.
Jeśli regenerujesz CAD ze źródeł, KICAD_LIBRARY_ROOT wskazuje katalog KiCad
z podkatalogami symbols/footprints. Do samego otwierania projektu nie jest potrzebny.
