# M1-R1 — paczka do recenzji (Astra)

*8.10.2026. Schemat, PCB, paczka do zamówienia i firmware: Claude. Recenzja: Astra. Źródło: gałąź `m1` repozytorium EGRLab (commit podany w `MANIFEST-RECENZJI.json` w ZIP-ie).*

## Co to jest M1

Wariant „jedna płytka” zamiast stosu S1 (11 płytek), dla świadomego użytkownika. Zakres funkcji jak S1 (LOGGER + TESTER zaworu EGR):
- AD7606B, 8 kanałów, w tym prąd silnika z INA240;
- 2 × MAX31856 (moduły);
- CAN tylko do odczytu;
- sterowanie modułem IBT-2 poza płytką;
- zasilanie czujnika przez TPS2553;
- ESP32-S3 DEV-KIT i moduł microSD;
- zasilanie z pakietu 4S z BMS przez TSR 2-2450 / 2-2433.

Przewody są lutowane do pól na płytce, w obudowie jest jedna listwa śrubowa X1, kable wychodzą przez mufy.

Decyzje użytkownika D-M1-1…13 (`Plytki/M1-specyfikacja/AUDYT.md`, `SPECYFIKACJA.md`) **są przyjęte i nie podlegają recenzji**. Dotyczy to:
- wycięcia zabezpieczeń S1 (SAFE, przekaźniki odczepów, UVLO, okno OC);
- IBT-2 poza płytką;
- **4 warstw** (wyjątek od dotychczasowej zasady 2 warstw);
- montażu ręcznego;
- modułów wlutowanych wprost;
- produkcji w JLCPCB.

Recenzja ocenia poprawność elektryczną, architekturę w tych ramach, PCB, pliki CAM i firmware. Nie ocenia kosztów ani zasadności wariantu.

**Status: pliki sprawdzone, sprzętu nie uruchamiano — przymiarka 1:1 i odbiór: NIE ZBADANO.**

## Zawartość ZIP (ścieżki jak w repozytorium)

| Ścieżka | Zawartość |
|---|---|
| `Plytki/M1-specyfikacja/` | audyt uproszczeń, decyzje, specyfikacja (kanały, GPIO, X1), zadania kroków 7–8, ten dokument |
| `Plytki/M1-R1-review/` | jeden generator (`src/parts.py`), schemat (7 arkuszy), PCB, łańcuch layoutu, kontrole, PDF-y (`output/pdf/M1-R1-schemat.pdf`, `M1-R1-PCB.pdf`) |
| `Plytki/M1-PCB-R1-zamowienie/` | paczka dla JLCPCB: `DO-ZAMOWIENIA_M1-PCB-R1.zip`, Gerbery, kontrola CAM, podglądy, specyfikacja dla producenta; `projekt/` = bajtowa kopia `M1-R1-review` |
| `Rewizje/EGRLab-v6.3-m1/` | firmware pod M1 (kopia 6.2-s1 zmieniona: M-01…M-13), testy, obrazy 5 wariantów |

Testy regresji firmware korzystają z `Rewizje/EGRLab-v6.1-rc1` i `Rewizje/EGRLab-v6.2-s1`. Tych katalogów nie ma w ZIP-ie, są w repozytorium.

## Wyniki kontroli (z plików weryfikacji)

| Etap | Wynik |
|---|---|
| Schemat (`M1-R1-review/verification/QA.md`) | ERC 0 na 7 arkuszach; netlista 357 pinów pin po pinie, 0 błędów; `verify_m1.py` 8/8 (X1, GPIO i piny zakazane, skale kanałów, tor prądu, bezpieczny start, wspólne MISO, budżet zasilania, sieci jednopinowe), mutacje 16/16 + zerowa |
| PCB (`QA-PCB.md`) | DRC 0 naruszeń / 0 niepołączonych / 0 niezgodności ze schematem; kontrole PCB 11/11, próby ujemne 13/13 z zerową |
| Paczka (`M1-PCB-R1-zamowienie/verification/`) | DRC 0/0/0 na kopii; CAM 24/24 (253 PTH, 16 NPTH); próby ujemne CAM 9/9 + zerowa; FABRICATION_FILES_VERIFIED; ZIP SHA-256 `824058fb…` |
| Firmware (`EGRLab-v6.3-m1/README.md`) | 5/5 kompilacji ESP-IDF 5.4.3 w chmurze; testy hosta C; Python 102 testy OK; próby mutacyjne 31/31 z zerową (testy i mutacje powtórzone lokalnie po recenzji) |

## Miejsca, które proszę sprawdzić szczególnie (moje znane ryzyka)

1. **Stany pinów ESP32-S3 w resecie.** W recenzji firmware znalazłem wadę płytki:
   - GPIO39 (MTCK) ma po resecie wewnętrzne podciąganie ok. 45 kΩ (karta v2.2, tab. 2-1, przypis 7);
   - przy 100 kΩ pull-down DRIVE_EN miał ok. 2,3 V, czyli stan wysoki dla 74AHCT125;
   - poprawka: R2 = 4,7 kΩ;
   - proszę sprawdzić tak samo pozostałe piny z pull-up / pull-down: GPIO1, 21, 40, 42, 15, 7, 8, 16, 10, 12, a także GPIO3 (pin strapujący, pole testowe).
2. **Tor prądu:**
   - INA240A2 z REF1 = 5 V / REF2 = GND, VS z TSR 2-2450 (szum i dokładność zera, zero zapisywane przez firmware);
   - zakres liniowy ok. ±9 A;
   - jeden tor dla LOGGER i TESTER (D-M1-7);
   - programowe ograniczenie 8 A po 2 próbkach (M-06, włączone decyzją użytkownika).
3. **Para Kelvina.** K_PLUS biegnie po F.Cu, K_MINUS dwiema przelotkami przez In2.Cu pod pasem P1_EGR (masa In1 między nimi). Pola pomiarowe WSK2512 leżą na przekątnej, więc jedna linia musi przejść pod torem prądowym. Proszę ocenić pętlę i sprzężenie.
4. **Otoczenie AD7606B przeniesione z P05 R3.** To samo ułożenie, przesunięcie +37 / −15 mm. Obejmuje:
   - 4 × 100 nF od spodu;
   - reguły 0,15 mm tylko w obrysie U3 (`eda/M1.kicad_dru`);
   - kolumnę filtrów 220 pF;
   - rezystory szeregowe w rzędach odcinków z P05.

   CH1 ma rezystor 300 k przy pasie P1_EGR, więc węzeł ADC_CH1 (ok. 74 k) jest długi: ok. 35 mm miedzi łącznie z odgałęzieniem do R12 i wejściem U3.
5. **Tor 7,5 A:**
   - wylewki 4 mm na F.Cu i B.Cu, 2–6 przelotek zszywających na sieć;
   - F1 MINI 7,5 A w oprawce lutowanej;
   - jedna masa na płytce; minus IBT-2 przez mostek X1.4 ↔ X1.2 na listwie (prąd silnika poza płytką);
   - pola przewodów połączone z wylewkami szprychami 2 mm.
6. **TPS2553:** R_ILIM 232 kΩ przeniesiony z P08 R2 (sprawdzić prąd ograniczenia); SENS_5V wchodzi do CH8 przez 100 k.
7. **MAX31856:**
   - moduły zasilane z 3,3 V (opcja 5 V przez R25 / R27 — DNP);
   - bufor 74LVC125 na SDO z OE = CS, bo moduł nie gwarantuje stanu Z;
   - termopary wchodzą wprost do zacisków modułów, nie przez X1.
8. **CAN:** TCAN1051V z TXD i S na stałe w VIO (tylko odbiór), PESD2CAN, bez terminatora 120 Ω (odczep na istniejącej magistrali, jak P10 R2).
9. **Rozmieszczenie:**
   - antena ESP32 w rogu, strefa bez miedzi na wszystkich warstwach;
   - USB-C, gniazdo microSD i zaciski termopar przy dolnej krawędzi;
   - pola X1 w kolejności zacisków przy górnej.

   Wysokości modułów w PDF PCB, strona 7, to szacunki.
10. **Nadruk:** 4 oznaczenia ukryte z braku miejsca (R32, C12, C29, C14), są na rysunku montażowym z F.Fab. Od spodu, między listwami ESP32, brak fragmentu wylewki GND (odcięta wyspa); In1 jest tam ciągła.
11. **Firmware:**
    - M-01…M-13;
    - brak PFAIL_N: przy zaniku zasilania ginie najwyżej ok. 1 s danych;
    - typ diody RGB na DEV-KIT (WS2812 na GPIO38) niepotwierdzony;
    - obrazy w `prebuilt/` zbudowane przed poprawką komentarza w `board.c`; zmiana tylko w komentarzu, w tej samej linii.
12. **Poprawka w trakcie:** `verify_m1.py` liczył z wejściem AD7606B 1 MΩ, a wersja B ma 5 MΩ (jak firmware 6.2-s1 F-03). Skale CH1/CH2 4,06, CH3–5/CH8 1,02, CH7 6,0898, CH6 1,0002.
13. **Producent:** pierścień przelotek 0,15 mm, czyli paczka tylko dla JLCPCB (Satland wymaga 0,20 mm).

## Odtworzenie

- Schemat, layout z zapisanego wyniku routera, nadruk, kontrole i PDF: z `Plytki/M1-R1-review` uruchomić `scripts/egrlab-docker python3 src/run_release.py`. KiCad 10.0.6 w obrazie `egrlab-kicad:10.0.6`; nowy przebieg routera: `--new-route`.
- Paczka: z `Plytki/M1-PCB-R1-zamowienie` uruchomić `src/copy_source.py`, `export_production.py`, `check_cam.py`, `cam_negative_controls.py`, `write_docs.py`, `seal_package.py`. Oględziny są zapisane w `verification/visual-review.json`.
- Firmware: polecenia w `Rewizje/EGRLab-v6.3-m1/README.md`, sekcja „Budowanie i testy”.

## Forma odpowiedzi

Jak w poprzednich recenzjach: `Plytki/M1-R1-recenzja-Astra/RECENZJA-M1-R1.md`. Każde zgłoszenie ma:
- ID (M1-01…);
- wagę (krytyczne / ważne / drobne);
- miejsce (ref, pin, sieć, plik i linię);
- dowód lub obliczenie;
- proponowaną zmianę.

Jeśli Astra wydaje własną rewizję, proszę o nowy katalog (np. `M1-R2-review`), bez zmian w `M1-R1-review`.
