# Uwagi wykonawcze do schematu S1

S1 jest rozwinięciem rysunkowym V4. Poniższe punkty usuwają niejednoznaczności dokumentacji wejściowej; oryginały V4 pozostały niezmienione.

## 1. Dzielnik OVP w LM74800EVM-CD - istotne doprecyzowanie

W V4 podano górną gałąź 47,5 kΩ i dolną 3,48 kΩ. Na rzeczywistym schemacie TI górną gałąź tworzą **dwa rezystory szeregowe: R8 + R3**, a węzeł pomiędzy nimi służy jako VIN_MON. Fabrycznie R8=9,1 kΩ, R3=91 kΩ i R4=3,48 kΩ. Wymiana samego R3 na 47,5 kΩ pozostawiłaby sumę 56,6 kΩ i dałaby około 21,25 V, zamiast zamierzonych około 18 V. To obliczenie z nominalnego progu OV 1,231 V.

Schemat S1 wskazuje konkretną realizację: **R8=9,10 kΩ, R3=38,3 kΩ, R4=3,48 kΩ**, najlepiej po 0,1%, oraz J6 2-3. Suma górnej gałęzi 47,4 kΩ daje nominalnie 17,998 V. Tolerancja progu układu nadal wymaga pomiaru i dostrojenia do 17,5-18,5 V. Oznaczenia `M5_R8`, `M5_R3`, `M5_R4` w schemacie oznaczają elementy wewnątrz EVM, nie dodatkowy dzielnik na płycie EGRLab. Sprawdź rewizję swojego EVM przed wymianą. Nie pomyl OV z EN/UVLO.

Źródła: [TI SLVUBU3A, schemat na stronie 4](https://www.ti.com/lit/ug/slvubu3a/slvubu3a.pdf) oraz [LM7480-Q1, próg OV na stronie 5](https://www.ti.com/lit/ds/symlink/lm7480-q1.pdf). Podane progi wynikają z obliczenia dzielnika, nie z pomiaru egzemplarza.

## 2. Fizyczne piny przekaźników sygnałowych

Dla **G6K-2F-Y DC5**, w widoku od góry: cewka +1/-8; biegun A COM3/NC2/NO4; biegun B COM6/NC7/NO5. Piny naniesiono na arkusze. Nie używaj bez sprawdzenia rysunku lustrzanego dla wersji przewlekanej ani przekaźnika zatrzaskowego G6KU. [Karta Omron, strona 6](https://omronfs.omron.com/en_US/ecb/products/pdf/en-g6k.pdf).

Niepodłączone NC KMEAS i KSENSOR oraz nieużyte bieguny KMEAS3/KCUR oznaczono krzyżykami. Cewki i styki przedstawiono jako części tego samego elementu z jednoznacznymi nazwami i numerami. KPWR pozostaje samochodowym przekaźnikiem dobieranym według wymagań V4; przed montażem sprawdź oznaczenia 30/87/85/86 na konkretnym modelu.

## 3. Uzupełnienia połączeń opisanych w tekście V4

- Dodano C_MOTOR_HF=100 nF/50 V i C_MOTOR_MF=1 µF/50 V przy VMOTOR, wymienione w opisie V4, lecz pominięte w connections.csv.
- Dodano wszystkie trzy listwy JP4/JP5/JP6 i przewody do OEM4/5/6. Montuje się łącznie dwie zwory, według wyniku IDENTIFY.
- Dodano osobny symbol JT_LOOP dla przewodu T.10-T.11 **w adapterze**. Na płycie bazowej LOOP_OUT i INTERLOCK pozostają różnymi sieciami.
- Dodano symbole złączy OEM oraz wprost przedstawiono ciągłość ECU3/4/5/6 do EGR3/4/5/6 w adapterze L1.
- Podłączono ekran L1/L2 do masy tylko po stronie urządzenia. Koniec przy EGR ma być odizolowany. Ekran nie zastępuje przewodu odniesienia ani nie łączy się z masą sensora.
- Trzy rezystory Q8_PD/Q9_PD/Q10_PD=100 kΩ były w connections.csv, ale nie występowały w automatycznie rozwiniętym BOM-passives.csv. Są narysowane i wpisane do uzupełnienia BOM. Oznaczenia zachowano dla identyfikowalności; są to rezystory, nie dodatkowe tranzystory.
- STATUS_LED z MCP otrzymała zewnętrzną LED i rezystor 1 kΩ. Brak migania nie jest dowodem awarii: zachowanie zależy od implementacji portu firmware.
- Dodano 100 nF przy VIO transceivera CAN oraz lokalne kondensatory wejść/wyjść obu przetwornic. Ich ESR, skuteczną pojemność i zgodność z wymaganiami rzeczywistego modułu sprawdź podczas odbioru.

U1 pin 9 to CONVST, a pin 10 to WR. Opis `CONVST_A=CONVST_B` w starym wierszu pinout.csv nie dotyczy podstawowego AD7606B. Schemat S1 stosuje AD7606B z WR na 3V3_IO i OS=111. Nie przenoś tego połączenia bezpośrednio na zwykły AD7606. [Karta AD7606B](https://www.analog.com/media/en/technical-documentation/data-sheets/AD7606B.pdf).

## 4. Granice dokumentacji wykonawczej

Waveshare: oznaczenia przy symbolu M1 to numery GPIO, nie kolejność pinów złącza. Trzeba potwierdzić nadruk i rewizję posiadanej płytki oraz odłączyć RGB z GPIO38. M3/M4 mają zaciski opisane VIN/GND/VOUT - ich fizyczny rozkład sprawdź na kupionym module. RSH ma zaciski funkcjonalne P1/P2/K1/K2; dobierz rzeczywisty czterokońcówkowy bocznik i footprint.

Zachowano niezależne 3V3_IO i regulator pokładowy Waveshare zgodnie z V4. Nie wolno ich połączyć równolegle. Nie rozstrzygnięto pomiarem, czy określona kolejność zaniku szyn powoduje zasilanie pasożytnicze przez IO. Odbiór z V4 nadal obowiązuje; jeśli ten test nie przejdzie, przed użyciem w aucie potrzebne będzie uzupełnienie obwodu zasilania/sekwencjonowania.

M5, M2, Waveshare oraz moduły MAX31856 są podzespołami kupnymi. PDF przedstawia komplet połączeń pomiędzy nimi oraz elementy zewnętrzne, bez kopiowania ich wewnętrznych schematów. Wewnętrznych elementów EVM nie liczy się ponownie w BOM poza wskazaną modyfikacją OVP. Nie wykonano PCB ani uruchomienia elektroniki.
