# Odbiór P05-R2 — formularz stanowiskowy

*R2 (29.09.2026): kroki 3, 5 i 7 według recenzji P5-02/P5-05, nowe kroki 10a/10b (P5-03). Dotyczy schematu R2; PCB powstanie w formacie S1.*

Płytka/numer: ______ Data: ______ Osoba: ______ Miernik: ______ Oscyloskop: ______ Firmware/hash: ______

**Wszystkie wyniki początkowe: NIE ZBADANO.** Wpisy „PASS” w raportach JSON dotyczą kontroli plików, nie poniższych pomiarów. Pierwsze uruchomienie z zasilaczem laboratoryjnym i generatorami napięcia, bez ECU i silnika.

| Etap | Czynność i kryterium | Wynik/pomiar |
|---|---|---|
|0|Wydruk1:1, belka100mm; wszystkie rzeczywiste obudowy i otwory pasują. Osobno mating P03/P05 oraz komplet16 pozycji z tabeli MECHANIKA.|NIE ZBADANO|
|1|Obejrzeć luty U1/U3 pod powiększeniem; brak mostków. Sprawdzić polaryzację C1, U6/U7/U12, K1–K3, D1–D3.|NIE ZBADANO|
|2|Bez zasilania sprawdzić brak zwarć 5V/GND oraz3V3/GND; uwzględnić ładowanie C1. LV05.3 nie jest zwarte z lokalnym3V3. REGCAP36/39 nie są zwarte;44/45 są zwarte.|NIE ZBADANO|
|3|Zasilanie5,00V, MEAS_EN=0. Początkowy limit100mA; po braku zwarć limit250mA. Zmierzyć prąd, napięcie przed/za R1,3V3_DAQ. 5V_SYS na złączu LV05 P05: **4,93–5,07V przy ok.23°C** (w 60°C daje to ≥25mV zapasu do obu progów okna). 5VA = 5V_SYS − I·1Ω, spadek na R1 12–20mV. 3V3_DAQ 3,20–3,40V.|NIE ZBADANO|
|4|Oscyloskop: AVCC,VDRIVE,DAQ_OK przy narastaniu, wolnym/szybkim wyłączaniu oraz ponownym załączeniu. VDRIVE nie przekracza AVCC+0,3V. Nie zasilać osobno VDRIVE.|NIE ZBADANO|
|5|Zmieniać napięcie powoli; zanotować rzeczywiste progi okna. Docelowo (R5 6,04k, R7 5,11k, U2 REF5025IDR) dolny **4,753–4,848V**, górny **5,138–5,234V** przy założonym budżecie; nominalnie 4,800 i 5,186V. Nie przekraczać5,5V na regulatorze; próby okna tylko do5,3V.|NIE ZBADANO|
|6|DAQ_OK=0 przy braku dowolnego warunku zasilania. MEAS_PERMIT=0 mimo MEAS_EN=1, gdy DAQ_OK=0. Sprawdzić czas do odpadnięcia cewek i zaników przy progu.|NIE ZBADANO|
|7|Kontrola Ioff: P03 włączone/P05 wyłączone oraz odwrotnie. Brak „podnoszenia” wyłączonej szyny, brak znaczącego prądu przez IO. Zmierzyć napięcia, nie tylko LED. Przy P03 włączonym i P05 wyłączonym 3V3_DAQ ≈0,07V (R13 47k; w R1 z 10k było 0,30V, granica VDRIVE≤AVCC+0,3V).|NIE ZBADANO|
|8|Po stabilnym zasilaniu pełnyRESET20µs i2100ms oczekiwania. SPI1MHz: poprawne odczyty kontrolne rejestrów; BUSY/CONVST zgodne z oscyloskopem.|NIE ZBADANO|
|9|CS=1: DOUT nie blokuje magistrali. Próbny pull10k doGND, potem do3V3 na wspólnym MISO potwierdza stan wysokiej impedancji, gdy pozostali użytkownicy busa też są wyłączeni.|NIE ZBADANO|
|10|MEAS_EN=0: odczepy odłączone. MEAS_EN=1 iDAQ_OK=1: cewki≈60mA łącznie; właściwe piny przechodzą do właściwych CH. Przy zaniku DAQ_OK odczepy ponownie się rozłączają.|NIE ZBADANO|
|10a|Przekaźniki K1–K3 przed wlutowaniem: cewka zasilana wprost z zasilacza, przy ok.23°C napięcie zadziałania każdej sztuki **≤3,9V** (daje ≤4,4V przy 60°C). Sztuki powyżej limitu wymienić; o innym wariancie cewki decydować dopiero po pomiarze.|NIE ZBADANO|
|10b|VDS na U4.18 przy trzech włączonych cewkach (≈63mA): **≤0,3V**.|NIE ZBADANO|
|11|C12/C13: dokumentacja DC-bias wybranego MPN lub pomiarCeff przy2,5/4,4V potwierdza≥10µF wraz z tolerancją i zakresem temperatur. REGCAP iREF bez nadmiernych tętnień.|NIE ZBADANO|
|12|Przez docelowe adaptery podać0/1/2,5/4,5V dlaCH3–5;0/5/12/16V dlaCH1–2 iCH7. Kontrola znaków, brak zamiany kanałów, kalibracja dwóch punktów i kontrola pozostałych.|NIE ZBADANO|
|13|AUX: pozycjaHI iLO potwierdzona omomierzem; oddzielne profile i kalibracje. Kontrola na0/1/4V LO oraz0/5/12V HI. Nie przełączać pod napięciem.|NIE ZBADANO|
|14|CH6 przez10k: zapisać offset iRMS szumu; nie oczekiwać idealnego kodu zero. Wstępny cel po rozgrzaniu≤2mV RMS odniesione do wejściaADC przy zakresie±5V iOS×8; przekroczenie wymaga diagnostyki, nie arbitralnego „zerowania”.|NIE ZBADANO|
|15|Niezależnie sprawdzić przesłuch: stałe2,5V na feedback, impulsy0–12V przez tor motor. PorównaćADC i oscyloskop; odróżnić prawdziwe zakłócenie od aliasingu.|NIE ZBADANO|
|16|Próba temperatury samegoP05: około20/40/60°C, bez kondensacji. Zapisać zero, gain, progiDAQ_OK i szum. Ciepły EGR nie oznacza, żeP05 wolno podgrzewać do tej samej temperatury.|NIE ZBADANO|
|17|1MHz/do2kSPS stabilnie przez30min; potem kwalifikacja4MHz/docelowego10kSPS. ZliczyćCONVST/próbki, gapy, opóźnienia oraz zapisSD przy aktywnych innych modułach.|NIE ZBADANO|
|18|Zanik zasilaniaP05 podczas sesji: brak uznania starych próbek za nowe, napęd zablokowany, sesja przerwana. Ponowna inicjalizacja iARM wymagane przedTEST.|NIE ZBADANO|

Do prób pinów5/6 stosować znane źródła na stanowisku i wszystkie przewidziane permutacje rozpoznawania. W aucie identyfikacja jest pasywna. Dołączenie do ECU dopiero po odbiorze P11/adapterów oraz pomiarze, że przy wyłączonym P05 tor nie zasila fabrycznych sygnałów przez wejścia.

Akceptacja etapów0–11: ______ Akceptacja kalibracji12–16: ______ Akceptacja integracji17–18: ______

Uwagi/odstępstwa i decyzja: ______________________________________________________
