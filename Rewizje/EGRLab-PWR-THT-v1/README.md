# EGRLab PWR-THT v1

Projekt własnego modułu ochrony zasilania zastępującego M5 / LM74800EVM-CD w EGRLab v4/v4.1. Wszystkie elementy nowego modułu są przewlekane. Data: 22.09.2026.

**Status: projekt do wykonania i odbioru prototypu. Sprawdzono połączenia i obliczenia statyczne; nie wykonano pomiarów sprzętowych ani kwalifikacji automotive.** Ochrona działa analogowo, niezależnie od ESP32. Dotychczasowe katalogi projektu pozostają bez zmian.

## Co otrzymujesz

- `EGRLab-PWR-THT-v1.pdf`: schematy, połączenia, wykaz elementów i instrukcja odbioru.
- `hardware/BOM.csv`: każdy element z oznaczeniem, obudową i wymaganiami.
- `hardware/do-zamowienia.csv`: zgrupowane pozycje „nazwa; ilość szt.”, razem z materiałami montażowymi.
- `hardware/netlist.csv`: komplet połączeń pin-sieć. Nazwy sieci są globalne na wszystkich arkuszach.
- `hardware/components.json`: dane źródłowe elementów i połączeń.
- `PROJEKT.md`, `URUCHOMIENIE.md`: obliczenia, ograniczenia i pomiary odbiorcze.
- `verification/report.json`, `src/verify.py`: odtwarzalna kontrola połączeń i modelu DC.
- `svg/`: edytowalne arkusze schematu; `src/`: generatory dokumentacji.

## Wybrana konstrukcja

```
B+ --- istniejący F1 5 A --- BAT_FUSED --- D2 Schottky --- VS --- Q1 P-MOS --- VPROT
                              |                          |                  |
                         D1 15KPA24CA                 sterowanie          D3 5KP18A
                              |                          |                  |
B- ---------------------------+--------------------------+------------------+--- GND

BAT_FUSED -> D6 -> pomiar OVP/UVLO -> LM2903P + TL431 -> OK -> driver Q2...Q6
VS -> R1 + D5 -> LM2936 5 V -> komparator / wzorzec / MCP120 (start i brownout)
ENABLE -> Q7/Q8 -> FAULT_OC -> SAFE_N istniejącej płyty -> sprzętowe rozbrojenie ARM
```

Q1 to **Vishay SUP53P06-20-E3**, 60 V, TO-220AB, z określoną rezystancją przy VGS=-4,5 V. Zastępuje rozważany IRF5210: ogranicza straty i pozwala pracować przy niższym napięciu wejściowym. Jego zastosowanie jest związane z obecnością D1 oraz limitem zmierzonego napięcia VS 48 V w badanych impulsach. Nie montować zamiennie IRF5210 z pozostawionymi progami UVLO.

| Parametr | Projekt / kryterium |
|---|---|
| Instalacja | 12 V; normalna praca 10,5-16 V |
| Prąd | 5 A łącznie, po odbiorze cieplnym; bezpiecznik F1 nadal 5 A |
| OVP, narastanie VIN | 18,00 V po regulacji RV1 przy temperaturze pokojowej |
| Powrót po OVP | nominalnie 16,66 V; nie regulować jako niezależnego progu |
| UVLO, opadanie VIN | nominalnie 9,37 V |
| Start po UVLO | nominalnie 9,85 V |
| Start po pojawieniu się AUX5 | opóźnienie MCP120: 150-700 ms, typowo 350 ms |
| Odwrotne podłączenie | blokada szeregowa D2 i osobna D6 w pomiarze; próba -14 V, następnie -24 V przy ograniczeniu prądu |
| Prąd wsteczny do B+ | blokowany przez D2; pozostaje prąd upływu, zależny od temperatury |
| Nadmierne napięcie stałe | odłączenie; 24 V jest stanem błędu, nie napięciem pracy |
| Uruchamianie obciążenia | KPWR otwarty; pojemność bezpośrednio na VPROT maks. 220 uF, pobór podczas startu maks. 1,5 A |
| Temperatura modułu | projektowy zakres otoczenia 0-50°C; nie umieszczać w komorze grzania zaworu |

Wartości progów są obliczeniami nominalnymi. Dioda pomiarowa, offset komparatora i temperatura przesuwają progi. RV1 ustawia rzeczywiste 18 V na **zaciskach wejścia**, a nie napięcie po diodzie mocy. Nie obiecujemy dokładności całego odcięcia ±0,1% tylko dlatego, że takie są rezystory.

## Wpięcie do EGRLab

Oznaczenia na schematach tego dodatku są lokalne. Na przykład `PG.Q8` oznacza Q8 tego modułu, a nie Q8 istniejącej płyty.

| Nowy moduł | Istniejący projekt |
|---|---|
| J1.1 | BAT_FUSED, po F1; dawniej M5.J1 |
| J1.2 | GND_STAR; dawniej M5.J3 |
| J2.1 | VPROT; dawniej M5.J2 |
| J2.2 | GND_STAR; dawniej M5.J4 |
| J4.1 | 3V3_IO z istniejącej płyty |
| J4.2 | SAFE_N / U9 SN74HC74N pin 1 na istniejącej płycie |
| J4.3 | GND_STAR, wspólne odniesienie; nie wykonywać nowego połączenia do karoserii |
| J3 | styk INHIBIT; zwarcie pinów wyłącza moduł, normalnie rozwarte |

**J4 jest wymagane w docelowym EGRLab.** Dzięki niemu również krótki błąd zasilania rozbraja zatrzask ARM, nawet kiedy kondensatory podtrzymują 3V3_IO. Po ustąpieniu błędu wraca VPROT, ale ruch wymaga ponownego naciśnięcia ARM. J4.2 jest wyłącznie otwartym kolektorem. Nie łączyć sieci OK ani AUX5 z SAFE_N, ESP32 lub 3V3_IO.

Usuń z listy zakupów M5 LM74800EVM-CD oraz trzy rezystory przeznaczone do jego modyfikacji: 9,10 kΩ, 38,3 kΩ i 3,48 kΩ. W tym wariancie **PG.D1 15KPA24CA zastępuje stary wejściowy D1 SM8S24CA**. F1 i jego oprawa są istniejące, nie kupuj drugiego zestawu do tego samego toru.

Pozostają F2/F3/F4, KPWR, lokalne C_BULK 1000 uF, SMCJ18A przy VMOTOR oraz wszystkie blokady silnika. Pojemność 1000 uF jest za otwartym KPWR i nie wlicza się do limitu 220 uF na VPROT podczas startu modułu. Jej późniejszy prąd ładowania przez KPWR nadal wymaga kontroli; PWR-THT nie jest ogranicznikiem prądu.

ADC CH7 nadal mierzy **VPROT**, z dotychczasowym dzielnikiem i kalibracją. SENSE_RAW jest węzłem zabezpieczenia, nie nowym wejściem ADC. Zmiana nie wymaga nowego pinu ESP32 ani modyfikacji firmware. W LOGGER przewody ECU-EGR pozostają w dotychczasowym torze przelotowym; nie wolno zasilać ich z VPROT.

## Różnice względem modułu TI

Zachowane są funkcje potrzebne w tym projekcie: blokada odwrotnej polaryzacji i energii zwrotnej do B+, odłączenie OVP, sprzętowe wyłączenie oraz kształtowanie załączenia. Dodano UVLO i sygnał rozbrajający SAFE_N.

Dioda szeregowa powoduje większy spadek napięcia i wydzielanie ciepła. Zakres pracy, czasy odcięcia i parametry impulsowe nie są kopiami LM74800EVM-CD. Nie ma trybu utrzymywania wyjścia na 18 V, aktywnego limitu prądu, podtrzymania loggera przy rozruchu ani gwarancji zachowania ostatnich danych SD po odcięciu.

**Nie deklarujemy odporności na dowolny load dump ani zgodności z ISO 7637/16750.** Moc „15 kW” transila dotyczy określonego impulsu, nie ciągłego pochłaniania energii. Odbiór zwarć, impulsów i temperatur jest opisany w URUCHOMIENIE.md. Do czasu jego wykonania jest to projekt prototypu, a nie zweryfikowany samochodowy zamiennik modułu TI.
