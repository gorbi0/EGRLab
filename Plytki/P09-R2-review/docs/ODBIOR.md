# Odbiór P09-R2 — NIE ZBADANO

Egzemplarz / data / wykonujący: __________. Rewizja / SHA256 pakietu: __________.

Punkty pomiarowe są na **listwie serwisowej J2** (krawędź B, dostępna po skręceniu stosu; kołki przez 1 kΩ). Numeracja kołków od strony większego x (patrząc od krawędzi B: od prawej; nazwa sygnału przy każdym kołku): 1 GND, 2 3V3_IO, 3 5V_SYS, 4 TC1_VIN, 5 TC2_VIN, 6 TC1_3VO, 7 TC2_3VO, 8 CS1_BUF, 9 CS2_BUF, 10 OE1_N, 11 OE2_N, 12 SPI3_MISO, 13 GND. Wejściowych SCLK/MOSI/CS z J_BP na listwie nie ma (mierzyć na listwie P03).

| Sprawdzenie | Kołek J2 / kryterium | Wynik |
|---|---|---|
| Moduły TC1/TC2 | Zdjęcia, napisy, numer partii; zgodność 9 pinów (bez kołka) | NIE ZBADANO |
| Przymiarka wydruku | Obrys 53 × 100 mm, otwory M3 slotu, J_BP przy krawędzi A, listwa przy B, obrys gniazd modułów, podparcie nylonowe | NIE ZBADANO |
| J_BP | Piny nieparzyste 1:1 z GND, parzyste wg `docs/J_BP.csv`, brak zwarć do sąsiadów | NIE ZBADANO |
| Listwa J2 | Rezystancja kołek–węzeł 1 kΩ dla kołków 2–12; kołki 1 i 13 = GND | NIE ZBADANO |
| Nośnik bez modułów | Kołki 2, 3: brak zwarć szyn, pobór 3,3 V i 5 V; kołki 8, 9: oba CS HIGH | NIE ZBADANO |
| TC1 VIN 3,3 V | Kołki 4 i 6: VIN i 3Vo, prąd przy minimalnej szynie i temperaturze | NIE ZBADANO |
| TC2 VIN 3,3 V | Kołki 5 i 7: VIN i 3Vo, prąd | NIE ZBADANO |
| Wariant VIN 5 V, jeśli potrzebny | Kołki 4/5 i 6/7: VDD 3,0–3,6 V i poziomy SPI zgodne; brak konfliktu na wyjściach U1 | NIE ZBADANO |
| Ostateczne JP1/JP2 | Wybrana szyna osobno, naklejki, tylko jedna zwora na selektor | NIE ZBADANO |
| MISO | Kołek 12 z kołkami 10, 11: TC1, TC2, oba HIGH, oba LOW; Hi-Z w stanach nieaktywnych | NIE ZBADANO |
| CS oscyloskop | Kołki 8, 9: setup/hold 2 takty przy 1 MHz; przerwa obu HIGH ≥ 1 µs | NIE ZBADANO |
| Zanik zasilania | Osobno P09/P03, kolejność 3,3 V/5 V, brownout; brak aktywnego MISO (kołek 12) przy martwej P09 | NIE ZBADANO |
| Konfiguracja | Odczyt CR0 = 91h / CR1 = 03h, pierwsza próbka po 300 ms | NIE ZBADANO |
| TC odłączona | Fault, NAN, poprawny zapis statusu | NIE ZBADANO |
| Moduł odłączony | Błąd konfiguracji/komunikacji, brak fikcyjnego 0 °C | NIE ZBADANO |
| Termometr odniesienia | Otoczenie, punkt ciepły, powrót; wpisać błędy TC1/TC2 | NIE ZBADANO |
| Zapis SD + obie TC | Ciągły zapis, brak konfliktu SPI, poprawne znaczniki odczytu | NIE ZBADANO |
| Powtarzalność mechaniczna sond | Stałe miejsce/docisk/izolowana spoina, zdjęcia montażu | NIE ZBADANO |
| HOT-SOAK | Bez ogrzewania P09; porównanie temperatur i logu EGR | NIE ZBADANO |

Żaden wynik CAD nie uzupełnia automatycznie tej tabeli. Odchyłki / działania / decyzja o użyciu: __________.
