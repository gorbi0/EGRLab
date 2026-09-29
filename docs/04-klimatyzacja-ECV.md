# 04 — Naprawa klimatyzacji / ECV (zamknięta, lipiec 2026)

Istotna dla H1 i H7 — wiązka ECV biegnie tą samą trasą przy pokrywie rozrządu co wiązka EGR.

## Objaw
Przerywany brak pracy kompresora, **bez kodów w żadnym module**, wyzwalany ruchem auta (nie położeniem).

## Przyczyna
**Przerwana żyła w wiązce ECV** między FATC a złączem kompresora. Przy przerwie FATC wykrywał usterkę przez pin sprzężenia zwrotnego ECV (B11) i przestawał żądać pracy kompresora → ECU silnika nie załączało przekaźnika sprzęgła → brak kodów.

## Naprawa
Przewód obejściowy LGY 6 mm² od złącza FATC przez kabinę do wtyczki kompresora, zaciskane tulejki, poprowadzony wzdłuż oryginalnej wiązki, spięty opaskami. AC działa w pełni. Przy okazji: znalezione połamane mocowania wiązki i luźna masa silnika (dokręcona) — pozostałość po wymianie rozrządu.

## Dane techniczne
- Kompresor: nr 977012Y100 = **Denso 6SE14**, zmienna wydajność, zewnętrzne ECV (nie Halla VS16E).
- Złącze kompresora 3-pin: pin 3 (żółty) — cewka sprzęgła, 3,8 Ω, masa przez obudowę (jednoprzewodowo); piny 1–2 — solenoid ECV, 11 Ω, izolowany, dwuprzewodowo (spec. Denso 10,1–11,1 Ω).
- FATC, złącze B (22-pin, węższe): ECV Out — pin 22; ECV feedback — pin 11; CAN — piny 1–2 (~60 Ω z terminatorami); pozostałe: masy czujników, referencje potencjometrów, sygnały aktuatorów.
- Czujnik ciśnienia APT: V = 0,00878835 × P_psia + 0,37081095. Ciśnienie prawidłowe: 16,05 bar przy 34,5°C otoczenia.
- ECV sterowany PWM w sposób ciągły (nie on/off) — potencjalne źródło sprzężenia w linię wipera EGR przy uszkodzonej izolacji (H7).

## Wykluczone
Niedobór/nadmiar czynnika (dotankowany 2 h przed testem; ubytek przez 7 lat = przenikanie, nie wyciek), zawór rozprężny / osuszacz, odcinanie przez ECU wg prędkości lub luzu, uszkodzony driver przekaźnika, niskie napięcie, czujnik parownika (38°C vs wartość awaryjna −2°C), P0820 jako blokada.
