# QA P06-R1 / 27.09.2026

Wynik plików: **PASS, do niezależnej recenzji i przymiarki**. Sprzęt: **NIE ZBADANO**. Nie jest to dopuszczenie pracy przy ECU ani zamknięcie odbioru.

| Kontrola | Wynik |
|---|---|
| Natywne ERC KiCad 10.0.6, wszystkie severities | 0 naruszeń, 6 arkuszy |
| XML eksportowany z finalnego schematu vs opis części | 208/208 pinów; 74 elementy, 43 sieci; brak brakujących/dodatkowych części |
| Natywne DRC, refill, wszystkie błędy ścieżek i schematic parity | 0 naruszeń / 0 niepołączonych / 0 różnic schemat-PCB |
| Wymagania elektryczne z XML | 32/32 PASS |
| Kontrole geometrii i padów z finalnej PCB | 24/24 PASS |
| Celowe błędy obwodu / PCB | 19/19 oraz 8/8 wykryte |
| READY z rzeczywistej netlisty bramek | 8/8 kombinacji |
| Spójność GND z geometrii wypełnionej miedzi i padów | 1 połączona składowa |
| Odtworzenie od pustego katalogu CAD | PASS, identyczny odcisk geometrii, świeże ERC/DRC 0 |
| Nazwy przenośne na Windows | PASS; arkusz CONNECT zamiast zarezerwowanego CON |
| PDF | 6 stron A3 schematu + 4 strony A4 PCB, komplet obejrzany |

Geometria: 120 × 100 mm, 2 × 70 µm, 77 footprintów (53 elementy na PCB, 20 zakończeń/testpadów, 4 mocowania), 545 pozycji miedzi ścieżek/via, w tym 34 via. SW1 jest elementem panelowym. Wszystkie 73 referencje elementów/terminali PCB są widoczne przed montażem. Termiki zachowane; `routing/solid-pads.json` jest pustą listą.

Odcisk geometrii: `0e00b540a813ee2a4acf80279cdb4a3475ca063af956764ac9cb95b64b1eefc8`. Szczegóły i zakres porównania w `rebuild-check.json`; wynik DRC i hashe wejść w `drc.provenance.json`. Raporty pośrednie trasowania nie są oceną wydania. Nie zastosowano wyjątków DRC; domyślnie nieaktywne reguły KiCad są wymienione w `ignored_checks` natywnego raportu.

Testy nie kopiują wyłącznie wzoru z generatora: wczytują eksportowane połączenia, MPN, wartości i rzeczywiste pady/trasy. Kontrole negatywne zmieniają m.in. pinout INA/TO92, wspólny styk SW1, 10K zamiast 100K na CS, dzielnik, filtr, OE DOUT, READY, szerokość mocy, brak Kelvina, średnicę otworów i kotwę. Weryfikacja geometrii nie zastępuje elektromagnetycznej ani termicznej analizy sprzętu.

## Domknięte problemy wykryte w tej iteracji

- Obciążenie INA240: 10,2 kΩ zamiast 4 kΩ; filtr dostosowany do pomiaru trendu 2 ksps.
- Numeracja SOIC/TO92, cztery wyprowadzenia PBV i wspólne 2/5 S6A sprawdzone w kartach producentów.
- Suche styki pomocnicze i prąd przez zewnętrzny pull-up przy braku zasilania: jawne obciążenie R21, R8=100K, bleed R24.
- Odsunięte napisy, osobny odsyłacz TP3, rozdzielone etykiety Kelvina na schemacie.
- Nazwa pliku zarezerwowana w Windows usunięta, kontrola dodana do procesu.
- Generator tworzy plik projektu przed ERC: bez niego KiCad pomijał lokalne tabele bibliotek przy odtworzeniu od zera.
- Test czystego odtworzenia i manifest wykrywają brakujące pliki oraz nieaktualne raporty.

## Pozostaje do sprawdzenia na fizycznych częściach

M01 i E01-E20 z ODBIOR.md. Szczególnie: PBV i otwory/luty przewodów, konkretny impulsowy R6, pasowanie wtyków (P11 jeszcze niezatwierdzona), napięcie minimalne i histereza MCP120-450, pobór/HOLD całego urządzenia, SPI z P03/P05, kalibracja ±6 A, nagrzewanie 10 A, przebieg PWM/aliasowanie. R21 jest celowo ciepły; READY nie sprawdza wzorca ani ciągłości bocznika. Nie ma wyników pomiarów ani podstaw do oznaczenia tych punktów jako zaliczone.

## Powtarzanie procesu kolejnych PCB

Najpierw kontrakt pinów i mechanika konkretnych MPN, następnie schemat/PCB. Przed wydaniem: świeże ERC/DRC z hashami, porównanie sąsiadujących modułów, testy negatywne na wyeksportowanych danych, pełny przegląd wizualny PDF, odtworzenie po usunięciu wygenerowanego CAD, kontrola nazw Windows i manifest archiwum. Wynik komputerowy i formularz odbioru sprzętu pozostają osobnymi dokumentami.
