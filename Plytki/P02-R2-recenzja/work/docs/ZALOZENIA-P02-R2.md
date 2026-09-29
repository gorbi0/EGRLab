# P02-R2 — kontrakt rewizji

P02 zasila szyny 5V_SYS i 3V3_IO, rozdziela LV03…LV10, podaje VPROT do P07 oraz VPROT_SENSE do P05. HOLD podtrzymuje tylko elektronikę. MCU i firmware pozostają poza zmianą tej płytki.

Wymagania: 160×120 mm; FR4 1,6 mm; dwie warstwy miedzi 70 µm; montaż THT z U5 na posiadanym adapterze SO14; złącza, otwory mocujące i kotwy wiązek według R1. Obciążenie VMOTOR maks. 5 A, suma elektroniki maks. 6 W na VLOG_RES. Bank 3×22 mF/35 V, Ceff≥52,8 mF, cel podtrzymania 50 ms przy VLOG_RES≥7 V.

R2 zamyka cztery uwagi z recenzji: obwiednie progów, filtrację sprzężenia, ochronę TP3 oraz czytelność schematu. Zmienione elementy: R5…R11, C14/C15; nowe R18…R20 na PCB i C16 na adapterze U5. Dodatkowo dokładne MPN Mini-Fit Au i F1. R17 pozostaje poza PCB na oddzielnym radiatorze/blaszce.

HOLD_READY jest wskaźnikiem napięciowym. Podtrzymanie kwalifikuje operator (15 s) po wykonaniu odbioru obciążeniowego. Nie ma implementacji tego opóźnienia w CORE; J12.3 pozostaje NC na P04. Szczegóły progów, ograniczeń i strat zawiera `HOLD-ANALIZA.md`.

Stan docelowy wydania: ERC i DRC bez naruszeń; zgodność każdej sieci; kontrole geometrii; rzeczywiste mutacje sprawdzające czułość testów; natywne wydruki CAD; rejestr otwartych pozycji. Stan sprzętu: NIE ZBADANO. Wcześniejsza karta R1 jest archiwum w `reference/R1-docs/`.
