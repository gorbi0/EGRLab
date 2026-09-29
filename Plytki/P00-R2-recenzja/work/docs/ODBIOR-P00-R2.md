# P00-R2 - uruchomienie i odbiór

Egzemplarz / data / wykonawca: ____________________

Status wszystkich poniższych prób: **NIEWYKONANE**. Wyniki ERC/DRC i obliczenia nie wypełniają tego formularza. Potrzebne: miernik, oscyloskop, zasilacz z ograniczeniem prądu, rezystory testowe 10 kΩ i 5,1 kΩ (lub dwa 10 kΩ równolegle), pomiar temperatury.

## Uruchamianie etapami

1. Przed lutowaniem wydruk 1:1: belka 100 mm, obrys 115 x 70 mm, przymiarka U2, C4/C6, przełączników, podstawki i J10. Sprawdzić omomierzem kierunek przełącznika Würth. Obejrzeć stronę taba TO-220, polaryzacje LED i kondensatorów.
2. Wlutować J10, D1, U2, C4-C7, R5 i R6 oraz LED10 z RL10. U1 pozostaje wyjęty, przełączniki w L/STOP. R5 jest wymagany już w tym etapie. Zmierzyć rezystancję R5/R6 przed montażem; późniejszy pomiar w obwodzie może być zakłócony innymi gałęziami.
3. Zasilacz 9 V, ograniczenie początkowo 30 mA. Jeśli po naładowaniu kondensatorów ogranicza prąd, zatrzymać próbę i sprawdzić montaż. Zmierzyć 3V3 i jego przebieg. Sprawdzić również 6 V i 15 V.
4. Wlutować pozostałe elementy i podstawkę, skontrolować przerwy i zwarcia, wyłączyć zasilanie, włożyć TLC555CP. Ograniczenie prądu do pełnych prób 100 mA. Sprawdzić wszystkie kanały bez obciążenia i z rezystorami testowymi.
5. Zmierzyć heartbeat oraz stany RUN/STOP. Do P04 przejść dopiero po odbiorze samego P00 i sprawdzeniu mapy wiązki.

## Wyniki do wpisania

Kryteria tętnień, amplitudy z zapasem i temperatury poniżej są przyjętymi kryteriami odbioru tego prototypu, nie dodatkowymi gwarancjami producenta układu.

| Próba | Kryterium / sposób pomiaru | Wynik |
|---|---|---|
| Wymiary i części 1:1 | Belka 100 mm; wszystkie części mieszczą się, brak naprężania nóżek | __________ |
| Polaryzacja i R5/R6 | R5 560 Ω ±1%, R6 1 Ω ±1%, uwzględnić przewody miernika dla 1 Ω | __________ |
| Zasilanie 6 V | TP3 za D1 co najmniej 4,75 V, bez ograniczenia prądu zasilacza | __________ |
| 3V3 bez U1 | 3,14-3,46 V przy 6 / 9 / 15 V na J10 | __________ |
| 3V3 z U1, L/STOP | 3,14-3,46 V, brak trwałych oscylacji | __________ |
| 3V3, wszystkie H/RUN | Jak wyżej; także po dołączeniu odbiorników testowych | __________ |
| Tętnienia | Cel ≤50 mVpp, pasmo pomiaru 20 MHz, krótka masa sondy; zapisać warunki | __________ |
| Skok obciążenia | Przełączanie kanałów z 10 kΩ do GND; brak podtrzymywanego dzwonienia/oscylacji | __________ |
| J1-J8 bez obciążenia | Każdy H blisko zmierzonej szyny 3V3, L blisko GND | __________ |
| J1-J8 z pulldown 10 kΩ | H nominalnie 3,0 V; zapisać min/max dla 8 kanałów | __________ |
| Kanał z obciążeniem 5 kΩ | H nominalnie 2,75 V; cel ≥2,5 V | __________ |
| Zwarcie wyjścia do GND | Pojedynczy kanał przez własny 1 kΩ: około 3,3 mA; LED nadal pokazuje H źródła | __________ |
| Heartbeat RUN | Częstotliwość orientacyjnie 80-125 Hz, nominalnie 102 Hz; zapisać f i duty | __________ |
| Heartbeat obciążony | Po R3, z 10 kΩ do GND / P04: cel H ≥2,4 V i L ≤0,4 V, mierzyć przebieg | __________ |
| Heartbeat STOP | J9 w stałym L; brak impulsów po ustaleniu przełącznika | __________ |
| Temperatura U2 przy 15 V | 10 min, wszystkie kanały H i obciążenia 10 kΩ; zapisać TA, temperaturę obudowy i prąd | __________ |
| Próba większego obciążenia | Powtórzyć temperaturę przy dozwolonych zwarciach J1-J8 do GND; 3V3 w granicach, obudowa U2 <85°C | __________ |
| P04, watchdog L / H / odłączenie | 50-150 ms od ostatniego zbocza, zgodnie z zatwierdzoną rewizją P04 | __________ |
| P04, ponowne uzbrojenie | Po usunięciu przyczyny rozbrojenia wymagany nowy ARM | __________ |

Przy utracie regulacji lub wzroście temperatury powyżej kryterium przerwać próbę. Nie zaliczać przez zmianę wartości w formularzu: skorygować montaż/układ albo zastosować radiator i powtórzyć pomiar. Jeśli egzemplarz pracuje wyłącznie do 12 V, odnotować ograniczenie przy J10 i w tej karcie.

## Stan końcowy

Przymiarka: __________  Zasilanie: __________  Kanały: __________  Heartbeat: __________

Temperatura / warunki: __________  Wiązka P04 i rewizja odbiornika: __________

Decyzja o dopuszczeniu egzemplarza do prób stanowiskowych: ____________________
