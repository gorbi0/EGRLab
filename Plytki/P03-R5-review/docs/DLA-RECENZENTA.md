# P03-R5 — kolejność kontroli

1. ZMIANY-R5.md i ZASILANIE-RESET.md: U4 LVC1G37, R17 na sąsiedniej P04, poprawione granice obliczeń.
2. POWER w PDF P03-R5-schemat.pdf: pinout i rodzaj wyjść U4/U6; BOM i karta LVC1G37.
3. verification/revision-checks.json: tylko U4 i numer nadruku; miedź, wiercenia i wylewki R4 zachowane.
4. verification/reset-budget.json: wartości z netlisty; próby cofające U4 i R17 do poprzedniego stanu muszą zawieść.
5. B2B-STATUS.md i ODBIOR.md: oddzielić potwierdzoną geometrię CAD od niewykonanej przymiarki i pomiarów.

Zmiana to para P03-R5 + P04-R2.2. Firmware i P05 nie są zmieniane; P07 HOLD.
