# Odbiór P03-R3 — formularz

*R3: dodane próby „Zbocze SUP_N na P04” i „CORE_LINK przez R14 1 kΩ”; reszta jak w R2.*

Wyniki sprzętowe: **NIE ZBADANO**. Wypełnić datę, rewizje modułów, przyrząd, przebiegi, wynik oraz odchylenia. Pierwsze próby bez ECU i zaworu.

| Próba | Oczekiwany wynik | Wynik / dowód |
|---|---|---|
| Przymiarka wydruku 1:1 | Obrys, listwy M1 22,86 mm, SD, PA0085, adaptery LVC pasują | NIE ZBADANO |
| P03–P05 B2B | Zatwierdzone MPN, wysokości rzędów, dystanse i pełne zazębienie; ciągłość 1:1, klucz 2 | NIE ZBADANO |
| Kontrola montażu U4/U5/Q1 | Numery pinów zgodne ze schematem; D/S Q1 niezamienione, brak zwarć i mostków | NIE ZBADANO |
| P02-only, USB-only, oba, oba odłączone | Zgodnie z tabelą zasilania; USB-only nie podnosi 5V_SYS pod obciążeniem testowym | NIE ZBADANO |
| Prąd wsteczny USB→SYS | Zmierzyć przy 5V_SYS=0, USB aktywne; cel <50 µA ustalonego prądu, osobno zanotować impulsy | NIE ZBADANO |
| SD + używany tryb Wi-Fi, 30 min | 5V_M1 ≥4,60 V, 3V3_CORE stabilne; bez resetów; zmierzone temperatury LDO/Q1 | NIE ZBADANO |
| Start bez firmware / bootloader / RESET przytrzymany | MEAS_EN=0, ADC_RESET=0, CONVST=0, CS ADC/TC/ILOG/ITEST/SD nieaktywne | NIE ZBADANO |
| Zapad 3V3_CORE przez 3,07 V (bez zwarcia regulatora) | SUP_RAW_N i SUP_N LOW; reset ESP i MCP; P04 rozbrojone | NIE ZBADANO |
| Wymuszenie SUP_N do GND | ESP i MCP restartują; po zwolnieniu IODIR/OLAT odtworzone, nowa sesja, wymagane ARM | NIE ZBADANO |
| Programowanie USB/DTR/RTS | Wejście do bootloadera i flash działają, reset obejmuje MCP | NIE ZBADANO |
| Zbocze SUP_N na P04 (R3) | Oscyloskop na J4.15, SUP_N_P04 (P04 U9.6) i SUP_OK (P04 TP4) przy zwolnieniu i narzuceniu resetu CORE (przycisk RESET, zapad 3V3_CORE); zapisać przebiegi. Oczekiwane: HW_ARMED i MOTOR_PERMIT stale L w czasie przejścia; ewentualne serie impulsów SUP_OK opisać (czas, liczba). Łącznie z E16 P04 | NIE ZBADANO |
| CORE_LINK przez R14 1 kΩ (R3) | Na P04 J2.13 / R16 ≥ 2,7 V przy zasilonym CORE; zwarcie J4.13 do GND ≈ 3,3 mA, 3V3_CORE bez zapadu | NIE ZBADANO |
| Kolejność P03/P05/P04: każdy pierwszy i ostatni | Brak niezamierzonego MEAS_EN/ruchu; nieprawidłowe pomiary odrzucane | NIE ZBADANO |
| Wypięcie każdego modułu | Wejścia zgodne z STANY-DOMYSLNE.csv; brak danych nie zastępowany ważnym zerem | NIE ZBADANO |
| SPI na końcu P05 i P09, krótka sonda masowa | Zgodne setup/hold, bez wielokrotnych przejść progów; dobór R36–R40 | NIE ZBADANO |
| Odłączenie SD / błąd zapisu | Obsługa błędu w aplikacji, brak deklaracji poprawnego zapisu | NIE ZBADANO |

Test zapadu realizować kontrolowanym źródłem/obciążeniem i pomiarem na module; nie zwierać wyjścia AMS1117 ani nie łączyć dwóch aktywnych źródeł 3,3 V. Dla testu statycznego prądu wstecznego odłączyć pozostałe łącza sygnałowe, potem powtórzyć w kompletnym zestawie, aby rozdzielić tor mocy od zasilania przez sygnały.

Stan ADC_BUSY=0 i ADC_DOUT=0 przy wypiętym P05 jest tylko elektrycznym stanem domyślnym. Obecność AD7606B potwierdza sekwencja BUSY po CONVST oraz kontrola konfiguracji/testowego wzorca. Dla MCP3201 brak osobnego identyfikatora urządzenia: sam kod 0 nie dowodzi obecności; wykorzystać CURRENT_OK i procedurę odbioru. CAN_RX=1 oznacza recessive, a nie obecność transceivera. ENA/B=0 traktować jako FAULT/ABSENT; ostateczna diagnostyka zależy od wstrzymanego P07.
