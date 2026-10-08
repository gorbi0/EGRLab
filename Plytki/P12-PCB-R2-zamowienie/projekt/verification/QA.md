# P12-R2 — QA schematu (plik generowany przez src/run_schematic.py)

ERC: 0 naruszeń na 1 arkuszu. Netlista: 20 części, 280 pinów sprawdzonych pin po pinie względem `parts.py`, 0 błędów, 57 sieci.

Kontrakt (`src/kontrakt.py`): 16 złączy, 276 pinów, źródła zgodne z blobami w `kontrakty.json`: 10/10; sieci: 57 (z GND), wszystkie z co najmniej dwoma końcami; piny bez połączenia: 0; łączone mimo stanu „czeka”: brak (0 sieci czeka).

Netlista wobec kontraktów: 10/10 PASS. Próby ujemne: 22/22 (w tym zerowa: czysta).

| Kontrola | Opis | Wynik |
|---|---|---|
| K1 | Złącza J1..J16: footprint prostego IDC o typie z kontraktu (2x5 / 2x8 / 2x10, kontrakty.json) i wszystkie piny w netliście | PASS |
| K2 | Każdy pin każdego złącza: sieć = kontrakt-P12.json (pinout płytki, GND jawnie; R2: docs/NIEPODLACZONE.csv pusta) | PASS |
| K3 | Grupy połączeń P12 = grupy z kontraktu (każda sieć dokładnie z pinami tej nazwy, bez sieci dodatkowych) | PASS |
| K4 | Kontrola krzyżowa: końce każdej sieci poza GND = P12-przygotowanie/wyniki/kontrakty.json (56 OK, 0 innych) | PASS |
| K5 | GND, 5V_SYS i 3V3_IO to osobne sieci; P03 J_BP2 16/17/19/20 (PFAIL_N / 5V_SYS) nie łączą się z P05 J_BP2 16/17/19/20 (GND) | PASS |
| K6 | Żadna sieć nie łączy pinów, którym kontrakt daje różne sieci (brak połączeń pin w pin) | PASS |
| K7 | 5V_SYS: 3 piny źródła P02 + 16 pinów odbiorników (w tym P08 2, P07 2, P04 1) + TP2; 3V3_IO: 2 piny źródła + 9 odbiorników (w tym P04 2, P07 1, P08 1) + TP3; P04_3V3 osobno (P02 J_BP.15 - P04 J_BP2.14) | PASS |
| K8 | Brak pinów bez połączenia (R2: wszystkie płytki obecne, NIEPODLACZONE.csv pusta); PG_SEND (J1.17-J15.20) i PG_LINK (J1.18-J15.18) osobno, bez mostka na P12 (zwora R34 na P02) | PASS |
| K9 | Pola pomiarowe: TP1 / TP4 GND, TP2 5V_SYS, TP3 3V3_IO | PASS |
| K10 | Na schemacie tylko J1..J16 i TP1..TP4 (bez elementów aktywnych i biernych) | PASS |

## Próby ujemne

| Mutacja | Oczekiwana kontrola | Wynik | Zgłosiły kontrole |
|---|---|---|---|
| proba_zerowa | żadna | OK | — |
| zamieniony_pin_ADC_SCLK_DOUTA | K2 | OK | K2, K3, K4, K6 |
| zamieniony_pin_P09_MISO_MOSI | K2 | OK | K2, K3, K4, K6 |
| brak_sieci_ADC_BUSY | K2 | OK | K2, K3, K4, K8 |
| brak_konca_CAN_RX_P10 | K2 | OK | K2, K3, K4, K8 |
| zwarcie_5V_SYS_GND | K5 | OK | K2, K3, K4, K5, K6, K7, K9 |
| pin_w_pin_J3_17_J6_17 | K5 | OK | K2, K3, K4, K5, K6, K7 |
| pin_w_pin_J3_16_J6_16 | K6 | OK | K2, K3, K4, K5, K6 |
| zly_typ_P05_J_BP1_2x8 | K1 | OK | K1 |
| zly_typ_katowy_P10 | K1 | OK | K1 |
| P04_3V3_do_3V3_IO | K7 | OK | K2, K3, K4, K6, K7, K8 |
| PG_SEND_PG_LINK_zmostkowane | K8 | OK | K2, K3, K4, K6, K8 |
| zamieniony_pin_P04_MOTOR_PERMIT_PWM_OUT | K2 | OK | K2, K3, K4, K6 |
| zamieniony_pin_P08_SENSOR_OK_HEALTHY | K2 | OK | K2, K3, K4, K6 |
| brak_sieci_DRIVE_OK | K2 | OK | K2, K3, K4, K8 |
| brak_konca_SAFE_N_P07 | K8 | OK | K2, K3, K4, K8 |
| pin_w_pin_P07_J_BP2_10_P04_J_BP2_10 | K7 | OK | K2, K3, K4, K6, K7 |
| zwarcie_5V_SYS_GND_P08 | K2 | OK | K2, K3, K4, K6, K7 |
| zly_typ_P07_J_BP1_2x10 | K1 | OK | K1 |
| zly_typ_katowy_P04_J_BP3 | K1 | OK | K1 |
| TP2_na_GND | K9 | OK | K3, K6, K7, K9 |
| dodatkowa_czesc_R1 | K10 | OK | K3, K8, K10 |

Kontrole nie zastępują odbioru na sprzęcie (NIE ZBADANO).
