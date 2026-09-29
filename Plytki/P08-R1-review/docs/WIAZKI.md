# Wiązki P08-R1

J1–J3 są polami PTH. Kotwy z dwoma otworami NPTH 3,2 mm leżą 12 mm przed pierwszym rzędem lutu; drugi rząd taśmy jest oddalony o 14,54 mm. Opaska 2,5 mm chwyta izolację. Zostawić łagodny łuk, bez naprężania lutów i bez ciasnego zginania przy końcu pocynowanej żyły. Wiązki wychodzą nad górną krawędzią PCB. Pod opaską i podkładkami M3 nie prowadzi się miedzi.

| Wiązka | Lutowany koniec | Wpinany koniec | Długość | Przewód |
|---|---|---|---:|---|
| W1 LV08 | P08 J1 | P02-R3 J8 Mini-Fit Jr 4p Au | 200 mm | 4 × AWG22 |
| W2 SENSOR | P08 J2 | P04-R2.1 J4 IDC6 Au, KEY2 | 150 mm | taśma 6 × AWG28 / 1,27 mm |
| W3 SFAULT | P08 J3 | P03-R2 J6 IDC6 Au, KEY3 | 150 mm | taśma 6 × AWG28 / 1,27 mm |
| W4 TSENSOR | przyszła P11 | P08 J4 Mini-Fit Jr 2p Au | 150 mm | 2 × AWG22 |

W4 należy do karty/BOM P11; na P08 montowany jest tylko nagłówek J4. Przed projektowaniem P11 przenieść ten kontrakt bez zmiany numeracji.

Widok P08 od strony elementów, górna krawędź kartki = górna krawędź PCB:

```text
     kotwa/opaska                    kotwa/opaska
 J1:  1  2  3  4            J2/J3:    1  3  5
                                     2  4  6
```

**Numeracja dotyczy padów, nie kolejności kolorów taśmy.** Wtyk IDC oglądany od strony współpracującej może wyglądać jak odbicie widoku od strony przewodów. Wykonać kontrolę ciągłości wszystkich aktywnych żył według tabeli, zamiast polegać tylko na czerwonym pasku. Pady nieużywane i ich żyły pozostawić niepodłączone i zaizolowane. Klucz mechaniczny jest na wtyku i nagłówku drugiej płytki, nie na polu lutowniczym P08.

| Złącze P08 | Pin | Sieć | Odbiorca / źródło |
|---|---:|---|---|
| J1 LV08 | 1 | 5V_SYS | P02/J8.1 |
| J1 LV08 | 2 | GND | P02/J8.2 |
| J1 LV08 | 3 | 3V3_IO | P02/J8.3 |
| J1 LV08 | 4 | GND | P02/J8.4 |
| J2 SENSOR | 1 | SENSOR_PERMIT | P04/J4.1 → P08 |
| J2 SENSOR | 2 | NC / KEY2 | zaślepiona pozycja wtyku |
| J2 SENSOR | 3 | SENSOR_OK | P08 → P04/J4.3 |
| J2 SENSOR | 4 | GND | P04/J4.4 |
| J2 SENSOR | 5,6 | NC | nie podłączać |
| J3 SFAULT | 1 | SENSOR_HEALTHY | P08 → P03/J6.1 |
| J3 SFAULT | 2 | GND | P03/J6.2 |
| J3 SFAULT | 3 | NC / KEY3 | zaślepiona pozycja wtyku |
| J3 SFAULT | 4,5,6 | NC | nie podłączać |
| J4 TSENSOR | 1 | 5V_SENSOR | P08 → P11 |
| J4 TSENSOR | 2 | AGND_SENSOR | powrót z P11, rozłączany przez K1 |

J2 i J3 mają tę samą liczbę pozycji, ale różne klucze i opisy. Sprawdzić, że nie da się ich zamienić. Nie zwierać AGND_SENSOR do GND przewodem, ekranem ani masą oscyloskopu: w odbiorze rozłączania używać pomiaru różnicowego lub izolowanego miernika między J4.1–J4.2. Podłączając kilka oscyloskopowych mas do różnych punktów pamiętać, że zwykle są zwarte wewnętrznie.
