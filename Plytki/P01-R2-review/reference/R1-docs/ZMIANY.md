# Rejestr zmian P01-R1-review

| ID | Zmiana | Skutek i sprawdzenie |
|---|---|---|
| P01-001 | Trzy funkcjonalne arkusze KiCad: tor mocy, AUX/OVP/UVLO, SAFE | Eksport XML porównany pin po pinie z 6.1-rc1. |
| P01-002 | J_PGB → J5, J_SUPPLYA → J6, J_BATB → J7, J_PRES → J8, W_PRES → R34 | Wyłącznie oznaczenia. Pole BaselineRef zachowuje powiązanie. Numeracja pinów zewnętrznych bez zmian. |
| P01-003 | Lokalny symbol TL431BILP: 1=K, 2=A, 3=REF | Standardowy symbol biblioteki miał inne przypisanie 1/3. W tym układzie 1 i 3 są zwarte, ale funkcje pinów muszą być poprawne. Kontrola automatyczna funkcji. |
| P01-004 | Dokładne serie rezystorów: większe MFR-50/H4; R1/R23/R27 PR02 2 W | Wartości R i progi bez zmian. R27 zwiększony z 0,5 do 2 W; nie jest to dowód odporności impulsowej całej gałęzi. |
| P01-005 | C7 22 µF/50 V i C9 47 µF/50 V | Wyższe napięcie znamionowe, te same pojemności. R2=1 Ω nadal w szeregu z C9. |
| P01-006 | C8/C10/C11/C12/C13 w wykonaniu Vishay H5, 5 mm | W trakcie doboru odrzucono L2 (2,5 mm); nie był to wariant opublikowany. Konkretny MPN i footprint są zgodne. |
| P01-007 | TP1–TP10: dodatkowe PTH do pomiarów | Brak nowej funkcji obwodu; same pola, nie zamawiać 10 złączy. |
| P01-008 | H_PG i H_BAT lutowane; kotwy 12,5 mm od rzędu lutów | PG 200 mm/AWG22; BAT 200 mm/2,5 mm². Zgodnie z 6.1. Otwory opasek 3,2/4,2 mm. |
| P01-009 | Q2/Q4: do zakupu onsemi 2N5401YBU zamiast starszego 2N5401G | E-B-C, PNP 150 V, 600 mA; brak zmiany sieci. Nowy producentowy bondout potwierdzony w karcie. Czas odcięcia pozostaje próbą sprzętową; nie zakładać identycznej dynamiki serii. Nie zamawiać wariantu -C. |
| P01-010 | J6 Phoenix 1757255; gniazdo kątowe MSTBA 3p 5,08 | Zgodne z rodziną MSTB 5,08. Wiązka SUPPLY należy do P02. |
| P01-011 | Q1/D2: otwory TO-220 powiększone do 1,4 mm, pady 2,1×3 mm | Zwykły footprint miał 1,1 mm, mniej niż przekątna maksymalnej nóżki Q1 ok.1,18 mm. Rozstaw2,54 bez zmian, odstęp miedzi między padami0,44 mm. |
| P07-HOLD | Zatrzymanie P07 do odbioru modułu BTS7960 | Bez zmian P07 w bazie. Nie zamawiać jego PCB ani Pololu według starej listy. |

Nie zmieniono wartości dzielników, punktów pracy, połączeń SAFE_N, budżetu 5 A,
ani strategii zewnętrznego bezpiecznika. Dokładny dobór zamienników przy zakupie
jest kontrolowaną zmianą; nie wolno go ukrywać pod tym samym numerem pakietu.
