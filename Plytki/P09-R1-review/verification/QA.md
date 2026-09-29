# QA P09-R1 — 27.09.2026

Status: CAD do recenzji. Sprzęt, rzeczywisty regulator modułu i przymiarka mechaniczna NIE ZBADANO.

| Kontrola | Wynik |
|---|---|
| Native ERC KiCad 10.0.6 | 0 naruszeń, 4 arkusze |
| Netlista vs części | 48 części, 147/147 pinów, 39 sieci |
| Niezależny kontrakt elektryczny | 43/43 PASS; zgodność P02-R3/J9 i P03-R2/J7 |
| Niezależna geometria PCB | 20/20 PASS |
| Celowe błędy obwodu/PCB | 15/15 + 10/10 wykrytych |
| Funkcja temperatury kompilowana TCC | 27 przypadków PASS; 3/3 regresje wykryte |
| Native DRC / brakujące / parity | 0 / 0 / 0 |
| Wyłączenia pojedynczych naruszeń DRC | Brak |
| Wylewki GND, niezależny graf geometrii | Jeden połączony obszar elektryczny |
| Czysta odbudowa | Ten sam odcisk geometrii, identyczne 4 pliki schematu; ponownie ERC/DRC0 |
| PDF | 4×A3 schemat + 4×A4 poziomo PCB, każda strona wyrenderowana i obejrzana |

Domyślne pomijane klasy KiCad są wyszczególnione w `drc.json/ignored_checks` (m.in. brak courtyard i filtry footprintów); „0” nie oznacza uruchomienia nieistniejącego testu dla każdej możliwej reguły. Projekt nie zawiera doraźnych wyłączeń poszczególnych kolizji. Mechanikę modułu i wymiary podpór oceniamy także oddzielnie; nominalne podpory nadal wymagają przymiarki.

Raport `drc.provenance.json` zawiera skróty dokładnych źródeł, bibliotek, schematów, PCB i patcha firmware użytych do świeżej kontroli. `manifest.sha256.json` obejmuje cały dostarczony pakiet. Hash PDF zapisano w `pdf-check.json`.

Przegląd wizualny usunął kolizje symboli z ramką schematu i przesunął napis JP1 OPEN pod właściwy selektor. Miedź, położenie części, oznaczenia listwy, kotwy, dostęp do termopar i wydruk1:1 zostały obejrzane. Odbicie warstwy dolnej jest opisane jako prześwietlenie, nie szablon trawienia.

Nie wykonano pełnej kompilacji ESP-IDF, badań EMC, testu brownout ani pomiarów temperatury. Poprawka firmware obejmuje sam tor MAX31856; integracja zmian P05/P08 pozostaje osobno. Brak modułu jest wykrywany przez konfigurację, ale stała poprawna ramka nie dowodzi świeżości konwersji.

Do zatwierdzenia produkcji: przymiarka zakupionego egzemplarza, wybrany VIN i poziomy SPI, niezależna recenzja. Do użycia urządzenia: pomiary z formularza ODBIOR. Gerberów nie wygenerowano na podstawie niepotwierdzonej mechaniki.
