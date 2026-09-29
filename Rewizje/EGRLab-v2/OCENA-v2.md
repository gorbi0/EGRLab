**Ocena EGRLab v2 — przegląd z 21.09.2026**

**Wniosek: v2 jest lepiej ukierunkowana diagnostycznie, ale nie jest gotową dokumentacją wykonawczą.** Warto rozwijać jej koncepcję. Obecne połączenia sprzętowe i firmware wymagają korekt przed montażem oraz podłączeniem TEST. Powrót do całej v1 nie jest rozwiązaniem: część krytyki v1 jest słuszna, a niektóre ograniczenia zapisu zostały odziedziczone.

Przegląd obejmuje dokumentację v2, listę połączeń, BOM, pinout, kod C, narzędzie Python, testy i porównanie z v1. Sprawdziłem dokumentację producentów dla kluczowych elementów. Nie kompilowałem ESP-IDF ani testów C: w dostępnym środowisku nie znalazłem toolchainu. Nie wykonywałem pomiarów sprzętowych, ERC ani DRC. Oryginalnego katalogu v2 nie zmieniałem.

**Ocena proponowanych zmian**

| Zmiana | Ocena i decyzja |
|---|---|
| IDENTIFY wszystkich sześciu permutacji 4/5/6 | Zachować. Usuwa niepotwierdzone założenie v1 o pinie 4. Jednoznaczność i bierny pomiar z ECU są właściwym kierunkiem. |
| L2 back-probe przed L1 inline | Zachować jako pierwszy etap. Rozpięcie złącza może zmienić zachowanie podejrzanego styku. Sondowanie także wymaga ostrożności. |
| Wspólny kanał prądu i AUX | Zachować funkcję. AUX zwiększa wartość porównania z ECV lub spadkiem masy. Wykonanie przekaźników wymaga poprawki F03. |
| AD7606B, zakresy per kanał | Przydatne, ale dopiero po naprawie sterownika i metadanych. Więcej działek ADC samo nie gwarantuje lepszej dokładności. |
| HOT-SOAK | Duża wartość dla zależności termicznej. Wymaga kwalifikacji temperatury, powtarzalnego wymuszenia i ostrożniejszej interpretacji wyniku. |
| SUBSTITUTE LOAD / HARNESS-ONLY | Testy pomocnicze. Nie pozwalają automatycznie uznać całej wiązki lub ECU za sprawne. |
| Kalibracja per bank, mierzone zero prądu | Słuszna poprawka v1. Musi obejmować także zapis i analizę plików; obecnie obejmuje je niekompletnie. |
| Sprzętowy wire-AND | Zasadny sposób uproszczenia, lecz obecny obwód jest błędny. Nie wystarczy opis funkcjonalny. |
| Usunięcie OVP i nadzoru 5V_A | Nie akceptuję jako gotowego wariantu do auta. Należy skoordynować ochronę i zachować niezależną kontrolę ważnych szyn. |
| Zapis ciągły zamiast osobnego zrzutu pretrigger | Rozsądne uproszczenie. Historia przed zdarzeniem już jest w pliku. Zmniejszenie bufora PSRAM to osobna decyzja, nie warunek tego uproszczenia. |
| 2 kS/s jako punkt startowy | Rozsądne dla trendów. Nie dowodzi wykrywania krótkich zakłóceń ani poprawnego pomiaru RMS prądu PWM. |
| Triggery i SCOPE_TRIG | Zachować, po korekcie kryteriów i konfiguracji DHO804. |
| SoftAP | Opcja na koniec; obecna integracja nie działa zgodnie z opisem. |
| Posiadany ESP32-S3 | Nie znalazłem powodu do wymiany MCU wynikającego ze zmian v2. Problemy są w torach, połączeniach i oprogramowaniu. |

P1 poniżej oznacza błąd blokujący bezpieczne uruchomienie albo wiarygodny pomiar. P2 oznacza problem funkcjonalny lub ograniczenie, które trzeba naprawić przed użyciem danej funkcji.

**F01 — P1: obwód STOP / SAFE_N jest wewnętrznie sprzeczny**

[connections.csv](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/EGRLab-v2/hardware/connections.csv:78) łączy wyjścia open-collector komparatorów i open-drain supervisora z SAFE_N, po czym do tego samego węzła dołącza wyjście U9.Y1, czyli push-pull 74HC08. Przy wysokim wyjściu bramki i aktywnym błędzie powstaje konflikt wyjść. Samo wstawienie AND przed tym węzłem nie zmienia push-pull w open-drain.

[Opis komparatora](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/EGRLab-v2/docs/01-projekt.md:197) dodaje pull-up 10 kΩ do 3,3 V bez STOP. Jeśli zrealizować go dosłownie obok pull-upu przez STOP, otwarcie grzybka zostawia około 3,0 V na dzielniku 10 kΩ / 100 kΩ. To przeczy deklaracji, że przerwany przewód STOP wymusi stan niski.

Dodatkowo CSV podaje HW_ARMED i MCU_ARM na bramkę nr 2, a INTERLOCK na B3; brakuje połączenia, które włączyłoby trzeci warunek do MOTOR_PERMIT. Równania trzech i czterech wejść nie mieszczą się po prostu w jednej bramce dwuwejściowej każde.

**Poprawka:** narysować kompletny schemat z numerami nóżek. Oddzielić węzeł wyjść otwartych od końcowego wyjścia AND albo zastosować właściwe wyjście otwarte dla watchdog. Zachować tylko zamierzony pull-up przez STOP. Rozpisać wszystkie bramki i odcięcie czujnika, następnie sprawdzić tabelę stanów dla każdego błędu i przerwania przewodu.

**F02 — P1: P-MOS ochrony odwrotnej polaryzacji jest odwrócony; TVS nie zapewnia koordynacji z TSR**

[Wejście zasilania](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/EGRLab-v2/hardware/connections.csv:3) podaje BAT+ na source, a obciążenie na drain. Dla pojedynczego P-MOS w tej funkcji należy odwrócić te połączenia: drain od akumulatora, source od chronionej strony. Obecne połączenie pozostawia drogę przez diodę strukturalną przy odwróconej baterii. Rozróżnienie ochrony odwrotnej polaryzacji i zwykłego przełącznika opisuje [TI](https://e2e.ti.com/support/power-management-group/power-management/f/power-management-forum/944817/mc33063a-q1-reverse-polarity-protection-using-p-mosfet).

SM8S24CA nie ogranicza do 24 V: przykładowa karta producenta podaje **38,9 V przy znamionowym prądzie impulsu**, a TSR ma zakres wejściowy do **36 V**. Nie oznacza to uszkodzenia przy każdym impulsie, lecz brak wykazanej ochrony w wymaganych warunkach. Firmware nie chroni przetwornicy przed szybkim przepięciem. [SMC, tabela parametrów](https://www.smc-diodes.com/propdf/SM8S20CA%20THRU%20SM8S43CA%20N2149%20REV.-.pdf), [Traco TSR 2](https://www.tracopower.com/products/tsr2.pdf).

**Poprawka:** właściwa orientacja MOSFET-a, konkretny numer części i obwód bramki; dla auta OVP albo cały tor zaprojektowany na napięcie ograniczania TVS z zapasem. Przywrócenie sprawdzonego modułu OVP z v1 jest rozsądną drogą. Nadzór 5V_A powinien również być niezależny od pomiarów ADC zasilanego z tej szyny.

**F03 — P1: jedna cewka KMEAS3 dostała dwie niezależne funkcje**

[Styki i wybór prądu](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/EGRLab-v2/hardware/connections.csv:60) wykorzystują jeden biegun KMEAS3 do dołączania pinu 6, drugi do wyboru TEST/LOGGER. [Sterowanie cewkami](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/EGRLab-v2/hardware/connections.csv:101) wymaga osobno MEAS_EN i MEAS_BANK dla tego samego przekaźnika.

G6K-2F-Y jest DPDT ze wspólnym napędem obu zestyków; nie ma dodatkowej niezależnej cewki „coil_bank”. W LOGGER odczep pinu 6 wymaga NO, a prąd LOGGER wymaga NC drugiego bieguna. Tych stanów nie można uzyskać jednocześnie. [Omron G6K](https://components.omron.com/sites/default/files/datasheet_pdf/K106-E1.pdf).

**Poprawka:** osobny przekaźnik lub odpowiedni multiplekser dla prądu. Wspólny bank odczepów pozostawić, ale nie próbować oszczędzić tego jednego niezależnego przełącznika.

**F04 — P1: obsługa AD7606B i „automatyczny fallback” są niepoprawne**

[board.c](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/EGRLab-v2/firmware/main/board.c:109) wysyła odczyt jako 0x8000. W interfejsie szeregowym początek komendy odczytu to 01: flaga 0x4000 i sześciobitowy adres. Kod myli format szeregowy z równoległym. Brakuje powrotu z register mode zapisem do adresu 0x00 oraz konfiguracji DOUT_FORMAT do deklarowanego odczytu jednym wyjściem. Reset CONFIG ustawia dwa DOUT. [AD7606B, interfejs i CONFIG](https://www.analog.com/media/en/technical-documentation/data-sheets/AD7606B.pdf).

Software mode wymaga OS[2:0]=111; same zapisy SPI go nie włączają. Zworki opisano dla x1/x8, a kod nie przełącza pinów OS. Zmiana zmiennej software_mode nie przełącza sprzętu w hardware mode. [Analog Devices AN-2011](https://www.analog.com/en/resources/app-notes/an-2011.html).

Po nieudanej konfiguracji zakresy w profilu nadal służą do przeliczeń. Przy sprzętowym ±10 V i programowym ±5 V rzeczywiste 2,5 V daje 1,25 V, czyli **−5 A zamiast 0 A**. Błędy konfiguracji są ignorowane na starcie.

**Poprawka:** jawny, sprawdzony tryb sprzętu; poprawny protokół; rzeczywiście zastosowane zakresy oddzielone od żądanych; błąd konfiguracji blokuje TEST. Najpierw test ośmioma różnymi napięciami. Kodów zakresów 0/1/2 i adresów 0x03–0x08 nie uznaję za błędne.

**F05 — P1: zmiana kierunku może odblokować PWM mimo błędu I²C**

[board_drive](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/EGRLab-v2/firmware/main/board.c:83) ustawia current_sign przed potwierdzeniem zapisu MCP23017. Timeout mutexu lub błąd I²C nie blokują późniejszego ARM/PWM. Napęd może dostać poprzedni kierunek.

Ponadto [board_mode](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/EGRLab-v2/firmware/main/board.c:243) zeruje INA/INB, ale nie resetuje current_sign. Po przejściu STOP → TEST żądanie tego samego znaku może pominąć ustawienie kierunku i pozostawić oba wejścia niskie.

**Poprawka:** aktualizować stan kierunku dopiero po udanym zapisie, resetować go przy wyzerowaniu portu, a niepowodzenie kończyć zatrzaśniętym FAULT. Odmierzanie przerwy oprzeć na potwierdzonym stanie wyjść.

**F06 — P1: kalibracja per bank nie dociera poprawnie do analizy plików**

[storage_init](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/EGRLab-v2/firmware/main/storage.c:69) zapisuje zakresy i kalibrację tylko przy starcie, dla banku 0. Później IDENTIFY zmienia zakresy, TEST wybiera drugi bank, AUX zmienia zakres i gain, a ZERO oraz LEARN zmieniają profil.

Zdarzenie [profile](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/EGRLab-v2/firmware/main/app_main.c:152) nie zawiera nowych zakresów i kompletu kalibracji. [Eksporter](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/EGRLab-v2/tools/egrlog.py:213) aktualizuje tylko mapowanie i krańce pozycji. Flaga SAMPLE_TEST nie wybiera w nim właściwego banku.

Odtworzone na oryginalnym czytniku:
- po przejściu kanału masy z ±10 V na ±2,5 V rzeczywiste **20 mV eksportuje się jako 79,956 mV**;
- przy zerze TEST=2,6 V i LOGGER=2,5 V zerowy prąd TEST eksportuje się jako **0,4004 A**.

To może stworzyć pozorną usterkę masy lub prądu. Ograniczenie jednorazowych metadanych było częściowo już w v1, ale dynamiczne zakresy i banki zwiększają jego skutek w v2.

**Poprawka:** nowy segment/sesja przy zmianie konfiguracji albo pełne zdarzenia konfiguracji z identyfikatorem przypisanym próbkom. Zapisywać oba banki, zakres faktyczny, zero, AUX, mapowanie, LEARN i ważność prądu L1/L2/bypass. Analizator musi je stosować w czasie.

**F07 — P1 dla pomiaru: konfiguracja ADC i akwizycja nie mają wspólnej synchronizacji**

[Zmiana zakresów w tasku safety](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/EGRLab-v2/firmware/main/app_main.c:149) może działać równolegle z board_adc na drugim rdzeniu. io_lock z board_adc_ranges nie jest używany przez board_adc. Profil może być zmieniony zanim sprzęt zakończy zmianę; dodatkowo stan triggerów zeruje inny task niż ten, który go aktualizuje.

**Poprawka:** pojedynczy właściciel ADC i jego konfiguracji. Zatrzymać akwizycję na zmianę, odczekać ustalenie, atomowo zatwierdzić profil oraz oznaczyć przerwę i konfigurację w logu. Dane triggerów przekazywać przez kolejkę lub chronioną migawkę.

**F08 — P1 dla uruchomienia: firmware ma jednoznaczny błąd składni C**

W [app_main.c](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/EGRLab-v2/firmware/main/app_main.c:339) tekst printf zawiera rzeczywisty koniec wiersza wewnątrz cudzysłowu. Nie jest to sekwencja backslash-n. To blokuje kompilację. Stwierdzenie wynika z pliku; nie przedstawiam go jako wyniku uruchomionego kompilatora.

Dokument v2 uczciwie przyznaje, że projektu ESP-IDF nie skompilowano. Przejście testów Pythona niczego tu nie potwierdza.

**F09 — P2: podsumowania sekundowe są obcinane do niepoprawnego JSON**

[Tworzenie summary](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/EGRLab-v2/firmware/main/app_main.c:195) ma bufor 420 B, natomiast [storage_event](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/EGRLab-v2/firmware/main/storage.c:99) zapisuje najwyżej 254 znaki i nie sprawdza obcięcia. Przykładowe poprawne podsumowanie o długości 266 znaków zostaje niepoprawną linią NDJSON. Czytnik ją pomija jako uszkodzoną.

**Poprawka:** wspólny limit rozmiaru, kontrola wyniku formatowania, jawny błąd lub kompletny krótszy format. Nie zgłaszać zdrowego zapisu po cichej utracie części zdarzenia.

**F10 — P2: SoftAP nie dostaje aktualnej informacji o adapterze; STOP webowy pomija czujnik**

[snapshot](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/EGRLab-v2/firmware/main/app_main.c:38) kopiuje latest, ale wartości test_present/log_present są uzupełniane tylko w lokalnej zmiennej taska safety. Konsola widzi domyślne false, więc warunek uruchomienia SoftAP nie zostaje spełniony. Polityka radia jest wywoływana tylko po poleceniach konsoli.

[web_command](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/EGRLab-v2/firmware/main/app_main.c:258) dla STOP wyłącza silnik i stan logiczny, lecz nie wykonuje board_mode odłączającego K_SENSOR. Nie jest równoważny STOP z konsoli. Ten drugi błąd pozostanie po naprawieniu startu radia.

**Poprawka:** jeden dispatcher poleceń i jedna ścieżka zmiany wyjść dla konsoli i WWW; publikowane, aktualne wejścia; polityka radia reagująca na zmianę trybu i adaptera.

**F11 — P2: DHO804 wymaga oddania jednego kanału na SCOPE_TRIG**

DHO804 nie ma osobnego wejścia EXT TRIG. Instrukcja przypisuje je dwukanałowym DHO802/812. Sygnał trzeba podać np. na CH4, zostają trzy kanały analogowe do pomiaru. [RIGOL DHO800, rozdział 8.1](https://www.rigol.com/dam/global/downloads/brochures/en/user-manual/oscillosopes/DHO800_UserGuide_EN.pdf).

Trigger powstaje po próbkowaniu i warunkach detekcji. STALL celowo czeka 200 ms, OPEN 50 ms. Należy ustawić odpowiednią historię przed wyzwoleniem na oscyloskopie; impuls nie występuje dokładnie w chwili początku awarii.

**F12 — P2: wymagane doprecyzowanie AUX i konfiguracji jego zakresu**

[JP_AUX](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/EGRLab-v2/hardware/connections.csv:69) wybiera wejściową gałąź HI/LO, lecz obie kończą się na V8. Brakuje jednoznacznego odłączenia dolnego rezystora 100 kΩ z toru HI w trybie LO. Jeśli zostaje na wspólnym węźle, mnożnik LO wynosi około **2,01796**, zamiast deklarowanego **1,01996**. Potrzebny jest kompletny schemat przełącznika obejmujący RB4, nie tylko opis jednej gałęzi.

Osobno control_init zeruje range[AUX], czyli wybiera enum ±2,5 V, a zostawia gain 4,06 z HI. Polecenie AUX zastępuje wykalibrowany gain nominalnym. Należy przechowywać odrębną kalibrację HI/LO i jasno ustalać konfigurację startową.

**F13 — P2: triggery wymagają powiązania z trybem i czasem**

[trigger.c](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/EGRLab-v2/firmware/main/trigger.c:35) zapisuje sample_hz, ale nie używa go w warunku skoku. Próg 0,05 dotyczy sąsiednich próbek, więc przy 2 kS/s jest to 0,5 ms, a nie deklarowane 1 ms. Wymagany jest rzeczywisty czas albo właściwe okno próbek.

W L2 i przy założonym bypass prąd nie jest mierzony. Brak flagi ważności pozwala uruchamiać kryterium OPEN na kanale pozbawionym informacji. STALL może oznaczać również normalne utrzymywanie pozycji pod obciążeniem. Ponadto ustąpienie warunku od razu zeruje zatrzask, więc seria naprzemiennych glitchy omija deklarowany limit jednego zdarzenia na 250 ms.

Próg masy wynosi 300 mV. Jeśli celem jest obserwowanie dziesiątek mV, trzeba ustalić odrębne progi zdarzenia i ostrzeżenia po pomiarze szumu, zamiast polegać na samej rozdzielczości 76 µV.

**Przydatność nowych procedur i granice wnioskowania**

**HOT-SOAK** jest wartościowy, bo pozwala porównać ten sam zawór podczas stygnięcia. Jednak domyślny limit firmware 60°C zatrzyma ruch na gorętszym korpusie, a dokument mówi o porównaniu od 100°C. Nie podnosić limitu arbitralnie: najpierw ustalić dopuszczalne warunki konkretnego zespołu i sposób pomiaru. Temperatura obudowy nie jest temperaturą uzwojenia.

Wzrost prądu zerwania wraz z temperaturą wspiera podejrzenie napędu, ale nie stanowi samodzielnego dowodu. Prąd zależy również od napięcia, fazy PWM, sterowania, sprężyny i dryfu toru. W obecnym pomiarze 2 kS/s przy PWM 1 kHz nie wolno automatycznie uznawać próbki za średni lub skuteczny prąd. Do takich miar potrzebna jest metoda obejmująca cykle PWM.

Dobry wynik HOT-SOAK zmniejsza podejrzenie zaworu w sprawdzonych warunkach; nie „oczyszcza” go ze wszystkich usterek pod ciśnieniem, drganiami lub innym obciążeniem. Porównanie zdjętych zaworów jest przydatne, lecz nie tworzy automatycznie grupy wzorcowo sprawnych egzemplarzy.

**SUBSTITUTE LOAD:** 12 Ω daje około 1 A przy 12 V; przy 14,4 V to 1,2 A i 17,28 W dla ciągłego zasilania. To przydatne obciążenie elektryczne, wymagające przewidzianego radiatora. Nie odtwarza indukcyjności, SEM ani prądu zatrzymanego silnika. Bez feedbacku ECU może ograniczyć lub w ogóle nie podjąć sterowania; deklarowane kilkusekundowe okno wymaga sprawdzenia na tym aucie. Dobry wynik potwierdza tor jedynie dla uzyskanego prądu, temperatury i położenia wiązki.

**HARNESS-ONLY:** może ujawnić niektóre przerwy, ale pomiar bez obciążenia słabo ujawnia zwiększoną rezystancję styku. Napięcia jałowe mogą pochodzić z diagnostyki ECU i zmieniać się po odłączeniu zaworu. Nie każdy zapad jest dowodem przerwy. Nie zastępuje pomiaru spadków pod rzeczywistym obciążeniem.

**AUX / klimatyzacja:** powtarzalna korelacja zwiększa wartość hipotezy, lecz nie dowodzi przetarcia ani sprzężenia pojemnościowego. Włączenie klimatyzacji zmienia też obciążenie elektryczne i mechaniczne silnika. Należy rozróżnić przesunięcie masy, zakłócenie napięcia i prawidłową zmianę rozkazu EGR.

**1500–1700 rpm / CAN:** pasywny odbiornik nie zapewnia sam obecności PID obrotów. Dekoder v2 rozpoznaje odpowiedzi OBD 0C tylko wtedy, gdy ktoś o nie pyta i odpowiedzi są widoczne na tej magistrali. Przed jazdą trzeba potwierdzić obecność RPM i oznaczać brak danych; zachować porównywalny bieg, obciążenie, temperaturę oraz stan AC/DPF. Brak zdarzenia w zapisie 2 kS/s nie wyklucza znacznie krótszego glitcha.

**Co zrobić z pretriggerem**

Ciągły zapis i MARK wystarczą do zachowania historii przed zdarzeniem, więc osobny plik zrzutu nie jest konieczny. Argument, że ring był jedynym ryzykiem utraty danych, jest jednak nieprawidłowy. Bufor 1 MiB to 16,384 s przy 2000 rekordach/s po 32 B; 8 MiB daje około 131 s. To odporność na opóźnienie SD, niezależna od formatu pliku. Można zostawić prosty ciągły writer i większy bufor PSRAM. Około 18,6 h do limitu FAT32 to przybliżenie nieuwzględniające narzutu bloków.

**Zalecana kolejność v2.1**

1. Zamknąć schemat zasilania, STOP, latcha, interlocku i K_SENSOR z konkretnymi nóżkami; naprawić KMEAS3 i AUX.
2. Uruchomić bierną akwizycję na znanym AD7606B, początkowo ze stałymi zakresami. Bez deklaracji automatycznej zgodności z innym ADC.
3. Naprawić format konfiguracji sesji i udowodnić zgodność wyniku online z eksportem dla obu banków, każdego zakresu oraz ZERO/LEARN.
4. Skompilować ESP-IDF; dodać próby integracyjne dla błędu I²C, restartu kierunku, zmiany zakresu, utraty adaptera i STOP z obu interfejsów.
5. Po odbiorze torów: L2, potem L1 i dopiero aktywny TEST/HOT-SOAK. Funkcje telefonu na końcu.

**Wyniki sprawdzeń**

Uruchomiono oryginalne 15 testów Pythona: wszystkie przeszły. Dodatkowe kontrprzykłady korzystające z oryginalnego czytnika potwierdziły błąd zakresu, banku oraz obcinanie JSON. Potwierdzono też literalny koniec wiersza w stringu C. Wyniki i powtarzalny skrypt są obok tego raportu: counterexamples.json, check_review.py, fixtures/. Manifest reviewed-files.sha256.json identyfikuje przejrzane pliki.

Największy wkład v2 to lepsza kolejność diagnostyki, L2, AUX i HOT-SOAK. Największy problem to rozdźwięk między opisanym zachowaniem a konkretnymi połączeniami i kodem. **Zachowałbym kierunek v2 i wykonał korektę v2.1 przed zakupem pełnego BOM oraz lutowaniem części aktywnej.**

