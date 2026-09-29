# EGRLab — bieżący etap projektu

Aktualizacja: 23.09.2026. Baza odniesienia: `Rewizje/EGRLab-v6.1-rc1`.
Pakiety płytek i ich recenzje znajdują się w `Plytki/`.

## P07 DRIVE — WSTRZYMANE

Decyzja użytkownika: zamiast Pololu 1451 rozważamy moduł z dwoma BTS7960B. Powrót do projektu P07 dopiero po otrzymaniu płytki i sprawdzeniu jej rzeczywistego wykonania. Nie zatwierdzać layoutu, nie zamawiać PCB P07 i nie kupować Pololu z dotychczasowego BOM bez ponownego rozstrzygnięcia wariantu.

Przed wznowieniem: oznaczenia układów, połączenia bufora 74HC244 i jego zasilanie, poziomy sterujące, R_EN/L_EN, sposób odczytu R_IS/L_IS, stany rozruchu/STOP, hamowanie i przebieg PWM, mechanika modułu. Zachować własny bocznik/INA240/MCP3201, lokalne OC, zatrzask i KPWR. Zmiana obejmie P07 i jego obsługę; nie stanowi zatwierdzonej zamiany pin za pin. W trybie LOGGER mostek testera nadal nie jest połączony z ECU.

## P01 PROTECT — PO RECENZJI R2, PRZED LAYOUTEM

Aktualny pakiet: `Plytki/P01-R2-review`, archiwum `Plytki/P01-R2-review.zip`.
Recenzja: `Plytki/P01-R2-recenzja/RECENZJA-P01-R2.md`.
Ocena autora i powtórzenia modeli: `Plytki/P01-R2-odniesienie/ODNIESIENIE.md`.
R1, R2 i rewizje systemu pozostają niezmienionymi punktami odniesienia.
Nie wydano R3 ani plików produkcyjnych PCB.

R2 zawiera nowy zacisk Q2 P-MOS+D9, wartości RC, spójny schemat/BOM/footprinty,
większe PTH H_BAT, mate Phoenix1786174 oraz protokół i proces weryfikacji.
Dokumenty źródłowe: `Plytki/P01-R2-review/docs/`.

Wyniki wydania R2: ERC0, XML88 elementów/191 końcówek/34 sieci,203 kontrole pakietu,
9 wykrywanych mutacji,26 scenariuszy dynamiki R2 i odrzucenie znanego błędu R1,
3 porównania kroku czasowego,19 końcowych kontroli spójności. Model przybliżony;
nie potwierdza sprzętu, SOA, termiki, pełnego detektora OVP ani odporności ISO.
Po otrzymaniu recenzji powtórzono trzy skrypty recenzenta. SHA256 archiwum oraz
wszystkie 170 plików manifestu R2 są zgodne z wydaniem.

- E-02: recenzja otrzymana i przeanalizowana; sprawy poniżej pozostają otwarte.
- R1-01: SPRAWDZONE_NIEZALEŻNIE w analizie/modelu, do odbioru sprzętowego H-01.
- R1-02 / R2-02: poprawić metodę pomiaru VGS i prądu przed layoutem. Nie stosować
  propozycji masy DHO804 na SOURCE przy zasilaniu z powerbanku — jest niezgodna
  z instrukcją Rigola. Zalecane miejsce na mostek pomiarowy/bocznik Q1.
- R2-01: model potwierdza 10–27 ms przerwy po 50 µs zaniku ENABLE i możliwość
  restartu logiki. Rekomendacja autora: oddzielne krótkie podtrzymanie pomiarów
  i zapisu na P02; zakres do rozstrzygnięcia, obwód nie został zaprojektowany.
- R1-03: większe otwory, do sprawdzenia rzeczywisty przewód.
- R1-04 / R2-03: mate dobrany; zalecana zamiana stron BAT — żeński przy źródle,
  męski na H_BAT. W opublikowanym R2 jeszcze nie wprowadzona.
- B-01 / R2-04: dostępny detalicznie C6 i zgodny footprint; po wyborze zamiennika
  ponownie sprawdzić dynamikę dla jego tolerancji.
- M-01 / R2-05: mocowania radiatorów, termiki J7 i dostęp do TP1/TP2 przy Q1.

Przed integracją: H-01 odbiór na stole, w tym pełne VIN18,5V→VGS<0,5V≤100µs,
powrót po krótkim zakłóceniu, SOA i termika impulsu OVP przy już otwartym Q1.
SAFE_N nie oznacza gotowego VPROT. W integracji P04/P07 przed KPWR należy
potwierdzić stabilne VPROT przez≥300ms, także przy CORE z USB. Firmware nie
został zmieniony w pakiecie P01 ani podczas tej oceny. P07 pozostaje HOLD.

Kolejność: decyzje P01/P02 i metody pomiarowe → części/mechanika → ograniczona
poprawka przed layoutem i regresja → layout2L → DRC/Gerbery/wiercenia →
zamówienie → samodzielny odbiór P01 → integracja następnego modułu.
