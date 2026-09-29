# Procedura diagnostyczna EGR / P0404 — v3
**Kia Sportage SL 2013 · 1.7 CRDi D4FD · Bosch EDC17C08 · ~280 tys. km · złącze EGR CUD87 (6-pin) · Rigol DHO804**

> **v3 zastępuje v2 i osobny dokument z nastawami.** To jest jedyny plik, który bierzesz do auta.
> **Co nowego:** obserwacje terenowe z wyjazdu wrześniowego (sekcja 1), nowa hipoteza **H7 — sprzężenie z obwodem AC/ECV**, przestawiona kolejność testów (test klimatyzacji na pierwszym miejscu), osobna ścieżka dla szarpania na zimno, oraz nastawy DHO804 wpisane wprost w każdy krok.
>
> **Uwaga po przeniesieniu (2026-09-21):** po powstaniu v3 ustalono z manuala GDS (D4FD), że P0404 oznacza aktuator zablokowany otwarty/zamknięty >4 s, z progiem wysokiej temperatury silnika aktuatora; przyczyna wg GDS: obwód silnika aktuatora. To podnosi wagę Kroku 5 (H-bridge) i H5 — kandydat do przestawienia kolejności w v4.

---

## 1. OBSERWACJE Z TERENU — przeczytaj to pierwsze

Dane z 7-dniowego wyjazdu (wrzesień 2026), 100–300 km dziennie, mieszana jazda miejska i autostradowa.

### Obserwacja 1 — P0404 zależy od temperatury otoczenia
- **Wyjazd wrześniowy:** 7 dni codziennej jazdy, **jedno** wystąpienie P0404 — w najcieplejszy dzień, ok. **35°C**. W pozostałe, chłodniejsze dni: ani razu.
- **Lipiec/sierpień:** przy **35–42°C** błąd pojawiał się **kilka razy dziennie**.
- Charakterystyka jest **stroma** — nie liniowy dryf, tylko gwałtowny wzrost częstości powyżej ~35°C.

### Obserwacja 2 — szarpanie na zimno, zależność ODWROTNA
- Szarpanie po uruchomieniu w okolicach **1500–1700 obr./min**, ustępujące po nagrzaniu.
- Występuje **tym częściej, im zimniej**. Przy porankach ~18°C — **zawsze**. W gorące lipcowe poranki — czasem w ogóle.

### Co z tego wynika — trzy wnioski

**(a) Bierne czekanie na usterkę w chłodzie jest bezcelowe.** 7 dni, 700–2100 km, jedno zdarzenie. Jeśli wrócisz przy 20°C i będziesz czekał z uzbrojonym skopem, prawdopodobnie nie złapiesz nic. **Usterkę trzeba prowokować** — stąd awans testu termicznego i testu AC na początek listy.

**(b) Zmienną może nie być temperatura, tylko praca klimatyzacji.** Przy 35–42°C AC pracuje bez przerwy; przy 18°C rano — wcale. To generuje hipotezę H7 (niżej). Kluczowe, bo pozwala wywołać usterkę **w każdą pogodę**.

**(c) Szarpanie to prawdopodobnie osobna usterka.** Przeciwne sygnatury termiczne. Sprawdziłem wersję jednoprzyczynową (mechanicznie zakleszczony zawór: na zimno uchylony → szarpanie, na gorąco zakleszczony → P0404) i **ona się nie broni**: gdyby na zimno zawór był uchylony wbrew komendzie zamknięcia, P0404 sypałby się też na zimno. A nie sypie. Do tego zawory zdejmowane z tego auta nie mają istotnego nagaru. Szarpanie idzie na osobną ścieżkę B.

---

## 2. Hipotezy

| # | Hipoteza | Rozstrzyga |
|---|---|---|
| **H1** | Wspólne przetarcie wiązki EGR ↔ AC/ECV przy pokrywie rozrządu | Krok 4 + 6a |
| **H2** | Rezystancyjna masa potencjometru (pin 6 → GUD09) | Krok 2 |
| **H3** | Chwilowa przerwa w torze sygnału wipera | Krok 3 |
| **H4** | Zapad referencji 5 V | Krok 1 |
| **H5** | Mechanika / silnik / przekładnia / tor potencjometru | Krok 5 |
| **H6** | Rozwarte styki żeńskie złącza CUD87 (3× wymiana zaworu = 3× rozpinanie) | Krok 6b |
| **H7** | **Sprzężenie z obwodem AC/ECV — usterka zależy od pracy klimatyzacji, nie od temperatury** | **Test A** |

### H7 — uzasadnienie (nowa, mocny kandydat)

Kompresor to **Denso 6SE14 o zmiennej wydajności ze sterowanym zewnętrznie ECV**. Wcześniejsza usterka AC to była **przerwana żyła w wiązce ECV**, naprawiona obejściem — a ta wiązka biegnie **tą samą trasą przy pokrywie rozrządu** co EGR, gdzie po wymianie rozrządu zostały połamane mocowania.

Trzy mechanizmy, przez które praca AC daje P0404:

1. **Prąd przez wspólną masę.** Wentylatory chłodnicy i sprzęgło AC to dziesiątki amperów. Jeśli masa potencjometru (pin 6 → GUD09) ma podwyższoną rezystancję albo dzieli punkt masowy z tymi obciążeniami, jej potencjał rośnie dokładnie wtedy, gdy AC pracuje. Potencjometr odnosi się do zafałszowanej masy → P0404. To H2 i H1 naraz, **bez udziału rozszerzalności cieplnej**.
2. **Sprzężenie PWM przez przetarcie.** ECV kompresora o zmiennej wydajności jest sterowany PWM **w sposób ciągły**, nie jak zwykłe sprzęgło on/off. Uszkodzona izolacja w miejscu przetarcia → przebieg PWM sprzęga się w linię wipera. Tylko gdy AC pracuje.
3. **Ta sama uszkodzona wiązka.** Skoro jedna żyła była już przerwana, sąsiednie są prawdopodobnie nadtarte, ale jeszcze nie przerwane.

---

## 3. Tor pomiarowy

Cztery własne koncentryki RG174 (~4 m), wtyk BNC przy skopie, pin back-probe w komorze. **Gotowe i przetestowane.**

- **Probe ratio w skopie: 1X na wszystkich kanałach.** Koncentryk nie ma dzielnika. Błąd tutaj = błąd 10×.
- **Żyła środkowa** → punkt pomiarowy. **Ekran** → wspólny węzeł → **jeden** przewód na minus akumulatora.
- **Dokładnie jedno połączenie galwaniczne skopu z autem.** Nigdy nie pinaj poszczególnych ekranów do różnych punktów masy.
- Przy skopie nic nie robisz — korpusy BNC są wewnętrznie wspólne.

### Bezpieczeństwo

- **Zasilaj skop z power banku USB-C** (wymagany profil **15 V/3 A**, bank ≥45 W; banki 5 V/9 V/20 V nie uruchomią skopu). Power bank usuwa drogę przez uziemienie sieci. **Nie wpinaj do ładowarki z zapalniczki podczas Kroku 2** — nieizolowana przetwornica zewrze masę skopu z nadwoziem w desce i zrobisz pętlę masy dokładnie w pomiarze miliwoltów.
- Ładowarka samochodowa jest dopuszczalna w krokach, gdzie patrzysz na wolty (3, 4, 5, 6) — nie w 1 (zoom) i 2.
- Wszystkie kanały mają **wspólną masę**. Jeden klips → minus akumulatora.
- **Nigdy nie pinaj masy do pinów napędu 1/3** — zewrzesz gałąź H-bridge.
- Back-probe od strony wiązki. Nie rozchylaj styków CUD87 — wygenerujesz H6 samodzielnie.
- Wiggle przy pracującym silniku: uwaga na pasek i wentylator.
- Test termiczny: opalarka **z dystansu**, nie palnik.

---

## 4. Ograniczenia DHO804 — ważne

### Pamięć zależy od liczby aktywnych kanałów

| Aktywne kanały | Tryb | Pamięć | Próbkowanie |
|---|---|---|---|
| 1 | single-channel | 25 Mpts | 1,25 GSa/s |
| 2 | dual-channel | 10 Mpts | 625 MSa/s |
| **3 lub 4** | full-channel | **1 Mpts** | 312,5 MSa/s |

Przy czterech kanałach masz **1 Mpts, nie 25**. Długi ciągły zapis trasy na 4 kanałach odpada — patrz Krok 7. Gdy potrzebujesz pamięci, **wyłącz nieużywane kanały**.

### Nie ma trybu High Res

Dostępne tryby akwizycji: **Normal, Peak Detect, Average (2…65536), UltraAcquire**. Zamiast High Res używaj:
- **Average 8–16** → pomiar poziomów (masa, 5 V). Uwaga: zamazuje glitche.
- **Peak Detect** → polowanie na glitche (łapie impulsy 1,6 ns niezależnie od próbkowania — dlatego działa nawet przy 1 Mpts).

### Trzy funkcje zrobione pod usterkę przerywaną

- **Waveform Recording** — do 500 000 ramek, każda wyzwolona zdarzeniem, ze wszystkich włączonych kanałów, z odtwarzaniem klatka po klatce. To jest właściwe narzędzie do jazdy, lepsze niż single-shot, i nie potrzebuje głębokiej pamięci.
- **Digital Voltmeter → Limits → Beeper** — skop **piszczy**, gdy napięcie wyjdzie poza zadany zakres. Nie musisz patrzeć w ekran.
- **Pass/Fail z maską** — przy naruszeniu zatrzymuje akwizycję, piszczy i robi zrzut ekranu.
- Dodatkowo **Display → Persistence → Infinite** przy wiggle: ślad zostaje, nawet jeśli glitch mrugnął raz.

---

## 5. Mapa punktów i konfiguracje

| Pin | Sygnał | ECM (CUD-K) | Probe |
|----|--------------------------|------|------|
| 1  | Napęd silnika (H-bridge) | 5    | 1X |
| 3  | Napęd silnika (H-bridge) | 20   | 1X |
| 4  | Zasilanie potencjometru 5 V | 39 | 1X |
| 5  | Wiper / sygnał pozycji   | 31   | 1X |
| 6  | Masa potencjometru → GUD09 | 23 | 1X |

*Zweryfikuj pinout względem schematu dla swojego VIN przed pierwszym wpięciem.*

| Konfig. | CH1 | CH2 | CH3 | CH4 | Math |
|---|---|---|---|---|---|
| **A** | pin 5 wiper | pin 4 (5 V) | pin 6 masa | AC/ECV | — |
| **B** | pin 5 wiper | pin 1 napęd | pin 3 napęd | pin 4 (5 V) | **CH2 − CH3** |

### Nastawy wspólne
Wejście w menu kanału: **dotknij etykiety kanału** na dole ekranu.

Probe **1X** · Coupling **DC** · BW Limit **20M** (na pinach 4/5/6; na 1/3 może być FULL) · Invert OFF.

Parametry sprzętowe: czułość 500 µV/div…10 V/div · maks. wejście CAT I 300 Vrms / 400 Vpk (12 V to zero ryzyka) · zakres dynamiczny ±4 dz = cały ekran · offset ±1 V przy ≤65 mV/div, ±8 V przy ≤270 mV/div, ±20 V przy ≤2,75 V/div · timebase 5 ns/div…500 s/div · **ROLL od 50 ms/div**.

### Przygotowanie jednorazowe
1. Rozgrzej skop ≥30 min, zrób **Self-Cal** (Utility).
2. Sprawdź wszystkie cztery tory na wyjściu kompensacyjnym (**1 kHz, 3 Vpp**) — wykrywa zimny lut i zwarcie ekranu.
3. **Zapisz setupy** (Storage → Save → Setup, *.stp): `testA_ac.stp`, `krok1_5V.stp`, `krok2_masa.stp`, `krok5_hbridge.stp`, `krok7_jazda.stp`. Przy masce wczytujesz plik zamiast klikać dwadzieścia parametrów. **To oszczędzi Ci najwięcej czasu ze wszystkiego w tym dokumencie.**
4. Zmierz realny czas zapisu: ustaw Mem Depth i timebase, **odczytaj wyświetlany sample rate**, policz `pamięć ÷ sample rate`. Zapisz: przy 2 kan. ______ s, przy 4 kan. ______ s.

---

# TEST A — klimatyzacja (NOWY, PRIORYTET 1)

**Dlaczego pierwszy:** rozstrzyga H7, trwa kwadrans, **działa w każdą pogodę** i nie wymaga czekania na upał. Jeśli wyjdzie pozytywnie, oszczędza Ci całą resztę.

**Konfiguracja A** (4 kanały, 1 Mpts — wystarczy, bo łapiesz zdarzenie, nie rejestrujesz trasy).

| | CH1 wiper | CH2 5 V | CH3 masa | CH4 AC/ECV |
|---|---|---|---|---|
| V/div | 1 V | 1 V | **20 mV** | 5 V |
| Offset | ~2,5 V | ~2,5 V | 0 | ~6 V |
| BW Limit | 20M | 20M | 20M | 20M |

- **Timebase:** 500 ms – 1 s/div (ROLL) — żebyś widział cykle załączania AC.
- **Trigger:** Sweep **Auto** (obserwacja).
- **Przebieg 1 — poziomy:** Acquire **Average 16**. Szukasz **skoku poziomu DC** na CH3 w momencie załączenia AC.
- **Przebieg 2 — glitche:** Acquire **Peak Detect**, Persistence **Infinite**. Szukasz zakłóceń i skoków na CH1.

### Procedura
1. Silnik ciepły, na postoju, **AC wyłączona**. Zapisz poziomy odniesienia: masa, wiper, 5 V.
2. **AC na maksimum**, najniższa temperatura, dmuchawa max. Poczekaj, aż załączą się wentylatory chłodnicy.
3. Obserwuj CH3 — czy poziom masy skacze. Obserwuj CH1 — czy pojawia się szum/PWM.
4. **Przełącz AC on/off 5 razy.** Dowodem jest powtarzalność, nie pojedyncza zbieżność.
5. Klemą **MS2115A** zmierz prąd pobierany przez wentylatory/AC — żebyś wiedział, jakie obciążenie faktycznie wchodzi.
6. Jeśli na postoju czysto — powtórz w jeździe z AC na maksa.

### Test przeciwny (gdy trafisz na gorący dzień)
Przejazd przy wysokiej temperaturze z **wyłączoną AC**, otwarte okna.

### Tabela rozstrzygająca

| | AC ON | AC OFF |
|---|---|---|
| **Gorąco (>35°C)** | usterka? | usterka? |
| **Chłodno (<25°C)** | usterka? | usterka? |

- Usterka w polu **chłodno + AC ON** → **H7 potwierdzona.** Sprawcą jest praca klimatyzacji, nie temperatura. Idziesz w masy i przetarcie przy pokrywie rozrządu.
- Usterka w polu **gorąco + AC OFF** → sprawcą jest temperatura. Priorytet: Krok 6c (termiczny).
- Usterka tylko w **gorąco + AC ON** → czynniki się sumują; rób oba tory.

---

# KROK 0 — envelope „known good"

Bez tego nie ustawisz progów okna w Krokach 3, 4 i 7.

**Konfiguracja A.** CH1–CH3 na 1 V/div, CH4 2 V/div. Acquire **Average 8**. Timebase 200 ms/div (ROLL). Trigger Sweep **Auto**. Measure: Vmax, Vmin, Vpp na CH1; Vavg na CH2 i CH3.

1. **KOEO:** zanotuj 5 V (pin 4), masę (pin 6), **napięcie spoczynkowe wipera**.
2. **Ciepły silnik, potwierdzony BRAK aktywnej regeneracji DPF** (PID w Car Scanner) — regen tłumi EGR i zafałszuje obraz.
3. **Wymuś ruch zaworu:** MaxiECU (test aktuatora) albo rutyna **EGR Replacement** (kończy się na zielono i cykluje zawór), albo naturalne sterowanie w spokojnej jeździe.
4. **Zapisz Vmin/Vmax wipera** → progi okna ustawisz ~0,3 V poza tym zakresem.

Zapis: `krok0_envelope` (PNG + CSV).

---

# KROK 2 — masa potencjometru, pin 6 (H2)

**Zmiana w v3:** mierz pod **realnym obciążeniem elektrycznym**, nie pod ruchem zaworu. Aktuator EGR ciągnie ułamek tego, co wentylatory i AC.

Rób na **dwóch kanałach** (CH1 + CH3) → 10 Mpts zamiast 1.

| Etap | V/div CH3 | Offset | Acquire | Timebase |
|---|---|---|---|---|
| Rozpoznanie | 1 V | 0 | Average 8 | 200 ms/div (ROLL) |
| Pomiar właściwy | **20 mV** | 0 | **Average 16** | 200 ms/div |
| Polowanie na skok | 20 mV | 0 | **Peak Detect** | 200 ms/div |

Przy 20 mV/div ekran obejmuje 160 mV. Większy spadek wyjdzie poza ekran — to już jest wynik; do zmierzenia wartości cofnij się na 100 mV/div.

**Mierz w stanach:** KOEO → idle → **AC + wentylatory na maksa** → ruch EGR → wiggle.

- **Próg przesiewowy:** < ~50 mV statycznie, < ~100 mV pod obciążeniem.
- **Dowód:** *powtarzalny* wzrost skorelowany z obciążeniem lub ruchem odcinka.
- **Lokalizacja:** po trafieniu zmierz to samo bezpośrednio na GUD09 i na podejrzanym odcinku.

---

# KROK 1 — referencja 5 V, pin 4 (H4)

| Etap | V/div CH2 | Offset | Acquire |
|---|---|---|---|
| Rozpoznanie | 1 V | ~2,5 V | Average 8 |
| Zoom | **100 mV** | ~5 V (aż przebieg wyląduje na środku) | Average 16 |
| Zapady | 100 mV | ~5 V | **Peak Detect** |

Timebase 200 ms/div (ROLL). Przy 100 mV/div offset sięga ±8 V, więc wycentrowanie 5 V jest w zasięgu; ekran obejmie 800 mV wokół 5 V.

- **Próg:** 5,00 V ±0,1.
- **FAIL:** powtarzalny zapad/skok, zwłaszcza skorelowany z ruchem EGR, pracą AC lub wyginaniem wiązki.
- **Jeśli wiper reaguje w tej samej chwili co zapad 5 V → H4 wiodąca, wiper jest tylko ofiarą.**

---

# KROK 3 — wiper, pin 5 (H3)

CH1: 1 V/div, offset ~2,5 V, Acquire **Peak Detect**, timebase 100–500 ms/div.

**Wyzwalanie na biurku (prostsze):**
Trigger → Type **Edge** → Source **CH1** → Slope **Falling** → Level **0,3 V** → Sweep **Single**.

**Wyzwalanie pełne (łapie oba kierunki):**
Trigger → Type **Window** → Source **CH1** → górny **4,7 V**, dolny **0,3 V** → state **Exit** → Sweep **Normal**.

Trigger Level Range to ±4,5 dz od środka — przy 1 V/div i offsecie 2,5 V progi mieszczą się bez problemu.

Opcjonalnie **Persistence: Infinite**.

**Czego szukasz:** zejścia do ~0 V, skoku w stronę 5 V, schodków, przerw w płynnym przebiegu.
**Interpretacja:** wiper glitchuje przy stabilnym 5 V i stabilnej masie → H3. Jeśli 5 V albo masa lecą równocześnie → wróć do H2/H4, nie obwiniaj wipera.

---

# KROK 6c — TEST TERMICZNY (awans do priorytetu 2)

**Dlaczego wysoko:** obserwacja 1 mówi wprost, że usterka jest termiczna. To najszybszy sposób wywołania jej na postoju, bez czekania na 35°C.

- Konfiguracja A, Acquire **Peak Detect**, **Persistence Infinite**.
- Trigger: **Window na CH1**, Exit, Sweep **Normal**.
- Włącz **Digital Voltmeter → Limits → Beeper** na CH1 — będziesz miał wolne ręce i alarm dźwiękowy.

**Procedura:** przy podpiętym skopie podgrzewaj opalarką **z dystansu** (albo schładzaj zamrażaczem) kolejno:
1. **złącze CUD87** (to samo testuje H6 termicznie),
2. **odcinek przy pokrywie rozrządu** — połamane mocowania, miejsce naprawy ECV,
3. podejrzane miejsca tarcia dalej w wiązce,
4. punkt masowy **GUD09**.

Zmiana przebiegu skorelowana z konkretnym punktem = lokalizacja. **Powtórz 3–5 razy** na tym samym punkcie.

---

# KROK 6a / 6b — wiggle

Konfiguracja A, Acquire **Peak Detect**, **Persistence Infinite**, timebase 200–500 ms/div, Sweep Auto. DVM Beeper włączony.

**6a — wiązka.** Idź **odcinkami**, jeden fragment naraz: CUD87 → pierwsze mocowania → **pokrywa rozrządu** → miejsca tarcia → dalej w stronę ECM. Po trafieniu **powtórz 3–5 razy**. Zapis PNG + notatka który odcinek.

**6b — samo złącze (H6).** Przy **nieruszanej** wiązce poruszaj i dociskaj wtyczkę CUD87 — bocznie, osiowo, z naciskiem na pojedyncze piny. Glitch tylko tutaj → usterka w złączu, nie w przewodach. Potwierdzenie: rozłącz, obejrzyj styki żeńskie pod lupą (rozwarcie, przegrzanie, zielony nalot), porównaj opór wsuwania z pinami nieużywanymi.

---

# KROK 4 — korelacja EGR ↔ AC/ECV (H1)

Konfiguracja A, Acquire **Peak Detect**, Trigger **Window na CH1**, Exit, Sweep **Normal**, **Waveform Recording włączone**.

**Warunek wstępny:** musisz jednoznacznie wiedzieć, jaki sygnał mierzysz na CH4 i którędy biegnie.

**Kryterium:** sam jednoczesny glitch na CH1 i CH4 **nie jest dowodem** — to korelacja czasowa. Oba kanały mogą skoczyć razem, bo wspólnie odniosły się do przesuniętej masy albo złapały transient z wtryskiwaczy.

**Test rozstrzygający:** poruszaj **konkretnym fragmentem** wiązki i sprawdź, czy **ten sam ruch powtarzalnie (3–5×)** wywołuje glitch na dwóch lub więcej kanałach jednocześnie.

- Powtarzalny jednoczesny glitch → **H1 bardzo mocna.**
- CH1/CH3 reagują, CH4 stabilny → H1 słabnie, wracamy do lokalnej gałęzi EGR.

---

# KROK 5 — H-bridge, piny 1 i 3 (H5)

**Konfiguracja B.**

| | CH1 wiper | CH2 pin 1 | CH3 pin 3 | CH4 pin 4 |
|---|---|---|---|---|
| V/div | 1 V | **5 V** | **5 V** | 1 V |
| Offset | ~2,5 V | ~10 V | ~10 V | ~2,5 V |
| BW Limit | 20M | FULL | FULL | 20M |

- **Math:** nawigacja → Math1 → Operation **A−B** → Source A **CH2**, Source B **CH3**. To jest napięcie realnie przyłożone do silnika i sedno tego kroku.
- Timebase: start 5 ms/div, potem dostrój do rzeczywistej częstotliwości PWM.
- Acquire **Normal**, Trigger Edge na CH2, Sweep Normal.
- **Nie zakładaj z góry kształtu PWM ani przeciwnych faz** — oceniaj, co widzisz.

**Werdykty:**
- **PASS:** napęd zmienia stan na komendę, Math przełącza poprawnie, wiper podąża płynnie i proporcjonalnie.
- **FAIL A:** napęd i Math OK, **wiper nie podąża** → mechanika, silnik, przekładnia, tor potencjometru.
- **FAIL B:** brak sterowania na **obu** przewodach → przewody 1/3, złącza, sterowanie ECU.
- **FAIL C:** **jeden** przewód nietypowy → konkretna gałąź H-bridge, tor do CUD-K 5/20.

---

# KROK 7 — przechwycenie w jeździe

Dopiero gdy prowokacja (Test A, 6c, 6a/6b) nic nie dała.

### Wariant A — Waveform Recording (polecany)
- 4 kanały, Konfiguracja A. Acquire **Peak Detect**. Trigger **Window na CH1**, progi z Kroku 0, Exit, Sweep **Normal**.
- **Waveform Recording włączone** — każde wyjście wipera poza okno zapisze się jako osobna ramka ze wszystkimi czterema sygnałami (do 500 000 ramek). Po powrocie odtwarzasz klatka po klatce.
- Ograniczenie 1 Mpts przestaje przeszkadzać, bo zapisujesz zdarzenia, nie trasę.
- **Jedź z włączoną AC** — po Teście A wiesz, czy to ma znaczenie.

### Wariant B — długi zapis ciągły, 2 kanały
Tylko **CH1 + CH3** → 10 Mpts. Mem Depth 10M, timebase wg pomiaru z sekcji 5.4, ROLL. Sensowne, gdy szukasz powolnego dryfu, nie zdarzenia.

### Wariant C — Pass/Fail jako druga sieć
Maska wokół poprawnego przebiegu wipera; przy naruszeniu skop zatrzymuje akwizycję, piszczy i robi zrzut. Może iść równolegle z alarmem DVM.

### Logowanie równoległe (tester)
Jedyny PID EGR, RPM, MAF, temperatura silnika, **temperatura otoczenia / IAT**, prędkość, napięcie instalacji, status DPF, **stan pracy AC**. Pamiętaj o limicie 1,8–4,6 Hz — **maks. 3–4 kanały na sesję**.

---

# ŚCIEŻKA B — szarpanie na zimno (osobny wątek)

Nie miesza się z kampanią EGR. Cel: ustalić w 10 minut, czy EGR ma z tym cokolwiek wspólnego.

**Test za darmo:** przy najbliższym **zimnym rozruchu**, podczas szarpania, loguj jedyny PID EGR.
- EGR pokazuje **zamknięty**, gdy ECU go zamyka → **EGR oczyszczony z zarzutu**, szarpanie na osobną listę.
- EGR pokazuje **otwarty** → wracamy do rozmowy, bo to zmienia obraz.

**Wersja skopowa:** CH1 (wiper) + Math CH2−CH3 podczas zimnego rozruchu — widzisz komendę i odpowiedź naraz.

**Jeśli EGR wyjdzie czysty, kandydaci na szarpanie 1500–1700 obr. na zimno** (rzeczy, które uwalniają się wraz z ciepłem): zakoksowany mechanizm zmiennej geometrii turbiny, klapy wirowe w kolektorze, jakość rozpylenia wtryskiwaczy na zimno, świece żarowe i dogrzewanie po rozruchu. To osobna diagnostyka — **nie pozwól jej zablokować kampanii EGR**.

---

# Macierz interpretacji

| Obserwacja | Kierunek |
|---|---|
| Usterka pojawia się przy włączonej AC, w chłodny dzień | **H7** — sprzężenie z obwodem AC/ECV lub prąd przez wspólną masę |
| Masa (pin 6) rośnie powtarzalnie przy załączeniu AC/wentylatorów | **H2 + H7** — rezystancyjna masa obciążana prądem AC |
| Glitch pojawia się przy podgrzaniu konkretnego punktu | usterka termiczna w tym punkcie |
| Glitch tylko przy poruszaniu **samej wtyczki**, wiązka spokojna | **H6** — rozwarte styki CUD87 |
| Glitch powtarzalnie przy ruchu **konkretnego odcinka** wiązki | usterka mechaniczna tego odcinka |
| Powtarzalny jednoczesny glitch EGR + AC/ECV przy ruchu odcinka | **H1** — wspólne przetarcie |
| Jednoczesny glitch **bez** powtarzalnego wywołania | tylko korelacja — nic nie potwierdzone |
| Pin 4 zapada, wiper reaguje w tej samej chwili | **H4** — referencja 5 V |
| Wiper skacze przy stabilnym 5 V i stabilnej masie | **H3** — tor wipera / styk / potencjometr |
| Math CH2−CH3 przełącza poprawnie, wiper nie podąża | **H5** — mechanika |
| Szarpanie na zimno przy EGR zamkniętym zgodnie z komendą | **poza EGR** — ścieżka B |

---

# Kolejność wykonania

1. **TEST A — klimatyzacja** ← zacznij tutaj, każda pogoda, kwadrans
2. **KROK 0** — envelope wipera
3. **KROK 2** — masa pin 6, **pod obciążeniem AC/wentylatorów**
4. **KROK 1** — referencja 5 V
5. **KROK 6c** — test termiczny (opalarka / zamrażacz)
6. **KROK 6a** — wiggle wiązki
7. **KROK 6b** — wiggle złącza CUD87
8. **KROK 3** — wiper
9. **KROK 4** — korelacja z AC/ECV
10. **KROK 5** — H-bridge + Math
11. **KROK 7** — capture w jeździe, jeśli nic wcześniej nie wyszło
12. **ŚCIEŻKA B** — test PID EGR przy zimnym rozruchu (równolegle, kiedykolwiek)

**Logika kolejności:** prowokacja przed czekaniem (obserwacja 1 dowodzi, że czekanie w chłodzie nie działa), masa i zasilanie przed wiperem (ich usterka udaje usterkę sygnału), testy bezpieczne na postoju przed jazdą.

---

# Prowadź dziennik zdarzeń

Najtańsza rzecz o najwyższym zwrocie. Przy każdym P0404 zapisz: **data, godzina, temperatura otoczenia, AC włączona tak/nie, przebieg dnia, typ jazdy, czy była regeneracja DPF**. Po kilkunastu wpisach masz zbiór, który przemielisz w Pythonie tak jak resztę logów — i korelacja przestanie zależeć od pamięci. (Plik: `docs/dziennik-zdarzen.csv`.)

---

# Ściąga na maskę

| Chcę… | Ustaw |
|---|---|
| zobaczyć poziom czysto | Acquire → **Average 8–16** |
| złapać krótki glitch | Acquire → **Peak Detect** |
| nie przegapić glitcha przy wiggle | Display → Persistence → **Infinite** |
| żeby skop sam mnie zawołał | **Digital Voltmeter → Limits → Beeper** |
| łapać zdarzenia przez całą jazdę | **Window trigger + Waveform Recording** |
| napięcie na silniku EGR | **Math1 = CH2 − CH3** |
| mierzyć miliwolty na masie | **1X, DC, 20 mV/div, Average 16, 2 kanały, power bank** |
| najwięcej pamięci | **wyłącz nieużywane kanały** (4 kan. = 1 Mpts, 2 kan. = 10 Mpts, 1 kan. = 25 Mpts) |
| wywołać usterkę bez czekania | **Test A (AC) lub Krok 6c (opalarka)** |

---

**Zastrzeżenia.** Dane sprzętowe DHO804 (zakresy, tryby, wyzwalanie, pamięć) potwierdzone w dokumentacji Rigola; brzmienie pozycji menu może się różnić między wersjami firmware — nawigacja jest dotykowa, więc najpewniej dotykaj etykiet na ekranie. Pinout pochodzi z Twojej dokumentacji, nie z niezależnie potwierdzonego schematu dla tego VIN. Przed Krokiem 4 jednoznacznie ustal, jaki sygnał AC/ECV mierzysz i którędy biegnie jego przewód.
