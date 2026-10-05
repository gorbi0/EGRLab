# Działanie P08-R2 (obwód R1 bez zmian)

*R2 (5.10.2026, format S1): obwód, wartości i obliczenia jak w R1 — kontrola `R1-CIRCUIT-PARITY` porównuje netlistę z `reference/P08-R1.xml` pin po pinie. Zmieniły się tylko złącza (J_BP na krawędzi A zamiast wiązek LV08 / SENSOR / SFAULT, J4 jako pole przewodów do portu TEST), punkty pomiarowe (listwa J2 z R19–R29) i obudowy części (S1). Opis poniżej pochodzi z R1; „P02”, „P04”, „P03” oznaczają teraz połączenia przez P12, a „J4” — parę przewodów do portu TEST. Sekcja „Interfejsy i montaż”: J4 nie jest już złączem Mini-Fit, U4/U5 lutowane wprost od góry, R1–R18 bez R15/R16 to SMD 1206.*

```text
P02 5V_SYS ── TPS2553 ── SENSOR_LIMITED ── K1 COM3/NO4 ── 5V_SENSOR ── P11
P02 GND ──────────────────────────────── K1 COM6/NO5 ── AGND_SENSOR ── P11
                            R18: 10k między dwiema żyłami WYJŚCIA

P02 3V3_IO ── MCP120-300 ── SUP3_N ─┐
P02 5V_SYS ── MCP120-450 ── LVC125 ─┴─ AND ── SENSOR_OK ── P04
P04 SENSOR_PERMIT ── LVC125 ── AND(SENSOR_OK_LOCAL) ── SENSOR_LOCAL
                                                      ├─ TBD62083 ── K1
                                                      └─ 4k7/6k8 ── TPS_EN
P02 3V3_IO ── dodatkowy MCP120-300 U8 ────────────────────────┘ reset OD

SENSOR_OK_LOCAL AND TPS_FAULT_N ── LVC125 ── SENSOR_HEALTHY ── P03
```

P08 nie mierzy pozycji, nie identyfikuje pinów 5/6 i nie zasila czujnika w LOGGER. Za połączenie do zatwierdzonego profilu zaworu odpowiada adapter/P11. P04 kwalifikuje zezwolenie z CORE. SENSOR_OK nie zależy od PERMIT ani od K1: brak pętli, w której nie można uruchomić zasilania, dopóki nie jest uruchomione.

## Parametry i obliczenia

Wejście z P02: 5V_SYS nominalnie 5 V, projektowy zakres 4,75–5,25 V; 3V3_IO nominalnie 3,3 V. P08 nie jest regulatorem dokładnego napięcia 5,000 V i nie wolno zasilać go z akumulatora. Budżet: 200 mA z 5 V, 15 mA z 3,3 V. Typowa cewka pobiera 21,1 mA (237 Ω ±10% przy 23°C). R17 i R18 pobierają łącznie około 1 mA, gdy wyjście jest włączone. Te prądy wlicza się do limitu TPS.

R1 = 232 kΩ ±1%, pojedynczy rezystor, maksymalna nominalna wartość zalecana przez TI. Wzory TI (R w kΩ, I w mA):

```text
Imin = 25230 / R^1.016
Ityp = 23950 / R^0.977
Imax = 22980 / R^0.94
```

Po uwzględnieniu tolerancji R: **98,67 / 117,01 / 138,64 mA**. To obliczenie projektowe z krzywych granicznych, nie pomiar gotowej płytki. U1 pracuje w trybie stałego ograniczenia prądu. Krótkie zwarcie ogranicza lokalnie; po deglitch FAULT (5–10 ms przy przeciążeniu) zgłasza błąd. Zwarcie do GND daje chwilowo do około 0,73 W w U1 przy 5,25 V i górnym oszacowaniu limitu. Nie jest to dopuszczalny ciągły tryb pracy płytki. Długie zwarcie może powodować cykle termiczne TPS.

Brak sprzętowego zatrzasku błędu. Firmware musi zatrzasnąć FAULT i wycofać zezwolenie, a przed wznowieniem wymagać świadomego resetu. **Nie łączyć FAULT bezpośrednio z EN:** samoczynne kasowanie FAULT po wyłączeniu stworzyłoby cykliczne próby. Czas całkowitego wyłączenia obejmuje detekcję TPS, odczyt MCP23017 i reakcję CORE; trzeba go zmierzyć. Gwarantowany szybki efekt lokalny to ograniczenie prądu, nie natychmiastowe mechaniczne rozłączenie.

Wyjście U1 ma RON do 135 mΩ w warunkach tabeli TI; dwa styki K1 mają po maks. 100 mΩ jako parametr początkowy w warunkach pomiaru Omrona. Przy 20 mA daje to około 6,7 mV spadku na samym U1 i stykach, przed doliczeniem przewodów i PCB. Nie utożsamiać tego rachunku z błędem całego zasilania: tolerancja 5V_SYS i zmiany styków są oddzielne. Pozycję interpretować z rzeczywiście zmierzonym napięciem odniesienia sensora.

## Start, zanik i wyłączenie

U6 obserwuje 3,3 V (próg opadania 2,85–3,00 V); U7 obserwuje 5 V (4,25–4,50 V). U7 ma pull-up do 5 V, dlatego jego wyjście przechodzi przez 5V-tolerant U4 do logiki 3,3 V. Opóźnienie zwolnienia MCP120: 150–700 ms; histereza 50 mV jest typowa, bez podanego maksimum. Próbę przy minimalnym napięciu i w temperaturze wykonać przy odbiorze.

U8 jest dodatkowym, niezależnym od bramek wymuszeniem LOW na TPS_EN przy brownout 3,3 V. R15/R16 oddzielają wyjście push-pull od resetu open-drain i dzielą napięcie w stosunku nominalnym 0,5913. Przy poprawnym sterowaniu EN wynosi około 1,95 V, powyżej VIH TPS = 1,1 V. Gdy zasilanie bramek spadnie poniżej 1 V, dzielnik daje poniżej VIL TPS = 0,66 V nawet bez pomocy resetu; margines z tolerancjami/leakage sprawdza test obliczeniowy. W pośrednim zakresie działa U8. Pomiary powolnej rampy i szybkiego zaniku pozostają obowiązkowe; parametr VOL MCP120 jest tabelarycznie określony przy VTRIPMIN, a nie jako kompletna charakterystyka każdej rampy.

U8 może zwolnić później niż U6. Po pierwszym pojawieniu się SENSOR_OK=1 i po każdym jego zaniku należy odczekać **750 ms ciągłej gotowości** przed pierwszym SENSOR_PERMIT. Przy normalnych kolejnych cyklach zasilania samego sensora, bez zaniku szyn, ten dodatkowy czas nie jest potrzebny. K1 i TPS_EN mają osobne ścieżki sterowania: w rozruchu K1 może zamknąć się wcześniej, a wyjście TPS pozostawać jeszcze wyłączone. Nie jest to uszkodzenie.

Po wycofaniu PERMIT U1 i cewka są wyłączane. D1 spowalnia zwolnienie przekaźnika względem wartości dla nieobciążonej cewki; nie obiecujemy 3 ms dla kompletnego układu. R17 rozładowuje C2 (nominalnie 10 ms); R18 rozładowuje pojemność zewnętrznego sensora **między jego własnymi przewodami**, bez obchodzenia styku masy. Czas rozładowania zewnętrznego obciążenia wynosi R18 × Czew i jest do pomiaru. K1 nie zapewnia izolacji całego pojazdu — inne tory pomiarowe P05/P11 mają własne odniesienia i impedancje.

## Interfejsy i montaż

U4/U5 wymagają Nexperia 74LVC125AD z Ioff. Bufor wejściowy chroni martwą P08 przed zasilaniem przez przewód PERMIT; bufory wyjściowe, rezystory 100 Ω i pull-down 10 kΩ współpracują z odbiornikami P03/P04. NC, nieużywane wejścia i OE są jawnie zakończone. Obie szyny są z P02; brak równoległego lokalnego regulatora 3,3 V.

K1 to monostabilny **G6K-2P-Y DC5**, nie wersja bistabilna G6KU. Cewka ma polaryzację: 1 plus, 8 minus. Rysunek Omrona dla THT jest widokiem od spodu; footprint jest widokiem z góry. Zastosowano rozstaw wzdłuż rzędu 0 / 3,2 / 5,4 / 7,6 mm i między rzędami 5,08 mm. Lokalne wyprowadzenia 2/7 poprawiono z 3,0 mm występujących w zainstalowanej bibliotece KiCad. J4: raster styków w części współpracującej 4,2 mm, ale **odstęp rzędów otworów PCB 5,5 mm**, zgodnie z rysunkiem Molex SD-5566-002.

K1 ma zakres otoczenia do +70°C. P08 jest elektroniką w obudowie testera, nie sondą do pieca: w próbie HOT-SOAK ogrzewamy zawór i mierzymy jego temperaturę, a P08 pozostaje poza strefą grzania. Zalecany zakres odbioru prototypu 0–50°C. SO14 i SOT-23-6 lutować bezpośrednio; zakupione uniwersalne adaptery SO14 nie są częścią tej PCB.

Źródła: [TI TPS2553](https://www.ti.com/lit/ds/symlink/tps2553.pdf), [Omron G6K](https://omronfs.omron.com/en_US/ecb/products/pdf/en-g6k.pdf), [Microchip MCP120](https://ww1.microchip.com/downloads/en/DeviceDoc/11184d.pdf), [Toshiba TBD62083](https://toshiba.semicon-storage.com/info/docget.jsp?did=29893&prodName=TBD62083APG), [Nexperia 74LVC125A](https://assets.nexperia.com/documents/data-sheet/74LVC125A.pdf), [Molex J4](https://www.molex.com/en-us/products/part-detail/39296028). Rysunek Molex producenta z kopii dystrybutora zapisano w `reference/datasheets/Molex-5566-drawing.pdf`, strony 13–14; aktualną część nadal przymierzyć fizycznie.
