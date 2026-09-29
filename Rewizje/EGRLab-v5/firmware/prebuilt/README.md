# Skompilowane obrazy do uruchamiania

ESP-IDF 5.4.3, ESP32-S3 N32R16V: flash 32 MB OPI i PSRAM 16 MiB OCT. W każdym wariancie **EGR_HARDWARE_ACCEPTED=0**. Obrazy TEST/Wi-Fi nie są zatwierdzeniem sprzętu i nie dopuszczają aktywnego testu przed ponowną kompilacją po odbiorze. Do etapu CORE wybierz `core`, potem według dokumentacji odpowiedni wariant.

Każdy podkatalog zawiera bootloader, tablicę partycji, aplikację i wygenerowane `flash_args`. W terminalu ESP-IDF przejdź do wybranego podkatalogu i użyj własnego portu:

```
python -m esptool --chip esp32s3 -p COMx -b 460800 --before default_reset --after hard_reset write_flash @flash_args
```

W PowerShell przekaż ostatni argument jako `"@flash_args"`. Wgrywanie wykonuj przy odłączonym zaworze i porcie LOGGER. Układ GPIO i osprzęt muszą odpowiadać v5; obrazy nie są przeznaczone do okablowania v4.1/MOD0.1. Hasło Wi-Fi w obrazie jest domyślne; przed użyciem Wi-Fi ustaw własne i przebuduj firmware.

Sumy i rozmiary: `verification/builds.json`; użyte sdkconfig oraz logi kompilacji są w verification/. Nie sprawdzono uruchomienia binariów na fizycznej płytce.
