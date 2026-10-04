# P12 — pakiet do zamówienia PCB

Wydanie **04.10.2026**, źródło **P12-R1-review**. Plik płytki jest bajtowo zgodny z wydaniem R1. Płytka połączeń krawędzi A formatu S1, wariant LOGGER: 10 prostych gniazd IDC (P02, P03 ×3, P05 ×2, P09, P06, P10, P11) i 4 pola pomiarowe, bez elementów aktywnych. Wspólne zamówienie z P02 R4, P03 R6, P05 R3, P06 R2, P09 R2 i P10 R2 (decyzja użytkownika 4.10.2026).

**Do producenta wgraj `DO-ZAMOWIENIA_P12-PCB-R1.zip`.** Zawiera wyłącznie 7 warstw Gerber X2 i 2 pliki wierceń Excellon. Parametry: `SPECYFIKACJA-DLA-PRODUCENTA.txt` (ustawienia dla JLCPCB i uwagi dla Satlandu).

| Parametr | Ustawienie |
|---|---|
| Wymiary | **160 × 92 mm**, narożniki R1 |
| Warstwy | 2 |
| Laminat | FR4 1,6 mm (JLCPCB: 1.6 mm; w Satlandzie 1,5 mm) |
| Miedź | **35 µm na każdej stronie** |
| Wykończenie | HAL |
| Maska | zielona, obie strony |
| Opis | biały, obie strony |
| Otwory | 233 PTH (w tym 57 przelotek), 6 NPTH; wiertła 0,4–3,2 mm; bez szczelin |
| Najwęższa ścieżka / najmniejszy odstęp (reguła) | 0,3 mm / 0,25 mm; miedź–krawędź ≥ 0,5 mm |
| Najmniejszy pierścień (z geometrii) | ≥ 0,25 mm (przelotki 0,25 mm, pola 0,35 mm) |

Kontrole: DRC KiCad 10.0.6 ze świeżym wypełnieniem stref i zgodnością ze schematem — **0 naruszeń, 0 niepołączonych, 0 rozbieżności**. Kontrola CAM własnym parserem Gerber/Excellon: **20/20** (każdy otwór, każde pole z siecią, otwarcia maski, obrys, liczba konturów wylewek). Próby ujemne kontroli CAM: **8/8 wykryte**, próba zerowa przechodzi. Oględziny podglądów wygenerowanych z samych plików CAM. 

**Przymiarka rzeczywistych części, próby elektryczne i cieplne: NIE ZBADANO.** To wydanie plików do wykonania prototypu, nie odbiór działającej płytki. Wydruk 1:1: `projekt/output/pdf/P12-R1-PCB.pdf` (skala 100 %, zmierzyć belkę 100 mm i obrys). Odbiór: przymiarka taśm i sprawdzenie ciągłości według README wydania (`projekt/README.md`, „Pytania”).

| Ścieżka | Zawartość |
|---|---|
| `DO-ZAMOWIENIA_P12-PCB-R1.zip` (+ `.sha256`) | jedyny plik dla producenta |
| `gerber/` | te same pliki co w ZIP |
| `podglad/CAM-top.png`, `CAM-bottom.png` | wygląd wynikający z Gerberów; spód oglądany od spodu |
| `podglad/CAM-kontrola-warstw.png` | zestawienie warstw |
| `verification/QA.md` | zakres kontroli i odtworzenie |
| `projekt/` | kopia wydania P12-R1-review (KiCad, dokumentacja, BOM) |
| `src/` | eksport, kontrola CAM, próby ujemne, zamknięcie paczki |

Montaż: gniazda IDC J1–J10 od strony F (strona stosu), klucz obudowy według nadruku, pin 1 (pole kwadratowe) od mniejszego x; wyprowadzenia od strony B przyciąć (P12 przykręcona dystansami M3 do ściany A).
