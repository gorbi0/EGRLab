# Odbiór P08-R2 — wyniki do wypełnienia

Formularz R1 (`P08-R1-review/verification/ODBIOR.md`) z punktami pomiarowymi przeniesionymi na listwę serwisową J2 (krawędź B, `docs/SERWIS.csv`). Kołki mierzyć względem GND na pinie 1 lub 13; każdy kołek idzie przez rezystor przy węźle (1 kΩ, TPS_EN 10 kΩ), więc multimetr 10 MΩ mierzy bez zauważalnego błędu, a sonda oscyloskopu ma stałą czasową ok. 15 ns (TPS_EN ok. 150 ns).

| Punkt R1 | R2 |
|---|---|
| TP1 5V_SYS, TP2 3V3_IO, TP3 GND | J2.2, J2.3; GND J2.1 / J2.13 |
| TP4 SUP3_N, TP5 SUP5_N | J2.4, J2.5 |
| TP10 SENSOR_OK, TP11 SENSOR_HEALTHY | J2.6, J2.7 |
| — (nowy) PERMIT_LOCAL (E10) | J2.8 |
| TP6 SENSOR_LOCAL, TP7 TPS_EN | J2.9, J2.10 (10 kΩ) |
| TP8 SENSOR_LIMITED, TP9 SENSOR_FAULT_LOCAL_N | J2.11, J2.12 |
| TP12 5V_SENSOR, TP13 AGND_SENSOR | **nie na listwie** — różnicowo na porcie TEST (para J4); zsunięta sonda przy GND ominęłaby styk powrotu K1 |
| SENSOR_PERMIT (podawane w E04, E10, E13) | J1.6 przez taśmę J_BP (na stole: gniazdo IDC 2×8 z wyprowadzeniami) |


Egzemplarz / data / osoba: ____________________. Wszystkie poniższe próby: **NIE ZBADANO**. Początkowo bez samochodu, EGR i P07. Zasilacz laboratoryjny z ograniczeniem prądu; sztuczne obciążenie rezystancyjne. Logować napięcia i przebiegi, a nie tylko wpis „działa”.

| ID | Próba i kryterium | Pomiar / wynik |
|---|---|---|
| M01 | Wydruk PCB 1:1 (53 × 100 mm, po layoucie). Przymierzyć U1, U4/U5, TO92, K1, podstawki DIP, J1 (IDC 2×8 kątowe) i J2 (goldpin kątowy 1×13, kołki ok. 6 mm za krawędzią B). K1: 3,2/2,2/2,2 mm. Strefy M3 Ø7 mm wolne. | NIE ZBADANO |
| M02 | Taśma J_BP ↔ P12: ciągłość pin po pinie według `docs/J_BP.csv` (piny 12/14 bez połączenia). Para J4 → port TEST: ciągłość, brak zwarcia AGND_SENSOR do GND i obudowy, test pociągnięcia za izolację po zamocowaniu opaską. | NIE ZBADANO |
| E01 | Bez zasilania: brak zwarć 5V–GND / 3V3–GND; odłączony J4.1 i J4.2 od torów wejściowych K1. R18 ≈10k między J4.1/J4.2. | NIE ZBADANO |
| E02 | Najpierw 5 V z limitem 50 mA, 3,3 V z limitem 15 mA, PERMIT=0. K1 wyłączony; TPS_EN ≤0,66 V; wyjście między J4.1/J4.2 ≤0,2 V po ustaleniu. Zanotować pobór każdej szyny. | NIE ZBADANO |
| E03 | Obie szyny poprawne, czekać ≥1,5 s. SENSOR_OK i HEALTHY HIGH, PERMIT=0: wyjście nadal wyłączone. Sprawdzić HIGH/LOW na rzeczywistych odbiornikach P04/P03. | NIE ZBADANO |
| E04 | Zwiększyć limit źródła 5 V do 200 mA. Po 750 ms stabilnej gotowości podać PERMIT=3,3 V. TPS_EN około 1,95 V, K1 zamknięty. Na J4 napięcie zbliżone do zmierzonego 5V_SYS. | NIE ZBADANO |
| E05 | Obciążenia 1k, 250R (≥0,25 W) i 100R (≥0,5 W). Zmierzyć wejście i wyjście różnicowo oraz spadek na obu stykach. Cel spadku kompletnej PCB przy 20 mA: <50 mV. | NIE ZBADANO |
| E06 | Krótkie impulsy obciążenia 33R/2W lub obciążenie elektroniczne: zmierzyć limit, oczekiwane obliczeniowo 99–139 mA. Prąd czujnika pomniejszony o prądy R17/R18. Wynik poza zakresem wymaga analizy części i układu. | NIE ZBADANO |
| E07 | Impuls zwarcia 10–20 ms na sztucznym obciążeniu. Oscyloskop: prąd, FAULT, HEALTHY, PERMIT, TPS_EN. FAULT po deglitch 5–10 ms, lokalne ograniczenie wcześniej. Nie wykonywać długich zwarć jako normalnego testu. | NIE ZBADANO |
| E08 | Z P03: przeciążenie i przerwanie linii SENSOR_HEALTHY (J1.10, taśma J_BP). CORE zatrzaskuje FAULT, cofa PERMIT i zatrzymuje test. Powrót HEALTHY nie wznawia testu sam. Zmierzyć całkowity czas od zwarcia do wycofania PERMIT i wpisać wynik. | NIE ZBADANO |
| E09 | Wycofać PERMIT. Zmierzyć TPS_EN, lokalny OUT oraz J4. U1 wyłącza, K1 zwalnia, R17 rozładowuje C2. Zmierzyć czas zwolnienia K1 z D1 oraz zanik J4 dla docelowego sensora. | NIE ZBADANO |
| E10 | Odłączyć SENSOR_PERMIT (J1.6) przy prawidłowych szynach. PERMIT_LOCAL i SENSOR_LOCAL LOW, wyjście wyłączone; READY nadal HIGH. | NIE ZBADANO |
| E11 | Osobno odłączyć 5 V, 3,3 V, oba. Wymusić wcześniej PERMIT=HIGH. Wyjście nie może zasilać obciążenia po zaniku 3,3 V, mimo pozostawienia 5 V. HEALTHY/READY LOW przy braku dowolnej szyny. | NIE ZBADANO |
| E12 | Powolne rampy i szybkie zaniki 3,3 V przy 5 V obecnym. U8 ma utrzymywać TPS_EN LOW podczas resetu, także w przejściu przez 2 V i 1 V. Szukać impulsów na J4. K1 może zachowywać się inaczej niż TPS; samo kliknięcie nie rozstrzyga. | NIE ZBADANO |
| E13 | P08 bez zasilania, P03/P04 zasilone, PERMIT HIGH. Zmierzyć napięcie martwej szyny i prądy I/O; brak zasilania wyjścia, odbiorniki widzą LOW. Powtórzyć z samym 5 V i samym 3,3 V. | NIE ZBADANO |
| E14 | Po powrocie zasilania zachować 750 ms stabilnej gotowości. Sprawdzić, że przypadkowy reset/powrót przewodu nie uruchamia wcześniej przerwanego TEST. | NIE ZBADANO |
| E15 | 4,75 / 5,25 V i granice 3,3 V, temperatury PCB 0 / 25 / 50°C, 100 cykli. Sprawdzić progi, pewne przyciąganie cewki i spadek TBD przy sterowaniu 3,3 V. | NIE ZBADANO |
| E16 | Dopiero zatwierdzony adapter i pinmap, wstępna identyfikacja przy limicie 20 mA. TEST z EGR, pomiar zasilania/pozycji, zaników i powtarzalności. | NIE ZBADANO |
| E17 | LOGGER: PERMIT=0, K1 otwarty. Włączyć i wyłączyć EGRLab przy działającym torze ECU↔EGR; brak podania z P08 zasilania na obwód ECU. | NIE ZBADANO |

Warunki zamknięcia płytki: recenzja schematu i tras, M01/M02 oraz udane E01–E15. Integracja z zaworem wymaga także E16/E17 i potwierdzonego wspólnego firmware. „ERC/DRC=0” nie wypełnia tych pól.
