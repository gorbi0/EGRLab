# Co się zmieniło między v2 a v3

**v3 zastępuje EGRLab-v2.** Katalogi `EGRLab-v1/` i `EGRLab-v2/` zostają jako punkty odniesienia — nie buduj z nich. Historia zmian v1 → v2: `00-zmiany-v1-v2.md`.

Powód rewizji: zewnętrzny przegląd v2 (`../../EGRLab-v2/OCENA-v2.md`, 21.09.2026) znalazł osiem błędów blokujących i pięć funkcjonalnych. Sprawdziłem każdy z nich w plikach i w kodzie; **jedenaście potwierdziło się w całości, dwa częściowo**. v3 naprawia wszystkie oraz dwie rzeczy, które sam uznałem za pogorszenie względem v1.

Kierunek diagnostyczny v2 przeglądu nie podważył: sześć permutacji IDENTIFY, kolejność L2 przed L1, kanał AUX, HOT-SOAK, kalibracja per bank i rezygnacja z osobnego pliku pretriggera zostają bez zmian.

## Naprawione błędy blokujące

**F01 — obwód STOP/SAFE_N był wewnętrznie sprzeczny.** v2 wpinała w węzeł typu wire-AND wyjście push-pull bramki 74HC08, dokładała drugi pull-up omijający grzybek i próbowała zmieścić trzy warunki w bramce dwuwejściowej.

W v3 węzeł `SAFE_N` ma **dokładnie jeden pull-up, poprowadzony przez styk NC grzybka**, i wiszą na nim wyłącznie wyjścia otwarte: dwa komparatory okna prądu, dwa komparatory okna 5V_A, supervisor 3V3 i pętla interlock. Watchdog, który ma wyjście push-pull, dostał **tranzystor 2N7002 sterowany przez inwerter 74HC14** — dopiero to jest wyjście otwarte. Zezwolenia rozpisane są bramka po bramce w `hardware/connections.csv`: `MOTOR_PERMIT` zajmuje dwie bramki, PWM jedną, zezwolenie czujnika trzy. Przerwany przewód grzybka nadal wygląda jak wciśnięty STOP, bo węzeł ma rezystor 100 kΩ do masy i żadnego innego zasilania.

**F02 — ochrona wejścia była narysowana odwrotnie.** v2 miała P-MOS ze źródłem od akumulatora, czyli orientację zwykłego przełącznika: przy odwróconej baterii przewodzi dioda strukturalna. Do tego clamp SM8S24CA przy znamionowym prądzie impulsu leży powyżej 36 V, czyli powyżej dopuszczalnego wejścia przetwornic TSR.

W v3 wariantem bazowym jest z powrotem **moduł LM74800EVM-CD** z v1: odwrotna polaryzacja i aktywne odcięcie nadnapięciowe, z wymogiem ustawienia i **zmierzenia** progu 17,5–18,5 V. Wariant z pojedynczym P-MOS-em został w BOM jako opcja, z jawnie zapisaną poprawną orientacją (dren od akumulatora, źródło od strony chronionej) i z informacją, co się przez to traci.

**F03 — jeden przekaźnik miał robić dwie niezależne rzeczy.** v2 używała obu biegunów KMEAS3 do dwóch funkcji sterowanych osobnymi sygnałami, a G6K-2F-Y ma jedną cewkę na oba zestyki. W LOGGER odczep pinu 6 wymagał styku NO, a prąd LOGGER styku NC tego samego przekaźnika — fizycznie niewykonalne.

v3 ma **osobny przekaźnik `KCUR`** na multiplekser prądu, z własną cewką sterowaną `MEAS_BANK`. Bank odczepów zostaje przy trzech przekaźnikach i jednym sygnale `MEAS_EN`.

**F04 — obsługa AD7606B i „automatyczny fallback".** Trzy osobne rzeczy były źle. Ramka odczytu rejestru szła jako `0x8000` zamiast `0x4000`; software mode wymaga **zworek OS[2:0] = 111**, czego sam zapis po SPI nie załatwia; a po nieudanej konfiguracji firmware dalej przeliczał próbki według zakresów z profilu, więc przy sprzętowym ±10 V i programowym ±5 V zero prądu wychodziło jako −5 A.

W v3 tryb pracy przetwornika jest **decyzją podejmowaną przy kompilacji** (`CONFIG_EGR_ADC_SOFTWARE_MODE`), a nie zgadywaną w czasie pracy. Software mode wymaga AD7606B i zworek OS = 111; hardware mode ustawia ±10 V na wszystkich kanałach i czyta ośmioma ramkami. Każdy zapis rejestru jest weryfikowany odczytem, a **niepowodzenie jest błędem**: blokuje TEST przez nowy fault `ADC_CONFIG` i trafia do każdego rekordu jako `adc_config_ok: false`. Do przeliczeń służą wyłącznie zakresy **potwierdzone przez sprzęt**, nie żądane przez profil.

**F05 — zmiana kierunku mogła odblokować PWM mimo błędu I²C.** v2 zapamiętywała nowy znak przed potwierdzeniem zapisu do ekspandera, a `board_mode()` zerowała port, nie kasując zapamiętanego kierunku.

W v3 `board_drive()` aktualizuje stan **dopiero po potwierdzonym zapisie**, a nieudany zapis ustawia `drive_ok = false`, co kończy próbę faultem `DRIVE_IO`. Wyzerowanie portu w `board_mode()` kasuje też kierunek i odlicza przerwę od nowa.

**F06 — kalibracja nie docierała do analizy plików. To był najgroźniejszy błąd v2**, bo nie powodował awarii, tylko wiarygodnie wyglądającą nieprawdę: kanał masy po przejściu na ±2,5 V eksportował się razy cztery, więc 20 mV wyglądało jak 80 mV — dokładnie tam, gdzie szukamy H2.

v3 zmienia format pliku. Pole `reserved` w rekordzie stało się **`config_id`**, a każda migawka konfiguracji (mapowanie pinów, bank, faktyczne zakresy, wzmocnienia, offsety, zero prądu, ważność prądu, punkty LEARN, pozycja zworki AUX, tryb i stan ADC) trafia do `events.ndjson` jako zdarzenie `config` z tym numerem. Eksporter dobiera konfigurację **per próbka**, a nie jedną na sesję. Regresję pilnuje test, który tworzy plik ze zmianą zakresu w połowie i sprawdza, że to samo napięcie fizyczne eksportuje się tak samo po obu stronach zmiany.

**F07 — konfiguracja ADC i akwizycja nie miały wspólnej synchronizacji.** v3 ma **jednego właściciela**: osobne zadanie konfiguracyjne zatrzymuje timer próbkowania, czeka na wygaszenie akwizycji, zmienia zakresy, buduje nową migawkę w nieaktywnym buforze, przestawia indeks i dopiero wtedy wznawia próbkowanie. `board_adc_ranges()` **odmawia**, dopóki akwizycja jest zgłoszona jako pracująca. Stan detektorów jest zerowany w tym samym oknie, więc nie ma już zapisu z jednego zadania i odczytu z drugiego.

**F08 — firmware v2 nie kompilował się.** W `app_main.c` był literalny koniec wiersza wewnątrz stałej znakowej. Wpadł tam przy ostatniej poprawce, już po tym, jak przestałem cokolwiek weryfikować, a testy Pythona nie dotykają kodu C.

v3 dokłada `tests/test_c_sanity.py`: sprawdza wszystkie źródła C pod kątem końca wiersza w stałych znakowych, niezamkniętych literałów i komentarzy, bilansu nawiasów, braku tabulatorów i obecności `#pragma once`. Sprawdziłem, że **wyłapuje dokładnie ten błąd z v2**. To nie zastępuje kompilatora, ale zamyka klasę błędów, która raz już przeszła.

## Naprawione błędy funkcjonalne

**F09 — podsumowania sekundowe były przycinane do niepoprawnego JSON-a.** v2 składała linię w buforze 420 B, a kolejka zdarzeń przyjmowała 254 znaki i nikt nie sprawdzał obcięcia. W v3 limit jest wspólny (`STORAGE_EVENT_MAX`), bufor podsumowania jest od niego mniejszy, każde `snprintf` sprawdza wynik, a `storage_event()` **zwraca błąd i oznacza zapis jako niezdrowy** zamiast po cichu gubić fragment. Nieudane podsumowanie zostawia w logu krótką linię `summary_dropped`.

**F10 — SoftAP nigdy nie startował, a webowy STOP nie odcinał czujnika.** Pierwsze, bo `snapshot()` w ogóle nie wypełniało informacji o wpiętym adapterze — ta siedziała w zmiennej lokalnej zadania bezpieczeństwa. Drugie, bo konsola i strona miały **dwie różne ścieżki poleceń**.

v3 publikuje stan adapterów do wspólnej struktury, politykę radia liczy zadanie bezpieczeństwa co 200 ms, a wszystkie polecenia — z konsoli i ze strony — idą przez **jeden dispatcher**, który zmienia wyjścia w jednym miejscu. STOP z telefonu robi dokładnie to samo co STOP z konsoli.

**F11 — SCOPE_TRIG kosztuje kanał oscyloskopu i nie powstaje w chwili awarii.** DHO804 nie ma osobnego wejścia wyzwalania, więc sygnał zajmuje jeden z czterech kanałów analogowych — a Konfiguracja A z procedury v3 używa wszystkich czterech. Do tego detektory `stall` i `open` z założenia czekają 200 ms i 50 ms, więc impuls jest **opóźniony względem początku zjawiska**.

Obie rzeczy są teraz zapisane w `01-projekt.md` i w `02-procedury.md`, razem z wnioskiem praktycznym: na skopie trzeba ustawić odpowiednią głębokość przed wyzwoleniem, a przy wpiętym SCOPE_TRIG rezygnujesz z jednego kanału pomiarowego — zwykle z pinu 3.

**F12 — kanał AUX.** Zworka w v2 przełączała tylko gałąź wejściową, zostawiając dolny rezystor 100 kΩ wspólny, przez co w pozycji LO mnożnik wychodził około 2,0 zamiast 1,02. Do tego `control_init` zerowało pole zakresu, czyli wybierało ±2,5 V, zostawiając wzmocnienie z pozycji HI.

W v3 `JP_AUX` jest **dwubiegunowy** i odłącza także `RB4`, profil trzyma **osobną parę współczynników dla HI i LO**, a stan startowy to spójne HI. Pozycję zworki zgłasza się komendą `aux 0` / `aux 1`, co od razu buduje nową migawkę konfiguracji.

**F13 — detektory zdarzeń.** Okno skoku `ratio` jest teraz wyrażone **w czasie (1 ms), a nie w sąsiednich próbkach** — przy 2 kS/s to dwie próbki, przy 20 kS/s dwadzieścia. Zatrzask trzyma przez pełne 250 ms niezależnie od tego, czy warunek w międzyczasie ustąpił, więc seria naprzemiennych glitchy już go nie obchodzi. Doszła **flaga ważności prądu**: przy sondach back-probe albo założonym mostku bocznikującym (`bypass 1`) kryteria `stall` i `open` milczą, zamiast zgłaszać przerwę na kanale bez informacji. Masa czujnika ma teraz **dwa progi** — zdarzenia (0,30 V) i ostrzegawczy (0,05 V) — przy czym drugi trzeba dobrać po pomiarze szumu własnego toru, bo 76 µV rozdzielczości samo z siebie nie znaczy, że 50 mV jest wykrywalne w aucie.

Jedno zastrzeżenie z F13 było nietrafione: przegląd zarzuca, że okno skoku „przy 2 kS/s to 0,5 ms, a nie deklarowane 1 ms" — dokumentacja v2 deklarowała 0,5 ms wprost i tłumaczyła, że to poprawka po v1. Sama zmiana na okno czasowe i tak jest słuszna, więc weszła.

## Dwie poprawki spoza przeglądu

**Nadzór 5V_A wrócił.** v2 usunęła go razem z oknem VPROT jako „redundancję". To był błąd z mocniejszego powodu, niż podaje przegląd: **z szyny 5V_A wyprowadzone są progi komparatora przetężeniowego oraz odniesienie INA240**. Dryf albo cichy zanik tej szyny przesuwa jedyne sprzętowe zabezpieczenie nieznanego silnika zaworu, i to bez żadnego objawu. Wracają więc drugi TLV1702 i ADR4525 jako niezależne okno 5V_A.

**Bufor zapisu wrócił do 8 MiB.** Zmniejszenie go do 1 MiB było w v2 doczepione do usunięcia pretriggera, choć to dwie osobne decyzje: bufor jest odpornością na zadławienie karty, a nie mechanizmem historii. Przy 2 kS/s 8 MiB to około 131 s zapasu zamiast 16 s. Pretrigger nadal nie wraca — historia jest w ciągłym pliku.

Przy okazji poprawione drobiazgi: limit 4 GiB FAT32 przy 2 kS/s to **około 18,4 h**, nie 18,6 h, bo doliczyć trzeba nagłówki bloków (16 B na 64 rekordy, ok. 0,8 %).

## Ostrzeżenia, które v3 dopisuje do procedur

Przegląd słusznie zwraca uwagę, że kilka wniosków było formułowanych zbyt mocno. W `02-procedury.md` doszły granice wnioskowania: **HOT-SOAK** nie „oczyszcza" zaworu, a domyślny limit 60 °C zatrzyma ruch na gorętszym korpusie, więc kampanię zaczyna się dopiero poniżej ustalonego limitu — który wyznacza się osobno, nie podnosi arbitralnie. Prąd zerwania zależy też od napięcia, fazy PWM i sprężyny, a przy 2 kS/s i PWM 1 kHz **pojedyncza próbka nie jest średnią ani wartością skuteczną**. **SUBSTITUTE LOAD** przy 14,4 V to około 1,2 A i 17 W na rezystorze (radiator obowiązkowy), nie odtwarza indukcyjności ani prądu zatrzymanego silnika, a długość okna przed zgłoszeniem błędu przez ECU trzeba sprawdzić na tym aucie. **HARNESS-ONLY** bez obciążenia słabo ujawnia podwyższoną rezystancję styku. **Korelacja z klimatyzacją** nie dowodzi przetarcia — włączenie AC zmienia też obciążenie elektryczne i mechaniczne silnika.

## Czego v3 nadal nie ma

Nie ma PCB ani Gerberów, nie ma testów EMC/ISO, nie ma kompilacji na docelowym MCU ani uruchomionych testów logiki w C — w tym środowisku nadal nie ma ani ESP-IDF, ani kompilatora C. Adresy rejestrów AD7606B pozostają do zweryfikowania z datasheetem; różnica względem v2 jest taka, że teraz **niezgodność blokuje TEST i jest widoczna w każdym rekordzie**, zamiast po cichu przestawiać skalę.
