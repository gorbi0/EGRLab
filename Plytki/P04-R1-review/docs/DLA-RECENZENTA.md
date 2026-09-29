# Zakres niezależnej recenzji P04-R1

To pierwsza PCB P04, nie mechaniczne przerysowanie jednej wcześniejszej PCB. Bazowy schemat v6.1 ma placeholdery footprintów; kopia i hash są w `reference/`. Wszystkie oryginalne aktywne piny ośmiu interfejsów zachowano; raport `verification/interface-scope.json` wskazuje także jawne pady NC kluczy, których bazowa netlista nie wymieniała.

Proszę zacząć od `eda/P04.kicad_sch`, a nie od renderu. W sześciu arkuszach są osobno: zasilanie, złącza, bufory, interlock, watchdog/ARM i wyjścia. `docs/PROJEKT.md` podaje uzasadnienie zmian i ograniczenia.

## Do szczególnej kontroli

1. HC123: rzeczywisty pinout, Cext pomiędzy 14/15, CLR od SUP_OK niezależne od SAFE_N, zachowanie po zwolnieniu CLR z B=H. Przy 3,3 V czas wymaga pomiaru; nie wpisano fałszywej gwarancji 99 ms.
2. MCP100-315 **D** / TO92: RESET=1, VDD=2, VSS=3. Współpraca progu z tolerancją 3V3 P02 i resetem CORE. Zachowanie obu domen podczas zaniku zasilania.
3. SAFE_N: pojedynczy pull-up przez STOP, pulldown, wyłącznie kolektory Q1–Q3/P01/P07 i wejście Schmitta. Obciążenie dodatkowych modułów, stany przejściowe, RC STOP. Nie mieszać go z cyfrowym SAFE_OK.
4. ARM: zapamiętanie tylko po nowym zboczu; powrót READY/heartbeat nie uzbraja. R2/R3/C2 zapewniają filtr, ale odbiór przycisku pozostaje otwarty. Sprawdzić także równoczesne zwolnienie resetu i ARM.
5. SENSOR_PERMIT nie wymaga HW_ARMED, nadal wymaga wszystkich READY/INTERLOCK/SAFE. MCU_ARM=0 wyłącza silnik bez skasowania fizycznego ARM — zamierzone.
6. Nexperia LVC125: wejście i wyjście każdego adaptera z pulldownem, Ioff, niewykorzystany kanał U10. C15–C17 montowane na adapterach, nie na płycie głównej.
7. Złącza oraz dostępność rzeczywistych MPN: szczególnie karta wymiarowa Würth 10p i kołki/ogonki Mini-Fit. Lista niezamkniętych przymiarek w MECHANIKA. SENSOR6 M2.2 wymaga nowej wiązki P08; CORE SAFE nie zmienia pinów.
8. Layout: pętla RC, odsprzęganie, powroty GND, własne ścieżki uzupełniające, termiki i dostęp do pól pomiarowych po montażu. Opaski 12–14,54 mm od lutów, nie przy samym cynowanym przewodzie.

## Jak sprawdzić automatykę

`verify_electrical.py` czyta **eksport KiCad XML** i łączy bramki według pinów pakietów; nie importuje `parts.py`. Oczekiwaną logikę wyjść opisano osobno. 131072 kombinacje, z policzoną liczbą stanów H każdego wyjścia; testy sekwencji reset/ARM oraz 10 mutacji. Cyfrowy model nie jest analizą analogową ani czasową.

`verify_pcb.py` uruchamia świeży native DRC dla wszystkich poziomów, z kontrolą zgodności schematu. Następnie sprawdza mechanikę/RC/decouplery/pady/klucze/kotwy i 5 mutacji geometrii lub połączeń. Raport zawiera hashe wejść; nie używa starego DRC. Zwykła zgodność BOM→netlista to dodatkowa kontrola generatora, nie substytut kontroli elektrycznej.

Proces poprawiono o jawne sprawdzenie skuteczności testów (mutacje), liczb stanów aktywnych w tablicy, odtworzenie w czystym folderze i listę niepotwierdzonych części. Sam raport autoroutera nie jest podstawą zaliczenia: brakujące połączenia zostały uzupełnione i sprawdzone przez KiCad. Do finalnej geometrii należy `routing/completion-routes.json` wraz z SES.

## Co nie jest zamknięte

Recenzja, przymiarka zakupionych części, oscyloskopowa kwalifikacja czasu watchdoga i ARM, odporność na zakłócenia w docelowej wiązce, współpraca z przyszłym P07/P08. Bez deklaracji sprawności termicznej samochodu na podstawie testów PCB. P04 nie mierzy EGR ani nie rozstrzyga przyczyny P0404 — zapewnia sterowanie warunkami testu.
