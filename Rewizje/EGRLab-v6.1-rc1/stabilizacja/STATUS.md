# Stabilizacja EGRLab 6.1-rc1 — 23.09.2026

Zamknięto offline zgłoszone usterki V6 i dwie dodatkowo znalezione. Zachowano V6 jako bazę z SHA256. Powstały testy wykazujące błędy bazy, osobne różnice poprawek, kontrole pełnego grafu przewodów i import KiCad porównany przez rzeczywisty eksport netlisty. **To kandydat do odbioru projektu, nie wydanie dopuszczone do zamawiania PCB.**

| ID | Zmiana / rozstrzygnięcie | Dowód |
|---|---|---|
| F01 | Osobny VSENSE z P02 do P05, F100mA na źródle; Mini-Fit 14p, bez zmiany LV | baseline-fail, electrical-pass, F01.diff |
| F02 | Aktywne HIGH SENSOR_HEALTHY, lokalny FAULT_N i bufor Ioff; pull-down na CORE; błąd zatrzaskiwany także w SENSOR_CHECK | health-before-fix, test_health, test_v61 |
| F03 | PANELSAFE.5/.6 NC, nadal korpus 10p | F03.diff, test portów |
| F04 | VMOTOR PC4 7,62mm, SUPPLY MSTB 5,08mm; bez zmiany pinoutu | F04.diff, dokumentacja Phoenix |
| F05 | OVP nominalnie około 18V, kalibracja pokojowa i osobna próba temperaturowa | F05.diff, instrukcja P01 |
| F06 | Migawka wejść z czasem odczytu; >100ms bez świeżych danych daje INPUTS_STALE w TEST | test_health, kontrola integracji w app_main |
| F07 | Usunięta nieużywana kopia STATUS_LED na PANELCORE.6, LED na CORE pozostaje | F07-before-fix, F07.diff |
| T01/T02 | Graf obejmuje zasilania i masę; kontrola odbiorników z jawnymi wyjątkami | checks.py, 10 mutacji |

Rejestr zawiera kryteria i odnośniki, nie tylko opis. „VERIFIED_OFFLINE” oznacza zamknięcie na poziomie dokumentacji i programu. Nie oznacza zmierzonego działania sprzętu. Stare 79 testów przechodziło mimo F01; nowy test rzeczywiście wykazuje VPROT/P05 na zamrożonym V6. Kontrola grafu wykrywa także dwie rozłączne grupy z pozornie poprawną listą uczestniczących płytek.

### Zakres sprawdzony

- Wszystkie 225 pozycji mapy wiązek (włącznie z NC), zgodność obu końców, pełna osiągalność sieci zasilania i sygnałów, nieużywane odnogi, zgodność grupy LV.
- Rzeczywiste piny bramek interlock, OC i HEALTHY; wyjścia otwarte SAFE_N, podciągania właściwych domen; zachowanie Ioff pozostaje również przedmiotem odbioru sprzętowego.
- Statyczny model ochrony P01: 39 kontroli i analiza wrażliwości 5000 zestawów parametrów. Oddzielny test potwierdza zgodność całego zintegrowanego obwodu P01 z tym modelem, z jawną korektą zasilania R30 z V6. To nie symulacja SPICE tranzystorów ani wynik load dump.
- Program: FAULT i brak samoczynnego wznowienia w siedmiu stanach TEST, limit wieku wejść z osobnym kodem błędu; regresja ADC, SD, logów i profili. Wyniki uruchomień znajdują się w verification/.
- KiCad 10.0.6: 16 projektów, eksport XML wszystkich elementów i połączeń zgodny z modelem; niesfiltrowane raporty ERC w eda/. Role pinów i zasięg sprawdzenia opisuje eda/README.md.

### Co nadal blokuje dopuszczenie do layoutu

1. Import pinowy EDA wymaga ułożenia obwodów funkcjonalnie, końcowej kontroli symboli oraz pełnego przypisania footprintów. Część pinów kupnych modułów jest jeszcze nazwana funkcjami, a nie numerami fizycznych padów. Wybrane footprinty P01 są kandydatami. Nie wystawiono na tej podstawie zgody na layout.
2. Trzeba zamknąć rysunki mechaniczne konkretnych złączy, nośnika Waveshare, B2B CORE–DAQ, kotew i radiatorów. Wymiary modułów z poprzednich wersji są rezerwą obrysu, nie sprawdzonym rozmieszczeniem wszystkich części.
3. Potrzebny osobny, niezależny przegląd tego RC. Nie przedstawiam samokontroli jako recenzji Opusa; gotowy zakres jest w PRZEGLAD-NIEZALEZNY.md.

P01 jest pierwszym modułem do zakończenia tych trzech czynności, potem P05 z P03/B2B, następnie P07. Brak pomiarów gotowego sprzętu nie blokuje samego projektu PCB prototypu, ale nie wolno oznaczać go jako sprawdzony w samochodzie. Zamówienie wymaga dodatkowo gotowego layoutu 2L, DRC, kontroli Gerberów i wierceń. Aktualne statusy: bramki-modulow.csv.

### Zasada dalszej pracy

Nie twórz pełnej V7 po każdej uwadze. Zmieniaj ten kandydat małymi poprawkami z ID, testem przed poprawką, różnicą i dowodem po poprawce. Zmiana pinu lub interfejsu otwiera ponownie bramkę obu sąsiednich modułów. Po zatwierdzeniu schematu EDA staje się źródłem połączeń, a CSV/BOM są eksportami — dopiero wtedy wycofuje się generator modelu. Nie wolno utrzymywać dwóch ręcznie edytowanych, konkurencyjnych netlist.

Ograniczenia pozostają konkretne: rzeczywisty pinout posiadanego zaworu i identyfikacja wymagają pomiaru, termika i zakłócenia wymagają stołu, a przyczynę P0404 trzeba ustalić z danych auta. Ta stabilizacja nie potwierdza jeszcze diagnozy zaworu.

Źródła nowych decyzji: [TPS2553 Rev F](https://www.ti.com/lit/ds/symlink/tps2553.pdf), [AD7606B Rev B](https://www.analog.com/media/en/technical-documentation/data-sheets/ad7606b.pdf), [LM2936](https://www.ti.com/lit/ds/symlink/lm2936.pdf), [LM2903](https://www.ti.com/lit/ds/symlink/lm2903.pdf), [PC4 wtyk 1804917](https://www.phoenixcontact.com/en-us/products/pcb-plug-pc-4-3-st-762-1804917), [PC4 gniazdo 1804807](https://www.phoenixcontact.com/en-us/products/pcb-header-pc-4-3-g-762-1804807). Pozostałe źródła: docs/08-zrodla-i-zmiany.md i materiały P01.
