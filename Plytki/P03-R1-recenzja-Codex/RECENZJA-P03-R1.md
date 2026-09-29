# Recenzja P03-R1 — CORE

25.09.2026 · Codex · recenzja ukończonego pakietu `P03-R1-review`.

**Werdykt: potrzebna R2 przed zamówieniem PCB.** Gotowa miedź przechodzi kontrolę KiCada, a rozmieszczenie jest czytelne. Pozostały jednak błędy funkcjonalne dotyczące resetu i stanów początkowych, których ERC/DRC nie wykrywa. Nie rekomenduję projektowania całej płytki od nowa: należy zamknąć opisane poniżej problemy, wprowadzić ograniczony zakres zmian i ponownie sprawdzić finalne pliki.

Recenzja dotyczy plików, nie autora/modelu. Nazwy autorów pozostawione w dokumentacji pakietu nie są dowodem jego pochodzenia. Oryginalny projekt nie był edytowany. Analizowano zamrożoną kopię po potwierdzeniu przez użytkownika zakończenia prac.

## Wyniki niezależnego sprawdzenia

| Kontrola | Wynik i zakres |
|---|---|
| Manifest wydania | 98/98 plików zgodnych z SHA256 |
| Świeży ERC, wszystkie ważności | 0 naruszeń |
| Świeży DRC, wszystkie ważności, ponowne wypełnienie stref, parity | 0 naruszeń / 0 niepołączonych / 0 różnic schemat–PCB |
| Ponowne uruchomienie kontroli PCB autora | 26/26 PASS; poniżej pokazano lukę w jednej kontroli |
| Testy ujemne autora | Przeczytano skrypt i raport 14/14. Nie powtarzano całego zestawu; to wynik dostarczony w pakiecie |
| P03 J4 ↔ P04-R1 J2 | Zgodność logiczna 16/16 pozycji |
| P03 J1 ↔ P05-R1 J1 | Zgodność logiczna 16/16 pozycji; nie potwierdza fizycznego spasowania |
| Waveshare | Mapa użytych GPIO zgodna ze schematem producenta rodziny; GPIO47/48 nie są używane |
| Inspekcja wizualna | Oba arkusze PDF schematu, cztery strony PDF PCB, montaż oraz obie warstwy miedzi |
| Odtworzenie schematu z izolowanego pakietu | FAIL: zależność od zewnętrznego katalogu P02-R1-review |
| Pomiary sprzętu | Nie wykonano; nie ma podstaw do deklarowania sprawności urządzenia |

Dowody: `evidence/fresh-erc.json`, `fresh-drc.json`, `fresh-netlist.xml`, `independent-audit.json`, `author-checks-rerun/pcb-checks.json`, `standalone-rebuild.txt`. Skrypt `audit.py` czyta netlistę i PCB bez uruchamiania generatorów. Pomiar długości ścieżki korzysta z funkcji geometrycznej dostarczonego weryfikatora, wywołanej dla właściwego pinu VDD.

## Problemy wymagające poprawy

### P03-01 · P1 · Brak stanów spoczynkowych przed stale włączonymi buforami

**Miejsca:** `src/parts.py:185–188, 210–216`; schemat arkusz IO: U21, U22, U23.

W świeżej netliście `ADC_RESET_SRC` ma tylko U1.21 i U22.2, a `MEAS_EN_SRC` tylko U1.22 i U22.5. Nie ma tam rezystorów ustalających stan. OE# odpowiednich kanałów U22 są stale zwarte do GND. Po resecie MCP23017 porty są wejściami, a podciąganie jest wyłączone. Zasilany bufor dostaje więc nieustalony poziom i może wystawić HIGH, LOW lub zmieniać stan. Funkcja Ioff chroni przy wyłączonym zasilaniu bufora; nie ustala wartości jego wejścia, gdy jest zasilany. [MCP23017, tabela rejestrów POR/RST](https://ww1.microchip.com/downloads/aemDocuments/documents/APID/ProductDocuments/DataSheets/MCP23017-Data-Sheet-DS20001952.pdf), [74LVC125A](https://assets.nexperia.com/documents/data-sheet/74LVC125A.pdf).

To dotyczy również braku zewnętrznego ustalenia `ADC_CS_SRC`, `ADC_CONVST_SRC`, `ADC_SCLK_SRC`, `ADC_SDI_SRC`, `TC1_CS_SRC`, `TC2_CS_SRC`, `SPI3_SCLK_SRC`, `SPI3_MOSI_SRC` oraz wejścia dekodera `MEAS_BANK`. Nie należy uzależniać stanu urządzenia od tego, kiedy firmware ustawi GPIO.

**Skutek:** możliwe niezamierzone załączenie odczepów P05, reset ADC lub wybór układu SPI w czasie startu/resetu CORE. Pull-downy i pull-upy P05/P09 znajdują się ZA aktywnym wyjściem P03 i nie potrafią go przeważyć. Przy stabilnym DAQ_OK P05 nie blokuje błędnego MEAS_EN pochodzącego z P03. Nie jest to dowód samoczynnego ruchu silnika — ten nadal ma osobny tor zezwoleń P04.

**Zmiana:** dodać po stronie `_SRC` pull-upy 10 kΩ do 3V3_CORE dla aktywnych LOW CS oraz pull-downy 10 kΩ dla MEAS_EN, ADC_RESET, CONVST i pozostałych linii wymagających LOW przed inicjalizacją. Ustalić MEAS_BANK. Zachować istniejące poprawne R1 CURRENT_CS_N i R11 SD_CS. Alternatywa z kontrolowanym OE musi jawnie obejmować zarówno reset ESP32, jak i MCP, oraz mieć odbiorcze rezystory na wyjściach.

**Odbiór:** start bez aplikacji, tryb bootloadera, przytrzymany reset i reset samego MCP; oscyloskopem potwierdzić MEAS_EN=0, ADC_RESET=0, CONVST=0 i wszystkie CS nieaktywne. Zasilać też P05 wcześniej niż CORE. Dodać kontrolę netlisty wykrywającą usunięcie każdego wymaganego rezystora przed buforem.

### P03-02 · P1 · Reset MCP23017 nie jest zsynchronizowany ze stanem firmware ESP32

**Miejsca:** `src/parts.py:173–180, 185–198`; netlista `SUP_N`; firmware bazowe v6.1 `board.c`: `porta_set()`, `board_init()`, `board_inputs()`.

SUP_N łączy U3.1, U1.18, R13.1, TP5 i J4.15. Nie trafia do ESP32; M1.J1-3/RST jest NC. TPS3808G33 reaguje nominalnie przy 3,07 V. W dostarczonym bazowym firmware poziom brownout ESP32-S3 jest ustawiony na 7; lokalna dokumentacja ESP-IDF opisuje go jako około 2,44 V, z rozrzutem. To nie zapewnia wspólnego resetu. [TPS3808, tabela progów](https://www.ti.com/lit/ds/symlink/tps3808.pdf), [ESP-IDF — poziomy brownout ESP32-S3](https://docs.espressif.com/projects/esp-idf/zh_CN/v5.0.6/esp32s3/api-reference/kconfig.html).

**Scenariusz:** krótki spadek 3V3_CORE w okolice 3,0 V resetuje MCP, ale nie musi zresetować ESP32. Po powrocie napięcia ekspander ma IODIR=0xFF, a aplikacja nadal pamięta `mcp_ready`, `porta`, poprzedni tryb i konfigurację ADC. `porta_set()` potrafi wtedy uznać zapis za zbędny; samo ACK z I²C nie potwierdza przywrócenia kierunku portów. Inicjalizacja IODIR jest wykonywana przy starcie aplikacji, nie po takim zdarzeniu. Powstaje niespójność sprzętu i metadanych pomiarowych.

P04 dostaje SUP_N i rozbraja tor wykonawczy — to prawidłowa ochrona, ale nie naprawia stanu ekspandera ani wiarygodności logu.

**Zmiana:** preferuję objęcie MCU i MCP wspólnym nadzorem resetu, z uwzględnieniem obwodu EN/automatycznego programowania Waveshare. Nie należy bez sprawdzenia obciążenia pojemnościowego dopinać SUP_N do EN. Alternatywnie potrzebny jest udokumentowany mechanizm wykrycia resetu MCP, odczyt konfiguracji IODIR/IOCON, unieważnienie stanu oraz pełna kontrolowana reinicjalizacja przed wznowieniem pomiarów i zezwoleniem na ARM. To zmiana sprzętowo-programowa; sam pull-down z P03-01 jej nie zamyka.

**Odbiór:** wymusić reset MCP przy działającym ESP32 oraz zapad przez próg supervisora; wymagane jednoznaczne zatrzymanie, zapis zdarzenia/reset sesji, odtworzenie konfiguracji i brak automatycznego powrotu do ruchu. Przetestować też przycisk RESET i auto-reset USB.

### P03-03 · P2 · USB zasila wspólną szynę 5V_SYS przez moduł Waveshare

**Miejsca:** `src/parts.py:177, 207–208`; J10.1 ↔ M1.J1-21; P02-R2 wspólna 5V_SYS.

Według schematu Waveshare USB VBUS dochodzi przez D1 B5819WS do VDDUSB, które wychodzi na pin 5 V listwy i zasila LDO modułu. P03 łączy ten pin bezpośrednio z LV03/5V_SYS. Przy wyłączonym P02 i podłączonym kablu USB prąd może więc popłynąć z komputera do całej wspólnej szyny 5 V, w tym wyjścia przetwornicy P02. Dokumentacja P03 nie określa tego trybu. [Schemat producenta Waveshare](https://files.waveshare.com/wiki/ESP32-S3-DEV-KIT-N8R8/ESP32-S3-DEV-KIT-N8R8-schematic.pdf).

**Skutek:** niezamierzone częściowe zasilanie innych PCB i obciążenie USB podczas programowania; nie można traktować tego jako uruchomienia samego CORE. Nie stwierdzam zwarcia dwóch idealnych źródeł ani pewnego uszkodzenia komputera: D1 blokuje kierunek do VBUS, a rzeczywiste obciążenie i zachowanie przetwornicy przy zasilaniu od wyjścia pozostają do pomiaru. Schemat producenta jest wspólnym dokumentem rodziny; ciągłość tej drogi trzeba potwierdzić na posiadanej rewizji N32R16V.

**Zmiana:** rozdzielić 5V_SYS i lokalne 5V_M1, zapewniając blokadę kierunku M1→P02, albo przewidzieć jednoznaczny sprzętowy wybór zasilania serwisowego. Przy diodzie w torze P02→M1 trzeba policzyć jej spadek i zapas LDO. Odpięcie LV03 jest doraźną procedurą serwisową, nie rozwiązaniem docelowego zasilania przy pełnym zestawie połączeń.

**Odbiór:** USB-only / P02-only / oba źródła / odłączenie każdego ze źródeł; zmierzyć prądy i napięcia 5V_SYS, 5V_M1, 3V3_CORE, 3V3_IO oraz zachowanie resetów. Dodać ten przypadek do tabeli zasilania częściowego całego EGRLab.

### P03-04 · P2 · C3 sprawdzany względem błędnego pinu TPS3808

**Miejsca:** `src/route_critical.py` lista kondensatorów; `src/verify_pcb.py:284–285`; `src/parts.py:196`.

BOM prawidłowo opisuje C3 jako odsprzęganie U3.6. Generator i kontrola PCB używają jednak U3.3. W obudowie DBV pin 3 to MR, pin 6 to VDD. Oba są w tej samej sieci, dlatego ERC i porównanie netlist przechodzą. [TPS3808 — pinout i zalecenie lokalnego 100 nF](https://www.ti.com/lit/ds/symlink/tps3808.pdf).

| Pomiar gotowej PCB | Do U3.3, użyte w teście | Do rzeczywistego VDD U3.6 |
|---|---:|---:|
| Odległość prosta od C3.1 | 4,5 mm | 20,38 mm |
| Najkrótsza droga po ścieżkach | 4,5 mm | 23,3 mm |

Wartości nie obejmują dodatkowej drogi na adapterze. Kontrola „≤8 mm prosto i ≤20 mm po miedzi do VDD” daje więc fałszywe PASS. Nie dowodzi to samo w sobie niestabilności supervisora; dowodzi błędnej weryfikacji i odstępstwa od własnego wymagania.

**Zmiana:** poprawić pin w generatorze i weryfikatorze na 6, przenieść C3; jeszcze lepiej umieścić lokalne 100 nF bezpośrednio na PA0085 przy VDD/GND układu i jawnie uwzględnić je w BOM i montażu. Nie zmieniać samego limitu testu, aby zalegalizować obecną pozycję.

**Odbiór:** niezależna tabela pinów zasilania z not katalogowych; próba ujemna polegająca na umieszczeniu kondensatora przy MR zamiast VDD musi oblać kontrolę. Zaktualizować opis „wszystkie ≤4,9 mm” w QA i PDF.

### P03-05 · P2 · Samodzielny pakiet nie odtwarza schematu

**Miejsce:** `src/parts.py:15, 24–25, 105`.

Generowanie wymaga sąsiedniego `P02-R1-review/eda/libraries/P02.pretty`. W izolowanej kopii, mimo obecności gotowych lokalnych footprintów P03, `build_schematic.py` kończy się `FileNotFoundError` przy pierwszym `copyp02()`. Udokumentowane `run_release.py` zaczyna od tego samego kroku. To rzeczywista próba, nie wniosek wyłącznie z czytania kodu; log w `evidence/standalone-rebuild.txt`.

**Zmiana:** trzy potrzebne footprinty utrzymywać jako zamrożone zasoby wewnątrz pakietu. Generator nie może zależeć od przypadkowej zawartości poprzedniej rewizji w katalogu obok. Zadeklarować wersję bibliotek systemowych KiCada i wszystkie pozostałe zależności.

**Odbiór:** rozpakować tylko P03 do pustego katalogu z zadeklarowanym toolchainem i odtworzyć całość. Porównać połączenia, geometrię, reguły oraz finalne raporty. Nie wymagać identycznych UUID i metadanych PDF.

### P03-06 · P2 · Część wejść odłączonych modułów nie ma stanu domyślnego przed buforem

**Miejsca:** U12.5 INTERLOCK, U14.2 TEST_KEY, U13.2/5 ENA_DIAG/ENB_DIAG, U11.12 CAN_RX; `src/parts.py:210–214, 222–226`.

P03 przewiduje poprawne rezystory dla HW_ARMED, LOGGER_CURRENT_OK, SENSOR_HEALTHY, LOGGER_CLEAR i TEST_PRESENT. Nie ma ich jednak dla powyższych sygnałów. Odłączony przewód zostawia zasilane wejście 74LVC125 w stanie nieustalonym. Podciąganie wewnętrzne MCU/MCP po stronie `_CORE` nie ustali poziomu po drugiej stronie bufora. Jest to szczególnie istotne przy planowanym uruchamianiu po jednym module.

**Skutek:** losowe wskazanie TEST_KEY/INTERLOCK, nieokreślone stany diagnostyczne i możliwe pozorne aktywności CAN przy braku P10. Nie oznacza to obejścia całego interlocka: HW_ARMED ma poprawny pull-down, a P04 niezależnie sprawdza swoje wejścia.

**Zmiana:** jawna tabela polaryzacji i rezystory po stronie złącza/bufora: INTERLOCK i TEST_KEY domyślnie LOW; CAN_RX domyślnie HIGH (stan recessive). Dla ENA/B zdefiniować stan „brak modułu/fault” zgodny z docelowym P07 i jego niepodłączoną diagnostyką. Dla wejść magistral ADC/SPI również zapisać poziom idle i sposób rozpoznania nieobecnego urządzenia. Nie należy przez dodanie HIGH na DIAG maskować braku P07. P07 pozostaje HOLD do oceny rzeczywistego modułu BTS7960.

**Odbiór:** każde złącze sygnałowe odłączone osobno przy zasilonym CORE, bez polegania na polaryzacji wewnętrznej MCU za buforem. Dla testów funkcjonalnych brak modułu ma dawać jawne ABSENT/FAULT, nie wiarygodnie wyglądające pomiary.

### P03-07 · P3 · Schemat PDF ma kolizje opisów i ucięty tytuł

Arkusz 1: opisy M1/U1/U3 nakładają się na symbole lub linie; tytuł wychodzi poza prawą krawędź strony. Arkusz IO: napisy jednostek buforów wchodzą na nagłówki sekcji; niektóre etykiety dochodzą do ramki. Obszerny arkusz ma wystarczająco dużo wolnego miejsca, żeby to poprawić. PDF PCB jest czytelniejszy i nie wymaga analogicznej przebudowy.

**Zmiana:** osobne pozycje pól Reference/Value, krótszy tytuł tabelki, większe marginesy dla globalnych etykiet. Render obu arkuszy po eksporcie i oględziny w powiększeniu, nie tylko miniatury. Przykład: `evidence/schematic-clipping-detail.png`.

## Kwestie otwarte — nie przedstawiam ich jako potwierdzonych usterek

1. **Para B2B P03–P05.** Logiczna mapa 16 pozycji jest zgodna. W R1 uczciwie pozostawiono przymiarkę złączy i dystansów. Przed produkcją obu PCB potrzebny jest jeden zatwierdzony przekrój z wymiarami: numery części, odległość krawędzi, wysokość osi obu rzędów, głębokość zazębienia, orientacja pinów, klucz i punkty mocowania. Ogólny footprint 2×8 ani zgodność nazw sieci tego nie zastępują. Dostępne są [rysunki Samtec SSW](https://suddendocs.samtec.com/prints/ssw-1xx-xx-xxx-x-xx-xxx-xx-mkt.pdf). Zapis o przymiarce i teście ciągłości należy zachować.
2. **Antena.** Przyjęte +3 mm po bokach i +8 mm za końcem modułu jest kompromisem autora, a nie potwierdzoną kwalifikacją RF. Espressif zaleca położenie anteny poza płytą bazową lub odpowiednie wycięcie i przestrzeń wokół niej; wskazuje również potrzebę kontroli wpływu obudowy. [Wytyczne układu PCB ESP32-S3](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/pcb-layout-design.html). Ponieważ Wi-Fi jest opcjonalne, nie traktuję tego jako samodzielnego powodu zatrzymania przewodowego loggera. Jeśli Wi-Fi ma być używane, warto zmienić orientację M1 przed produkcją albo przyjąć jawne kryterium zasięgu i zmierzyć gotowy zestaw. Test sprawdzający wyłącznie prostokąt 3/8 mm nie jest testem RF.
3. **Zbocza magistral.** Brak rezystorów źródłowych na wyjściach U21/U23 i długie połączenia wymagają pomiaru na końcu toru. Częstotliwość zegara nie określa szybkości zbocza LVC. W prototypie warto przewidzieć pola na 22–47 Ω (ewentualnie początkowo 0 Ω), przede wszystkim przy SCLK/CONVST i zegarze do P09. Dobór po oscyloskopie; nie twierdzę, że obecna magistrala na pewno nie zadziała.
4. **Adaptery i zasilanie SD.** Sprawdzić odsprzęganie przy samych układach na adapterach, impulsowe obciążenie microSD i margines termiczny regulatora konkretnego Waveshare. Kondensator blisko pinu adaptera nie zawsze daje krótką pętlę przy scalaku. Nie ma podstaw do wymiany MCU tylko z powodu tej recenzji.
5. **Rzeczywiste części.** Potwierdzić obrys Waveshare, PA0085, SD i wysokości gniazd. Rysunek Adafruit 4682 i przypisanie 3V/GND/CLK/SO/SI/CS/D1/DAT2/DET są spójne z przyjętym adapterem. Sprawdzenie biblioteki nie zastępuje fizycznej przymiarki zakupionych elementów.

## Co jest wykonane dobrze

Zachowałbym format płytki, układ złączy przy krawędziach, dodatkowe mocowanie przy DAQ, lutowaną wiązkę LV03 z kotwą 12,5 mm, rozdzielenie 3V3_CORE i 3V3_IO, buforowanie z Ioff i większość rozmieszczenia. Świeży DRC jest naprawdę czysty; reguły nie zostały wyłączone, a testy ujemne sprawdzają konkretne rodzaje usterek. To dobry fundament do ograniczonej R2.

Porównanie 310 pinów ze starszą wersją jest użyteczną kontrolą regresji. Nie jest jednak niezależnym sprawdzeniem poprawności: P03-01 i P03-02 zachowują błędy odziedziczone z wcześniejszej architektury. Nie należy przypisywać ich wyłącznie nowemu layoutowi.

## Jak zamknąć R2 i poprawić proces

1. Przed trasowaniem zatwierdzić krótką tabelę każdego sygnału: kierunek, domena zasilania, stan przy reset/bootloader, brak przewodu, brak nadajnika, brak odbiornika, element ustalający ten stan i strona bufora. Z tej tabeli generować niezależne kontrole netlisty. Stan źródła Hi-Z musi być przypadkiem testowym.
2. Narysować graf resetów i zasilania obejmujący USB. Zdefiniować, co dzieje się po resecie każdego układu osobno, nie tylko po jednoczesnym power-on całego urządzenia. Zweryfikować stan firmware po resecie ekspandera.
3. Oddzielić dane użyte do generowania od wymagań użytych do kontroli. Numery VDD/MR/SENSE mają wynikać z niezależnej tabeli not katalogowych. C3 przy U3.3 pokazuje, dlaczego kopiowanie tej samej listy pinów do generatora i testu nie wystarcza.
4. Zamknąć mechaniczną parę P03–P05 jako wspólny interfejs, z konkretnymi częściami. Dopiero wtedy traktować pozycję J1 i otworów jako zamrożoną.
5. Wprowadzić ograniczoną R2: stany wejść, wspólny reset lub pełna obsługa resetu MCP, rozdzielenie zasilania USB, poprawa C3, samodzielny build i porządek na schemacie. Aktualizować BOM, instrukcję montażu oraz kryteria odbioru razem ze schematem.
6. Po zmianach: świeży ERC/DRC/parity, porównanie netlist R1→R2 z listą dozwolonych zmian, istniejące testy ujemne plus nowe przypadki elektryczne, odtworzenie z samego archiwum, inspekcja obu PDF. Do zamówienia przechodzi jedna zamrożona paczka z hashami.
7. Na stole wykonać scenariusze z P03-01/02/03/06 i dopiero potem połączyć z torem wykonawczym. Pomiary mają zamknąć konkretne niewiadome; nie ma potrzeby rozbudowywania projektu o kolejne warstwy zabezpieczeń bez powodu.

**Zakres tej recenzji:** schemat, PCB, generatory/kontrole oraz wybrane istotne interakcje z P02/P04/P05 i bazowym firmware v6.1. Nie jest to pełny ponowny audyt całego firmware ani kwalifikacja automotive. Wcześniejsze otwarte tematy P05 (m.in. sekwencja startu ADC i szybkość SPI) nadal obowiązują; przegląd P03 ich nie zamyka.
