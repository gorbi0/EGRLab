# P00-R2 - odniesienie do recenzji R1

*Historia R1 → R2 (Astra), bez zmian merytorycznych. R3: uwagi z recenzji R2 zamyka `ZMIANY-R3.md`. Punkt R05 („potwierdzić po wydaniu PCB P04”) jest zamknięty w R3: wiązka opisana dla P04-R2.1 i sprawdzana `src/check_harness.py`.*

| Uwaga | Zmiana w R2 | Dowód / pozostający odbiór |
|---|---|---|
| R01: błędne 5 V i karta U2 | 6-15 V na wejściu, karta SNVS015F, zmieniony schemat/nadruk/BOM | Obliczenie napięcia za D1; fizyczny pomiar przy 6 V |
| R02: brak minimum obciążenia | R5 560 Ω bezpośrednio 3V3-GND | 5,54 mA minimum z tolerancją i TCR; kontrola netlisty i PCB |
| R03: niepotwierdzony C6, niepełne ESR | EEUFR1H220; R6 1 Ω w gałęzi C6; dolna i górna granica ESR w wymaganiach | Źródło Panasonic, obliczenie w warunkach odniesienia; stabilność do pomiaru |
| R04: zależność generatora od P02 | Lokalne wejściowe footprinty i ich hashe; opis toolchainu | Pełny czysty rebuild i porównanie geometrii w osobnym raporcie |
| R05: wiązka i próby P04 | Mapa wejść, odgałęzienia SUP/MCU/H_HB, ARM/STOP, próby H/L/odłączenia | Dokument wiązki odnosi się do netlisty v6.1; potwierdzić po wydaniu PCB P04 |
| Nakładające się teksty | Przeniesione opisy LED, zwiększony odstęp C4/C5 i C6/C7, krótszy tytuł | Inspekcja wyrenderowanego finalnego PDF |
| Błędne linki LED9/10 | Osobne dokumenty producenta dla żółtej i czerwonej LED | BOM i źródła |
| Zbyt szeroka deklaracja ochrony 1 kΩ | Nominalny prąd zwarcia do GND oraz granica 3,51 mA z tolerancjami | Wyjaśniony zakres użycia: wejścia logiczne 3,3 V |

R6 jest uzupełnieniem doboru C6 po recenzji: gwarantuje rezystancyjny składnik szeregowy bez polegania na niepodanej dolnej granicy ESR elektrolitu. Pozostałe kanały nie zostały przeprojektowane.

Nie oznaczono pomiarów sprzętu jako wykonanych. Statusy elektryczne są oceną dokumentacji i obliczeń, a pola odbioru fizycznego pozostają puste. Zmiany R2 nie dotyczą P01, P02, P03 ani wariantu P07.
