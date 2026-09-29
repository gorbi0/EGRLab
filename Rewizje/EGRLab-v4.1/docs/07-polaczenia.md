# Połączenia wykonawcze v4

Do montażu używaj [kompletu schematów S1](../schemat-S1/README.md) i [uwag wykonawczych](08-schemat-S1.md); zawierają rozwinięcia i uzupełnienia list v4.

Czytaj łącznie `ic-pins.csv` (pin → sieć), `connections.csv` (elementy między sieciami), `connectors.csv` (panel) i `pinout.csv` (GPIO). Jednakowe nazwy sieci oznaczają połączenie; NC oznacza pozostawić niepodłączone. Numery układów scalonych dotyczą **widoku od góry** konkretnej obudowy z BOM, nie adaptera uniwersalnego. Numery cewek i styków przekaźników dopasuj do rysunku producenta; oznaczenia COM/NC/NO opisują stan bez zasilania.

## 1. Interlock — pełny obwód

```text
3V3_IO ─ KEY TEST.NO ─ TEST_KEY ─ LOG1.A.NC ─ LOG2.A.NC ─ T.10
                                                              [mostek tylko w adapterze T]
INTERLOCK ─ T.11 ──────────────────────────────────────────────┘
INTERLOCK ─ 10k ─ GND; INTERLOCK → GPIO42 i U8.9 oraz U10.5/U12.2

3V3_IO ─ LOG1.B.NC ─ LOG2.B.NC ─ LOGGER_CLEAR → MCP.B4
                                      └─ 10k ─ GND
3V3_IO ─ TEST presence.NO ─ TEST_PRESENT → MCP.B5 ─ 10k ─ GND
3V3_IO ─ STOP auxiliary.NO ─ STOP_PRESSED → MCP.B6 ─ 10k ─ GND
TEST_KEY → MCP.B0; TEST_KEY ─ 10k ─ GND
```

LOG1=A/B krańcówki gniazda L1; LOG2=A/B gniazda L2. Włożenie dowolnego wtyku LOGGER otwiera oba jego NC. Sekcje A/B są **niezależne elektrycznie**. Obecność T wykrywa oddzielny NO panelu, a sprzętowy loop jest przewodem wracającym z adaptera. Rozwarcie przewodu diagnostycznego B4 daje `log_present=true`, a rozwarcie T.B5 daje `test_present=false`.

| KEY TEST | Wtyk L1/L2 | Mostek T | B4 LOGGER_CLEAR | B5 przy T | INTERLOCK |
|---:|---:|---:|---:|---:|---:|
|0|brak|brak|1|0|0|
|1|brak|brak|1|0|0|
|1|brak|zamknięty|1|1|1|
|0|brak|zamknięty|1|1|0|
|dowolny|co najmniej jeden|dowolny|0|zależny od T|0|
|1|brak|przerwany przewód|1|1|0|

Q10 odwraca stan INTERLOCK przez HC14 i ściąga SAFE_N. Obwód nie ma żadnego dodatkowego pull-up na SAFE_N. Włożenie LOGGER przy trzymanym ARM musi skasować latch; późniejsze wyjęcie wtyku nie uzbraja ponownie.

## 2. Adapter T — styk po styku

Złącze panelowe T ma12 styków i inny klucz niż L1/L2. Zewnętrzna strona: wtyk pasujący do zaworu. Numery OEM1/3/4/5/6 potwierdź po oznaczeniach obudowy; nie odwracaj lustrzanie widoku styków i przewodów.

| T | Połączenie w adapterze |
|---:|---|
|1|EGR1, przewód≥1,5mm²|
|2|EGR3, przewód≥1,5mm²|
|3|5V_SENSOR → pin1 każdej listwy JP4/JP5/JP6|
|4|AGND_SENSOR → pin3 każdej listwy JP4/JP5/JP6|
|5|EGR1 przez2×150kΩ przy EGR → TAP_P1|
|6|EGR3 przez2×150kΩ → TAP_P3|
|7|EGR4 przez2×49,9kΩ → TAP_P4|
|8|EGR5 przez2×49,9kΩ → TAP_P5|
|9|EGR6 przez2×49,9kΩ → TAP_P6|
|10–11|mostek w adapterze; bez połączenia z EGR|
|12|NC|

JP4.pin2 → EGR4; JP5.pin2 → EGR5; JP6.pin2 → EGR6. Każda listwa ma układ **[+5V, środkowy pin EGR, GND]**. Zworka1–2 oznacza supply;2–3 oznacza ground; brak zworki oznacza feedback. W całym adapterze są dokładnie DWIE zworki. Przekładanie tylko bez zasilania i z wypiętym T.

| Supply OEM | Ground OEM | Feedback OEM | JP4 | JP5 | JP6 |
|---:|---:|---:|---|---|---|
|4|5|6|1–2|2–3|brak|
|4|6|5|1–2|brak|2–3|
|5|4|6|2–3|1–2|brak|
|5|6|4|brak|1–2|2–3|
|6|4|5|2–3|brak|1–2|
|6|5|4|brak|2–3|1–2|

Typowa oczekiwana funkcja feedback na4 jest wskazówką, nie powodem do nadpisania sprzecznego pomiaru. Rozbieżność wymaga potwierdzenia numeracji, wersji zaworu i poprawności adaptera. Program wymaga jednoznacznej permutacji stabilnej≥2s.

## 3. L1 inline

Fabryczna wiązka → złącze OEM adaptera → zawór. OEM3/4/5/6 prowadź wprost bez zasilania z EGRLab. OEM1 po stronie ECU → L1.1 → RSH_L → L1.2 → OEM1 po stronie zaworu. Bocznik na płycie przy INA; grube przewody pary motorowej prowadź razem. L1.3–7 to kolejno TAP_P1/P3/P4/P5/P6, z rezystorami przy punkcie pomiaru po stronie zaworu. L1.8–11 NC,12 opcjonalny ekran wyłącznie od strony obudowy urządzenia.

Przewody panelowe3–7 niosą **już ograniczone prądowo** odczepy. Wszystkie nieużyte styki NC odizoluj. Wejście tap OEM1 mierzy stronę zaworu; spadek ECU↔zawór poznajesz z INA, nie z różnicy dwóch nieistniejących kanałów napięcia. Mostek RSH_L wymaga styku≥5A i `bypass 1`. L1 dokłada rezystancję przewodów/złączy: porównaj fabryczną wiązkę, L1 z mostkiem i L1 z bocznikiem przed interpretacją usterki.

## 4. L2 back-probe

Pięć sond na OEM1/3/4/5/6 bez rozpinania złącza. Każda sonda od razu przechodzi przez swój komplet rezystorów jak w T. L2.1–5 → TAP_P1/P3/P4/P5/P6. L2.6–11 NC,12 ekran od strony urządzenia. Brak toru motorowego i sensora zasilanego przez tester. `bank 0`, `bypass 1`, `logger`. Sondy mocuj i izoluj pojedynczo.

Każdy z trzech adapterów ma własne rezystory: łącznie12×150kΩ i18×49,9kΩ, jeśli budujesz wszystkie trzy. Nie stosuj jednego kompletu dopiero wewnątrz obudowy.

## 5. AUX i zasilanie sensora

AUX DPDT: COM_A=gorący styk wejścia; HI_A przez300kΩ doCH8; LO_A przez99,8kΩ doCH8. **RB4 górą doCH8, dołem doCOM_B; HI_B=AGND, LO_B=NC.** CF7=220pF doAGND. Przełączaj bez napięcia na AUX i odzwierciedl `aux 0/1`. Firmware nie wykrywa położenia mechanicznego. LO nie służy do przewodów12V.

KSENSOR: COM_A=TPS2553.OUT; NO_A=T.3; COM_B=AGND; NO_B=T.4; oba NC niepodłączone. Cewka z5V_SYS sterowana U18.O3. TPS2553.EN=SENSOR_PERMIT; FAULT_N z pull-upem10k do3V3_IO i naB1. RILIM232k doGND. IN/OUT po1µF doAGND. Oba przewody zasilania sensora rozłączają się bez zasilania i bez interlocku.

## 6. ADC / pozostałe elementy

Pełne64 piny ADC są w `ic-pins.csv`. U1.REGCA PA/D (36/39) mają **oddzielne**1µF doAGND;44/45 zwarte,10µF doAGND;42 ma100nF. Każde AVCC i VDRIVE ma100nF przy pinie. Nieużyte DB0–6 i DB12–15 doAGND; nieużyte DOUT i FRSTDATA NC. Nie łącz REGCAP z żadną zewnętrzną szyną.

Moduły MAX31856: VIN3,3V/GND, SCK4/MOSI5/MISO6, CS8/16. Karty SD: CLK4/DI5/DO6/CS7, VDD3,3V. Moduł TC musi mieć aplikacyjne filtry wejścia i kompensację zimnego końca zgodnie z producentem; nie jest dopuszczony dowolny moduł z logiką5V. RezystoryCS10k do3V3_IO. I²C SDA10/SCL15 z4,7k do3V3_IO.

Schemat logiczny `safety.svg` pokazuje działanie; o połączeniu nóżek rozstrzygają CSV. Nie wykonano ERC/DRC CAD ani prototypowej płytki. Kontrola ciągłości i polaryzacji każdej wiązki jest etapem0 odbioru.
