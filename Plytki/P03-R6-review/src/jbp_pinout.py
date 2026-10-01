"""P03 R6 (format S1): pinout of the three edge-A connectors J_BP1..J_BP3 (IDC 2x10, right angle, one per slot).
Single source for parts.py and docs/J_BP.csv. Ribbon order = pin number (1..20), so pin n neighbours n-1 and n+1.
Rules (task ZADANIE-P03-S1 §2): odd pins GND where possible; ADC_SCLK, SPI3_SCLK and MEAS_EN with GND on both sides;
an odd pin that is not GND carries only a static signal or a supply (exceptions listed in EXCEPTIONS with a reason).
Group moves against the task table (reasons in README): TEMP J_BP2 -> J_BP3 (P09 sits in S3), PFAIL_N J_BP3 -> J_BP2,
P07 group (DIR + ITEST) J_BP3 -> J_BP1. Without them J_BP2 or J_BP3 would carry 15 signals with 5 GND, which cannot give
every clock two GND neighbours and every edge signal one.
Columns: pin -> (net, direction seen from P03, target boards, note).
"""
G = ('GND', 'gnd', 'P12 (wszystkie)', '')
JBP = {
 'J_BP1': {  # slot S1: panel P11 (x = 0), P10 CAN, P06 ILOG, P08 SENSOR, P07 (DIR, ITEST)
  1: G, 2: ('CS_ILOG_N', 'out', 'P06', 'U22 (dekoder U2 Y0)'), 3: G, 4: ('CS_ITEST_N', 'out', 'P07', 'U22 (dekoder U2 Y1)'), 5: G,
  6: ('CAN_TX', 'out', 'P10', 'GPIO17 bezposrednio'), 7: G, 8: ('CAN_RX', 'in', 'P10', 'U11, domyslnie 1 (recessive)'), 9: G,
  10: ('N_J_SCOPE_HOT', 'out', 'P11 (BNC SCOPE)', 'SCOPE_TRIG przez R12 330R'),
  11: ('LOGGER_CURRENT_OK', 'in', 'P06', 'statyczny; wyjatek od GND na nieparzystym'), 12: ('SENSOR_HEALTHY', 'in', 'P08', 'statyczny'),
  13: ('MARK', 'in', 'P11', 'przycisk; statyczny; wyjatek'), 14: ('TEST_KEY', 'in', 'P11', 'przelacznik; statyczny'),
  15: ('LOGGER_CLEAR', 'in', 'P11', 'przycisk; statyczny; wyjatek'), 16: ('TEST_PRESENT', 'in', 'P11', 'statyczny'),
  17: ('ENA_DIAG', 'in', 'P07', 'statyczny; wyjatek'), 18: ('ENB_DIAG', 'in', 'P07', 'statyczny'),
  19: ('MOTOR_INA', 'out', 'P07', 'MCP23017, statyczny; wyjatek'), 20: ('MOTOR_INB', 'out', 'P07', 'MCP23017, statyczny')},
 'J_BP2': {  # slot S2: P05 DAQ (poziom 3, S1-S2), wspolna magistrala ADC do P05/P06/P07, PFAIL_N i 5V_SYS z P02 R4
  1: G, 2: ('ADC_SCLK', 'out', 'P05, P06, P07', 'zegar; GND po obu stronach; P12 rozprowadza wielopunktowo'), 3: G,
  4: ('ADC_DOUTA', 'in', 'P05, P06, P07', 'wspolna linia danych; P12 wielopunktowo'), 5: G, 6: ('ADC_SDI', 'out', 'P05', ''), 7: G,
  8: ('ADC_CS', 'out', 'P05', ''), 9: G, 10: ('ADC_CONVST', 'out', 'P05', 'zbocze startu przetwarzania'), 11: G,
  12: ('ADC_BUSY', 'in', 'P05', ''), 13: G, 14: ('MEAS_EN', 'out', 'P05', 'GND po obu stronach'), 15: G,
  16: ('PFAIL_N', 'in', 'P02 R4', 'aktywny niski; na P03 1k szeregowo + 100k do 3V3_CORE; GND na 15'),
  17: ('5V_SYS', 'pwr', 'P02 R4', 'trzecia zyla zasilania P03 (30.09); wyjatek od GND na nieparzystym'),
  18: ('ADC_RESET', 'out', 'P05', 'statyczny, miedzy zylami 5V_SYS'),
  19: ('5V_SYS', 'pwr', 'P02 R4', 'zasilanie P03; wyjatek od GND na nieparzystym'), 20: ('5V_SYS', 'pwr', 'P02 R4', 'zasilanie P03')},
 'J_BP3': {  # slot S3: P04 SAFE (poziom 4, S2-S3), P09 TEMP (poziom 3, S3), 3V3_IO z P02 R4
  1: G, 2: ('SPI3_SCLK', 'out', 'P09', 'zegar; GND po obu stronach'), 3: G, 4: ('SPI3_MOSI', 'out', 'P09', ''),
  5: ('3V3_IO', 'pwr', 'P02 R4', 'zasilanie OE U14; wyjatek (zasilanie odsprzezone)'), 6: ('SPI3_MISO', 'in', 'P09', 'wspolne z karta SD na P03'), 7: G,
  8: ('TC1_CS', 'out', 'P09', ''), 9: ('SENSOR_ENABLE', 'out', 'P04', 'MCP23017, statyczny; wyjatek'), 10: ('TC2_CS', 'out', 'P09', ''), 11: G,
  12: ('SUP_N_OUT', 'out', 'P04', 'reset przez U6 (Schmitt) i R41 220R'), 13: ('CORE_LINK', 'out', 'P04', '3V3_CORE przez R14 1k, statyczny; wyjatek'),
  14: ('PWM', 'out', 'P04', 'GPIO1 bezposrednio'), 15: G, 16: ('HEARTBEAT', 'out', 'P04', 'GPIO21 bezposrednio'),
  17: ('HW_ARMED', 'in', 'P04', 'statyczny; wyjatek'), 18: ('MCU_ARM', 'out', 'P04', 'statyczny'), 19: G,
  20: ('INTERLOCK', 'in', 'P04', 'statyczny')},
}
EXCEPTIONS = {  # odd pins that are not GND, with the one-line reason required by the task
 ('J_BP1', 11): 'J_BP1 ma 15 sygnalow (panel, CAN, ILOG, SENSOR, P07); piny 11-19 to blok sygnalow statycznych',
 ('J_BP1', 13): 'jw.', ('J_BP1', 15): 'jw.', ('J_BP1', 17): 'jw.', ('J_BP1', 19): 'jw.',
 ('J_BP2', 17): 'trzecia zyla 5V_SYS (30.09: spadek na tasmie i P12 przy 0,8 A wobec 4,85 V); zasilanie, nie sygnal',
 ('J_BP2', 19): 'druga zyla 5V_SYS (IDC ok. 1 A na styk); zasilanie, nie sygnal',
 ('J_BP3', 5): '3V3_IO (zasilanie odsprzezone) jako powrot AC dla SPI3_MOSI/MISO',
 ('J_BP3', 9): 'SENSOR_ENABLE statyczny miedzy liniami CS termopar',
 ('J_BP3', 13): 'CORE_LINK statyczny (1k z 3V3_CORE)',
 ('J_BP3', 17): 'HW_ARMED statyczny (wejscie odpytywane przez U12)',
}
