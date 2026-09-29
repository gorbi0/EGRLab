# P01 — pakiet do zamówienia PCB

Wydanie: **27.09.2026**, baza **P01-PCB-R3.1-review**. Geometria PCB R3,
schemat R3, wariant montażowy A1. Plik płytki jest bajtowo zgodny z R3.1;
nie zmieniano tras, rozmieszczenia, otworów ani nadruku.

**Do formularza producenta wgraj `DO-ZAMOWIENIA_P01-PCB-R3.1.zip`.**
Zawiera wyłącznie 7 warstw Gerber X2 i 2 pliki wierceń Excellon.
Parametry wpisz według `INSTRUKCJA-ZAMOWIENIA.md`. Zamówienie obejmuje gołe PCB.

| Parametr | Ustawienie |
|---|---|
| Wymiary | **160 × 120 mm** |
| Warstwy | **2** |
| Laminat | **FR4, 1,6 mm** |
| Miedź | **35 µm / 1 oz na każdej stronie** (zmiana z 70 µm — poniżej) |
| Wykończenie | HASL bezołowiowy |
| Maska / nadruk | zielona / biały, obustronnie |
| Test elektryczny producenta | tak |
| Panel, montaż, szablon pasty | nie |

**Zmiana 28.09.2026: miedź 35 µm zamiast 70 µm** (decyzja użytkownika, koszt 70 µm ok. 4×). Uzasadnienie: przy 5 A najwęższe odcinki toru mocy (2 mm) grzeją się wg IPC-2221 o ok. 17 °C zamiast 5 °C, a sam rejestrator bez P07 pobiera poniżej 1 A. Warunek: przed pierwszym uruchomieniem P07 próba nagrzewania toru mocy przy 0,1 / 1 / 3,5 / 5 A (ODBIOR R3). Pliki CAM bez zmian — grubość miedzi to tylko parametr zamówienia. Dokumenty w `projekt/` opisują pierwotne założenie 70 µm.

Kontrole: **31/31 projektu**, DRC **0/0/0**, wykryte **5/5 celowych usterek**,
**28/28 kontroli CAM**. Niezależny parser porównał wszystkie 202 otwory PTH,
8 NPTH i 199 pól lutowniczych na każdej warstwie z modelem PCB.
Obejrzano podglądy wyeksportowanych warstw, obu stron i wierceń.

**Przymiarka rzeczywistych części oraz próby elektryczne i termiczne nie mają
potwierdzonego wyniku.** To wydanie plików do wykonania prototypu, a nie odbiór
działającego urządzenia. Eksport wykonano na bieżące zlecenie użytkownika;
dawny zapis „eksport po przymiarce” w dokumentacji R3.1 nie jest dowodem jej wykonania.
Formularz przymiarki: `projekt/docs/MECHANIKA.md`.

Materiały pomocnicze:

- `podglad/CAM-top.png`, `CAM-bottom.png` — wygląd wynikający z Gerberów; spód oglądany od spodu.
- `podglad/CAM-kontrola-warstw.png` — zbiorczy widok warstw; pojedyncze warstwy CAM w orientacji od góry.
- `projekt/output/pdf/P01-PCB-R3.1-dokumentacja.pdf` — niezmieniony PDF R3.1, montaż i wydruk 1:1.
- `projekt/docs/BOM-MONTAZOWY-A1.csv` — właściwy BOM montażowy.
- `projekt/eda/P01.kicad_pro` — kopia źródeł KiCad; właściwa płytka obok, `P01.kicad_pcb`.
- `verification/QA.md` — zakres kontroli i identyfikacja plików.
- `SPECYFIKACJA-DLA-PRODUCENTA.txt` — opis wykonania po angielsku.

Na nadruku pozostaje „PCB R3”: R3.1 poprawiała dokumentację i ukryte pole U4,
nie geometrię. To prawidłowe oznaczenie tej płytki. Przy montażu **C6 dopiero po
dokręceniu Q1 do radiatora**, zgodnie z MECHANIKA. Uruchamianie samej P01:
`projekt/reference/R3-docs/ODBIOR.md`, `METROLOGIA.md` oraz
`projekt/docs/ODBIOR-R3-DODATEK.md`.

Do wykonania nie używać materiałów historycznych z `projekt/reference` ani
`projekt/routing`. Jedynym pakietem CAM do zamówienia jest ZIP wskazany powyżej.
