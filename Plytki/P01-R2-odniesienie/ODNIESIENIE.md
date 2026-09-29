# P01-R2 — odniesienie do recenzji Opusa

23.09.2026. Przedmiot: `../P01-R2-recenzja/RECENZJA-P01-R2.md` i opublikowany `../P01-R2-review/`.

**Wniosek: poprawka R1-01 ma potwierdzenie w niezależnej recenzji i modelu. R2 można dalej rozwijać, ale przed layoutem trzeba zamknąć sposób pomiarów, dobór części i mechanikę. Krótkie zadziałanie zabezpieczenia rzeczywiście powoduje długie ponowne załączenie. Nie przyjmuję zalecenia pomiaru VGS przez podłączenie masy DHO804 do SOURCE.**

To jest ocena recenzji, nie R3 ani zatwierdzenie PCB do produkcji. Schemat, BOM, firmware, archiwum R2 i pliki Opusa pozostają niezmienione. Aktualna struktura: pakiety płytek w `EGRLab/Plytki/`, rewizje systemu w `EGRLab/Rewizje/`. P07 pozostaje wstrzymane.

## 1. Co sprawdziłem

Uruchomiłem ponownie trzy skrypty z recenzji, bez modyfikowania ich ani talii R2. Wyniki zapisano obok tego dokumentu:

| Próba | Powtórzony wynik |
|---|---|
| Podłączenie 48 V, narożnik modelu | VSG szczytowo 0,595 V |
| Wyłączenie, wolny narożnik | 64,23 µs od idealnego ENABLE |
| Wolny start | 95% VPROT po 74,3 ms |
| OVP 17→24 V | 96,698 A szczytowo; wyłączenie 77,97 µs |
| Dodany tor OK→Q6→ENABLE | wyłączenie 44,4/66,6 µs zamiast 42,9/64,3 µs |
| ENABLE wyłączone na 50 µs; obciążenie 3 W | Q1 wyłączony przez 10,38–27,31 ms |

Jest to powtórzenie obliczeń, nie drugi niezależnie opracowany model tranzystorów ani pomiar sprzętu. Kontrola tożsamości opublikowanego pakietu i rachunki pomocnicze są w `sprawdzenie.json`. Nie powtarzałem całego ERC i wszystkich kontroli pakietu: recenzent je wykonał, a w tym kroku nie zmieniam połączeń.

## 2. R2-01 — przerwa zasilania: uwaga zasadna, rekomendacja wymaga zmiany

Pominąłem w poprzedniej analizie ważną sekwencję: **krótki fault → usunięcie faultu → ponowne załączenie przy pracującej przetwornicy**. Badania zimnego startu i trwałego wyłączenia nie zastępują tego scenariusza.

R21∥R22 z C6 daje około 82,46 ms. Po rozładowaniu C6 przez Q2 ponowne otwarcie Q1 trwa w modelu 10–27 ms. Energia 220 µF między 14 a 6,5 V wynosi 16,9 mJ, czyli zaledwie 5,64 ms przy poborze 3 W. Wynik Opusa odtworzyłem.

Trzeba jednak rozróżnić wynik modelu od zachowania gotowego urządzenia. 6,5 V jest założonym progiem odłączenia modelowego odbiornika. Nie jest zmierzonym progiem UVLO P02. Faktyczny restart zależy od poboru, pojemności, przetwornic i zasilania CORE. Nie wpisywałbym zatem jako pewnika „każde zadziałanie powyżej kilkudziesięciu µs restartuje system”.

**Dla finalnego LOGGER-a nie rekomenduję domyślnego pogodzenia się z restartem.** Rejestrator ma wychwytywać również przyczyny pozornych usterek EGR. Przerwa może usunąć właśnie interesujący zapis. W bieżącym firmware `Rewizje/EGRLab-v6.1-rc1/firmware/main/storage.c` okresowy `fflush/fsync` jest wykonywany co około 2 s. PSRAM jest ulotna, a częstszy sync nie zapewnia odporności karty SD na odcięcie zasilania. W kodzie `main/` nie znalazłem też rejestracji `esp_reset_reason`. Po całkowitym zaniku zasilania sam powód resetu MCU nie pozwala stwierdzić, że przyczyną było konkretnie OVP.

Proponuję zachować funkcję ochronną P01, a krótkie podtrzymanie opracować w **P02, wyłącznie dla gałęzi pomiarowej i zapisu**. Trzeba objąć nim potrzebne ADC, referencje i interfejsy, albo oznaczać przerwę ważności próbek. Samo podtrzymanie ESP nie wystarczy. Silnik i KPWR nadal mają się wyłączyć, a ponowny ruch wymagać ARM. Pojemność podtrzymująca musi mieć kontrolowane ładowanie i odseparowanie: nie wolno po prostu dołożyć jej do VPROT ponad przyjęte 220 µF.

To rekomendacja architektury do rozstrzygnięcia, nie gotowy obwód P02. Podtrzymanie krótkiego faultu nie oznacza automatycznie podtrzymania podczas całego rozruchu silnika. P01 można uruchamiać samodzielnie z udokumentowaną przerwą, lecz ograniczenia nie należy przenosić bez decyzji na docelowy LOGGER.

## 3. R2-02 — metrologia: problem rzeczywisty, wyjątek dla powerbanku odrzucony

Zgadzam się, że obecny protokół wymaga lepszego określenia sprzętu i niepewności. **Rozdzielczość 0,1 V nie jest niepewnością 0,1 V.** DHO800 ma dokładność wzmocnienia odniesioną do pełnej skali; dochodzą błędy offsetu, sond i odejmowania kanałów. Podane przez Opusa 1% napięcia wspólnego jest ilustracją, nie kompletnym budżetem. Odejmowanie A−B można rozważyć po sprawdzeniu konkretnego zestawu, ale nie daje ono automatycznie miarodajnego PASS przy 0,5 V. [Specyfikacja Rigola, Vertical System](https://www.rigol.com/dam/global/downloads/brochures/en/data-sheet/oscilloscopes/DHO800_DataSheet_EN.pdf).

**Nie dodawać wyjątku „powerbank pozwala podłączyć masę sondy do SOURCE”.** Instrukcja DHO800, rozdział 1.1, określa przyrząd jako nieizolowany i zabrania pomiarów pływających bez sond izolowanych. Uziemienie należy wykonać oddzielnym przewodem; samo zasilanie USB-C, także z zasilacza, nie zapewnia uziemienia. Izolująca podstawka i odłączony LAN nie zastępują właściwego toru pomiarowego. [Rigol DHO800 User Guide, §1.1](https://download.rigol.com/en/Manual/Digital%20Oscilloscope/DHO800/DHO800_UserGuide_EN.pdf). Kopię dokumentu i tekst przeszukiwalny zachowano w `zrodla/`.

Rekomendowany kierunek: sonda różnicowa o odpowiednim zakresie napięcia wspólnego i sprawdzonej niepewności dla małego VGS, ewentualnie osobno zaprojektowany i zweryfikowany przyrząd pomiarowy. Dowolna sonda wysokonapięciowa 100:1 nie rozwiązuje automatycznie problemu dokładności. Sprzęt można pożyczyć na odbiór; nie musi stale należeć do EGRLab.

Pozostałe propozycje rozdzielam:

- **ΔVPROT** jest dobrym kryterium funkcjonalnym. Jednak 0,1 V × 220 µF = 22 µC, a nie wymagane wcześniej 10 µC. Pomiar mówi o przyroście ładunku kondensatora netto, zależnym również od innych gałęzi i tolerancji pojemności. Nie wolno ogłosić tych kryteriów równoważnymi. Zmiana kryterium wymaga jawnej korekty wymagania, nie tylko zmiany metody pomiaru.
- **ID≈C·dV/dt+V/R** przyda się do oszacowania wolnego startu z rezystorem obciążającym. Przy szybkim zdarzeniu trzeba uwzględnić także prąd D3, C5, pozostałych odbiorników, ESR i błąd różniczkowania. To nie zastępuje pomiaru prądu impulsowego i pełnej oceny SOA.
- **Dostęp do gałęzi Q1:** polecam przewidzieć rozłączalny mostek mocy między drenem Q1 a całym VPROT oraz pady Kelvina pod tymczasowy bocznik. Normalnie mostek ma małą rezystancję; jego wykonanie musi przenosić impulsy, nie tylko 5 A DC. Bocznik dobiera się do próby i sprawdza jego wpływ. To mała, użyteczna zmiana prototypu przed layoutem. Nadal potrzebny jest właściwy pomiar różnicowy bocznika po stronie wysokiej.

## 4. R2-03, R2-04, R2-05

| Uwaga | Ocena i działanie przed layoutem |
|---|---|
| R2-03 — BAT | Przyjmuję: żeński Phoenix 1757019 po stronie źródła za bezpiecznikiem, męski 1786174 po stronie H_BAT. Zmiana wiązki i opisów, bez zmiany PCB. Osłony opisane w R2 nadal są przydatne. |
| R2-04 — C6 | Potwierdzam problem wskazanej oferty: strona TME pokazuje brak stanu, wielokrotność 1000 i pierwszy próg cenowy 4000 szt. Przed zamrożeniem footprintu trzeba wybrać realnie kupowalny pojedynczo kondensator. |
| R2-05 — J7 | Przyjmuję potrzebę termików albo świadomie zaplanowanego podgrzewania. Stwierdzenie, że pad na pewno nie da się polutować, jest zbyt kategoryczne — zależy od grotu, mocy i pola miedzi. Szprychy trzeba dobrać do prądu i wykonania 70 µm. TP1/TP2 umieścić bezpośrednio przy S/G Q1. |

Dane C6: [TME B32529D1105J000](https://www.tme.eu/en/details/b32529d1105j000/tht-film-capacitors/tdk/), sprawdzone 23.09.2026; dostępność może się zmienić. Dopuszczenie ±10% wygląda rozsądnie: rachunek podłączenia daje około 0,683 V. **Nie jest to jeszcze pełne zatwierdzenie zamiennika** — większe C6 wydłuża wyłączenie i restart. Po wyborze części trzeba powtórzyć narożniki dla jej rzeczywistej tolerancji oraz sprawdzić gabaryty i wyprowadzenia.

## 5. Dwa wnioski recenzji, których nie rozszerzam na gwarancję

**Detektor i integracja:** rozszerzony model toru ENABLE jest przydatny i mieści się w budżecie czasu. Nadal nie ma gwarantowanego modelu opóźnienia LM2903 i magazynowania ładunku konkretnych tranzystorów. Typowego czasu komparatora nie traktuję jako maksimum w całym zakresie warunków. Nadzorca 5V_SYS w P02 pomaga w sekwencji startu, ale trzeba wspólnie zmierzyć VPROT, szyny logiki, PSU_OK, SAFE_N i ARM, także z USB. Prawidłowe 5 V nie dowodzi samo w sobie, że Q1 zakończył przejście.

**Impuls OVP i D3:** zgadzam się, że 96,7 A zależy od założonego źródła i nie jest samoistnym dowodem wady. Nie zamykam jednak SOA na podstawie 1,4 mJ uproszczonego modelu. D3 nie jest idealnym ogranicznikiem 21 V: dla 5KP18A producent podaje VBR 20–22,1 V przy 5 mA oraz VC maks. 29,2 V przy 174,7 A. Nie gwarantuje to 21 V przy 40 A. Włączenie D3 do modelu zmienia prąd Q1 i D2, temperaturę i energię; nie tylko ogranicza ładowanie kondensatora. [Littelfuse 5KP, tabela parametrów](https://www.littelfuse.com/assetdocs/littelfuse_tvs_diode_5kp_datasheet.pdf?assetguid=b1ddd6a2-fccb-4327-bea1-7d77c0793479).

Pierwsze próby powinny mieć ograniczoną energię. Jeżeli jednak zasilacz ogranicza prąd i deformuje zadany skok, trzeba zmierzyć faktyczne VIN/VS i oznaczyć test jako inny bodziec. Taka próba nie potwierdza automatycznie odporności na szybki skok ani impuls samochodowy. H-01, SOA i termika pozostają otwarte.

## 6. Co dopisać do procesu

1. Do macierzy stanów dodać **powrót po usterce**, serie krótkich faultów oraz model pracującej przetwornicy, nie tylko rezystor. Sprawdzać jednocześnie ochronę mocy i ciągłość rejestracji.
2. Przed zatwierdzeniem kryterium odbioru określić **metodę, dostępne punkty pomiarowe i niepewność**. Sprawdzić instrukcję przyrządu, nie wyłącznie zakres napięcia.
3. Dla każdej zmiany RC lub tolerancji wykonać regresję: podłączenie, start, wyłączenie, powrót, kolejne impulsy. Zachować wynik R1 jako test wykrywający znany błąd.
4. Przed layoutem potwierdzić **zakup 1–5 sztuk**, footprint, chłodzenie i lutowanie. Sam numer katalogowy istniejącej części nie zamyka B-01.

## 7. Rekomendowana kolejność

Najpierw zamknąć zakres podtrzymania LOGGER-a na styku P01/P02 i metodę pomiaru VGS/prądu. Następnie dobrać dostępne C6 i radiatory, odwrócić strony złącza BAT oraz dodać dostęp do pomiaru gałęzi Q1. Dopiero wtedy wydać jedną, ograniczoną poprawkę przed layoutem z testami zmienionych elementów. Nie proponuję ponownego przepisywania całego EGRLab.

Recenzja E-02 została otrzymana i przeanalizowana. R1-01: sprawdzone niezależnie w analizie/modelu, jeszcze bez odbioru sprzętu. R1-02: wymaga korekty metody pomiarowej. M-01, B-01 i H-01 pozostają otwarte. Ten dokument nie wydaje zgody na zamówienie PCB.
