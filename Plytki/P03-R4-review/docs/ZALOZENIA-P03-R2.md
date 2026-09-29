# Zakres P03 (R2, uzupełnione w R3)

*Nazwa pliku z R2. R3 (27.09.2026): R14 = 1 kΩ, wymagania interfejsowe dla P09/P10, bez zmiany miedzi. R4 (27.09.2026): bufor Schmitta U6 z R41 i C15 w resecie do P04, lokalna zmiana miedzi przy J4.*

Płyta CORE dla EGRLab: zachowany ESP32-S3 N32R16V Waveshare, lokalne SD, MCP23017, dekoder CS i bufory Ioff. Rewizja naprawia problemy recenzji P03-R1; nie zmienia modułów pomiarowych, zaworu, P01 ani P07.

Schemat zawiera 91 pozycji na PCB (R4: + U6, R41, C15), dodatkowo 5 otworów. Dwie warstwy 35 µm. Domyślne sygnały: ścieżka 0,30 mm, odstęp 0,25 mm. Zasilanie: odgałęzienia 0,60 mm/0,30 mm, główny tor J10-Q1-M1 trasowany 1 mm. Przelotki sygnałowe 0,8/0,4 mm, GND przy odsprzęganiu 1,0/0,5 mm. Nie wyłączać DRC w celu uzyskania zera.

Każda zmiana pinów istniejącej części musi znaleźć się na krótkiej liście w niezależnym `verify_function.py`. Złącza bez zmian. B2B i antena pozostają jawnie niezakwalifikowane fizycznie. Wydanie nie zawiera zatwierdzenia do produkcji ani wyników sprzętowych.

## Wymagania dla modułów po drugiej stronie złączy (R3)

- **P10 (CAN):** CAN_RX ma na P03 10 kΩ do 3V3_CORE po stronie złącza (stan recesywny bez P10). Gdy P10 jest wyłączony, a P03 zasilony, do wyjścia RXD transceivera wpływa do 0,35 mA. RXD P10 musi to znosić (Ioff albo rezystor szeregowy na P10).
- **P09 (TEMP):** SPI3_MISO jest wspólne z kartą SD na P03 (J7.5). Wyjście MISO P09 musi być w wysokiej impedancji także bez zasilania P09, inaczej karta SD nie odczyta danych przy zasilaniu samym USB. Na Adafruit 4682 widać drabinki „473” (najpewniej 47 kΩ podciągania linii SD); z R33 10 kΩ linia spoczynkowo ma ≈ 0,6 V, czyli poprawne L.
- **P04 (SAFE):** CORE_LINK przez R14 1 kΩ, na P04 ≥ 2,85 V. Od R4 J4.15 = SUP_N_OUT z bufora Schmitta U6 przez R41 220 Ω. Przy taśmie H_SAFE 150 mm zbocze na P04 ≤ 5,5 ns/V w oknie 0,8–2,0 V; limit 10 ns/V obowiązuje do ok. 36 pF łącznego obciążenia — `ZASILANIE-RESET.md`.

Stan na 27.09: P09-R1 (74LVC125A z Ioff, jeden MISO wybierany przez 74HC139) i P10-R1 (bufor RX 74LVC125A z Ioff) już spełniają oba wymagania. Złącza P06 J2, P08 J3, P09 J2 i P10 J2 zgadzają się pin w pin z P03 J2, J6, J7 i J8.

