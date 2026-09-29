# P04-R2.2 — reset z CORE

Jedyna zmiana elektryczna: **R17 100 kΩ -> 10 kΩ ±1%, MFR-25FRF52-10K**. R17 jest pomiędzy SUP_N a GND, przed U9.5. R30 po stronie wyjścia U9 pozostaje 100 kΩ. Obciążenie źródła resetu rośnie do około 0,33 mA; P03-R5 dostarcza sygnał przez U6 i R41=220 Ω.

Przy wyłączonym CORE konserwatywne 30 µA sumy modułów upływności × 10,1 kΩ daje 0,303 V < VIL=0,8 V. Nie jest to prognoza zmierzonego napięcia ani kierunku upływu. Szczegóły: KONTRAKT-RESET.md.

Zmieniono generator, schemat, BOM, PCB (wartość i numer nadruku), PDF, oczekiwania niezależnej kontroli wartości i jej mutację: powrót R17 do 100 kΩ jest teraz wykrywanym błędem. Dodano kontrolę budżetu resetu i ścisłe porównanie geometrii z R2.1. Schemat logiczny, miedź, wiercenia, obrys, rozmieszczenie, złącza i firmware bez zmian.

Oryginalne P04-R2.1 i P03-R4 zachowane. Nowe wydanie zawiera zamrożony punkt odniesienia w reference/previous-release. Historyczne zamknięcie R2.1 nie stanowi pomiarowego zaliczenia R2.2.
