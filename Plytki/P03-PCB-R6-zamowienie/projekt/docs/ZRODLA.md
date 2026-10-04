# Źródła i wyprowadzenia niezależne od generatora

## Uzupełnienie R5 (28.09.2026)

U4: **SN74LVC1G37DBVR**, [karta TI](https://www.ti.com/lit/gpn/SN74LVC1G37), lokalnie `reference/datasheets/SN74LVC1G37.pdf`. DBV: NC1, A2, GND3, Y4, VCC5. Wejście Schmitta, wyjście nieodwracające open-drain; limit szybkości zmian wejścia 100 ms/V; przy VCC=3 V dopuszczalne IOL=32 mA, VOL≤0,4 V przy 16 mA. To element montowany w R5; poniższe wpisy o SN74LVC1G07 są historią R2–R4. Parametry resetu i warunki pomiarów: `KONTRAKT-RESET.md` oraz `ZASILANIE-RESET.md`. Kody złącz i nierozstrzygnięte warunki przymiarki: `B2B-STATUS.md`.

Sprawdzone 26.09.2026. Tabele producentów, nie rysunki sprzedawców, są podstawą nowych pinów. Kopie not TI/AOS i schematu Waveshare w `reference/datasheets/`; hash w manifeście. Nota LTC4412 Rev. C została w R2 zweryfikowana w przeglądarce źródłowej (14 stron). W R3 dołączono lokalną kopię wcześniejszego wydania karty Linear (4412f, 12 stron) z serwera DigiKey: `reference/datasheets/LTC4412.pdf`, SHA256 w `sources.json`.

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

## Uzupełnienia R3 (27.09.2026)

| Część | Fakt użyty w R3 | Źródło |
|---|---|---|
| LTC4412 | VIN i SENSE zasilają układ; bramka klampowana 7 V poniżej wyższego z nich; wyłączenie wsteczne przy SENSE > VIN + 20 mV | `reference/datasheets/LTC4412.pdf`, s. 5–6 i 8 |
| MCP23017 | RESET jest wejściem Schmitta: VIL 0,2 VDD, VIH 0,8 VDD (tabela DC) | DS20001952, link wyżej |
| 74LVC125A Nexperia Rev. 12 | Δt/ΔV ≤ 10 ns/V przy VCC 2,7–3,6 V (tab. 5); VIH 2,0 V, VIL 0,8 V (tab. 6) | link wyżej |
| SN74LVC1G07 | VOL ≤ 0,1 V przy 100 µA; 0,55 V przy 24 mA (VCC 3 V) | `reference/datasheets/SN74LVC1G07.pdf` |
| TPS3808 | CT otwarte = ok. 20 ms; MR z wewnętrznym 90 kΩ do VDD | `reference/datasheets/TPS3808.pdf` |

## Uzupełnienia R4 (27.09.2026)

| Część / dane | Fakt użyty w R4 | Źródło |
|---|---|---|
| SN74LVC1G17 (TI SCES351Y, X 2025) | DBV: 1 NC, 2 A, 3 GND, 4 Y, 5 VCC. Przy VCC 3 V: VT+ 1,48–1,92 V, VT− 0,89–1,2 V, histereza 0,51–0,83 V; VOH ≥ 2,4 V przy −16 mA, ≥ 2,3 V przy −24 mA; zalecane IOH/IOL ±24 mA (maks. ±50 mA); Ioff ±10 µA. Brak wymagania szybkości zbocza wejściowego; karta wskazuje wolne i zaszumione wejścia jako zastosowanie | `reference/datasheets/SN74LVC1G17.pdf`, tab. 5.3 i 5-1; SHA256 w `sources.json` |
| Taśma H_SAFE (P04-R2.1) | J2 P04: taśma 16 żył AWG28, raster 1,27 mm, 150 mm, końcówka żeńska IDC16 | `Plytki/P04-R2.1-review/docs/MECHANIKA.md` |
| Obciążenie J4.15 | Ok. 20 pF (taśma 150 mm, wejście 74LVC125A, ścieżki) — szacunek, nie dane producenta; rozstrzyga pomiar w `ODBIOR.md` | szacunek |
