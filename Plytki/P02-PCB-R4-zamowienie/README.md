# P02 — pakiet do zamówienia PCB

Wydanie **02.10.2026**, źródło **P02-R4-review**. Plik płytki jest bajtowo zgodny z wydaniem R4 (stan 2.10: nowy nadruk; trasy, rozmieszczenie i otwory jak w wydaniu z 30.09). Format S1, klasa L (cały poziom 1 stosu). Płytka zaakceptowana przez użytkownika 30.09.2026 po recenzji PR #4; 2.10.2026 nowe wydanie: nadruk ≥ 1,0 mm z linią 0,15 mm (minimum JLCPCB, ustalenie niezależnych recenzji P05 / P06), miedź i otwory bez zmian.

**Do producenta wgraj `DO-ZAMOWIENIA_P02-PCB-R4.zip`.** Zawiera wyłącznie 7 warstw Gerber X2 i 2 pliki wierceń Excellon. Parametry: `SPECYFIKACJA-DLA-PRODUCENTA.txt` (ustawienia dla JLCPCB i uwagi dla Satlandu).

| Parametr | Ustawienie |
|---|---|
| Wymiary | **160 × 100 mm**, narożniki R1 |
| Warstwy | 2 |
| Laminat | FR4 1,6 mm (JLCPCB: 1.6 mm; w Satlandzie 1,5 mm) |
| Miedź | **35 µm na każdej stronie** |
| Wykończenie | HAL |
| Maska | zielona, obie strony |
| Opis | biały, obie strony |
| Otwory | 363 PTH (w tym 97 przelotek), 16 NPTH; wiertła 0,4–4,2 mm; bez szczelin |
| Najwęższa ścieżka / najmniejszy odstęp (reguła) | 0,3 mm / 0,25 mm; miedź–krawędź ≥ 0,5 mm |
| Najmniejszy pierścień (z geometrii) | ≥ 0,25 mm (przelotki 0,25 mm, pola 0,3 mm) |

Kontrole: DRC KiCad 10.0.6 ze świeżym wypełnieniem stref i zgodnością ze schematem — **0 naruszeń, 0 niepołączonych, 0 rozbieżności**. Przyjęte zgłoszenia `lib_footprint_mismatch` (14) dotyczą wyłącznie części, którym skrypt nadruku wydania przyciął linie lub przesunął tekst (`drc-accepted.json`); KiCad porównuje je z nieprzyciętą kopią w bibliotece. Nie wpływa to na miedź ani otwory. Kontrola CAM własnym parserem Gerber/Excellon: **20/20** (każdy otwór, każde pole z siecią, otwarcia maski, obrys, liczba konturów wylewek). Próby ujemne kontroli CAM: **8/8 wykryte**, próba zerowa przechodzi. Oględziny podglądów wygenerowanych z samych plików CAM. 

**Przymiarka rzeczywistych części, próby elektryczne i cieplne: NIE ZBADANO.** To wydanie plików do wykonania prototypu, nie odbiór działającej płytki. Wydruk 1:1: `projekt/output/pdf/P02-R4-PCB.pdf` (skala 100 %, zmierzyć belkę 100 mm i obrys). Procedura odbioru P02 R4 na stanowisku P00: do opracowania (punkty pomiarowe na listwach serwisowych J_SV1/J_SV2).

| Ścieżka | Zawartość |
|---|---|
| `DO-ZAMOWIENIA_P02-PCB-R4.zip` (+ `.sha256`) | jedyny plik dla producenta |
| `gerber/` | te same pliki co w ZIP |
| `podglad/CAM-top.png`, `CAM-bottom.png` | wygląd wynikający z Gerberów; spód oglądany od spodu |
| `podglad/CAM-kontrola-warstw.png` | zestawienie warstw |
| `verification/QA.md` | zakres kontroli i odtworzenie |
| `projekt/` | kopia wydania P02-R4-review (KiCad, dokumentacja, BOM) |
| `src/` | eksport, kontrola CAM, próby ujemne, zamknięcie paczki |

Montaż: najpierw od spodu U9 (SOIC-14) oraz C27 i C28 (1206), potem części THT od góry; wyprowadzenia THT od spodu przyciąć do ≤ 1,5 mm (S1 §4). Pola z pełnym połączeniem ze strefą GND (lista w `projekt/routing/solid-pads.json`, m.in. D3.2 — wyprowadzenie transila P600) lutować mocniejszą lutownicą. Opis montażu i wysokości: `projekt/output/pdf/P02-R4-PCB.pdf`.
