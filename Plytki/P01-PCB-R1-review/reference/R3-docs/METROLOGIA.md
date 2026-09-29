# Stanowisko odbioru P01 R3

To instrukcja kwalifikacji stanowiska. Nie stwierdza, że posiadane sondy już
osiągają wymaganą niepewność. MS2115A służy do DC; nie do impulsu mikrosekundowego.

## Masa i VGS

DHO804 jest oscyloskopem nieizolowanym. Masy kanałów i interfejsów są wspólne.
Uziemić zgodnie z instrukcją; USB-C nie zapewnia go przez sam przewód zasilania.
**Powerbank nie dopuszcza podłączenia masy sondy do SOURCE.** Masy zwykłych sond
pozostają na GND badanego stanowiska. Nie odłączać uziemienia dla tego pomiaru.
Źródło: [Rigol DHO800 User Guide §1.1](https://download.rigol.com/en/Manual/Digital%20Oscilloscope/DHO800/DHO800_UserGuide_EN.pdf).

Są dwie dopuszczalne metody po kwalifikacji:

1. Sonda różnicowa: plus GATE, minus SOURCE, przewody przy TP2/TP1, krótka para.
   Dopuszczalne napięcie wspólne z zapasem ponad48V i zmierzone przepięcie,
   pasmo≥10MHz, zakres różnicowy obejmujący -18…+1V. Tłumienie i offset mają
   pozwolić rozstrzygnąć0,5V. Sam opis „sonda wysokonapięciowa” nie wystarcza.
2. Dwie zwykłe sondy do GATE/SOURCE, obie masy GND, odejmowanie CH_G−CH_S.
   Jednakowe tłumienie, zakres, pasmo i kompensacja; kwalifikacja niedopasowania
   DC i odpowiedzi na zbocze wspólne. To możliwość wykorzystania obecnego sprzętu,
   nie automatyczne zaliczenie wynikające z12bit. Jeżeli budżet się nie zamyka,
   potrzebna jest odpowiednia sonda różnicowa lub zewnętrzne stanowisko.

Źródło parametrów oscyloskopu: [Rigol DHO800 datasheet, Vertical System](https://www.rigol.com/dam/global/downloads/brochures/en/data-sheet/oscilloscopes/DHO800_DataSheet_EN.pdf).
Wzmocnienie jest określone jako procent pełnej skali, osobno występuje błąd offsetu.
Nie używać samego „1% mierzonego napięcia” jako pełnego oszacowania.

## Kwalifikacja przed próbą

- Rozgrzać i wykonać self-cal według instrukcji, skompensować sondy. Zmierzyć DC
  w punktach używanego zakresu, z referencją o znanej niepewności.
- Zewrzeć oba wejścia toru różnicowego przy obiekcie. Sprawdzić resztę wskazania
  przy wspólnym0/14/24/48V i przy rzeczywistym zboczu około1µs. Krótkie przewody
  i ustawienia pozostają takie same w próbie właściwej.
- Sprawdzić odpowiedź różnicową około0,5/0,8V oraz pełne VGS, bez przekroczenia
  napięcia wspólnego. Uwzględnić zmienność między powtórzeniami, offset, wzmocnienie,
  szum, kwantyzację, pasmo i opóźnienia. Zapis kalibracji dołączyć do przebiegów.
- Granica błędu/niepewności całego toru U(VGS)≤0,10V; U(czasu)≤2µs.
  U(ΔVPROT)≤0,02V dla granicy0,1V; U(Q)≤2µC dla granicy10µC.
  Przyrząd odniesienia też wnosi niepewność. Zera na ekranie nie traktować jako
  dowodu braku napięcia poniżej rozdzielczości toru.
- Dla hotplug próbkuj≥100MS/s, pasmo≥10MHz, bez wygładzania usuwającego szczyty.
  Zapisać surowe przebiegi. Opóźnienie sondy skorygować, a błąd korekty uwzględnić.

## LK1 i pomiar prądu

Normalna praca: miedziana zwora LK1. W stanie bez zasilania i po rozładowaniu
kondensatorów zdjąć zworę, wstawić przyrząd w gałąź DRAIN→VPROT. Dodatni kierunek
prądu: LK1.1→LK1.2. Pady wewnętrzne służą wyłącznie do pary sense; powrót pomiaru
nie trafia do GND. Bocznik na górnej szynie także wymaga pomiaru różnicowego.

Przewidujemy dwa zakresy, nie jeden bocznik dla wszystkich prób:

| Próba | Przykładowy dobór stanowiska | Co sprawdzić |
|---|---|---|
| OFF, mały ładunek | Skalibrowany niskoindukcyjny0,1Ω, połączenie Kelvin | Offset, szum, odpowiedź wspólna i impulsowa; niepewność całki≤2µC. |
| Start/OVP, duży prąd | Skalibrowany niskoindukcyjny około1mΩ albo sonda prądowa | Pasmo, prąd szczytowy, zakres bez nasycenia, dopuszczalna energia i wpływ na impedancję źródła. |

To specyfikacja przyrządu pomiarowego, nie dodatkowy rezystor do zakupów P01.
Rzeczywisty bocznik musi mieć znaną tolerancję, indukcyjność i zdolność impulsową.
Nie stosować zwykłego drutowego rezystora mocy do pomiaru szybkich zboczy.
Porównać VGS/VPROT z miedzianym LK1 i z bocznikiem; różnice muszą mieścić się
w zadeklarowanym błędzie próby. Jeżeli stanowisko ogranicza prąd lub zmienia
zbocze, wynik opisać jako osobny bodziec, nie jako odbiór pierwotnego warunku.

Q = całka dodatniej części zmierzonego prądu gałęzi w oknie200µs. Rachunek ma
uwzględniać pomiar offsetu przed zboczem, U(R), błąd czasu i odpowiedź toru.
Prąd na LK1 obejmuje także zjawiska pojemnościowe Q1. Modelowe I(vq1i) pokazuje
sam kanał. Nie odejmować arbitralnie pików z pomiaru, by uzyskać PASS; wpływ
displacement musi mieć osobne uzasadnienie i niepewność. Nierozdzielone zjawiska
dają NIE ROZSTRZYGNIĘTO dla kryterium przewodzenia, nie automatyczny PASS/FAIL Q1.

ΔVPROT≤0,1V jest **drugim, funkcjonalnym kryterium**. Przy220µF odpowiada22µC netto;
nie zastępuje10µC w gałęzi Q1. Nie zwiększamy dopuszczalnego ładunku w tej rewizji.
Szacowanie I=C·dV/dt+V/R stosować pomocniczo przy wolnym starcie i znanym R/C;
prąd D3/C5, ESR i inne odbiorniki muszą być wtedy uwzględnione.

## Cztery kanały i granica czasowa

Z sondą różnicową: CH1=VIN na J1, CH2=VGS, CH3=VPROT, CH4=prąd Q1.
Pomiar VS, ENABLE i SAFE_N wykonać w osobnej powtarzalnej serii, zachowując VIN
oraz VGS jako odniesienie. Z A−B: CH1=GATE, CH2=SOURCE, CH3=VIN, CH4=VPROT;
pomiar prądu wymaga osobnej serii. Jeżeli przebieg jest niepowtarzalny, nie wolno
łączyć niezgodnych serii w jeden rzekomo jednoczesny wynik; użyć innego toru.

Cały czas OVP liczony jest od **VIN na J1>18,5V**, nie od wygodnego zbocza ENABLE.
Pomiar opóźnienia ENABLE służy dodatkowo do rozdzielenia podbudżetów.

## Decyzja o wyniku

Dla limitu górnego L: PASS gdy wynik+U≤L; FAIL gdy wynik−U>L; pomiędzy tymi
granicami NIE ROZSTRZYGNIĘTO. Dla minimalnego napięcia zasada jest odwrotna.
Czas wyłączenia mierzyć do chwili, od której |VGS|+U pozostaje<0,5V; uwzględnić
U(czasu). Przykładowo0,47±0,10V nie dowodzi |VGS|<0,5V.

Przed każdym nowym ustawieniem sond, zakresu lub okablowania powtórzyć potrzebną
część kwalifikacji. Dopiero wyniki rzeczywistego stanowiska zamykają ten punkt.
