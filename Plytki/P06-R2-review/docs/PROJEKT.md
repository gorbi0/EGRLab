# Obwód i granice pomiaru (P06-R2)

*R2 (1.10.2026, S1): obwód R1 bez zmian; zmienione fragmenty — bocznik SMD 2512 Kelvin, przełącznik BYPASS ogólny DPDT ON-ON, R3/R4 5,11 kΩ, C1/C4/C5 ceramiczne 1206, C3 220 µF, zasilanie przez J_BP, miedź 35 µm. Liczby filtra i rozruchu przeliczone; reszta tekstu jak w R1.*

P06 mierzy prąd jednej gałęzi silnika EGR 28410-2A850 podczas sterowania przez ECU. Dodatni znak oznacza przepływ ECU_P1 → EGR_P1. Ruch powrotny i recyrkulacja mogą dawać prąd przeciwny; sam znak nie jest rozpoznaniem kierunku mechanicznego zaworu. Piny czujnika pozycji ani drugi przewód silnika nie przechodzą przez elektronikę P06.

## Tor mocy i BYPASS

RSH1 to bocznik SMD 2512 z czterema polami (Kelvin), 5 mΩ, ≤ 1 % — Vishay WSK25125L000FEA (karta 30108, sprawdzona lokalnie 1.10: 1,0 W przy 70 °C, TCR ±35 ppm/K; pola według tabeli karty). Strata przy 6 A: 0,18 W; w biernej próbie 10 A: 0,5 W. Pola prądowe (1, 4) łączą się z J3/J4 polami miedzi ≥ 4 mm na obu warstwach, zszytymi przelotkami (35 µm zamiast 70 µm w R1 — tor krótki, próba nagrzewania E15). W polach bocznika nie ma przelotek ani styków przekaźnika. Pola pomiarowe (2, 3) dochodzą osobną parą przez R1/R2 do INA240. Nie ma złącza Kelvina.

SW1 — przełącznik na panelu, DPDT ON-ON ≥ 10 A przy 12–30 V DC, z oczkami lutowniczymi (MPN do potwierdzenia; w R1 NKK S6A 20 A / 30 V DC). W BYPASS styki 2-3 zwierają bocznik równolegle; 5-6 zwierają sygnał pozycji do GND. W MEASURE 2-1 prowadzi do niepodłączonego wyprowadzenia, a 5-4 podaje 5VA na SW_RAW (numeracja schematu, wspólne 2 i 5; oczka konkretnego przełącznika ustalić omomierzem). **Bocznik pozostaje włączony niezależnie od położenia przełącznika i zasilania elektroniki.** Jego przerwanie nie jest jednak automatycznie naprawiane — wówczas potrzebne jest ręczne BYPASS albo usunięcie interfejsu z wiązki.

Przewody i styk BYPASS mają własną rezystancję: obejście zmniejsza rezystancję toru, nie zapewnia idealnego 0 Ω. Prąd może dzielić się między bocznik i obejście. Odczyt w BYPASS jest NIEWAŻNY, nawet jeśli wygląda wiarygodnie. Przełączać przy wyłączonym zapłonie, przed rozpoczęciem zapisu. To nie jest przełącznik bezpieczeństwa ani automatyczne obejście uszkodzonej wiązki.

R21 39 Ω (PR02 2 W, leżący) obciąża styk pomocniczy prądem ok. 0,13 A i wydziela 0,64 W przy 5,00 V, 0,71 W przy 5,25 V. Prąd zwilżania pozwala użyć zwykłego (srebrnego) styku przełącznika mocy jako czujnika położenia. Przerwa styku lub jego przewodu daje LOW, a nie fałszywe potwierdzenie pomiaru. Zwarcie SW_RAW do 5VA lub sklejony styk może dać fałszywe READY; READY nie zastępuje próby prądowej BYPASS/MEASURE.

## Wzmocnienie i filtr

- INA240A2: G = 50 V/V, odniesienie 2,5 V z MCP1525 buforowane przez U2B na oba piny REF.
- R3/R4 = 5,11 kΩ / 5,11 kΩ, 0,1 %, 25 ppm/K (1206, zamiana 1:1 z listy 2); dzielnik 1:2 obciąża INA240 rezystancją 10,22 kΩ (10,21 kΩ w dolnym narożniku tolerancji). Odpowiada to warunkowi 10 kΩ z tabeli wychylenia wyjścia TI. Stosunek w narożnikach (0,1 % + 25 ppm/K × 50 K) 0,49888–0,50113.
- C1 = 470 nF X7R 1206 / 10 % (R1: PET). Rezystancja Thevenina 2,555 kΩ: τ = 1,2009 ms; fc = 132,5 Hz. Tolerancja X7R i zmiana z temperaturą w kabinie dają τ ok. 0,92–1,39 ms (ok. 115–173 Hz; R1 z PET: 121–148 Hz). Rzeczywiste τ zmierzyć przy odbiorze (E16) i zapisać w kalibracji.
- U2A jest wtórnikiem dzielnika. R5 47 Ω + C2 470 pF przy IN+ ADC izoluje obciążenie pojemnościowe; nie jest głównym filtrem pasma.
- MCP3201: VREF = 2,5 V, 12 bitów, odczyt SPI 500 kHz / 16 taktów.

Idealnie: `VINA = 2.5 + 0.25*I`, `VADC = 1.25 + 0.125*I`, `raw = 2048 + 204.8*I`. Kwantyzacja to 4,8828 mA/kod. R1/R2 10 Ω wnoszą według modelu TI współczynnik 3000/3010 = 0,99668, czyli około -0,332% wzmocnienia. Do tego dochodzą tolerancje bocznika, dzielnika, wzorca, wzmocnienia i offsety. **204,8 kodu/A jest wartością startową, nie wynikiem kalibracji.** Kalibrować offset i nachylenie z co najmniej dwoma polaryzacjami prądu.

Zakres matematyczny ADC wynosi ±10 A. Przy niższym 5VA wcześniej ogranicza się dodatnie wyjście INA240. Odbiór R1 obejmuje **±6 A**, najpierw ±1 A i ±3 A, przy minimalnym zasilaniu i po rozgrzaniu. Nie rozszerzać zakresu na podstawie samego pełnego zakresu ADC. Ujemne i dodatnie nasycenie analogowe nie muszą dać kodów 0/4095; porównywać również I_L_OUT z szynami zasilania. 10 A to cel kwalifikacji biernego toru prądowego, nie zakres potwierdzonego pomiaru i nie nowy limit aktywnego sterowania EGR.

## Co widać przy 2 kS/s

To pomiar trendu prądu, użyteczny do porównywania zimnego i gorącego EGR, narastania obciążenia i zaniku ruchu. Nie odtwarza impulsów PWM 20 kHz. Filtr pierwszego rzędu tłumi 20 kHz około 43,6 dB, 2 kHz około 23,6 dB, a 1 kHz około 17,6 dB. Nie usuwa wszystkich możliwych aliasów; trzeba sprawdzić rzeczywistą częstotliwość PWM ECU i porównać trend z oscyloskopem/próbnikiem prądu. Przy niskiej częstotliwości PWM lub istotnym resztkowym aliasie potrzebne będzie większe próbkowanie albo filtr wyższego rzędu - obecnej próbki nie przedstawiać jako pomiaru tętnień.

Filtr opóźnia wolnozmienne zjawiska o około 1,2 ms; 10-90% skoku to około 2,63 ms, ustalenie do 1% około 5,52 ms. Rejestrowany skew SPI względem AD7606B jest oddzielnym opóźnieniem. Nie wyrównywać całego przebiegu arbitralnym przesunięciem czasowym bez uwzględnienia fazy filtru. Po włączeniu/zmianie pozycji odczekać 1 s przed ZERO i zapisem.

## Zasilanie i stany nieaktywne

J_BP.10/12 = 5V_SYS; J_BP.14 = 3V3_IO wyłącznie na kołku J_SV2.6 (przez 1 kΩ). Lokalny MCP1702 wytwarza 3V3_P06. Nie łączyć obu szyn 3,3 V. R6 1 Ω / 1 W (KNP01U-1R) i C3 220 µF odsprzęgają 5VA (decyzja 1.10: 220 µF zamiast 470 µF; razem z C1 220 µF w P05 R3 szyna 5V_SYS ma ok. 486 µF wobec 600 µF dopuszczalnych dla TSR 2-2450). Przy włączeniu C3 magazynuje do 3,0 mJ przy 5,25 V i tyle wydziela R6; τ = R6·C3 = 0,22 ms. R6 powinien mieć dopuszczalną energię impulsu co najmniej 5 mJ — część doboru rezystora, nie wynika z samego napisu „1 W”. Mniejszy C3 słabiej tłumi skoki obciążenia R21 przy przełączaniu SW1 (przełączać i tak przy wyłączonym zapłonie, przed zapisem).

Budżet P06: przyjąć **180 mA z 5V_SYS** w MEASURE (około 0,95 W przy 5,25 V); zmierzyć pobór w BYPASS i MEASURE. Część tego poboru jest nowa względem bazowego P06. Zasilanie daje P02 R4 (pakiet 4S, TSR 2-2450); budżet 5V_SYS LOGGERA ok. 1090 mA (P12 przygotowanie). Po PFAIL_N z P02 R4 firmware unieważnia pomiar; niniejszy pakiet nie potwierdza czasu podtrzymania kompletu.

Przy 5V_SYS = 4,75 V, R21 minimalnym 38,61 Ω i pozostałym obciążeniu 20 mA, 5VA wynosi około 4,61 V. MCP120-450 ma próg opadania 4,25-4,50 V; 50 mV histerezy to wartość TYP. Około 60 mV względem 4,55 V jest zatem oszacowaniem, nie gwarantowanym marginesem zwolnienia resetu. Sprawdzić najniższe 5V_SYS z P02, rozgrzanie i działanie HOLD. MCP120-300 obserwuje lokalne 3,3 V. READY jest iloczynem obu sygnałów resetu oraz pozycji MEASURE; nie sprawdza VREF, kalibracji ani ciągłości bocznika.

U5/U6: wyłącznie Nexperia 74LVC125AD z Ioff i wejściami tolerującymi 5 V. U5C zwalnia wspólne DOUTA przy CS_LOCAL_N=H. Lokalne CS ma pull-up 10 kΩ, CLK pull-down 10 kΩ. R8 po stronie złącza ma **100 kΩ**: gdy CORE jest włączony, a P06 wyłączony, ogranicza zasilanie przez tę polaryzację do około 33 µA. R24 1 kΩ utrzymuje wtedy martwą szynę na około 33 mV plus upływy. To ograniczenie prądu, nie izolacja; odbiór wymaga V3V3_P06 <0,1 V w tym stanie. Gdy CORE jest odłączony, R8 podciąga CS do H.

D1 rozładowuje lokalne 3,3 V w kierunku 5VA, D2 rozładowuje kondensator VREF w kierunku 3,3 V. Pomagają zachować kolejność zaniku zasilania. Twarde zwarcie szyny jest osobnym przypadkiem odbioru ograniczonym prądowo; z modelu RC nie wynika odporność na każde zwarcie. Wszystkie pomiary P06 są odniesione do wspólnej GND EGRLab. INA240 ma szeroki zakres napięcia wspólnego; nie zapewnia separacji galwanicznej.

## Źródła

- [TI INA240, pinout SOIC oraz §9.1.1 i tabela 7.5](https://www.ti.com/lit/ds/symlink/ina240.pdf).
- [Vishay WSK2512](https://www.vishay.com/docs/30108/wsk.pdf) — do potwierdzenia lokalnie (w chmurze zablokowane); [Vishay PR01/02/03](https://www.vishay.com/docs/28729/pr010203.pdf).
- [Microchip MCP3201](https://ww1.microchip.com/downloads/en/DeviceDoc/21290F.pdf), [MCP1525](https://ww1.microchip.com/downloads/en/devicedoc/21653c.pdf), [MCP1702](https://ww1.microchip.com/downloads/en/devicedoc/22008e.pdf), [MCP120](https://ww1.microchip.com/downloads/en/DeviceDoc/11184d.pdf).
- [Nexperia 74LVC125A](https://assets.nexperia.com/documents/data-sheet/74LVC125A.pdf).

Obliczenia powyżej są analizą projektu na podstawie kart producentów; wyniki sprzętowe pozostają niewypełnione w ODBIOR.md.
