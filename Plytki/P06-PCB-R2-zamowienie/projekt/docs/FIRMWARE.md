# Współpraca z firmware i diagnostyka (P06-R2)

*R2 (1.10.2026): interfejs elektryczny bez zmian; sygnały przez J_BP i P12 zamiast taśmy ILOG do P03/J2. Konfiguracja sesji: płytka `P06-R2`, dzielnik 5,11 kΩ / 5,11 kΩ, C1 470 nF X7R (τ nominalnie 1200,9 µs — wpisać zmierzone).*

Interfejs elektryczny jest zgodny z v6.1: SPI mode 0, 500 kHz, 16 taktów CS, `raw = (word >> 1) & 0x0FFF`, nominalnie 2 kS/s. CS wybierany przez istniejący dekoder CORE, a LOGGER_CURRENT_OK odbierany przez MCP23017. Snapshot właściwych źródeł jest w `reference/board.c`. P06 nie wymaga nowego GPIO ESP32. W S1 CS_ILOG_N (P03 R6 J_BP1.2 → P06 J_BP.6) i LOGGER_CURRENT_OK (P06 J_BP.8 → P03 R6 J_BP1.11) prowadzi P12; ADC_SCLK/ADC_DOUTA to wspólna magistrala z P05 (J_BP2.2/4).

Przed pomiarem: wyłączyć zapłon → ustawić MEASURE → włączyć elektronikę → odczekać 1 s i potwierdzić READY → wykonać ZERO przy potwierdzonym braku prądu. Nie zerować podczas pracy ECU ani uznawać kodu z BYPASS za pomiar zerowego prądu. Przełącznika nie używać do znaczenia zdarzeń podczas rejestracji.

Konfiguracja sesji musi identyfikować płytkę `P06-R2`, RSH 0,005 Ω, INA240A2 G50, dzielnik 1:2, C1 470 nF X7R, nominalną stałą czasową 1200,9 µs (zmierzoną w E16) oraz indywidualne współczynniki ZERO/gain. Początkowe 204,8 kodu/A nie zastępuje kalibracji. Gdy format firmware nie ma pola stałej czasowej, do sesji dołączyć plik boczny `P06-calibration.json` według wzoru poniżej; nie nadpisywać historycznych plików ani nie udawać, że firmware już emituje to pole.

```json
{
  "board": "P06-R2",
  "serial": "DO_UZUPELNIENIA",
  "shunt_ohm": 0.005,
  "nominal_filter_tau_us": 1200.9,
  "sampling_hz": 2000,
  "zero_code_measured": null,
  "codes_per_amp_measured": null,
  "qualified_current_A": null,
  "calibration_temperature_C": null,
  "date": null
}
```

READY=0, przerwana taśma, błąd SPI lub niepotwierdzona kalibracja oznaczają brak ważnej wartości fizycznej. Samo READY=1 nie dowodzi poprawnego VREF ani prawidłowego styku prądowego. Sprawdzić na firmware odrzucenie danych w BYPASS i po zaniku zasilania. Nie zmieniono kodu firmware w innych katalogach; integracja musi przejść test wspólnej magistrali z P05, w tym powrót do trybu SPI właściwego dla AD7606B.

Dla P0404 porównywać w tej samej osi czasu: trend prądu P06, napięcia obu końców silnika z DAQ, pozycję EGR, zasilanie/masę czujnika, temperaturę i dostępne parametry ECU. Powtarzalny wzrost prądu z zatrzymaniem pozycji jest wskazówką przeciążenia mechanicznego, ale nie rozstrzyga samodzielnie przyczyny. Brak prądu przy niezmieniającej się pozycji wymaga sprawdzenia napięć i polecenia ECU. Szarpanie 1500-1700 rpm może mieć inną przyczynę; zachować dane odniesienia z poprawnej jazdy i nie stosować automatycznej diagnozy „uszkodzony EGR” na podstawie samego kanału prądu.
