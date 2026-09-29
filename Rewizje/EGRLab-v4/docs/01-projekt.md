# Projekt elektryczny EGRLab v4

Kia Sportage 1.7 CRDi 2013 / EGR 28410-2A850. D4FD i EDC17C08 wynikają z materiałów projektu; konkretny schemat auta dobierz po VIN. Piny1/3 jako napęd przyjęto według użytkownika. Piny4/5/6 rozpoznajemy pasywnie przy ECU. Nie ustalamy polaryzacji przez podawanie napięcia na nieznane piny.

## Architektura

```text
ECU ─ adapter L1 (ciągłość pięciu obwodów) ─ EGR
       pin1 przez RSH_L; reszta wprost
       odczepy z rezystorami przy EGR ─────────┐
L2: alternatywnie sondy bez rozpinania złącza ─┤
                                             ├ KMEAS ─ AD7606B ─ SPI2 ─ ESP32-S3
TEST: VNH5019 ─ RSH_T ─ osobny adapter T ─ EGR│                      ├ PSRAM 8 MiB RAW
      KSENSOR ─ 5V i masa sensora ────────────┘                      ├ SD / TC1 / TC2
INA240×2 ─ KCUR ─ CH6; VPROT ─ CH7; AUX HI/LO ─ CH8                 ├ CAN odbiór
                                                                    └ UART / Wi-Fi TEST
B+ ─ F1 ─ TVS ─ LM74800 OVP ─ VPROT ─ DC/DC
                                  └ F4 ─ KPWR(NO) ─ VMOTOR
STOP + interlock + okna + watchdog ─ SAFE_N ─ fizyczny ARM ─ bramki
```

Trzy mechanicznie niezamienne gniazda L1, L2 i T; jednocześnie tylko jeden adapter. L1 nie ma przewodowego połączenia z wyjściem VNH5019. Odczepy o dużej impedancji zbiegają się na wejściach ADC; nie jest to izolacja galwaniczna. T ma12 styków: musi przenieść też pięć niezależnych odczepów pomiarowych. Numeracja panelu różni się od numeracji EGR.

## Zasilanie

F1=5A przy źródle; SM8S24CA między BAT_FUSED a B−. LM74800EVM-CD: **J6 2–3, cutoff**. Fabryczne 37,5V jest za wysokie. Dzielnik OV górny47,5kΩ/dolny3,48kΩ, 0,1%, daje nominalnie18,03V przy progu1,231V. Zidentyfikuj rzeczywiste rezystory po węzłach OV/wybrana szyna J6/GND na schemacie rewizji EVM; nie pomyl z VIN_MON. Po pomiarze dopasuj górny rezystor tak, aby odcięcie następowało przy **17,5–18,5V**; tolerancja wewnętrznego progu nie gwarantuje tego okna dla samej wartości nominalnej. Zmierz też próg powrotu i odpowiedź na skok napięcia.

Bazowy EVM ma tor5A. F1 nie może być10A bez przebudowy i odbioru stopnia mocy. F2/F3=1A zasilają TSR2-2450 i TSR2-2433. TVS24V sam nie chroni wejścia TSR o maksimum36V. Brak gwarancji podtrzymania podczas cold-crank; zanik kończy sesję. Nie deklarujemy badań ISO7637/16750.

5V_SYS: Waveshare wejście5V, CAN VCC, cewki, U11 i niezależny nadzór 5V_A. 5V_A przez1Ω+470µF: ADC, INA240, komparator prądu. 3V3_IO z osobnego TSR: logika zewnętrzna, ADC VDRIVE, SD, TC, MCP, CAN VIO. **Nie łącz 3V3_IO równolegle z wyjściem regulatora Waveshare.** Złącza łącz bez napięcia. Odbiór wymaga sprawdzenia sekwencji zasilania i braku podtrzymywania MCU przez IO przy zaniku5V_SYS; jeśli występuje, potrzebne są bufory Ioff lub wspólne sterowane zasilanie przed dopuszczeniem układu do auta.

Jedyny przewód masy do auta: J_PWR.2 → B− akumulatora. AGND/DGND/PGND spotykają się przy GND_STAR na płycie; prąd motoru nie wraca ścieżką ADC. Masa sensora jest mierzona przez99,8kΩ, a nie zwarta do masy urządzenia. OBD: tylko6/14; **4/5/16 NC**. Odniesienie CAN przez główne B−. USB izolowane albo laptop na akumulatorze, bez dodatkowego VBUS; sprawdź schemat CH343 danej rewizji. BNC nie może zwierać mierzonej masy sensora/GUD09 do B−.

## Mostek i prąd

Pololu1451/VNH5019; VMOTOR przez F4=5A i KPWR NO. VMOTOR:1000µF50V+1µF+100nF, SMCJ18A i2,2kΩ/0,5W. TVS jest do krótkiej energii regeneracji, nie ciągłego hamowania. PWM start1kHz. INA/INB z MCP przez330Ω z pull-down47kΩ. PWM po bramce sprzętowej. VDD pull-upów ENA/ENB nośnika z MOTOR_PERMIT, nie ze stałego3,3V.

RSH_T/RSH_L=5mΩ≥2W, cztery wyprowadzenia Kelvin, TCR≤50ppm/K. INA240A2 SOIC-8: gain50, REF1=5V_A, REF2=AGND. I=(Vout−Vzero)/0,25. Kelvin przez dobrane10Ω. Zakres common-mode −4…80V sprawdź skopem podczas recyrkulacji ECU. Nasycenie wzmacniacza przed ADC wymaga oddzielnego odbioru.

KCUR przełącza jedynie wyjścia INA na CH6; własna cewka. KMEAS nie przełącza fabrycznych obwodów ECU. L2 i bocznik z mostkiem wymagają `bypass 1` — prąd wtedy nieważny.

U18 TBD62083APG: sink cewek KMEAS1–3 razem, KCUR, KSENSOR, KPWR. COM NC; osobne diody dla cewek5V; dla KPWR dioda szeregowo z Zener18V. Wejścia mają100kΩ do masy. Nie zamieniaj DMOS na Darlington bez przeliczenia spadku napięcia. KPWR cewka≤150mA, styki≥20A, bez wbudowanej diody; zmierz pickup i release.

## Sprzętowe bezpieczeństwo

SAFE_N: dokładnie jeden pull-up10kΩ przez NC STOP i100kΩ do AGND. Na węźle wyłącznie otwarte wyjścia komparatorów i dreny Q8/Q9/Q10. **SUP_N jest oddzielnym węzłem.**

- TPS3808G33 U5: SUP_N pull-up10kΩ, CT NC=20ms, resetuje /CLR U7 i MCP. U8c/Q9 przenoszą błąd na SAFE_N bez sprzężenia zwrotnego.
- CD74HC123 U7: A=0, B=GPIO21, /CLR=SUP_N, Q=WD_Q. R220kΩ do pinu15, C1µF niepolarny **między14–15**. U8a/Q8 ściąga SAFE_N przy Q=0. Timeout po pomiarze50–150ms. Heartbeat taska co10ms tylko przy świeżym ADC.
- U8d/Q10: INTERLOCK=0 ściąga SAFE_N.
- HC74 U9: /CLR=SAFE_N, D=/PRE=3,3V, CLK po przycisku ARM/HC14/RC. Powrót warunków OK nie uzbraja; potrzebne nowe naciśnięcie.
- MOTOR_PERMIT=HW_ARMED ∧ MCU_ARM ∧ INTERLOCK; PWM_OUT=PWM ∧ MOTOR_PERMIT.
- SENSOR_PERMIT=SENSOR_ENABLE ∧ TEST_KEY ∧ INTERLOCK ∧ SAFE_N. Sensor może zostać sprawdzony bez włączenia motoru.

U4 okno OC, zasilanie5V_A: I_FILT z INA TEST przez1kΩ/1nF. LOW IN+=I_FILT, IN−=0,3×5V_A; HIGH IN+=0,7×5V_A, IN−=I_FILT. Dzielniki7k/3k i3k/7k0,1%. Nominalnie±4A; próg i czas do PWM/EN low trzeba zmierzyć. Cel <20µs od utrzymanego przekroczenia; osobno zmierz czas zaniku energii motoru. Brak zworki±8A w wersji bazowej.

U6 i ADR4525 zasilane **5V_SYS**, nie nadzorowaną5V_A. Dzielnik15k/10k daje0,4×5V_A; odniesienia1,9V i2,1V z2,5V przez6k/19k i4k/21k. Nominalne okno4,75–5,25V. Brak deklaracji SIL/ASIL i odporności na każdą pojedynczą awarię.

## Czujnik, ADC, AUX

TPS2553 RILIM232kΩ, limit około0,1A — zmierzyć, nie jest to20mA. Pierwsze zasilenie znanego sensora z zewnętrznym limitem20mA. KSENSOR odłącza plus i powrót AGND_SENSOR. JP4/5/6 to trzy osobne1×3; tylko dwie zworki, feedback pozostaje bez zworki. Tabela sześciu mapowań w07.

| ADC / indeks | Tor | Zakres SW | Mnożnik nominalny |
|---|---|---|---|
| 1/0 i2/1 | motor1/3; 2×150k +100k dolny | ±10V | 4,06 |
| 3/2…5/4 | piny4/5/6; 2×49,9k | przed IDENTIFY ±10; po: supply±10, feedback±5, GND±2,5 | 1,01996 |
| 6/5 | INA aktywnego banku | ±5V | 1 |
| 7/6 | VPROT; 2×249k +100k | ±10V | 6,0796 |
| 8/7 | AUX DPDT | HI±10 / LO±2,5V | 4,06 /1,01996 |

Mnożniki uwzględniają typowe RIN5MΩ AD7606B; kalibruj całe tory. 220pF do AGND na1–5/7/8, 1nF na6. Rezystory odczepów montuj przy EGR, przed długim przewodem. AUX LO odłącza również dolny RB4. Ekran AUX do AGND urządzenia; tylko gorący styk do badanego punktu masy.

AD7606B: SPI mode2, OS=111, CONFIG0x02=0, OS0x08=3(×8), zakresy0x03–06. Odczyt rejestru0x4000|adres<<8, zapis adresu0 wraca do ADC. **Pin9=CONVST, pin10=WR** (high w naszym serial); nie kopiuj CONVST_B ze zwykłego AD7606. Pełny reset≥10µs. SW odczyt128bitów z jedną CS. Tryb legacy HW jest odrębną konfiguracją: wszystkie kanały±10V, osiem ramek16bitów. Wariant podstawowy i BOM: AD7606B; zwykły AD7606 wymaga innych współczynników.

2kS/s nie daje gwarancji uchwycenia dowolnego impulsu<1ms ani poprawnego RMS PWM1kHz. `sample_mean_20ms` oznacza średnią próbek, nie certyfikowany pomiar średniej fizycznej. FRICTION zapisuje ją dopiero po kwalifikacji, domyślnie `null`. Skop służy do kształtu PWM i kwalifikacji aliasingu.

## MCU i peryferia

N32R16V:32MB Flash OPI/16MB PSRAM OCT, wymagane potwierdzenie nadruku i test pamięci. GPIO w CSV; 0/3/45/46,35–37 i47/48 nieużywane;19/20 USB,43/44 CH343. GPIO38 SCOPE wymaga sprawdzenia wejścia RGB na rewizji płytki.

MCP0x20: A0 ADC_RESET, A1 KMEAS, A2 KCUR, A3 SENSOR_ENABLE, A4 rezerwa, A5/A6 kierunek, A7 LED. B0 key, B1 sensor fault, B2/B3 EN diag, B4 LOGGER_CLEAR, B5 TEST_PRESENT, B6 STOP auxiliary, B7 wyjście nieużywane. GPPUB=0x0E; inne wejścia mają fizyczne pull-downy. B6/B2/B3 są punktami diagnostycznymi, nie publikowanymi polami statusu. STOP działa bez MCP.

MAX31856×2 jako moduły3,3V, SPI mode1,1MHz, typK, filtr50Hz. TC1 izolowana na korpusie napędu, TC2 na kołnierzu części gazowej. Nie są to temperatury uzwojenia. Błąd daje `null`; aktywny ruch wymaga ważnego TC1.

TCAN1051V: VCC5V, VIO3,3V, S fizycznie high, TWAI listen-only500kbit/s, bez dodatkowych120Ω w aucie. Brak nadawania/ACK/adaptacji. PID0C dekodowany tylko z odpowiedzi wywołanej przez inny tester; bez niej RPM jest nieznane.

SCOPE GPIO38 przez330Ω,20µs. DHO804 wymaga zajęcia kanału analogowego; stall wykrywany po≥200ms, open po≥50ms. Okno skopu musi objąć czas przed triggerem. Wi‑Fi opcjonalne w TEST, wyłączane dla LOGGER. UART służy też kalibracji.
