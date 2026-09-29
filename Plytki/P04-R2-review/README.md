# P04 SAFE — R2 do recenzji

26.09.2026. Płytka sprzętowego STOP, watchdoga, ręcznego ARM i zezwoleń EGRLab.
R2 (Claude) powstała z R1 Astry po recenzji `Plytki/P04-R1-recenzja/RECENZJA-P04-R1.md`: wdrożone uwagi R4-01…R4-07. Pakiet R1 (`Plytki/P04-R1-review`) pozostaje bez zmian jako punkt odniesienia. Mapa zmian: `docs/ZMIANY-R2.md`.
Projekt oparty na zamrożonej netliście v6.1-rc1. Oryginały w `reference/` z hashami. P07 pozostaje HOLD do kontroli modułu BTS7960.

**Stan: gotowe pliki do niezależnej recenzji i przymiarki. Sprzęt NIE ZBADANO. Nie jest to zwolnienie PCB do zamówienia.**

- `eda/P04.kicad_pro`, `eda/P04.kicad_sch`, `eda/P04.kicad_pcb`: kompletny, edytowalny projekt KiCad 10; lokalne biblioteki.
- `output/pdf/P04-R2-schemat.pdf`: sześć arkuszy A3.
- `output/pdf/P04-R2-PCB.pdf`: opis, montaż i miedź obu stron 1:1.
- `docs/ZMIANY-R2.md`: co zmieniono względem R1 i dlaczego, z odwołaniem do uwag recenzji.
- `docs/PROJEKT.md`: działanie, zmiany względem bazy, obliczenia i granice weryfikacji.
- `docs/BOM.csv`, `docs/ZAKUPY.csv`, `docs/WIAZKI-BOM.csv`: elementy, zestawienie zakupowe i wiązki.
- `docs/interfejsy.csv`, `docs/pinout.csv`: kontrakt P04 i numeracja.
- `docs/P00-P04.md`, `docs/ODBIOR.md`: samodzielne uruchomienie bez samochodu i bez silnika.
- `docs/MECHANIKA.md`, `docs/DLA-RECENZENTA.md`: przymiarka oraz zakres recenzji.
- `verification/QA.md`: wyniki kontroli i polecenie odtworzenia.

Płytka ma 160 × 120 mm, dwie warstwy 35 µm, FR4 1,6 mm i cztery otwory M3. To celowo luźny montaż THT, z trzema układami SO14 na adapterach. Nie potrzeba pieca ani układów QFN.

Najważniejsze zmiany R2: nadzorca U11 w wariancie MCP100-300 (próg 2,85–3,00 V); watchdog kasuje zatrzask ARM i obie zgody drugą drogą przez wolną bramkę U7D, niezależnie od Q1; 3,3 V wychodzi na złącza PG i panelu wyłącznie przez rezystory (1 kΩ, 1 kΩ, 100 Ω); C18 1 nF i R5 przy wejściu Schmitta SAFE_N; R41/R42 1 kΩ w liniach TEST_KEY i MECH_OK; napisy KEY n przy złączach IDC; wylewki GND zszyte przelotkami. Wyprowadzenia wszystkich złączy zachowane; zmieniła się tylko sieć na J7.1 i J8.1 (ten sam sygnał 3,3 V, ale przez rezystor).

Gerberów do zamawiania nie wydano. Najpierw recenzja, sprawdzenie zakupionych złączy/adapterów na wydruku 100% i zamknięcie listy w `docs/MECHANIKA.md`.
