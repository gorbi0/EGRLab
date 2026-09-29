# P00-R3 — wykaz części

Ilości na jeden egzemplarz, bez zapasu. To pełny BOM zakupowy, bez odliczania stanu magazynu. Szczegóły oznaczeń: `BOM.csv`. Wartości i MPN są takie same jak w R2. Już kupione rezystory MF0207 1 % o tych samych wartościach i wymiarach też pasują; kody MFR poniżej to rodzina odniesienia.

| Nazwa / typ | Ilość szt. |
|---|---:|
| PCB P00-R3, 115 × 70 mm, 2 warstwy | 1 |
| TLC555CP, DIP8 | 1 |
| Podstawka DIP8, rozstaw rzędów 7,62 mm | 1 |
| LM2937ET-3.3/NOPB, TO-220 | 1 |
| 1N5819, DO-41 | 1 |
| Würth 450301014042, SPDT ON-ON | 9 |
| Listwa goldpin 1×02, 2,54 mm (albo odcinki listwy 1×40) | 9 |
| Phoenix 1715721, MKDS 1,5/2-5,08 | 1 |
| LED zielona 3 mm Kingbright L-934GD | 8 |
| LED żółta 3 mm Kingbright L-934YD | 1 |
| LED czerwona 3 mm Kingbright L-934ID | 1 |
| Rezystor 1 kΩ, 1 %, 0,25 W, MFR-25FRF52-1K | 19 |
| Rezystor 4,7 kΩ, 1 %, 0,25 W, MFR-25FRF52-4K7 | 1 |
| Rezystor 68 kΩ, 1 %, 0,25 W, MFR-25FRF52-68K | 1 |
| Rezystor 100 kΩ, 1 %, 0,25 W, MFR-25FRF52-100K | 1 |
| Rezystor 560 Ω, 1 %, 0,25 W, MFR-25FRF52-560R (R5) | 1 |
| Rezystor 1 Ω, 0,25 W, korpus 0207 (R6; tolerancja 1–5 % bez znaczenia), np. MFR-25FRF52-1R | 1 |
| 100 nF X7R, Vishay K104K15X7RF53H5, P5 | 4 |
| 10 nF X7R, Vishay K103K15X7RF53H5, P5 | 1 |
| 10 µF / 50 V, Panasonic EEUFR1H100, D5 / P2 | 1 |
| 22 µF / 50 V, Panasonic EEUFR1H220, D5 / P2 (C6) | 1 |
| Dystans/nóżka M3 | 4 |
| Śruba M3 i podkładka, dobrane do dystansu | 4 komplety |

TP1–TP3 to pola PCB, bez pinów do kupienia. Nie kupować błędnego C6 EEUFR1C220 z R1.

Na liście `Zamowione/ZAMOWIONE.md` (zamówienie P01 z 24.09) są sztuki ponad BOM P01, zgodne z tą listą: EEUFR1H220 1 szt., L-934GD 1 szt., MF0207FTE-1R 1 szt. (1 Ω, korpus 0207). Jest też K104K15X7RF5TH5 2 szt. — inny kod wyprowadzeń niż …53H5 w tym BOM.

## Wyposażenie wiązki do P04-R2.1 (osobno od PCB)

Połączenia i użycie w próbach opisuje `P00-P04-WIAZKA.md`. To wyposażenie stanowiska, nie elementy PCB P00 ani P04.

| Pozycja | Ilość | Uwagi |
|---|---:|---|
| Rezystor 1 kΩ / 1 % / 0,25 W | 5 | H_SUP, H_MCU, H_HB, H_PWM, H_SENSOR; izolowane i opisane |
| Zworka lub przełącznik rozłączający gałąź | 4 | H_SUP, H_MCU, H_PWM, H_SENSOR |
| Listwa 1×3, 2,54 mm + zworka | 1 | wybierak HB: J9.1 P00 albo H_HB |
| Przycisk NO chwilowy | 2 | ARM (J8.9–J8.10), SAFE_N_TEST (J7.2–J7.3) |
| Styk NC (przycisk NC albo zworka) | 1 | STOP (J8.1–J8.7) |
| Gniazdo IDC 2,54 mm, 16 poz. + taśma | 1 | J2; np. Würth 61201623021 jak w P04 |
| Gniazdo IDC 10 poz. + taśma | 1 | J3 |
| Gniazdo IDC 6 poz. + taśma | 3 | J4, J5, J6 |
| Mini-Fit Jr: obudowa żeńska 6 poz. + styki | 1 + 6 | J7 |
| Mini-Fit Jr: obudowa żeńska 10 poz. + styki | 1 + 10 | J8 |
| Mini-Fit Jr: obudowa żeńska 4 poz. + styki | 1 + 4 | J1, zasilanie P04 3,3 V (jak H_LV04: 39-01-2040, styki 39-00-0074) |
| Przewody z żeńskim Dupont 2,54 mm, do 20 cm | ok. 25 | strona P00 |

Numery katalogowe obudów IDC 10/6 poz. i Mini-Fit 6/10 poz. dobrać przy zakupie do rodzin użytych w P04. W adapterach testowych zaślepki kluczy nie są potrzebne.
