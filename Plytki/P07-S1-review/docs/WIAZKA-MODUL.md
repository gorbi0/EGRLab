# P07 S1 — wiązki do modułu IBT-2 i portu TEST

*5.10.2026. Moduł IBT-2 / HW-39 (2 × BTS7960B, 74HC244) stoi poza stosem, na ściance obudowy (4 × M3 w kwadracie 40 × 40 mm, radiator 22,8 mm pod płytką do przepływu powietrza). Długości są szacunkowe — potwierdzić przymiarką w obudowie. Tabela maszynowa: `interfejsy.csv`.*

## Sterowanie — J5 (J_MOD), taśma 8 żył

| J5 / moduł | Sieć | Kierunek | Na P07 | Na module (pomiar 5.10) |
|---|---|---|---|---|
| 1 | RPWM | P07 → moduł | U16A + R39 100 Ω | 74HC244 1A1 (pin 2), 30 k do GND |
| 2 | LPWM | P07 → moduł | U16B + R40 100 Ω | 74HC244, 30 k do GND |
| 3 | R_EN | P07 → moduł | U16C + R41 100 Ω (= DRIVE_EN) | 30 k do GND, rozdzielone z L_EN |
| 4 | L_EN | P07 → moduł | U16D + R42 100 Ω (= DRIVE_EN) | 30 k do GND |
| 5 | R_IS | moduł → P07 | R44/R45 100 k/100 k, C14, D5, U17 | 10 k do GND |
| 6 | L_IS | moduł → P07 | R46/R47, C15, D6, U17 | 10 k do GND |
| 7 | 5V_MOD | P07 → moduł | 5V_SYS przez PTC F1 | VCC 74HC244 |
| 8 | MOD_GND | — | R43 10 Ω do GND | GND logiki; z B− 508 mV w trybie diody (C5 — do sprawdzenia omomierzem) |

- Złącze na P07: kątowe obudowane IDC 2 × 4 (J5), przy krawędzi płytki, żeby taśma wychodziła w bok (pionowe z wtykiem przekroczyłoby 16,5 mm).
- Taśma: 8 żył 1,27 mm, ok. **300 mm**, gniazdo IDC 2 × 4 na obu końcach (1:1). Na module wtyk pasuje na kątowy 2 × 4 goldpin.
- **Do potwierdzenia przed zaciśnięciem taśmy (POMIARY B4):** numeracja pinów listwy modułu. Założenie: pary w kolumnach RPWM/LPWM, R_EN/L_EN, R_IS/L_IS, VCC/GND, czyli numeracja IDC 1–8 jak w tabeli. Jeśli listwa modułu ma inny układ, zmienia się tylko kolejność pinów J5 w `src/parts.py` (kontrola `JMOD-PINOUT`).
- **Do potwierdzenia (POMIARY E2):** RPWM = 1 → M+ wyżej (kierunek A). Od tego zależy znak prądu ITEST i to, który próg OC (dodatni czy ujemny) zadziała w kierunku A. Progi są symetryczne, więc zamiana nie osłabia ochrony.

## Moc — przewody 2,0 mm² (decyzja 4.10)

| P07 | Sieć | Drugi koniec | Długość (szac.) | Przewód |
|---|---|---|---|---|
| J1.1 / J1.2 | VMOTOR / PGND | P02 R4 J2.1 / J2.2 (wtyk GMSTB 2,5/3-ST-7,62) | 250 mm | 2 × 2,0 mm², czerwony / czarny |
| J2.1 / J2.2 | MOD_BP / PGND | moduł B+ / B− (zaciski śrubowe, tulejki) | 300 mm | 2 × 2,0 mm², czerwony / czarny |
| J3.1 / J3.2 | MOD_MP / T_EGR_P3 | moduł M+ / M− | 300 mm | 2 × 2,0 mm², żółty / niebieski |
| J4.1 / J4.2 | T_EGR_P1 / T_EGR_P3 | P11 port TEST (piny zaworu 1 / 3) | 200 mm | 2 × 2,0 mm² |

- Wszystkie końce na P07 są lutowane w PTH (otwór 2,4 mm, pole 4,5 mm, raster 7,62 mm) z dwoma otworami kotwy 3,2 mm 12 mm za rzędem (opaska), jak J3/J4 w P06 R2.
- J4 (TEST) przy krawędzi x = 0 (zadanie). Położenie J1–J3 zostaje do layoutu. Rekomendacja: przy tej samej krawędzi co bocznik, żeby pętla 10 A (J3 → RSH1 → J4) była krótka. Tor 10 A: pola ≥ 4 mm na obu warstwach, zszyte przelotkami (35 µm, S1 3).
- Spadek na 2,0 mm² (8,9 mΩ/m): przy 6 A i łącznie ok. 1,1 m toru ok. 60 mV; przy 10 A ok. 0,1 V.
- Przewód PGND z P02 jest jedynym powrotem prądu silnika (masy GND i PGND rozdzielone na P07 — `PROJEKT.md`, „Masy”). Nie łączyć B− modułu z obudową ani z GND przyrządu w innym miejscu.
