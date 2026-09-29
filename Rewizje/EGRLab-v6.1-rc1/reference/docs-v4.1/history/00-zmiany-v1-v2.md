# Co się zmieniło między v1 a v2

**v2 zastępuje EGRLab-v1 rewizja A.** Katalog `EGRLab-v1/` zostaje nietknięty jako punkt odniesienia — nie buduj z niego.

Powód rewizji: v1 był projektowany jako uniwersalny tester zaworu EGR. v2 jest projektowany pod jedną konkretną kampanię — przerywany **P0404** w Kii Sportage SL 2013 (D4FD, EDC17C08), z hipotezami H1–H7 opisanymi w `../docs/01-overview.md` — i pod dwa realne scenariusze użycia: **rejestracja w jadącym aucie** oraz **sterowanie zaworem przy zgaszonym silniku**, bez demontażu zaworu.

## Zmiany merytoryczne

**1. Pinout 4/5/6 przestał być założeniem.** v1 miał zaszyte „pin 4 = feedback", co jest sprzeczne z pinoutem CUD87 wyprowadzonym ze schematu Monolith (`../docs/02-learnings-and-tools.md`: pin 4 = 5 V, pin 5 = wiper, pin 6 = masa). Przy pinoucie ze schematu procedura IDENTIFY z v1 nigdy by się nie zakwalifikowała i TEST zostałby zablokowany na stałe. W v2 IDENTIFY sprawdza **wszystkie sześć permutacji** trójki 4/5/6 i wymaga, żeby dokładnie jedna spełniała kryteria. Mapowanie kanałów jest polem profilu, nie stałą w kodzie. Piny 1/3 jako napęd pozostają założeniem — oba źródła są tu zgodne.

**2. Ósmy kanał ADC jest wolny — kanał AUX.** v1 marnował jeden kanał na prąd nieaktywnego banku. W v2 prąd jest multipleksowany razem z odczepami, a zwolniony kanał to zewnętrzny odczep pomiarowy. W LOGGER wpinasz go w **linię ECV klimatyzacji (H7)** albo w **punkt masowy GUD09 względem minusa akumulatora (H2)**. To jedyna przewaga tego urządzenia nad DHO804, której skop nie dogoni: siedem sygnałów EGR plus ósmy punkt odniesienia, wspólnie próbkowane, przez wiele godzin.

**3. ADC w software mode, zakres per kanał.** Masa czujnika dostaje ±2,5 V (76 µV/LSB zamiast 311 µV/LSB), czyli pomiar spadku na masie z Kroku 2 procedury v3 robi się sensowny. Przy okazji znika ryzyko przepustowości: jedna ramka 128-bit zamiast ośmiu po 16 bitów. Sterownik weryfikuje konfigurację odczytem rejestrów i **przy niezgodności sam wraca do hardware mode**, więc tańsza płytka z AD7606 (bez B) też zadziała, tylko z gorszą rozdzielczością na masie.

**4. Nowe tryby pod tę kampanię.** **HOT-SOAK** — po przejeździe gasisz silnik, wypinasz zawór z wiązki, wpinasz tester i on sam co kilka minut robi rampę oporów ruchu w obu kierunkach, zapisując prąd zerwania i czas przejścia razem z temperaturą, dopóki silnik stygnie. To jest test uszyty pod definicję P0404 z GDS („aktuator zablokowany, wysoka temperatura silnika aktuatora") i nie wymaga demontażu zaworu ani czekania na 35°C. **SUBSTITUTE LOAD** — rezystor 12 Ω zamiast zaworu, żeby zobaczyć, co ECU naprawdę wystawia w znane obciążenie. **HARNESS-ONLY** — pomiar na wypiętej wiązce, bez obciążenia, przy wyginaniu.

**5. Triggery i wyjście na skop.** Firmware sam oznacza w logu podejrzane zdarzenia (referencja poza 4,5–5,5 V, masa powyżej progu, skok ratio, prąd rosnący bez ruchu, napęd obecny bez prądu) i do tego wystawia impuls na **SCOPE_TRIG** — wpinasz to w wejście wyzwalania DHO804 i skop łapie pełnopasmowy przebieg dokładnie w momencie, który wykrył rejestrator. Dodatkowo raz na sekundę idzie do logu podsumowanie min/max/średnia z każdego kanału, żeby 18-godzinny plik dało się przejrzeć.

**6. Mniej do zlutowania.** Sygnały nadzoru są zwarte w jeden węzeł **wire-AND** na jednym pull-upie zamiast kaskady sześciu układów 74HC08; jeden bank przekaźników pomiarowych zamiast dwóch (adaptery i tak są fizycznie wyłączne); okno napięciowe VPROT, ADR4525, TLV1704 i dwa z trzech supervisorów wypadły, bo ich funkcję pełni firmware plus własne zabezpieczenia VNH5019 i TSR-ów; LM74800EVM-CD zszedł do opcji, a bazowo jest bezpiecznik + TVS + P-MOS. Z ~9 układów logiki i nadzoru zostały 4, z 8 przekaźników — 5.

**7. Kalibracja per bank.** v1 miał jedną tablicę gain/offset na dwa różne tory i sam to zgłaszał jako otwarty problem. v2 ma `gain[2][8]`, `offset[2][8]` i `current_zero[2]`, wybierane bankiem.

**8. Ring i pretrigger wyleciały.** Przy 2 kS/s ciągły plik i tak mieści 18,6 h do limitu FAT32, więc pretrigger niczego nie ratował, a dokładał jedyne ryzyko utraty danych wymienione w v1. Został prosty bufor zapisu 1 MiB i ciągły plik.

**9. Sterowanie z telefonu (opcjonalne).** SoftAP z prostą stroną: żywa pozycja, prąd i napięcie, przyciski OPEN/CLOSE/GOTO/SWEEP/STOP. Włącza się **tylko poza trybem LOGGER** — wejście w LOGGER wyłącza radio, żeby nie zakłócać pomiaru i nie wnosić jittera. Fizyczny ARM obowiązuje tak samo: telefon nie ruszy zaworem, jeśli nie trzymasz uzbrojenia sprzętowo.

**10. Poprawki błędów z przeglądu v1.** Zero prądu przestało być zaszytą stałą 2,5 V i jest mierzone oraz trzymane w profilu (przy REF = 5V/2 błąd szyny ±2% to było ±0,2 A przy soft-limicie 1,5 A). `status` pokazuje prąd z aktywnego banku, a nie zawsze z TEST. IDENTIFY ma timeout. Próg „skok ratio w 1 ms" przeliczony na liczbę próbek zamiast na czas. Domyślna częstotliwość została przy 2 kS/s, bo 20 kS/s przez `esp_timer` z dyspozycją w tasku i tak było nierealne, a do tej usterki niepotrzebne.

## Co zostało bez zmian

Sprzętowy latch ARM bez automatycznego wznowienia, niezależny komparator przetężeniowy, monostabilny watchdog, pętla interlock z krańcówkami w gniazdach, odcięcie obu linii zasilania czujnika, rezystory ograniczające przy złączu EGR a nie przy elektronice, format logu z CRC per blok i trybem recovery. Dalej **nie ma emulacji EGR i nie ma zapisu czegokolwiek do ECU** — to przyrząd pomiarowy, nie obejście usterki.

## Czego v2 nadal nie ma

Nie ma PCB ani Gerberów, nie ma testów EMC/ISO, nie ma kompilacji na docelowym MCU (brak toolchainu w środowisku, w którym to powstało), nie ma potwierdzonych OEM limitów prądowych i termicznych zaworu 28410-2A850. Adresy rejestrów AD7606B w software mode są do zweryfikowania z datasheetem przed pierwszym uruchomieniem — sterownik sam się z tego wycofuje przy niezgodności, ale sprawdź je.
