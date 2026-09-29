# P00-R3 — uruchomienie i odbiór

*Nazwa pliku pochodzi z R2; treść dotyczy R3. Zmiany R3: pomiar heartbeat na J9 przed P04, ze środkiem zaradczym; plan B 12 V; TP3 „ZA D1”; odwołania do prób P04-R2.1.*

Egzemplarz / data / wykonawca: ____________________

Status wszystkich poniższych prób: **NIE ZBADANO**. Wyniki ERC/DRC i obliczenia nie wypełniają tego formularza. Potrzebne: miernik, oscyloskop, zasilacz z ograniczeniem prądu, rezystory testowe 10 kΩ i 5,1 kΩ (albo dwa 10 kΩ równolegle), pomiar temperatury.

## Uruchamianie etapami

1. **Przed lutowaniem wydruk 1:1.** Zmierzyć belkę 100 mm i obrys 115 × 70 mm. Przymierzyć U2, C4/C6, przełączniki, podstawkę i J10. Napis „+VIN 6-15V” stoi pod J10. Pole TP3 („ZA D1”) służy tylko do pomiaru za diodą. Sprawdzić omomierzem kierunek przełącznika Würth. Obejrzeć stronę taba TO-220 (za tabem są C5/C7) oraz polaryzację LED i kondensatorów.
2. **Zasilanie.** Wlutować J10, D1, U2, C4–C7, R5, R6 oraz LED10 z RL10. U1 zostaje wyjęty, przełączniki w L, SW9 w STOP. R5 jest potrzebny już na tym etapie. Rezystancję R5 i R6 zmierzyć przed montażem, bo w obwodzie zakłócają pomiar inne gałęzie.
3. **Pierwsze włączenie.** Zasilacz 9 V, ograniczenie początkowo 30 mA. Jeśli po naładowaniu kondensatorów zasilacz dalej ogranicza prąd, zatrzymać próbę i sprawdzić montaż. Zmierzyć 3V3 i jego przebieg, potem to samo przy 6 V i 15 V.
4. **Reszta elementów.** Wlutować pozostałe elementy i podstawkę, sprawdzić przerwy i zwarcia. Przy wyłączonym zasilaniu włożyć TLC555CP. Do pełnych prób ograniczenie 100 mA. Sprawdzić wszystkie kanały bez obciążenia i z rezystorami testowymi.
5. **Heartbeat.** Zmierzyć HB, w tym H na J9 z 10 kΩ, oraz stany RUN/STOP. Do P04 przechodzić dopiero po odbiorze samego P00 i sprawdzeniu wiązki (`P00-P04-WIAZKA.md`).

## Wyniki do wpisania

Kryteria tętnień, amplitudy z zapasem i temperatury są przyjętymi kryteriami odbioru tego prototypu, nie gwarancjami producenta.

| Próba | Kryterium / sposób pomiaru | Wynik |
|---|---|---|
| Wymiary i części 1:1 | Belka 100 mm; wszystkie części się mieszczą, nóżki bez naprężeń | __________ |
| Polaryzacja i R5/R6 | R5 560 Ω ±1 %, R6 ok. 1 Ω (uwzględnić przewody miernika) | __________ |
| Zasilanie 6 V | TP3 (ZA D1) co najmniej 4,75 V, zasilacz nie ogranicza prądu | __________ |
| 3V3 bez U1 | 3,14–3,46 V przy 6 / 9 / 15 V na J10 | __________ |
| 3V3 z U1, L/STOP | 3,14–3,46 V, brak trwałych oscylacji | __________ |
| 3V3, wszystkie H/RUN | Jak wyżej, także z odbiornikami testowymi | __________ |
| Tętnienia | Cel ≤ 50 mVpp, pasmo 20 MHz, krótka masa sondy; zapisać warunki | __________ |
| Skok obciążenia | Przełączanie kanałów z 10 kΩ do GND; bez podtrzymanego dzwonienia i oscylacji | __________ |
| J1–J8 bez obciążenia | H blisko zmierzonej szyny 3V3, L blisko GND | __________ |
| J1–J8 z 10 kΩ | H nominalnie 3,0 V (min. obliczone 2,85 V); zapisać min/max dla 8 kanałów | __________ |
| Kanał z 5 kΩ | H nominalnie 2,75 V; cel ≥ 2,5 V | __________ |
| Zwarcie wyjścia do GND | Jeden kanał przez własny 1 kΩ: ok. 3,3 mA; LED nadal pokazuje H źródła | __________ |
| Heartbeat RUN | Orientacyjnie 80–125 Hz, nominalnie 102 Hz; zapisać f i wypełnienie | __________ |
| **Heartbeat na J9 z 10 kΩ do GND** (przed P04) | **H ≥ 2,4 V**, L ≤ 0,4 V, mierzyć przebieg. Przy H < 2,4 V: RL9 → 4,7 kΩ albo inny TLC555 i powtórzyć. P04 ma próg 2,0 V; szczegóły w `ZALOZENIA-P00-R2.md` | __________ |
| Heartbeat STOP | J9 w stałym L; brak impulsów po ustaleniu przełącznika | __________ |
| Temperatura U2 przy 15 V | 10 min, wszystkie kanały H z 10 kΩ; zapisać TA, temperaturę obudowy i prąd | __________ |
| Próba większego obciążenia | Temperatura przy zwartych J1–J8 do GND; 3V3 w granicach, obudowa U2 < 85 °C. Przy przekroczeniu powtórzyć przy 12 V; jeśli przechodzi, egzemplarz pracuje do 12 V | __________ |
| Wiązka do P04-R2.1 | Ciągłość, mapa i wybierak HB wg `P00-P04-WIAZKA.md`; brak połączenia szyn 3V3 | __________ |

Przy utracie regulacji lub przekroczeniu kryterium temperatury przerwać próbę. Nie zaliczać przez zmianę wartości w formularzu. Poprawić montaż albo zastosować plan B (12 V) i powtórzyć pomiar. Próby samego P04 (E01–E22, m.in. watchdog E11, ponowne uzbrojenie E14, E17 bez zasilania P04) zapisuje się w formularzu P04, nie tutaj.

## Stan końcowy

Przymiarka: __________  Zasilanie: __________  Kanały: __________  Heartbeat (H na J9): __________

Temperatura / warunki: __________  Zakres zasilania egzemplarza (15 V / 12 V): __________

Wiązka P04 i rewizja odbiornika (P04-R2.1): __________

Decyzja o dopuszczeniu egzemplarza do prób stanowiskowych: ____________________
