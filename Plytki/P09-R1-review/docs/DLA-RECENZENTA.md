# Zakres recenzji P09-R1

Najpierw sprawdzić moduł z oferty użytkownika: pinoutVIN/3Vo/GND/SCK/SDO/SDI/CS/FLT/DRDY, orientacja w nośniku, kwalifikacja regulatora i mechaniki. Projekt nie przypisuje temu modułowi schematu Adafruit. Rozstaw podparcia pozostaje warunkowy i jest opisany wprost; nie zatwierdzać produkcji bez przymiarki1:1.

Następnie zweryfikować Y2/Y1 dekoderaHC139, polaryzację OE buforów, osobne rezystory100Ω, zachowanie obuCS=0 i obuCS=1 oraz wymaganie przerwy1µs. To logika stanów ustalonych. Sprawdzić zasilanie3,3V wszystkich bramek, pull-up/pull-down, niewykorzystane wejścia i Ioff rzeczywistego Nexperia74LVC125AD.

Porównać TEMP z P03-R2/J7 i LV09 z P02-R3/J9, w tym KEY4, numerację PTH i fizyczną kolejność żył. Sprawdzić lokalne kondensatory, dostęp do złącz termopar, kotwy wiązek, obszary bez miedzi pod mocowaniami i podkładki na dużych otworach nośnika. Wszystkie poprzednie PCB pozostają bez zmian.

Firmware: niezależnie porównać rejestry0x0A–0x0F w datasheecie z diffem; sprawdzić typy ujemne, fault i brak modułu. Odróżnić czas odczytu od czasu konwersji. Pełna kompilacja ESP-IDF i pomiary sprzętu pozostają do integracji/odbioru.

Raporty automatyczne obejmują prawdziwy eksport KiCad, wszystkie147 pinów, niezależne wymagania i celowo uszkodzone warianty, świeży ERC/DRC bez wyłączeń oraz analizę połączenia wylewek. Nie dowodzą poprawności nieudokumentowanej elektroniki kupnego modułu. Niewypełniony formularz ODBIOR jest celowy.
