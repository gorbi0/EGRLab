# Recenzja P01-R1-review (bramka E-01)

23.09.2026 · recenzent: Claude (Opus 5.5) · przedmiot: `../P01-R1-review/` w stanie otrzymanym, bez zmian w paczce.

**Wynik: pakiet NIE przechodzi do layoutu.** Jeden błąd projektowy (R1-01) wymaga zmiany czterech wartości i footprintu C6, więc trzeba go poprawić przed PCB. Poza nim zakres E-01 sprawdzony bez uwag. Po wprowadzeniu R1-01 i R1-02 nie widzę przeszkód dla layoutu; otwarte zostają tylko pozycje, które pakiet sam wskazuje: M-01 (radiatory) i B-01 (MPN).

Dowód liczbowy do R1-01: `model/model_bramki_Q1.py` (biblioteka standardowa Pythona, kilka minut), wynik w `model/wynik.txt`.

## Rejestr uwag

| ID | Waga | Krótko |
|---|---|---|
| R1-01 | **BLOKUJE layout** | Q1 załącza się sam przy szybkim narastaniu VS, mimo stanu „domyślnie OFF” |
| R1-02 | WAŻNE | ODBIOR sekcje 3 i 7: próba „szybkiego podłączenia” może przejść fałszywie |
| R1-03 | drobne | Otwór 2,4 mm H_BAT a rzeczywisty przewód 2,5 mm² |
| R1-04 | drobne | Gniazdo EXT/J_BATA dla wtyku 1757019 bez MPN |

---

## R1-01 — Q1 przewodzi przy szybkim zboczu VS

**Sieć / elementy:** `/P01_GATE` — C5 (220 nF, GATE–VPROT), C6 (47 nF, GATE–VS), Q2+R27 (47 Ω), R21 (4,7 kΩ), D4.

**Warunek:** Q1 ma być wyłączony (brak AUX5, POR MCP120, INHIBIT, OVP albo UVLO), a VS narasta szybciej niż ~100 µs. Przypadki praktyczne:
- podłączenie klem lub wtyku H_BAT do źródła pod napięciem — normalny sposób wpięcia w aucie;
- podłączenie boostera 24 V;
- szybki dalszy wzrost VS, gdy Q1 jest już odcięty przez OVP.

**Mechanizm:** VPROT trzymają kondensatory (C3 100 µF i dalsze, do 220 µF). W chwili skoku bramka jest w dzielniku pojemnościowym C6 do VS i C5 do VPROT, więc VSG ≈ ΔVS × C5/(C5+C6) = **0,82 × ΔVS**. Q2 ma przytrzymać bramkę przy VS, ale dysponuje około 250 mA (ograniczenie β przy IB z R23). Przy zboczu 1 µs utrzymanie bramki wymaga C5 × dV/dt ≈ 3 A. D4 nie pomaga, bo ogranicza dopiero przy 15 V. „Domyślny OFF” opisany w PROJEKT.md i PRZEGLAD.md jest prawdziwy tylko dla zboczy wolniejszych niż ~100 µs.

**Dowód (model, `model/wynik.txt`):**

| Sytuacja | R1 (obecnie) | Po poprawce |
|---|---|---|
| Wpięcie 14 V, zbocze 1–10 µs, 50 mΩ wiązki + C1 | Q1 przewodzi: 46–80 A, 4–5 mJ w Q1 w zakresie liniowym, VPROT do ~2,4 V | VSG ≤ 0,42 V, 0 A |
| Wpięcie 24 V, zbocze 1–10 µs | 120–190 A, 18–21 mJ w Q1, VPROT do ~6,7 V | VSG ≤ 0,71 V, 0 A |
| To samo, najgorszy Vt = 1,0 V | 210 A | VSG 0,71 V, 0 A |
| Stan OVP-OFF: VS 18 V, VPROT 17 V, skok do 30 V w 1–10 µs (źródło idealne) | 56–164 A przez Q1 | 0 A |
| Normalny start przy 14 V do 220 µF | 2,6 A | 1,8 A |
| Wyłączenie OVP przy 18,5 V do \|VGS\| < 2 V / < 0,5 V | 27 / 47 µs | 44 / 80 µs |
| Szczytowy prąd Q2 przy wyłączeniu (limit 2N5401: 600 mA) | ~376 mA | ~381 mA |

Model jest uproszczony: Q1 kwadratowy, β Q2 = 60, bez czasów magazynowania Q4/Q5/Q6/Q8 i komparatora (dodają się jednakowo w obu wariantach). Liczby służą do porównania wariantów, nie jako gwarancja.

**Skutek i waga:** SAFE_N pozostaje we wszystkich tych przypadkach aktywny (ENABLE = 0), a zatrzask ARM wyłączony, więc nie jest to zagrożenie ze strony zaworu. Problem jest inny. Q1 i D2 przy każdym wpięciu dostają impuls prądu, którego dokumentacja nie analizuje w SOA; przekracza on ~10–16 razy własne kryterium pakietu (5 A przy starcie). Do tego stan OVP-OFF nie jest odporny na szybkie zbocza i Q1 przenosi je na VPROT, gdzie ogranicza je dopiero D3.

**Dlaczego kontrole pakietu tego nie wykryły:** ERC, porównanie netlisty z bazą i testy mutacyjne badają połączenia. To jest własność dynamiczna przy poprawnych połączeniach.

**Proponowana decyzja:**

| Element | R1 | R2 |
|---|---|---|
| C5 (GATE–VPROT) | 220 nF / 100 V | **22 nF** / 100 V |
| C6 (GATE–VS) | 47 nF / 100 V | **680 nF**, folia ≥ 63 V (widzi najwyżej 15 V dzięki D4) |
| R21 | 4,7 kΩ | **47 kΩ** |
| R27 | 47 Ω / 2 W | **33 Ω** / 2 W |

Topologia bez zmian. Nadal jest to kształtowanie Millera, z tym samym narastaniem ~10 V/ms, ale teraz C_GS ≫ C_GD. Konsekwencje do przeniesienia:
- **Footprint C6:** 680 nF w tej samej serii ma większy korpus niż 47 nF. Dobrać MPN i obrys w ramach B-01.
- **VGS w stanie ON:** −0,68 × VS zamiast −0,95 × VS. Przy UVLO 9,37 V to −6,4 V, nadal powyżej −4,5 V, przy którym katalog podaje RDS(on).
- **D4:** przestaje przewodzić w normalnej pracy. Poprzednio przy VS ≈ 16 V już się zbliżał do progu.
- **Start:** VPROT osiąga pełne napięcie ~9–10 ms po ENABLE zamiast ~2 ms. Bez znaczenia funkcjonalnego.
- **PROJEKT.md, sekcja „Start, szybkie odcięcie i przepięcia”:** przeliczyć ładunek wyłączenia (dominuje C6 × VSG; przy 18,5 V ≈ 8,6 µC), czasy i opis „domyślnego OFF”, z warunkiem dotyczącym szybkich zboczy.

**Wariant odrzucony — nie stosować:** rezystor szeregowo z C5 (1–4,7 kΩ). Blokuje sprzężenie, ale psuje kształtowanie startu: w modelu 63–80 A zamiast 2,6 A, bo opóźnia pętlę Millera przez R × C_GS.

**Kontrola, która wykryje powtórzenie:**
1. Reguła statyczna w `check_package.py`, z wartości w BOM: `24 V × C5 / (C5 + C6 + Ciss) ≤ 0,8 V`. R1 daje 19,6 V, poprawka 0,75 V.
2. `model/model_bramki_Q1.py` jako test regresji: dla R2 przypadki A i B muszą dawać Id szczyt = 0, a przypadek D |VGS| < 0,5 V w czasie ≤ 100 µs.
3. Próba sprzętowa według R1-02.

---

## R1-02 — metoda próby „szybkiego podłączenia” w ODBIOR

**Miejsce:** `docs/ODBIOR.md`, sekcja 3 („szybkie podłączenie 13,8 V … start od razu z 24 V”) i sekcja 7.

**Problem:** wynik zależy od szybkości zbocza. Włączenie wyjścia zasilacza laboratoryjnego zwykle narasta w milisekundach. Obecny projekt przeszedłby wtedy próbę, a R1-01 zostałby ukryty.

**Proponowana decyzja:** robić te próby **stykiem mechanicznym** (wtyk H_BAT, przekaźnik, wyłącznik) przy już ustalonym napięciu źródła i mierzyć jednocześnie VGS (różnicowo) oraz prąd wejściowy. Dopisać próbę szybkiego skoku VS w stanie OVP-OFF (np. 18 → 24 V przez styk). Kryterium: brak prądu przez Q1 i |VGS| poniżej progu Q1 przez cały czas zbocza.

**Kontrola:** rubryka protokołu „Start 0 → 13,8 V i 0 → 24 V” ma zawierać sposób wykonania zbocza i zmierzony czas narastania.

---

## R1-03 — otwór 2,4 mm na przewód 2,5 mm² (H_BAT, J7)

Pasuje dla zwykłej linki H07V-K. Dla bardzo giętkiej linki silikonowej 2,5 mm² może być ciasno. **Decyzja:** zmierzyć średnicę żyły przewodu, który faktycznie będzie użyty, zanim powstaną Gerbery. **Kontrola:** średnica żyły wpisana do WIAZKI.md obok średnicy otworu.

## R1-04 — gniazdo po stronie źródła dla wtyku H_BAT

H_BAT kończy się wtykiem Phoenix 1757019 (MSTB 2,5/2-ST-5,08). W `EGRLab-v6.1-rc1/hardware/EXT-BOM.csv` pozycja EXT/J_BATA to tylko „MSTB 5.08 gniazdo 2p”, bez MPN. **Decyzja:** dobrać konkretną część współpracującą (panelową lub przewodową) przed zaciśnięciem tulejek. Nie blokuje PCB P01.

---

## Sprawdzone bez uwag (zakres E-01)

| Zakres | Wynik |
|---|---|
| Kontrole pakietu | Sam wyeksportowałem netlistę KiCad 10 CLI z `eda/P01.kicad_sch`: identyczna z `verification/P01.xml` (34 sieci). ERC ze wszystkimi poziomami: 0 naruszeń. `src/verify.py` i `src/check_package.py` przechodzą. |
| Orientacja Q1/D2 | Q1: S = VS, D = VPROT; dioda strukturalna VPROT → VS, więc OVP nie jest omijane. D2: obie anody BAT_FUSED, katoda (tab) VS, blokuje zwrot do akumulatora. Taby na różnych potencjałach — izolacja wymagana, jak w MECHANIKA.md. |
| Domyślny OFF bez AUX5 | Statycznie poprawny: Q2 polaryzowany z VS przez R23. **Dynamicznie — patrz R1-01.** |
| MCP120, wspólna sieć OK, INHIBIT | U2.1/U2.7/U4.1 otwarte, R13 jedynym pull-upem. D7/D8 dają ~2,4 V zapasu nad słabym stanem niskim, więc ENABLE nie ruszy nawet przy VOL rzędu 1 V. J3 zwiera OK do GND. |
| Progi | Przeliczone z wartości w netliście: OVP 18,0/16,66 V przy RV1 ≈ 2,14 kΩ, zakres RV1 17,4–18,7 V; UVLO 9,85/9,37 V. Histereza ma poprawny kierunek w obu komparatorach, okna rozłączne, start możliwy tylko przy 9,85–16,66 V. |
| TL431 | ~3 mA katody przy AUX5 = 5 V, brak kondensatora na REF. Piny 1 i 3 zwarte, więc spór o numerację K/REF nie ma skutku elektrycznego. |
| LM2936, C9 + R2 | Wejście za R1/D5; R2 = 1 Ω + ESR C9 mieści się w oknie stabilności; dwa 100 nF równolegle to pomijalny udział. |
| Łańcuch ENABLE | ENABLE ≈ 2,7–2,9 V, prądy baz Q3/Q5/Q8 0,2–0,45 mA — nasycenie z zapasem, także przy AUX5 = 4,85 V i −10 °C. |
| SAFE_N | Q7 polaryzowany z 3V3_IO przez R30, zwalniany przez Q8 z ENABLE. Przy zaniku P01 i obecnym 3V3_IO SAFE_N aktywny. Brak ścieżki zasilania zwrotnego do 3V3_IO. |
| Moce i napięcia | R1 ≤ 1,1 W przy 32 V (PR02 2 W); R23 ≤ 0,5 W przy 32 V; D5 ≤ 1,5 W przy 32 V (1.5KE: 5 W); napięcia znamionowe C1/C3/C7/C9 z zapasem wobec napięć ograniczania D1/D3/D5. |
| Pinouty | Q1 G-D-S, D2 A-K-A, 2N5401/2N5551 E-B-C, LM2936 OUT/GND/IN, MCP120 RST/VDD/VSS, LM2903P zgodny z DIP-8, 3296W: suwak (2) zwarty z końcem 1. |
| Footprinty | Katody D3/D4/D5/D6–D8 na padzie 1, LED K na padzie 1. Otwory: TO-220 1,4 mm (przekątna nóżki ~1,18 mm), P600 1,6 mm, DO-201 1,3 mm, TO-92 0,8 mm, AWG22 1,1 mm. Odstęp miedzi między padami TO-220 0,44 mm — wykonalny. |
| Złącza do systemu | J5 = P04/J_PGA pin w pin (3V3_IO, SAFE_N, GND, PG_SEND, PG_LINK, GND); J6 = SUPPLY do P02 (VPROT, GND, NC); J7 = BAT (BAT_FUSED, GND). Zgodne z `baseline/wiring.csv`. |

Nie oceniano: layoutu (nie istnieje), mocowania radiatorów (M-01) ani dostępności MPN (B-01). Energia TVS i SOA Q1 przy impulsach pozostają, zgodnie z pakietem, do pomiaru w ODBIOR sekcja 9.
