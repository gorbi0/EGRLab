# 05 — Szarpanie 1600–1800 obr. (diagnostyka lipiec 2026)

Aktualnie traktowane jako **osobna usterka** (ścieżka B w procedurze v3), bo ma odwrotną sygnaturę termiczną niż P0404.

## Objaw (pierwotnie)
Falowanie/szarpanie przy 1600–1800 obr. i lekkim gazie; znika przy mocniejszym przyspieszeniu. Obecnie: głównie po zimnym rozruchu (1500–1700 obr.), ustępuje po nagrzaniu, częstsze przy chłodnych porankach.

## Wykluczone / sprawdzone
- **Układ paliwowy:** zimny rozruch po nocy — ciśnienie szyny 259 bar w 0,5 s od kręcenia. Czysto.
- **Kody IQA wtryskiwaczy:** fizycznie porównane z głowicami wtryskiwaczy — zgodne z ECU.
- **Adaptacja przepustnicy:** wykonana (ręcznie i interfejsem) — bez zmiany.
- **Solenoid VGT:** mało prawdopodobny (brak kodów doładowania).

## Obserwacje z logów
- Log 24.07: EGR aktywny, średnio 10,9%, szczyty 43,5% w strefie objawu; MAF oscyluje 43–129 kg/h przy stałych obrotach.
- Log z regeneracją DPF: EGR stłumiony (średnio 4,7%), brak szarpania → regeneracja maskuje objaw.
- Log 24.07 był z AC zawsze włączoną (brak start-stop).

## Otwarte testy
- Zimny rozruch: zalogować jedyny PID EGR podczas szarpania. EGR zamknięty zgodnie z komendą → szarpanie poza EGR.
- Jazda z odpiętą wtyczką EGR (odróżnienie EGR od klap wirowych).
- Kandydaci poza EGR (uwalniające się z ciepłem): zakoksowana zmienna geometria turbiny, klapy wirowe kolektora, rozpylenie wtryskiwaczy na zimno, świece żarowe / dogrzewanie po rozruchu.
