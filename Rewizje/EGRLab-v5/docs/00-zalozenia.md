# EGRLab - założenia prototypu i rozbudowy

Uzgodnienia projektowe na podstawie doprecyzowania użytkownika z 22.09.2026. Dokument uzupełnia MOD v0.1; nie jest nową kompletną rewizją elektryczną ani gotowym projektem PCB.

## Cel

Urządzenie jest prototypem badawczym do ustalenia przyczyny nawracających problemów przypisywanych EGR. Użytkownik zna pięć przypadków łącznie ze swoim autem, w których wymiana EGR nie rozwiązała problemu. Samo podobieństwo objawów nie rozstrzyga, czy przyczyna we wszystkich samochodach jest wspólna.

Zakres docelowy obejmuje LOGGER i aktywny TESTER. Logger ma powstać wcześniej jako działający zestaw, lecz wynik pierwszej diagnostyki nie usuwa z projektu testera. Możliwość zmiany metody pomiarowej, naprawy i późniejszego dodania jednego kolejnego typu EGR/marki jest wymaganiem podstawowym.

Priorytety: czytelność, uruchamianie etapowe, powtarzalność pomiarów, wymienność modułów, dostęp do sond i zapas elektryczny. Koszt pojedynczych elementów, minimalna powierzchnia PCB i liczba części mają znaczenie drugorzędne. Nie projektujemy uniwersalnego urządzenia do wszystkich samochodów.

## Decyzje dotyczące płytek

Zachowujemy dziesięć funkcji z MOD v0.1 jako osobno wymienne zespoły: PROTECT, PSU, CORE, SAFE, DAQ, I-LOGGER, DRIVE, SENSOR, TEMP, CAN. PANEL jest opcjonalny; P00 służy uruchamianiu. Nie narzucamy scalenia do siedmiu lub ośmiu PCB tylko dla zmniejszenia ich liczby.

I-LOGGER i SENSOR pozostają oddzielne. Pierwszy może dostać inny bocznik, wzmocnienie albo metodę pomiaru, drugi inne napięcie/limit lub dodatkowe kanały. Dla obecnego zaworu zachowujemy dotychczasowe ograniczenia. Zwiększenie możliwości nowej płytki nie podnosi automatycznie dopuszczalnego obciążenia badanego zaworu.

Małe płytki mogą być mocowane bezpośrednio obok siebie albo jako krótkie, demontowalne nakładki na nośniku. Wrażliwe obwody pozostają lokalne: bocznik + Kelvin + wzmacniacz; ADC + odniesienie + filtry; mostek + kondensator + TVS; MOSFET ochrony + driver bramki. Obudowa ma zapewniać miejsce na większą rewizję modułu, dostęp serwisowy, opisane punkty pomiarowe i odciążenie przewodów. Nie dokładamy procesora do każdej płytki.

## Zapas elektryczny

- Główny tor przewodów, złączy i miedzi projektujemy z rezerwą, orientacyjnie pod 10 A w rzeczywistych warunkach montażu, przy pozostawieniu ograniczenia całego obecnego urządzenia do 5 A oraz dotychczasowych niższych limitów pracy EGR. Weryfikacja dotyczy kompletu: styku, przewodu, zacisku, temperatury i miedzi.
- Nie zmniejszamy teraz radiatorów na podstawie przypuszczenia, że TEST będzie tylko krótkimi impulsami. Zachowujemy projekt chłodzenia dla obciążenia ciągłego przyjętego dla PWR-THT, do potwierdzenia pomiarem.
- Kondensatory, rezystory mocy i półprzewodniki dostają zapas napięcia, mocy i temperatury właściwy dla ich miejsca w układzie. Nie wybieramy MOSFET-a wyłącznie według największej liczby amperów: sterowanie bramki, rezystancja i zachowanie podczas załączania nadal muszą pasować.
- Zakres pomiarowy dobieramy do rozdzielczości potrzebnej w diagnostyce. Zapas obciążalności elementów nie oznacza dowolnego zmniejszania rezystancji wejścia podłączonego do ECU ani zastąpienia pomiaru małych prądów zakresem setek amperów.
- Bezpiecznik, odcięcie nieprawidłowego zasilania, STOP, lokalne OC i fizyczny rozdział TEST/ECU zostają. Zmniejszamy rozbudowę pomocniczej diagnostyki tam, gdzie nie daje konkretnej korzyści pomiarowej lub serwisowej.

## Analog lokalnie, dane między modułami

Kierunek docelowy: sygnał z bocznika i wzmocnienie pozostają na module pomiarowym, a ADC znajduje się przy nich. Do CORE wychodzą dane cyfrowe. P05 już realizuje tę zasadę dla odczepów napięciowych; P09 dla temperatur.

Dla przyszłej wersji I-LOGGER i pomiaru prądu TEST przewidujemy lokalny ADC z możliwością zsynchronizowania próbkowania z napięciami EGR. Preferowany punkt wyjścia dla szybkich torów to ADC SAR ze sterowaniem chwili konwersji i SPI. Jego model, zakres wejścia, odniesienie, linie CS oraz dostępne wyprowadzenia CORE wymagają doboru w schemacie. Nie deklarujemy, że dowolny lokalny ADC jest zgodny z AD7606B ani że sama wspólna linia START gwarantuje identyczną chwilę pomiaru.

Ważne są częstotliwość próbkowania, opóźnienia filtrów i przypisanie czasu konwersji. Odczyt kilku układów jeden po drugim nie musi oznaczać próbkowania w tych samych chwilach. Log zawiera informację o synchronizacji i opóźnieniu, a nie sztucznie wspólny czas odbioru.

Na etapie przejściowym można pozostawić wyjście analogowe INA do AD7606B oraz punkt pomiarowy do oscyloskopu. Jeśli jest używany kabel analogowy, ma być krótki i mieć poprawne odniesienie; dla dłuższego połączenia należy zaprojektować transmisję różnicową albo lokalną konwersję. Opcja analogowa pozwala porównać wyniki i uruchomić podstawę bez czekania na nowy przetwornik. Wyjścia pomiarowe nie sterują lokalnym OC: szybka blokada DRIVE działa niezależnie od transmisji i procesora.

I2C wykorzystujemy do konfiguracji, identyfikacji i wolnych pomiarów pomocniczych. Przykładowy ADS1115 ma do 860 konwersji/s i multiplekser wejściowy, więc nie zastępuje bez zmiany możliwości zsynchronizowanego toru prądu i napięcia 2 kS/s. Ograniczenie dotyczy tego przetwornika, nie teoretycznego zakazu szybkich ADC z I2C. Dane producenta: https://www.ti.com/lit/ds/symlink/ads1115.pdf

P05 zachowuje AD7606B jako bazę równoczesnego próbkowania ośmiu napięć: https://www.analog.com/media/en/technical-documentation/data-sheets/AD7606B.pdf . Dodatkowe szybkie pomiary powinny móc tworzyć osobny strumień, aby nie ograniczać całego loggera do najwolniejszego modułu. Cyfrowe połączenie nie zastępuje ochrony wejścia ani prawidłowego odniesienia masy; izolację dodajemy tam, gdzie ma uzasadnienie w pomiarze.

## Granice wymienności

Każdy moduł ma typ, rewizję sprzętu, numer egzemplarza oraz wersję interfejsu. Na początku wystarczą trwałe oznaczenia i jawny wpis w konfiguracji; nie jest konieczna automatyczna identyfikacja EEPROM każdej PCB. Rozbudowa może później dodać pamięć identyfikacji.

Stałe mają być funkcje złączy, poziomy napięć, kierunki sygnałów, dopuszczalne obciążenie, stan bez zasilania i mechanika mocowania. Nieprzydzielone styki oznaczamy NC/rezerwa; przyszła niezgodna funkcja wymaga nowej wersji interfejsu i odpowiedniego kodowania. Ten sam korpus złącza nie oznacza zgodności elektrycznej.

Złącza napędu, adapterów EGR i zasilania nie są dowolnym wspólnym portem. Zachowujemy oddzielenie LOGGER od aktywnego TEST. Wymieniamy moduły po odłączeniu zasilania; hot-plug nie jest celem prototypu.

## Firmware i dane - konieczne zmiany przed nową rewizją

Obecny firmware v4.1 ma stałe przypisanie kanałów i przelicznik prądu 0,25 V/A wpisany w control.c, trigger.c i jsonlog.c. Rekord próbek ma osiem pól 16-bitowych. To działa dla obecnej konfiguracji, ale nie zapewnia jeszcze dowolnej wymiany modułów.

Rozdzielamy trzy rodzaje informacji:

1. **Sprzęt i kalibracja:** moduł/egzemplarz, bocznik, wzmocnienie, ADC, zakres, zero, opóźnienie, konfiguracja oraz data odbioru. Kalibracja pełnego toru uwzględnia także adapter i jego rezystory.
2. **Zawór i adapter:** rodzaj napędu, mapa pinów i funkcji, charakterystyka feedbacku, częstotliwość PWM, limity prądu/temperatury/ruchu, metoda IDENTIFY i LEARN. Profil nie może nakazać sprzętowi przekroczenia jego możliwości.
3. **Samochód i sesja:** identyfikator auta, zamontowany egzemplarz EGR, stan przed/po naprawie, warunki próby, konfiguracja ECU jeśli znana i źródło danych CAN/OBD. Nie przenosimy automatycznie progów diagnostycznych ani map CAN między samochodami.

Sterowniki sprzętu udostępniają opis kanałów i możliwości. Algorytmy używają funkcji takich jak napięcie motoru, feedback, masa odniesienia i prąd, zamiast rozproszonych w kodzie stałych numerów kanałów. Limity wykonawcze wynikają z przecięcia możliwości sprzętu i zatwierdzonego profilu zaworu. Dane raw, nieważność pomiaru, nasycenie i utrata próbek pozostają jawne.

Wymiana modułu prądu nie może zachować starego przelicznika lub statusu kwalifikacji. Wymiana adaptera wymaga sprawdzenia mapy i właściwej kalibracji toru, a zmiana zaworu właściwego LEARN. Kalibrację sprawdzonego modułu temperatury można zachować przy zmianie innego, niezależnego modułu.

Format logów dostaje opis strumieni: kanały, jednostki, rozdzielczość raw, częstotliwość, źródło czasu, synchronizacja, moduły i kalibracje. Dotychczasowe config_id jest przydatną podstawą. Rozszerzenia zmieniające układ binarny wymagają nowej wersji formatu; starych plików nie interpretujemy nowym układem pól. Do czasu implementacji zachowujemy działający format v4 dla podstawowych ośmiu kanałów i nie deklarujemy obsługi nowych strumieni.

**Korekta MOD v0.1:** LOGGER_CURRENT_OK nie może trafiać na GPB7 MCP23017. Przewidzieć wolne GPA4 z pull-downem i poprawną obsługą portu. GPA7/GPB7 pozostają wyjściami zgodnie z dokumentacją Microchip: https://ww1.microchip.com/downloads/aemDocuments/documents/APID/ProductDocuments/DataSheets/MCP23017-Data-Sheet-DS20001952.pdf .

## Rozszerzenie na kolejne auto

Dla drugiego zaworu 12 V o zgodnym rodzaju napędu i analogowym feedbacku możliwe jest zachowanie większości elektroniki: nowy adapter, profil i odbiór zakresów/prądu. Nie wystarczy sama zgodność liczby styków. Pasywna identyfikacja trzech przewodów z v4.1 jest przeznaczona dla obecnej klasy czujnika, a nie dowolnej magistrali cyfrowej.

Jeżeli kolejny zawór wymaga innego rodzaju napędu, zasilania czujnika albo komunikacji, wymieniamy odpowiednio DRIVE, SENSOR lub moduł komunikacyjny i dodajemy jego sterownik oraz procedurę. CORE, zapis, interfejs użytkownika i część pomiarów mogą pozostać. Nie gwarantujemy samej zmiany adaptera dla nieznanego zaworu. Drugi model wybieramy przed doborem jego części, a nie projektujemy teraz wszystkich hipotetycznych wariantów.

Wewnętrzna komunikacja nowych modułów, gdy będzie potrzebna, nie może zostać omyłkowo dołączona do CAN auta. Nowe protokoły wymagają osobnego, świadomie dobranego interfejsu.

## Sposób rozwijania prototypu

Pierwsza działająca wersja zbiera napięcia i temperatury, potem prąd oraz kontekst CAN. Aktywny tester jest rozwijany równolegle projektowo i uruchamiany po odebraniu jego blokad. Zachowujemy identyczną metodę pomiaru dla porównywanych samochodów; zapisujemy numer auta i zaworu, warunki oraz zmianę konfiguracji.

Zadaniem pomiarów jest rozróżnienie zachowania samego zaworu, zasilania, masy, połączeń i sterowania. Dobry test stołowy nie odtwarza automatycznie obciążenia spalinami i warunków całego silnika. Jednocześnie prawidłowy log elektryczny nie dowodzi sprawności mechanicznej. Wyniki wskazują, jaki następny pomiar lub moduł jest potrzebny.

Przed wykonaniem kolejnej rewizji: zamknąć wersjonowane interfejsy, przydział GPIO/CS, kalibrację i identyfikatory; uprościć wiązki przez lokalne przetwarzanie oraz sąsiedztwo płytek; pozostawić kilka uzasadnionych blokad sprzętowych i proste procedury odbioru. Nie dodawać rozbudowanej infrastruktury tylko na wypadek nieokreślonych przyszłych zastosowań.
