# Budowa, odbiór i logistyka

Plan jest podzielony na **wieczory**: każdy etap ma zamknięty zakres, własne kryterium i nadaje się do odłożenia narzędzi bez niedokończonego węzła na stole. Kryteria są planem pomiarów, nie deklaracją, że coś już przeszło.

Posiadana płytka Waveshare N32R16-M wystarcza. Nie kupuj innego MCU — wymiana procesora nie usunęłaby ani potrzeby porządnego front-endu, ani kwalifikacji SPI i SD, ani niezależnych zabezpieczeń.

## Kolejność wieczorów

| # | Wieczór | Robisz | Kryterium przejścia |
|---|---|---|---|
| 0 | inwentaryzacja | oznaczenie modułu, odczyt nadruku WROOM-2-N32R16V, rewizja płytki, ciągłość do modułu | numeracja GPIO zgodna z Twoją rewizją, nie z cudzą |
| 1 | sam ESP | USB, konsola, PSRAM, pusty firmware | boot bez błędów, rozpoznane 16 MiB PSRAM, MCU_ARM = 0 |
| 2 | zasilanie | F1, TVS, P-MOS, oba TSR-y, bez MCU i bez mostka | 5 V i 3,3 V w tolerancji, brak grzania, prąd jałowy zmierzony |
| 3 | próby zasilania | odwrotna polaryzacja, zapady, powrót napięcia | brak uszkodzenia; po powrocie latch zostaje rozbrojony |
| 4 | bezpieczeństwo | latch, watchdog przez 2N7002, okno prądu, **okno 5V_A**, supervisor 3V3, wire-AND, sześć bramek AND, przyciski | każdy sygnał osobno zdejmuje PERMIT; ustąpienie błędu nie uzbraja; **przerwany przewód grzybka = STOP** |
| 5 | ADC i bank pomiarowy | AD7606B, przekaźniki K_MEAS i KCUR, dzielniki, AUX w obu pozycjach | osiem **różnych** napięć na ośmiu kanałach; tryb ADC potwierdzony odczytem rejestrów; zmierzony **szum własny kanału masy** |
| 6 | prąd | boczniki, INA240, multiplekser banku, obciążenie rezystancyjne | oba znaki prądu, offset zmierzony, dynamiczne wyłączenie OC |
| 7 | zapis i peryferia | SD, CAN stanowiskowy, dwie termopary, SCOPE_TRIG | 30 min bez utraty danych; CAN w listen nie wystawia ACK; impuls na BNC widoczny na skopie |
| 8 | mostek | VNH5019 na rezystorze 12 Ohm/25 W, potem na małym silniku | poprawny znak U oraz I, bezpieczny STOP, brak przepięć szyny ponad projekt |
| 9 | symulator czujnika | dzielnik 5 V z potencjometrem jako atrapa czujnika | rozpoznaje wszystkie sześć permutacji, odrzuca niestabilne dane, zwarcie odczepu ograniczone |
| 10 | adaptery | wykonanie L1, L2 i T po identyfikacji obudów OEM | ciągłość, brak odbicia lustrzanego, krańcówki i pętla TEST_PRESENT działają |
| 11 | kalibracja | źródło wzorcowe, oba banki osobno, AUX w HI i LO osobno | sensor ≤ 10 mV, napęd ≤ 1 %, prąd ≤ 2 % używanego zakresu |
| 11b | zgodność logu | zmiana zakresu, banku, `zero` i `aux` w trakcie sesji | **eksport daje to samo napięcie fizyczne po obu stronach każdej zmiany** |
| 12 | pierwszy zawór na stole | zdjęty egzemplarz, limity rozruchowe | ruch i kierunek potwierdzone wzrokowo, LEARN zapisany |
| 13 | procedury | SWEEP, FRICTION, CYCLE, THERMAL na zdjętych egzemplarzach | powtarzalny zakres bez dociskania do ograniczników |
| 14 | opcjonalnie | SoftAP i strona na telefon | radio nie startuje w LOGGER, STOP działa z telefonu, ARM nadal wymagany |

Wieczory 0–9 i 11–14 robisz **w Polsce, bez samochodu** — to jest ta część, którą chciałeś mieć na wieczory. Wieczór 10 wymaga dostępu do złącza w aucie albo do wypiętego zaworu, żeby zidentyfikować obudowy.

## Etapy przy samochodzie (Hiszpania)

| # | Etap | Kryterium |
|---|---|---|
| A | LOGGER L2, back-probe, bez ruszania CUD87 | komplet ośmiu kanałów, w tym AUX; sesja ≥ 30 min bez GAP |
| B | HARNESS-ONLY przy wyginaniu wiązki | zdarzenia powtarzalne 3–5× albo czysto |
| C | LOGGER L1 z prądem, po porównaniu bypass/shunt | brak nowych DTC po założeniu adaptera |
| D | HOT-SOAK po przejeździe, zawór na silniku | co najmniej 8 punktów w zakresie temperatur |
| E | SUBSTITUTE LOAD, na koniec dnia | zarejestrowane okno przed zgłoszeniem błędu przez ECU |
| F | LOGGER podczas objawu | kompletne okno przed i po, freeze-frame zapisany |

## Zanim zaczniesz lutować

Dwie rzeczy, których v2 nie miała i przez które dwa wieczory poszłyby w błoto:

**Narysuj schemat z numerami nóżek.** `hardware/connections.csv` opisuje sygnały i przypisanie bramek (U10a–U10d, U12a–U12b), ale nóżki konkretnych obudów dobierasz z datasheetów zamówionych wariantów. Szczególnie: węzeł `SAFE_N` wolno łączyć **tylko z wyjściami otwartymi** — jedyne wyjście push-pull w tym torze, watchdog 74HC123, ma przejść przez inwerter i tranzystor 2N7002. Wpięcie tam bramki AND to zwarcie przy każdym aktywnym błędzie.

**Uruchom testy logiki na PC.** Jeden wieczór, zero sprzętu:

```bash
gcc -std=c11 -I firmware/main -o test_control tests/test_control.c firmware/main/control.c -lm
./test_control
python -m unittest discover -s tests -p "test_*.py" -v
```

Testy Pythona przechodzą w tym pakiecie; testów C **nie uruchomiono**, bo w środowisku, w którym powstał, nie ma kompilatora. Zrób to, zanim weźmiesz lutownicę.

## Odbiór niezależności zabezpieczeń

Tego nie da się zastąpić przeglądem schematu. Osiem prób, każda z zapisanym wynikiem:

1. Odłącz MCU i wymuś PWM = HIGH. Bez fizycznego ARM napęd zostaje wyłączony.
2. Zatrzymaj task bezpieczeństwa przy aktywnym PWM. Monostabilny zdejmuje zezwolenie w 50–150 ms; komparator prądu działa niezależnie i znacznie szybciej.
3. Wstrzyknij do I_FILT napięcie poniżej LOW i powyżej HIGH. Zmierz PWM_OUT oraz ENA/ENB. Cel: poniżej 20 µs od utrzymanego przekroczenia. Sprawdź oba znaki i kilka temperatur.
4. Włóż wtyk LOGGER podczas TEST na sztucznym obciążeniu. PERMIT znika; żadne wyjście ECU nie dostaje napięcia mostka.
5. Odłącz BUSY, zatrzymaj I²C, wyjmij kartę SD — ruch ustaje, a fabryczny tor LOGGER pozostaje połączony.
6. Przytrzymaj ARM przed włączeniem zasilania. Po ustąpieniu resetu nie może pojawić się nowe zbocze uzbrajające. Sprawdź debounce.
7. Sprawdź ciągłość TEST–LOGGER we wszystkich położeniach przekaźników. Zmierz resztkową drogę przy obu adapterach wpiętych naraz i porównaj z obliczonymi ~8 µA. **Wspólnej masy nie nazywaj izolacją galwaniczną.**
8. Przerwij każdą linię nadzoru i zasilanie każdego bloku osobno; udokumentuj zachowanie. Projekt nie deklaruje odporności na dowolną pojedynczą awarię.
9. **Przerwij przewód grzybka E-STOP.** Węzeł SAFE_N ma opaść — jedyny pull-up idzie przez ten styk. Sprawdź to miernikiem, nie rozumowaniem.
10. **Wymuś błąd I²C w trakcie ruchu** (rozepnij SDA na chwilę). Napęd ma stanąć z faultem `DRIVE_IO`, a nie jechać poprzednim kierunkiem.
11. **Zepsuj konfigurację ADC** (rozepnij SDI albo zmień zworki OS). Urządzenie ma odmówić TEST z faultem `ADC_CONFIG`, a w logu ma się pojawić `adc_config_ok: false` — nie wolno mu przeliczać próbek dalej.
12. **STOP z telefonu i STOP z konsoli** mają dać identyczny stan wyjść, łącznie z odcięciem K_SENSOR. Sprawdź miernikiem na pinach czujnika.
13. **Wyjmij adapter TEST w trakcie ruchu.** PERMIT znika, radio gaśnie, stan idzie w FAULT.

## Kalibracja

Źródło i miernik odniesienia. Punkty: czujnik 0 / 0,5 / 2,5 / 5 V; napęd i VBAT 0 / 5 / 12 / 16 V oraz −5 V, jeśli źródło pozwala; prąd 0, ±0,5, ±1, ±2 A. **Zapisuj wskazania miernika, nie nastawy zasilacza.**

Kalibrujesz osobno dla każdego banku — profil ma `gain[2][8]`, `offset[2][8]` i `current_zero[2]`. Jedno dopasowanie nie przechodzi na drugi tor, bo rezystory ograniczające siedzą przy złączach adapterów, a nie na płytce.

Kalibrujesz osobno **każdą pozycję zworki AUX** — to dwa różne dzielniki, nie jeden z przełączanym zakresem.

Nominalny LSB zależy od zakresu kanału:

| Zakres | LSB na wejściu ADC | Po dzielniku czujnika (×1,02) | Po dzielniku napędu (×4,06) |
|---|---|---|---|
| ±10 V | 305 µV | 311 µV | 1,24 mV |
| ±5 V | 153 µV | 156 µV | 620 µV |
| ±2,5 V | 76 µV | 78 µV | 310 µV |

**Rozdzielczość to nie wykrywalność.** Zanim ustawisz próg ostrzegawczy na masie czujnika (domyślnie 0,05 V), zmierz szum własny tego kanału przy zwartym wejściu i przy realnie podłączonej wiązce — 76 µV na działkę nie znaczy, że 50 mV wyjdzie z tła w aucie. Próg wpisuje się po pomiarze, nie z katalogu.

Rozdzielczość to nie dokładność. Dolicz R_IN przetwornika, tolerancje rezystorów, offset, błąd wzmocnienia, bocznik z jego TCR, masę i temperaturę. Cele po kalibracji: czujnik ≤ 10 mV, napęd ≤ 1 %, prąd ≤ 2 % używanego zakresu. Jeśli ich nie osiągasz — zapisz rzeczywisty błąd i nie wyciągaj wniosków o zmianach mniejszych niż on.

**Zero prądu** mierzysz osobno, po rozgrzaniu toru, przy pewnym zerowym prądzie, i wpisujesz do profilu. To nie jest 2,5 V z założenia.

## Przepustowość

Startuj od **2 kS/s** i sprawdź osiem różnych napięć na ośmiu kanałach — to wykrywa błędne powtarzanie kanału przy złej ramce SPI, klasyczny objaw pomylenia trybu hardware z software.

2 kS/s to w tej kampanii **wystarczająco dużo**: szukasz zdarzeń milisekundowych i wolnych korelacji z temperaturą i klimatyzacją, a P0404 wymaga 4,4 s zablokowanego aktuatora. Do kształtu impulsu PWM i tak potrzebujesz skopu, i po to jest SCOPE_TRIG.

Jeśli mimo to chcesz wyżej: w software mode odczyt to jedna transakcja 128-bit, więc wąskim gardłem przestaje być ramkowanie, a zaczyna dyspozycja timera. `esp_timer` z dyspozycją w tasku nie da stabilnych 50 µs — powyżej ok. 5 kS/s trzeba przejść na timer sprzętowy z przerwaniem i kolejką DMA. **Nie obiecuję 20 kS/s** i firmware tego nie deklaruje.

Kryterium pomiaru: zero GAP, zero błędów CRC, zmierzony jitter i raport `max_dt` przy jednoczesnym zapisie SD, CAN i termopar przez minimum 30 minut.

## Zakupy i logistyka

Części kupujesz w Polsce; do Hiszpanii idzie InPost. Rozdziel listę na trzy paczki:

**Paczka 1 — elektronika (wieczory 1–9).** AD7606B albo gotowa płytka z tym układem, MCP23017, INA240A2 ×2, TLV1702, TPS3808, 74HC74/123/14/08, moduł Pololu 1451, TSR 2-2450 i 2-2433, MAX31856 ×2, TCAN1051V, przekaźniki sygnałowe, boczniki 4-terminal, rezystory precyzyjne 0,1 %, kondensatory, płytki uniwersalne, adapter LQFP-64 jeśli kupujesz goły układ.

**Paczka 2 — mechanika i wiązki (wieczór 10).** Obudowa, przepusty, grzybek E-STOP, przyciski, przełącznik kluczykowy, krańcówki, złącza 12- i 8-stykowe, przewody 1,5 mm² i 0,5 mm², tulejki, opaski, termopary typu K z przewodem kompensacyjnym, gniazdo BNC na SCOPE_TRIG, rezystor 12 Ohm/25 W.

**Paczka 3 — złącza OEM.** Kupujesz **dopiero po identyfikacji** obudowy CUD87 z fotografii oznaczeń i pomiaru. Numer części zaworu nie identyfikuje pewnie obudowy złącza, a kupienie „czegoś podobnego" kończy się drugim zamówieniem.

**Ryanair, bagaż kabinowy.** Zmontowane urządzenie w bagażu podręcznym: sondy back-probe mają ostre końcówki — spakuj je w twardym etui, a jeśli masz wątpliwości, wyślij InPostem razem z paczką 2. Akumulator power banku do skopu zawsze w kabinie, nigdy w luku. Zasilacz laboratoryjny zostaje w Polsce; w aucie zasilasz się z akumulatora przez bezpiecznik 10 A.

## Co nadal wymaga rzeczywistego sprzętu

* Decyzja o trybie ADC: AD7606B ze zworkami OS = 111 (software mode) albo zwykły AD7606 na ±10 V. Wybierasz w `menuconfig` przed kompilacją.
* Identyfikacja obudów złączy OEM i rewizji płytki Waveshare.
* Weryfikacja adresów i bitów rejestrów AD7606B w software mode z datasheetem Twojej rewizji.
* Layout, temperatury, przepięcia regeneracyjne, EMC i impulsy automotive.
* Kompilacja ESP-IDF, próby integracyjne, pomiar jittera i opóźnień SD.
* Profil konkretnego zaworu: mapowanie pinów, punkty pozycji, prądy, czasy, temperatury.

W pakiecie są schematy blokowe i połączeniowe oraz BOM — **nie ma routowanej PCB ani Gerberów**. Źródła firmware mają `EGR_HARDWARE_ACCEPTED = 0` w `commissioning.h` i wyłączone `CONFIG_EGR_ACTIVE_TEST`. Oba przestawiasz dopiero po odbiorze i po wpisaniu **zmierzonych** współczynników kalibracji. To nie zastępuje fizycznego ARM.
