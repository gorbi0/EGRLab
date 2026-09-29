# EGRLab v5 — odpowiedź na ocenę Opusa i założenia wykonania

Data: 22.09.2026. Podstawa: `ocena_opusa.txt`, pliki rzeczywistego katalogu EGRLab-v5 i dokumentacja producentów. Sprawdzono integralność 314 plików objętych manifestem wydania: bez różnic. Ten dokument jest **aneksem przeglądu i rejestrem decyzji**, a nie wdrożoną rewizją schematu, BOM-u ani firmware.

Przyjmuję założenie użytkownika: **P01, P05 i P07 zamawiane jako PCB dwuwarstwowe, lutowane samodzielnie; pozostałe moduły na lutowanych płytkach uniwersalnych lub gotowych nośnikach.** P00/P11 mogą być montażem pomocniczym/panelowym. Rozdział na wymienne funkcje zostaje.

## 1. Błędy zakupowe znalezione dodatkowo

### P05 U1: błędny kod zamówieniowy ADC — poprawić przed zakupem

W `hardware/components.json`, BOM-ie i atlasie występuje **AD7606BSTZ**. To kod starszego **AD7606**, a projekt i firmware zakładają **AD7606B**. Właściwy kod to **AD7606BBSTZ**, ewentualnie wariant pakowania **AD7606BBSTZ-RL**. Podwójne B jest istotne. To mój błąd w wydaniu v5; pozytywna kontrola połączeń go nie wykryła. Schemat i kod muszą nadal dotyczyć AD7606B; nie należy naprawiać tego przez zakup starszego układu i wyłączenie funkcji programu.

Potwierdzenie: [AD7606 — lista modeli](https://www.analog.com/en/products/ad7606.html) oraz [AD7606B — Ordering Guide, str. 74](https://www.analog.com/media/en/technical-documentation/data-sheets/AD7606B.pdf).

### P05 U6 / P07 U4: kod i obudowa komparatora

Wpis **TLV1702QDGKRQ1** jest niepełny. Potwierdzony kod producenta to **TLV1702AQDGKRQ1**. Obudowa DGK to **VSSOP-8 z rastrem 0,65 mm**, nie SOIC. Dlatego stwierdzenie, że jedynie AD7606B wymaga lutowania drobniejszego niż SOIC, jest nieprawidłowe. Komparator ma dostępne wyprowadzenia i można go lutować ręcznie, ale footprint i opis montażu muszą wskazywać właściwą obudowę. [TI — dokładny model](https://www.ti.com/product/TLV1702-Q1/part-details/TLV1702AQDGKRQ1), [datasheet i rysunek DGK](https://www.ti.com/lit/ds/symlink/tlv1702-q1.pdf).

Wymaganie łatwego montażu dotyczy części lutowanych przez użytkownika. Pololu/VNH5019 i MAX31856 są przewidziane jako gotowe moduły; obudowy scalaków już na nich zamontowanych nie oznaczają obowiązku lutowania ich w domu.

## 2. Uwagi Opusa: co przyjmuję i co doprecyzowuję

| Uwaga | Ocena i dalsze działanie |
|---|---|
| Lokalny ADC prądu i wymienne moduły | Zasadne. Wrażliwy tor zostaje na P06/P07; nie przywracamy przewodu INA→DAQ. |
| Krok prądu 4,88 mA | Obliczenie poprawne: 2,5 V / 4096 / (5 mΩ × 50 × 1/2). Przy 0,1 A jest około 20,5 **kroków LSB**, nie „20 bitów”. Zero 2048 jest nominalne, do kalibracji. |
| Zakres ±8 A | Mieści się nominalnie w 0,25–2,25 V na wejściu lokalnego ADC. To zapas toru pomiarowego, a nie dozwolony prąd TEST; obowiązują dotychczasowe limity i OC około ±4 A. |
| Progi OC ze wspólnego odniesienia | Poprawnie: −4,00 A / +4,016 A nominalnie. Zmniejszamy zależność od szyny 5 V; nie znosimy tolerancji i dryftu wszystkich elementów. |
| Brak deklaracji warstw | Słusznie. Nowa reguła: trzy wskazane PCB mają dwie warstwy. Dokładność P05 trzeba potwierdzić po wykonaniu. |
| Adaptery pod każdy SO14 | Zależne od sposobu montażu. Na P05/P07 bez adapterów, na uniwersalnych z adapterami. |
| Cztery wiszące sieci | Potwierdzone; szczegółowe rozstrzygnięcia poniżej. |
| MCP1525 bez dodatkowego bufora VREF ADC | To uwaga do odsprzęgania i pomiaru, a nie wykazany błąd wymagający nowego układu. Szczegóły poniżej. |
| Brak narzędzi/materiałów w zakupach | Centralny wykaz ich nie wycenia ani nie liczy. Materiały są już wymienione w docs/07, a część w osobnym BOM-ie P01; brakuje jednego uporządkowanego zestawienia. |
| P01 ma skończony projekt | Ma dokumentację obwodu i obliczenia. **Nie ma gotowego layoutu ani Gerberów do zamówienia.** |

Policzone w aktualnych danych: 26 układów 74LVC125, 67 użytych bramek. Podana przez Opusa liczba 28 układów nie zgadza się z plikami. P05 i P07 mają po cztery; pozostałe 18 sztuk przypada na moduły uniwersalne. To liczba adapterów tylko dla 74LVC125, bez INA, transceivera i innych SMD.

## 3. Przyjęte wykonanie modułów

| Moduł | Wykonanie | Istotna zasada montażu |
|---|---|---|
| P01 PROTECT | PCB 2 warstwy, fabryka | Pętle ochrony i TVS krótkie; szeroki tor mocy, zaciski i radiatory z dostępem do śrub. |
| P02 PSU | Uniwersalna lutowana | Gotowe TSR; tor SUPPLY→VMOTOR i jego powrót grubymi przewodami/szynami. Nie przez standardowe pola lub cienkie paski miedzi uniwersalnej. |
| P03 CORE | Uniwersalna lutowana | Waveshare i SD na nośnikach, bufory przy złączach, krótkie połączenia SPI z masą; przewidzieć regulację zegarów w firmware. |
| P04 SAFE | Uniwersalna lutowana | Krótkie CLK, /CLR, ARM; 100 nF przy każdym scalaku, solidna masa, oddalenie przewodów motoru. |
| P05 DAQ | PCB 2 warstwy, fabryka | Rozmieszczenie pod pomiar analogowy i ciągły powrót masy; ADC i jego kondensatory lokalnie. |
| P06 I-LOGGER | Uniwersalna lutowana, po odbiorze może zostać | Bocznik i INA blisko, oddzielone połączenia mocy i pomiaru, ADC/REF w zwartej części płytki. |
| P07 DRIVE | PCB 2 warstwy, fabryka | Gotowy nośnik mostka, lokalny kondensator/TVS/bocznik/OC, mała pętla prądu i mechaniczne mocowanie mocy. |
| P08 SENSOR | Uniwersalna lutowana | Adapter TPS2553, lokalne kondensatory i przekaźnik; odseparować przewody 5 V sensora od motoru. |
| P09 TEMP | Uniwersalna + gotowe MAX31856 | Złącza termopar i kompensacja zimnego złącza z dala od ciepła radiatorów i przetwornic. |
| P10 CAN | Uniwersalna lutowana | Krótki odcinek CANH/CANL, zabezpieczenie ESD blisko złącza, lokalne odsprzęganie. |
| P11 PANEL | Wiązka/panel, ewentualnie uniwersalna | Styki wykrywające wtyki i mocowanie złączy nadal wymagają wykonania mechanicznego. Prąd motoru grubymi przewodami. |
| P00 | Uniwersalna lutowana | Przyrząd stanowiskowy, odpinany przed integracją. |

Płytka uniwersalna oznacza tu trwały montaż lutowany, przykręcone moduły i odciążenie kabli. Płytka stykowa oraz luźne przewody Dupont nie są wykonaniem do użycia w aucie. Nie ma obowiązku późniejszego przerysowania poprawnie działających modułów uniwersalnych na zamawiane PCB.

Dla P06: dwa połączenia mocy do bocznika oraz **jedna para pomiarowa K1/K2** prowadzona razem, możliwie krótko od osobnych wyprowadzeń Kelvin do INA. Określenie Opusa „dwie pary Kelvina” jest nieprecyzyjne. Nie może być wspólnego odcinka przewodu pomiarowego i mocy. Odbiór obejmuje zero, oba znaki prądu, temperaturę i zakłócenia od PWM.

P04 nie jest całkowicie obojętne na montaż: częstotliwość funkcji może być mała, a zbocza logiczne szybkie. Uniwersalna jest właściwym rozwiązaniem, ale /CLR i CLK nie powinny biec długimi luźnymi drutami.

## 4. Reguły dla trzech zamawianych PCB

Założenia projektowe do layoutu: FR-4 1,6 mm, dwie warstwy, metalizowane otwory, soldermaska i opis, pola pod ręczne lutowanie. Dla P01/P07 przewidzieć miedź 70 µm, dla P05 35 µm. Grubość miedzi nie zastępuje obliczenia szerokości, przewężeń, przelotek i temperatury. Zostawić miejsce na wzmocnienie szyną tam, gdzie jest potrzebne; nie minimalizować obrysu kosztem lutowania.

**P05:** spód przeznaczony przede wszystkim na nieprzerywaną masę w obszarze ADC i wejść; rozdział analogu i cyfry rozmieszczeniem, bez szczeliny w powrocie masy. CLK/CONVST daleko od wejść. Kondensatory zasilania, odniesienia i REGCAP przy właściwych pinach; położenie ważniejsze od tego, czy wszystkie elementy są na jednej stronie. Takie prowadzenie odpowiada [zaleceniom ADI, str. 52](https://www.analog.com/media/en/technical-documentation/data-sheets/AD7606B.pdf). Dwie warstwy przyjmujemy jako założenie inżynierskie, nie gwarancję dokładności 16 bitów. Można zwiększyć obrys i użyć lokalnych zworek zamiast przecinać istotny powrót masy.

Ponieważ P05 i tak będzie zamawiane, wariant bazowy to **AD7606BBSTZ bezpośrednio na PCB**. Gotowy moduł ADC jest opcją po sprawdzeniu konkretnego produktu: właściwy układ, jego schemat, kondensatory, wyprowadzenia i software mode. Sam adapter LQFP→goldpin nie rozwiązuje odsprzęgania. Nie wybieram anonimowego modułu opisanego tylko „AD7606”.

Lutowanie AD7606B 0,5 mm i TLV1702 0,65 mm pozostaje ręczną pracą wymagającą topnika, kontroli pod powiększeniem i usuwania mostków. Nie ma wymogu lutowania obudowy bez wyprowadzeń pod korpusem zamiast tych elementów.

## 5. Porządki w obwodzie do następnej rewizji

- **P06 RO2 / I_LOG_SER i P07 RO1 / I_TEST_SER:** usunąć rezystory 100 Ω i samotne sieci. Wyjścia do oscyloskopu już są na J_ANALOG_TP; nie potrzebują tych rezystorów zakończonych w powietrzu.
- **P11 STOP_PRESSED:** pomocnicze styki NO pozostawić jawnie niepodłączone, usunąć nazwę pozornej sieci/punktu pomiarowego. Sprzętowe NC pozostaje. Nie podłączać do GPB7 — w projekcie pozostaje on niewykorzystanym wyjściem.
- **P07 LOCAL_ARM_CLK:** wejścia niewykorzystanej bramki U_GATE, piny 4/5, ustalić na GND, wyjście 6 oznaczyć NC. Taktowanie zatrzasku nadal ARM_CLK_P07, dane PERMIT_N; nie zmieniać tej zasady.
- Rozdzielić pola BOM: kod producenta, obudowa, metoda montażu, adapter. Poprawić oba kody zakupowe opisane w punkcie 1, również w generatorze, zestawieniu zakupów i atlasie.

To ustalenia przeglądu; dotychczasowego BOM-u i binariów v5 w ramach tego aneksu nie przebudowano. Błędnych kodów z punktu 1 nie używać do zamówienia.

## 6. VREF i zegary — proste doprecyzowanie, bez mnożenia układów

MCP1525 jest połączony przewodem z VREF MCP3201; 1 µF jest dołączone **do masy**, nie szeregowo. Producent odniesienia przewiduje 1–10 µF blisko wyjścia. Dlatego nie ma podstaw, by z góry odrzucać ten układ lub obowiązkowo dodawać kolejny wzmacniacz. Przy layoutcie/montażu przewiduję miejsce na 4,7 µF i 100 nF, z bardzo krótkim połączeniem do ADC i odniesienia, a następnie pomiar VREF podczas konwersji. Zmiana pojemności wymaga uwzględnienia czasu ustalenia po starcie. [MCP1525, rozdział 4.1.3](https://ww1.microchip.com/downloads/en/devicedoc/21653c.pdf).

Mierzyć przy pinie ADC, sondą z krótką sprężynką masową: zero i stałe wejście, brak/obecność transferów pozostałych urządzeń, PWM wyłączone/włączone. Oprócz przebiegu VREF sprawdzić rozrzut kodów i błąd przy znanym prądzie. Sam wynik pojedynczego pomiaru DC nie zatwierdza dynamiki. [MCP3201, rozdział 4.2](https://ww1.microchip.com/downloads/en/DeviceDoc/21290F.pdf).

Aktualny kod v5 ma AD7606B 8 MHz, SD 10 MHz, lokalny MCP3201 500 kHz. Dla przewodowego CORE należy dodać wybierane parametry, zamiast ręcznie poprawiać stałe. Punkt wyjścia do prób: AD 1 MHz, SD 2–4 MHz, MCP3201 nadal 500 kHz. To propozycja do sprawdzenia, nie wykonana modyfikacja firmware.

Odczyt 128 bitów AD przy 1 MHz trwa na przewodzie 128 µs, lokalny ADC 16/500 kHz = 32 µs. Trzeba doliczyć konwersję, sterowniki i planowanie; pozostają limity 500 µs okresu i zakończenia prądu do 400 µs. Obniżenie samej częstotliwości nie zmniejsza automatycznie stromości zboczy. Krótkie połączenia i powrót masy są nadal wymagane.

Nie obniżać SD bezwarunkowo do 1 MHz: 2 kS/s × 40 B to już 80 kB/s próbek, a surowe 1 MHz SPI daje najwyżej 125 kB/s przed narzutem. Dochodzą CRC, system plików, zajętość karty oraz CAN/zdarzenia. Odbiór obejmuje trwały zapis pełnego przewidywanego strumienia, liczniki strat i czas blokowania karty.

## 7. Materiały, złącza i dokumentacja wykonawcza

Zachować obecne klucze i pinout M1. Macierz zawiera także analogowe MSTB 3,81 mm; nie pomylić z mocowym 5,08 mm. Narzędzia dobrać do faktycznie wybranych styków DEUTSCH i Micro-Fit. Nie przesądzam zakupu dwóch drogich zaciskarek: możliwe narzędzie z odpowiednimi matrycami albo gotowe przewody ze stykami. IDC można zaciskać małą prasą lub równoległym przyrządem odpowiednim do korpusu, a potem sprawdzić każdy styk i klucz.

Do wspólnej listy zakupów dodać osobno: adaptery według modułów, listwy/podstawki, płytki uniwersalne, przewody mocy i sygnałów, styki i zapas na naukę zaciskania, tulejki, narzędzia do wyjmowania styków, dystanse, mocowanie przewodów, izolatory radiatorów, etykiety i materiały lutownicze. Obudowy i liczby adapterów muszą wynikać z deklarowanego sposobu wykonania.

Każdy moduł uniwersalny powinien otrzymać rysunek rozmieszczenia na rastrze 2,54 mm i kolejność lutowania. Sama netlista/atlas pinowy nie jest taką instrukcją. P01/P05/P07 wymagają schematów w EDA, layoutu 2L, ERC/DRC i plików produkcyjnych. W formularzu odbioru dopisać: sposób montażu, zdjęcie obu stron, długości kabli, rewizję nośników, zegary oraz pomiary VREF. Kalibrację po zmianie fizycznego wykonania modułu powtórzyć.
