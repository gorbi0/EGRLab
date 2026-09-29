# Przegląd i przejście do layoutu

Stan 23.09.2026: sprawdzenia autora zakończone; recenzja niezależna NIE WYKONANA;
PCB/layout, DRC, pomiary sprzętowe NIE WYKONANE. Nie stawiać znaków PASS dla etapów,
które dopiero są opisane.

| ID | Do rozstrzygnięcia | Kryterium zamknięcia |
|---|---|---|
| E-01 | Niezależny przegląd schematu i warunków granicznych | Recenzent podaje pin/sieć/warunek i dowód błędu albo potwierdza sprawdzenie. Uwagi trafiają do rejestru; brak zmian „przy okazji”. |
| M-01 | Mocowanie dwóch radiatorów | Rysunek konkretnego wykonania TO-220, pozycje kołków/śrub i dostęp do śrub przeniesione do footprintu, zweryfikowane 1:1. |
| B-01 | Zamknięcie zakupów | Dokładne dostępne MPN dla H4, C1 i złącza J6. Sprawdzenie maksymalnych gabarytów i średnic wyprowadzeń, w szczególności TO-220 względem otworu footprintu. Zamienniki ze zmianą w rejestrze. |
| L-01 | PCB 2L | Placement, ścieżki, płaszczyzny, DRC, porównanie PCB–schemat, odczyt Gerberów niezależną przeglądarką. |
| H-01 | Odbiór P01 na stole | Wypełniony protokół ODBIOR.md, bez przenoszenia wyników obliczeń do rubryki pomiarów. |

## Zakres recenzji E-01

- Orientacja D2/Q1; brak obejścia odłącznika przez body diode i radiator.
- Domyślny OFF bez AUX5, startup MCP120, wspólna sieć OC/OK, INHIBIT.
- OVP/UVLO/histereza, obciążenie TL431, ESR C9+R2, tolerancje i temperatura.
- Praca Q2/Q4 z wybranym 2N5401YBU; budżet czasu wyłączenia wraz z C5/C6.
- Wyjście SAFE_N przy zaniku zasilania P01 i nadal obecnym 3V3_IO.
- Energia TVS, SOA Q1 i regeneracja: rozdzielić przyjęty cel od wyniku pomiaru.
- Konkretne footprinty i numeracja; nie wystarcza samo „TO-92/TO-220”.

ERC i porównanie połączeń wykrywają błędy przeniesienia projektu do CAD; nie
udowadniają poprawności samej architektury. Test mutacyjny potwierdza działanie
kontroli regresji, nie pełne pokrycie wszystkich możliwych awarii.

## Jak poprawiać

Zamrozić otrzymaną paczkę. Każda uwaga ma ID, wagę, dowód, decyzję i kontrolę,
która wykryje powtórzenie błędu. Kolejny pakiet P01-R2 powstaje tylko dla zmian
wynikających z przeglądu. Po zmianie elektrycznej ponownie XML/porównanie/ERC;
po zmianie footprintu także pad mapping i kontrola wymiarów. Po poprawkach recenzent
sprawdza różnicę i punkty dotknięte zmianą. Nie przenosić prac na P07.

## Powtórzenie kontroli

W katalogu pakietu, z KiCad CLI 10 i Pythonem 3:

```text
kicad-cli sch export netlist --format kicadxml -o verification/P01.xml eda/P01.kicad_sch
kicad-cli sch erc --format json -o verification/erc.json eda/P01.kicad_sch
python src/verify.py
python src/check_package.py
```

Nie wykonywać `build_schematic.py` po ręcznej edycji jako sposobu na „naprawienie”
wyniku testu. Eksport i porównanie mają badać rzeczywisty zapis edytora.
