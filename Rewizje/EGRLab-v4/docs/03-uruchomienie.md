# Uruchomienie etapami i kryteria odbioru

Wyniki wpisuj w `verification/ODBIOR.md`. Żadna wartość nominalna ani test na PC nie zastępuje pomiaru na egzemplarzu. Przed etapem TEST `EGR_HARDWARE_ACCEPTED=0`. Podczas montażu ECU i zawór odłączone.

| Etap | Budujesz / sprawdzasz | Warunek przejścia |
|---:|---|---|
|0|Złącza OEM i panelowe, listwy GPIO, rezystory przy sondach|ciągłość pin po pinie; brak pomyłek widoku; T/L1/L2 niezamienne; mapa12pin T|
|1|Waveshare na stole, właściwa konfiguracja Flash/PSRAM|boot,32MB/16MB zgodne z nadrukiem, test PSRAM, stabilny UART|
|2|F1, TVS, **LM74800 OVP**, TSR, obciążenia zamiast elektroniki|OVP17,5–18,5V, próg powrotu,5V/3,3V, prąd/temperatura; brak cofania z USB|
|3|Logika/MCP, bez motoru|kolejność zasilania, brak zasilania pasożytniczego; wyjścia po resecie niskie; B4/B5 zgodne z wtykami|
|4|STOP, watchdog, latch, interlock, okna OC/5V_A|każdy błąd kasuje HW_ARMED; ustąpienie nie uzbraja; nowe zboczeARM; timeout50–150ms|
|5|ADC, KMEAS, AUX, źródło wzorcowe|identyfikacja kanałów; zakresy/znaki;5,8V supply widoczne bez clippingu; saturacja jawna|
|6|INA/KCUR/shunty, wzorcowy prąd, motor jeszcze odłączony|oba banki i znaki; zero świeże; prógOC i czasPWM/EN low zmierzone|
|7|SD, TC, CAN na stole|długie logi, CRC, rotacja, weryfikacja temperaturefault/null; CAN tylko słucha|
|8|Mostek i12Ω/25W na radiatorze|kierunki,5ms deadtime od zakończeniaI²C, STOP przy blokadzieI²C/SD; VMOTOR rozładowanie|
|9|Sensor z limitem zewnętrznym20mA, bez motoru|znana polaryzacja; KSENSOR rozłącza obie linie; TPS2553 limit zmierzony|
|10|L2 w aucie|brak zmiany sygnału po dołączeniu; IDENTIFY jednoznaczne; radioOFF|
|11|L1 w aucie, najpierw z mostkiem|wpływ przewodów/złączy zmierzony; właściwy znakINA i bypass|
|12|Zawór w TEST, ECU odłączone|krótkie impulsy przy duty≤0,1, ograniczeniu0,5A iTC1≤60°C; kontrola ruchem fizycznym|
|13|LEARN i automatyczne testy|powtarzalność, limity, kalibracja, kwalifikacja metryki PWM lub pozostawione `metric 0`|

## Odbiór logiki przed motorami

Sprawdź wszystkie16 kombinacji key/L1/L2/loopT oraz przerwanie każdego przewodu. Dodatkowo: brak heartbeat przy starcie, pierwszy heartbeat, timeout i jego powrót, STOP przy trzymanymARM, spadek3V3_IO,5V_A poniżej4,75 i powyżej5,25V, oba znaki OC. Mierz jednocześnie SUP_N, SAFE_N, WD_Q iHW_ARMED: SAFE_N=0 nie może wymuszać SUP_N=0. Zapisz przebiegi. Zwarcie wyjść push-pull doSAFE_N jest niedopuszczalne.

## Kalibracja i jej wprowadzenie

Odłącz wszystkie adaptery LOGGER. Użyj źródła o potwierdzonej dokładności i miernika. Kalibruj bank0/1, każdy kanał, a AUX osobnoHI/LO. Dla wejść1/3/VPROT zastosuj np.0/6/12V, sensor0/2,5/5V, masa0/50/300mV, AUX LO0/50/1000mV. Dokładne poziomy muszą mieścić się w aktualnym zakresie. Przy zmianie zakresu potwierdź ciągłość wskazania, nie tylko same współczynniki.

Firmware: v=raw×FS/32768×gain+offset. Jeżeli x oznacza raw×FS/32768, to gain=(V2−V1)/(x2−x1), offset=V1−gain×x1. Sprawdź niezależny trzeci punkt. `cal BANK CH GAIN OFFSET` ma indeks kanału0…7, bank0LOGGER/1TEST. `auxcal POS GAIN OFFSET`: POS0HI/1LO. CH7 w tablicy bankowej jest nadpisywany współczynnikami AUX przy budowie konfiguracji.

`bank 0`, `zero`; potem `bank 1`, `zero`, zawsze bez wpiętego LOGGER i z pewnym zerowym prądem. Funkcja czeka na nową pełną sekundę, wymaga zgodnego config_id/banku, wszystkich ważnych próbek, rozrzutu<20mV i średniej1…4V. Wynik nie pochodzi z poprzedniego okna. Możesz użyć `currentcal BANK ZERO_V` do wprowadzenia pomiaru zewnętrznego. Polecenia są dozwolone w SAFE; `zero` także READY bez ruchu.

Przykładowa składnia, liczby zastąp własnymi:

```text
stop
cal 0 4 1.01985 -0.0012
auxcal 1 1.0201 0.0003
currentcal 0 2.5032
limits 0.1 0.5 60
metric 0
save
profile
```

Wypełnij `hardware/profile.template.json`, zachowując wersję4, i wygeneruj plik poleceń:

```text
python tools/profile_commands.py measured.json --out measured.txt
```

Wysyłaj **po jednej linii, czekając na końcowe OK**; QUEUED oznacza tylko przyjęcie do kolejki. Nie wklejaj całego pliku do małej kolejki. Konwerter nie wysyła nic do urządzenia. `null` zamiast zmierzonego zera jest odrzucane. Po `save` zrestartuj i sprawdź `profile/status`. Stary blob v3 nie jest migrowany automatycznie. Profil sprzętowy nie potwierdza osobno sprawności zaworu.

## Próby integracyjne v4

- Zablokuj/odłącz BUSY, SD iI²C przy obciążeniu zastępczym. Motor ma się wyłączyć, config nie może zostać opublikowany bez ACK. Nie wolno kontynuować testu z „domyślnym” zakresem.
- W trakcie bank/config/zero wywołaj STOP. Sprawdź brak wznowienia ruchu z zaległego polecenia. STOP sprzętowy nie zależy od responsywności taska.
- Wstrzyknij opóźnienie odczytuADC >20ms. Przełączenie przekaźników może nastąpić dopiero po ACK. PAUSE timeout500ms pozostawia błąd i wyłączony napęd.
- Nieudany zapis pierwszego, środkowego i ostatniego rejestru ADC: brak nowych próbek z rzekomo poprawną skalą; brak aktywnego TEST.
- Zmień bank przed`zero`, zadawaj różne zera obu INA, przerwij serię błędem lub STOP. Poprzednie ID/summary nie może posłużyć do nowego zera.
- Przeprowadź100 cykli AP on/off przez zmiany adaptera/stanu; brak restartu MCU i narastającego użycia pamięci. PrzyciskSTOP i wejścieUART mają działać podczas startu/stopu HTTP.
- Zapis co najmniej8h przy2000S/s, z CAN iTC; przekroczenie granicy1GiB obu typów plików. `inspect` wszystkich segmentów: brak CRC, zgodne sesje, brak nieopisanych przerw. Zasymuluj pełną kartę i wolne fsync.
- Mierz jitter/rzeczywiste odstępy próbek, straty ticków/kolejki i amplitudę/szerokość znanych impulsów. Przy przeciążeniu czasowym nie uznawaj nominalnego2kHz za gwarantowane.
- Przy PWM różnej fazy względemADC porównaj średnią20ms ze skopem. Kryterium robocze≤10% lub50mA (większa wartość), powtarzalność≤5%, obydwa kierunki. Kryterium służy porównaniom warsztatowym; jeśli nie przejdzie, `metric 0`.

Przykładowy szum masy: przy zwartych wejściach doB− wyznacz min/max/odchylenie podczas pracyPWM, SD iCAN. Alarm50mV wymaga, aby szum i dryf były wyraźnie mniejsze, roboczo<10mVpp. W przeciwnym razie popraw masy/ekranowanie lub jawnie podnieś próg; nie zmieniaj progu wyłącznie po to, by ukryć rzeczywistą usterkę.

## Odblokowanie i zakończenie

Po etapach0–11 i odbiorze na obciążeniu zastępczym: zapisz wyniki, ustaw `EGR_HARDWARE_ACCEPTED=1`, zbuduj z `CONFIG_EGR_ACTIVE_TEST=y`, pozostaw małe limity. To decyzja konstruktora oparta na jego pomiarach, nie wynik obecnych testów PC. Wi‑Fi opcjonalne, domyślnieoff. Po sesji `stop`, poczekaj≥3s na zapis przy zdrowej karcie, dopiero wyłącz zasilanie. Nie ma podtrzymania energii; nagły zanik może utracić dane z RAM/cache/SD.
