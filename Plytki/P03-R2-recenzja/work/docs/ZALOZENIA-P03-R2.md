# Zakres P03-R2

Płyta CORE dla EGRLab: zachowany ESP32-S3 N32R16V Waveshare, lokalne SD, MCP23017, dekoder CS i bufory Ioff. Rewizja naprawia problemy recenzji P03-R1; nie zmienia modułów pomiarowych, zaworu, P01 ani P07.

Schemat zawiera 88 pozycji na PCB, dodatkowo 5 otworów. Dwie warstwy 35 µm. Domyślne sygnały: ścieżka 0,30 mm, odstęp 0,25 mm. Zasilanie: odgałęzienia 0,60 mm/0,30 mm, główny tor J10-Q1-M1 trasowany 1 mm. Przelotki sygnałowe 0,8/0,4 mm, GND przy odsprzęganiu 1,0/0,5 mm. Nie wyłączać DRC w celu uzyskania zera.

Każda zmiana pinów istniejącej części musi znaleźć się na krótkiej liście w niezależnym `verify_function.py`. Złącza bez zmian. B2B i antena pozostają jawnie niezakwalifikowane fizycznie. Wydanie nie zawiera zatwierdzenia do produkcji ani wyników sprzętowych.
