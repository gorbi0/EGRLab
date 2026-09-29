# P02-R2/R3 — zakres lokalnej zmiany PCB

*R3 (26.09.2026): geometria identyczna z R2 — te same ścieżki, przelotki, strefy, pozycje i połączenia z wylewką (sprawdza `check_revision.py`). Zmieniły się tylko napisy przy F2/F3/F4 (T1A, T1A, T500mA) i linia tytułowa; U5.9/U5.12 nadal z pełnym połączeniem, teraz wybierane po UUID z DRC.*

Zachowano format i główne sekcje R1. Przesunięto R8, R11 i TP3; dodano R18/R19/R20. Pozostałe elementy pozostają na pozycjach R1. C16 nie zajmuje miejsca na głównej PCB — jest na adapterze U5.

Tor VPROT i powrót VMOTOR utrzymują strefę wejściową oraz korytarz B.Cu bez ścieżek/przelotek. Bank, bezpiecznik i szyny LV mają zablokowane ścieżki mocy z route_critical.py. Zmieniono jedynie odgałęzienie TP3: surowy bank→R20, dalej osobna sieć HOLD_TP. Dzielniki R6/R9 nadal przy źródłach. Sygnały trasowano ponownie, następnie sprawdzono świeżym DRC i porównaniem pinów.

U5.9 i U5.12 mają bezpośrednie połączenie z masą, ponieważ dostępne geometrie termików nie dawały dwóch ramion. Dotyczy małych pól sygnałowych adaptera; pola lutowania wiązek zachowują swoje warunki. Nie obniżono reguły liczby ramion ani nie dodano wykluczeń DRC.

Wyniki i długości ścieżek są w verification/pcb-checks.json. DRC obejmuje wszystkie poziomy ważności, zgodność schematu i ponowne wypełnienie stref. Model 3D nie wchodzi do algorytmu DRC; obwiednie mechaniczne sprawdza się osobno na wydruku i fizycznymi częściami.
