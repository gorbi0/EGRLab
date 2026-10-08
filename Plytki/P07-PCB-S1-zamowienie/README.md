# P07 — pakiet do zamówienia PCB

Wydanie **08.10.2026**, źródło **P07-S1-review**. Plik płytki jest bajtowo zgodny z wydaniem S1. Format S1, klasa 2/3 (sloty S2–S3 poziomu 5), 4 warstwy JLC04161H-7628, DRIVE pod moduł IBT-2 (2 × BTS7960B) poza stosem: KPWR, bocznik Kelvin + INA240, tor 10 A na wylewkach obu warstw zewnętrznych; końcówki przewodów J1 / J2 / J4 przy krawędzi x = 106,5, J3 na krawędzi B (decyzje 6.10 wieczorem / 7.10). Ścieżki sygnałowe 0,2 mm, przelotki 0,6 / 0,3 (moc 0,9 / 0,4). Wspólne zamówienie (decyzja 4.10.2026).

**Do producenta wgraj `DO-ZAMOWIENIA_P07-PCB-S1.zip`.** Zawiera wyłącznie 9 warstw Gerber X2 i 2 pliki wierceń Excellon. Parametry: `SPECYFIKACJA-DLA-PRODUCENTA.txt` (ustawienia dla JLCPCB i uwagi dla Satlandu).

| Parametr | Ustawienie |
|---|---|
| Wymiary | **106,5 × 100 mm**, narożniki R1 |
| Warstwy | 2 |
| Laminat | FR4 1,6 mm (JLCPCB: 1.6 mm; w Satlandzie 1,5 mm) |
| Miedź | **35 µm na każdej stronie** |
| Wykończenie | HAL |
| Maska | zielona, obie strony |
| Opis | biały, obie strony |
| Otwory | 360 PTH (w tym 270 przelotek), 16 NPTH; wiertła 0,3–3,2 mm; bez szczelin |
| Najwęższa ścieżka / najmniejszy odstęp (reguła) | 0,2 mm / 0,25 mm; miedź–krawędź ≥ 0,5 mm |
| Najmniejszy pierścień (z geometrii) | ≥ 0,15 mm (przelotki 0,15 mm, pola 0,35 mm) |

Kontrole: DRC KiCad 10.0.6 ze świeżym wypełnieniem stref i zgodnością ze schematem — **0 naruszeń, 0 niepołączonych, 0 rozbieżności**. Przyjęte zgłoszenia `lib_footprint_mismatch` (4) dotyczą wyłącznie części, którym skrypt nadruku wydania przyciął linie lub przesunął tekst (`drc-accepted.json`); KiCad porównuje je z nieprzyciętą kopią w bibliotece. Nie wpływa to na miedź ani otwory. Kontrola CAM własnym parserem Gerber/Excellon: **24/24** (każdy otwór, każde pole z siecią, otwarcia maski, obrys, liczba konturów wylewek). Próby ujemne kontroli CAM: **9/9 wykryte**, próba zerowa przechodzi. Oględziny podglądów wygenerowanych z samych plików CAM. 

**Przymiarka rzeczywistych części, próby elektryczne i cieplne: NIE ZBADANO.** To wydanie plików do wykonania prototypu, nie odbiór działającej płytki. Wydruk 1:1: `projekt/output/pdf/P07-S1-PCB.pdf` (skala 100 %, zmierzyć belkę 100 mm i obrys). Odbiór sprzętu: według README wydania (`projekt/README.md`); pomiary modułu D1 / E2 / E3 przy odbiorze.

| Ścieżka | Zawartość |
|---|---|
| `DO-ZAMOWIENIA_P07-PCB-S1.zip` (+ `.sha256`) | jedyny plik dla producenta |
| `gerber/` | te same pliki co w ZIP |
| `podglad/CAM-top.png`, `CAM-bottom.png` | wygląd wynikający z Gerberów; spód oglądany od spodu |
| `podglad/CAM-kontrola-warstw.png` | zestawienie warstw |
| `verification/QA.md` | zakres kontroli i odtworzenie |
| `projekt/` | kopia wydania P07-S1-review (KiCad, dokumentacja, BOM) |
| `src/` | eksport, kontrola CAM, próby ujemne, zamknięcie paczki |


