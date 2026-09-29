# Stan weryfikacji pakietu v2

Data: 2026-09-21.

## Wykonano

**15 testów narzędzia do logów — wszystkie przechodzą.** Sprawdzają: zgodność rozmiarów struktur, zapis i odczyt, CRC, wykrycie urwanego bloku, odrzucenie nieprawidłowej długości bloku, monotoniczność czasu, **wszystkie sześć permutacji mapowania pinów dające ten sam ratio**, zgodność wstecz z plikami wersji 1 (mapowanie `supply_pin`), zwrot NaN zamiast fałszywego zera przy nieznanym mapowaniu, wpływ `full_scale` na przeliczenie napięć, zastosowanie zmierzonego zera prądu, eksport CSV, generowanie raportu HTML i przegląd zdarzeń NDJSON razem z odpornością na uszkodzoną linię.

```text
python -m unittest discover -s tests -p "test_*.py" -v
Ran 15 tests — OK
```

**Przykład `examples/synthetic.egr`** — 4000 próbek, osiem kanałów, 2 kS/s, wersja formatu 2. Zawiera celowo zasymulowany krótki zanik sygnału pozycji (przy 1,0 s) i skok masy czujnika do 0,42 V (1,40–1,55 s). Do tego `examples/events.ndjson` z przykładowymi triggerami, znacznikiem, podsumowaniami sekundowymi i dwoma punktami HOT-SOAK. **To nie jest dowód, że takie uszkodzenie występuje w samochodzie** — to dane do sprawdzenia narzędzi. Czytnik potwierdza stały krok 500 µs i brak błędów CRC.

## Przygotowano, ale nie uruchomiono

**`tests/test_control.c`** — dziewięć testów czystej logiki: permutacje pinów, wymagane 2 s stabilności i timeout IDENTIFY, ratio i pozycja także przy ujemnym zakresie, prąd liczony ze zmierzonego zera, sześć osobnych blokad wywracających stan w FAULT, brak ARM blokujący ruch a nie stan READY, zapis prądu zerwania w FRICTION, kasowanie kampanii HOT-SOAK przez FAULT, limity rozkazów. **W środowisku, w którym powstał pakiet, nie było kompilatora C**, więc nie zostały ani skompilowane, ani wykonane. Uruchom je pierwszym wieczorem, zanim zaczniesz lutować:

```text
gcc -std=c11 -I firmware/main -o test_control tests/test_control.c firmware/main/control.c -lm
./test_control
```

**Projekt ESP-IDF** — nie skompilowany. Brak toolchainu i sprzętu. Nie deklaruję poprawnej kompilacji, działania peryferiów ani żadnej konkretnej przepustowości na podstawie testów w Pythonie.

## Nie wykonano

ERC/DRC w programie EDA, routingu PCB, pomiarów napięć, prądów, opóźnień, temperatury, EMC ani impulsów automotive. Pliki CSV w `hardware/` to lista montażowa i lista sygnałów, **nie netlista KiCad**. Źródła dokumentacji producentów zostały zebrane przy v1; w v2 nie były odpytywane ponownie.

## Otwarte ryzyka techniczne

| Element | Co trzeba rozstrzygnąć | Jak v2 ogranicza skutek |
|---|---|---|
| Rejestry AD7606B w software mode | adresy i bity dla Twojej rewizji | weryfikacja odczytem i automatyczny powrót do hardware mode |
| Mapowanie pinów 4/5/6 | dwa źródła w projekcie mówiły różne rzeczy | IDENTIFY sprawdza sześć permutacji i wymaga jednoznaczności; nic nie jest zaszyte |
| Złącza OEM | obudowa, klucze, orientacja CUD87 | zakup złączy dopiero po fotografii i pomiarze (paczka 3) |
| Limity zaworu | brak potwierdzonych OEM prądów i temperatur | limity rozruchowe w profilu, twardy trip ±4 A, ostrożny LEARN |
| Ochrona wejścia | brak aktywnego odcięcia OVP w wersji bazowej | TVS + P-MOS + bezpiecznik; LM74800EVM jako opcja, gdy uznasz za konieczne |
| Redundancja nadzoru | v2 ma jeden supervisor zamiast trzech | świadomy kompromis na rzecz mniejszej liczby błędów montażowych; opisany w `01-projekt.md` §6 |
| Przepustowość | `esp_timer` z dyspozycją w zadaniu | domyślnie 2 kS/s, co dla tej usterki wystarcza; powyżej ~5 kS/s trzeba timera sprzętowego |
| Adapter L1 | bocznik i dwie pary styków zmieniają obwód | wariant L2 (back-probe) jako pierwszy krok, bez ruszania złącza |
| SD i FAT | brak rotacji plików i odzyskiwania po zaniku zasilania | format znosi urwany ostatni blok; przy 2 kS/s limit 4 GiB to 18,6 h |
| Bezpieczeństwo | projekt warsztatowy | brak deklaracji SIL/ASIL i odporności na dowolną pojedynczą awarię |

## Czego ten pakiet nie zmienia

Nie zmienia tego, że **najtańsze rozstrzygnięcie kampanii leży w procedurze v3 i skopie**, a EGRLab wchodzi po niej. Budowa tego urządzenia to kilkanaście wieczorów; Test A, Krok 2, test opalarką i wiggle to weekend. Kolejność w `02-procedury.md` §„Jak to się ma do procedury skopowej v3" jest tam nie z uprzejmości, tylko dlatego, że rozpięcie CUD87 zaburza hipotezę H6.
