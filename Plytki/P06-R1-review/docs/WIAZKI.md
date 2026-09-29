# Wiązki P06

Pinout zawsze według numerów, oglądanie złącza od strony kabla nie jest podstawą numeracji. Prostokątny pad oznacza pin 1. Długości mierzone między końcem lutowania a czołem wtyku; pozostawić łagodny łuk serwisowy. Przewody przechodzą po górze PCB do kotwy, a opaska obejmuje izolację, 12 mm od rzędu lutów (14,54 mm dla drugiego rzędu ILOG). Nie zalewać cyną odcinka pracującego przy opasce.

| ID / PCB | Koniec P06 | Drugi koniec | Długość / materiał |
|---|---|---|---|
| W1 / J1 LV06 | 4 × PTH, otwory 1,1 mm | Mini-Fit Jr 4p do P02/J6 (J_LV06A), styki Au AWG22 | 200 mm; 4 × AWG22 |
| W2 / J2 ILOG | 8 × PTH, otwory 0,8 mm; pin 2 NC | IDC 2×4 2,54 mm Au do P03/J2; pozycja 2 zablokowana | 100 mm; taśma 8 × AWG28, raster 1,27 mm |
| W3 / J3 ISERIES | lutowane wyłącznie piny 1 i 2, otwory 2,4 mm | MSTB 2,5/4-ST-5,08 do P11/J_ISERIESA; pozycje 3/4 puste | 150 mm; 2 × elastyczna miedź 2,5 mm² |
| W4 / J4 SW1-A | PTH 1/2, otwory 2,4 mm | lutowane do zacisków SW1.2 / SW1.3, koszulki termokurczliwe | 100 mm; 2 × 2,5 mm² |
| W5 / J5 SW1-B | PTH 1/2/3 | lutowane do SW1.4 / SW1.5 / SW1.6, osobny splot | 150 mm; 3 × AWG22 |

S6A ma oczka lutownicze. Nie kupować S6F (konektory wsuwane) jako automatycznego zamiennika tej wiązki. Nie zaciskać dużych przewodów razem z cienkimi w jednej końcówce. Wiązka prądowa ma pozostać oddzielona od ILOG. Nie umieszczać żadnego złącza pomiędzy RSH1 pinami Kelvina i INA240.

| Złącze | Numeracja |
|---|---|
| J1 | 1 5V_SYS; 2 GND; 3 3V3_IO tylko TP4; 4 GND |
| J2 | 1 SCLK; 2 NC/KEY; 3 DOUTA; 4 GND; 5 CS_ILOG_N; 6 GND; 7 LOGGER_CURRENT_OK; 8 GND |
| J3 | 1 ECU_P1; 2 EGR_P1; 3 NC; 4 NC |
| J4 | 1 ECU_P1 → SW1.2; 2 EGR_P1 → SW1.3 |
| J5 | 1 5VA → SW1.4; 2 SW_RAW → SW1.5; 3 GND → SW1.6 |

Wtyk IDC po stronie P03 jest jedynym rozłącznym końcem taśmy. Zaślepienie pozycji 2 należy wykonać na wtyku; nie traktować samego opisu KEY na płytce jako mechanicznego kodowania. P11 jeszcze nie jest zatwierdzoną płytką - przed wykonaniem W3 sprawdzić jego rzeczywisty odpowiednik i stronę połączenia. Najpierw sprawdzić ciągłość każdej żyły bez podłączonego ECU.

