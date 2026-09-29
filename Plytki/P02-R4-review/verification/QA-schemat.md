# P02-R4 — QA schematu (etap 2, format S1; plik generowany przez src/run_schematic.py)

ERC: 0 naruszeń na 5 arkuszach. Netlista: 127 części, 342 pinów sprawdzonych, 0 błędów, 80 sieci.

Kontrole elektryczne: 39/39 PASS. Próby ujemne: 25/25 (w tym próba zerowa).

| Kontrola | Wynik | Wartość |
|---|---|---|
| C01 Every exported functional pin agrees with parts.py | PASS | 0 mismatches |
| T01 Q9 and Q1 back-to-back: Q9 D=BAT_IN S=SW_COM, Q1 S=SW_COM D=VSW (reverse polarity blocked by Q9 body diode) | PASS |  |
| T02 BAT_IN reaches only J1.1, Q9 drain and the service resistor R61 | PASS | J1.1, Q9.2, R61.1 |
| T03 Zener clamps D10/D4/D9: cathode SW_COM, anode on the gate of Q9/Q1/Q2 | PASS |  |
| T04 Gate block as P01 R3: C5 GATE-VSW, C6 GATE-SW_COM, Q2 S=SW_COM D->R27->GATE, Q4 E=SW_COM C=OFF_G, R23 OFF_G-GND | PASS |  |
| T05 PWR switch in the UVLO top branch: SW_COM-R5-J14-R9-UV_DIV, R10 to GND (open = UV_DIV at 0 V = off) | PASS |  |
| T06 Filter C13 on UV_DIV before R12; hysteresis R11 from OK into UV_CMP; U2B + = UV_CMP, - = REF, out = OK | PASS |  |
| T07 PFAIL_N buffers OK: U2A + = OK x R7/(R6+R7), - = REF; pull-up to 3V3_IO; R37 to PFAIL_N at J_BP.14 | PASS |  |
| T08 SAFE_N as P01: Q7 base fed only from J_BP.15 (P04 3V3, separate from local 3V3_IO; R58 = service pin); Q8 released by ENABLE | PASS |  |
| T09 C_H: charged only via R40 + D2 (K = HOLD_C), discharged only via D1 A2; D1 A1 = VSW, K = VLOG | PASS |  |
| T10 VMOTOR only from VSW through F1; nothing else on VMOTOR but J2.1 and the service resistor R66 | PASS |  |
| T11 TSR inputs from VLOG through F2/F3 | PASS |  |
| T12 AUX5 supply V_CTRL = SW_COM (D11) OR VLOG (D12) | PASS |  |
| T13 VBAT: J15 - R38 - VBAT_SENSE (D13 bidirectional TVS to GND) - J_BP.20; no GND wire from the car | PASS |  |
| T14 TVS on VSW with VWM >= 16.8 V | PASS | 5KP24A: VWM 24.0 V |
| T15 Z-01: no damage at a steady 25 V (5S by mistake): VBR min of the VSW transil >= 25 V (R4E1-01) | PASS | 5KP24A: VBR min 26.7 V |
| T16 J_BP pinout = S1 section 8 (GND 1,3,5,7,9,11,13,19; 5V_SYS 2,4,6; 3V3_IO 8,10; 12 PSU_OK, 14 PFAIL_N, 15 P04_3V3, 16 SAFE_N, 17 PG_SEND, 18 PG_LINK, 20 VBAT_SENSE) | PASS |  |
| T17 Service headers (S1 section 6): <= 13 pins, GND on both ends, every other pin only through one series resistor of its class (4K7 pack rails, 10K high-impedance, 1K logic/<= 5 V); all O-01..O-09 points present | PASS |  |
| U01 Nominal UVLO matches spec 13.53 / 12.51 V within 0.05 V | PASS | 13.501 / 12.548 V |
| U02 Z-03: no start at 12.6 V (3S full) in any corner (on_min > 12.6 V) | PASS | on_min 12.90 V |
| U03 Rested 4S at 3.6 V/cell (14.4 V) always starts (on_max < 14.4 V) | PASS | on_max 14.08 V |
| U04 Off threshold >= 11.6 V in all corners (2.9 V/cell, above the BMS cut-off 2.5..2.8 V/cell); on > off per corner is U05 | PASS | off 11.98..13.11 V |
| U05 Hysteresis >= 0.7 V in all corners (D-05) | PASS | 0.84 V |
| P01 PFAIL_N follows OK with >= 0.2 V margin both ways (U2A) | PASS | high 0.23 V, low 2.19 V |
| P02 U2 inputs: REF inside the LM2903 CM range over temperature (one input in range) | PASS |  |
| P03 Z-09: PFAIL_N edge <= 100 us after OK/ENABLE change | PASS | 5.4 us |
| S01 Q1 turn-off after ENABLE loss <= 1 ms in all declared cases (R23 = 22k) | PASS | max 239 us |
| S02 Hot plug 25 V: VSG(Q1) step C5/(C5+C6+Ciss) <= 0.8 V (P01 R1 blocker rule) | PASS | 0.29 V |
| S03 Z-07: capacitive inrush at the 220 uF budget <= 3.0 A (nominal) | PASS | 2.53 A |
| S04 O-04: VSW slew 5..15 V/ms in all corners | PASS | 11.5, 14.7, 5.6 |
| S05 Start: Q1 peak <= 5 A and energy <= 50 mJ (P01 R3 accepted 137 mJ) | PASS | 3.69 A / 37 mJ, 4.40 A / 35 mJ, 2.31 A / 25 mJ |
| S06 Z-06: VSW cap <= 100 uF and switched on-board C <= 120 uF (>= 100 uF left for P07 within 220 uF) | PASS | C3 47 uF, on-board 89 uF, P07 allowance 131 uF |
| H01 Hold-up after PFAIL_N >= 10 ms at 6 W in the worst corner (firmware closes the file in <= 10 ms, spec section 9) | PASS | 11.1 ms |
| L01 Z-13: Q1 and Q9 each <= 1 W and Tj <= 110 C at 5 A, 50 C ambient, no heatsink (62 K/W) | PASS | 0.37 W at 3.5 A, 0.75 W at 5 A |
| L02 PWR wire shorted to GND: R5 <= 60 % of its rating (anti-surge 1206, 0.66 W) | PASS | 286 mW of 660 mW |
| L05 Service resistor with its pin shorted to GND: <= 50 % of its rating (node at its maximum voltage) | PASS | max 112 mW (R59) |
| L03 R23 static loss (Q4 on, OFF_G at SW_COM) <= 10 % of 0.5 W | PASS | 13.0 mW |
| L04 AUX5 regulates down to V_CTRL: LM2936 input >= 5.5 V at VLOG = 7 V | PASS | 5.89 V at 8.8 mA |
| R01 Z-14: every part on the pack-side nets rated >= 25 V (clamps and wire terminations listed as exempt) | PASS |  |

## Zgodność ze specyfikacją (informacyjnie, do decyzji)

| Wymaganie | Treść | Wynik | Spełnione |
|---|---|---|---|
| Z-02 | UVLO envelope (after etap 1): on 12.90..14.08 V, off 11.98..13.11 V, hysteresis >= 0.84 V | on 12.90..14.08 V, off 11.98..13.11 V, hysteresis >= 0.84 V | tak |
| Z-08 | after PFAIL_N >= 10 ms at 6 W in the worst corner (after etap 1); nominal 16.8 / 33.5 ms at 6 / 3 W | worst 11.1 / 22.3 ms; nominal 16.8 / 33.5 ms | tak |
| Z-01 | no damage at 0..25 V | 5KP24A on VSW: VBR min 26.7 V | tak |

## Próby ujemne

| Mutacja | Oczekiwana | Zgłoszone | Wykryta |
|---|---|---|---|
| null_control | all PASS | — | tak |
| c5_220n_hotplug | S02 | S02, S04, S05 | tak |
| c6_100n_hotplug | S02 | S02 | tak |
| r23_220k_slow_off | S01 | S01 | tak |
| pwr_bypassed | T05 | T05 | tak |
| safe_from_local_3v3 | T08 | T08, T16 | tak |
| d3_5kp18a_z01 | T15 | T15 | tak |
| jbp_5v_on_pin1 | T16 | T16 | tak |
| sv_pin_straight_to_vsw | T17 | T17 | tak |
| sv_no_gnd_at_end | T17 | T17 | tak |
| sv_bat_in_through_1k | T17 | T17, L05 | tak |
| sv_gate_through_100r | L05 | T17, L05 | tak |
| r9_36k5_starts_on_3s | U02 | U01, U02, U04, H01 | tak |
| r11_4m64_no_hysteresis | U05 | U01, U02, U05 | tak |
| dch_reversed | T09 | T09 | tak |
| ch_1000u | H01 | H01 | tak |
| pfail_from_uv_cmp_literal_D06 | T07 | T07 | tak |
| qrev_swapped | T01 | T01, T02 | tak |
| vmotor_unswitched | T10 | T10 | tak |
| r5_100r | L02 | U01, L02 | tak |
| r7_47k_pfail_divider | P01 | P01 | tak |
| c3_220u | S06 | S06 | tak |
| c13_on_feedback | T06 | T06 | tak |
| r1_1k_aux_dropout | L04 | L04 | tak |
| r10_11k5_off_too_low | U04 | U01, U02, U04, H01 | tak |

Oględziny PDF (5 stron A3): wykonane przy tworzeniu pakietu; etykiety czytelne, połączenia wyłącznie etykietami, sprawdzone pin po pinie.
