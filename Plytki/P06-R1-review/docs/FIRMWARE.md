# Współpraca z firmware i diagnostyka

Interfejs elektryczny jest zgodny z v6.1: SPI mode 0, 500 kHz, 16 taktów CS, `raw = (word >> 1) & 0x0FFF`, nominalnie 2 kS/s. CS wybierany przez istniejący dekoder CORE, a LOGGER_CURRENT_OK odbierany przez MCP23017. Snapshot właściwych źródeł jest w `reference/board.c`. P06 nie wymaga nowego GPIO ESP32. P03-R2/J2 i P06/J2 mają identyczne funkcje pinów; nr 2 pozostaje kluczem.

Przed pomiarem: wyłączyć zapłon → ustawić MEASURE → włączyć elektronikę → odczekać 1 s i potwierdzić READY → wykonać ZERO przy potwierdzonym braku prądu. Nie zerować podczas pracy ECU ani uznawać kodu z BYPASS za pomiar zerowego prądu. Przełącznika nie używać do znaczenia zdarzeń podczas rejestracji.

Konfiguracja sesji musi identyfikować płytkę `P06-R1`, RSH 0,005 Ω, INA240A2 G50, dzielnik 1:2, C1 470 nF, nominalną stałą czasową 1198,5 µs oraz indywidualne współczynniki ZERO/gain. Początkowe 204,8 kodu/A nie zastępuje kalibracji. Gdy format firmware nie ma pola stałej czasowej, do sesji dołączyć plik boczny `P06-calibration.json` według wzoru poniżej; nie nadpisywać historycznych plików ani nie udawać, że firmware już emituje to pole.

```json
{
  "board": "P06-R1",
  "serial": "DO_UZUPELNIENIA",
  "shunt_ohm": 0.005,
  "nominal_filter_tau_us": 1198.5,
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
