# Źródła i wyprowadzenia niezależne od generatora

Sprawdzone 26.09.2026. Tabele producentów, nie rysunki sprzedawców, są podstawą nowych pinów. Kopie not TI/AOS i schematu Waveshare w `reference/datasheets/`; hash w manifeście. Nota LTC4412 Rev. C została zweryfikowana w przeglądarce źródłowej (14 stron); bezpośrednie pobranie PDF zakończyło się timeoutem, dlatego w pakiecie jest link i tabela pinów, bez lokalnej kopii tej noty.

| Część | Fakty użyte w R2 | Źródło |
|---|---|---|
| TPS3808G33DBV | RESET1, GND2, MR3, CT4, SENSE5, VDD6; próg 3,07 V, wyjście OD | https://www.ti.com/lit/ds/symlink/tps3808.pdf |
| SN74LVC1G07DBVR | NC1, A2, GND3, Y4, VCC5; nieodwracający OD | https://www.ti.com/lit/ds/symlink/sn74lvc1g07.pdf |
| LTC4412IS6 | VIN1 GND2 CTL3 STAT4 GATE5 SENSE6; CTL=LOW włącza | https://www.analog.com/media/en/technical-documentation/data-sheets/ltc4412.pdf |
| AO3401A | SOT23 G1 S2 D3; 85 mΩ przy VGS=-2,5 V i 25°C | https://www.aosmd.com/pdfs/datasheet/AO3401A.pdf |
| Waveshare rodzina DEV-KIT | USB przez D1 do VDDUSB/5V listwy; EN 10K/1uF i auto-reset | https://files.waveshare.com/wiki/ESP32-S3-DEV-KIT-N8R8/ESP32-S3-DEV-KIT-N8R8-schematic.pdf |
| MCP23017 | Po resecie IODIR=0xFF; GPPU=0 | https://ww1.microchip.com/downloads/aemDocuments/documents/APID/ProductDocuments/DataSheets/MCP23017-Data-Sheet-DS20001952.pdf |
| 74LVC125A Nexperia | Ioff dla częściowego wyłączenia; nie ustala wejścia zasilanego bufora | https://assets.nexperia.com/documents/data-sheet/74LVC125A.pdf |

Waveshare publikuje wspólny schemat rodziny N8R8/N32R16V. Potwierdzenie rewizji rzeczywistego modułu, zastosowanego LDO i obwodu EN jest kryterium odbioru, a nie założeniem wynikającym z samego oznaczenia pamięci.
