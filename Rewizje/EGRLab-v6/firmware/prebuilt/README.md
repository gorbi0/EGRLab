# Obrazy V6 do etapowego uruchamiania

ESP-IDF 5.4.3 / ESP32-S3 N32R16V. Warianty core, minimal, logger, test, wifi. Każdy ma EGR_HARDWARE_ACCEPTED=0; aktywny TEST wymaga odbioru sprzętu i ponownej kompilacji. Zegary startowe: AD1MHz, SD4MHz, lokalny prąd500kHz. Płytki i wiązki muszą odpowiadać HW6.0/M2. Dawne profile NVS EGR5 zostaną odrzucone; potrzebna nowa kalibracja.

Każdy katalog zawiera bootloader, tablicę partycji, aplikację i flash_args. W terminalu ESP-IDF, we właściwym podkatalogu, podstaw swój port:

```
python -m esptool --chip esp32s3 -p COMx -b 460800 --before default_reset --after hard_reset write_flash @flash_args
```

W PowerShell ostatni argument zapisz jako "@flash_args". Programuj przy odłączonym EGR i LOGGER. Hasło Wi-Fi w obrazie jest domyślne; zmień je przed użyciem i przebuduj. Sumy, konfiguracje i logi: verification/. Kompilacja nie oznacza sprawdzenia na urządzeniu.
