"""Recenzja P04-R1, uwaga R4-01: margines progu nadzorcy U11 względem 3V3_IO z P02 (TRACO TSR 2-2433).
Źródła: TRACO TSR 2 (kopia tekstu w Plytki/P02-R2-review/reference/TRACO_TSR2.txt): dokładność ±2 %, linia 0,5 %,
obciążenie 1 %, tętnienia 50 mV p-p; Microchip MCP1X0 (DS11184, kopia w Plytki/P05-R1-review/reference/datasheets):
-315: 3,00-3,15 V, -300: 2,85-3,00 V (-40...+85 °C), histereza 50 mV typ."""
V = 3.3
dc_min = V * (1 - 0.02 - 0.005 - 0.01)
valley = dc_min - 0.050 / 2
for name, vmax in (('MCP100-315', 3.15), ('MCP100-300', 3.00)):
    release = vmax + 0.050
    print(f'{name}: 3V3_IO min DC {dc_min:.3f} V, dolina tętnień {valley:.3f} V; próg max {vmax:.2f} V -> zapas {1000 * (valley - vmax):+.0f} mV; '
          f'zwolnienie resetu do {release:.2f} V -> zapas {1000 * (dc_min - release):+.0f} mV')
