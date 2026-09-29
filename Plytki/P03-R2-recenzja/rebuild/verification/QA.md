# Odbiór plików P03-R2

26.09.2026 · **PASS dla kontroli plikowych; pakiet do niezależnej recenzji. Sprzęt NIE ZBADANO.**

| Kontrola | Wynik | Dowód |
|---|---|---|
| ERC, pięć arkuszy A3 | 0 naruszeń | `erc.json` |
| Schemat / lista części / piny | 88 części, 421/421 pinów | `schematic-check.json`, `P03.xml` |
| Kontrakt v6.1 | 310 pozycji, 8 jawnych zmian, 0 nieoczekiwanych | `v61-compare.json` |
| Kontrakt R1 | Wszystkie stare piny sprawdzone; tylko 9 dopuszczonych zmian R2 | `function-checks.json`, ostatnia kontrola |
| Kontrole elektryczne netlisty | 48/48 PASS | `function-checks.json` |
| Celowe błędy netlisty | 33/33 wykryte właściwą kontrolą | `function-mutations.json` |
| Świeży DRC / niepołączone / różnice ze schematem | 0 / 0 / 0 | `drc.json`, `drc.provenance.json` |
| Kontrole PCB | 29/29 PASS | `pcb-checks.json` |
| Celowe błędy PCB | 15/15 wykryte właściwą kontrolą | `negative-controls.json` |
| Spójność masy | Jeden elektrycznie połączony zbiór miedzi GND | `ground-islands.json` |
| Tabele użytkowe | Netlista 421 pinów i interfejsy 88 pozycji zgodne z CAD; BOM 88 części | `table-checks.json` |
| Odtworzenie od zera | PASS, bez katalogu P02 i bez gotowych plików CAD | `standalone-rebuild.json`, `standalone-run.log` |
| Zachowanie oryginału R1 | 98/98 hashy zgodnych z oryginalnym manifestem | `original-R1-unchanged.json` |
| Oględziny PDF | Wszystkie 5 stron schematu i 4 strony PCB obejrzane; PDF PCB ponownie zrasteryzowany Popplerem | `visual-review.json`, `output/previews/` |

## Co kontroluje R2 dodatkowo

- Stan po resecie jest sprawdzany przed buforem, na wyeksportowanej netliście. Usunięcie każdego z 26 rezystorów ustalających stan ma własną próbę ujemną.
- Wspólny reset obejmuje EN MCU, MCP i P04. Test wykrywa odłączenie EN, pominięcie bufora, jego zamianę na push-pull i zwarcie R34.
- Numery pinów U4/U5/Q1 pochodzą z not producentów i są zapisane osobno w weryfikatorze. Sprawdzane są rozdzielenie SYS/M1 oraz kierunek D/S MOSFET-u.
- C3 jest sprawdzany względem **VDD=6**, z osobną mutacją odtwarzającą położenie przy MR=3 z R1. Sam DRC tego problemu funkcjonalnego nie rozstrzyga.
- Krótkie odcinki od buforów do R36–R40 i główny tor zasilania są zamrożone przed routingiem, a ich geometria kontrolowana po imporcie.
- Masy C13/U5 otrzymały dwie jawne przelotki. Dodatkowy graf wypełnień, padów i przelotek zatrzymuje budowę przy odizolowanym obszarze GND.
- Referencje, nazwy interfejsów i oznaczenia KEY muszą być poza obrysem sąsiedniej części i wskazywać najbliższy właściwy element. `KEY2` przy J3 jest obrócone o 90°, aby zmieścić się obok R15; limit położenia nie został zwiększony.
- Raport DRC zawiera hashe rzeczywistych wejść. Zmiana plików podczas kontroli jest błędem wykonania, **nie** zaliczoną mutacją.

## Odtworzenie niezależnego katalogu

Do nowego, pustego katalogu skopiowano tylko `src/`, `reference/`, `docs/`, README i `routing/P03.ses`. Utworzono puste katalogi wyjściowe. Nie kopiowano `eda/`, gotowych raportów ani P02. Uruchomiono pełne `src/run_release.py`, łącznie z ERC, DRC, testami ujemnymi i eksportem PDF. Kod wyjścia: 0. Po tym teście poprawiono filtr archiwizacji, aby wykluczał katalog kopii testowych, ale zachowywał raport `negative-controls.json`. Skrypty tworzące CAD nie zmieniły się; końcowy DRC powtórzono, a zawartość ZIP sprawdzono osobno.

Skrypt `rebuild-compare.py` porównuje dwie wersje: położenia/pady/opisy, ścieżki i przelotki, granice stref, rysunki, sieci, reguły, arkusze schematu i biblioteki. Te kategorie są zgodne. Wypełnienia porównano geometrycznie przez XOR: F.Cu 0 mm², B.Cu 4,475×10⁻¹⁰ mm². Różna kolejność punktów na stykających się granicach oraz reszta zaokrągleń KiCada nie są zmianą tras. Dla wypełnień jawny limit numeryczny wynosi 10⁻⁸ mm²; nie zmienia on reguł DRC, odstępów ani szerokości ścieżek.

## Ponowne sprawdzenie

1. Według `docs/ODTWARZANIE.md` uruchomić KiCad Python: `python src/run_release.py`.
2. Uruchomić `python verification/check_tables.py` po każdej zmianie tabel.
3. Obejrzeć wszystkie strony obu nowych PDF. Automatyczne kontrole nie oceniają czytelności całego arkusza ani fizycznego zazębienia modułów.
4. Po dodaniu dokumentów/raportów odświeżyć manifest i archiwum; porównać hash PCB z `drc.provenance.json`.

Kontrola DRC używa wszystkich ważności i reguł projektu, bez indywidualnych wykluczeń. Standardowe kategorie pomijane przez KiCad są jawnie wymienione w `drc.json` (`ignored_checks`); nie należy interpretować zera jako certyfikacji elektrycznej. Robocze pliki w `routing/` pokazują etapy przed uzupełnieniem mas i nadruków — projektem końcowym jest wyłącznie `eda/P03.kicad_pcb`.

## Granice wyniku

Nie wykonano pomiarów spadków napięcia, prądu zwrotnego, zboczy SPI, resetu, temperatur ani RF. Nie potwierdzono fizycznego spasowania P03–P05. Warunki i formularz: `docs/ODBIOR.md`. Błędy firmware związane z uruchomieniem AD7606B/czasem ramki SPI z recenzji P05 pozostają poza zakresem tej rewizji. P07 nadal HOLD. Brak Gerberów i zatwierdzenia do produkcji.
