# P00-R3 — warunki pracy i połączenia

*Nazwa pliku pochodzi z R2; treść dotyczy R3. Zmiany R3: bilans cieplny policzony z netlisty, poziom H heartbeat, TP3 jako punkt za diodą, plan B dla temperatury.*

Przyrząd stołowy pracuje w temperaturze otoczenia **10–40 °C**. Zasila go zasilacz laboratoryjny 6–15 V z ograniczeniem prądu; zalecane 9–12 V. Przy 6 V na J10 i przyjętym budżecie spadku D1 0,6 V na U2 zostaje 5,4 V. TP3 (napis „ZA D1”) leży za D1 i służy tylko do pomiaru — nie podłączać tam zasilania. TP1 = 3V3 P00, TP2 = GND.

U2: LM2937ET-3.3/NOPB, TO-220; 1 IN, 2 GND/tab, 3 OUT. D1 chroni też elektrolit wejściowy. Na wejściu C4 10 µF / 50 V i C5 100 nF. C7 100 nF leży bezpośrednio między 3V3 i GND. Plus C6 idzie na 3V3, minus przez R6 do GND. R5 łączy bezpośrednio 3V3 z GND.

## Warunki aplikacji U2

VIN na pinie U2 co najmniej 4,75 V. Parametry wyjścia są określone od 5 mA. COUT co najmniej 10 µF; rezystancja szeregowa gałęzi kondensatora wyjściowego 0,01–3 Ω. Źródło: TI SNVS015F, strony 4–5 i 11–12 (cytat z R2; lokalnie niezweryfikowany, bo kopia u dystrybutora nie odpowiada).

R5 560 Ω daje minimum 5,54 mA przy 3,14 V, tolerancji 1 % i TCR 100 ppm/K. Bez U1 i przy wszystkich kanałach w L razem z LED10 płynie co najmniej 6,57 mA. Moc R5 wynosi najwyżej 21,7 mW. R6 1 Ω nie przewodzi prądu odbiorników, tylko dodaje rezystancję w gałęzi C6; jego tolerancja nie ma znaczenia. C6 ma nominalnie 22 µF, po tolerancji −20 % zostaje 17,6 µF. Panasonic podaje dla EEUFR1H220 impedancję do 0,340 Ω przy 100 kHz i 20 °C. Z R6 daje to 0,99–1,35 Ω. To obliczenie w warunkach katalogowych, nie dowód stabilności pętli. Stabilność sprawdza się oscyloskopem w odbiorze. Nie zastępować R6 zworką ani C6 kondensatorem polimerowym bez ponownej oceny.

## Sygnały

SW1–SW9: środkowy pin 1 = COM, pin 2 = 3V3, pin 3 = GND. Würth 450301014042 łączy COM ze stykiem po przeciwnej stronie suwaka, więc suwak w górę daje H. COM idzie przez RSn 1 kΩ na Jn.1; Jn.2 = GND. Zielona LED stoi przed RSn i pokazuje stan źródła, nie odbiornika.

Kanał w H przy odbiorniku z pulldownem 10 kΩ daje co najmniej 2,85 V. Tak jest na wejściach 74LVC125A w P04 (VIH 2,0 V przy VCC 2,7–3,6 V, Nexperia Rev. 12, tab. 6). Przez dodatkowe R41/R42 1 kΩ w P04 (KEY, MECH) co najmniej 2,61 V trafia na bramki HC08, których próg wynosi ok. 2,36 V. Prąd zwarcia kanału do GND: nominalnie 3,3 mA, najwyżej ok. 3,5 mA. To ograniczenie dla logiki 3,3 V, nie ochrona przed obcym napięciem. Mapa do P04: `P00-P04-WIAZKA.md`.

U1 TLC555CP: RA 4,7 kΩ, RB 68 kΩ, C1 100 nF. Nominalnie 102,3 Hz, wypełnienie H ok. 51,7 %. Z tolerancji R i C wychodzi ok. 92–115 Hz. SW9 STOP trzyma RESET w L, więc na wyjściu jest stałe L; RUN włącza przebieg. J9: 1 = heartbeat przez R3 1 kΩ, 2 = GND.

**Poziom H heartbeat.** LED9 z RL9 1 kΩ (ok. 1 mA) obciąża wyjście U1 przed R3. Wyjście TLC555 wg TI SLFS043K: VOH min 4,1 V / typ 4,8 V przy 5 V i −1 mA; min 1,5 V / typ 1,9 V przy 2 V i −0,3 mA. Na wejściu P04 (R13 10 kΩ) daje to typowo 2,45–2,82 V. W narożniku minimalnego VOH wychodzi 1,87–2,25 V wobec VIH 2,0 V. Dlatego odbiór P00 wymaga H ≥ 2,4 V na J9 z 10 kΩ do GND, zanim wiązka trafi do P04. Przy niższym wyniku: RL9 4,7 kΩ (LED9 wyraźnie słabsza) albo inny egzemplarz TLC555. Kontrola `verify_electrical.py` pilnuje wariantu typowego i zapisuje narożnik.

## Bilans cieplny

Z netlisty wynika najwyższy możliwy pobór 57,1 mA. Składają się na niego: R5, wszystkie LED, wszystkie J1–J8 zwarte do GND, J9 zwarty, U1 i R4. Typowy pobór przy P04 (kanały H na 10 kΩ, HB pracuje) to ok. 22 mA. Budżet 65 mA pokrywa to maksimum; pilnuje tego kontrola.

Przy IG 20 mA (górne założenie) i RθJA 77,9 K/W w 40 °C wychodzi:

| J10 | TJ przy maksimum 57 mA | TJ przy typowym 22 mA |
|---|---|---|
| 12 V | ok. 98 °C | ok. 74 °C |
| 15 V | ok. 116 °C | ok. 84 °C |

Radiator nie jest potrzebny. **Plan B przy przekroczeniu kryterium odbioru: ograniczyć zasilanie do 12 V** i zapisać to na egzemplarzu. Radiator nasuwany na tab wymagałby przymiarki, bo tab U2 jest zwrócony do C5/C7, ok. 1,5 mm od ich obrysu. Kryterium obudowy < 85 °C w próbie zwarć przy 15 V zależy od rzeczywistego IG. Przy 20 mA obudowa ma ok. 96 °C przy 23 °C w pomieszczeniu, a przy 3 mA ok. 77 °C. Wynik tej próby decyduje, czy egzemplarz pracuje do 15 V, czy do 12 V. TP1 nie służy do zasilania badanej płytki.

Sprzęt, tętnienia i temperatura: NIE ZBADANO. Obliczenia odczytuje `src/verify_electrical.py` z eksportowanej netlisty.
