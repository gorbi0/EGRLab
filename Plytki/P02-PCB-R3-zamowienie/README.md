# P02 — pakiet do zamówienia PCB

Wydanie **28.09.2026**, źródło **P02-R3-review**. Plik płytki jest bajtowo zgodny z wydaniem R3; nie zmieniano tras, rozmieszczenia, otworów ani opisu. 

**Do producenta wgraj `DO-ZAMOWIENIA_P02-PCB-R3.zip`.** Zawiera wyłącznie 6 warstw Gerber X2 i 2 pliki wierceń Excellon. Parametry: `SPECYFIKACJA-DLA-PRODUCENTA.txt`; zamówienie w Satland krok po kroku: `../Zamowienie-Satland/INSTRUKCJA-SATLAND.md`.

| Parametr | Ustawienie |
|---|---|
| Wymiary | **160 × 120 mm** |
| Warstwy | 2 |
| Laminat | FR4; projekt 1,6 mm, w Satlandzie wybrać 1,5 mm |
| Miedź | **35 µm na każdej stronie** (zmiana z 70 µm — poniżej) |
| Wykończenie | HAL |
| Maska | zielona, obie strony |
| Opis | biały, **tylko góra** (dolny opis w projekcie jest pusty) |
| Otwory | 205 PTH (w tym 1 przelotka), 10 NPTH; wiertła 0,5–4,2 mm; bez szczelin |
| Najwęższa ścieżka / najmniejszy odstęp (reguła) | 0,5 mm / 0,25 mm; miedź–krawędź ≥ 0,5 mm |

**Zmiana 28.09.2026: miedź 35 µm zamiast 70 µm z założeń R2/R3** (decyzja użytkownika, koszt 70 µm ok. 4×). Uzasadnienie: tor VMOTOR 5 A biegnie wylewką VPROT, a szyny za F1 T2A przy 2 A grzeją się wg IPC-2221 najwyżej o ok. 7 °C; sam rejestrator bez P07 pobiera poniżej 1 A. Warunek: przed pierwszym uruchomieniem P07 próba nagrzewania toru VMOTOR przy 1 / 3,5 / 5 A. Pliki CAM bez zmian — grubość miedzi to tylko parametr zamówienia.

Kontrole: DRC KiCad 10.0.6 ze świeżym wypełnieniem stref i zgodnością ze schematem — **0 naruszeń, 0 niepołączonych, 0 rozbieżności**. Kontrola CAM własnym parserem Gerber/Excellon: **20/20** (każdy otwór, każde pole z siecią, otwarcia maski, obrys, liczba konturów wylewek). Próby ujemne kontroli CAM: **7/7 wykryte**, próba zerowa przechodzi. Oględziny podglądów wygenerowanych z samych plików CAM. 

**Przymiarka rzeczywistych części, próby elektryczne i cieplne: NIE ZBADANO.** To wydanie plików do wykonania prototypu, nie odbiór działającej płytki. Wydruk 1:1: `projekt/output/pdf/P02-R3-PCB.pdf` (skala 100 %, zmierzyć belkę 100 mm i obrys). Formularz odbioru: `projekt/verification/ODBIOR.md`.

| Ścieżka | Zawartość |
|---|---|
| `DO-ZAMOWIENIA_P02-PCB-R3.zip` (+ `.sha256`) | jedyny plik dla producenta |
| `gerber/` | te same pliki co w ZIP |
| `podglad/CAM-top.png`, `CAM-bottom.png` | wygląd wynikający z Gerberów; spód oglądany od spodu |
| `podglad/CAM-kontrola-warstw.png` | zestawienie warstw |
| `verification/QA.md` | zakres kontroli i odtworzenie |
| `projekt/` | kopia wydania P02-R3-review (KiCad, dokumentacja, BOM) |
| `src/` | eksport, kontrola CAM, próby ujemne, zamknięcie paczki |

Kolejność montażu, podparcie i osłona banku: `projekt/docs/MECHANIKA.md` — bank C1–C3 na końcu, pierwszy test bez banku, R17 (47 Ω / 25 W) poza płytką na osobnym radiatorze.
