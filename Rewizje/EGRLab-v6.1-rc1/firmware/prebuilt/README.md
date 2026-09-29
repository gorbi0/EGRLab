# Firmware 6.1-rc1

Pięć aktualnie skompilowanych wariantów: core, minimal, logger, test, wifi. ESP-IDF 5.4.3, ESP32-S3 N32R16V. EGR_HARDWARE_ACCEPTED=0. Nazwa aplikacji egrlab_v6.bin jest zachowana z projektu CMake; SHA256 i źródła wskazują tę rewizję w verification/builds.json. M2.1 wymaga zgodnego kompletu CORE/P08/SFAULT oraz VSENSE do DAQ. Nie wgrywać obrazów historycznych z reference/.

W terminalu ESP-IDF przejdź do katalogu wybranego wariantu i uruchom (po podstawieniu portu):

```
python -m esptool --chip esp32s3 -p COMx -b 460800 --before default_reset --after hard_reset write_flash "@flash_args"
```

Pierwsze uruchamianie według docs/03-uruchomienie.md. Aktywny TEST wymaga fizycznego odbioru, kalibracji, świadomej ponownej kompilacji i sprzętowego ARM. Kompilacja nie jest odbiorem sprzętu. Hasło domyślne wariantu Wi-Fi zmień przed użytkowaniem.
