# P00-R1 — niezależna recenzja Codex

25.09.2026. Oceniony pakiet: `Plytki/P00-R1-review`. Autor projektu: Opus/Claude. Recenzja obejmuje schemat, gotową PCB, dokumentację, BOM, kontrolę zgodności z P04 v6.1-rc1 oraz ponowne wykonanie kontroli na kopii. Oryginału nie poprawiano.

**Werdykt: dobra baza do niewielkiej rewizji R2. Przed zamówieniem poprawić sekcję zasilania i BOM C6. Nie ma uzasadnienia do projektowania całej PCB od nowa.**

Najistotniejsze problemy są w warunkach pracy stabilizatora. Poprawne ERC i DRC ich nie sprawdzają. Nie stwierdzam uszkadzania odbiornika przez ten projekt; stwierdzam brak zagwarantowanego napięcia źródeł logicznych w dwóch przewidzianych stanach pracy.

## 1. Wyniki odtworzonych kontroli

| Kontrola | Wynik recenzji |
|---|---|
| SHA-256 plików z oryginalnego manifestu | 84/84 zgodne |
| ERC na dostarczonym schemacie | 0 naruszeń według reguł projektu |
| Świeży eksport netlisty i sprawdzenie schematu | 64 elementy, 36 sieci, 141/141 pinów zgodnych |
| Natywny DRC gotowej PCB, wszystkie poziomy istotności | 0 naruszeń / 0 niepołączonych / 0 rozbieżności ze schematem |
| Kontrole `verify_pcb.py` | 22/22 |
| Ponownie uruchomione mutacje PCB | 8/8 wykrytych, również przez oczekiwaną kontrolę szczegółową |
| Inspekcja dokumentów | Schemat A3 i wszystkie cztery strony PDF PCB obejrzane po rasteryzacji |
| Regeneracja w katalogu bez sąsiedniej P02-R1 | BŁĄD: brak pliku footprintu pobieranego z P02-R1 |
| Pomiary egzemplarza | NIEWYKONANE — recenzja plików |

Wyniki pozytywne dotyczą dostarczonych artefaktów. Nie deklaruję pełnej, samodzielnej regeneracji wydania: znaleziono opisaną niżej zależność od innego pakietu. Sprawdzenia porównujące PCB z netlistą oraz netlistę z listą części potwierdzają spójność, a nie poprawność doboru części. Analizę elektryczną przeprowadzono dodatkowo na podstawie kart producentów.

## 2. R01 — błędna dolna granica napięcia zasilania

**Priorytet: przed zamówieniem, bo wpływa na deklarację na PCB i ewentualny wybór U2.**

Lokalizacja: `docs/ZALOZENIA-P00-R1.md:38`, `src/parts.py:62`, `src/build_schematic.py:51`, `reference/ZRODLA.md:4`.

Projekt deklaruje 5–15 V na J10, a przed U2 jest szeregowa 1N5819. Powołuje się na SNVS100F, czyli tabelę parametrów wariantów LM2937 o wyższych napięciach. Dla **LM2937-3.3** właściwa karta **TI SNVS015F, strony 4–5**, podaje minimum **4,75 V na wejściu samego regulatora**; przypis wyjaśnia ograniczenie jego wewnętrznego zasilania. Nie wystarcza sprawdzenie typowego dropout. [TI LM2937-2.5/-3.3, kopia dokumentu producenta](https://www.mouser.com/datasheet/2/405/lm2937-3.3-484674.pdf).

Przykład obliczeniowy: 5,00 V na J10 i spadek D1 0,35 V dają 4,65 V na U2. Dodatkowo tolerancja źródła może obniżyć napięcie. Działanie pojedynczego egzemplarza przy 5 V nie potwierdzi całego zadeklarowanego zakresu.

**Rekomendacja:** dla tego przyrządu stołowego pozostawić LM2937 i diodę, zmienić zakres na **6–15 V na J10**, z zalecanym zasilaniem 9–12 V. Zaktualizować schemat, nadruk, README i kartę modułu. Jeżeli 5 V jest koniecznym wymaganiem użytkowym, dobrać inny regulator dla 3,3 V i uwzględnić D1. To alternatywna decyzja projektowa, a nie zamiana samego napisu.

Odbiór: zmierzyć TP3 i TP1 przy najniższym zadeklarowanym napięciu, dla małego i największego rzeczywistego obciążenia.

## 3. R02 — zbyt małe obciążenie LM2937 w stanie spoczynkowym

**Priorytet: przed zamówieniem — dodać obciążenie lub wybrać regulator pracujący bez niego.**

Lokalizacja: `src/parts.py:60–81`; sieć `P00_V33` w wyeksportowanym schemacie.

Parametry napięcia wyjściowego w SNVS015F są określone dla **IOUT ≥ 5 mA**. R1 nie zapewnia tego warunku. [TI, tabela Electrical Characteristics, strona 5](https://www.mouser.com/datasheet/2/405/lm2937-3.3-484674.pdf).

Przy SW1–SW8 w L, SW9 w STOP i odłączonych odbiornikach obciążenie stanowią głównie LED10 z rezystorem, R1 przez załączony DISCHARGE, R4 oraz sam TLC555. Szacunek przy nominalnych 3,3 V:

| Składnik | Przybliżony prąd |
|---|---:|
| LED10 + RL10, przy założonym VF = 1,9 V | 1,40 mA |
| R1 = 4,7 kΩ do aktywnego DISCHARGE | 0,70 mA |
| R4 = 100 kΩ do RESET w L | 0,033 mA |
| Przyjęty prąd TLC555 | 0,20 mA |
| Suma | **2,34 mA** |

To model typowego stanu, nie pomiar ani gwarantowany minimalny pobór. Wystarcza do wykazania, że nie zaprojektowano wymaganych 5 mA. Prąd własny LM2937 płynący do jego GND nie jest obciążeniem jego wyjścia. Przy uruchamianiu z wyjętym U1 problem jest jeszcze wyraźniejszy. Konsekwencją jest praca poza warunkami gwarancji napięcia; nie przesądzam kierunku ani wielkości odchyłki.

**Prosta poprawka:** rezystor **560 Ω, 1%, 0,25 W** pomiędzy 3V3 i GND. Sam zapewni około 5,55 mA przy 3,14 V i rezystancji +1%; największa obliczona moc przy 3,46 V i −1% to około 21,6 mW. Jest duży zapas. Doliczyć go do bilansu U2. Nie zwiększać sztucznie jasności LED tylko po to, aby spełnić minimum regulatora.

Odbiór: pomiar 3V3 i oscyloskopem tętnień w stanie wszystkie L/STOP, również bez U1, następnie przy wszystkich H. Po zmianie policzyć straty U2 z uwzględnieniem także jego prądu GND; dotychczasowe 0,5 W jest przybliżeniem, nie pełnym maksimum.

## 4. R03 — niepotwierdzony numer C6 i niepełny warunek ESR

**Priorytet: poprawić BOM przed zakupem; nie wymaga przebudowy całej płytki.**

Lokalizacja: `docs/BOM.csv:7`, `src/parts.py:64`, `docs/ZAKUPY-P00.md`.

Wpis **EEUFR1C220, 22 µF / 16 V** nie ma potwierdzenia w sprawdzonym katalogu Panasonic FR-A. Dla 16 V tabela rozpoczyna się od 68 µF; nie znalazłem w niej tego MPN. Nie traktować go jako zweryfikowanego elementu zakupowego. [Panasonic FR-A, tabela 16 V](https://industrial.panasonic.com/cdbs/www-data/pdf/RDF0000/ABA0000C1259.pdf).

Konkretny kandydat bez zmiany rastra: **EEUFR1H220, 22 µF / 50 V, średnica 5 mm, wysokość 11 mm, raster 2 mm**, potwierdzony na stronie producenta. [Panasonic EEUFR1H220](https://industrial.panasonic.com/ww/products/pt/aluminum-cap-lead/models/EEUFR1H220). Wyższe napięcie znamionowe nie przeszkadza. Dobór ESR i odbiór stabilności nadal trzeba zamknąć dla rzeczywiście kupionej części.

Dokumentacja regulatora wymaga COUT co najmniej 10 µF oraz ESR w odpowiednim przedziale; podaje **0,01–3 Ω** i wykres zależności od obciążenia. W R1 zapisano tylko górną granicę. Uzupełnić dolną i zadeklarować temperaturę pracy przyrządu stołowego. [TI SNVS015F, strony 11–12](https://www.mouser.com/datasheet/2/405/lm2937-3.3-484674.pdf).

Nie ma tu dowodu oscylacji istniejącego układu. Zalecam potwierdzony MPN, prawidłowy zapis kryteriów i zwykły pomiar oscyloskopem. Nie ma potrzeby profilaktycznie komplikować zasilania. Uwaga na rozróżnienie impedancji katalogowej przy 100 kHz od gwarantowanego przedziału ESR.

## 5. R04 — generator nie odtwarza samodzielnie archiwum P00

**Priorytet: poprawka procesu wydania, niezależna od działania gotowej PCB.**

Lokalizacja: `src/parts.py:8`, `src/parts.py:17–22`, instrukcja odtworzenia w README.

`copyp02()` bezwarunkowo pobiera trzy footprinty z `../P02-R1-review/eda/libraries/P02.pretty`. Są one już obecne w lokalnej bibliotece P00, jednak generator z nich nie korzysta jako źródła. Próba uruchomienia pierwszego kroku regeneracji bez sąsiedniego pakietu kończy się `FileNotFoundError` dla `C_Vishay_K15_H5_P5.kicad_mod`. Zapis błędu: `rebuild-probe.log`.

**Poprawka:** przechowywać wejściowe footprinty niestandardowe w pakiecie P00 i regenerować bibliotekę z nich. Zachować informację o pochodzeniu i hash. Przygotować test wydania uruchamiany po rozpakowaniu ZIP w czystym katalogu, z samym zadeklarowanym toolchainem. Nie naprawiać tego przez dodawanie ukrytej zależności od nowej wersji P02.

## 6. R05 — domknąć instrukcję współpracy z P04

**Priorytet: przed odbiorem P04; nie blokuje samego rozmieszczenia P00.**

R1 uczciwie odkłada wiązkę poza zakres, lecz równocześnie opisuje używanie przewodów Dupont bezpośrednio na badanej płytce. P04 v6.1 ma również Mini-Fit i lutowane wyprowadzenia. Potrzebna będzie mała wiązka/adaptor stołowy z mapą sygnałów, a nie samo dziewięć identycznych przewodów.

Sprawdzono rzeczywistą netlistę `Rewizje/EGRLab-v6.1-rc1/eda/P04/P04.xml`. Poniżej mapa do przygotowania wiązki; po wydaniu PCB P04 trzeba ponownie sprawdzić jej oznaczenia. Nie jest to polecenie podpinania źródeł do kompletnego, zasilanego zestawu.

| Sygnał wejściowy P04 | Złącze logiczne / pin w netliście v6.1 | Oznaczenie w tej netliście |
|---|---|---|
| PSU_OK | J_PSUOKA.1 | J18.1 |
| DAQ_OK | J_DAQOKA.1 | J13.1 |
| DRIVE_OK | J_DRIVEA.7 | J14.7 |
| SENSOR_OK | J_SENSORA.3 | J20.3 |
| CORE_LINK | J_SAFEB.13 | J19.13 |
| PG_LINK | J_PGA.5 | J17.5 |
| TEST_KEY | J_PANELSAFEA.3 | J16.3 |
| MECH_OK | J_PANELSAFEA.4 | J16.4 |
| HEARTBEAT | J_SAFEB.3 | J19.3 |
| MCU_ARM | J_SAFEB.5 | J19.5 |
| SUP_N | J_SAFEB.15 | J19.15 |

Osiem przełączników wystarcza na sześć głównych wejść dodatnich i TEST_KEY/MECH_OK, ale pozostają MCU_ARM, SUP_N oraz styki ARM i STOP. Trzeba określić ich stan w każdej próbie. Można użyć oznaczonych zworek lub przepinać kanały między testami; **nie widzę konieczności powiększania P00 tylko z tego powodu**. Nie zwierać wyjścia 3V3 P00 z zasilaniem 3V3 P04 — wspólna jest masa, a źródła trafiają na wskazane wejścia przez swoje rezystory.

Dopisać do odbioru:

- Pomiary H/L na wejściu P04 pod rzeczywistym obciążeniem. P00 z 1 kΩ daje nominalnie 3,0 V na 10 kΩ do masy, a na dwóch równoległych 10 kΩ około 2,75 V. To nie są wyjścia 3,3 V bez spadku. W aktualnej netliście MECH_OK ma dwa takie rezystory. Większość pozostałych wejść jest buforowana 74LVC125A; jego próg H przy zasilaniu 2,7–3,6 V wynosi 2,0 V. [Karta Nexperia, strona 4, kopia dokumentu producenta](https://xonstorage.z8.web.core.windows.net/pdf/nexperia_74lvc125ad118_apr22_xonlink.pdf).
- Pomiar amplitudy heartbeatu po R3 z podłączonym P04 i świecącą LED9. Dzielnik obciąża go dodatkowo, a wyjście TLC555 nie jest idealnym źródłem napięcia. Nie stwierdzono, że układ nie zadziała; potrzebny jest pomiar, którego nie zastępuje samo obliczenie częstotliwości.
- Próby watchdoga dla braku przewodu, stałego L i stałego H. SW9 poprawnie daje stałe L. Dla H można odłączyć J9 i użyć jednego kanału statycznego; nie łączyć ze sobą dwóch wyjść. Czas zadziałania mierzyć od ostatniego zbocza HEARTBEAT, nie od ruchu ręki przy przełączniku.
- LED kanału wskazuje położenie źródła przed rezystorem. Nie potwierdza ciągłości wiązki ani poprawnego napięcia na odbiorniku. LED9 świecąca przy około 100 Hz też nie dowodzi obecności prawidłowych zboczy.
- Kolejność zasilania i przełączeń: zacząć od L/STOP, wspólnej masy oraz poprawnie zasilonego P04. Nie zakładać odporności wszystkich wejść na zasilanie przy wyłączonej płytce; TEST_KEY i MECH_OK nie przechodzą przez te same bufory co główne wejścia modułów.

## 7. Co w projekcie jest dobre i co poprawić kosmetycznie

Poprawnie rozwiązano rzeczywiste pułapki: numerację wspólnego styku WS-SLTV, orientację suwaka, jednakową polaryzację J1–J9, rezystory szeregowe na wszystkich dziewięciu wyjściach, nieobciążanie wyjść kanałowych ich LED-ami oraz STOP na RESET timera. Pinout U2 jest prawidłowy. Obliczenie timera daje około 102,3 Hz; do próby watchdoga nie potrzeba precyzyjnego generatora. [Würth WS-SLTV](https://www.we-online.com/en/components/products/datasheet/450301014042.pdf), [TI TLC555, układ astabilny](https://www.ti.com/lit/ds/symlink/tlc555.pdf).

PCB ma uporządkowane kolumny i wystarczające szerokości ścieżek dla tego przyrządu. Kontrole nie ograniczają się do liczenia elementów: sprawdzają także orientację, nadruk, dostęp do zasilania, odstępy od śrub i zachowanie poprowadzonych ręcznie połączeń. Mutacje faktycznie są wykrywane. Zachowałbym ten układ i te kontrole.

Drobne poprawki dokumentów:

- W schemacie PDF opisy LED1–LED9 nakładają się na symbole/oznaczenia wyprowadzeń; tekst tabliczki tytułowej wychodzi poza jej szerokość. Poprawić pozycje właściwości i ponownie obejrzeć eksport. Dokument PCB jest znacznie czytelniejszy.
- BOM LED9 i LED10 odsyła do karty zielonej L-934GD zamiast właściwych kart żółtej i czerwonej diody.
- Zapis „≤3,3 mA przy dowolnej pomyłce” jest zbyt szeroki. To około 3,3 mA przy zwarciu nominalnego źródła do GND. Już przy 3,46 V i rezystorze −1% jest około 3,49 mA. Opisać ograniczenie dla badanego obwodu logicznego, bez obietnicy ochrony przed dowolnym obcym napięciem.

## 8. Minimalny zakres R2 i zmiana procesu

1. Zamknąć wybór: 6–15 V z LM2937 albo inny regulator zachowujący wymagane 5 V na J10. Dodać minimalne obciążenie, jeśli pozostaje LM2937.
2. Poprawić C6, jego źródło katalogowe i warunki stabilności; przeliczyć pobór i grzanie.
3. Uniezależnić generator od katalogu P02, poprawić PDF oraz opisy zasilania.
4. Ponowić ERC, DRC, 22 kontrole i 8 mutacji na finalnej rewizji. Wykonać regenerację z czystej kopii wydania i kontrolę wizualną finalnego eksportu.
5. Przygotować krótką kartę odbioru P00: zasilanie minimalne/maksymalne, stan minimalnego obciążenia, H/L pod obciążeniem, heartbeat RUN/L/H i próba temperatury U2. Wiązkę do P04 można domknąć wraz z jej PCB.

**Do procesu dodałbym jedną krótką kontrolę warunków pracy każdego nowego układu:** dokładny wariant MPN i rewizja karty, minimalne napięcie na jego pinie po elementach szeregowych, minimalne i maksymalne obciążenie, wymagane elementy aplikacyjne. Druga kontrola to potwierdzenie każdego MPN w tabeli producenta, zamiast wyprowadzania oznaczenia z reguły numeracji. Te dwa kroki wychwyciłyby trzy główne uwagi tej recenzji bez rozbudowy przyrządu.

Pliki pomocnicze: `evidence/` — odtworzone kontrole; `operating-points.json` i `analyse_operating_points.py` — jawne założenia obliczeń; `P04-contract.json` — odczyt połączeń P04; `source-sha256.json` i `original-integrity.json` — identyfikacja niezmienionego oryginału. Nie są to wyniki pomiarów sprzętu ani deklaracja wykonania R2.
