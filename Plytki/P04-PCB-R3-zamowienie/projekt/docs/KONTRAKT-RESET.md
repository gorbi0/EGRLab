*R3 (5.10.2026): partner P03 R6 (U6 SN74LVC1G17 + R41 220 Ω → J_BP3.12 SUP_N_OUT), P04 R3 J_BP3.12 SUP_N_OUT → R17 10 kΩ, U9.5. Zamiast taśmy H_SAFE 150 mm droga: taśma ok. 30 mm + miedź P12 + taśma ok. 30 mm; wymaganie ≤ 10 ns/V na U9.5 bez zmian, do pomiaru przy odbiorze P04/P12. Kontrola `verify_reset.py` czyta zamrożoną mapę P03 R6 (`reference/reset-peer-parts.json`).*

# Kontrakt resetu P03-R5 / P04-R2.2

| Odcinek | Źródło / odbiornik | Domena | Stan bez źródła | Budżet / wymaganie |
|---|---|---|---|---|
| SUP_RAW_N | TPS3808 OD -> U4 LVC1G37 Schmitt | 3V3_CORE | reset według supervisora | R13 10 kΩ; wejście U4 dopuszcza 100 ms/V |
| SUP_N | U4 OD -> R34 220 Ω -> M1 EN/MCP RESET/U6 | 3V3_CORE | rozładowanie EN, start do odbioru | R35 10 kΩ || EN 10 kΩ; VOL do obliczeń 0,4 V; C_EN 1 µF |
| SUP_N_OUT/SUP_N | U6 LVC1G17 -> R41 220 Ω -> P04 U9.5 LVC125 | CORE -> IO, wspólna GND | R17 10 kΩ ściąga LOW | U6 Ioff 10 µA + U9 II 20 µA: 0,303 V z R17 +1%; VIL ≤0,8 V |
| To samo, źródło ON | U6 push-pull -> P04 U9.5 | domeny osobne | utrata CORE zdejmuje reset OK | VOH min 2,4 V, po R41 i upływie nadal >2,0 V; obciążenie około 0,33 mA |
| Zbocza na U9.5 | taśma H_SAFE 150 mm | 3,3 V | nie dotyczy | ≤10 ns/V przez 0,8–2,0 V; oba zbocza, pomiar z uwzględnieniem sondy |

Prądy upływu sumowane konserwatywnie co do modułu, nie jako prognoza kierunku. Dla zakresu do 85°C budżet wynosi 15 µA, czyli 0,152 V. Sprzęt NIE ZBADANO. Dodatkowe warunki ARM/PERMIT P04 pozostają aktywne; powrót resetu nie uruchamia ruchu.

Źródła: [TI LVC1G37](https://www.ti.com/lit/gpn/SN74LVC1G37), [TI LVC1G17](https://www.ti.com/lit/ds/symlink/sn74lvc1g17.pdf), [Nexperia LVC125A](https://assets.nexperia.com/documents/data-sheet/74LVC125A.pdf), [TI TPS3808](https://www.ti.com/lit/gpn/TPS3808).

Kontrola verify_reset.py czyta własną wyeksportowaną netlistę i zamrożoną mapę części drugiej płytki; nie importuje generatora części. Po wspólnym wydaniu sprawdza się zgodność kopii z rzeczywistymi częściami sąsiada. Nie kwalifikuje zboczy ani startu analogowego.

Przy następnej zmianie łącza zapisać w takiej tabeli źródło, odbiornik, domeny, stan bez zasilania, granice upływu, progi i limit zbocza. Przeliczać zmieniony wiersz, następnie testować na sprzęcie.
