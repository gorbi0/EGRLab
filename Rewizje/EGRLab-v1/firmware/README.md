# ESP-IDF source project

Target: ESP32-S3, Waveshare N32R16-M. Start with ESP-IDF5.4.x and the supplied `sdkconfig.defaults`. Confirm memory settings in menuconfig before flashing. No eFuse programming is required by this project.

Active output is disabled twice: `CONFIG_EGR_ACTIVE_TEST=n` and `EGR_HARDWARE_ACCEPTED=0` in `main/commissioning.h`. Hardware acceptance, measured calibration and a physical ARM are required before motor operation. Never connect TEST to the vehicle ECU wiring.

The reference code has **not been target-compiled or hardware-tested** in the authoring environment. Read `../docs/03-uruchomienie.md` and `../docs/06-weryfikacja.md` before treating it as an operational instrument.

The default ADC rate is2kS/s.20kS/s is an acceptance target, not a verified capability of the eight-transaction hardware-mode driver. The source intentionally reports timing loss rather than concealing it.

Host control tests, with a C11 compiler:

```sh
cc -std=c11 -Wall -Wextra -I main ../tests/test_control.c main/control.c -lm -o test_control
./test_control
```

Configuration changes must be reviewed together with the wiring. The supplied pinout uses GPIO38 for INB (the board RGB input shares it), GPIO43/44 remain reserved for CH343, and GPIO47/48 are not used.
