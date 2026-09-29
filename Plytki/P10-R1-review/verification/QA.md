# QA P10-R1 — 27.09.2026

Status: CAD do recenzji. Sprzęt, wiązki i prototyp NIE ZBADANO.

| Kontrola | Wynik |
|---|---|
| Native ERC KiCad 10.0.6 | 0 naruszeń, 2 arkusze |
| Netlista vs części | 19 części/pól, 57/57 pinów, 15 sieci |
| Niezależny kontrakt elektryczny | 26/26 PASS; zgodność P02-R3/J10 i P03-R2/J8 |
| Niezależna geometria PCB | 21/21 PASS |
| Celowe błędy obwodu/PCB | 16/16 + 12/12 wykrytych |
| Native DRC / brakujące / parity | 0 / 0 / 0 |
| Wyłączenia pojedynczych naruszeń DRC | Brak |
| Reguły rzeczywistego DSN | 0,30 mm / 0,25 mm, przelotki 0,8/0,4 mm |
| Wylewki GND, niezależny graf geometrii | Jeden połączony obszar elektryczny |
| Czysta odbudowa | Identyczny odcisk geometrii, identyczne 2 pliki schematu; ponownie ERC/DRC 0 |
| PDF | 2×A3 schemat + 4×A4 poziomo PCB, każda strona wyrenderowana i obejrzana |

Domyślne pomijane klasy KiCad są wyszczególnione w `drc.json/ignored_checks`
(m.in. brak courtyard i filtry footprintów). „0” nie oznacza sprawdzenia każdej
możliwej reguły. Projekt nie zawiera doraźnych wyłączeń poszczególnych kolizji.
Kontrole geometrii obejmują kotwy, otwory, pad parity, odsprzęganie, TVS i tory H/L.

W toku generacji wykryto użycie domyślnych reguł eksportera DSN; poprawiono jawne
ustawienie netclass w route_critical i dodano kontrolę eksportowanego DSN przed
trasowaniem. Nie rozwiązano tego przez złagodzenie DRC. Końcowy router pracował
na zadanych 0,30/0,25 mm i via 0,8/0,4 mm. Wyniki pośrednie w routing/ poprzedzają
porządkowanie i opisy. Wynik wydania to verification/drc.json z provenance.

Przegląd wizualny objął obie warstwy, położenie D1 i masy, orientację układów,
oznaczenia przewodów, kotwy i wydruk 1:1. Usunięto konflikt opisu zasilania U2E
na schemacie oraz przeniesiono numery J1 nad rząd pól. PDF dolnej warstwy pokazuje
prześwietlenie od góry, bez odbicia lustrzanego. Łącznie 32 przelotki.

Raport `drc.provenance.json` zawiera skróty dokładnych źródeł, bibliotek, schematów
i PCB użytych do świeżej kontroli. `manifest.sha256.json` obejmuje dostarczony pakiet.
Hash PDF zapisano w `pdf-check.json`; clean build w `rebuild-check.json`.

Testy pinów i mutacji nie symulują ramp zasilania ani impulsów CAN. Nie wykonano
pełnej kompilacji ESP-IDF, pomiarów Ioff/brownout, badania obciążenia CAN/SD/DAQ,
EMC ani prób w samochodzie. Wspólnego firmware nie zmieniono; otwarte działania
integracyjne są w docs/INTEGRACJA.md. Nie ma potwierdzonego dekodera fabrycznego RPM Kia.

Przed produkcją: niezależna recenzja, wydruk 1:1, przymiarka przewodów/obudowy.
Przed podłączeniem do pojazdu: pozytywny odbiór stanowiskowy ODBIOR.md.
Pakiet nie zawiera gerberów. P07 pozostaje HOLD; wcześniejszych płytek nie zmieniano.
