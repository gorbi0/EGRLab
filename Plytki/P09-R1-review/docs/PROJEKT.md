# P09 — dwa pomiary temperatury

TC1 mierzy obudowę EGR w powtarzalnym miejscu, TC2 temperaturę drugiego punktu, np. wiązki przy zaworze lub powietrza w pobliżu. P09 pozostaje wewnątrz obudowy interfejsu, poza strefą grzania EGR. Temperatury uzupełniają logi pozycji, prądu i napięć; sama korelacja temperatury z P0404 nie dowodzi uszkodzenia EGR. Porównywać zimny start, rozgrzanie i HOT-SOAK wraz z warunkami jazdy i czasem zdarzenia.

## Zasilanie i SPI

J1 doprowadza 5V_SYS, 3V3_IO i dwa powroty z P02-R3/J9. U1/U2/U3 zawsze pracują z 3V3_IO. JP1 i JP2 wybierają VIN każdego modułu: 1–2 daje 3,3 V, 2–3 daje 5 V. Początkowo oba selektory są otwarte. Nie wolno zakładać dwóch zwór na jednym selektorze. Wybór napięcia tylko bez zasilania, po procedurze kwalifikacji. Wyjścia 3Vo są osobne, doprowadzone wyłącznie do TP8/TP9.

Na prototyp przyjmujemy rezerwę 200 mA dla obu modułów i logiki na wybranych szynach łącznie; rzeczywisty pobór trzeba zmierzyć i dodać do bilansu P02. To budżet projektowy, nie specyfikacja nieznanego regulatora modułu. Tor mocy silnika nie przechodzi przez P09.

U1 (Nexperia 74LVC125AD z Ioff) buforuje SCLK, MOSI i oba CS. U2 buforuje każdy SDO osobno przed połączeniem do wspólnego MISO. Rezystory wyjściowe 100 Ω są oddzielne. HC139 U3 dekoduje rzeczywiste CS: A=CS1, B=CS2, Y2→OE1, Y1→OE2. Nieaktywne bufory MISO pozostają w Hi-Z.

| CS1 | CS2 | MISO dopuszczone na magistralę |
|---:|---:|---|
| 0 | 1 | TC1 |
| 1 | 0 | TC2 |
| 1 | 1 | żadne |
| 0 | 0 | żadne |

Tablica dotyczy stanów ustalonych. Dekoder nie jest bezhazardowy przy jednoczesnych zboczach; firmware musi rozdzielać wybór kanałów stanem oba CS=HIGH co najmniej 1 µs. Rezystory ograniczają prąd ewentualnego krótkiego nakładania się sterowania. Brak P09 nie powinien obciążać MISO aktywnym wyjściem dzięki Ioff U2; trzeba sprawdzić stan pośredni i obie kolejności szyn na stole. Ioff nie jest izolacją galwaniczną ani dowodem zachowania podczas dowolnego brownoutu.

Start SPI: mode1, 1 MHz, CS setup/hold po 2 takty. MAX31856 dopuszcza mode1 lub3, maksymalnie 5 MHz; nie ma potrzeby przyspieszania tego toru. P03 i SD współdzielą magistralę SPI3; sprawdzić równoległy zapis SD i odczyt TC1/TC2. Właścicielem obu urządzeń TC ma być jeden task TEMP. FLT i DRDY są dostępne na TP10–TP13; kontrakt TEMP nie ma dla nich wolnych żył.

## Termopary i jakość danych

Termopary K z izolowaną spoiną pomiarową podłącza się bezpośrednio do zacisków modułów. P09 nie przenosi sygnału mikrovoltowego i nie zmienia fabrycznych listew modułów. Sprawdzić biegunowość według dokumentacji sondy i reakcji na ogrzanie, nie tylko koloru izolacji. Przedłużenie termopary wymaga odpowiedniego przewodu kompensacyjnego i właściwych złączy; zwykły przewód miedziany zmienia miejsce zimnego końca.

Unikać gwałtownych gradientów temperatury między zaciskiem termopary i układem. Trzymać nośnik z dala od P01/P07 i źródeł ciepła. Rozdzielczość 0,0078125°C nie jest dokładnością sondy ani pomiaru obudowy EGR. Docelową niepewność wyznaczyć porównaniem z termometrem odniesienia w kilku punktach i z uwzględnieniem mocowania sondy.

Dla 50 Hz pierwsza konwersja może trwać do 185 ms, kolejne do 110 ms według datasheetu. Odczyt co 200 ms jest wystarczający dla diagnostyki termicznej obudowy. Czas zapisu wyniku jest czasem odczytu, nie dokładnym czasem konwersji. Nie interpolować braków i błędów jako 0°C; zapisywać status/fault. Stała poprawna ramka nie dowodzi świeżości przetwornika; bez DRDY nie ma sprzętowego znacznika nowej konwersji.

## Montaż

PCB 100×100 mm, FR4 1,6 mm, Cu35 µm na obu warstwach; minimum ścieżka0,30 mm/prześwit0,25 mm. U1/U2 SO14 i kondensatory0805 lutować najpierw, później pojedyncze rezystory DIN0207, U3 DIP16, selektory i gniazda, na końcu wiązki. Moduły montować dopiero po sprawdzeniu nośnika. Pod nimi nie ma wysokich elementów nośnika.

Gniazda J3/J4 1×9 / 2,54 mm, pin1 VIN ma pad kwadratowy, pin2=3Vo, pin3=GND. Otwory podparcia Ø6 mm są celowo większe dla regulowanych nylonowych słupków M2.5 z podkładkami OD8 mm. Nominalny rozstaw podparcia 20,32×16 mm względem końców listwy jest założeniem do przymiarki, nie wymiarem producenta. Dopuszczalny przesuw osi M2.5 w Ø6 mm to do 1,75 mm; realny zakres ogranicza także podkładka i moduł. Dobrać wysokość słupków do gniazda, bez wyginania PCB modułu. Metalowe słupki nie są przewidziane.

Wszystkie powroty połączone z GND. Brak izolacji galwanicznej pomiaru od interfejsu. Odbiór nośnika planowany przy 0–50°C; nie jest to deklaracja przetestowanego zakresu tanich modułów.
