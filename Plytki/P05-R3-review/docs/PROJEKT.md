*R3 (1.10.2026, format S1): złącza do innych płytek to J_BP1/J_BP2 przez P12; punkty pomiarowe na listwach J_SV1/J_SV2. Obwód jak w R2.*

# Projekt elektryczny P05-R1

## Zakres

P05 mierzy napięcia, nie zasila silnika EGR i nie przełącza jego prądu. P06/P07 mierzą prąd lokalnie przez MCP3201; kanał CH6 AD7606B pozostaje terminacją zera. Osiem jednoczesnych kanałów i dodatkowe pomiary prądu łączy firmware według znaczników czasu.

```text
P02 5V_SYS -> R1 1R -> 5VA_P05 -> AD7606B AVCC
                           +-> MCP1700 -> 3V3_DAQ -> VDRIVE, bufory, HC08
P03 R6 J_BP2 (przez P12) -> J_BP2 -> bufory Ioff -> SPI/CONVST/RESET -> ADC
ADC DOUT/BUSY -> bufory Ioff -> J_BP2 -> P12 -> P03
P11 TAPS -> K1..K3 NO -> filtry -> CH1..CH5
GND -> 10k -> CH6; P02 R4 J_BP.20 -> P12 -> J_BP1.10 (akumulator auta, VBAT_SENSE) -> dzielnik -> CH7; AUX HI/LO -> CH8
okno 5VA & supervisor 3V3 & supervisor 5V -> DAQ_OK -> P04
MEAS_EN & DAQ_OK -> TBD62083 -> cewki K1..K3
```

## Zmiany i uzasadnienia

1. U12 MCP1700-3302E/TO tworzy lokalne 3V3_DAQ z 5VA_P05. R3: 3V3_IO nie wchodzi na P05 (dawny LV05.3 był tylko punktem kontrolnym). Nie łączyć 3V3_DAQ z żadną szyną z P12. Rozwiązuje to przypadek prawidłowo zasilonego VDRIVE przy wyłączonym AVCC z osobnego źródła. C1 470µF oraz R2 1k pomagają przy zaniku zasilania. To nie jest dowód zgodności przebiegu przy twardym zwarciu AVCC: VDRIVE ≤ AVCC+0,3V trzeba sprawdzić oscyloskopem, także przy wyłączaniu i szybkim ponownym załączeniu.
2. Bufory U8–U11 Nexperia 74LVC125AD,118 mają funkcję Ioff. Po obu stronach odbiorników są rezystory określające stany spoczynkowe. CS jest H, pozostałe wejścia L. U11A włącza DOUT tylko przy aktywnym CS. Dodano bufor BUSY i rezystory wyjściowe 33Ω. Nie zastępować tych układów zwykłym HC125.
3. U5C sprzętowo blokuje cewki przy niepoprawnym DAQ_OK. Układ nie czeka na reakcję programu. Nie jest jednak natychmiastowym odłączeniem odczepów: przekaźniki i diody gaszące wydłużają zwolnienie; rezystory ograniczające w adapterach są wymagane również w tej krótkiej fazie.
4. K1–K3 to **G6K-2P-Y DC5, THT**. Nie kupować G6K-2F-Y SMD do tych footprintów. U4 COM ma połączenie z 5V_SYS; dodatkowe diody są przy cewkach. Trzy cewki 5V pobierają nominalnie łącznie około 60mA. Driver TBD62083APG jest sterowany 3,3V; wersja 62084 ma inny wymagany poziom wejścia.
5. **R2:** R5=6,04k, R6=20k, R7=5,11k, R8=24,9k dają okno 4,800–5,186V (w R1 5,90k/5,23k: 4,826–5,165V, węższe niż tolerancja TSR 2-2450). Obliczenie obejmuje tolerancję rezystorów 0,1%, niezależne TCR ±25ppm/K, Vos ±5,5mV, Ib 20nA i budżet referencji 0,115% (REF5025IDR). Daje progi dolne 4,752–4,849V i górne 5,137–5,234V. **R3:** rezystory okna 1206 0,1 %/10 ppm/K (RT1206BRB07) z zapasem 0,1 % na lutowanie i starzenie: dolny 4,756–4,845 V, górny 5,141–5,230 V (README „Okno DAQ_OK”). To statyczny model przyjętych granic, a nie pomiar ani gwarancja dla impulsów. Nie stosować w tym oknie rezystorów 1%. Przy napięciu bliskim progowi możliwe jest drganie DAQ_OK: nie dodano dodatniego sprzężenia/histerezy, aby nie przesuwać granic bez ponownego przeliczenia.
6. U2 **REF5025IDR** (klasa wysoka: 0,05%, 3ppm/K; w R1 ADR4525BRZ, niedostępny do 2027) służy tylko komparatorom. Wyprowadzenia: 2 VIN, 4 GND, 6 VOUT (C24 1µF, karta REF50xx wymaga 1–50µF); 1/8 DNC, 3 TEMP, 5 TRIM/NR, 7 NC wolne. **REF5025AIDR (klasa standardowa 0,1%, 8ppm/K) nie był zamiennikiem w R2:** dolny narożnik okna spadał do 4,748V < 4,75V (w R3 przy 10 ppm/K mieściłby się z zapasem 1,6 mV; U2 zostaje REF5025ID(R) według decyzji 29.09). ADC korzysta z własnej referencji. Piny REGCAP 36 i 39 mają oddzielne 1µF; REFCAP44/45 są zwarte. C12/C13 wybrane jako 22µF/25V X7R 1210, z wymaganiem efektywnej pojemności ≥10µF po uwzględnieniu napięcia, tolerancji i temperatury. Kandydat MPN jest w BOM; spełnienie warunku Ceff nie zostało tu zmierzone i jest punktem kwalifikacji części.

Podstawy: [AD7606B Rev.B, pinout i reset](https://www.analog.com/media/en/technical-documentation/data-sheets/AD7606B.pdf), [TLV1702-Q1](https://www.ti.com/lit/ds/symlink/tlv1702-q1.pdf), [REF50xx](https://www.ti.com/lit/ds/symlink/ref5025.pdf), [MCP1700](https://ww1.microchip.com/downloads/aemDocuments/documents/APID/ProductDocuments/DataSheets/MCP1700-Data-Sheet-20001826F.pdf), [MCP120](https://ww1.microchip.com/downloads/en/DeviceDoc/11184d.pdf), [74LVC125A](https://assets.nexperia.com/documents/data-sheet/74LVC125A.pdf), [G6K](https://components.omron.com/sites/default/files/datasheet_pdf/K106-E1.pdf), [TBD62083](https://toshiba-semicon-storage.com/info/TBD62083APG_datasheet_en_20160511.pdf?did=29893&prodName=TBD62083APG).

## Kanały i kalibracja

| ADC | Funkcja | Tor przed ADC | Nominalny mnożnik |
|---|---|---|---:|
| CH1 | motor pin1 | 300k w adapterze, 100k na P05 | 4,06 |
| CH2 | motor pin3 | 300k w adapterze, 100k na P05 | 4,06 |
| CH3 | feedback pin4 | 100k w adapterze, bez dolnego 100k | 1,02 |
| CH4 | pin5 | jak CH3 | 1,02 |
| CH5 | pin6 | jak CH3 | 1,02 |
| CH6 | zero diagnostyczne | 10k do GND | nie dotyczy |
| CH7 | VBAT_SENSE | 499k/100k | 6,0898 |
| CH8 HI | AUX do ±30V roboczo | 300k/100k | 4,06 |
| CH8 LO | AUX do ±5V roboczo | 100k, bez shunta | 1,02 |

Mnożniki uwzględniają typową rezystancję wejściową 5MΩ. Nie zastępują kalibracji: model wejścia odniesionego do około 2V przewiduje także offset. Szacowany offset odniesiony do źródła wynosi 120mV dla motor/HI, 40mV dla sensor/LO i 200mV dla VSENSE. Nie odejmować tych wartości „na sztywno”; zmierzyć zero oraz co najmniej drugi punkt dla każdego toru, banku i zakresu. Kalibrować z właściwym adapterem i wiązką. CH6 przez 10k również nie daje idealnego kodu zero.

To wejścia względem wspólnej masy, nie izolowane pomiary różnicowe. Napięcie silnika oblicza się jako skalibrowane CH1−CH2. Odwrócenie 5V/GND pinów5/6 jest rozpoznawane przez LOGGER/IDENTYFIKACJĘ, nie przez podawanie próbnego zasilania na nieznany pin. P05 tylko dostarcza pomiarów.

P05 nie zawiera rezystorów 300k/100k znajdujących się przy źródłach w adapterach AT/AL1/AL2. Podanie surowego motoru na J4 zmienia skalę i usuwa przewidziane ograniczenie prądu. VBAT_SENSE (J_BP1.10) jest ograniczony po stronie P02 R4 (10 kΩ + P6KE24CA). Pozycje NC w wiązkach mają pozostać nieobsadzone.

220pF daje zewnętrzne bieguny około 7,4–9,8kHz, zależnie od kanału. To filtr wejściowy, który nie eliminuje aliasingu przy zapisie 2kSPS. Do oceny PWM/szpilek potrzebny jest tryb szybszy lub równoległy oscyloskop. Oversampling ADC i późniejsze filtrowanie/decymacja muszą odpowiadać celowi badania; przy porównaniu motor/feedback uwzględnić różne opóźnienia torów.

## Zasilanie i montaż

Zakładany przydział P05: 5V_SYS **0,20A ciągle**, test rozruchowy z limitem początkowo 0,10A i podniesieniem do 0,25A po sprawdzeniu braku zwarć. Cewki pobierają zasilanie przed R1. Dla roboczego budżetu gałęzi filtrowanej 80mA spadek R1 wynosi 80mV, moc 6,4mW; 1W jest przewymiarowaniem i ułatwia zniesienie rozruchu, ale należy sprawdzić dopuszczalny impuls dla wybranego MPN. Energia ładowania 470µF do5V wynosi około5,9mJ. U12 ma przy 25mA około43mW strat. Budżet uwzględnia zapas, nie zastępuje pomiaru całej płytki.

U1 LQFP0,5mm oraz U3 VSSOP0,65mm są lutowane bezpośrednio; w ich rejonie uzasadnione są krótkie elementy SMD. R3: rezystory SMD 1206 (poza posiadanymi MF0207 47k i 4,7k na stojąco i R1 1 W leżącym), każdy pojedynczy, pełnej wartości. Układy DIP i TO92 są THT. Szczegóły odsprzęgania i odległości zawiera raport PCB. Długie przewody analogowe nie są zastąpione magistralą I²C: przetwarzanie pozostaje lokalne na P05, a połączenie cyfrowe z CORE jest bez kabla.
