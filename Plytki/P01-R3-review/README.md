# P01 PROTECT R3 — poprawki przed layoutem

23.09.2026. Nowy pakiet po recenzji R2; R1/R2 i system 6.1 pozostają niezmienione.
**Projekt schematu i przygotowanie do layoutu. Nie ma jeszcze produkcyjnej PCB ani pomiarów prototypu.** P07: HOLD.

Zmiany elektryczne P01: rozłączalny LK1 w drenie Q1, z dostępem Kelvina.
C6 zmieniono na dostępny WIMA 1µF/100V/±5%; wartości RC i zabezpieczenia zachowano.
H_BAT ma teraz męski 1786174, a przewód od źródła żeński 1757019.
Radiatory dobrano jako SK129-63STS z lokalnym footprintem; J7 ma termiki.

## Pliki do pracy

- `eda/P01.kicad_pro` — trzy arkusze i lokalne biblioteki.
- `output/pdf/P01-R3-schemat.pdf` — aktualny schemat do przeglądania.
- `docs/ZMIANY.md` — zamknięcie każdej uwagi i pozostałe próby fizyczne.
- `docs/BOM.csv`, `ZAKUPY.csv`, `BOM-MECHANIKA.csv`, `ZAKUPY-NOWE.md` — części.
- `docs/METROLOGIA.md`, `ODBIOR.md` — przyrządy, niepewność i procedura.
- `mechanical/MECHANIKA.md` — radiator, termiki, punkty pomiarowe, montaż.
- `integration/P02-HOLD/` — ustalony kontrakt oraz obwód podtrzymania do P02;
  to dodatek do przyszłego projektu P02, nie zatwierdzona kompletna płytka P02.
- `verification/` — wyniki testów; `simulation/` — talie i przebiegi.
- `docs/PROCES.md` — obowiązkowa kontrola powrotu po usterce i wykonalności pomiarów.

Do rozpoczęcia layoutu używać tej rewizji i jej delty. Przymiarka realnych części
i kontrola gotowego rozmieszczenia są konieczne przed Gerberami. Podtrzymanie P02
nie zmienia złącza ani limitu pojemności widzianej bezpośrednio przez P01.

## Odtworzenie weryfikacji

KiCad CLI 10, Python z numpy, ngspice DLL. Ustaw `NGSPICE_LIBRARY` na bibliotekę
ngspice, a tylko przy regeneracji CAD `KICAD_LIBRARY_ROOT` na share/kicad.
Nie regeneruj schematu po ręcznych edycjach, aby wymusić przejście testów.

```text
kicad-cli sch export netlist --format kicadxml -o verification/P01.xml eda/P01.kicad_sch
kicad-cli sch erc --severity-all --format json -o verification/erc.json eda/P01.kicad_sch
python src/verify.py
python src/check_package.py
python src/bounds.py
python src/dynamics.py
python src/recovery.py
python src/hold_budget.py
python src/write_r3_docs.py
python src/check_release.py
python src/check_r3.py
```

Modele tranzystorów są przybliżone. Raporty rozdzielają pozytywne kryteria,
oczekiwane wykrycie zaniku zasilania oraz wyczerpanie rezerwy. PASS nie jest
potwierdzeniem SOA, odporności automotive ani działania konkretnego egzemplarza.
