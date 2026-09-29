# P04 SAFE — R1 do recenzji

25.09.2026. Płytka sprzętowego STOP, watchdoga, ręcznego ARM i zezwoleń EGRLab.
Projekt oparty na zamrożonej netliście v6.1-rc1. Oryginały w `reference/` z hashami.
P03 opracowuje Opus; niniejszy pakiet nie zmienia jej plików. P07 pozostaje HOLD do kontroli modułu BTS7960.

**Stan: gotowe pliki do niezależnej recenzji i przymiarki. Sprzęt NIE ZBADANO. Nie jest to zwolnienie PCB do zamówienia.**

- `eda/P04.kicad_pro`, `eda/P04.kicad_sch`, `eda/P04.kicad_pcb`: kompletny, edytowalny projekt KiCad 10; lokalne biblioteki.
- `output/pdf/P04-R1-schemat.pdf`: sześć arkuszy A3.
- `output/pdf/P04-R1-PCB.pdf`: opis, montaż i miedź obu stron 1:1.
- `docs/PROJEKT.md`: działanie, zmiany względem bazy, obliczenia i granice weryfikacji.
- `docs/BOM.csv`, `docs/ZAKUPY.csv`, `docs/WIAZKI-BOM.csv`: elementy, zestawienie zakupowe i wiązki.
- `docs/interfejsy.csv`, `docs/pinout.csv`: kontrakt P04 i numeracja.
- `docs/P00-P04.md`, `docs/ODBIOR.md`: samodzielne uruchomienie bez samochodu i bez silnika.
- `docs/MECHANIKA.md`, `docs/DLA-RECENZENTA.md`: przymiarka oraz zakres recenzji.
- `verification/QA.md`: wyniki kontroli i polecenie odtworzenia.

Płytka ma 160 × 120 mm, dwie warstwy 35 µm, FR4 1,6 mm i cztery otwory M3. To celowo luźny montaż THT, z trzema układami SO14 na adapterach. Nie potrzeba pieca ani układów QFN.

Najważniejsze zmiany: lokalny nadzór 3,3 V; odtworzenie poziomu SAFE_N przez dwie bramki Schmitta; tranzystory przewlekane w otwartych kolektorach; odsprzęganie i punkty pomiarowe. Wyprowadzenia SAFE do CORE zachowane. SENSOR przechodzi z 4 na **6 pozycji IDC (M2.2)**: piny 1–4 zachowane, 5–6 NC. Wymaga zgodnej wiązki przyszłej P08.

Gerberów do zamawiania nie wydano. Najpierw recenzja, sprawdzenie zakupionych złączy/adapterów na wydruku 100% i zamknięcie listy w `docs/MECHANIKA.md`.
