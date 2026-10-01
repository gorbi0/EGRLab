# Wiązki P06-R2

*R2 (1.10.2026, S1): W1 LV06 i W2 ILOG zastąpione przez J_BP i taśmę IDC 2×8 do P12 (ok. 30 mm, S1 §5). Zostają W3 ISERIES oraz W4/W5 do przełącznika BYPASS na panelu (S1 §5: prąd silnika i elementy panelu przewodami). Wszystkie trzy końce od strony P06 lutowane w PTH przy brzegu x = 0.*

Pinout zawsze według numerów; prostokątny pad oznacza pin 1. Długości między końcem lutowania a czołem wtyku lub oczkiem; zostawić łagodny łuk serwisowy. Przewody przechodzą po górze PCB do kotwy, opaska obejmuje izolację 12 mm od rzędu lutów. Nie zalewać cyną odcinka pracującego przy opasce.

| ID / PCB | Koniec P06 | Drugi koniec | Długość / materiał |
|---|---|---|---|
| W3 / J3 ISERIES | lutowane piny 1 i 2 (2 pola, od 1.10), otwory 2,4 mm | MSTB 2,5/4-ST-5,08 do P11/J_ISERIESA (pozycje 3/4 puste) — do potwierdzenia z P11 w S1 | 150 mm; 2 × linka 2,5 mm² (długość sprawdzić na makiecie stosu) |
| W4 / J4 SW1-A | PTH 1/2, otwory 2,4 mm | lutowane do oczek SW1.2 / SW1.3, koszulki termokurczliwe | 100 mm; 2 × 2,5 mm² |
| W5 / J5 SW1-B | PTH 1/2/3, otwory 1,1 mm | lutowane do SW1.4 / SW1.5 / SW1.6, osobny splot | 150 mm; 3 × AWG22 |

| Złącze | Numeracja |
|---|---|
| J3 | 1 ECU_P1; 2 EGR_P1; 3 NC; 4 NC |
| J4 | 1 ECU_P1 → SW1.2; 2 EGR_P1 → SW1.3 |
| J5 | 1 5VA_P06 → SW1.4; 2 SW_RAW → SW1.5; 3 GND → SW1.6 |
| J_BP (taśma do P12) | 2 ADC_SCLK; 4 ADC_DOUTA; 6 CS_ILOG_N; 8 LOGGER_CURRENT_OK; 10/12 5V_SYS; 14 3V3_IO; nieparzyste i 16 GND |

Numery SW1 to numeracja schematu (wspólne 2 i 5). Przełącznik inny niż S6A może mieć inne numery oczek — przed lutowaniem W4/W5 ustalić wspólne oczka i położenia omomierzem (ODBIOR E03) i opisać przewody. Wiązka prądowa (W3/W4) oddzielona od taśmy J_BP i od W5. Nie umieszczać żadnego złącza między polami Kelvina RSH1 a INA240. P11 w S1 jeszcze nie istnieje — przed wykonaniem W3 sprawdzić jego odpowiednik i stronę połączenia. Najpierw sprawdzić ciągłość każdej żyły bez podłączonego ECU.
