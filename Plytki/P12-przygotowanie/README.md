# P12 — przygotowanie: kontrakty krawędzi A (1.10.2026)

**Status:** narzędzie i raport, bez schematu P12. Płytka połączeń powstanie, gdy będą pinouty P05, P06 i P11, a w wariancie pełnym także P04, P07 i P08 (`docs/CHMURA.md`, „Kolejne zadania”).

## Zawartość

| Plik | Co robi |
|---|---|
| `zrodla.json` | Skąd brać pinouty (gałąź git i plik), poziom i sloty płytek, kierunki sygnałów P02 R4 (jego `parts.json` ich nie ma), budżety prądu z dokumentów płytek |
| `src/kontrakty.py` | Mapa sieci J_BP wszystkich płytek i kontrole; wynik w `wyniki/` |
| `wyniki/KONTRAKTY.md` | Raport: błędy, źródła z wersjami, miejsca złączy dla P12, sieci, zasilanie |
| `wyniki/zlacza-P12.csv` | Miejsca złączy: poziom, slot, x w układzie stosu, z spodu płytki, typ IDC |
| `wyniki/kontrakty.json` | To samo dla programów (przyszły generator netlisty P12) |
| `src/proby.py`, `wyniki/proby.json` | Próby ujemne skryptu: 7 wstrzykniętych wad i próba zerowa, każda porównana z przebiegiem bazowym |

**Kontrole:**
- **Złącza:** wielkość IDC (2×5, 2×8 albo 2×10, bez dziur w numeracji) i piny nieparzyste inne niż GND (wypisane z uwagami płytki). Do tego środek złącza zmierzony w raporcie PCB płytki wobec slotu (S1 §5).
- **Sieci:** drugi koniec ma być na płytce wskazanej w kolumnie `plytka_docelowa`. Brak na płytce, która ma już pinout, to błąd; brak na płytce bez pinoutu oznacza stan „czeka”.
  - Na sieć ma być jeden nadajnik. Wyjątki to magistrale ADC_DOUTA i SPI3_MISO oraz pętla PG_SEND–PG_LINK.
  - Kontrola obejmuje też cele wskazane w obie strony i zbliżone nazwy (np. DAQ_OK / DAQOK).
- **Zasilanie:** piny 5V_SYS / 3V3_IO, budżety prądu wobec styków (ok. 1 A na styk, S1 §5) i zasilacza P02 R4.
- **Opis położenia J_BP P02 R4** w specyfikacji S1 wobec zmierzonej płytki.
- **Pojemność na szynach 5 V** (5V_SYS i szyny za kluczem / opornikiem do 1 Ω) wobec obciążenia pojemnościowego TSR 2-2450 z karty TRACO.

## Wynik 1.10.2026

**1 błąd (pojemność 5 V, niżej pkt 5), poza tym czysto.** 17 sieci jest kompletnych: P02 R4 ↔ P03 R6 ↔ P05 R3 ↔ P09 R2 ↔ P10 R2. 29 sieci czeka na P04, P06, P07, P08 albo P11. Próby ujemne: 8/8 z zerową.

**1.10 (po PR #7):** P05 R3 czytany ze schematu z chmury (`origin/p05-s1`, `docs/J_BP.csv`), a tabele z zadania zostały w `zrodla.json` jako `plan_piny`: skrypt porównuje schemat z planem pin po pinie (zgodne; nowa próba ujemna `schemat_inny_niz_plan`).

Ustalenia:
1. **Specyfikacja S1 §8 miała zły nagłówek:** „Pinout P02 R4 J_BP (2×10, slot S3, środek x = 80,0 mm)”. Slot S3 ma środek 133,5 mm i tam stoi J_BP na płytce P02 R4 (raport PCB: 133,5 mm). Poprawione w tej gałęzi; P02 R4 bez zmian.
2. **Zasilanie 5V_SYS:** budżety z dokumentów płytek LOGGER dają razem 1,09 A:
   - P03 0,5 A średnio (0,8 A w impulsie);
   - P05 0,14 A;
   - P06 0,18 A;
   - P09 do 0,2 A;
   - P10 0,07 A.

   P02 R4 ma TSR 2-2450 (2 A, bezpiecznik T1A po stronie wejścia) i trzy styki 5V_SYS na J_BP, czyli ok. 0,36 A na styk. Budżetów 3V3_IO płytki nie podają.
3. Wszystkie sygnały P09 i P10 oraz magistrala DAQ P05 mają na P03 R6 te same nazwy i po jednym nadajniku.
4. **PFAIL_N** idzie tylko do P03; na P04 jest NC (specyfikacja P02 R4, J12 pin 3).
5. **Pojemność na szynach 5 V przekracza limit TSR 2-2450 (do decyzji przy P05 R3 i P06 w S1):** P05 C1 i P06 C3 to po 470 µF za opornikiem 1 Ω (R1 / R6), czyli praktycznie wprost na 5V_SYS (stała 0,47 ms wobec startu TSR 5 ms). Razem z resztą płytek ok. **986 µF wobec 600 µF max** według karty TRACO TSR 2. Przy starcie oba kondensatory biorą ok. 2 × 0,47 A (szacunek z `P05-R2-review/docs/INTEGRACJA.md`), do tego ok. 1 A obciążenia: to granica 2 A, a przeciążenie TSR przechodzi w foldback (ryzyko restartów „czkawkowych”). Uwaga z P05 R2 („budżet trzeba przeliczyć dla P02 R4”) jest tym samym problemem. Możliwe kierunki: mniejsze C1/C3, ogranicznik udaru albo opóźnione załączanie na P05/P06, pomiar startu kompletu na stole.
6. **Geometria dla P12:** tabela złączy w raporcie. x jest w układzie stosu (x = 0 od panelu), z to spód płytki: poziom 1 — 8 mm, 2 — 34,6 mm, 3 — 56,2 mm, 4 — 77,8 mm, 5 — 99,4 mm (dno 8 mm, płytki 1,6 mm, dystanse z S1 §7).

## Aktualizacja

- **Po scaleniu gałęzi płytki:** w `zrodla.json` zmienić jej `ref` na `origin/main`.
- **P05 (zrobione 1.10):** źródło `csv` z `origin/p05-s1`; po scaleniu PR #7 zmienić `ref` na `origin/main`.
- **P06, P11, P04, P07, P08:** dopisać źródła, gdy powstaną pinouty.

Uruchomienie (Python 3, bez dodatkowych pakietów; najpierw `git fetch origin`):

```
python3 Plytki/P12-przygotowanie/src/kontrakty.py
python3 Plytki/P12-przygotowanie/src/proby.py
```
