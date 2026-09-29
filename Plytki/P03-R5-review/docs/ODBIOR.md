# Odbiór P03-R5 — formularz

*R4: próba zbocza na P04 dotyczy teraz wyjścia bufora U6 (SUP_N_OUT); dodane „Kontrola montażu U6/R41/C15” i „SUP_N_OUT przez R41”. R3: „CORE_LINK przez R14 1 kΩ”; reszta jak w R2.*

Wyniki sprzętowe: **NIE ZBADANO**. Wypełnić datę, rewizje modułów, przyrząd, przebiegi, wynik oraz odchylenia. Pierwsze próby bez ECU i zaworu.

| Próba | Oczekiwany wynik | Wynik / dowód |
|---|---|---|
| Przymiarka wydruku 1:1 | Obrys, listwy M1 22,86 mm, SD, PA0085, adaptery LVC pasują | NIE ZBADANO |
| P03–P05 B2B | Zatwierdzone MPN, wysokości rzędów, dystanse i pełne zazębienie; ciągłość 1:1, klucz 2 | NIE ZBADANO |
| Kontrola montażu U4/U5/Q1 | Numery pinów zgodne ze schematem; D/S Q1 niezamienione, brak zwarć i mostków | NIE ZBADANO |
| Kontrola montażu U6/R41/C15 (R4) | U4 (LVC1G37) i U6 (LVC1G17) to różne układy w tej samej obudowie SOT-23-5: oznaczenie na obudowie zgodne z kartą, pin 1 przy znaczniku; R41 = 220 Ω; brak mostków przy obudowie J4 | NIE ZBADANO |
| P02-only, USB-only, oba, oba odłączone | Zgodnie z tabelą zasilania; USB-only nie podnosi 5V_SYS pod obciążeniem testowym | NIE ZBADANO |
| Prąd wsteczny USB→SYS | Zmierzyć przy 5V_SYS=0, USB aktywne; cel <50 µA ustalonego prądu, osobno zanotować impulsy | NIE ZBADANO |
| SD + używany tryb Wi-Fi, 30 min | 5V_M1 ≥4,60 V, 3V3_CORE stabilne; bez resetów; zmierzone temperatury LDO/Q1 | NIE ZBADANO |
| Start bez firmware / bootloader / RESET przytrzymany | MEAS_EN=0, ADC_RESET=0, CONVST=0, CS ADC/TC/ILOG/ITEST/SD nieaktywne | NIE ZBADANO |
| Zapad 3V3_CORE przez 3,07 V (bez zwarcia regulatora) | SUP_RAW_N i SUP_N LOW; reset ESP i MCP; P04 rozbrojone | NIE ZBADANO |
| Wymuszenie SUP_N do GND | ESP i MCP restartują; po zwolnieniu IODIR/OLAT odtworzone, nowa sesja, wymagane ARM | NIE ZBADANO |
| Programowanie USB/DTR/RTS | Wejście do bootloadera i flash działają, reset obejmuje MCP | NIE ZBADANO |
| Zbocze SUP_N_OUT na P04 (R4) | Oscyloskop (sonda ×10, krótka masa): SUP_N (TP5), J2.15/U9.5 po stronie P04, SUP_N_P04 (P04 U9.6) i SUP_OK (P04 TP4) przy zwolnieniu i narzuceniu resetu CORE (przycisk RESET, zapad 3V3_CORE). Oczekiwane: na U9.5 jedno zbocze na przejście, ≤10 ns/V w całym obszarze przełączania 0,8–2,0 V, oba kierunki; zapisać przebieg i monotoniczność, nie wyciągać wniosku tylko z 10–90%. Podać model/pasmo i pojemność sondy; uwzględnić jej obciążenie; nominalny szacunek opóźnienia U6 to 2,6–4,0 ms po zwolnieniu U4 i 0,2–0,3 ms po narzuceniu (nie jest to kryterium PASS); SUP_N_P04 i SUP_OK bez serii impulsów; HW_ARMED i MOTOR_PERMIT stale L. Łącznie z E16 P04 | NIE ZBADANO |
| CORE_LINK przez R14 1 kΩ (R3) | Na P04 J2.13 / R16 ≥ 2,7 V przy zasilonym CORE; zwarcie J4.13 do GND ≈ 3,3 mA, 3V3_CORE bez zapadu | NIE ZBADANO |
| SUP_N_OUT przez R41 (R4) | P04 odłączony, reset zwolniony: amperomierz J4.15–GND 11–16 mA (dolna granica z VOH ≥ 2,4 V przy −16 mA, typowo ok. 14 mA), 3V3_CORE bez zapadu, U6 nie grzeje się; po zdjęciu amperomierza J4.15 w H (≥ 3,0 V). Przy wyłączonym CORE J4.15 z 10 kΩ do GND w L (Ioff U6) | NIE ZBADANO |
| Kolejność P03/P05/P04: każdy pierwszy i ostatni | Brak niezamierzonego MEAS_EN/ruchu; nieprawidłowe pomiary odrzucane | NIE ZBADANO |
| Wypięcie każdego modułu | Wejścia zgodne z STANY-DOMYSLNE.csv; brak danych nie zastępowany ważnym zerem | NIE ZBADANO |
| SPI na końcu P05 i P09, krótka sonda masowa | Zgodne setup/hold, bez wielokrotnych przejść progów; dobór R36–R40 | NIE ZBADANO |
| Odłączenie SD / błąd zapisu | Obsługa błędu w aplikacji, brak deklaracji poprawnego zapisu | NIE ZBADANO |

Test zapadu realizować kontrolowanym źródłem/obciążeniem i pomiarem na module; nie zwierać wyjścia AMS1117 ani nie łączyć dwóch aktywnych źródeł 3,3 V. Dla testu statycznego prądu wstecznego odłączyć pozostałe łącza sygnałowe, potem powtórzyć w kompletnym zestawie, aby rozdzielić tor mocy od zasilania przez sygnały.

Stan ADC_BUSY=0 i ADC_DOUT=0 przy wypiętym P05 jest tylko elektrycznym stanem domyślnym. Obecność AD7606B potwierdza sekwencja BUSY po CONVST oraz kontrola konfiguracji/testowego wzorca. Dla MCP3201 brak osobnego identyfikatora urządzenia: sam kod 0 nie dowodzi obecności; wykorzystać CURRENT_OK i procedurę odbioru. CAN_RX=1 oznacza recessive, a nie obecność transceivera. ENA/B=0 traktować jako FAULT/ABSENT; ostateczna diagnostyka zależy od wstrzymanego P07.

## R5 — dodatkowy odbiór resetu

- Potwierdzić U4 SN74LVC1G37DBVR (Schmitt, OD), R13 10 kΩ, R34 220 Ω i rezystor EN rzeczywistego modułu.
- Połączyć z P04-R2.2, R17=10 kΩ; przy P04 ON/CORE OFF zmierzyć U9.5 ≤0,8 V, bez odtwarzania ARM. Powtórzyć obie kolejności zasilania i reset USB.
- Dla wymuszonego LOW SUP_N zapisać napięcie, VDD i margines do 0,2 VDD MCP23017; nie stosować starego kryterium 0,25 V jako gwarancji.
- Wszystkie powyższe próby: NIE ZBADANO.
