# Kontrola wydania do wykonania P01 — 27.09.2026

Źródło: P01-PCB-R3.1-review. SHA-256 właściwej PCB:
`1de61495fa878eb05c8e8707e20257b313c1160763756146557789249a2f8f42`.

## Wyniki

- Natywny KiCad 10.0.6 DRC z ponownym wypełnieniem stref i porównaniem schematu:
  0 naruszeń, 0 niepołączonych, 0 rozbieżności. `projekt/verification/drc.json`.
- Odbiór R3.1: 31/31. `projekt/verification/pcb-checks.json`.
- Próby ujemne: 5/5 wykryte. `projekt/verification/negative-controls.json`.
  Celowo uszkodzonych kopii PCB nie ma w opublikowanym pakiecie.
- Eksport KiCad bez regeneracji projektu i bez zapisu zmian PCB; hashe wejść
  zgodne przed i po. `export-receipt.json`, logi obok.
- Niezależny odczyt Gerber/Excellon, gerbonara 1.5.0: 28/28. `cam-checks.json`.
  Porównanie współrzędnych i średnic wszystkich 210 otworów oraz położenia
  i sieci 199 pól THT na każdej warstwie. Zweryfikowane otwarcia maski.
- Oględziny podglądów wyprowadzonych z plików CAM: obie strony, warstwy miedzi,
  maski, nadruki i mapy wierceń. `visual-review.json`.
- Pakiet ZIP ma dokładnie 9 właściwych plików, bez podkatalogów, starych rewizji,
  rysunków przymiarki i plików kontrolnych. Ich bajty muszą odpowiadać eksportom.
- Manifest i suma ZIP pozwalają sprawdzić kompletność po skopiowaniu.

## Szczegóły interpretacji

Parser Excellon ostrzega o G90 po końcu nagłówka pliku KiCad. Porównanie każdego
otworu z PCB potwierdza poprawny odczyt jednostek, średnic i współrzędnych.
Inne ostrzeżenia parsera są błędem kontroli. Biblioteka 1.5.0 gubi atrybuty X2
na obiektach Region; checker odczytuje samą metadokumentację padów z rodzimego
strumienia, a geometrię regionów nadal bierze z niezależnego parsera.

`P01-job.gbrjob` pozostawiono wyłącznie w verification: natywny zapis KiCad podaje
160,05 × 120,05 mm jako obwiednię kreski obrysu. Wykonawczy obrys po osi kreski
ma dokładnie 160 × 120 mm. Nie zmieniano tego pliku ręcznie; nie trafił do ZIP-a.

Podglądy kolorowe są ilustracją geometrii CAM, nie specyfikacją koloru laminatu.
Spód kolorowy oglądany jest od spodu; pojedyncze warstwy zachowują orientację od góry.
PNG nie służą do wykonywania PCB ani do wydruku przymiarki 1:1.

Przymiarka rzeczywistych części, elektryka, dynamika odcięcia, SOA i termika:
**NIE ZBADANO**. Wynik cyfrowy nie stanowi zatwierdzenia sprzętu do pracy w aucie.
Zakres wydania to pliki do wykonania i uruchomienia prototypu P01.

## Odtworzenie

1. KiCad Python 10.0.6: `projekt/src/verify_pcb.py`.
2. Tym samym Pythonem: `src/export_production.py` (uruchamia też próby ujemne).
3. Python z gerbonara 1.5.0: `src/check_cam.py`.
4. Node z sharp: `src/render_cam.mjs <podglad> <sciezka-do-sharp>`;
   Python z Pillow i gerbonara: `src/compose_cam.py`.
5. Oględziny podglądów i ponowne zamknięcie ZIP/manifestu przez `src/seal_package.py`.

Po dowolnej zmianie CAD potrzebny jest cały nowy odbiór. Nie korzystać z raportu
z poprzednim hashem. Archiwalny `projekt/src/run_release.py` odtwarza wyłącznie
dawny pakiet przeglądowy R3.1; nie tworzy niniejszego ZIP-a do producenta.

Dokumentacja narzędzi: [KiCad CLI 10.0](https://docs.kicad.org/10.0/en/cli/cli.html)
oraz [Gerbonara](https://gerbolyze.gitlab.io/gerbonara/).
