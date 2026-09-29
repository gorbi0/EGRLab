# Obwód i granice pomiaru

P06 mierzy prąd jednej gałęzi silnika EGR 28410-2A850 podczas sterowania przez ECU. Dodatni znak oznacza przepływ ECU_P1 → EGR_P1. Ruch powrotny i recyrkulacja mogą dawać prąd przeciwny; sam znak nie jest rozpoznaniem kierunku mechanicznego zaworu. Piny czujnika pozycji ani drugi przewód silnika nie przechodzą przez elektronikę P06.

## Tor mocy i BYPASS

RSH1 to PBV-R005-F1-0.5: 5 mΩ, cztery końcówki, 0,5%, **3 W bez radiatora**. Zewnętrzne końcówki prądowe są połączone z J3/J4 ścieżkami 6 mm, 70 µm. W torze silnika nie ma przelotek ani styków przekaźnika. Wewnętrzne wyprowadzenia Kelvina dochodzą przez R1/R2 do INA240. Nie ma złącza Kelvina.

SW1 NKK S6A, DPDT ON-ON, 20 A / 30 V DC dla obciążenia rezystancyjnego, jest poza PCB. W BYPASS styki 2-3 zwierają bocznik równolegle; 5-6 zwierają sygnał pozycji do GND. W MEASURE 2-1 prowadzi do niepodłączonego wyprowadzenia, a 5-4 podaje 5VA na SW_RAW. **Bocznik pozostaje włączony niezależnie od położenia przełącznika i zasilania elektroniki.** Jego przerwanie nie jest jednak automatycznie naprawiane - wówczas potrzebne jest ręczne BYPASS albo usunięcie interfejsu z wiązki.

Przewody i styk BYPASS mają własną rezystancję: obejście zmniejsza rezystancję toru, nie zapewnia idealnego 0 Ω. Prąd może dzielić się między bocznik i obejście. Odczyt w BYPASS jest NIEWAŻNY, nawet jeśli wygląda wiarygodnie. Przełączać przy wyłączonym zapłonie, przed rozpoczęciem zapisu. To nie jest przełącznik bezpieczeństwa ani automatyczne obejście uszkodzonej wiązki.

R21 39 Ω / 2 W obciąża pomocniczy srebrny styk około 120-130 mA; wydziela około 0,6 W. Producent zaleca złoto do małych sygnałów, a srebro dla większych obciążeń. Obciążenie powyżej 0,4 VA eliminuje świadome użycie styku mocy jako suchego styku mikroamperowego; trwałość rzeczywistego egzemplarza podlega odbiorowi. Przerwa styku lub jego przewodu daje LOW, a nie fałszywe potwierdzenie pomiaru. Zwarcie SW_RAW do 5VA lub sklejony styk może dać fałszywe READY; READY nie zastępuje próby prądowej BYPASS/MEASURE.

## Wzmocnienie i filtr

- INA240A2: G = 50 V/V, odniesienie 2,5 V z MCP1525 buforowane przez U2B na oba piny REF.
- R3/R4 = 5,1 kΩ / 5,1 kΩ, 0,1%; dzielnik 1:2 obciąża INA240 rezystancją 10,2 kΩ. Odpowiada to warunkowi 10 kΩ z tabeli wychylenia wyjścia TI.
- C1 = 470 nF PET / 10%. Rezystancja Thevenina 2,55 kΩ: τ = 1,1985 ms; fc = 132,79 Hz. Tolerancja C1 i R daje w przybliżeniu 121-148 Hz.
- U2A jest wtórnikiem dzielnika. R5 47 Ω + C2 470 pF przy IN+ ADC izoluje obciążenie pojemnościowe; nie jest głównym filtrem pasma.
- MCP3201: VREF = 2,5 V, 12 bitów, odczyt SPI 500 kHz / 16 taktów.

Idealnie: `VINA = 2.5 + 0.25*I`, `VADC = 1.25 + 0.125*I`, `raw = 2048 + 204.8*I`. Kwantyzacja to 4,8828 mA/kod. R1/R2 10 Ω wnoszą według modelu TI współczynnik 3000/3010 = 0,99668, czyli około -0,332% wzmocnienia. Do tego dochodzą tolerancje bocznika, dzielnika, wzorca, wzmocnienia i offsety. **204,8 kodu/A jest wartością startową, nie wynikiem kalibracji.** Kalibrować offset i nachylenie z co najmniej dwoma polaryzacjami prądu.

Zakres matematyczny ADC wynosi ±10 A. Przy niższym 5VA wcześniej ogranicza się dodatnie wyjście INA240. Odbiór R1 obejmuje **±6 A**, najpierw ±1 A i ±3 A, przy minimalnym zasilaniu i po rozgrzaniu. Nie rozszerzać zakresu na podstawie samego pełnego zakresu ADC. Ujemne i dodatnie nasycenie analogowe nie muszą dać kodów 0/4095; porównywać również I_L_OUT z szynami zasilania. 10 A to cel kwalifikacji biernego toru prądowego, nie zakres potwierdzonego pomiaru i nie nowy limit aktywnego sterowania EGR.

## Co widać przy 2 kS/s

To pomiar trendu prądu, użyteczny do porównywania zimnego i gorącego EGR, narastania obciążenia i zaniku ruchu. Nie odtwarza impulsów PWM 20 kHz. Filtr pierwszego rzędu tłumi 20 kHz około 43,6 dB, 2 kHz około 23,6 dB, a 1 kHz około 17,6 dB. Nie usuwa wszystkich możliwych aliasów; trzeba sprawdzić rzeczywistą częstotliwość PWM ECU i porównać trend z oscyloskopem/próbnikiem prądu. Przy niskiej częstotliwości PWM lub istotnym resztkowym aliasie potrzebne będzie większe próbkowanie albo filtr wyższego rzędu - obecnej próbki nie przedstawiać jako pomiaru tętnień.

Filtr opóźnia wolnozmienne zjawiska o około 1,2 ms; 10-90% skoku to około 2,63 ms, ustalenie do 1% około 5,52 ms. Rejestrowany skew SPI względem AD7606B jest oddzielnym opóźnieniem. Nie wyrównywać całego przebiegu arbitralnym przesunięciem czasowym bez uwzględnienia fazy filtru. Po włączeniu/zmianie pozycji odczekać 1 s przed ZERO i zapisem.

## Zasilanie i stany nieaktywne

LV06.1 = 5V_SYS; LV06.3 = 3V3_IO wyłącznie na TP4. Lokalny MCP1702 wytwarza 3V3_P06. Nie łączyć obu szyn 3,3 V. R6 1 Ω / 1 W i C3 470 µF odsprzęgają 5VA. Przy włączeniu C3 magazynuje do 6,5 mJ przy 5,25 V; R6 powinien mieć dopuszczalną energię impulsu co najmniej 10 mJ. Wymóg ten jest częścią doboru zamiennika rezystora, nie wynika z samego napisu „1 W”.

Budżet P06: przyjąć **180 mA z 5V_SYS** w MEASURE (około 0,95 W przy 5,25 V); zmierzyć pobór w BYPASS i MEASURE. Część tego poboru jest nowa względem bazowego P06. W P02-R3 nadal obowiązuje limit 6 W z VLOG_RES dla deklarowanego HOLD 50 ms. Do odbioru całego urządzenia wliczyć P06 i straty przetwornic; niniejszy pakiet nie potwierdza 50 ms dla niezmierzonego kompletu modułów.

Przy 5V_SYS = 4,75 V, R21 minimalnym 38,61 Ω i pozostałym obciążeniu 20 mA, 5VA wynosi około 4,61 V. MCP120-450 ma próg opadania 4,25-4,50 V; 50 mV histerezy to wartość TYP. Około 60 mV względem 4,55 V jest zatem oszacowaniem, nie gwarantowanym marginesem zwolnienia resetu. Sprawdzić najniższe 5V_SYS z P02, rozgrzanie i działanie HOLD. MCP120-300 obserwuje lokalne 3,3 V. READY jest iloczynem obu sygnałów resetu oraz pozycji MEASURE; nie sprawdza VREF, kalibracji ani ciągłości bocznika.

U5/U6: wyłącznie Nexperia 74LVC125AD z Ioff i wejściami tolerującymi 5 V. U5C zwalnia wspólne DOUTA przy CS_LOCAL_N=H. Lokalne CS ma pull-up 10 kΩ, CLK pull-down 10 kΩ. R8 po stronie złącza ma **100 kΩ**: gdy CORE jest włączony, a P06 wyłączony, ogranicza zasilanie przez tę polaryzację do około 33 µA. R24 1 kΩ utrzymuje wtedy martwą szynę na około 33 mV plus upływy. To ograniczenie prądu, nie izolacja; odbiór wymaga V3V3_P06 <0,1 V w tym stanie. Gdy CORE jest odłączony, R8 podciąga CS do H.

D1 rozładowuje lokalne 3,3 V w kierunku 5VA, D2 rozładowuje kondensator VREF w kierunku 3,3 V. Pomagają zachować kolejność zaniku zasilania. Twarde zwarcie szyny jest osobnym przypadkiem odbioru ograniczonym prądowo; z modelu RC nie wynika odporność na każde zwarcie. Wszystkie pomiary P06 są odniesione do wspólnej GND EGRLab. INA240 ma szeroki zakres napięcia wspólnego; nie zapewnia separacji galwanicznej i nie zastępuje P01/P02.

## Źródła

- [TI INA240, pinout SOIC oraz §9.1.1 i tabela 7.5](https://www.ti.com/lit/ds/symlink/ina240.pdf).
- [Isabellenhütte PBV, parametry i rysunek F1](https://www.isabellenhuette.com/hubfs/Files/Data-sheets/PBV.pdf).
- [Microchip MCP3201](https://ww1.microchip.com/downloads/en/DeviceDoc/21290F.pdf), [MCP1525](https://ww1.microchip.com/downloads/en/devicedoc/21653c.pdf), [MCP1702](https://ww1.microchip.com/downloads/en/devicedoc/22008e.pdf), [MCP120](https://ww1.microchip.com/downloads/en/DeviceDoc/11184d.pdf).
- [Nexperia 74LVC125A](https://assets.nexperia.com/documents/data-sheet/74LVC125A.pdf).
- [NKK S, model S6A](https://www.nkkswitches.com.hk/documents/products/series_pdf/toggle_S.pdf), [dobór materiału styków](https://www.nkkswitches.eu/engineering/electrical.html).

Obliczenia powyżej są analizą projektu na podstawie kart producentów; wyniki sprzętowe pozostają niewypełnione w ODBIOR.md.
