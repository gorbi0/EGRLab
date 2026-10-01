# P09 R2 — dwa pomiary temperatury (format S1)

*R2 (29.09.2026): klasa 1/3 (53 × 100 mm), slot S3 poziomu 3. Wiązki LV09 i TEMP zastąpiło złącze J_BP do płytki połączeń P12, punkty pomiarowe TP1–TP13 zastąpiła listwa serwisowa. Poniżej zmieniono tylko opisy związane z tym; logika, moduły i uwagi o termoparach są z R1.*

TC1 mierzy obudowę EGR w powtarzalnym miejscu, TC2 temperaturę drugiego punktu, np. wiązki przy zaworze lub powietrza w pobliżu. P09 pozostaje wewnątrz obudowy interfejsu, poza strefą grzania EGR. Temperatury uzupełniają logi pozycji, prądu i napięć; sama korelacja temperatury z P0404 nie dowodzi uszkodzenia EGR. Porównywać zimny start, rozgrzanie i HOT-SOAK wraz z warunkami jazdy i czasem zdarzenia.

## Zasilanie i SPI

J_BP (J1) doprowadza 5V_SYS (dwa piny), 3V3_IO i GND na wszystkich pinach nieparzystych; zasilanie idzie z P02 R4 przez P12. U1/U2/U3 zawsze pracują z 3V3_IO. JP1 i JP2 wybierają VIN każdego modułu: 1–2 daje 3,3 V, 2–3 daje 5 V. Początkowo oba selektory są otwarte. Nie wolno zakładać dwóch zwór na jednym selektorze. Wybór napięcia tylko bez zasilania, po procedurze kwalifikacji. Wyjścia 3Vo są osobne, doprowadzone wyłącznie do kołków serwisowych (przez R24/R25).

Na prototyp przyjmujemy rezerwę 200 mA dla obu modułów i logiki na wybranych szynach łącznie; rzeczywisty pobór trzeba zmierzyć i dodać do bilansu P02. To budżet projektowy, nie specyfikacja nieznanego regulatora modułu. Tor mocy silnika nie przechodzi przez P09.

U1 (Nexperia 74LVC125AD z Ioff) buforuje SCLK, MOSI i oba CS. U2 buforuje każdy SDO osobno przed połączeniem do wspólnego MISO. Rezystory wyjściowe 100 Ω są oddzielne. HC139 U3 dekoduje rzeczywiste CS: A=CS1, B=CS2, Y2→OE1, Y1→OE2. Nieaktywne bufory MISO pozostają w Hi-Z.

| CS1 | CS2 | MISO dopuszczone na magistralę |
|---:|---:|---|
| 0 | 1 | TC1 |
| 1 | 0 | TC2 |
| 1 | 1 | żadne |
| 0 | 0 | żadne |

Tablica dotyczy stanów ustalonych. Dekoder nie jest bezhazardowy przy jednoczesnych zboczach; firmware musi rozdzielać wybór kanałów stanem oba CS=HIGH co najmniej 1 µs. Rezystory ograniczają prąd ewentualnego krótkiego nakładania się sterowania. Brak P09 nie powinien obciążać MISO aktywnym wyjściem dzięki Ioff U2; trzeba sprawdzić stan pośredni i obie kolejności szyn na stole. Ioff nie jest izolacją galwaniczną ani dowodem zachowania podczas dowolnego brownoutu.

Start SPI: mode1, 1 MHz, CS setup/hold po 2 takty. MAX31856 dopuszcza mode1 lub3, maksymalnie 5 MHz; nie ma potrzeby przyspieszania tego toru. Sygnały SPI3 wchodzą przez J_BP (piny 6, 8, 10, 12, 14). P03 i SD współdzielą magistralę SPI3; sprawdzić równoległy zapis SD i odczyt TC1/TC2. Właścicielem obu urządzeń TC ma być jeden task TEMP. FLT i DRDY modułów są w R2 nieprzyłączone (kontrakt nie ma dla nich wolnych żył, a R1 miała je tylko na polach testowych); dostępne wyłącznie na pinach modułu od góry.

## Termopary i jakość danych

Termopary K z izolowaną spoiną pomiarową podłącza się bezpośrednio do zacisków modułów. P09 nie przenosi sygnału mikrovoltowego i nie zmienia fabrycznych listew modułów. Sprawdzić biegunowość według dokumentacji sondy i reakcji na ogrzanie, nie tylko koloru izolacji. Przedłużenie termopary wymaga odpowiedniego przewodu kompensacyjnego i właściwych złączy; zwykły przewód miedziany zmienia miejsce zimnego końca.

Unikać gwałtownych gradientów temperatury między zaciskiem termopary i układem. Trzymać nośnik z dala od P01/P07 i źródeł ciepła. Rozdzielczość 0,0078125°C nie jest dokładnością sondy ani pomiaru obudowy EGR. Docelową niepewność wyznaczyć porównaniem z termometrem odniesienia w kilku punktach i z uwzględnieniem mocowania sondy.

Dla 50 Hz pierwsza konwersja może trwać do 185 ms, kolejne do 110 ms według datasheetu. Odczyt co 200 ms jest wystarczający dla diagnostyki termicznej obudowy. Czas zapisu wyniku jest czasem odczytu, nie dokładnym czasem konwersji. Nie interpolować braków i błędów jako 0°C; zapisywać status/fault. Stała poprawna ramka nie dowodzi świeżości przetwornika; bez DRDY nie ma sprzętowego znacznika nowej konwersji.

## Montaż

PCB 53 × 100 mm (klasa 1/3), FR4 1,6 mm, Cu 35 µm, dwie warstwy, JLCPCB; layout: 30.09–1.10.2026, komputer 24/7 (README, sekcja „PCB”). Dystanse M3 20 mm na czterech otworach slotu. Najpierw spód: rezystory serwisowe R20–R30 (SMD 1206 ≤ 1,5 mm; kondensatory 1206 mają do 1,8 mm, więc są na górze). Potem góra: U1/U2 SO14 i pozostałe SMD 1206, posiadane rezystory MF0207 i kondensatory 100 n na stojąco, U3 DIP16, selektory i listwy. Moduły na końcu, po kwalifikacji (`MODUL-KWALIFIKACJA.md` kroki 1–4) i sprawdzeniu nośnika bez modułów (`ODBIOR.md`).

Moduły J3/J4 lutowane wprost fabryczną listwą 1×9 / 2,54 mm (decyzja użytkownika 1.10.2026: bez gniazd i bez słupków podparcia). Pin 1 VIN ma pad kwadratowy i nadruk „1”, pin 2 = 3Vo, pin 3 = GND. Plastik listwy zostaje między modułem a płytką (ok. 2,5 mm); wyprowadzenia listwy od spodu przyciąć do ≤ 1,5 mm (S1 §4). Moduł trzyma się na 9 lutach: przewody od gniazd termopar na ścianie wejść do terminala krótkie i bez naciągu. Wymiana modułu wymaga wylutowania 9 pinów (odsysacz albo plecionka). Obrys modułu (ok. 24 × 21 mm) mieści się w slocie 53 mm; zajęcie miejsca sprawdza layout.

Wszystkie powroty połączone z GND. Brak izolacji galwanicznej pomiaru od interfejsu. Odbiór nośnika planowany przy 0–50°C; nie jest to deklaracja przetestowanego zakresu tanich modułów.
