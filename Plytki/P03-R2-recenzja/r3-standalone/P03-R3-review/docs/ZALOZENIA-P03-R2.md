# Zakres P03 (R2, uzupełnione w R3)

*Nazwa pliku z R2. R3 (27.09.2026): R14 = 1 kΩ, wymagania interfejsowe dla P09/P10, bez zmiany miedzi.*

Płyta CORE dla EGRLab: zachowany ESP32-S3 N32R16V Waveshare, lokalne SD, MCP23017, dekoder CS i bufory Ioff. Rewizja naprawia problemy recenzji P03-R1; nie zmienia modułów pomiarowych, zaworu, P01 ani P07.

Schemat zawiera 88 pozycji na PCB, dodatkowo 5 otworów. Dwie warstwy 35 µm. Domyślne sygnały: ścieżka 0,30 mm, odstęp 0,25 mm. Zasilanie: odgałęzienia 0,60 mm/0,30 mm, główny tor J10-Q1-M1 trasowany 1 mm. Przelotki sygnałowe 0,8/0,4 mm, GND przy odsprzęganiu 1,0/0,5 mm. Nie wyłączać DRC w celu uzyskania zera.

Każda zmiana pinów istniejącej części musi znaleźć się na krótkiej liście w niezależnym `verify_function.py`. Złącza bez zmian. B2B i antena pozostają jawnie niezakwalifikowane fizycznie. Wydanie nie zawiera zatwierdzenia do produkcji ani wyników sprzętowych.

## Wymagania dla modułów po drugiej stronie złączy (R3)

- **P10 (CAN):** CAN_RX ma na P03 10 kΩ do 3V3_CORE po stronie złącza (stan recesywny bez P10). Gdy P10 jest wyłączony, a P03 zasilony, do wyjścia RXD transceivera wpływa do 0,35 mA. RXD P10 musi to znosić (Ioff albo rezystor szeregowy na P10).
- **P09 (TEMP):** SPI3_MISO jest wspólne z kartą SD na P03 (J7.5). Wyjście MISO P09 musi być w wysokiej impedancji także bez zasilania P09, inaczej karta SD nie odczyta danych przy zasilaniu samym USB. Na Adafruit 4682 widać drabinki „473” (najpewniej 47 kΩ podciągania linii SD); z R33 10 kΩ linia spoczynkowo ma ≈ 0,6 V, czyli poprawne L.
- **P04 (SAFE):** CORE_LINK przez R14 1 kΩ, na P04 ≥ 2,85 V. SUP_N ma wolne zbocze (EN modułu) — `ZASILANIE-RESET.md`.

