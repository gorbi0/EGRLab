# Wiązki P09

W1/LV09: 200 mm, cztery przewodyAWG22. P09/J1:1=5V_SYS,2=GND,3=3V3_IO,4=GND. Drugi koniec Mini-Fit Jr4p Au do P02-R3/J9, połączenie1:1. Na P09 pola PTH w jednym rzędzie od lewej1–4 w widoku montażowym. Nie mylić LV z zasilaniem modułu: moduł wybiera szynę poprzez JP1/JP2.

W2/TEMP: 100 mm, taśma10×AWG28 o rastrze żył1,27 mm, IDC2×5 o rastrze styków2,54 mm, stykiAu i odciążka. P09/J2→P03-R2/J7, połączenie1:1. Górny rząd PTH1,3,5,7,9 od lewej; dolny2,4,6,8,10. 1=SCLK,2=GND,3=MOSI,4=NC/KEY,5=MISO,6=GND,7=TC1_CS,8=GND,9=TC2_CS,10=GND. Wtyk KEY4 ma fizycznie zaślepioną pozycję4 pasującą do usuniętego pinu nagłówka P03; wolny przewód4 na P09 zaizolować. Oznaczona żyła taśmy to1.

Obie wiązki lutowane tylko po stronie P09 do otworów metalizowanych, nie do SMD. Kotwy opaski są12 mm przed pierwszym rzędem lutów (14,54 mm przed drugim rzędem TEMP). Nie zaciskać opaski do przecięcia izolacji. Pozostawić mały łuk między kotwą i lutem; cyna nie powinna usztywniać przewodu aż do miejsca zginania. Opaskę przeprowadzić przez oba otwory kotwy, omijając elementy.

Przed podłączeniem sprawdzić ciągłość wszystkich żył i brak zwarć, numerację po obu stronach, plus i3,3 V oddzielnie. Oznaczyć W1/W2 i stronęCORE. Nie wnioskować numeracji IDC z widoku od strony kabla — sprawdzić styki miernikiem. Przymierzyć zatrzask Mini-Fit do rzeczywistego P02.

MAX31856 pozostają w gniazdach J3/J4 ze swoimi listwami. Nie lutujemy kupionych modułów na stałe do nośnika. Połączenie CORE–DAQ pozostaje poza P09 i bez zmian.
