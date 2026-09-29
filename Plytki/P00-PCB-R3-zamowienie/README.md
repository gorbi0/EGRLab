# P00 — pakiet do zamówienia PCB

Wydanie **28.09.2026**, źródło **P00-R3-review**. Plik płytki jest bajtowo zgodny z wydaniem R3; nie zmieniano tras, rozmieszczenia, otworów ani opisu. 

**Do producenta wgraj `DO-ZAMOWIENIA_P00-PCB-R3.zip`.** Zawiera wyłącznie 6 warstw Gerber X2 i 2 pliki wierceń Excellon. Parametry: `SPECYFIKACJA-DLA-PRODUCENTA.txt`; zamówienie w Satland krok po kroku: `../Zamowienie-Satland/INSTRUKCJA-SATLAND.md`.

| Parametr | Ustawienie |
|---|---|
| Wymiary | **115 × 70 mm** |
| Warstwy | 2 |
| Laminat | FR4; projekt 1,6 mm, w Satlandzie wybrać 1,5 mm |
| Miedź | **35 µm na każdej stronie** |
| Wykończenie | HAL |
| Maska | zielona, obie strony |
| Opis | biały, **tylko góra** (dolny opis w projekcie jest pusty) |
| Otwory | 146 PTH (w tym 1 przelotka), 4 NPTH; wiertła 0,5–3,2 mm; bez szczelin |
| Najwęższa ścieżka / najmniejszy odstęp (reguła) | 0,5 mm / 0,25 mm; miedź–krawędź ≥ 0,5 mm |

Kontrole: DRC KiCad 10.0.6 ze świeżym wypełnieniem stref i zgodnością ze schematem — **0 naruszeń, 0 niepołączonych, 0 rozbieżności**. Kontrola CAM własnym parserem Gerber/Excellon: **20/20** (każdy otwór, każde pole z siecią, otwarcia maski, obrys, liczba konturów wylewek). Próby ujemne kontroli CAM: **7/7 wykryte**, próba zerowa przechodzi. Oględziny podglądów wygenerowanych z samych plików CAM. Dodatkowo porównano z Gerberami wydania R3 (`projekt/output/fabrication`): wiercenia, maski, ścieżki, obrys i wylewki identyczne; pola te same co do położenia i sieci. Wydanie R3 zapisało 5 pól z zaokrąglonym narożnikiem jako makra apertur, ten eksport — jak P01 — jako regiony (`verification/porownanie-z-wydaniem-R3.json`).

**Przymiarka rzeczywistych części, próby elektryczne i cieplne: NIE ZBADANO.** To wydanie plików do wykonania prototypu, nie odbiór działającej płytki. Wydruk 1:1: `projekt/output/pdf/P00-R3-PCB.pdf` (skala 100 %, zmierzyć belkę 100 mm i obrys). Formularz odbioru: `projekt/docs/ODBIOR-P00-R2.md`.

| Ścieżka | Zawartość |
|---|---|
| `DO-ZAMOWIENIA_P00-PCB-R3.zip` (+ `.sha256`) | jedyny plik dla producenta |
| `gerber/` | te same pliki co w ZIP |
| `podglad/CAM-top.png`, `CAM-bottom.png` | wygląd wynikający z Gerberów; spód oglądany od spodu |
| `podglad/CAM-kontrola-warstw.png` | zestawienie warstw |
| `verification/QA.md` | zakres kontroli i odtworzenie |
| `projekt/` | kopia wydania P00-R3-review (KiCad, dokumentacja, BOM) |
| `src/` | eksport, kontrola CAM, próby ujemne, zamknięcie paczki |

Montaż i uruchomienie: `projekt/docs/LAYOUT.md` i `projekt/docs/ODBIOR-P00-R2.md`. W `projekt/output/pdf` leżą też stare PDF R2 — do wydruku brać `P00-R3-PCB.pdf`. Lista wyposażenia wiązki stanowiskowej w `projekt/docs/ZAKUPY-P00.md` ma błąd (J1 i J2 po stronie P00 muszą być męskie); poprawka w `Plytki/Zakupy-2/ZAKUPY-2.md`. Płytki to nie dotyczy.
