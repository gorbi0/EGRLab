# 01 — Stan kampanii (overview)
*Ostatnia aktualizacja: 2026-09-29 (schemat P02 R4 w chmurze, etap 1; specyfikacja P02 R4; zasilanie z ogniw 18650, wstrzymane P01/P02, zamienniki; koncepcja obudowy Kaseta R1); wcześniej 2026-09-28 (lista zakupowa 2; pliki PCB P00/P01/P02/P04 do zamówienia); wcześniej 2026-09-27 (recenzja P05 R1; P03 R4 — bufor Schmitta w resecie do P04; recenzja P00 R2 i zamykająca P00 R3; końcowa recenzja P03 R2 i zamykająca P03 R3); wcześniej 2026-09-26 (recenzja P04 R1, P04 R2, recenzja P02 R2 i zamykająca P02 R3), 2026-09-25 (P02 R1, P00 R1, P03 R1) i 2026-09-21 (przeniesienie z projektu claude.ai „Kia Sportage”; projekt przyrządu EGRLab, obecnie w rewizji v3)*

## Auto i kontekst
- Kia Sportage SL 2013, 1.7 CRDi, silnik D4FD, ECU Bosch EDC17C08, ~280 000 km. Brak start-stop.
- Cel: rozwiązać przewlekłą usterkę EGR samodzielnie, bez warsztatów w Hiszpanii (dwóch hiszpańskich mechaników już próbowało bez skutku).
- Auto kursuje między Polską a Camposol (Murcia/Alicante, Hiszpania). Logistyka: InPost międzynarodowy, Ryanair z bagażem kabinowym.
- Historia prac: wymiana rozrządu, przepustnicy, zaworu EGR, zaworu sterującego turbiny (solenoid VGT), regeneracja wtryskiwaczy; rok wcześniej wymiana turbiny. Po wymianie rozrządu zostały połamane mocowania wiązki i luźna masa silnika (masa dokręcona).

## Stan obecny
- **Główna usterka:** przerywany **P0404** → tryb awaryjny; kasowanie w trakcie jazdy.
- **Zależność od temperatury (stroma):** lipiec/sierpień przy 35–42°C — kilka razy dziennie. Wrzesień: 7 dni po 100–300 km, **jedno** wystąpienie, w najcieplejszy dzień (~35°C); chłodniejsze dni — zero.
- **Osobny objaw, odwrotna sygnatura:** szarpanie po zimnym rozruchu przy 1500–1700 obr., ustępuje po nagrzaniu; przy porankach ~18°C zawsze, w gorące lipcowe poranki czasem wcale. Traktowane jako osobna usterka (ścieżka B).
- **Trzeci zawór EGR w ~20 tys. km**; zdejmowane zawory bez istotnego nagaru.
- **MaxiECU „Initialization EGR”** konsekwentnie kończy się błędem warunku wyzwolenia; „EGR Replacement” przechodzi na zielono. Blokada adaptacji **poprzedza** P0404; przyczyna nieznana. Ticket w MaxiECU eskalowany do developerów (zaszyfrowany log wewnętrznie niespójny).
- Wrzesień w Hiszpanii minął **bez pomiarów skopem** (goście, dużo jazdy). Powrót za kilka tygodni na pomiary.
- **Powstał projekt własnego przyrządu: `EGRLab-v3/`** — ośmiokanałowy rejestrator do auta plus tester sterujący zaworem przy zgaszonym silniku. Do budowy wieczorami w Polsce; nie zastępuje procedury v3, wchodzi po niej.

## Hipotezy (szczegóły i testy: procedura_v3_DHO804.md)
| # | Hipoteza |
|---|---|
| H1 | Wspólne przetarcie wiązki EGR ↔ AC/ECV przy pokrywie rozrządu (połamane mocowania) |
| H2 | Rezystancyjna masa potencjometru (pin 6 → GUD09) |
| H3 | Chwilowa przerwa w torze wipera |
| H4 | Zapad referencji 5 V |
| H5 | Mechanika / silnik / przekładnia / potencjometr |
| H6 | Rozwarte styki żeńskie złącza CUD87 (3× rozpinane) |
| H7 | **Sprzężenie z obwodem AC/ECV** — usterka zależy od pracy klimatyzacji, nie od temperatury (mocny kandydat) |

Uwaga: masa potencjometru EGR wraca do ECM (GUD09), nie do splotu na nadwoziu — wspólna usterka z AC wymaga więc wspólnego punktu G na nadwoziu albo fizycznego przetarcia w jednym miejscu.

**Nowa informacja (GDS, Hyundai i40 VF 2013, ten sam D4FD):** P0404 = aktuator EGR pozostaje całkowicie otwarty lub zamknięty >4 s (czas diagnozy 4,4 s); progi: wysoka temperatura silnika aktuatora albo silnik zablokowany przy otwieraniu/zamykaniu; możliwa przyczyna: **obwód silnika aktuatora**. Wcześniej traktowane jako usterka obwodu czujnika pozycji — to przesuwa wagę w stronę Kroku 5 (H-bridge, piny 1/3) i H5, a „wysoka temperatura silnika aktuatora” dobrze pasuje do zależności od upału. Procedura v3 powstała przed tym ustaleniem — do uwzględnienia w v4.

## Otwarta sprzeczność: pinout CUD87

Dwa źródła w projekcie podają różne mapowanie pinów czujnika i **nie jest to rozstrzygnięte**:

| Źródło | pin 4 | pin 5 | pin 6 |
|---|---|---|---|
| Schemat Monolith (s. 56–59 PDF), zmapowany na piny ECM | zasilanie 5 V | wiper | masa → GUD09 |
| Założenie przekazane przy projektowaniu EGRLab v1 | wiper | jedno z {5 V, masa} | drugie z {5 V, masa} |

Wersja ze schematu ma wyższą wiarygodność, bo jest wyprowadzona z dokumentu i zmapowana na CUD-K 5/20/39/31/23. Do potwierdzenia multimetrem przy pierwszym wpięciu: **który pin ma realnie 5 V przy zapłonie**. Piny 1/3 jako napęd są zgodne w obu źródłach, ale też przyjęte na wiarę — pomyłka tutaj zwiera gałąź mostka.

EGRLab v3 rozpoznaje trójkę 4/5/6 sam, sprawdzając sześć permutacji, więc nie blokuje się na tej niepewności. Procedura skopowa v3 blokuje się — tam mapowanie jest wpisane wprost.

## Przyrząd własny — EGRLab v3

Katalog `EGRLab-v3/` (v1 i v2 zostają jako punkty odniesienia). Dwie funkcje pod tę kampanię:

- **LOGGER** — osiem kanałów wspólnie próbkowanych przez wiele godzin: piny 1, 3, 4, 5, 6, prąd uzwojenia, napięcie instalacji i **kanał AUX** wpinany w punkt spoza EGR (linia ECV dla H7 albo masa GUD09 dla H2). Masa czujnika mierzona z rozdzielczością 76 µV. Wyjście **SCOPE_TRIG** wyzwala DHO804 dokładnie w chwili wykrycia anomalii.
- **TEST / HOT-SOAK** — sterowanie zaworem przy zgaszonym silniku, **bez demontażu**: po przejeździe tester co kilka minut mierzy prąd zerwania i czas przejścia na stygnącym silniku. Pod definicję P0404 z GDS (temperatura silnika aktuatora). Trzy zdjęte zawory służą jako grupa odniesienia.

Stan: dokumentacja i firmware gotowe, **bez PCB i bez kompilacji na sprzęcie**. v3 powstała po zewnętrznym przeglądzie v2, który znalazł osiem błędów blokujących — wszystkie naprawione, opis w `EGRLab-v3/docs/00-zmiany-v2-v3.md`. Szczegóły i otwarte ryzyka: `EGRLab-v3/docs/06-weryfikacja.md`.

Aktualizacja 24.09.2026: bieżący etap projektu opisuje `EGRLab-AKTYWNE.md` (baza v6.1-rc1, moduły P01–P11, płytki w `Plytki/`). Zamówiono wszystkie części z BOM P01 (TME + Mouser) oraz część układów scalonych dla P02–P10. Płytka P01 nie jest jeszcze zamówiona. Rejestr zamówień: `Zamowione/ZAMOWIONE.md`. Layout P01: PCB-R3 Astry (lokalna poprawa mojego R2: D4 przy Q1, sondowanie od spodu, BOM montażowy A1, świeży DRC w odbiorze) przyjęta w recenzji `Plytki/P01-PCB-R3-recenzja/`; poprawki z recenzji zastosowane w wydaniu R3.1 (`Plytki/P01-PCB-R3.1-review`, płytka identyczna z R3): kolejność montażu C6/Q1, BOM A1 (U4, uwagi o wyprowadzeniach). Następny krok: wydruk 1:1 i przymiarka.

Aktualizacja 25.09.2026: P01 czeka na wydruk 1:1 i przymiarkę (użytkownik), równolegle powstał pierwszy schemat i PCB P02 (zasilacz + podtrzymanie HOLD): `Plytki/P02-R1-review`. Decyzje użytkownika: bank 3 × 22 mF na płytce P02, HOLD_READY tylko lokalnie. Kontrole plików czyste (ERC 0, DRC 0/0/0, 28/28, 8/8 prób ujemnych); czeka na recenzję Astry. Sprzęt P02 nie jest kupiony poza przetwornicami i układami logiki (`docs/ZAKUPY-P02.md` w pakiecie). Następnie P00 (przyrząd stanowiskowy do odbioru płytek, 8 źródeł 3,3 V/GND + heartbeat 555): `Plytki/P00-R1-review`, decyzje użytkownika — listwy 2,54 mm, zasilanie 5–15 V z LM2937, LED przy kanałach; kontrole plików czyste (22/22, 8/8), czeka na recenzję. Astra przygotowała P02 R2 i P00 R2 (czekają na moją recenzję) oraz nowe P04 R1 i P05 R1. Następnie P03 CORE R1 (ESP32-S3, microSD, bufory, złącza wiązek): `Plytki/P03-R1-review` — decyzje użytkownika: listwy 22,86 mm, P03 i P05 obok siebie ze złączem kątowym, Adafruit 4682, CAN jako IDC 2 × 3; kontrole plików czyste (ERC 0, DRC 0/0/0, 26/26, 14/14), J1 zgodne z kopią użytą w P05 R1; czeka na recenzję Astry.

Aktualizacja 26.09.2026: recenzja P04 R1 Astry (`Plytki/P04-R1-recenzja/`, bez blokera) i na jej podstawie P04 R2 (`Plytki/P04-R2-review`): MCP100-300 zamiast -315, druga droga watchdoga niezależna od Q1, 3,3 V na złącza tylko przez rezystory, C18/R5 przy wejściu Schmitta SAFE_N, rezystory szeregowe w liniach panelu, znaczniki KEY przy złączach IDC, zszyte wylewki GND. Kontrole plików czyste (ERC 0, DRC 0/0/0, 26/26 PCB, 22/22 elektrycznych, mutacje 14/14 i 11/11, czyste odtworzenie identyczne); czeka na recenzję. Równolegle powstał P03 R2 (`Plytki/P03-R2-review`), w którym R14 na CORE_LINK nadal ma 0 Ω.

Aktualizacja 26.09.2026 (wieczór): moja recenzja P02 R2 Astry (`Plytki/P02-R2-recenzja/`) — R2 przyjęte, progi HOLD_READY odtworzone niezależnie. Na decyzję użytkownika („po tej iteracji zamykamy płytkę”) zrobiłem zamykające P02 R3 (`Plytki/P02-R3-review`): miedź jak w R2, bezpieczniki Schurter SPT 300 VDC (F2/F3 T1A, F4 T0,5A), R16 470 Ω, naprawione odtwarzanie `--rebuild`, opis pracy przy zgaszonym silniku; kontrole czyste (ERC 0, DRC 0/0/0, 29/29, 11/11). Następny krok P02: przymiarka 1:1 i zakup. Równolegle Astra zamknęła P04 wydaniem R2.1 (tylko dokumentacja, CAD identyczny z moim R2).

Aktualizacja 27.09.2026: moja recenzja P00 R2 Astry (`Plytki/P00-R2-recenzja/RECENZJA-P00-R2.md`) — w PCB brak blokera, uwagi z R1 zamknięte poprawnie; główny błąd to mapa wiązki do P04 opisana dla v6.1 (J13–J20), a nie dla zamkniętego P04-R2.1. Powstała rewizja zamykająca `Plytki/P00-R3-review` (+ zip 97783cea…): miedź, rozmieszczenie, wartości i MPN identyczne z R2; wiązka przepisana na P04-R2.1 i sprawdzana skryptem na zamrożonej netliście P04; nadruk „+VIN 6-15V” pod J10, TP3 „ZA D1”; nowe kontrole (budżet cieplny z netlisty, poziom H heartbeat, próby ujemne z próbą zerową); czysta regeneracja PASS. Do rozstrzygnięcia pomiarem przy odbiorze P00: H heartbeat na J9 z 10 kΩ ≥ 2,4 V (narożnik minimalnego VOH TLC555 schodzi do ok. 1,9 V wobec progu 2,0 V w P04) oraz temperatura U2 przy 15 V (plan B: 12 V). Otwarte: przymiarka 1:1 i zakup części P00.

Aktualizacja 27.09.2026 (P03): końcowa recenzja P03 R2 Astry (`Plytki/P03-R2-recenzja/RECENZJA-P03-R2.md`) — bez blokera, wszystkie uwagi z R1 zamknięte i sprawdzone w kartach (m.in. LTC4412 trzyma blokadę USB→5V_SYS także bez P02). Zamykające P03 R3 (`Plytki/P03-R3-review`, zip 8f25ac8f…): miedź = R2, jedyna zmiana wartości R14 (CORE_LINK) 0 Ω → 1 kΩ, nowe kontrole złączy i próby ujemne z próbą zerową. Do decyzji: wspólny reset SUP_N ma na złączu do P04 zbocze rzędu ms (EN modułu z 1 µF), niezgodne z wymaganiem 74LVC125A w P04; skutki tylko w stanie rozbrojonym, poprawka (bufor Schmitta) wymaga nowego trasowania. Przed zamówieniem P03/P05: zatwierdzony przekrój mechaniczny pary B2B.

Aktualizacja 27.09.2026 (P03 R4): na decyzję użytkownika powstało P03 R4 (`Plytki/P03-R4-review`, zip 36d73f76…): bufor Schmitta SN74LVC1G17 (U6) z R41 220 Ω i C15 100 nF między wspólnym resetem SUP_N a J4.15, więc P04 dostaje jedno zbocze ok. 10 ns zamiast narastania EN modułu (przy taśmie H_SAFE 150 mm ≤ 5,5 ns/V wobec limitu 10 ns/V). Płytki nie trasowano od nowa: miedź = R3 poza obszarem przy J4 (3 odcinki R3 zastąpione, 25 nowych elementów położonych ręcznie, HW_ARMED_CORE obchodzi U6 po B.Cu). Kontrole czyste (ERC 0, DRC 0/0/0, PCB 30/30, funkcje 53/53, mutacje 43/43, próby 18/18 + zerowa, R3 → R4 13/13), czyste odtworzenie PASS. Czeka na recenzję layoutu przy J4; dalej przekrój B2B P03–P05 przed zamówieniem.

Aktualizacja 27.09.2026 (P05): moja recenzja P05 R1 Astry (`Plytki/P05-R1-recenzja/RECENZJA-P05-R1.md`) — logika DAQ_OK/MEAS_PERMIT, bufory Ioff, przekaźniki i interfejsy poprawne (świeże ERC 0, DRC 0/0/0). Przed PCB do poprawy: odsprzęganie AD7606B po prawej stronie układu (REFCAP, REFIN/REFOUT, REGCAP, AVCC) stoi 7–21 mm od pinów, a wyjście DOUT biegnie po B.Cu pod układem (oba wbrew wytycznym karty); okno DAQ_OK jest ciaśniejsze niż tolerancja TSR 2-2450 (±2 % plus dryft temperaturowy), więc w upale może blokować pomiar (R5 5,90k → 6,04k, R7 5,23k → 5,11k). Mniejsze: próba zadziałania przekaźników w upale, R13 47k, opcjonalna dioda 1N5817, budżet pojemności 5V_SYS (ok. 538 µF z 600 µF dopuszczalnych). 28.09: karta AD7606B Rev. B (od użytkownika) potwierdziła wszystkie 64 piny i odsprzęganie REFIN/REFOUT.

Aktualizacja 28.09.2026 (zakupy): lista zakupowa 2 dla P00, P02–P06, P08–P11 w `Plytki/Zakupy-2/ZAKUPY-2.md` (netto po zamówieniach z 24.09, P03-R5 i P04-R2.2, wartości P05 z recenzji; niezamówiona). TME ok. 855 zł netto, Kamami ok. 42 zł, Farnell ok. 247 zł, Mouser ok. 344 zł — wszystko na stanie. Części niedostępne do 2027 zastąpione 1:1 bez zmiany PCB: ADR4525BRZ → REF5025AIDR (P05), SN74LVC1G37DBVR → DBVRQ1 (P03), 5k1 0,1 % → 5k11 (P06), Molex 39-29-9129 → 39-29-6128 (P11). Do decyzji: bocznik PBV (tylko DigiKey, 163 zł), przyciski EAO (panel P11). W ZAKUPY-P00 (R3) wiązka stanowiskowa do P04 miała błędnie żeńskie IDC16 i Mini-Fit 4p — lista kupuje męskie.

Aktualizacja 28.09.2026 (PCB): pliki do zamówienia P00, P01 i P02 w Satland Prototype (Gdańsk) — `Plytki/Zamowienie-Satland/` (ZIP-y, specyfikacje, instrukcja, gotowy mail). P00 i P02 dostały paczki na wzór P01 (DRC 0/0/0, kontrola CAM 20/20, próby ujemne 7/7). Miedź 35 µm na wszystkich trzech płytkach (P01/P02 zmienione z 70 µm ze względu na koszt; przed P07 próba nagrzewania toru 5 A). Fabrykapcb.pl nie pasuje technologicznie (pierścienie, odstępy). Przymiarka 1:1 części przed wysyłką zamówienia — nie wykonana.

Aktualizacja 28.09.2026 (PCB P04): do zamówienia dołączona P04-R2.2 — `Plytki/P04-PCB-R2.2-zamowienie` (ZIP 1f7e9b84…), także w `Plytki/Zamowienie-Satland/`. Płytka bajtowo zgodna z wydaniem R2.2 (miedź, wiercenia i rozmieszczenie jak w zamkniętej R2.1; zmiana tylko R17 → 10 kΩ). DRC 0/0/0, kontrola CAM 20/20, próby ujemne 8/8. Najdrobniejsza z czterech: 101 przelotek z pierścieniem 0,20 mm (dokładnie minimum Satlandu, w JLCPCB bez znaczenia). Przymiarka 1:1 — nie wykonana.

Aktualizacja 29.09.2026 (obudowa): użytkownik obawiał się, że urządzenie nie zmieści się pod maską. Projekt zakłada elektronikę w kabinie (v4.1: „Elektronika w kabinie albo na stole; w komorze silnika tylko odpowiednie przewody i izolowane termopary”; P01/P02 liczone na 0–50 °C). Koncepcja kasety `Plytki/Kaseta-R1/` (płytki pionowo na prętach M3, dwie kolumny, panel z przodu): wariant LOGGER bez P04/P07/P08 — 361 × 209 × 151 mm (11,4 l), pełny — 361 × 265 × 151 mm (14,5 l); widoki z góry 1:1 do przymiarki w aucie. Długości wiązek v6.1 (pod płaski nośnik) w większości trzeba wydłużyć; wrażliwe: TAPS (wymaga przeniesienia J7 na P11), ogonki DT i VSENSE, SAFE, SPI. Makieta i przymiarka — nie wykonane.

Aktualizacja 29.09.2026 (decyzje użytkownika): przyrząd będzie zasilany z pakietu Li-ion 18650 (rekomendacja 4S, 12,0–16,8 V, ok. 50 Wh; ogniwa ładowane poza autem i wkładane naładowane, koszyk na zewnątrz obudowy) zamiast z instalacji auta — akumulator auta zostaje tylko jako sygnał mierzony VBAT, a masa przyrządu łączy się z autem wyłącznie przez odniesienie TAPS. P01 PROTECT i podtrzymanie HOLD w P02 stają się zbędne; powstanie nowa płytka zasilania (bezpiecznik, BMS 4S, P-MOSFET z UVLO i PG zamiast diody D2, TSR 5 V/3,3 V, VMOTOR, złącze PG do P04 bez zmian). Zamówienie PCB P01 i P02 wstrzymane, P00 i P04 bez zmian. Przyjęte zamienniki tańsze: EAO → zwykłe przyciski, PBV → bocznik 2512 Kelvin, C&K 7201 i NKK S6A → zwykłe przełączniki, DEUTSCH tylko przy adapterach. CAD jeszcze niezmieniony.

Aktualizacja 29.09.2026 (P02 R4): specyfikacja nowej płytki zasilania w `Plytki/P02-R4-specyfikacja/` — pakiet 4S przez XT60, P-MOSFET SUP53P06 z UVLO 13,47/12,47 V i włącznikiem na panelu, 2200 µF podtrzymania (po sygnale PFAIL_N co najmniej 14 ms przy 6 W) ładowane przez rezystor i diodę, TSR 2-2450/2-2433 bez zmian, złącze PG do P04 przeniesione z P01 (P04 bez zmian), CH7 P05 mierzy akumulator auta (propozycja: pin 16 OBD). Większość elementów sterujących pochodzi z zakupów do P01. Tanie moduły przetwornic z Allegro odrzucone dla szyn zasilających pomiar. Czeka na akceptację decyzji D-01…D-07, potem schemat.

Aktualizacja 29.09.2026 (repozytorium): decyzje D-01…D-07 przyjęte (D-01 ze zmianą: VBAT z klemy akumulatora w komorze, bo wszystkie połączenia z autem mają być w komorze). Przy projekcie schematu wyszedł błąd specyfikacji: jeden tranzystor nie da jednocześnie ochrony polaryzacji i wyłączania — są dwa SUP53P06 przeciwsobnie, tor sterowania przechodzi z P01 R3, UVLO 13,53/12,51 V (`Plytki/P02-R4-specyfikacja/STAN-PRAC.md`). Katalog projektu jest repozytorium git `github.com/gorbi0/EGRLab` (prywatne) przygotowanym pod sesje Claude w chmurze (`docs/CHMURA.md`).

Aktualizacja 29.09.2026 (chmura): pierwsza sesja w chmurze (gałąź `chmura-srodowisko`) sprawdziła środowisko. PPA KiCada i mirrory Debiana są blokowane przez politykę sieci, więc KiCad 10.0.6 działa z oficjalnego obrazu Docker (`scripts/setup-chmura.sh`, `scripts/egrlab-docker`). Kontrole zamkniętych pakietów odtworzone na kopiach z wynikami jak w repozytorium: P02-R3 — ERC 0, DRC 0/0/0, kontrole elektryczne 11/11, PCB 29/29, próby ujemne 10/10; P04-PCB-R2.2 — DRC 0/0/0, CAM 20/20, próby ujemne 8/8 + zerowa. Gerbery P04 z Linuksa są równoważne wydanym (w miedzi pojedyncze wierzchołki wylewek różnią się o 1 nm). Zamknięte pakiety niezmienione; różnice Windows/Linux i czasy w `docs/CHMURA.md`.

Aktualizacja 29.09.2026 (P02 R4, etap 1): sesja w chmurze zrobiła schemat nowej płytki zasilania `Plytki/P02-R4-review` (bez PCB): 4 arkusze A3, ERC 0, 317/317 pinów zgodnych z listą części, kontrole elektryczne 35/35, próby ujemne 19/19. UVLO nominalnie 13,50/12,55 V (obwiednia 12,90–14,08 / 11,98–13,11 V — szerzej niż ±0,34 V ze specyfikacji, ale 3S nie startuje, a 4S przy 3,6 V/ogniwo startuje zawsze). R23 22 kΩ wydłuża wyłączenie Q1 do 44–71 µs nominalnie i do ok. 240 µs w narożniku, bez skutków dla PFAIL_N. Podtrzymanie po PFAIL_N w najgorszym narożniku 11,1 ms przy 6 W (Z-08: 14 ms) — do decyzji: przyjąć albo C_H 3300 µF. PFAIL_N buforuje wyjście OK (odstępstwo od dosłownego D-06, bo porównanie tego samego węzła mogło drgać albo wrócić na H w czasie podtrzymania). Czeka na lokalną recenzję schematu.

Aktualizacja 29.09.2026 (recenzja etapu 1 P02 R4): PR #2 scalony po lokalnej recenzji (`Plytki/P02-R4-recenzja/RECENZJA-P02-R4-ETAP1.md`). Decyzje użytkownika: transil D3 5KP24A zamiast 5KP18A (Z-01: bez uszkodzeń do 25 V), C_H zostaje 2200 µF (Z-08 przepisane na ≥ 10 ms w najgorszym narożniku; jest 11,1 ms), UVLO bez zmian (Z-02 i O-02 przepisane na obwiednię narożników). Włącznik PWR na panelu i SW1 w P05 muszą mieć złocone styki, bo przełączają prądy rzędu µA–mA. SW1: E-Switch 100DP1T1B1M2REH (Mouser, ok. 17 zł; rozstaw nóżek do potwierdzenia). Równolegle w chmurze P05 R2; następny krok P02 R4: etap 2 (PCB).

## Najbliższe kroki (przy powrocie do Hiszpanii)
1. Potwierdzić pinout CUD87 ze schematu i multimetrem, **zanim cokolwiek zostanie wpięte**.
2. Test A (klimatyzacja) — kwadrans, każda pogoda.
3. Dzwonienie każdej żyły EGR multimetrem przy jednoczesnym wyginaniu wiązki.
4. Dalej wg kolejności w procedurze v3 (Krok 0 → 2 → 1 → 6c → 6a/6b → 3 → 4 → 5 → 7).
5. Dopiero potem EGRLab: LOGGER w wariancie back-probe (bez ruszania złącza) → LOGGER inline z prądem → TEST i HOT-SOAK.
6. Od zaraz: w każdej sesji Car Scanner logować temperaturę otoczenia/IAT i stan pracy AC; każde P0404 do `dziennik-zdarzen.csv`.

## Decyzje
- **Zaślepienie EGR — odrzucone:** nie wpływa na obwód elektryczny (P0404 nie jest usterką przepływu).
- **Programowe usunięcie EGR — odrzucone:** maskuje, nie naprawia.
- **Kolejność przyrządów:** skop i procedura v3 idą przed EGRLabem. Rozpięcie CUD87 jest operacją zaburzającą H6 (styki rozpinane już 3×) i raz zrobione nie da się cofnąć — dlatego pierwsza sesja rejestratora idzie na sondach back-probe, bez ruszania wtyczki.
- **Emulacja EGR — nadal odrzucona:** EGRLab mierzy i steruje zaworem, ale nie udaje czujnika przed ECU i nic nie zapisuje do sterownika.
