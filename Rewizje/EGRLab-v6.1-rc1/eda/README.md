# KiCad 10.0.6 — migracja do przeglądu

Każdy moduł ma osobny projekt, np. P01/P01.kicad_pro. 588 elementów przeniesiono do 16 projektów (11 modułów, P00, trzy adaptery i EXT). Sieci łączą elementy wewnątrz jednej płytki; przejścia między płytkami nadal określa wiring.csv i sprawdza osobny graf. Nie otwierać wszystkich arkuszy jako jednego schematu z globalnymi nazwami zasilania.

To **edytowalny import pinowy**, a nie zatwierdzony schemat wykonawczy ani layout. Elementy pokazano jako bloki z typowanymi pinami. Przed layoutem trzeba ułożyć obwody funkcjonalnie, sprawdzić modele symboli, uzupełnić footprinty i wymiary kupowanych podzespołów. Samo zero błędów ERC nie zamyka tych czynności.

RefDes EDA są numeryczne. Pole SourceRef i migration-map.json wiążą je z oryginalnymi oznaczeniami BOM; nie wolno ignorować tej mapy przy montażu. Pola A/K mają odwzorowanie do numerowanych padów, z zachowaniem biegunowości. Nazwane piny modułów kupnych nadal wymagają przypisania do fizycznych padów ich nośników.

Biblioteka libraries/EGRLab.kicad_sym jest lokalna. Typy pinów używają przypiętych ról bibliotek KiCad lub jawnych map producentów; pin-role-coverage.json pokazuje zakres. Pasywne bloki modułów kupnych nie dowodzą sprawdzenia ich wnętrza. power-source-declarations.json wymienia każde PWR_FLAG i rzeczywistą drogę zasilania. Nie dodawano flag do dowolnych zgłaszanych sieci.

Wybrane footprinty P01 są **kandydatami**, nie zatwierdzonym doborem kompletu części. Brakujące pola pozostają jawnie puste. Kopie pochodzą z bibliotek KiCad 10.0.6: https://gitlab.com/kicad/libraries/kicad-footprints ; licencja CC BY-SA 4.0 z KiCad Libraries Exception: https://www.kicad.org/libraries/license/ . Import zachowuje opisy źródłowe bibliotek.

W każdym katalogu: kicad_sch/kicad_pro, eksport XML, niesfiltrowany erc.json, podgląd SVG. Raport porównania: ../stabilizacja/evidence/eda-report.json. Osiem ostrzeżeń pozostawiono widoczne: GND ekranów AL1/AL2, niewykorzystane 5V standardowego LV na P04/P09, cztery zewnętrzne końce termopar P09. Nie są wyłączone globalną regułą.

Generator kicad_import.py odmawia nadpisania istniejących schematów. Po ręcznej edycji użyj verify_eda.py --cli <kicad-cli>, sprawdź różnice i dopiero zatwierdź migrację jako źródło schematów. Do tego momentu import jest dokumentem porównywanym z zamrożonym modelem; nie ma dwóch równocześnie nadrzędnych źródeł.
