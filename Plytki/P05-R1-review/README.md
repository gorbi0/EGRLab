# P05 DAQ — R1 do recenzji

Samodzielna płytka akwizycji dla EGRLab: AD7606BBSTZ, osiem kanałów, przekaźniki odczepów, VSENSE/AUX i sprzętowy nadzór zasilania. Projekt bazuje na v6.1-rc1 oraz zapisanej kopii pinoutu i mechaniki P03. P03 i pozostałe moduły nie są tu zmieniane; P07 pozostaje HOLD.

**Status: projekt do niezależnej recenzji i uruchomienia prototypu. Sprzętu nie zmontowano ani nie zmierzono. Nie wydano Gerberów do zamówienia.** Raporty dotyczą plików tej paczki, nie całego EGRLab ani zachowania na samochodzie.

- `eda/P05.kicad_pro` — projekt KiCad 10, osiem arkuszy schematu, PCB i lokalne biblioteki.
- `output/pdf/P05-R1-schemat.pdf` — schemat elektryczny A3.
- `output/pdf/P05-R1-PCB.pdf` — opis oraz montaż i obie warstwy miedzi 1:1, A4 poziomo.
- `docs/PROJEKT.md`, `MECHANIKA.md`, `INTEGRACJA.md`, `ODBIOR.md` — projekt, montaż, zależności i pomiary.
- `docs/BOM.csv`, `zakupy.csv`, `wiazki-BOM.csv`, `interfejsy.csv`, `pinout.csv` — części i wiązki. Kolumna końca lutowanego jest jawna.
- `docs/DLA-RECENZENTA.md` — zakres recenzji i otwarte warunki odbioru.
- `verification/QA.md` — odtwarzanie i zakres dowodów; raporty JSON obejmują także testy z celowo uszkodzonymi połączeniami.

Najważniejsze odstępstwa od ogólnego schematu v6.1: VDRIVE i logika P05 z lokalnego LDO za filtrem AVCC; BUSY również przez bufor Ioff; MEAS_EN sprzętowo połączone z DAQ_OK; zmarginesowane progi okna; przekaźniki THT; złącze B2B dobrane do koplanarnego ustawienia P03. Pełna lista i uzasadnienia w `docs/PROJEKT.md`.

Przed PCB szczególnie sprawdzić rzeczywistą parę złączy B2B, numerację widzianą od strony lutowania i przełącznik AUX. Przed pomiarami trzeba wdrożyć sekwencję rozruchową ADC opisaną w `docs/INTEGRACJA.md`. Zgodność pinów nie oznacza automatycznej zgodności niezmienionego firmware.

Weryfikacja tej paczki: ERC **0**, kontrola netlisty **421/421 pinów**, DRC **0 zgłoszeń / 0 braków połączeń / 0 rozbieżności ze schematem**, **21/21** kontroli elektrycznych i **20/20** PCB. Wykryto **9/9** celowych mutacji elektrycznych oraz **5/5** PCB. Odtworzenie w nowym katalogu dało identyczny odcisk geometrii. Obejrzano wszystkie 8 stron schematu i 4 strony dokumentacji PCB. Szczegóły oraz granice tych kontroli są w `verification/`.
