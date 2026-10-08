# M1 — pakiet do zamówienia PCB

Wydanie **08.10.2026**, źródło **M1-R1-review**. Plik płytki jest bajtowo zgodny z wydaniem R1. Jedna płytka LOGGER + TESTER (wariant M1), 4 warstwy JLC04161H-7628, 150 × 80 mm, otwory M3 w narożach, przewody lutowane do pól X1 przy górnej krawędzi, tor 7,5 A na wylewkach obu warstw zewnętrznych. Ścieżki 0,2 mm, przelotki 0,6 / 0,3 (moc 0,9 / 0,4). Części R25 i R27 (0R) są w BOM jako „nie montować” (DNP).

**Do producenta wgraj `DO-ZAMOWIENIA_M1-PCB-R1.zip`.** Zawiera wyłącznie 9 warstw Gerber X2 i 2 pliki wierceń Excellon. Parametry: `SPECYFIKACJA-DLA-PRODUCENTA.txt` (ustawienia dla JLCPCB i uwagi dla Satlandu).

| Parametr | Ustawienie |
|---|---|
| Wymiary | **150 × 80 mm**, narożniki R1 |
| Warstwy | 4 (JLC04161H-7628) |
| Laminat | FR4 1,6 mm (JLCPCB: 1.6 mm; w Satlandzie 1,5 mm) |
| Miedź | **35 µm na warstwach zewnętrznych, 15,2 µm na wewnętrznych** |
| Wykończenie | HAL |
| Maska | zielona, obie strony |
| Opis | biały, obie strony |
| Otwory | 253 PTH (w tym 149 przelotek), 16 NPTH; wiertła 0,3–3,2 mm; bez szczelin |
| Najwęższa ścieżka / najmniejszy odstęp (reguła) | 0,2 mm / 0,25 mm; miedź–krawędź ≥ 0,5 mm |
| Najmniejszy pierścień (z geometrii) | ≥ 0,15 mm (przelotki 0,15 mm, pola 0,3 mm) |

Kontrole: DRC KiCad 10.0.6 ze świeżym wypełnieniem stref i zgodnością ze schematem — **0 naruszeń, 0 niepołączonych, 0 rozbieżności**. Kontrola CAM własnym parserem Gerber/Excellon: **24/24** (każdy otwór, każde pole z siecią, otwarcia maski, obrys, liczba konturów wylewek). Próby ujemne kontroli CAM: **9/9 wykryte**, próba zerowa przechodzi. Oględziny podglądów wygenerowanych z samych plików CAM. 

**Przymiarka rzeczywistych części, próby elektryczne i cieplne: NIE ZBADANO.** To wydanie plików do wykonania prototypu, nie odbiór działającej płytki. Wydruk 1:1: `projekt/output/pdf/M1-R1-PCB.pdf` (skala 100 %, zmierzyć belkę 100 mm i obrys). Odbiór sprzętu: według README wydania (`projekt/README.md`).

| Ścieżka | Zawartość |
|---|---|
| `DO-ZAMOWIENIA_M1-PCB-R1.zip` (+ `.sha256`) | jedyny plik dla producenta |
| `gerber/` | te same pliki co w ZIP |
| `podglad/CAM-top.png`, `CAM-bottom.png` | wygląd wynikający z Gerberów; spód oglądany od spodu |
| `podglad/CAM-kontrola-warstw.png` | zestawienie warstw |
| `verification/QA.md` | zakres kontroli i odtworzenie |
| `projekt/` | kopia wydania M1-R1-review (KiCad, dokumentacja, BOM) |
| `src/` | eksport, kontrola CAM, próby ujemne, zamknięcie paczki |


