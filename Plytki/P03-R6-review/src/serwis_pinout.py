"""P03 R6 (format S1 §6): three right-angle 1x13 service headers on edge B, one per slot, GND on pins 1 and 13.
Every other pin reaches its node through a series resistor placed at the node: 1K for rails <= 5 V and driven logic,
10K for high-impedance nodes (pull-up/pull-down or open-drain only). Content from docs/ODBIOR.md (R5).
Pin -> (node net, resistor value, purpose). The header-side net is named SV_<node>.
"""
SERWIS = {
 'J_SV1': {  # S1: zasilanie i reset
  2: ('5V_SYS', '1K', 'szyna z P02 R4; tabela zasilania P02/USB'), 3: ('5V_M1', '1K', 'zasilanie modulu za blokada U5/Q1; USB-only, prad wsteczny'),
  4: ('3V3_CORE', '1K', 'LDO modulu; zapad przez 3,07 V'), 5: ('3V3_IO', '1K', 'szyna z P02 R4 (OE U14)'),
  6: ('SUP_RAW_N', '10K', 'wyjscie TPS3808 (OD, 10k R13)'), 7: ('SUP_N', '10K', 'wspolny reset = EN modulu (J1-3) + RESET MCP23017'),
  8: ('SUP_N_OUT', '1K', 'reset do P04 za U6/R41 (zwarcie J_BP3.12: 11-16 mA)'), 9: ('PFAIL_N', '10K', 'wejscie z P02 R4 po stronie zlacza (10k R43)'),
  10: ('I2C_SCL', '10K', 'I2C MCP23017 (OD, 4k7)'), 11: ('I2C_SDA', '10K', 'I2C MCP23017 (OD, 4k7)'), 12: ('SCOPE_TRIG', '1K', 'wyjscie GPIO41 przed R12')},
 'J_SV2': {  # S2: stany startowe DAQ i linii CS
  2: ('MEAS_EN', '1K', 'start bez firmware: 0'), 3: ('ADC_RESET', '1K', 'start bez firmware: 0'), 4: ('ADC_CONVST', '1K', 'start bez firmware: 0'),
  5: ('ADC_CS', '1K', 'start: 1 (nieaktywne)'), 6: ('ADC_BUSY', '1K', 'odpowiedz P05 na CONVST'), 7: ('CS_ILOG_N', '1K', 'start: 1'),
  8: ('CS_ITEST_N', '1K', 'start: 1'), 9: ('CURRENT_CS_N', '1K', '/G dekodera U2, start: 1'), 10: ('MEAS_BANK', '1K', 'wejscie A dekodera, start: 0'),
  11: ('SD_CS', '1K', 'karta SD, start: 1'), 12: ('TC1_CS', '1K', 'start: 1')},
 'J_SV3': {  # S3: SAFE, TEMP, naped
  2: ('TC2_CS', '1K', 'start: 1'), 3: ('PWM', '1K', 'GPIO1 do P04'), 4: ('HEARTBEAT', '1K', 'GPIO21 do P04'), 5: ('MCU_ARM', '1K', 'GPIO39; bez ARM stale 0'),
  6: ('HW_ARMED', '1K', 'z P04; stale L w probach resetu'), 7: ('INTERLOCK', '1K', 'z P04'), 8: ('SENSOR_ENABLE', '1K', 'MCP23017 GPA3 do P04'),
  9: ('CORE_LINK', '10K', 'R14 1k z 3V3_CORE; na P04 >= 2,7 V'), 10: ('MOTOR_INA', '1K', 'MCP23017; brak ruchu przy starcie'),
  11: ('MOTOR_INB', '1K', 'MCP23017; brak ruchu przy starcie'), 12: ('LOGGER_CURRENT_OK', '1K', 'z P06 (10k R2 do GND)')},
}
