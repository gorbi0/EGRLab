# Odbiór P03-R6 — formularz

*R6 (format S1): złącza J_BP1–3 zamiast J1–J10, wejście PFAIL_N, listwy serwisowe J_SV1–3 na krawędzi B. Nowe próby oznaczone „R6”. Próby resetu, zasilania i SPI jak w R5, z nowymi numerami pinów. Punkty dostępne na listwach serwisowych podano jako J_SVn.p (przez rezystor 1 kΩ albo 10 kΩ, multimetr i sonda ×10 mierzą bez zauważalnego błędu; stała czasowa z sondą 15 pF: 15 ns przez 1 kΩ, 150 ns przez 10 kΩ).*

Wyniki sprzętowe: **NIE ZBADANO**. Wypełnić datę, rewizje modułów, przyrząd, przebiegi, wynik oraz odchylenia. Pierwsze próby bez ECU i zaworu.

| Próba | Oczekiwany wynik | Wynik / dowód |
|---|---|---|
| Przymiarka wydruku 1:1 (R6) | Obrys L 160 × 100, 12 otworów M3, listwy M1 22,86 mm, SD, J_BP w osiach slotów, J_SV w pasie x = 10–43 mm; wysokość M1 na listwach ≤ 16,5 mm | NIE ZBADANO |
| Ciągłość J_BP (R6) | Każdy pin J_BP1–3 zgodny z `docs/J_BP.csv` (omomierz od pinu do węzła na P03); nieparzyste GND zwarte z masą poza wyjątkami | NIE ZBADANO |
| Listwy serwisowe (R6) | Pin 1 i 13 każdej J_SV = GND; każdy inny pin: rezystancja do węzła zgodna z `docs/SERWIS.csv` (1 kΩ / 10 kΩ ± 1 %); zwarcie sąsiednich kołków nie resetuje CORE | NIE ZBADANO |
| Kontrola montażu U3/U4/U5/U6/Q1 | Numery pinów zgodne ze schematem; U3 SOT-23-6 i U5 TSOT-23-6 niezamienione; U4 (LVC1G37) i U6 (LVC1G17) rozpoznane po oznaczeniu; D/S Q1 niezamienione | NIE ZBADANO |
| P02-only, USB-only, oba, oba odłączone | Zgodnie z tabelą w `ZASILANIE-RESET.md`; USB-only nie podnosi 5V_SYS (J_SV2.2) pod obciążeniem testowym | NIE ZBADANO |
| Spadek 5V_SYS na drodze P02 → P12 → P03 (R6) | Przy 0,8 A: 5V_SYS na P03 (J_SV2.2) ≥ 4,85 V; zapisać spadek na złączach | NIE ZBADANO |
| Prąd wsteczny USB→SYS | Przy 5V_SYS = 0 i aktywnym USB cel < 50 µA ustalonego prądu; impulsy zanotować osobno | NIE ZBADANO |
| SD + Wi-Fi, 30 min | 5V_M1 (J_SV2.12) ≥ 4,60 V, 3V3_CORE (J_SV1.4) stabilne; bez resetów; temperatury LDO/Q1 | NIE ZBADANO |
| Start bez firmware / bootloader / RESET przytrzymany | J_SV2: MEAS_EN (.5) = 0, ADC_RESET (.4) = 0, ADC_CONVST (.7) = 0, ADC_CS (.8) = 1, SD_CS (.10) = 1, CURRENT_CS_N (.3) = 1; J_SV1: CS_ITEST_N (.7) = 1, CS_ILOG_N (.8) = 1, MEAS_BANK (.5) = 0, MOTOR_INA/INB (.3/.2) = 0; J_SV3: TC1_CS (.9) = 1, TC2_CS (.8) = 1, MCU_ARM (.2) = 0 (30.09: grupy wg `docs/SERWIS.csv` po przydziale kołków według węzłów) | NIE ZBADANO |
| Zapad 3V3_CORE przez 3,07 V | SUP_RAW_N (J_SV2.11) i SUP_N (J_SV3.12, od 30.09) LOW; reset ESP i MCP; P04 rozbrojone | NIE ZBADANO |
| Wymuszenie SUP_N do GND | ESP i MCP restartują; IODIR/OLAT odtworzone, nowa sesja, wymagane ARM | NIE ZBADANO |
| Programowanie USB (R6: gniazdo od krawędzi B) | Przy złożonym stosie kabel USB wchodzi bez rozbierania; bootloader i flash działają, reset obejmuje MCP | NIE ZBADANO |
| Zbocze SUP_N_OUT na P04 | Jak w R5, na nowej drodze taśma 30 mm + P12 + taśma 30 mm: na P04 U9.5 jedno monotoniczne zbocze na przejście, ≤ 10 ns/V w całym obszarze 0,8–2,0 V, oba kierunki; szacunek R6 8,3 ns/V przy 30 pF (nie kryterium). Podać sondę i jej pojemność. SUP_N_P04 i SUP_OK bez serii impulsów; HW_ARMED i MOTOR_PERMIT stale L | NIE ZBADANO |
| CORE_LINK przez R14 1 kΩ | Na P04 ≥ 2,7 V przy zasilonym CORE; zwarcie J_BP3.13 do GND ≈ 3,3 mA, 3V3_CORE bez zapadu | NIE ZBADANO |
| SUP_N_OUT przez R41 | P04 odłączony, reset zwolniony: amperomierz J_BP3.12–GND 11–16 mA; po zdjęciu J_BP3.12 w H (≥ 3,0 V); przy wyłączonym CORE z 10 kΩ do GND w L (Ioff U6) | NIE ZBADANO |
| PFAIL_N bez P02 (R6) | J_BP2 odłączone: GPIO3 (M1 J1-13) i J_SV2.9 w H (≥ 3,0 V); firmware: zasilanie OK | NIE ZBADANO |
| PFAIL_N z P02 R4 (R6) | Włącznik PWR: po wyłączeniu zbocze na J1-13 w ≤ 100 µs; **napięcie L na J1-13 < 0,825 V** (zapisać VOL LM2903 na P02 i temperaturę; szacunek przy R43 100 kΩ: 0,43 V przy VOL 0,4 V, 0,73 V przy 0,7 V); po włączeniu H ≥ 2,5 V | NIE ZBADANO |
| PFAIL_N przy P02 bez zasilania (R6) | USB-only z podłączonym P12 i wyłączonym P02: J1-13 w L < 0,825 V (szacunek ok. 0,33 V: R43 100 kΩ wobec 11 kΩ do 3V3_IO = 0 V na P02; przy 10 kΩ było 1,7 V, stan nieokreślony); firmware w trybie tylko-USB ignoruje PFAIL_N | NIE ZBADANO |
| Kolejność P03/P05/P04: każdy pierwszy i ostatni | Brak niezamierzonego MEAS_EN/ruchu; nieprawidłowe pomiary odrzucane | NIE ZBADANO |
| Wypięcie każdej taśmy J_BP | Wejścia zgodne z `STANY-DOMYSLNE.csv`; brak danych nie zastępowany ważnym zerem | NIE ZBADANO |
| SPI na końcu P05 i P09 | Zgodne setup/hold, bez wielokrotnych przejść progów; dobór R36–R40 | NIE ZBADANO |
| Odłączenie SD / błąd zapisu | Obsługa błędu w aplikacji, brak deklaracji poprawnego zapisu | NIE ZBADANO |

Test zapadu realizować kontrolowanym źródłem/obciążeniem i pomiarem na module; nie zwierać wyjścia AMS1117 ani nie łączyć dwóch aktywnych źródeł 3,3 V.

Stan ADC_BUSY = 0 i ADC_DOUT = 0 przy wypiętym P05 jest tylko elektrycznym stanem domyślnym. Obecność AD7606B potwierdza sekwencja BUSY po CONVST. CAN_RX = 1 oznacza recessive, a nie obecność transceivera. ENA/B = 0 traktować jako FAULT/ABSENT.
