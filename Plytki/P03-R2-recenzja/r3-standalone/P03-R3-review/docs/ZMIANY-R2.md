# Odpowiedź na recenzję P03-R1

Zmiany dotyczą konstrukcji P03. „Poprawione w CAD” oznacza zgodność schematu, PCB i sprawdzeń plikowych; nie oznacza zaliczonego odbioru przy stole.

| Uwaga | Zmiana R2 | Dowód w pakiecie | Pozostaje przy stole |
|---|---|---|---|
| P03-01 / P1 | R15–R25 ustalają źródła przed aktywnymi buforami i wejście MEAS_BANK. CS=HIGH, pozostałe=LOW. R1 i R11 zachowane. | `function-checks.json`: default …; próba usunięcia każdego rezystora | Reset, bootloader, start w obu kolejnościach zasilania |
| P03-02 / P1 | TPS3808 → SUP_RAW_N → U4 SN74LVC1G07 (OD) → R34 220R → SUP_N. SUP_N łączy EN Waveshare, RESET MCP i P04. R35 10K podciąga wspólny reset. | Kontrole wspólnego resetu, rodzaju bufora, rezystora ograniczającego; mutacje odłączenia EN i podstawienia push-pull | Zapad 3V3, ręczny reset, DTR/RTS USB; nowa sesja po restarcie, bez automatycznego ARM |
| P03-03 / P2 | 5V_SYS → dren Q1 AO3401A → źródło/5V_M1. LTC4412IS6 steruje Q1. USB pozostaje po stronie 5V_M1. | Rozdzielone sieci, jawna kontrola D/S/G i pinów U5, zamrożona miedź toru głównego | Cztery kombinacje źródeł; prąd wsteczny, zapas LDO, SD+Wi-Fi |
| P03-04 / P2 | C3 przeniesiony przy VDD=U3.6. Generator używa pinu 6. Niezależny test dodatkowo porównuje odległość do VDD i MR. | Kontrola geometrii oraz mutacja C3 do położenia z R1 przy MR | Odsprzęganie z uwzględnieniem ścieżek adaptera PA0085 |
| P03-05 / P2 | Trzy zależne footprinty zamrożone w `reference/footprints`; brak odwołania do sąsiedniego projektu. | Odtworzenie z izolowanego pakietu, raport `standalone-rebuild.json` | Brak osobnego pomiaru sprzętowego |
| P03-06 / P2 | R26–R33 ustalają wejścia przed buforami. CAN_RX=HIGH, INTERLOCK/TEST_KEY/DIAG/ADC/SPI=LOW. | Kontrole każdego wejścia i próby usunięcia rezystorów; tabela stanów | Wypinanie modułów; stan ustalony nie jest wykryciem obecności |
| P03-07 / P3 | Pięć luźniej rozmieszczonych arkuszy A3, krótki tytuł, osobne miejsca pól i złączy. | Ponowny eksport i oględziny wszystkich stron PDF | Wydruk i czytelność podczas montażu |

Dodatkowo R36–R40 (33 Ω, THT DIN0207, raster 10,16 mm) umożliwiają dopasowanie zboczy SCLK, CONVST, SDI i magistrali SPI3. Krótki fragment od wyjścia bufora do rezystora jest trasowany przed routerem i sprawdzany geometrycznie. Nie zmieniono znaczenia pinów żadnego złącza.

Pozostają ograniczenia znane z recenzji: rzeczywiste spasowanie Samtec P03–P05, obrysy kupionych modułów/adapterów, antena skierowana do środka płyty i wydajność cieplna LDO Waveshare. Nie usunięto ich zmianą limitu testu. Użycie Wi-Fi wymaga pomiaru gotowego zestawu; dla pierwszego uruchomienia zalecany USB i Wi-Fi wyłączone.

Nowe małe elementy SMD to U4 SOT23-5, U5 TSOT23-6, Q1 SOT23 i trzy kondensatory 1206. Mają wyprowadzenia dostępne z zewnątrz; nie wymagają montażu obudowy z padem pod spodem. Pozostałe rezystory pozostają przewlekane. To nie jest zastosowanie LM74800 ani powrót do gotowego modułu ochrony P01.
