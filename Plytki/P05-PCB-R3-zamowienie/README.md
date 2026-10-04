# P05 — pakiet do zamówienia PCB

Wydanie **04.10.2026**, źródło **P05-R3-review**. Plik płytki jest bajtowo zgodny z wydaniem R3. Format S1, klasa 2/3 (sloty S1–S2 poziomu 3), DAQ. Płytka po niezależnej recenzji 2.10.2026 (dziewięć dróg powrotnych masy przyjętych jawnie, decyzja użytkownika 1) i zmianie schematu 2.10 (nóżki SW1 na GND, C35 10 µF). SW1: E-Switch 100 kątowy M6, tuleja B3 z gwintem i nakrętką na panel (decyzja 4.10). Wspólne zamówienie (decyzja 4.10.2026).

**Do producenta wgraj `DO-ZAMOWIENIA_P05-PCB-R3.zip`.** Zawiera wyłącznie 7 warstw Gerber X2 i 2 pliki wierceń Excellon. Parametry: `SPECYFIKACJA-DLA-PRODUCENTA.txt` (ustawienia dla JLCPCB i uwagi dla Satlandu).

| Parametr | Ustawienie |
|---|---|
| Wymiary | **106,5 × 100 mm**, narożniki R1 |
| Warstwy | 2 |
| Laminat | FR4 1,6 mm (JLCPCB: 1.6 mm; w Satlandzie 1,5 mm) |
| Miedź | **35 µm na każdej stronie** |
| Wykończenie | HAL |
| Maska | zielona, obie strony |
| Opis | biały, obie strony |
| Otwory | 362 PTH (w tym 198 przelotek), 12 NPTH; wiertła 0,4–3,2 mm; bez szczelin |
| Najwęższa ścieżka / najmniejszy odstęp (reguła) | 0,2 mm / 0,15 mm; miedź–krawędź ≥ 0,5 mm |
| Najmniejszy pierścień (z geometrii) | ≥ 0,25 mm (przelotki 0,25 mm, pola 0,35 mm) |

Kontrole: DRC KiCad 10.0.6 ze świeżym wypełnieniem stref i zgodnością ze schematem — **0 naruszeń, 0 niepołączonych, 0 rozbieżności**. Przyjęte zgłoszenia `lib_footprint_mismatch` (4) dotyczą wyłącznie części, którym skrypt nadruku wydania przyciął linie lub przesunął tekst (`drc-accepted.json`); KiCad porównuje je z nieprzyciętą kopią w bibliotece. Nie wpływa to na miedź ani otwory. Kontrola CAM własnym parserem Gerber/Excellon: **20/20** (każdy otwór, każde pole z siecią, otwarcia maski, obrys, liczba konturów wylewek). Próby ujemne kontroli CAM: **8/8 wykryte**, próba zerowa przechodzi. Oględziny podglądów wygenerowanych z samych plików CAM. 

**Przymiarka rzeczywistych części, próby elektryczne i cieplne: NIE ZBADANO.** To wydanie plików do wykonania prototypu, nie odbiór działającej płytki. Wydruk 1:1: `projekt/output/pdf/P05-R3-PCB.pdf` (skala 100 %, zmierzyć belkę 100 mm i obrys). Odbiór sprzętu: według README wydania (`projekt/README.md`, ODBIOR); footprint SW1 sprawdzić na wydruku 1:1 z próbką przełącznika.

| Ścieżka | Zawartość |
|---|---|
| `DO-ZAMOWIENIA_P05-PCB-R3.zip` (+ `.sha256`) | jedyny plik dla producenta |
| `gerber/` | te same pliki co w ZIP |
| `podglad/CAM-top.png`, `CAM-bottom.png` | wygląd wynikający z Gerberów; spód oglądany od spodu |
| `podglad/CAM-kontrola-warstw.png` | zestawienie warstw |
| `verification/QA.md` | zakres kontroli i odtworzenie |
| `projekt/` | kopia wydania P05-R3-review (KiCad, dokumentacja, BOM) |
| `src/` | eksport, kontrola CAM, próby ujemne, zamknięcie paczki |


