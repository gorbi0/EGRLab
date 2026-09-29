# Obciążenia i granice P11-R1

`src/check_budget.py` odczytuje wartości i węzły z kopii P03-R2/P04-R2.1.
R40=100 Ω zasila PANEL_3V3. W najgorszym stanie wszystkie kontakty dają
jednocześnie trzy obciążenia10 kΩ z CORE,dwa tory1 kΩ+10 kΩ z SAFE oraz
10 kΩ+100 kΩ obwodu STOP/SAFE_N. W modelu opory obciążenia obniżono o1%,
R40/R4 podniesiono o1%. Minimalne3,18 V jest założeniem do odbioru szyny,
nie nową gwarancją P02.

| Założenie przy3,18 V | PANEL_3V3 | SAFE_N |
|---|---:|---:|
| Same rezystory z tolerancjami | 3,028 V | 2,748 V |
| Dodatkowy sink1 µA na SAFE_N | 3,028 V | 2,739 V |
| Dodatkowy sink5 µA na SAFE_N | 3,028 V | 2,702 V |

Pobór≈1,50 mA. STOP zamknięty bez aktywnego ściągania SAFE_N przewodzi
około27,8 µA; podczas ściągania około0,3 mA. KEY zasila własne dwa wejścia
i tor MECH:około0,85 mA przy pełnej pętli. Każdy NC sprzętowy około0,28 mA,
NC diagnostyczny i TEST_NO około0,3 mA. ARM i MARK wykorzystują podciąganie
na sąsiednich PCB; nie obciążają PANEL_3V3. Katalogowe low-level należy sprawdzać
przy tych wartościach, a nie przy maksymalnym obciążeniu reklamowanym dla styków.

Model nie obejmuje pełnej sumy upływności wszystkich układów w temperaturze,
rezystancji zabrudzonych styków, ani nieznanego jeszcze P07. Nie wolno uznać
wiersza5 µA za udowodniony limit systemu. Cel odbiorczy pozostaje SAFE_N≥2,7 V
przy zwolnionych pull-downach. Jeżeli nie zostanie spełniony, wstrzymać aktywny
TEST i osobno zrewidować P04 (np.dobór R4), z ponownym sprawdzeniem prądów
ściągania oraz reakcji STOP. P11 nie omija R40 ani nie dodaje własnego pull-up.
Zapas do progu odbiorczego to nie to samo co próg przełączania SN74HC14.

Tory mocy P11 mają3 mm szerokości,Cu70 µm,bez przelotek:
LOGGER13,8 mm na żyłę,TEST10,8 mm. Dla miedziρ≈0,0175 Ω·mm²/m
R≈1,15 mΩ i0,90 mΩ na ścieżkę przy20°C. Przy10 A daje to0,115/0,090 W
na ścieżkę; nie obejmuje PTH,lutów,kontaktów i przewodów ani wzrostuρ po nagrzaniu.
10 A jest prądem kwalifikacji toru pasywnego, nie nowym ustawieniem mostka
ani dopuszczalnym prądem EGR. Podstawowy limit diagnostyczny pozostaje w projekcie
P06/P07; P07 nadal HOLD. Header Phoenix nominalnie12 A,styki DT nominalnie13 A,
ale najniższy dopuszczalny limit całej wiązki ustala pomiar cieplny.

Odbiór:obciążenie zastępcze,2/5/10 A,30 min w najwyższym dopuszczonym kroku,
pomiar temperatur PCB,lutów i obu kontaktów. CelΔT≤25 K,temperatura≤70°C;
zapisać temperaturę otoczenia. Jeśli złącze lub kabel przekracza warunki producenta,
zmniejszyć limit. Próba obejmuje kompletne zakończenia,pomiar samej miedzi
nie kwalifikuje zacisków. Przy integracji z P06 mierzyć również spadek całej
pętli LOGGER i porównać z trybem BYPASS.

TAPy pozostają bez dodatkowych RC i zabezpieczeń na P11. Ścieżki plus
nieużywane odgałęzienia dodają pojemność; kontrola przesłuchu PWM i porównanie
próbki z sondą odniesienia jest w odbiorze P05/P11. Brak filtrowania nie jest
obietnicą idealnej odpowiedzi częstotliwościowej.
