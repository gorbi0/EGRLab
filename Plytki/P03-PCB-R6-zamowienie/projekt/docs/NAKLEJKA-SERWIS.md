# Naklejka na ścianę serwisową P03 R6 — opisy kołków J_SV1–J_SV3

Plik generowany przez `src/write_tables.py` z `src/serwis_pinout.py` i tabel opisów w `src/silkscreen.py` (decyzja 1.10.2026: legenda skrótów na naklejce zamiast na płytce, gdzie po złożeniu stosu leżała pod płytką poziomu 3). Wydrukować i nakleić na ściance serwisowej obudowy (strona krawędzi B) na wysokości poziomu 2.

Patrząc od krawędzi B (od strony serwisu): J_SV1 po lewej (slot S1), J_SV3 po prawej (slot S3); w każdej listwie pin 1 po prawej (większe x). Każdy kołek poza GND przez rezystor przy węźle (1 kΩ; 10 kΩ dla linii z podciąganiem / otwartym drenem i SUP_N_OUT).

| Kołek | J_SV1 (S1) | J_SV2 (S2) | J_SV3 (S3) |
|---:|---|---|---|
| 1 | GND | GND | GND |
| 2 | **MOT_INB** = MOTOR_INB | **5VS** = 5V_SYS | **ARM** = MCU_ARM |
| 3 | **MOT_INA** = MOTOR_INA | **PFL** = PFAIL_N | **HBT** = HEARTBEAT |
| 4 | **MBANK** = MEAS_BANK | **ARS** = ADC_RESET | PWM |
| 5 | **ILOG_N** = CS_ILOG_N | **MEN** = MEAS_EN | **LNK** = CORE_LINK |
| 6 | **SCOPE** = SCOPE_TRIG | **BSY** = ADC_BUSY | **SPO** = SUP_N_OUT |
| 7 | **ITEST_N** = CS_ITEST_N | **CNV** = ADC_CONVST | **SEN** = SENSOR_ENABLE |
| 8 | **SCL** = I2C_SCL | **ACS** = ADC_CS | **TC2** = TC2_CS |
| 9 | 3V3_IO | **CCS** = CURRENT_CS_N | **TC1** = TC1_CS |
| 10 | **3V3** = 3V3_CORE | **SDC** = SD_CS | **ILK** = INTERLOCK |
| 11 | **SDA** = I2C_SDA | **SRW** = SUP_RAW_N | **HWA** = HW_ARMED |
| 12 | **LCUR_OK** = LOGGER_CURRENT_OK | **5VM** = 5V_M1 | **SUP** = SUP_N |
| 13 | GND | GND | GND |
