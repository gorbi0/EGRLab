# Recenzja P01-R2-review (bramka E-02)

23.09.2026 · recenzent: Claude (Opus 5.5) · przedmiot: `../P01-R2-review/` w stanie otrzymanym, bez zmian w paczce. Archiwum `P01-R2-review.zip` zgodne z plikiem `.sha256` (17f7d3d4…54ee).

**Wynik: w schemacie R2 nie ma błędu blokującego.** Poprawka R1-01 działa — sprawdziłem ją niezależnie. Przed layoutem trzeba jednak podjąć dwie decyzje, R2-01 i R2-02, bo jeden z wariantów każdej z nich zmienia PCB. Pozostałe uwagi dotyczą wiązek, zakupów i layoutu. Otwarte zostają M-01 i B-01 z pakietu.

Dowody w `model/`: wrapper ngspice (DLL z KiCad 10, bez numpy), trzy skrypty i `wynik.txt`. Skrypty czytają talie z `../P01-R2-review/simulation/decks/`.

## Rejestr uwag

| ID | Waga | Krótko |
|---|---|---|
| R2-01 | WAŻNE — decyzja przed layoutem | Zadziałanie OVP, UVLO albo INHIBIT trwające 50 µs zdejmuje VPROT na 10–27 ms, co oznacza restart CORE |
| R2-02 | WAŻNE — decyzja przed layoutem | Kryteriów ODBIOR 7 (VGS, ładunek gałęzi Q1) w obecnej formie nie da się zmierzyć posiadanym sprzętem |
| R2-03 | drobne | Złącze BAT: po stronie akumulatora, czyli pod napięciem, są styki męskie |
| R2-04 | drobne (B-01) | C6 w TME dostępny tylko hurtowo |
| R2-05 | drobne (L-01) | J7: pady 6 mm na miedzi 70 µm; położenie TP1/TP2 |

Status uwag R1 według PROCES.md:
- **R1-01:** SPRAWDZONE_NIEZALEŻNIE (model i rachunek; pomiar w H-01).
- **R1-02:** POPRAWIONE_W_PROJEKCIE, ale patrz R2-02.
- **R1-03:** POPRAWIONE_W_PROJEKCIE; dopasowanie rzeczywistego przewodu otwarte.
- **R1-04:** dobór zamknięty; patrz R2-03.

---

## R2-01 — krótkie zadziałanie zdejmuje VPROT na 10–27 ms

**Warunek:** Q1 jest włączony, a ENABLE opada na krótko. Przyczyną może być impuls powyżej 18 V, krótki spadek poniżej UVLO albo dotknięcie J3.

**Mechanizm:** Q2 w ciągu kilkunastu µs dociąga bramkę do VS i rozładowuje C6 do VSG ≈ 0. Po powrocie ENABLE bramka musi zejść od VS do plateau przez R21∥R22 = 82,5 kΩ na C6 = 1 µF, czyli z τ ≈ 82 ms. Q1 pozostaje więc wyłączony przez 10–27 ms, choć VPROT jest nadal naładowane i ponowne załączenie nie wymagałoby żadnego kształtowania prądu.

**Dowód** (`krotkie_zadzialanie.py`): talie autora, ENABLE niskie przez 50 µs, 220 µF plus odbiornik stałej mocy 3 W, który wyłącza się poniżej 6,5 V.

| Wariant | Q1 wyłączony | VPROT |
|---|---|---|
| R1, Vt 1–3 V | 0,12–0,32 ms | spadek o 0,1–0,3 V, bez skutku |
| R2, Vt 1–3 V | 10,4–27,3 ms | poniżej 6,5 V po ~5,7 ms; przetwornice stoją do 10,8–27,3 ms |

Wartość 6,50 V w wydruku to punkt, w którym wyłącza się model odbiornika, a nie rzeczywisty poziom napięcia.

Energia zgromadzona w 220 µF między 14 V a 6,5 V to 16,9 mJ. R2 przetrwa taką przerwę tylko przy odbiorze poniżej ~0,6–1,6 W. ESP32-S3 z punktem dostępowym, kartą SD i przekaźnikami pobiera więcej, więc skutkiem jest restart CORE i przerwany zapis na SD. SAFE_N i zatrzask ARM działają przy tym poprawnie — nie ma zagrożenia ze strony silnika.

To nieodłączny koszt kompromisu R2. Odporność na podłączenie wymaga C6/C5 ≥ ~60, a łagodny start wymaga R21·C5 rzędu 1 ms. Opóźnienie ponownego załączenia, proporcjonalne do R21·C6, musi więc wynosić dziesiątki milisekund i samą zmianą wartości elementów się go nie usunie.

**Decyzja właściciela:**
- **(a) — rekomendowane.** Przyjąć i opisać: każde zadziałanie P01 dłuższe niż kilkadziesiąt µs oznacza pełny restart systemu, więc LOGGER musi to znosić (częsty sync pliku, zdarzenie „reset z braku zasilania” po starcie). PCB bez zmian. Do ODBIOR 7.5 dopisać pomiar czasu braku VPROT po impulsie 50 µs. Ten wariant jest spójny z już przyjętym brakiem podtrzymania przy rozruchu.
- **(b)** Wymagać przetrwania krótkich zadziałań. To wymaga zmiany topologii: osobnej, szybkiej ścieżki ponownego załączenia, aktywnej tylko gdy VPROT ≈ VS, albo podtrzymania szyn logiki na P02. Zmienia PCB, więc trzeba to rozstrzygnąć przed layoutem.

---

## R2-02 — mierzalność kryteriów ODBIOR 7 posiadanym sprzętem

**Co wymaga ODBIOR:** sekcje 7.1 i 7.4 wymagają VGS z rozdzielczością ≤ 0,1 V (kryteria VSG ≤ 0,8 V oraz |VGS| < 0,5 V) i ładunku gałęzi Q1 ≤ 10 µC. Bez tych pomiarów wynik brzmi NIE ROZSTRZYGNIĘTO.

**Dlaczego się nie da:** w wyposażeniu z `docs/02-learnings-and-tools.md` nie ma sondy różnicowej ani prądowej. Cęgowy MS2115A nie mierzy zdarzeń trwających mikrosekundy. Na PCB nie ma miejsca na bocznik w gałęzi Q1. Różnica dwóch kanałów mierzonych względem GND przy 24–48 V obarczona jest błędem niedopasowania wzmocnień kanałów, który w skopach tej klasy wynosi kilka procent (sprawdź kartę DHO800). Już 1% daje 0,24 V przy 24 V i 0,48 V przy 48 V, czyli błąd rzędu samego kryterium. W obecnej formie próby przy 24 V i 48 V nie mogą więc zakończyć się wynikiem PASS.

**Propozycja bez zmiany PCB:**
- **Przewodzenie Q1 przy podłączeniu i w stanie OVP-OFF:** warunkiem PASS niech będzie ΔVPROT mierzone jednym kanałem względem GND. Kryterium jest już w 7.1: ≤ 0,1 V w ciągu 200 µs przy 220 µF, co odpowiada 22 µC. Przy 20 mV/dz rozdzielczość wynosi ~1 µC, lepiej niż dałby jakikolwiek pomiar prądu po stronie wysokiej. Ładunek gałęzi Q1 zostaje pomiarem informacyjnym.
- **VGS:** DHO804 zasilany wyłącznie z power banku, bez USB ani LAN do sprzętu sieciowego, jest pływający. Masę sondy podłączamy do TP1 (źródło Q1), końcówkę do TP2 i mierzymy VGS jednym kanałem z pełną rozdzielczością.
  - Wszystkie kanały mają wtedy odniesienie VS, więc to osobna seria pomiarów.
  - Obudowa skopu jest na potencjale VS (≤ 48 V DC). Skop i power bank muszą stać na podłożu izolującym.
  - Zakaz „masy nie podłączać do SOURCE” w ODBIOR dotyczy skopu uziemionego przez sieć. Trzeba dopisać wyjątek dla pracy z power banku.
- **ID przy starcie (do oceny SOA):** wyliczyć z przebiegu VPROT jako ID = C·dVPROT/dt + VPROT/R_obc, przy znanym C i rezystancyjnym obciążeniu.

**Alternatywa ze zmianą PCB** — tylko jeśli chcesz mierzyć ID bezpośrednio: mostek albo bocznik w szeregu między drenem Q1 a węzłem VPROT (C3/C4/D3/J2/J6). Decyzja przed layoutem.

---

## R2-03 — płeć styków złącza BAT po stronie pod napięciem

Według WIAZKI.md po stronie akumulatora, za bezpiecznikiem, siedzi EXT/J_BATA = Phoenix 1786174 (IC 2,5/2-ST, styki męskie), a H_BAT ma żeński 1757019. Po rozłączeniu strona akumulatora zostaje pod napięciem z odsłoniętymi stykami męskimi w rastrze 5,08 mm. Zwarcie o karoserię albo narzędzie przerwie bezpiecznik 5 A, ale z iskrą tuż przy akumulatorze.

**Propozycja:** zamienić strony — żeński 1757019 przy akumulatorze, męski 1786174 na H_BAT. Bez wpływu na PCB.

## R2-04 — C6: dostępność

B32529D1105J000 istnieje i pasuje (TME: 1 µF, 100 V DC, raster 5 mm, ±5%). TME oferuje go jednak tylko hurtowo: wielokrotność 1000 szt., pierwszy próg cenowy 4000 szt., brak na stanie (stan z 23.09.2026). Do zamknięcia w B-01: inny dystrybutor albo zamiennik foliowy z rastrem 5 mm, mieszczący się w obrysie 7,8 × 7,8 mm. Tolerancja ±10% nadal spełnia kryterium: 48 V × (11 + 2)/(11 + 2 + 900) nF ≈ 0,68 V < 0,8 V.

## R2-05 — uwagi do layoutu (L-01)

- **J7:** pady 6,0 mm z otworem 3,2 mm na miedzi 70 µm, podłączone do pola pełnym połączeniem, nie zwilżą się zwykłą lutownicą. Rozwiązanie: szerokie szprychy z przekrojem dobranym do 5 A albo zaplanowane podgrzewanie płytki.
- **TP1 (VS) i TP2 (GATE):** umieścić tuż przy nóżkach S i G tranzystora Q1. Od tego zależy pomiar VGS opisany w R2-02.

---

## Odpowiedzi na pytania z PRZEGLAD.md

### Budżet detektor → ENABLE i granica modelu (ENABLE jako idealne źródło)

Zbudowałem rzeczywisty tor (`tor_enable.py`): OK (R13) → R14 → D7/D8 → Q6 → ENABLE, z R16 = 10 kΩ oraz bazami Q3, Q5 i Q8 zawieszonymi na ENABLE.

Wyniki:
- ENABLE spada poniżej 1 V w 0,3–0,4 µs.
- Potem przez kilka µs utrzymuje się na ~0,45–0,52 V: ładunek baz wraca przez R17/R19/R32, a odprowadza go tylko R16.
- Całe wyłączenie wydłuża się jedynie o 1,5–2,3 µs (44,4 zamiast 42,9 µs; 66,6 zamiast 64,3 µs).
- Przy 18,5 V przesterowanie komparatora wynosi 75 mV, więc LM2903 odpowiada w czasie rzędu 1–2 µs.
- SAFE_N opada 2,7–6,1 µs po OK.

Podbudżet 20 µs ma zatem duży zapas, a idealne ENABLE w modelu jest dopuszczalnym uproszczeniem.

### Wyłączanie Q2 przez Q4

Q4 (2N5401) nasycony przy IC ≈ VS/2,2 kΩ i IB ≈ 1–1,7 mA ma VCE(sat) ~0,1–0,2 V. To mniej niż minimalny próg Q2 (1 V), więc Q2 jest wyłączony z zapasem, także na ciepło. D9 ogranicza VGS(Q2) do −15 V.

Najwolniejszy element łańcucha to rozładowanie bazy Q4 przez R25 = 47 kΩ. Model autora z TR = 1–3 µs daje 64 µs w wolnym narożniku, zgodnie z moim powtórzeniem. Rzeczywista stała magazynowania τs tych tranzystorów nie jest znana — rozstrzygnie ją pomiar w H-01.

### Granice modelu

Powtórzyłem cztery talie (`powtorzenie_talii.py`). Wyniki są identyczne z `dynamics.json`:
- hot_48_1e-06_1: 0,595 V / 0,001 A;
- off_1: 64,23 µs;
- start_slow_corner: 74,3 ms;
- ovp_17_24: 96,7 A / 77,97 µs.

Ręcznie sprawdziłem też wzór z `bounds.json` (0,623 V przy 48 V) i punkt ON 6,29 V.

Impedancja węzła bramki wzrosła 20 razy względem R1 (R21∥R22 = 82,5 kΩ). Daje to zapas ~20 µA łącznego upływu (IDSS Q2, D4, IGSS Q1), zanim VSG spadnie poniżej 4,5 V przy 8,9 V. W zakresie 0–50 °C to wystarcza, a ODBIOR 6 mierzy VGS na gorąco.

`bounds.py` i `check_release.py` wymagają numpy, którego nie instalowałem. Ich rachunki sprawdziłem ręcznie.

### Duży prąd przy OVP z Q1 już otwartym (96,7 A)

To nie jest wada P01, tylko skutek przyjętego bodźca: sztywne źródło 50 mΩ ze skokiem 7 V w 1 µs ładuje 220 µF przez w pełni otwarty Q1.

- **Brak D3 w talii:** w talii nie ma D3 (5KP18A), dlatego VPROT rośnie w niej do 22,3 V. W rzeczywistym układzie D3 ograniczy VPROT i przejmie prąd do chwili odcięcia.
- **Q1 i SOA:** Q1 jest wtedy w pełni otwarty, więc napięcie na nim jest małe (model: 1,4 mJ w całym zdarzeniu). SOA nie jest tu problemem.
- **Co wyznacza prąd:** impedancja źródła. Przy impulsach samochodowych (0,5–2 Ω) będą to dziesiątki amperów, przy zasilaczu z ograniczeniem prądu — pojedyncze ampery.
- **Energia w D3:** przez ≤ 100 µs przy ~40 A i ~21 V to ~0,1 J, wobec zdolności rzędu kilku dżuli dla impulsu 10/1000 µs.

**Wniosek dla ODBIOR 7.4:** próbę 14 → 24 V wykonać ze źródła z ograniczeniem prądu, a nie przekaźnikiem z akumulatora.

---

## Sprawdzone bez uwag

| Zakres | Wynik |
|---|---|
| Kontrole pakietu | Świeży eksport KiCad 10 jest identyczny z XML w paczce (88 elementów, 34 sieci). ERC ze wszystkimi poziomami: 0 naruszeń. `verify.py` i `check_package.py` (203 kontrole, 9 wykrytych mutacji) przechodzą. |
| Delta R1 → R2 | Zmieniono wyłącznie C5, C6, R21, R22, R27 i Q2 (PNP → P-MOS, nowe przypisanie G/D/S), dodano D9. Pozostałe połączenia są identyczne z R1. |
| Q2 P-MOS | S = VS, G = OFF_BASE, D → R27 → GATE. Dioda strukturalna D→S przewodzi tylko przy GATE > VS, tak jak D4. D9: K = VS, A = OFF_BASE. Bez AUX5 R23 otwiera Q2, więc Q1 jest OFF; przy aktywnym ENABLE Q4 zamyka Q2. |
| Odporność na podłączenie | 0,595 V przy 48 V / 1 µs w narożniku (powtórzone). Przy ±10% C5/C6: 0,68 V. |
| Start | Wolny narożnik osiąga 95% w 74,3 ms (< 300 ms). Prąd szczytowy ≤ 3,7 A (< 5 A). VSG w stanie ON ≥ 6,29 V przy 8,9 V. |
| Wyłączenie OVP | 43–67 µs od ENABLE z rzeczywistym torem ENABLE, plus ~2 µs komparatora. W modelu mieści się w 100 µs z zapasem ~30 µs. |
| Moce | R27: 1,5 A szczytowo, ~0,17 mJ na zdarzenie. R23: 0,495 W i D9: 0,223 W przy 48 V (chwilowo). Q2 nie przewodzi prądu stałego, więc nie potrzebuje radiatora. |
| „SAFE_N ≠ gotowe VPROT” (integracja) | Według v6.1 P02 ma w PSU_OK układ MCP120-450 na 5V_SYS. ARM jest więc możliwy dopiero ≥ ~150 ms po starcie przetwornic, a Q1 osiąga VSG = 4,5 V w ~100 ms po ENABLE nawet przy 8,9 V. Sprzętowa kolejność jest poprawna, pod warunkiem że USB z CORE nie zasila 5V_SYS — tylko to trzeba sprawdzić przy integracji. |
| Dokumenty | ODBIOR, README, ZMIANY i ANALIZA są spójne z BOM R2. Poza katalogami historycznymi nie ma nieaktualnych wartości z R1. |
