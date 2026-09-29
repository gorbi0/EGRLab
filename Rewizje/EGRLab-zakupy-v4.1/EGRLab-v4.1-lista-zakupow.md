# EGRLab v4.1 — wykaz do zamówienia

Zakres: jeden przyrząd i wszystkie trzy adaptery T, L1 i L2, według v4.1 oraz schematu S1. Ilości są montażowe, **bez zapasu i bez zaokrąglania do opakowań handlowych**. Nie doliczono posiadanego ESP32-S3 N32R16V. Wiersz „komplet” oznacza jeden kompletny zestaw, np. wtyk wraz z gniazdem i stykami.

Wybrano gotowe moduły MAX31856 — nie kupuj dodatkowo samych układów MAX31856. Pozostałe układy scalone z tabeli są osobnymi elementami. Uwzględniono zewnętrzną diodę STATUS.

Przed zakupem potwierdź konkretny model KPWR oraz obudowy i klucze złączy panelowych/OEM. Projekt określa ich funkcje i ilości, ale nie ustala numerów zamówieniowych. Trzy komplety złączy 12-pin muszą mieć trzy różne klucze. Wtyki OEM do zaworu są potrzebne dwa, a gniazdo do fabrycznej wiązki jedno; L2 korzysta z pięciu sond, nie z dodatkowego złącza OEM.

Trzy rezystory 0603 służą do ustawienia OVP w kupionym EVM. Policzone są jako wymiana, nie dodatkowy dzielnik. Rezystory 7 kΩ, 19 kΩ i 21 kΩ zamawiaj z dokładnie podaną wartością i tolerancją; nie zaokrąglaj ich do sąsiedniej wartości.

| Nazwa | Ilość szt. |
|---|---:|
|Moduł mostka H Pololu 1451 z VNH5019|1|
|Przetwornica Traco Power TSR 2-2450 — 5 V / 2 A|1|
|Przetwornica Traco Power TSR 2-2433 — 3,3 V / 2 A|1|
|Moduł ochrony zasilania TI LM74800EVM-CD|1|
|AD7606BSTZ — ADC, LQFP-64 (koniecznie wersja B)|1|
|INA240A2EDRQ1 — wzmacniacz pomiaru prądu, SOIC-8|2|
|TLV1702QDGKRQ1 — komparator podwójny, VSSOP-8|2|
|TPS3808G33DBVR — nadzorca napięcia, SOT-23-6|1|
|ADR4525BRZ — źródło odniesienia 2,5 V, SOIC-8|1|
|CD74HC123E — układ czasowy, DIP-16|1|
|SN74HC14N — inwertery Schmitta, DIP-14|1|
|SN74HC74N — przerzutniki, DIP-14|1|
|SN74HC08N — bramki AND, DIP-14|2|
|TPS2553DBVR — ogranicznik prądu zasilania czujnika, SOT-23-6|1|
|TCAN1051VDRQ1 — transceiver CAN z VIO, SOIC-8|1|
|MCP23017-E/SP — ekspander wejść/wyjść, DIP-28|1|
|TBD62083APG — sterownik cewek, DIP-18|1|
|Gotowy moduł MAX31856 do termopary K, zgodny z zasilaniem i logiką 3,3 V|2|
|Termopara K z izolowaną spoiną i przewodem kompensacyjnym|2|
|Moduł gniazda microSD SPI 3,3 V, bez translatorów do 5 V|1|
|Karta microSD High Endurance 32 GB|1|
|Tranzystor 2N7002, SOT-23|3|
|Przekaźnik Omron G6K-2F-Y DC5 — cewka 5 V, DPDT|5|
|Przekaźnik samochodowy NO 12 V, styki ≥20 A, cewka ≤150 mA, bez diody — model do doboru|1|
|Gniazdo z przewodami do wybranego przekaźnika samochodowego KPWR|1|
|Bocznik 5 mΩ / 2 W / 1%, 4 końcówki Kelvin, TCR ≤50 ppm/K|2|
|Dioda TVS SM8S24CA — dwukierunkowa|1|
|Dioda TVS SMCJ18A — jednokierunkowa|1|
|Zabezpieczenie CAN PESD2CAN, SOT-23|1|
|Dioda 1N4148|5|
|Dioda 1N4007|1|
|Dioda Zenera 18 V / ≥1 W|1|
|Dioda LED zielona, do pracy przy około 2 mA|1|
|Bezpiecznik 5 A, do instalacji DC|2|
|Bezpiecznik 1 A, do instalacji DC|2|
|Uchwyt bezpiecznika DC, zgodny z zakupionymi bezpiecznikami, ≥5 A|4|
|Rezystor 1 kΩ / 1%, 0805|2|
|Rezystor 1 Ω / 0,5 W, 1206|1|
|Rezystor 10 kΩ / 0,1%, 0805|1|
|Rezystor 10 kΩ / 1%, 0805|15|
|Rezystor 10 Ω / 0,1%, 0805|4|
|Rezystor 100 kΩ / 0,1%, 0805|4|
|Rezystor 100 kΩ / 1%, 0805|11|
|Rezystor 100 Ω / 1%, 0805|3|
|Rezystor 15 kΩ / 0,1%, 0805|1|
|Rezystor 150 kΩ / 0,1% / ≥200 V, 1206|14|
|Rezystor 19 kΩ / 0,1%, 0805|1|
|Rezystor 2,2 kΩ / 0,5 W, 1206|1|
|Rezystor 21 kΩ / 0,1%, 0805|1|
|Rezystor 220 kΩ / 1%, 0805|1|
|Rezystor 232 kΩ / 1%, 0805|1|
|Rezystor 249 kΩ / 0,1%, 1206|2|
|Rezystor 3 kΩ / 0,1%, 0805|2|
|Rezystor 3,48 kΩ / 0,1%, 0603 — wymiana M5.R4|1|
|Rezystor 330 Ω / 1%, 0805|4|
|Rezystor 38,3 kΩ / 0,1%, 0603 — wymiana M5.R3|1|
|Rezystor 4 kΩ / 0,1%, 0805|1|
|Rezystor 4,7 kΩ / 1%, 0805|2|
|Rezystor 47 kΩ / 1%, 0805|5|
|Rezystor 49,9 kΩ / 0,1% / ≥100 V, 1206|20|
|Rezystor 6 kΩ / 0,1%, 0805|1|
|Rezystor 7 kΩ / 0,1%, 0805|2|
|Rezystor 9,10 kΩ / 0,1%, 0603 — wymiana M5.R8|1|
|Kondensator 1 nF / 50 V, C0G, 0805|2|
|Kondensator 1 µF / 50 V, X7R, 0805|7|
|Kondensator 1 µF / ≥10 V / 10%, foliowy niepolarny, THT — watchdog|1|
|Kondensator 10 nF / 50 V, X7R, 0805|4|
|Kondensator 10 µF / 50 V — wejścia przetwornic TSR|2|
|Kondensator 10 µF / ≥10 V, ceramiczny X7R — REFCAP ADC|1|
|Kondensator 100 nF / 50 V, X7R, 0805|23|
|Kondensator 1000 µF / 50 V, elektrolityczny low ESR|1|
|Kondensator 22 µF / ≥10 V — wyjścia przetwornic TSR|2|
|Kondensator 220 pF / 50 V, C0G, 0805|7|
|Kondensator 470 µF / ≥10 V, elektrolityczny low ESR|1|
|Grzybek STOP zatrzaskowy, styki sprzężone 1NC + 1NO|1|
|Przycisk chwilowy NO — ARM i MARK|2|
|Przełącznik kluczykowy LOGGER/TEST, styk NO zwierany w TEST|1|
|Wyłącznik krańcowy DPDT, dwa niezależne tory NC — gniazda L1/L2|2|
|Wyłącznik krańcowy NO — wykrycie wtyku TEST|1|
|Przełącznik DPDT dwupozycyjny — AUX HI/LO|1|
|Komplet złącza blokowanego 12-pin: gniazdo panelowe + wtyk + styki; 3 różne klucze L1/L2/T, styki mocy ≥5 A|3|
|Komplet złącza zasilania 2-pin: gniazdo + wtyk + styki, ≥5 A|1|
|Wtyk OEM pasujący bezpośrednio do zaworu 28410-2A850, ze stykami/uszczelkami — obudowa do potwierdzenia|2|
|Gniazdo OEM pasujące do fabrycznej wtyczki wiązki ECU, ze stykami/uszczelkami — obudowa do potwierdzenia|1|
|Sonda back-probe izolowana — przewody OEM1/3/4/5/6 w L2|5|
|Gniazdo BNC panelowe izolowane — AUX i wyjście SCOPE|2|
|Wtyk OBD-II 16-pin z przewodem — użyte tylko styki 6 i 14|1|
|Listwa pinowa 1×3, raster 2,54 mm|3|
|Zworka na goldpin, raster 2,54 mm — mapowanie sensora|2|
|Rozłączny mostek bypass bocznika LOGGER ze złączem, prąd ≥5 A|1|
|Adapter USB–UART z logiką 3,3 V do konsoli|1|
|Rezystor mocy 12 Ω / ≥25 W — obciążenie testowe|1|
|Radiator do rezystora obciążenia 12 Ω / 25 W|1|

**Materiały zależne od sposobu montażu** — osobny plik CSV. Adaptery SMD/THT są potrzebne przy montażu na płytkach uniwersalnych; na zaprojektowanej PCB z właściwymi polami można je pominąć. Dobierz ich wyprowadzenia do dokładnych obudów. Przewody, przepusty i mocowania są zestawami do wymiarowania; dokumentacja nie pozwala uczciwie podać liczby metrów i śrub. Dla boczników, TVS i pozostałych SMD trzeba zapewnić odpowiednie pola montażowe; poniższa lista adapterów układów scalonych nie zastępuje projektu płyty.

| Nazwa | Ilość szt. |
|---|---:|
|Adapter LQFP-64, raster 0,5 mm → THT/DIP — AD7606BSTZ|1|
|Adapter SOIC-8, raster 1,27 mm → DIP-8 — INA240×2, ADR4525, TCAN1051|4|
|Adapter VSSOP-8, raster 0,65 mm → DIP-8 — TLV1702|2|
|Adapter SOT-23-6 → THT — TPS3808 i TPS2553|2|
|Adapter SOT-23-3 → THT — 2N7002×3 i PESD2CAN|4|
|Płytka adaptera SMD → THT dopasowana do Omron G6K-2F-Y|5|
|Obudowa przyrządu — rozmiar po rozmieszczeniu modułów|1|
|Zestaw płyt montażowych, dystansów i śrub — według rozkładu modułów|1|
|Zestaw przepustów i odciążeń przewodów — według obudowy|1|
|Zestaw przewodów zasilających ≥5 A, sygnałowych, ekranowanych i skrętki CAN — długości po rozmieszczeniu|1|
|Zestaw koszulek termokurczliwych i oznaczników przewodów|1|
|Przewód pomiarowy do BNC AUX z izolowaną końcówką|1|
|Przewód BNC do oscyloskopu — SCOPE_TRIG|1|

Nie sumuj tego wykazu z `BOM-passives.csv` ani z pakietami `R_MISC`, `C_MISC`, `C_ADC`, `R_OC` i `R_SUP` ze starego BOM — te same elementy są już tutaj rozpisane. W schemacie S1 są 2 kondensatory 1 nF, 7 kondensatorów 220 pF i 23 kondensatory 100 nF. Zbiorczy stary zapis `CI1–CI5` nie oznacza pięciu dodatkowych obsadzonych kondensatorów.

Nie uwzględniono nieobsadzanych D9/D10, OLED i RTC bez obsługi w firmware. Nie doliczono przełącznika SW_CAN ani listwy JP_OS: w S1 pin S transceivera CAN oraz OS0/OS1/OS2 ADC są połączone na stałe z 3V3_IO. Do mapowania sensora są trzy listwy 1×3 i łącznie dwie zworki. Przewód pętli T.10–T.11 wykonuje się z materiału wiązki.

Napięcia kondensatorów i tolerancje rezystorów ujednolicono tylko w kierunku spełniającym wymagania projektu. Pojemności efektywne ceramiki pod napięciem oraz wymagania ESR przetwornic nadal trzeba sprawdzić dla wybranego produktu. Lista nie obejmuje przyrządów warsztatowych ani niepotwierdzonych zapasów.

Źródła: `EGRLab-v4.1/hardware/BOM.csv`, `hardware/BOM-passives.csv`, `hardware/ic-pins.csv`, `hardware/connectors.csv`, `schemat-S1/BOM-uzupelnienia-S1.csv` i model elementów S1. Przypisania oznaczeń do wierszy: `kontrola-ilosci.json`.
