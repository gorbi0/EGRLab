# EGRLab — bieżący etap projektu

Aktualizacja: 23.09.2026. Baza odniesienia: EGRLab-v6.1-rc1.

## P07 DRIVE — WSTRZYMANE

Decyzja użytkownika: zamiast Pololu 1451 rozważamy moduł z dwoma BTS7960B. Powrót do projektu P07 dopiero po otrzymaniu płytki i sprawdzeniu jej rzeczywistego wykonania. Nie zatwierdzać layoutu, nie zamawiać PCB P07 i nie kupować Pololu z dotychczasowego BOM bez ponownego rozstrzygnięcia wariantu.

Przed wznowieniem: oznaczenia układów, połączenia bufora 74HC244 i jego zasilanie, poziomy sterujące, R_EN/L_EN, sposób odczytu R_IS/L_IS, stany rozruchu/STOP, hamowanie i przebieg PWM, mechanika modułu. Zachować własny bocznik/INA240/MCP3201, lokalne OC, zatrzask i KPWR. Zmiana obejmie P07 i jego obsługę; nie stanowi zatwierdzonej zamiany pin za pin. W trybie LOGGER mostek testera nadal nie jest połączony z ECU.

## P01 PROTECT — R2 DO RECENZJI, PRZED LAYOUTEM

Aktualny pakiet: `P01-R2-review`, archiwum `P01-R2-review.zip`. R1 i 6.1-rc1
pozostają historycznymi, niezmienionymi punktami odniesienia.

Wykonano poprawki po recenzji Opusa: nowy zacisk Q2 P-MOS+D9 i wartości RC,
spójny schemat/BOM/footprinty, większe PTH H_BAT i mate Phoenix1786174,
protokół szybkiego podłączenia zasilania oraz proces kontroli stanów/przejść.
Źródła: `docs/ZMIANY.md`, `ANALIZA.md`, `PROCES.md`, `ODBIOR.md`.

Wyniki autora: ERC0, XML88 elementów/191 końcówek/34 sieci,203 kontrole pakietu,
9 wykrywanych mutacji,26 scenariuszy dynamiki R2 i odrzucenie znanego błędu R1,
3 porównania kroku czasowego,19 końcowych kontroli spójności. Model przybliżony;
nie potwierdza sprzętu, SOA, termiki, pełnego detektora OVP ani odporności ISO.

R1-01/R1-02: poprawione w projekcie, do ponownej recenzji i pomiarów.
R1-03: większe otwory, do sprawdzenia rzeczywisty przewód. R1-04: mate dobrany.
Otwarte przed layoutem: E-02 recenzja R2, M-01 mocowania radiatorów, B-01 części
i dopasowanie mechaniczne. Przed integracją: H-01 odbiór na stole, w tym pełne
VIN18,5V→VGS<0,5V≤100µs i SOA impulsu OVP przy już otwartym Q1.

SAFE_N nie oznacza gotowego VPROT. W integracji P04/P07 przed KPWR należy
potwierdzić stabilne VPROT przez≥300ms, także przy CORE z USB. Tego firmware
nie zmieniano w pakiecie P01. P07 pozostaje HOLD do odbioru rzeczywistego BTS7960.

Kolejność: recenzja schematu i części → layout2L → DRC/Gerbery/wiercenia →
zamówienie → samodzielny odbiór P01 → integracja następnego modułu.
