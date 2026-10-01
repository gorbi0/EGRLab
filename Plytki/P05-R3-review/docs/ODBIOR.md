# Odbiór P05-R3 — formularz stanowiskowy

*R3 (1.10.2026, format S1): pomiary z kroków 3–10b na kołkach listew serwisowych J_SV1/J_SV2 (krawędź B) zamiast na LV05 i polach testowych; zasilanie i sygnały DAQ przez J_BP1/J_BP2; krok 0 bez matingu B2B; krok 13 dla suwaka JS202011AQN. Kryteria liczbowe R2 bez zmian poza progami okna (krok 5: rezystory 1206 10 ppm/K, nowy budżet).*

Płytka/numer: ______ Data: ______ Osoba: ______ Miernik: ______ Oscyloskop: ______ Firmware/hash: ______

**Wszystkie wyniki początkowe: NIE ZBADANO.** „PASS” w raportach JSON dotyczy kontroli plików, nie poniższych pomiarów. Pierwsze uruchomienie z zasilaczem laboratoryjnym i generatorami napięcia, bez ECU i silnika.

**Jak mierzyć na listwach.** Każdy kołek poza GND idzie przez rezystor przy węźle (1 kΩ, 4,7 kΩ dla VBAT_SENSE, 10 kΩ dla REF/dzielników/wyjść OD). Multimetr 10 MΩ mierzy przez niego z błędem ≤ 0,1 %; sonda oscyloskopu ok. 15 pF daje ok. 15 ns (1 kΩ) albo 150 ns (10 kΩ). Prądu przez kołek nie mierzyć. Masa sondy: pin 1 albo ostatni pin listwy. Numeracja zawsze od pinu 1; kątowa listwa widziana z góry ma pin 1 przy **większym** x — sprawdzić z nadrukiem.

| Kołek | Sieć | Kołek | Sieć |
|---|---|---|---|
| J_SV1.2 | 5V_SYS | J_SV2.2 | ADC_CS |
| J_SV1.3 | 5VA_P05 (za R1) | J_SV2.3 | ADC_CONVST |
| J_SV1.4 | 3V3_DAQ | J_SV2.4 | ADC_BUSY |
| J_SV1.5 | REF_2V5 | J_SV2.5 | ADC_DOUTA |
| J_SV1.6 | RAIL_SENSE | J_SV2.6 | ADC_RESET |
| J_SV1.7 | RAIL_LOW | J_SV2.7 | MEAS_EN |
| J_SV1.8 | RAIL_HIGH | J_SV2.8 | MEAS_PERMIT |
| J_SV1.9 | VBAT_SENSE | J_SV2.9 | DAQ_OK |
| J_SV1.10 | MEAS_COIL_LOW (U4.18) | J_SV2.10 | DAQ_RAIL_N |
| J_SV1.1/11 | GND | J_SV2.11 | P05_SUP3_N |
| | | J_SV2.12 | P05_SUP5_N |
| | | J_SV2.1/13 | GND |

Pełna tabela z rezystorami: `SERWIS.csv`. Węzły referencji ADC (REGCAP_A/D, ADC_REF, REFCAP) mają tylko pola TP2–TP5 przy U1 (TP1 = GND) i są mierzone przed skręceniem stosu (krok 11).

**Stanowisko.** Zasilanie 5,00 V wpinać na J_BP1 (piny 2/4 = 5V_SYS, nieparzyste = GND) przez taśmę IDC 2×5 albo przejściówkę; sygnały DAQ podawać na J_BP2 (taśma 2×10). Bez P03 stany wejść ustalają rezystory domyślne (CS = 1, reszta = 0); pojedyncze wejście można wysterować przez kołek listwy (1 kΩ do węzła z 10 kΩ — poziom ≥ 3 V przy 3,3 V ze źródła).

| Etap | Czynność i kryterium | Wynik/pomiar |
|---|---|---|
|0|Wydruk 1:1, belka 100 mm; wszystkie rzeczywiste obudowy i otwory pasują (klasa 2/3, 106,5 × 100 mm, 8 otworów M3). J_BP1/J_BP2 z taśmą IDC do makiety P12; J_SV1/J_SV2 kołki ok. 6 mm za krawędzią B; SW1 dostępny od strony x = 0.|NIE ZBADANO|
|1|Obejrzeć luty U1/U3 pod powiększeniem; brak mostków. Sprawdzić polaryzację C1, U6/U7/U12, K1–K3, D1–D3 oraz orientację pinu 1 J_BP1/J_BP2.|NIE ZBADANO|
|2|Bez zasilania: brak zwarć 5V_SYS/GND (J_BP1.2–1) i 3V3_DAQ/GND (J_SV1.4–1); uwzględnić ładowanie C1. REGCAP 36/39 (TP3/TP4) nie są zwarte; 44/45 są zwarte. Każdy kołek listwy względem swojego węzła: wartość rezystora z `SERWIS.csv` (±1 %).|NIE ZBADANO|
|3|Zasilanie 5,00 V na J_BP1, MEAS_EN = 0. Początkowy limit 100 mA; po braku zwarć 250 mA. Zmierzyć prąd. 5V_SYS na J_SV1.2: **4,93–5,07 V przy ok. 23 °C** (w 60 °C ≥ 0 mV zapasu do dolnego progu przy TSR −2 % — `verification/electrical-checks.json`, `tsr_margin`). 5VA_P05 na J_SV1.3 = 5V_SYS − I·1 Ω, różnica 12–20 mV (mierzyć różnicowo J_SV1.2–J_SV1.3). 3V3_DAQ na J_SV1.4: 3,20–3,40 V.|NIE ZBADANO|
|4|Oscyloskop: 5VA_P05 (J_SV1.3), 3V3_DAQ (J_SV1.4), DAQ_OK (J_SV2.9) przy narastaniu, wolnym/szybkim wyłączaniu i ponownym załączeniu. VDRIVE nie przekracza AVCC + 0,3 V. Nie zasilać osobno 3V3_DAQ.|NIE ZBADANO|
|5|Zmieniać napięcie powoli; zanotować rzeczywiste progi okna (DAQ_RAIL_N na J_SV2.10, RAIL_SENSE/LOW/HIGH na J_SV1.6–8, REF_2V5 na J_SV1.5: 2,4988–2,5013 V). Docelowo (R5 6,04k, R7 5,11k, 0,1 %/10 ppm/K, U2 REF5025IDR) dolny **4,756–4,845 V**, górny **5,141–5,230 V** przy budżecie z 0,1 % na lutowanie/starzenie; nominalnie 4,800 i 5,186 V. Nie przekraczać 5,5 V; próby okna tylko do 5,3 V.|NIE ZBADANO|
|6|DAQ_OK (J_SV2.9) = 0 przy braku dowolnego warunku: okno (J_SV2.10), nadzorca 3V3 (J_SV2.11), nadzorca 5 V (J_SV2.12). MEAS_PERMIT (J_SV2.8) = 0 mimo MEAS_EN = 1, gdy DAQ_OK = 0. Sprawdzić czas do odpadnięcia cewek i zaników przy progu.|NIE ZBADANO|
|7|Kontrola Ioff: strona P03 włączona/P05 wyłączona oraz odwrotnie (stanowisko: sygnały DAQ z zasilanego źródła 3,3 V na J_BP2 przy wyłączonym 5V_SYS). Brak „podnoszenia” wyłączonej szyny, brak znaczącego prądu przez IO. 3V3_DAQ (J_SV1.4) ≈ 0,07 V przy CS = 1 z zewnątrz (R13 47k; granica VDRIVE ≤ AVCC + 0,3 V).|NIE ZBADANO|
|8|Po stabilnym zasilaniu pełny RESET 20 µs (J_SV2.6) i 2100 ms oczekiwania. SPI 1 MHz: poprawne odczyty kontrolne rejestrów; BUSY (J_SV2.4) i CONVST (J_SV2.3) zgodne z oscyloskopem.|NIE ZBADANO|
|9|CS = 1 (J_SV2.2): DOUT nie blokuje magistrali. Próbny pull 10 kΩ do GND, potem do 3V3 na J_SV2.5 (razem z 1 kΩ R48 daje 11 kΩ) potwierdza stan wysokiej impedancji, gdy pozostali użytkownicy busa też są wyłączeni.|NIE ZBADANO|
|10|MEAS_EN = 0: odczepy odłączone. MEAS_EN = 1 i DAQ_OK = 1: cewki ≈ 60 mA łącznie; właściwe piny J4 przechodzą do właściwych CH. Przy zaniku DAQ_OK odczepy ponownie się rozłączają.|NIE ZBADANO|
|10a|Przekaźniki K1–K3 przed wlutowaniem: cewka wprost z zasilacza, przy ok. 23 °C napięcie zadziałania każdej sztuki **≤ 3,9 V** (daje ≤ 4,4 V przy 60 °C). Sztuki powyżej limitu wymienić.|NIE ZBADANO|
|10b|VDS na U4.18 (J_SV1.10 względem J_SV1.1) przy trzech włączonych cewkach (≈ 63 mA): **≤ 0,3 V**.|NIE ZBADANO|
|11|Przed skręceniem stosu, na TP2–TP5 (TP1 = GND): C12/C13 — dokumentacja DC-bias wybranego MPN lub pomiar Ceff przy 2,5/4,4 V potwierdza ≥ 10 µF z tolerancją i zakresem temperatur. REGCAP i REF bez nadmiernych tętnień.|NIE ZBADANO|
|12|Przez docelowe adaptery podać 0/1/2,5/4,5 V dla CH3–5; 0/5/12/16 V dla CH1–2; dla CH7 to samo napięcie na J_BP1.10 (kontrola na J_SV1.9). Kontrola znaków, brak zamiany kanałów, kalibracja dwóch punktów i kontrola pozostałych.|NIE ZBADANO|
|13|AUX (SW1 JS202011AQN): omomierzem bez zasilania — pozycja HI: J6.1–R33 (AUX_HI) zwarte z AUX_IN i AUX_SHUNT zwarte z GND (SW1.5–SW1.6); pozycja LO: AUX_IN–AUX_LO, AUX_SHUNT otwarte. Opisać pozycje na panelu dopiero po tym pomiarze. Oddzielne profile i kalibracje; kontrola na 0/1/4 V LO oraz 0/5/12 V HI. Nie przełączać pod napięciem.|NIE ZBADANO|
|14|CH6 przez 10 k: zapisać offset i RMS szumu; nie oczekiwać idealnego kodu zero. Wstępny cel po rozgrzaniu ≤ 2 mV RMS odniesione do wejścia ADC przy zakresie ±5 V i OS × 8.|NIE ZBADANO|
|15|Przesłuch: stałe 2,5 V na feedback, impulsy 0–12 V przez tor motor. Porównać ADC i oscyloskop; odróżnić zakłócenie od aliasingu. Powtórzyć z podpiętą sondą na J_SV2 (wpływ kołków na tory analogowe).|NIE ZBADANO|
|16|Próba temperatury samego P05: około 20/40/60 °C, bez kondensacji. Zapisać zero, gain, progi DAQ_OK i szum.|NIE ZBADANO|
|17|1 MHz/do 2 kSPS stabilnie przez 30 min; potem kwalifikacja 4 MHz/docelowego 10 kSPS w stosie z P12. Zliczyć CONVST/próbki, gapy, opóźnienia oraz zapis SD przy aktywnych innych modułach.|NIE ZBADANO|
|18|Zanik zasilania P05 podczas sesji: brak uznania starych próbek za nowe, napęd zablokowany, sesja przerwana. Ponowna inicjalizacja i ARM wymagane przed TEST.|NIE ZBADANO|

Do prób pinów 5/6 stosować znane źródła na stanowisku i wszystkie przewidziane permutacje rozpoznawania. W aucie identyfikacja jest pasywna. Dołączenie do ECU dopiero po odbiorze P11/adapterów oraz pomiarze, że przy wyłączonym P05 tor nie zasila fabrycznych sygnałów przez wejścia.

Akceptacja etapów 0–11: ______ Akceptacja kalibracji 12–16: ______ Akceptacja integracji 17–18: ______

Uwagi/odstępstwa i decyzja: ______________________________________________________
