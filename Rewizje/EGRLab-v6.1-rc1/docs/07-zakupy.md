# Zakupy i wykonanie V6

Główny wykaz `hardware/zakupy.csv` ma nazwę, ilość i jednostkę. Zawiera elementy, adaptery, części wiązek oraz materiały nośników. `BOM.csv` i osobne Pxx-BOM.csv zawierają wiązki jako komplet z długością i typem wtyku. **Nie dodawać BOM-u do zakupów ani ponownie sumować części wiązek**. Fabryczne moduły i opisane komplety złączy są zestawami: upewnić się, że dostawa zawiera wymienione styki, blokady i odciążki. Nie doliczono zapasu na naukę lutowania/zaciskania.

Kup AD7606BBSTZ bezpośrednio do P05, bez breakouta. TLV1702AQDGKRQ1 ma VSSOP8, nie SOIC. Nie kupuj LM74800EVM-CD. P01-PROTECT jest już policzony. Wykaz adapterów wynika z metody montażu; na P05/P07 nie stosować przejściówek pod układami zaprojektowanymi do bezpośredniego lutowania.

Kolejność: P01/P02/P00 → CORE i DAQ z parą B2B, TEMP i adapter L2 → I-LOGGER/L1/CAN → SAFE/DRIVE/SENSOR/TEST. Każdy etap ma własne próby w ODBIOR.csv. Przyrządy i materiały ogólne są w narzedzia.csv; pozycje „jeśli brak” nie są nakazem kupowania drugiego miernika lub zaciskarki.

P01/P05/P07 wymagają jeszcze layoutu PCB 2L. W pozostałych używać uniwersalnych PTH z rastrem 2,54 mm. Wymiary rezerwowe kart modułów można zwiększyć; nie zmniejszać odstępów i kotew dla oszczędności powierzchni. Mini-Fit mocować jako opisany w instrukcji korpus z ogonkami, ponieważ jego raster 4,2 mm nie odpowiada uniwersalnej 2,54 mm. Gotowe VNH5019/MAX31856 zachowują fabryczny sposób podłączenia.

Przed zamówieniem złączy sprawdzić rysunek konkretnej serii, klucz, liczby pozycji, pokrycia obu partnerów i obciążalność dla użytego przewodu. Katalog nie dowodzi dostępności w sklepie. Dopuszczalne zamienniki rezystorów opisano w docs/09; ich nominał, TCR i dopuszczalne napięcie są wymaganiami, a nie sam napis „większy rezystor”.
