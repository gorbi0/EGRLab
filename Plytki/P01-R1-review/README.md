# P01 PROTECT — R1-review

23.09.2026 · baza EGRLab-v6.1-rc1 · prototyp, montaż ręczny THT, plan PCB 2L.

Pakiet zawiera funkcjonalny schemat P01 w KiCad, listę części, lokalne biblioteki,
rysunek podziału płytki, kartę wiązek i dowody kontroli. **Etap: przegląd schematu,
przed prowadzeniem ścieżek.** Nie zawiera Gerberów ani zatwierdzonej płytki do produkcji.

P07 jest WSTRZYMANE: rozważany moduł BTS7960 zamiast Pololu 1451. Wrócić do P07 po
otrzymaniu egzemplarza. Decyzję zapisano także w EGRLab-AKTYWNE.md; P01 nie zależy
od rozstrzygnięcia sygnałów sterowania P07, ale jego budżet pozostaje 5 A.

## Otwieranie

- `output/pdf/P01-R1-schemat.pdf` — trzy arkusze A3 do czytania i wydruku.
- `eda/P01.kicad_pro` — projekt KiCad 10; otwórz główny `P01.kicad_sch`.
- `docs/BOM.csv` — części per oznaczenie, MPN, footprint, źródło.
- `docs/ZAKUPY.csv` — części zgrupowane; osobno `docs/BOM-MECHANIKA.csv`.
- `docs/ZMIANY.md` — różnice względem bazy; bez zmian topologii P01.
- `docs/WIAZKI.md` — lutowanie, kotwy i mapowanie pinów.
- `mechanical/P01-strefy.svg` i `mechanical/MECHANIKA.md` — plan 160 × 100 mm.
- `docs/ODBIOR.md` — procedura pomiarów, wszystkie próby sprzętowe jeszcze niewykonane.
- `docs/PRZEGLAD.md` — kolejna bramka procesu i kwestie do zamknięcia.

## Co jest sprawdzone

Porównanie rzeczywistego eksportu KiCad XML z zamrożoną bazą: 87 elementów (77 z bazy
+ 10 pól pomiarowych), 189 końcówek i 34 sieci. Zero różnic połączeń.
ERC: zero błędów i ostrzeżeń. Raporty znajdują się w `verification/`.
Kontrola padów dotyczy numeracji, rastra wybranych kondensatorów i kotew wiązek;
**nie zastępuje** odbioru gabarytów zakupionych części na wydruku 1:1.

Testy mutacyjne celowo podmieniają D/S Q1, wejścia OVP, odłączają SAFE_N i usuwają
footprint J6 w kopiach netlisty. Każda zmiana musi zostać wykryta. Obliczenia DC
z bazy uruchomiono na kopii, bez zmieniania bazy; nie są symulacją przełączeń.

## Co trzeba zamknąć przed layoutem

1. Niezależna recenzja tych konkretnych trzech arkuszy i doboru części.
2. Rysunek mocowania wybranego radiatora: obrys przewidziano, jego otworów jeszcze
   nie przeniesiono na PCB. Nie zgadywać wymiarów ze zdjęcia handlowego.
3. Dostępność dokładnych MPN, zwłaszcza C1 i rezystorów H4. Zamiennik wymaga
   sprawdzenia gabarytów, pinów i parametrów, zanim zostanie wpisany do layoutu.

Biblioteki są lokalne w `eda/libraries`; projekt otwiera się bez generatora.
Skrypty `src/build_*` to narzędzia autora, które nadpisują wygenerowane pliki.
Po ręcznej edycji w KiCad nie uruchamiać ich ponownie bez przeniesienia zmian.
`src/cadlib.py` szuka źródłowych bibliotek KiCad w lokalnym katalogu narzędzi autora;
ta ścieżka dotyczy regeneracji, nie otwierania projektu.

Wydania V3/V5/V6/6.1-rc1 pozostają niezmienione. `baseline/` jest kopią odniesienia
ze skrótami SHA-256; nie stanowi drugiej bieżącej wersji schematu.
