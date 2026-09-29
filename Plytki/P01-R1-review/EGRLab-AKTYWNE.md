# EGRLab — bieżący etap projektu

Aktualizacja: 23.09.2026. Baza odniesienia: EGRLab-v6.1-rc1.

## P07 DRIVE — WSTRZYMANE

Decyzja użytkownika: zamiast Pololu 1451 rozważamy moduł z dwoma BTS7960B. Powrót do projektu P07 dopiero po otrzymaniu płytki i sprawdzeniu jej rzeczywistego wykonania. Nie zatwierdzać layoutu, nie zamawiać PCB P07 i nie kupować Pololu z dotychczasowego BOM bez ponownego rozstrzygnięcia wariantu.

Przed wznowieniem: oznaczenia układów, połączenia bufora 74HC244 i jego zasilanie, poziomy sterujące, R_EN/L_EN, sposób odczytu R_IS/L_IS, stany rozruchu/STOP, hamowanie i przebieg PWM, mechanika modułu. Zachować własny bocznik/INA240/MCP3201, lokalne OC, zatrzask i KPWR. Zmiana obejmie P07 i jego obsługę; nie stanowi zatwierdzonej zamiany pin za pin. W trybie LOGGER mostek testera nadal nie jest połączony z ECU.

## P01 PROTECT — SCHEMAT DO PRZEGLĄDU

Użytkownik zatwierdził rozpoczęcie realizacji P01. Pakiet `P01-R1-review` obejmuje schemat funkcjonalny KiCad, dobór części i footprintów, mechanikę i plan odbioru. Baza 6.1-rc1 pozostaje niezmienionym punktem odniesienia. Każda zmiana elektryczna ma osobny wpis z porównaniem połączeń.

Gotowe: trzy arkusze A3, PDF, BOM, karta wiązek i plan stref 160×100 mm. Eksport XML ma 189 końcówek zgodnych z bazą; ERC bez uwag. Otwarte przed layoutem: niezależna recenzja, dokładne mocowanie radiatorów i zamknięcie części zakupowych. Szczegóły: `P01-R1-review/docs/PRZEGLAD.md`.

Kolejność: schemat i części → przegląd konkretnego pakietu → layout PCB 2L → DRC/Gerbery/wiercenia → zamówienie → odbiór na stole. Nie oznaczać importu bloków pinowych jako gotowego schematu produkcyjnego.
