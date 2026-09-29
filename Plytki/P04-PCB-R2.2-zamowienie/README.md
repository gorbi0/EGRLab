# P04 — pakiet do zamówienia PCB

Wydanie **28.09.2026**, źródło **P04-R2.2-review**. Plik płytki jest bajtowo zgodny z wydaniem R2.2; nie zmieniano tras, rozmieszczenia, otworów ani opisu. Miedź, wiercenia, strefy i rozmieszczenie są identyczne z zamkniętą R2.1 (kontrola rewizji R2.1 → R2.2: XOR miedzi 0); R2.2 zmienia wyłącznie R17 na 10 kΩ (kontrakt resetu z P03-R5) i numer wersji w opisie.

**Do producenta wgraj `DO-ZAMOWIENIA_P04-PCB-R2.2.zip`.** Zawiera wyłącznie 6 warstw Gerber X2 i 2 pliki wierceń Excellon. Parametry: `SPECYFIKACJA-DLA-PRODUCENTA.txt`; zamówienie w Satland krok po kroku: `../Zamowienie-Satland/INSTRUKCJA-SATLAND.md`.

| Parametr | Ustawienie |
|---|---|
| Wymiary | **160 × 120 mm** |
| Warstwy | 2 |
| Laminat | FR4; projekt 1,6 mm, w Satlandzie wybrać 1,5 mm |
| Miedź | **35 µm na każdej stronie** |
| Wykończenie | HAL |
| Maska | zielona, obie strony |
| Opis | biały, **tylko góra** (dolny opis w projekcie jest pusty) |
| Otwory | 450 PTH (w tym 101 przelotek), 12 NPTH; wiertła 0,4–3,2 mm; bez szczelin |
| Najwęższa ścieżka / najmniejszy odstęp (reguła) | 0,3 mm / 0,25 mm; miedź–krawędź ≥ 0,5 mm |
| Najmniejszy pierścień (z geometrii) | ≥ 0,2 mm (przelotki 0,2 mm, pola 0,35 mm) |

Kontrole: DRC KiCad 10.0.6 ze świeżym wypełnieniem stref i zgodnością ze schematem — **0 naruszeń, 0 niepołączonych, 0 rozbieżności**. Kontrola CAM własnym parserem Gerber/Excellon: **20/20** (każdy otwór, każde pole z siecią, otwarcia maski, obrys, liczba konturów wylewek). Próby ujemne kontroli CAM: **8/8 wykryte**, próba zerowa przechodzi. Oględziny podglądów wygenerowanych z samych plików CAM. 

**Przymiarka rzeczywistych części, próby elektryczne i cieplne: NIE ZBADANO.** To wydanie plików do wykonania prototypu, nie odbiór działającej płytki. Wydruk 1:1: `projekt/output/pdf/P04-R2.2-PCB.pdf` (skala 100 %, zmierzyć belkę 100 mm i obrys). Formularz odbioru: `projekt/docs/ODBIOR.md`.

| Ścieżka | Zawartość |
|---|---|
| `DO-ZAMOWIENIA_P04-PCB-R2.2.zip` (+ `.sha256`) | jedyny plik dla producenta |
| `gerber/` | te same pliki co w ZIP |
| `podglad/CAM-top.png`, `CAM-bottom.png` | wygląd wynikający z Gerberów; spód oglądany od spodu |
| `podglad/CAM-kontrola-warstw.png` | zestawienie warstw |
| `verification/QA.md` | zakres kontroli i odtworzenie |
| `projekt/` | kopia wydania P04-R2.2-review (KiCad, dokumentacja, BOM) |
| `src/` | eksport, kontrola CAM, próby ujemne, zamknięcie paczki |

Montaż: `projekt/docs/MECHANIKA.md`; R17 = 10 kΩ (nie 100 kΩ jak w R2.1). Adaptery U8–U10 (Kamami SO14) stoją na listwach żeńskich 1×7. Odbiór płytki na stanowisku P00: `projekt/docs/P00-P04.md` i `projekt/docs/ODBIOR.md`.
