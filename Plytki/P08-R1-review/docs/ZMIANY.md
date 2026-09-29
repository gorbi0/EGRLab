# R1 względem kontraktu v6.1-rc1

1. SENSOR jest zgodny z aktualną P04-R2.1: **6 pozycji**, nie historyczne 4. Piny 1/3/4 zachowują PERMIT/READY/GND; KEY2. SFAULT pasuje do P03-R2/J6, KEY3. Automatyczny test porównuje z migawkami dokumentacji sąsiednich płytek.
2. G6K-2F-Y SMD zastąpiono G6K-2P-Y DC5 THT. Funkcja styków pozostaje taka sama. W lokalnym footprintcie poprawiono otwory 2/7 na 3,2 mm. Test geometrii ma kontrolę negatywną odtwarzającą błąd 3,0 mm.
3. Dodano U8 MCP120-300, R15/R16 i C8 do wymuszania LOW na TPS_EN przy brownout, również poza prawidłowym zakresem pracy HC08. Obowiązuje czas 750 ms stabilnej gotowości przed pierwszym włączeniem i po zaniku zasilania. Nie zmieniono plików firmware poprzedniej rewizji; patrz integracja poniżej.
4. SENSOR_OK i SENSOR_HEALTHY wyprowadzone przez bufory z Ioff, rezystory 100 Ω i pull-down. Dodano pull-downy na lokalnych sygnałach; zduplikowane 10k/100k PERMIT z bazowego opisu zastąpiono jednym 10k.
5. COMMON sterownika TBD62083 podłączony do 5V_SYS, pozostawiono zewnętrzną D1 przy cewce. Nieużywane wejścia sterownika są zwarte do GND, wyjścia NC.
6. R17 rozładowuje lokalne wyjście TPS; R18 rozładowuje zewnętrzne wyjście między 5V_SENSOR i AGND_SENSOR. R18 nie obchodzi styku rozłączającego masę.
7. Wszystkie rezystory: pojedynczy element THT DIN0207. U4/U5 montowane bezpośrednio SO14; brak adapterów. C1/C2/C9 0805 1 µF, lokalne odsprzęganie 100 nF 0805, C10 22 µF THT.
8. Powstała trasowana PCB, samodzielne biblioteki, wydruk 1:1, BOM wiązek, testy niezależnej netlisty i geometrii, kontrole negatywne i odtwarzalny routing. Weryfikacja plików nie oznacza pomiaru sprzętu.

## Integracja z CORE — warunki do spełnienia

Migawka `reference/board.c` pochodzi z v6.1-rc1. `board_mode()` ma opóźnienie 100 ms przed A_SENSOR_EN; samo w sobie nie gwarantuje zwolnienia dodatkowego U8. Integracja przed pierwszym TEST musi zapewnić **750 ms ciągłego SENSOR_OK/HEALTHY przy poprawnych zasilaniach**, kasując ten czas po spadku gotowości, błędzie odczytu lub zaniku zasilania. W R1 nie wprowadzono po cichu nowego firmware do P03. Przy próbie samodzielnej zapewnia to operator; przed połączeniem całości potrzebna jest zmiana i sprawdzenie wspólnego firmware.

Dodatkowo CORE musi traktować HEALTHY=0, błąd odczytu oraz przeterminowane wejścia jako zatrzaśnięty błąd w aktywnym TEST. Usterka nie może samoczynnie wznowić cyklu. Po przejściu LOGGER→TEST i zmianie banku pomiarowego potrzebne może być ponowne ARM na P04; P08 nie zastępuje tego interlocka. Po wyłączeniu sensora odczekać na rzeczywisty zanik zasilania i powrót styków przed zmianą adaptera/mapowania. Nie ustalać pinów 5/6 na chybił trafił.

P08 SENSOR_OK informuje o szynach, HEALTHY o szynach i braku FAULT TPS. Ani jeden nie potwierdza styków K1, napięcia na sensorze czy wiarygodności pozycji. Weryfikacja pozycji i zasilania czujnika musi korzystać z P05/P11. W LOGGER brak P08 nie powinien blokować pasywnego zapisu.
