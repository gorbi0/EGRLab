# P08-R1 — zakres niezależnej recenzji

Zacząć od `requirements/KONTRAKT.md`, `PROJEKT.md` i `ZMIANY.md`. Otworzyć finalny projekt `eda/P08.kicad_pro`; PDF są pomocą do przeglądu. Wyniki bieżących kontroli i zakres testów zapisano w `verification/QA.md`.

Proszę szczególnie sprawdzić:

1. Pinout TPS2553, MCP120 w TO-92, TBD62083 oraz obu torów i polaryzacji cewki G6K. Footprint G6K jest lokalnie poprawiony względem biblioteki KiCad: otwory 2/7 w 3,2 mm, nie 3,0 mm.
2. Zachowanie podczas rozdzielnych zaników 5 V i 3,3 V: U8 oraz dzielnik R15/R16, Ioff buforów i pull-downy. Pomiary ramp na sprzęcie nadal są konieczne.
3. Rzeczywiste znaczenie OK/HEALTHY. Brak sprzętowego zatrzasku FAULT jest jawny; odpowiada za niego CORE. Dodatkowy U8 wymaga 750 ms stabilnej gotowości przed pierwszym PERMIT. Zmiana wspólnego firmware pozostaje zadaniem integracji.
4. Limit TPS: R1=232k/1%, około 117 mA typowo, około 99–139 mA z równań producenta. Nie mylić go z początkowym limitem 20 mA do identyfikacji sensora.
5. K1 rozłącza plus i powrót. R18 jest między obiema szynami wyjściowymi, nie do GND. Przy pomiarach masa oscyloskopu może obejść rozłączany styk.
6. Interfejs SENSOR ma sześć pozycji zgodnie z P04-R2.1. Pinouty są porównywane z migawkami P02/P03/P04. P11 nie jest jeszcze płytką zatwierdzoną; W4 jest przypisana do jej BOM.
7. Mechanika konkretnych MPN, wtyki i kotwy. Molex 39-29-6028 ma rozstaw rzędów otworów PCB 5,5 mm, chociaż rodzina złącza nosi nazwę 4,2 mm. Rysunek Molex SD-5566-002 jest w reference/datasheets/Molex-5566-drawing.pdf, strony 13–14.
8. Rzeczywisty margines załączenia cewki przy sterowaniu TBD62083 z 3,3 V, rozrzut limitu prądu i czas wyłączenia/rozładowania. ODBIOR.md nie zawiera zmyślonych wyników pomiarów.

Płytka jest prototypem do uruchamiania na stole. Pakiet nie deklaruje kwalifikacji automotive, dopuszczenia pracy z ECU ani zakończonego odbioru sprzętu. Starsze płytki i firmware nie zostały zmienione przez to wydanie.
