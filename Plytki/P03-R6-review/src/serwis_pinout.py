"""P03 R6 (format S1 §6): three right-angle 1x13 service headers on edge B, one per slot, GND on pins 1 and 13.
Every other pin reaches its node through a series resistor placed at the node: 1K for rails <= 5 V and driven logic,
10K for high-impedance nodes (pull-up/pull-down or open-drain only). Content from docs/ODBIOR.md (R5).
30.09 (layout): pins grouped by the position of their nodes on the board (J_SV1 = nodes in S1, J_SV2 = S2, J_SV3 = S3), so the
lines from the resistors to the headers stay in their slot; the first router runs left 12 of 33 service lines crossing the board.
1.10 (review, user decision): inside each header the rails sit next to each other and next to 10K lines already pulled up, so a
slipped probe cannot drive a logic input from a rail through 2 kOhm; order kept close to the routable one of 30.09 (the variants with
the rails on pins 2-3 and the one with the fewest straight-line crossings did not complete routing); SUP_N_OUT through 10K (exception).
Pin -> (node net, resistor value, purpose). The header-side net is named SV_<node>.
"""
SERWIS = {
 'J_SV1': {  # S1: MCP23017, dekoder, panel (LOGGER_CURRENT_OK od 30.09: bufor U14), I2C
  # 1.10 (recenzja, decyzja użytkownika): kolejność z 30.09 (ta się trasowała) z minimalnymi zmianami: szyny 3V3_IO / 3V3_CORE obok siebie
  # (9-10), z drugiej strony linie I2C (10K, i tak podciągnięte do 3,3 V); LOGGER_CURRENT_OK przy GND i SDA (poślizg sondy daje "nie OK");
  # MOTOR_INB/INA przy GND i MEAS_BANK (start 0), z dala od szyn i linii trzymanych w stanie wysokim (pływające wejścia MCP przy starcie)
  2: ('MOTOR_INB', '1K', 'MCP23017; brak ruchu przy starcie'), 3: ('MOTOR_INA', '1K', 'MCP23017; brak ruchu przy starcie'),
  4: ('MEAS_BANK', '1K', 'wejscie A dekodera, start: 0'), 5: ('CS_ILOG_N', '1K', 'start: 1'), 6: ('SCOPE_TRIG', '1K', 'wyjscie GPIO41 przed R12'),
  7: ('CS_ITEST_N', '1K', 'start: 1'), 8: ('I2C_SCL', '10K', 'I2C MCP23017 (OD, 4k7)'), 9: ('3V3_IO', '1K', 'szyna z P02 R4 (OE U14)'),
  10: ('3V3_CORE', '1K', 'LDO modulu; zapad przez 3,07 V'), 11: ('I2C_SDA', '10K', 'I2C MCP23017 (OD, 4k7)'),
  12: ('LOGGER_CURRENT_OK', '1K', 'z P06 (10k R2 do GND)')},
 'J_SV2': {  # S2: zasilanie 5 V, nadzor, PFAIL_N, DAQ, SD
  # 1.10: kolejność z 30.09 z jedną zamianą (PFAIL_N <-> CURRENT_CS_N): szyny 5 V na końcach przy GND, obok PFAIL_N i SUP_RAW_N (10K)
  2: ('5V_SYS', '1K', 'szyna z P02 R4; tabela zasilania P02/USB'), 3: ('PFAIL_N', '10K', 'wejscie z P02 R4 po stronie zlacza (100k R43)'),
  4: ('ADC_RESET', '1K', 'start bez firmware: 0'), 5: ('MEAS_EN', '1K', 'start bez firmware: 0'), 6: ('ADC_BUSY', '1K', 'odpowiedz P05 na CONVST'),
  7: ('ADC_CONVST', '1K', 'start bez firmware: 0'), 8: ('ADC_CS', '1K', 'start: 1 (nieaktywne)'),
  9: ('CURRENT_CS_N', '1K', '/G dekodera U2, start: 1'), 10: ('SD_CS', '1K', 'karta SD, start: 1'),
  11: ('SUP_RAW_N', '10K', 'wyjscie TPS3808 (OD, 10k R13)'), 12: ('5V_M1', '1K', 'zasilanie modulu za blokada U5/Q1; USB-only, prad wsteczny')},
 'J_SV3': {  # S3: SAFE P04, TEMP P09, reset do P04; SUP_N od 30.09 (wezel przy U6)
  2: ('MCU_ARM', '1K', 'GPIO39; bez ARM stale 0'), 3: ('HEARTBEAT', '1K', 'GPIO21 do P04'), 4: ('PWM', '1K', 'GPIO1 do P04'),
  5: ('CORE_LINK', '10K', 'R14 1k z 3V3_CORE; na P04 >= 2,7 V'),
  6: ('SUP_N_OUT', '10K', 'reset do P04 za U6/R41; 10K (1.10, wyjatek od S1 par. 6): galaz serwisowa nie spowalnia zbocza resetu'),
  7: ('SENSOR_ENABLE', '1K', 'MCP23017 GPA3 do P04'), 8: ('TC2_CS', '1K', 'start: 1'), 9: ('TC1_CS', '1K', 'start: 1'),
  10: ('INTERLOCK', '1K', 'z P04'), 11: ('HW_ARMED', '1K', 'z P04; stale L w probach resetu'),
  12: ('SUP_N', '10K', 'wspolny reset = EN modulu (J1-3) + RESET MCP23017')},
}
