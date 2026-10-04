# Lista zakupowa 4 — kandydaci MPN (4.10.2026, sesja w chmurze; poprawki po recenzji i decyzjach 4.10)

Zadanie: `Plytki/Format-S1/zadania/ZADANIE-ZAKUPY-4-KANDYDACI.md`. Stany, ceny i terminy sprawdzi sesja lokalna (TME, Mouser, Farnell — Cloudflare, nie obchodzono).

## Do sprawdzenia w sklepie przez sesję lokalną

| # | Co | Sprawdzić |
|---|---|---|
| 1 | E-Switch **100DP1T1B1M1REH** (SW1 P05, panel) | stan i termin (DigiKey 378868, Mouser, TME); jeśli brak — zgłosić użytkownikowi, **nie** zamieniać samodzielnie na wersję Q (srebro) |
| 2 | Amphenol **AT04-12PA-PM01 / AT04-12PB-PM01 / AT04-12PC-PM01** | czy TME ma PM01 (i PM05 — kołnierz z uszczelką) dla kluczy **B i C**, nie tylko A |
| 3 | Amphenol **AT06-12SA / SB / SC** | stan |
| 4 | Kliny **AW12P / AW12S** | stan (nie mylić z W12P/W12S — kody Deutsch) |
| 5 | Styki sygnałowe **AT60-202-1631** (pin) / **AT62-201-1631** (gniazdo), złocone, 16–20 AWG | stan, minimalna ilość w opakowaniu |
| 6 | Styki silnikowe **AT60-215-1631** (pin) / **AT62-209-1631** (gniazdo), złocone, AWG14 | stan, zakres przekroju w karcie (2,0 mm²) |
| 7 | Zaślepki komór **A114017** | stan |
| 8 | IDC **T821 1xx A1R100CEU** (2×10, 2×8, 2×5) | grubość złocenia (RS podaje „gold flash”), kierunek klucza wobec pinu 1, wymiary korpusu wobec footprintu |
| 9 | Samtec **TSW-1xx-08-G-S-RA** | stan; zamiennik Harwin M20 / Amphenol FCI 68016 — sprawdzić pokrycie styku (złoto, grubość) |
| 10 | BYPASS P06 | filtr w TME: DPDT ON-ON, **jawna obciążalność DC ≥ 10 A przy ≥ 28 V**; jeśli brak — NKK S6A jako zapas |
| 11 | Przyciski panelu (kluczyk, STOP, ARM, MARK) | filtr w TME: „Pokrycie styku: złoto”, otwór **22 mm** (MARK może być 19 mm) |

## Ważne: czego ta sesja NIE mogła zrobić

Sieć środowiska odrzuca wszystkie strony producentów i sklepów, które próbowałem otworzyć (Mouser, TME, Samtec, Panasonic, Amphenol, Harwin, E-Switch: 403 albo brak połączenia). **Żadnego kodu nie sprawdziłem na karcie producenta online.** Oparłem się na kartach już leżących w repozytorium i na pamięci; kody SW1 i Amphenol poprawiono po recenzji (4.10). Każdy kod ma znacznik pewności:

| Znacznik | Znaczenie |
|---|---|
| **[K]** | potwierdzone kartą w repozytorium (podany plik) |
| **[R]** | podane w recenzji / decyzji użytkownika 4.10 |
| **[P]** | z pamięci — konwencja kodu i parametry prawdopodobne, ale **do sprawdzenia w karcie i w sklepie przed zamówieniem** |
| **[?]** | nie mam kodu, w który wierzę; podane kryteria wyboru |

Nie zmieniałem żadnego pakietu płytek.

## Podsumowanie

| # | Pozycja | Kandydat główny | Pewność | Główne ryzyko |
|---|---|---|---|---|
| 1 | SW1 P05 (na panelu) | E-Switch 100DP1T1B1M1REH + 5 przewodów AWG24 | [R] | dostępność wersji złoconej R |
| 2 | BYPASS P06 | otwarte — filtr w TME; zapas NKK S6A | [K] dla S6A, [?] dla reszty | brak jawnej obciążalności DC w kartach |
| 3 | Porty L1/L2/TEST | Amphenol AT04-12Px-PM01 + AT06-12Sx, kliny AW12P/AW12S | [R] | PM01 dla kluczy B/C w TME |
| 4 | Przyciski panelu | otwarte — filtr w TME, otwór 22 mm | [?] | minimalne obciążenie 27 µA / 3 V rzadko jest w karcie |
| 5 | IDC kątowe, goldpiny kątowe | Amphenol FCI T821…A1R100CEU; Samtec TSW-1xx-08-G-S-RA | [P] / [K] | grubość złocenia T821, klucz |
| 6 | C1 P05 / C3 P06 | Panasonic EEUFR1C221 (bez zmiany) | [P] wymiary, [K] footprint | — |
| 7 | C35 P05, C17 P06 | C35 25 V: GRM31CR71E106KA12L; C17: bez zmiany | [P] | **lista 3 ma w C35 część 16 V, BOM wymaga 25 V** |

## 1. SW1 P05 — przełącznik NA PANELU: E-Switch 100DP1T1B1M1REH

Decyzja 4.10 (po makiecie panelu, `EGRLab-AKTYWNE.md`): SW1 **nie jest montowany na P05**. Idzie na panel, a z płytką łączy go 5 przewodów wlutowanych w otwory footprintu SW1. Płytka P05 i paczka zamówieniowa bez zmian.

Kandydat główny **[R]**: **100DP1T1B1M1REH** — 100 (seria) · DP1 (DPDT ON-NONE-ON) · T1 (dźwignia standard) · **B1 (tuleja gwintowana 1/4-40UNS, 8,89 mm)** · **M1 (oczka lutownicze, raster 4,70 mm)** · **R (styki złocone)** · E (uszczelnienie) · H (nakrętka i podkładka). DigiKey 378868. **Otwór w panelu Ø 6,35 mm.** Styki złocone 0,4 VA max przy 20 V (karta `Plytki/P05-R3-review/reference/E-Switch-100-series.pdf`, str. 1) — pasuje do obwodu µA–mA.

Zapas: **100DP1T1B1M1QEH** (styki srebrne) — **tylko za zgodą użytkownika** (wymaganie złoconych styków z decyzji 29.09).

Przewody **[R]**: **5 × AWG24, ok. 80 mm**, od oczek SW1 do otworów footprintu SW1 na P05: **1, 2, 3, 5, 4 = GND; 6 wolny**. Długość do potwierdzenia na makiecie (`Plytki/Panel-S1-makieta`).

**Nieaktualne (nie kupować):** 100DP1T1B3M6REH, 100DP1T1B3M6RE oraz każda wersja kątowa **M6** (zakończenie PCB) — były kandydatami, gdy SW1 miał siedzieć na P05.

## 2. BYPASS P06 — przełącznik panelowy DPDT ON-ON ≥ 10 A DC (otwarte)

Wymagania z `P06-R2-review/docs/PROJEKT.md`: ≥ 10 A przy 12–30 V DC (silnik EGR do 6 A, w próbie biernej 10 A), oczka lutownicze, tuleja z nakrętką; biegun B niesie ok. 0,13 A.

**Filtr dla sesji lokalnej (TME):**
1. DPDT ON-ON (2 pozycje stałe), montaż panelowy, tuleja z nakrętką;
2. w karcie **jawna obciążalność DC ≥ 10 A przy ≥ 28 V** (sam prąd AC nie wystarcza);
3. oczka lutownicze lub konektory 6,3 mm na przewód do 2,0 mm².

**Jeśli żaden przełącznik nie spełni pkt 2 — zapas: NKK S6A** (karta `P06-R2-review/reference/datasheets/NKK-S.txt`: **20 A / 30 V DC** **[K]**; S6AW — z uszczelnieniem panelu). Kandydaci bez potwierdzonej obciążalności DC (Honeywell 2NT1, Carling 2FA/2GK) **[?]** — tylko jeśli karta poda DC.

## 3. Porty L1 / L2 / TEST — Amphenol AT

Klucze jak w P11 R1 (`P11-R1-review/docs/ZAKUPY.md`): **TEST = A, L1 = B, L2 = C** **[K]**.

| Rola | Gniazdo panelowe z kołnierzem (AT04) | Wtyk adaptera (AT06) | Klin gniazda / wtyku |
|---|---|---|---|
| TEST (klucz A) | **AT04-12PA-PM01** | AT06-12SA | AW12P / AW12S |
| L1 (klucz B) | **AT04-12PB-PM01** | AT06-12SB | AW12P / AW12S |
| L2 (klucz C) | **AT04-12PC-PM01** | AT06-12SC | AW12P / AW12S |

- **PM01** = kołnierz do przykręcenia w panelu **[R]**; **PM05** = kołnierz z uszczelką — opcja, jeśli PM01 niedostępne lub panel ma być uszczelniony.
- Kliny: **AW12P** (do AT04, strona pinów) / **AW12S** (do AT06, strona gniazd). **Nie W12P/W12S** — to kody Deutsch.
- Zaślepki komór: **A114017** (nie „AT114017”).

**Styki (wszystkie złocone, rozmiar 16):**

| Obwód | Pin (AT04) | Gniazdo (AT06) | Przewód |
|---|---|---|---|
| sygnały | **AT60-202-1631** (16–20 AWG) | AT62-201-1631 | 0,5–1,0 mm² |
| prąd silnika (ECU_P1, EGR_P1) | **AT60-215-1631** | **AT62-209-1631** | **2,0 mm² (AWG14) na całej długości** |

Przekrój silnika (decyzja 4.10): **AWG14 = 2,08 mm²** (nie 2,5 mm²). 2,5 mm² nie mieści się w styku rozmiaru 16 — dlatego 2,0 mm² na całej długości przewodu, ze stykami 14 AWG. Nieaktualne: AT60-201-1631 (zastąpione przez AT60-202-1631), propozycja AWG16 / 1,5 mm².

Ilości (jak w P11 R1 **[K]**, podwojone dla strony adaptera): obudowy 3 + 3, kliny 3 + 3, zaślepki 11 + 11; styki ok. 25 + 25, z czego AT60-215 / AT62-209 tylko dla komór prądu silnika (ECU_P1, EGR_P1), reszta AT60-202 / AT62-201 — do przeliczenia po decyzji, ile adapterów powstaje.

## 4. Przyciski panelu ze stykami złoconymi (P11-7) (otwarte)

Zakres według P11-1/P11-7 (`P11-S1-przygotowanie/README.md`): **4 elementy** — kluczyk 2-pozycyjny (TEST_KEY), STOP zatrzaskowy NC, ARM chwilowy, MARK chwilowy. Detektory portów są w adapterach.

**Filtr dla sesji lokalnej (TME):**
1. parametr **„Pokrycie styku: złoto”** (albo jawny „min. load” ≤ 1 mA / ≤ 5 V);
2. **jeden rozmiar otworu: 22 mm** dla kluczyka, STOP i ARM; **MARK może być 19 mm**;
3. STOP — zatrzaskowy NC (nie deklarujemy certyfikowanego E-stopu, jak w R1); kluczyk 2 pozycje; ARM i MARK chwilowe NO.

Rodziny do przejrzenia **[?]**: przemysłowe 22 mm z blokami styków „low-level/electronics” (Eaton M22, Schneider XB5/ZB5 — blok styków osobny od nasadki), antywandalowe 19 mm (APEM, Bulgin) dla MARK. Prąd styku 27 µA / 3 V — jeśli karta milczy o złoceniu, nie kupować.

## 5. Złącza IDC kątowe obudowane i goldpiny kątowe

**Footprint IDC kątowy** (`IDC-Header_2x05/2x08/2x10_P2.54mm_Horizontal`) **[K]**: raster 2,54 mm, dystans rzędów 2,54 mm, pin 1 w (0, 0), otwór 1,0 mm / pad 1,7 mm. **Korpus 8,9 mm głębokości, x = 4,38…13,28 mm** od pinu 1. **Długość korpusu 33,06 mm dla 2×10** (zakres y 0…22,86 mm to tylko rozstaw pinów, nie korpus). Goldpin 1×13 (`PinHeader_1x13_P2.54mm_Horizontal`): długość 30,48 mm, obrys do x = 10,54 mm (pin 6 mm).

**IDC kątowe obudowane, złocone (2×10 ×5, 2×8 ×2, 2×5 ×2):**
- Główny **[P]**: Amphenol FCI **T821 1xx A1R100CEU** (xx = 10 / 16 / 20; „R” = kątowe).
- Do sprawdzenia: **grubość złocenia** (RS podaje „gold flash” — dla styków µA ważne, czy to wystarcza), **kierunek klucza (wcięcie) wobec pinu 1**, wymiary korpusu wobec footprintu (8,9 mm; 33,06 mm dla 2×10), wysokość nad płytką ≤ 16,5 mm.
- Zamiennik **[P]**: Würth WR-BHD kątowe (Mouser/Farnell; TME nie ma Würtha) — kody do sprawdzenia.

**Goldpiny kątowe 1×13 (×9), 1×9 (×1), 1×7 (×1):**
- Główny: Samtec **TSW-1xx-08-G-S-RA** (xx = 13 / 09 / 07) — **OK**. Karta `P05-R3-review/reference/datasheets/TSW.txt` potwierdza **-RA** i złocenie **-G** (10 µin styk, 3 µin ogon) **[K]**.
- Zamiennik: listwy kątowe **Harwin M20 / Amphenol FCI 68016** (1×40 cięte; 133 piny = 4 szt.) **[P]** — **sprawdzić pokrycie styku** (złoto i jego grubość) przed zamianą.

## 6. C1 P05 / C3 P06 — EEUFR1C221

Footprint `CP_Radial_D6.3mm_P2.50mm` **[K]**: raster 2,5 mm, otwór 0,8 mm, pad 1,6 mm. Panasonic **EEUFR1C221** (seria FR, 220 µF / 16 V, 105 °C, niska impedancja) **[P]**: obudowa 6,3 × 11,2 mm, raster 2,5 mm, drut Ø 0,5 mm — zgodna z footprintem; wysokość 11,2 mm mieści się w limicie 16,5 mm (poziom 4) z zapasem ok. 4 mm.

Zamienniki low-ESR **[P]** (te same 6,3 × 11 / 2,5 mm): Rubycon **16ZLH220MEFC6.3X11** (seria ZLH), Nichicon **UHE1C221MPD** (seria UHE), Panasonic EEU-FM1C221 (seria FM, wyższa ESR niż FR). Zamiennik wybrać z karty wg ESR przy 100 kHz — wartość referencyjna dla FR ok. 0,3 Ω; **wymaganie ESR w BOM nie jest podane**. Q5.

## 7. C35 P05 i C17 P06

- **C17 P06 (100 nF, 50 V, X7R, 1206):** C1206C104K5RAC (KEMET) — taki sam kod jest już na liście 2 jako 100 nF 1206 **[K]** (`Zakupy-3-szkic`: 0,4073 zł, stan 146336). Bez zmian.
- **C35 P05 (10 µF, 25 V, X7R, 1206):** BOM P05 R3 podaje **25 V** (`P05-R3-review/docs/BOM.csv`), ale lista 3 przypisała część **GRM31CR71C106KA12L**, a to jest **16 V** (symbol „1C”; ta sama część jest w BOM P03 R6 jako C14 „10uF / 16V”). **To rozbieżność.** Kandydat główny dla 25 V **[P]**: Murata **GRM31CR71E106KA12L** („1E” = 25 V). Zamienniki 25 V X7R 1206 **[P]**: TDK C3216X7R1E106K160AC, Samsung CL31B106KAHNNNE. Węzeł C35 to 5VA_P05 (5 V), więc 16 V też by działało, ale 25 V jest zgodne z BOM. Q6.

## Pytania do użytkownika

Rozstrzygnięte 4.10: Q1 (BYPASS — otwarte, filtr + zapas S6A, pozycja 2), Q2 (silnik AWG14 / 2,0 mm², pozycja 3), Q3 (otwór 22 mm, MARK 19 mm, pozycja 4).

- **Q4.** Czy listwy kątowe 1×13/9/7 mają być cięte z 1×40 kątowych (4 szt.), czy kupować gotowe długości TSW?
- **Q5.** Czy BOM ma graniczną ESR dla C1/C3? Bez niej nie rozstrzygnę FR vs ZLH vs UHE.
- **Q6.** C35: kupić 25 V zgodnie z BOM (GRM31CR71E106…), czy zostawić 16 V z listy 3 (jak C14 w P03)?

Plik `kandydaci.csv` zawiera te same pozycje w formie tabeli do wklejenia do zakupów.
