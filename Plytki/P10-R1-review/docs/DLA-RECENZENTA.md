# P10-R1 — wejście do recenzji

Cel: pasywny odbiór CAN jako źródło kontekstu czasowego dla pomiarów EGR. Jedna płytka80×70 mm
do montażu ręcznego. Dokumentem kontraktowym są piny natywnego schematu oraz snapshoty
P02-R3/J10 i P03-R2/J8 w `reference`. Poprzednie pakiety zachowane bez zmian.

Zmiany względem karty P10 w v6.1-rc1:

1. TCAN1051VDRQ1: S i TXD stale3V3_IO. S nie jest programowalne. CAN_TX z CORE kończy
   się na TP6. Usunięto potrzebę buforowania TX, bo urządzenie ma odbierać pasywnie.
2. Bufor74LVC125AD z Ioff znalazł się na **RX**. Chroni wyłączone P10 przed podciąganiem
   CAN_RX do3V3_CORE przez R30 P03. Bez niego RXD TCAN z nieaktywnym VIO otrzymywałby
   zewnętrzne napięcie. Ioff i zachowanie przy częściowym zaniku wymagają pomiaru.
3. PESD2CAN SOT23 na wejściu W3; piny1/2 równoważne, tutaj1=L,2=H,3=GND.
   Ścieżki H/L i odsprzęganie wykonane ręcznie i zablokowane przed trasowaniem.
4. Dopasowano do aktualnego CORE:IDC6 KEY4, nie starszy kabel CAN10p. Zasilanie LV10 4p.
5. W3 na stałe wlutowana para120 Ω do OBD6/14; bez dodatkowego wewnętrznego złącza.
   OBD4/5/16 NC. Masa wspólna przez główne zasilanie urządzenia jest warunkiem użycia.
6. Nie ma120 Ω na PCB. Pierwsze testy wymagają stanowiska z prawidłową magistralą,
   terminacją na końcach i aktywnym drugim węzłem ACK.

Sprawdzić niezależnie: pinySOIC8/SO14/SOT23, domyślny stan przy zanikach każdej szyny,
ścieżkę RX wraz z istniejącą P03, rzeczywistą numerację wtyku OBD i zaciskania IDC,
budżet opóźnień/kolejki CAN, wspólne odniesienie masy i sposób rozłączenia wiązek.
Rezerwa10 mA/szynę jest założeniem do bilansu P02, nie zmierzonym poborem.

Pliki do oceny: dwa arkusze KiCad, PCB, PDF montażu/miedzi, `docs/ZAKUPY.md`,
`docs/WIAZKI.md`, `docs/INTEGRACJA.md`, `verification/QA.md`, `ODBIOR.md`.
`verification/electrical-checks.json` i `pcb-checks.json` zawierają także wykryte
celowe regresje. Regeneracja i znaczenie wyników w `REPRODUKCJA.md`.

Należy rozdzielić odbiór płytki od odbioru loggera. P10 nie sprawia, że samochód zaczyna
nadawać odpowiedzi PID0C. Nie ma jeszcze potwierdzonej ramki RPM Kia w tym pakiecie.
Wspólne firmware wymaga scalania wcześniejszych poprawek oraz testu obciążenia CAN/SD/DAQ.
Nie deklarujemy fizycznych prób, zgodności automotive całego PCB ani zakończonego odbioru.
