# PCB-R3 - lokalna poprawa R2 i zamknięcie luk procesu

Schemat R3, pin-net, geometria padów, położenie bloków analogowych, interfejsy,
kotwy i mechanika główna są zachowane. Zmieniono pozycje tylko D4, C6, TP1 i TP2.
Nie wykonywano ponownego globalnego rozmieszczania ani autoroutingu.

| Zmiana | R2 | PCB-R3 |
|---|---|---|
| D4 | poniżej szyny VS, daleko od Q1 | we wnęce HS2; K-S 5,25 mm, A-G 6,78 mm |
| C6 | pad1 (105,5;30) | pad1 (105,5;32,1), 9,8 mm od G/S Q1 |
| TP1/TP2 | próba dostępu od góry w ciasnej wnęce | podstawowy dostęp od spodu, opisy B.SilkS, ścieżki po 4,62 mm |
| Szyna VS B.Cu | Y=34 pod późniejszym nowym położeniem C6 | lokalny uskok do Y=36; brak kolizji z padem GATE C6 |
| C5 GATE | odcinek B.Cu do dawnego pada D4 i odcinki F.Cu | bezpośrednia gałąź F.Cu do grzbietu GATE przy Y=44 |
| Oznaczenia rezystorów | pod korpusami | dodatkowe czytelne od spodu |
| Modele 3D | brak ważnych brył | 77 lokalnych modeli gabarytowych; jawna lista pozostałych pól/zworek |
| BOM | R3 + uwagi zakupowe w osobnym opisie | jednoznaczna nakładka montażowa A1 z rejestrem zamówień |
| DRC | skrypt mógł odczytać stary JSON | świeże uruchomienie przy każdym odbiorze, związanie wejść i wyniku |
| Próba przerwy | zmiana szerokości ścieżki | rzeczywiste usunięcie odcinka do TP2, potwierdzone także przez native DRC |

Kluczowe własności R2 zachowane: brak miedzi F.Cu pod metalem HS1/HS2, oznaczenia
orientacji TO-220, lokalne C10/U2 i C11/U4, funkcjonalne grupowanie, J5 skierowane
ku dolnej krawędzi, Kelvin LK1 bez prądu roboczego w małych padach, termiki J7.

Wyjątek BAT_FUSED 3 mm na odcinku około 29 mm jest przyjęty projektowo, z odbiorem
nagrzewania. Nominalnie 2,4 mOhm / 12 mV / 0,06 W przy 5 A i 70 um. Nie jest to
potwierdzenie obciążalności całego toru ani zabezpieczenia zwarciowego.

Prześwit D4-C6 jest nominalnie 1,075 mm, Q1-C6 4,85 mm. Umieszczenie D4 jest
kompromisem: krótsza pętla ograniczenia VGS kosztem montażu D4 przed radiatorem.
Sondowanie od spodu usuwa wymóg wsuwania sond w tę wnękę. Rzeczywiste tolerancje,
lutowanie i dostęp do śruby wymagają przymiarki, bez zmiany kryteriów testów.

Generatory zachowują sieci nowych ścieżek po ponownym odczycie. Przy usuwaniu
odcinków użyto bezpiecznej dla tego przebiegu operacji RemoveNative i zachowania
referencji do obiektów; nie pozostawiono obejścia polegającego na ignorowaniu
zwarć lub niezgodności po zapisie. Reguły projektu nie są nadpisywane podczas
SaveBoard (tryb pominięcia zapisu ustawień projektu).
