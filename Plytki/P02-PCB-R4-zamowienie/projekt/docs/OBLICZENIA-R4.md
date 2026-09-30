# P02 R4 — obliczenia do schematu (etap 1)

*29.09.2026. Wszystkie liczby liczy `src/check_electrical.py` z wartości w wyeksportowanej netliście (`verification/P02.xml`); wynik w `verification/electrical-checks.json`. Modele są analityczne, a sprzęt nie jest jeszcze sprawdzony.*

## Założenia

| Wielkość | Wartość w obliczeniach | Źródło |
|---|---|---|
| REF (TL431BILP) | 2,483–2,507 V ± 17 mV dryftu ± 4 mV od prądu katody | karta TI, jak P02 R3 |
| LM2903 | Vos ± 15 mV, Ib ≤ 250 nA, górna granica CM = V+ − 2 V | karta TI (pełny zakres temperatur) |
| AUX5 (LM2936Z-5.0) | 4,85–5,15 V | ± 3 % |
| Rezystory MFR-50 | 1 % + 100 ppm/K × 25 K | jak P01 R3 |
| Wyjście OK | niski stan 0–0,4 V; wysoki = AUX5 − spadek na R13 od obciążeń (R11, R6+R7, R14 → Q6) | nowe w R4 |
| Q2 (Q_OFF), wejście bramki | typ. Ciss 3,5 nF; model P01 R3: 10 nF + 30 % Millera (13 nF), narożnik 20 nF (26 nF); Vth 1–3 V | `P01-R3-review/src/dynamics.py` |
| Diody STPS20100CT | D_ch 0,25–0,30 V (ok. 1,6 mA), D1b 0,45–0,50 V (0,5–0,8 A) | szacunek z karty ST |
| TSR 2-2450/2-2433 | praca do VLOG = 7,0 V | jak R3 |

## UVLO (U2B, R5 + PWR + R9, R10, C13, R12, R11)

| | Nominalnie | Obwiednia 512 narożników | Specyfikacja (Z-02) |
|---|---|---|---|
| Załączenie | 13,50 V | 12,90–14,08 V | 13,53 ± 0,34 V |
| Wyłączenie | 12,55 V | 11,98–13,11 V | 12,51 ± 0,34 V |
| Histereza | 0,95 V | 0,84–1,05 V | ok. 1 V (D-05) |

Wartości nominalne zgadzają się ze STAN-PRAC w granicach 0,05 V. Różnica wynika z tego, że OK w stanie wysokim ma ok. 4,84 V, a nie 5,0 V (R13 2,2 kΩ zasila też R14 → Q6 i dzielnik R6/R7).

**Rozrzut jest większy niż ± 0,34 V ze specyfikacji.** Specyfikacja liczyła tylko tolerancję TL431B (0,5 %) i rezystorów (1 %). Obliczenia R4 dodają dryft TL431, offset LM2903 w pełnym zakresie temperatur i tolerancję AUX5. Wymagania funkcjonalne są spełnione we wszystkich narożnikach: pakiet 3S (12,6 V) nie wystartuje (najniższy próg załączenia to 12,90 V), odpoczywający 4S przy 3,6 V/ogniwo (14,4 V) wystartuje zawsze, a wyłączenie następuje przy co najmniej 11,98 V, czyli ok. 3,0 V na ogniwo, powyżej odcięcia BMS.

Rozwarcie PWR: stała czasowa filtra UV_DIV wynosi 79 µs, a zadziałanie następuje ok. 22 µs po rozwarciu przy pełnym pakiecie. Dzielnik pobiera 0,32 mA przy 16,8 V.

## PFAIL_N (U2A) — odstępstwo od dosłownego brzmienia D-06

D-06 mówi: „druga sekcja LM2903 daje PFAIL_N z tego samego węzła co UVLO”. Gdyby U2A porównywała UV_CMP z REF tak jak U2B, obie sekcje przełączałyby się przy progach różniących się o offset (do 2 × 15 mV na UV_CMP, czyli do ok. 0,16 V na pakiecie), a histerezę ma tylko U2B (R11 z OK):

- jeśli U2A przełącza się pierwsza przy opadaniu, PFAIL_N może drgać bez histerezy, choć Q1 dalej przewodzi;
- jeśli druga, to przy odbiciu napięcia pakietu po zdjęciu obciążenia (4 A silnika to ok. 1 V spadku na pakiecie) PFAIL_N może wrócić na H, gdy Q1 jest już wyłączony i trwa podtrzymanie. Firmware uznałby wtedy zasilanie za przywrócone.

**W R4 U2A buforuje wyjście OK:** wejście + dostaje 0,6 × OK (R6 100 kΩ, R7 150 kΩ), wejście − REF. PFAIL_N jest więc z definicji tym samym stanem co ENABLE, łącznie z resetem U4 przy starcie AUX5, i nadal pochodzi z drugiej sekcji LM2903. Zapas: 0,23 V w stanie wysokim (najgorszy narożnik: AUX5 4,85 V, OK 4,70 V) i 2,19 V w niskim. REF (≤ 2,53 V) leży w zakresie wspólnym (≤ 2,85 V), co wystarcza, by wyjście było poprawne także wtedy, gdy PF_IN wychodzi ponad zakres. Zbocze PFAIL_N następuje w ok. 5 µs od zmiany OK (wymaganie Z-09: ≤ 100 µs). Wariant dosłowny jest próbą ujemną `pfail_from_uv_cmp_literal_D06`.

## Wyłączanie Q1 z R23 = 22 kΩ

Sekwencja po utracie ENABLE: Q5 i Q4 wychodzą z nasycenia, potem bramka Q2 (OFF_G) opada od SW_COM w stronę SW_COM × R24/(R23 + R24) ze stałą czasową (R23 ∥ R24) × C_we. Gdy Q2 osiąga VSG potrzebne do przewodzenia, rozładowuje C6 (1 µF) przez R27 10 Ω od VSG_on ≈ 0,82 × SW_COM do 0,5 V.

Kalibracja modelu: dla wartości P01 R3 (R23 = 2,2 kΩ, 17 V) model daje 40 i 58 µs, a ngspice z P01 R3 dał 43 i 64 µs. Model zaniża wynik o 6–9 %.

| SW_COM | Ciss typ. 3,5 nF | model P01, wartości nominalne | model P01, narożnik |
|---|---|---|---|
| 12,5 V | 44 µs | 71 µs | 239 µs |
| 16,8 V | 45 µs | 64 µs | 184 µs |

Po korekcie o zaniżenie modelu najgorszy przypadek to ok. 265 µs, wobec 43–64 µs w P01 R3 z R23 = 2,2 kΩ. Szacunek „ok. 55 µs” ze STAN-PRAC odpowiada typowej Ciss z karty katalogowej. Model P01 z pojemnością zastępczą ładunku bramki daje 64–71 µs nominalnie i do ok. 240 µs w narożniku.

Skutki: przy pakiecie nie ma OVP, a PFAIL_N nie zależy od R23 (idzie z U2A). Opóźnienie przesuwa tylko chwilę otwarcia Q1 o ułamek milisekundy, a przejście Q1 przez zakres liniowy nadal ustala szybkie rozładowanie C6 przez R27. Straty stałe R23 (gdy Q4 przewodzi): 13 mW.

## Załączanie: narastanie VSW i prąd ładowania

Na plateau Millera Q1: `dVSW/dt = [(VS − Vpl − 0,1)/R21 − Vpl/R22] / (C5 + Crss)`. Prąd kondensatorów to C × dV/dt. C_H ładuje się rampą przez R40, więc `I_CH(T) = a·C_H·(1 − e^(−T/τ))`. Energia w Q1 to ½·C·VS² dla pojemności, VS³/(6·a·R40) dla toru C_H i całka obciążenia 6 W od VLOG = 7 V.

| Przypadek | dV/dt | Rampa | I pojemności (220 µF) | I C_H | I logiki | I szczyt | Energia w Q1 |
|---|---|---|---|---|---|---|---|
| nominalnie, 16,8 V (Vpl 4 V) | 11,5 V/ms | 1,46 ms | 2,53 A | 0,79 A | 0,37 A | 3,69 A | 37 mJ |
| szybki narożnik, 16,8 V (Vpl 2 V, C5 −5 %) | 14,7 V/ms | 1,14 ms | 3,24 A | 0,80 A | 0,37 A | 4,40 A | 35 mJ |
| wolny narożnik, 13,2 V (Vpl 5 V, Crss 2 nF) | 5,6 V/ms | 2,38 ms | 1,22 A | 0,62 A | 0,47 A | 2,31 A | 25 mJ |

Z-07 (≤ ok. 3 A przy 220 µF): 2,53 A nominalnie, a w szybkim narożniku 3,24 A. O-04 (5–15 V/ms) jest spełnione we wszystkich trzech przypadkach. Energia pozostaje poniżej 137 mJ, które przyjęto w symulacji startu P01 R3.

Budżet pojemności Z-06: przez Q1 załączane są C3 47 µF na VSW oraz, przez D1a, C20 22 µF, C21 10 µF i C23 10 µF, łącznie 89 µF. Na wejście P07 zostaje 131 µF w limicie 220 µF. C_H nie wlicza się do limitu, bo ładuje się przez R40.

Ładowanie C_H przez R40 = 22 Ω: stała czasowa 48 ms, prąd szczytowy 0,76 A, energia w R40 0,31 J przy każdym załączeniu. Zwarty C_H oznaczałby 12,8 W ciągle w R40, dlatego R40 musi być rezystorem bezpiecznikowym.

## Udar przy wpięciu XT60 (reguła z P01 R1)

Skok SW_COM o 25 V daje VSG(Q1) = 25 × C5/(C5 + C6 + Ciss) = 0,29 V (C5 +5 %, C6 −10 %, Ciss 2 nF). Granica z P01: 0,8 V.

## Podtrzymanie po PFAIL_N (C12 = C_H 2200 µF)

W chwili zadziałania UVLO C_H ma napięcie VSW minus spadek na D_ch (prąd rezystora rozładowującego), a do VLOG oddaje energię przez D1b. VLOG spada do 7,0 V.

| Przypadek | V0 | 6 W | 3 W |
|---|---|---|---|
| nominalnie (C nominalne, wyłączenie 12,55 V, Vf 0,25 + 0,45 V) | 11,85 V | 16,8 ms | 33,5 ms |
| metoda specyfikacji (C −20 %, jedna dioda 0,45 V) | 12,10 V | 14,3 ms | 28,6 ms |
| **najgorszy (C −20 %, wyłączenie 11,98 V, Vf 0,30 + 0,50 V)** | 11,18 V | **11,1 ms** | **22,3 ms** |
| wyłączenie PWR przy 16,8 V (C −20 %) | 16,0 V | 30,4 ms | 60,7 ms |

**Z-08 (≥ 14 ms przy 6 W i ≥ 28 ms przy 3 W) jest spełnione metodą specyfikacji, ale nie w najgorszym narożniku.** Specyfikacja nie uwzględniła spadku na D_ch ani rozrzutu progu wyłączenia. Budżet firmware z sekcji 9 specyfikacji (domknięcie pliku ≤ 10 ms) jest spełniony w każdym przypadku (kontrola H01). Do decyzji: przyjąć ≥ 11 ms albo dać C_H 3300 µF / 35 V, co daje ok. 16,7 ms w najgorszym narożniku i wymaga większego obrysu.

## Straty i znamionowe napięcia

- Q1 i Q9, każdy bez radiatora: 0,37 W przy 3,5 A, 0,75 W przy 5 A (Tj ok. 96 °C przy 50 °C otoczenia).
- R5: zwarcie przewodu PWR do masy daje 286 mW (MFR-50 0,5 W).
- R1 47 Ω (w P01 150 Ω/2 W): AUX5 stabilizuje do VLOG ≈ 6,5 V (dropout LM2936 ok. 0,4 V); przy VLOG = 7 V wejście LM2936 ma 5,89 V.
- Z-14: każda część na sieciach pakietu ma ≥ 25 V poza zaciskami (Zenery BZX55C15, TVS) i zakończeniami przewodów.
- **Z-01 (bez uszkodzeń przy 0–25 V) jest sprzeczne z 5KP18A na VSW** (VBR min 20 V, więc stałe 25 V wprowadza TVS w przebicie). Pakiet 5S (21 V) jest na granicy, bo 21 V to więcej niż VBR min. Do decyzji: zawęzić Z-01 do 21 V albo przejść na 5KP20A (VWM 20 V, VBR min 22,2 V).

## VBAT auta (J15 → R38 → J11)

Mnożnik CH7 zmienia się z 6,0898 na 6,1918 (+1,67 %), zakres ± 61,9 V, konieczna kalibracja. Przy napięciu ograniczania P6KE24CA (33,2 V) przetwornik widzi 5,36 V.

## Symulacja ngspice

Nie jest dołączona. Testbench P01 R3 (`dynamics.py`) ma w kodzie nazwy sieci P01 (`p01_vs`, `p01_gate`, `vprot`, `p01_enable`, `p01_off_base`), plik `verification/P01.xml` i referencję `reference/R1-P01.xml`. Na netliście R4 nie uruchomi się bez przepisania, więc zgodnie z poleceniem pominięty. Biblioteka ngspice w obrazie działa (krok 0), a model analityczny wyłączania skalibrowano na wynikach ngspice P01 R3 (patrz wyżej).
