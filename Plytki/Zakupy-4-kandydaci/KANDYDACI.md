# Lista zakupowa 4 — kandydaci MPN (4.10.2026, sesja w chmurze)

Zadanie: `Plytki/Format-S1/zadania/ZADANIE-ZAKUPY-4-KANDYDACI.md`. Stany, ceny i terminy sprawdzi sesja lokalna (TME, Mouser, Farnell — Cloudflare, nie obchodzono).

## Ważne: czego ta sesja NIE mogła zrobić

Sieć środowiska odrzuca wszystkie strony producentów i sklepów, które próbowałem otworzyć (Mouser, TME, Samtec, Panasonic, Amphenol, Harwin, E-Switch: 403 albo brak połączenia). **Żadnego kodu nie sprawdziłem na karcie producenta online.** Oparłem się na kartach już leżących w repozytorium i na pamięci. Każdy kod ma więc znacznik pewności:

| Znacznik | Znaczenie |
|---|---|
| **[K]** | potwierdzone kartą w repozytorium (podany plik) |
| **[P]** | z pamięci — konwencja kodu i parametry prawdopodobne, ale **do sprawdzenia w karcie i w sklepie przed zamówieniem** |
| **[?]** | nie mam kodu, w który wierzę; podane kryteria wyboru |

Nie zmieniałem żadnego pakietu płytek. Pytania do użytkownika są na końcu (Q1–Q6).

## Podsumowanie

| # | Pozycja | Kandydat główny | Pewność | Główne ryzyko |
|---|---|---|---|---|
| 1 | SW1 P05 | E-Switch 100DP1T1B3M6REH | [K] struktura kodu i footprint | dostępność/termin B3 (sklep) |
| 2 | BYPASS P06 | brak kandydata poza S6A (patrz niżej) | [K] dla rodziny NKK S, [?] dla reszty | wykluczone S6A; trzeba znać powód |
| 3 | Porty L1/L2/TEST | Amphenol AT04-12PA/PB/PC + AT06-12SA/SB/SC | [P] | **styk rozmiaru 16 nie przyjmie 2,5 mm²**; wersja panelowa z kołnierzem |
| 4 | Przyciski panelu | kryteria + rodziny, bez MPN | [?] | minimalne obciążenie 27 µA / 3 V rzadko jest w karcie |
| 5 | IDC kątowe, goldpiny kątowe | Amphenol FCI T821…R; Samtec TSW-1xx-08-G-S-RA | [P] | orientacja klucza, głębokość korpusu |
| 6 | C1 P05 / C3 P06 | Panasonic EEUFR1C221 (bez zmiany) | [P] wymiary, [K] footprint | — |
| 7 | C35 P05, C17 P06 | C35 25 V: GRM31CR71E106KA12L; C17: bez zmiany | [P] | **lista 3 ma w C35 część 16 V, BOM wymaga 25 V** |

## 1. SW1 P05 — E-Switch 100DP1T1B3M6REH

Rozszyfrowanie kodu według konfiguratora w `Plytki/P05-R3-review/reference/E-Switch-100-series.pdf` **[K]**: 100 (seria) · DP1 (DPDT On–None–On) · T1 (dźwignia standard) · **B3 (THD‑STD, gwint 1/4‑40UNS)** · **M6 (poziomy kątowy, PCB)** · **R (styki złocone)** · E (uszczelnienie epoksydowe) · H (osprzęt: nakrętka i podkładka, tylko do tulei gwintowanych). Kod jest więc poprawnie zbudowany i zgodny z decyzją 4.10. Uwaga: „M6” w kodzie to **zakończenie PCB**, nie gwint metryczny; gwint B3 to 1/4‑40UNS (ok. 6,35 mm), więc otwór w panelu ok. Ø 6,5 mm (do potwierdzenia z rysunkiem tulei B3, str. 5 karty).

Zgodność z footprintem `ESW_100DP_M6` (P05 R3): rysunek „M6 – DP” z karty podaje 3,81 / 4,70 / 12,70 / 5,08 / 9,40 mm i otwory 1,85 mm; footprint ma dokładnie te wartości **[K]**. Piny są takie same dla wszystkich tulei i materiałów styków (B1…B4, Q/R), więc zamiana wariantu nie zmienia PCB. Wyjątek: M61 (z zaczepem) ma inny wykrój — nie kupować.

Parametry: styki złocone 0,4 VA max przy 20 V (karta, str. 1) — pasuje do obwodu µA–mA; 40 000 cykli; −40…85 °C. Tuleja B3/B4 wydłuża korpus o 1,78 mm (przypis 7 karty) — dotyczy głębokości panelu, nie PCB.

Zamienniki:
- **100DP1T1B3M6RE** (bez „H”, nakrętkę dokupić osobno) — ten sam układ pinów **[K]**; sensowny, jeśli „H” jest niedostępne.
- 100DP1T1B4M6REH nie ma sensu: B4 jest bez gwintu, a „H” działa tylko z gwintem **[K]**.
- Nie kupować wariantu Q (srebro) — wymaganie złoconych styków z decyzji 29.09.
- Przełącznika innego producenta o rastrze 3,81 / 4,70 mm nie znam; C&K JS202011AQN został odrzucony wcześniej.

Do sprawdzenia lokalnie: stan i termin w Mouser (seria 612‑100…).

## 2. BYPASS P06 — przełącznik panelowy DPDT ON‑ON ≥ 10 A DC

Wymagania z `P06-R2-review/docs/PROJEKT.md`: ≥ 10 A przy 12–30 V DC (silnik EGR do 6 A, w próbie biernej 10 A), oczka lutownicze, tuleja z nakrętką; biegun B niesie ok. 0,13 A.

Karta NKK serii S w repozytorium (`P06-R2-review/reference/datasheets/NKK-S.txt`) podaje dla rodziny DPDT: S6A **20 A / 125 V AC, 20 A / 30 V DC** **[K]** (S6AW — ta sama obciążalność, wersja z uszczelnieniem panelu; S6F — z końcówkami konektorowymi 6,3 mm). Użytkownik zdecydował 29.09 „NKK S6A nie”, ale w repozytorium nie ma zapisu *dlaczego* (cena? wymiary 40 × 35 × 45 mm? dostępność?). Bez tej wiedzy nie umiem wskazać zamiennika, który spełni ten sam powód.

Kandydatów innych producentów znam tylko z pamięci i żadnego nie umiem podać z pewnością co do **prądu stałego** (karty dla przełączników przemysłowych często podają tylko AC):
- Honeywell (Microswitch) serii 2NT1 (DPDT ON‑ON, oczka lutownicze) **[?]** — AC do 15 A znane, DC do sprawdzenia;
- Carling (seria 2FA/2GK) **[?]**;
- serie „marine/automotive” DPDT 15–20 A / 12–28 V DC **[?]**.

Kryteria selekcji, którymi sesja lokalna może odsiać wyniki w TME/Mouser: (1) w karcie jest **jawna** obciążalność DC przy ≥ 28 V, nie sam prąd AC; (2) obciążenie indukcyjne ≥ 6 A; (3) oczka lutownicze 2,5 mm²; (4) tuleja z nakrętką, grubość panelu ≥ 3 mm; (5) styki w środku (2 i 5) — numeracja zostanie i tak ustalona omomierzem (ODBIÓR E03).

**Rekomendacja:** jeśli S6A odpadł z powodu ceny, a nie parametrów, S6A pozostaje jedynym przełącznikiem w tym zestawie danych potwierdzonym kartą na wymaganą obciążalność DC. Patrz Q1.

## 3. Porty L1 / L2 / TEST — Amphenol AT04‑12 / AT06‑12

Konwencja kodów (odpowiednik DEUTSCH DT) **[P]**:

| Rola | Strona panelu (gniazdo obudowy, AT04) | Strona adaptera (wtyk, AT06) | Klin |
|---|---|---|---|
| TEST (klucz A) | AT04‑12PA | AT06‑12SA | W12P / W12S |
| L1 (klucz B) | AT04‑12PB | AT06‑12SB | W12P / W12S |
| L2 (klucz C) | AT04‑12PC | AT06‑12SC | W12P / W12S |

Zgodność z pierwotnym planem P11 R1: tam było DT04‑12PA = TEST, PB = L1, PC = L2 **[K]** (`P11-R1-review/docs/ZAKUPY.md`). Zachowuję to przypisanie.

**Dwa problemy do rozstrzygnięcia:**

1. **Wersja panelowa.** AT04‑12P to gniazdo „kablowe” (przelotowe, na przewody). Wersja z kołnierzem do przykręcenia w panelu ma w rodzinie DT/AT osobne sufiksy (u DEUTSCH np. „‑C0xx”/kołnierz) — nie pamiętam ich pewnie dla Amphenola. Alternatywa: zwykłe AT04‑12P w wycięciu panelu z opaską/klipsem. **Do sprawdzenia w karcie Amphenol AT04 i w ofercie** (Mouser, TME nie ma Amphenol Sine). **[?]**
2. **Przekrój styków.** Standardowe styki rozmiaru 16 (DT04‑12) przyjmują ok. 0,5–2,0 mm² (AWG 20–14 zależnie od wariantu zaciskania); P11 R1 przewidywał 16–20 AWG **[K]**. W specyfikacji zadania jest „styki do 2,5 mm² dla prądu silnika” — **2,5 mm² (AWG 14) nie zmieści się w standardowym styku rozmiaru 16**. Prąd 6–10 A płynie przez AWG 16 (1,5 mm²) bez problemu przy 13 A znamionowych styku, więc proponuję 2 piny silnika (ECU_P1, EGR_P1) w AWG 16 / 1,5 mm², zamiast szukać styku na 2,5 mm². Q2.

Styki **[P]** (nie TE 0460‑…, jeśli złącza są Amphenol — mieszanie jest możliwe, ale Amphenol ma własne): AT60‑201‑1631 (pin, złocony, rozmiar 16) / AT62‑201‑1631 (gniazdo); sygnały 0,5–1 mm² — ten sam styk rozmiaru 16 (zaciskanie 20 AWG) **albo** rozmiar 20 w obudowach AT‑12 nie występuje (12 komór = wszystkie rozmiaru 16). Zaślepki komór: DEUTSCH 114017 jak w P11 R1 **[K]**, u Amphenola odpowiednik „AT114017” **[P]**.

Ilości (jak w P11 R1 **[K]**, podwojone dla strony adaptera): obudowy 3 + 3, klinów 3 + 3, styków ok. 25 + 25 (pin + gniazdo), zaślepek 11 + 11 — do przeliczenia po decyzji, ile adapterów powstaje.

## 4. Przyciski panelu ze stykami złoconymi (P11‑7)

Zakres według P11‑1/P11‑7 (`P11-S1-przygotowanie/README.md`): w odchudzonej P11 są **4 elementy**: kluczyk 2‑pozycyjny (TEST_KEY), STOP zatrzaskowy NC, ARM chwilowy, MARK chwilowy. Detektory portów (pętle NC L1/L2, TEST_PRESENT) są realizowane w adapterach, nie przyciskami, więc nie wchodzą na listę.

**Nie mam MPN, w który bym wierzył.** Wątpliwość nie jest techniczna, tylko informacyjna: wymaganie „działa przy 27 µA / 3 V” prawie nigdy nie występuje w karcie przycisku panelowego. Karty podają prąd minimalny tylko dla elementów oznaczonych jako „low‑level / gold” (EAO 14‑xxx, które odrzucono). Wskazuję rodziny do przejrzenia, bez kodu:

| Średnica otworu | Rodzina do przejrzenia | Co sprawdzić w karcie |
|---|---|---|
| 16 mm | miniaturowe przyciski panelowe złocone (Schurter, C&K, APEM, Multicomp) | jawny „min. load” ≤ 1 mA / ≤ 5 V albo styk „Au” |
| 19 mm | przyciski antywandalowe 19 mm (APEM, Bulgin) | jak wyżej |
| 22 mm | rodziny przemysłowe 22 mm z blokami styków „low‑level/electronics” (Eaton M22, Schneider XB5/ZB5) | blok styków **osobny** od nasadki; jawnie „5 V / 1 mA” |

Zalecenie: skoro prąd styku to 27 µA, a tylko STOP jest istotny bezpieczeństwa, **wybierz jeden rozmiar otworu dla wszystkich czterech** (upraszcza panel i makietę), a złocenie zweryfikuj zapytaniem do producenta, jeśli karta milczy. STOP ma być zatrzaskowy NC, kluczyk z dwiema pozycjami; nie deklarujemy certyfikowanego E‑stopu (jak w R1). Q3.

## 5. Złącza IDC kątowe obudowane i goldpiny kątowe

Footprinty w pakietach (`IDC-Header_2x05/2x08/2x10_P2.54mm_Horizontal`, `PinHeader_1x13_P2.54mm_Horizontal`) **[K]** — sprawdzone: raster 2,54 mm, dystans rzędów 2,54 mm, pin 1 w (0, 0), otwór 1,0 mm / pad 1,7 mm; obrys (courtyard) IDC zajmuje x −1,35…13,78 mm, a y 0…22,86 mm dla 2×10 (28,46 mm z obrysem); goldpin 1×13 — długość 30,48 mm, obrys do x = 10,54 mm (pin 6 mm).

**IDC kątowe obudowane, złocone (2×10 ×5, 2×8 ×2, 2×5 ×2):**
- Główny **[P]**: Amphenol FCI **T821** (kątowe, złocone). Schemat kodu, jak w liście 2 (proste): T821 1xx A1 **R** 100 CEU, gdzie xx = liczba styków (10 / 16 / 20), „R” = kątowe, „S” = proste. **Kody kątowe nie są potwierdzone** — wystarczy podmienić S→R w znanych kodach prostych z listy 2 i sprawdzić w TME.
- Zamiennik 1 **[P]**: Würth WR‑BHD, kątowe 2×5/2×8/2×10 (Mouser/Farnell; TME nie ma Würtha); kody 61200xx21821‑podobne — **do sprawdzenia**.
- Zamiennik 2 **[P]**: Harting/Ninigi/Connfly (tańsze, często tylko flash gold) — dla styków sygnałowych ok., ale nie dla złoconych wymagań µA.

Do potwierdzenia przed zamówieniem (żaden z kodów nie ma tego w repozytorium): głębokość korpusu 13,78 mm wobec footprintu, **kierunek klucza (wcięcie) obudowy kątowej wobec pinu 1**, wysokość nad płytką wobec limitu poziomu (≤ 16,5 mm).

**Goldpiny kątowe 1×13 (×9), 1×9 (×1), 1×7 (×1):**
- Główny **[P]**: Samtec **TSW‑1xx‑08‑G‑S‑RA** (xx = 13 / 09 / 07). Karta TSW w `P05-R3-review/reference/datasheets/TSW.txt` potwierdza opcję **‑RA** (kątowa) i złocenie **‑G** (10 µin styk, 3 µin ogon) **[K]**; styl wyprowadzenia „‑08” wcześniej użyty w P05 (TSW‑108‑08‑G‑D‑NA) — długość „6 mm” z footprintu odpowiada typowi ‑08, ale wymiar E/C trzeba potwierdzić w tabeli 3/5 karty.
- **Oszczędność:** 133 piny razem (9×13 + 9 + 7). Jedna taśma 1×40 kątowa daje 40 pinów, czyli 4 sztuki wystarczą z zapasem, ciąć nożem/szczypcami po długości. Zamiennik tani: standardowe listwy kątowe 1×40 (Amphenol FCI 68016/Harwin M20) **[P]**. Q4.

## 6. C1 P05 / C3 P06 — EEUFR1C221

Footprint `CP_Radial_D6.3mm_P2.50mm` **[K]**: raster 2,5 mm, otwór 0,8 mm, pad 1,6 mm. Panasonic **EEUFR1C221** (seria FR, 220 µF / 16 V, 105 °C, niska impedancja) **[P]**: obudowa 6,3 × 11,2 mm, raster 2,5 mm, drut Ø 0,5 mm — zgodna z footprintem; wysokość 11,2 mm mieści się w limicie 16,5 mm (poziom 4) z zapasem ok. 4 mm.

Zamienniki low‑ESR **[P]** (te same 6,3 × 11 / 2,5 mm): Rubycon **16ZLH220MEFC6.3X11** (seria ZLH), Nichicon **UHE1C221MPD** (seria UHE), Panasonic EEU‑FM1C221 (seria FM, wyższa ESR niż FR). Zamiennik wybrać z karty wg ESR przy 100 kHz — wartość referencyjna dla FR ok. 0,3 Ω; **wymaganie ESR w BOM nie jest podane**, więc nie wiem, jakie jest dopuszczalne minimum. Q5.

## 7. C35 P05 i C17 P06

- **C17 P06 (100 nF, 50 V, X7R, 1206):** C1206C104K5RAC (KEMET) — taki sam kod jest już na liście 2 jako 100 nF 1206 **[K]** (`Zakupy-3-szkic`: 0,4073 zł, stan 146336). Bez zmian.
- **C35 P05 (10 µF, 25 V, X7R, 1206):** BOM P05 R3 podaje **25 V** (`P05-R3-review/docs/BOM.csv`), ale lista 3 przypisała część **GRM31CR71C106KA12L**, a to jest **16 V** (symbol „1C”; ta sama część jest w BOM P03 R6 jako C14 „10uF / 16V”). **To rozbieżność.** Kandydat główny dla 25 V **[P]**: Murata **GRM31CR71E106KA12L** („1E” = 25 V). Zamienniki 25 V X7R 1206 **[P]**: TDK C3216X7R1E106K160AC, Samsung CL31B106KAHNNNE. Węzeł C35 to 5VA_P05 (5 V), więc 16 V też by działało przy ok. 50 % spadku pojemności od polaryzacji, ale 25 V jest bezpieczniejsze i zgodne z BOM. Q6.

## Pytania do użytkownika

- **Q1.** Dlaczego odpadł NKK S6A (cena, wymiary 40 × 35 × 45 mm, dostępność)? Od tego zależy, czego szukać dla BYPASS.
- **Q2.** Czy zgadzasz się na AWG 16 / 1,5 mm² dla pinów silnika w portach AT04 (zamiast 2,5 mm²)? Styk rozmiaru 16 nie przyjmie 2,5 mm².
- **Q3.** Który rozmiar otworu (16 / 19 / 22 mm) dla czterech przycisków? Zawęża wybór rodzin w pozycji 4.
- **Q4.** Czy listwy kątowe 1×13/9/7 mają być cięte z 1×40 kątowych (4 szt.), czy kupować gotowe długości?
- **Q5.** Czy BOM ma graniczną ESR dla C1/C3? Bez niej nie rozstrzygnę FR vs ZLH vs UHE.
- **Q6.** C35: kupić 25 V zgodnie z BOM (GRM31CR71E106…), czy zostawić 16 V z listy 3 (jak C14 w P03)?

Plik `kandydaci.csv` zawiera te same pozycje w formie tabeli do wklejenia do zakupów.
