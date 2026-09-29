# Recenzja P01-PCB-R1-review

24.09.2026 · recenzent: Claude (Opus 5.5) · przedmiot: `../P01-PCB-R1-review/` w stanie otrzymanym; archiwum zgodne z `.sha256` (74c9ee76…8c2d). Pakietu nie zmieniano.

**Wynik: nie eksportować jeszcze Gerberów.** Płytka jest czysta w DRC, a tor mocy jest zwymiarowany poprawnie. Są jednak dwa błędy projektowe, których DRC z zasady nie widzi (PCB1-01, PCB1-02). Oba są tanie do poprawienia. Do tego dochodzi zestaw słabości rozmieszczenia (PCB1-03 do PCB1-06), które warto usunąć przy okazji tych poprawek, bo i tak zmieniają trasy w tych samych miejscach.

Dowody w `skrypty/`. Skrypty uruchamia się Pythonem z KiCada (moduł `pcbnew`) z argumentem w postaci ścieżki do pliku `.kicad_pcb`. Wydruki są w `skrypty/wynik.txt`.

## Rejestr uwag

| ID | Waga | Krótko |
|---|---|---|
| PCB1-01 | **BLOKUJE eksport** | Pływające radiatory stoją na miedzi różnych sieci; jedyną izolacją jest maska |
| PCB1-02 | **BLOKUJE eksport** | Q2 (TO-220 bez radiatora) nie ma na nadruku oznaczenia orientacji; odwrotny montaż wyłącza całe zabezpieczenie |
| PCB1-03 | WAŻNE (jakość) | Rozmieszczenie nie trzyma bloków funkcjonalnych; wrażliwe wejście OV_REF biegnie 107 mm przez tor mocy |
| PCB1-04 | drobne | Wiązka PG z J5 wychodzi w głąb płytki, nad elementy |
| PCB1-05 | drobne | C6 stoi 18 mm od Q1; pętla G–S przez C6 ma ~40 mm |
| PCB1-06 | drobne | J1/J2/J4/J8 bez nazw sieci na nadruku; D9 daleko od Q2 wbrew notatce R2 |

---

## PCB1-01 — radiatory na miedzi różnych sieci

Radiatory SK129 stoją bezpośrednio na stronie F. Są celowo odizolowane — pady ich kołków nie mają sieci, a TO-220 montuje się przez podkładkę izolacyjną. Pod krawędziami profilu (obrys F.Fab footprintu HS) leży jednak miedź kilku sieci. Między aluminiowym profilem a miedzią jest tylko maska (~20 µm). Profil dociskają lutowane kołki i śruba TO-220, a całość pracuje w samochodzie, czyli w drganiach.

Pomiar z `radiatory_miedz.py`, gdzie wartość ujemna oznacza, że miedź leży pod metalem:

| Radiator | Sieć | Odcinek | Krawędź profilu względem miedzi |
|---|---|---|---|
| HS1 | **BAT_FUSED** | 5 mm, (15;31,5)→(44;31,5) | −1,50 mm (końce żeber na ścieżce) |
| HS1 | **BAT_FUSED** | 2 mm, (44;31,5)→(49;28) | −1,00 mm (koniec ścianki) |
| HS2 | **P01_GATE** | 0,8 mm, (99;30)→(98;34) | −0,38 mm |
| HS2 | **P01_GATE** | 0,8 mm, (103;26)→(99;30) | −0,05 mm |
| HS2 | P01_Q1_DRAIN | 2 mm, (115;30)→(118;34) | +0,10 mm (styk z krawędzią) |
| HS1, HS2 | GND | wylewka pod resztą obrysu | — |

Przebicie maski w dwóch miejscach pod jednym radiatorem daje:
- **HS1: BAT_FUSED z GND** — zwarcie przewodu akumulatora; przepala się bezpiecznik 5 A.
- **HS2: GATE z GND** — Q1 nie daje się wyłączyć, czyli OVP przestaje działać, a R27 przy próbie wyłączenia grzeje się ~20 W.
- **HS2: DRAIN z GND** — zwarcie wyjścia.

Pakiet zakłada izolację radiatorów („radiatory odizolowane od tabów i sieci PCB”), ale żadna kontrola nie sprawdza miedzi pod profilem.

**Poprawka:**
- Na F.Cu obszar reguł (bez ścieżek i bez wylewki) pod obrysem profilu, z zapasem ~0,5 mm, poza wnęką TO-220.
- BAT_FUSED, GATE i DRAIN poprowadzić poza tym obszarem.
- Minimum to brak miedzi innych sieci niż GND. Najczyściej: brak jakiejkolwiek miedzi, a radiator pozostaje pływający, jak zakłada projekt.
- Do `verify_pcb.py` dodać kontrolę „brak miedzi F.Cu w obrysie styku radiatora”.

## PCB1-02 — Q2 bez oznaczenia orientacji

Q1, Q2 i D2 nie mają na nadruku żadnego obrysu ani znacznika strony radiatora — tylko pady i oznaczenie. Pakiet świadomie usunął te obrysy z nadruku, bo kolidowały z padami (LAYOUT.md). Dla Q1 i D2 kierunek wymusza radiator. **Q2 stoi bez radiatora, więc da się go wlutować obróconego o 180°.**

Skutek odwrotnego montażu Q2:
- Fizyczna bramka trafia w pad 3 (VS), a źródło w pad 1 (OFF_BASE). VGS jest wtedy zawsze ≥ 0, więc Q2 nigdy nie przewodzi.
- Dioda strukturalna (dren → źródło, czyli OFF_COL → OFF_BASE) przewodzi przez R27 do OFF_BASE.
- Bez ENABLE OFF_BASE jest ściągany przez R23 do masy (D9 zatrzymuje go na VS − 15 V).
- W efekcie GATE ≈ OFF_BASE + 0,7 V, więc VSG ≈ VS − 0,8 V, z ograniczeniem do 15 V przez D4.

**Q1 przewodzi zawsze, gdy jest VS** — niezależnie od AUX5, OVP, UVLO i INHIBIT. Domyślne OFF i odcięcie OVP znikają całkowicie. Wykryje to ODBIOR, krok 2: przy zwartym J3 i 13,8 V / 100 mA LED musi być zgaszona. To jednak nadal pułapka montażowa z prawdopodobieństwem 50%, a jej skutek wyłącza główną funkcję płytki.

**Poprawka:** na nadruku Q2 obrys TO-220 albo przynajmniej gruba linia po stronie taba plus napis „TAB”. Najlepiej to samo dla Q1 i D2, dla spójności. Do kontroli dodać regułę „każdy element orientowany ma znacznik orientacji na F.SilkS”.

## PCB1-03 — rozmieszczenie i wrażliwe sieci

Rozmieszczenie wygląda na automatyczne upakowanie: elementy stoją w siatce, a nie w blokach funkcji. Najważniejszy skutek: R8 (histereza OVP, 220 kΩ) stoi na górze, między radiatorami (80; 14–29,5), 45–60 mm od U2. Wynik z `sieci_czule.py`:

| Sieć | Długość | Blisko toru mocy |
|---|---|---|
| OV_REF (wejście + komparatora OVP, ~9,6 kΩ, bez filtra) | 107 mm | krzyżuje BAT_FUSED i VS na drugiej warstwie; na tej samej warstwie 0,55–0,67 mm od nich |
| P01_OK | 210 mm | 0,5–0,7 mm od VS i BAT_FUSED |
| OV_SENSE / UV_SENSE / REF | 51 / 79 / 97 mm | poza torem mocy — dobrze |

Inne długie trasy z tego samego powodu: BUF_BASE 75 mm (R15 przy D6, Q6 w środku), ON_COL 64 mm (R21 przy J6), FAULT_BASE 56 mm.

**Skutek elektryczny oceniam jako mały.** Sprzężenie rzędu pF do węzła ~10 kΩ daje zakłócenia trwające ~µs, a OVP ma budżet 100 µs; kierunek sprzężenia raczej opóźnia wyzwolenie, niż je fałszuje. Takie rozmieszczenie utrudnia jednak pomiary i poprawki na stole (sieć idzie przez całą płytkę) i zabiera margines szumowy bez powodu.

**Zalecenie:**
- R7 i R8 przy nóżce 3 U2.
- R13 i R11 przy U2 i U4.
- R14, R15, D7 i D8 wokół Q6.
- R21 przy Q3.

Po PCB1-01 trasy w tym rejonie i tak trzeba poprawić.

## PCB1-04 — kierunek wyjścia wiązki PG (J5)

Pady J5 są na X = 143, a kotwy opaski na X = 130,5. Żyły wychodzą więc w głąb płytki, a zaraz za opaską stoją R31, R17 i R18. MECHANIKA każe jednocześnie „nie kłaść żył nad rezystorami”, co zostawia tylko ostre zagięcie w dół, do krawędzi odległej o 5 mm. Lepiej obrócić J5 tak, żeby żyły wychodziły prostopadle do najbliższej krawędzi. Uwaga: prawa krawędź koliduje z keepoutem H4, więc zostaje dolna albo przesunięcie J5 wyżej.

## PCB1-05 — położenie C6

C6 (1 µF, G–S) stoi w (100–105; 40), a Q1 w (105–110,5; 22,3). Droga G–S przez C6 ma ~40 mm, a pole pętli ~180 mm². Przy podłączeniu 48 V / 1 µs prąd C5 ~0,5 A na indukcyjności pętli ~0,1 µH daje oszacowanie rzędu 0,1–0,2 V dodatkowego VSG. Model R2/R3 bez pasożytów layoutu dawał 0,6 V przy kryterium 0,8 V. Przy poprawianiu tras GATE (PCB1-01) warto przesunąć C6 do wylotu wnęki radiatora (y ≈ 32–34).

## PCB1-06 — drobiazgi nadruku i położenia

- **J1/J2/J4/J8:** na nadruku tylko numery złączy. ODBIOR odwołuje się do J4.2 (SAFE_N) i J1.1 (BAT_FUSED) — warto dopisać nazwy sieci przy polach.
- **D9:** stoi ~25 mm od bramki Q2, choć MECHANIKA R2 mówiła „D9 przy G/S Q2”. Elektrycznie bez znaczenia (zacisk statyczny), ale niezgodne z własnym wymaganiem pakietu.

---

## Sprawdzone bez uwag

| Zakres | Wynik |
|---|---|
| DRC i zgodność ze schematem | Własne uruchomienie na kopii (`kicad-cli pcb drc --severity-all --schematic-parity --refill-zones`): 0 / 0 / 0. W projekcie wyłączone tylko domyślnie wyłączane kategorie KiCada; lista wyjątków pusta. |
| Kontrole pakietu | `verify_pcb.py` na kopii: 17/17 PASS. Żadna z nich nie dotyczy miedzi pod radiatorem ani znaczników orientacji. |
| Tor 5 A | Najwęższe odcinki mają 2 mm na jednej warstwie 70 µm (BAT_FUSED do anod D2, VS z D2 i do źródła Q1, DRAIN do LK1), każdy ≤ ~20 mm. Według IPC-2221 daje to ~5 °C przyrostu przy 5 A. Szyna VS ma 5 mm na obu warstwach. Powrót GND prowadzi pierścień 5 mm (B) i obie wylewki. |
| Termiki | J7: szprychy 1,2 mm / szczelina 0,3 mm na obu padach. D1.2, D3.2 i J6.2 mają bezpośrednie ścieżki 4–5 mm. |
| Pętle TVS | D1: ~12 mm od J7, powrót 4 mm (B). D3 za LK1, powrót 5 mm do J6.2. Rozsądnie przy obudowie P600 z rastrem 20 mm. |
| J6 | Korpus od X 146 do 158, więc wtyk wchodzi od prawej krawędzi. Opisy OUT+/GND/NC. |
| TO-220 a radiator | Rząd nóżek 3,3 mm od płyty montażowej radiatora; tył taba 0,1 mm od płyty według F.Fab. Zgodne z geometrią TO-220 w KiCadzie; rzeczywiste dojście z podkładką sprawdzi przymiarka (M-01). |
| LK1 | Pola DRAIN i VPROT rozdzielne; odczepy Kelvina 0,4 mm; C5 podpięty do pola siłowego. Otwór Ø2,4 dla drutu Cu 2,5 mm² (Ø1,78) pasuje. |
| TP1/TP2 | 4,8 / 4,7 mm od Q1, wewnątrz otwartej wnęki radiatora — dostępne z góry. |
| Mocowania, krawędzie | 4 × NPTH Ø3,2 z keepoutem Ø8 na obu warstwach; wylewka 1 mm od krawędzi. |
| Nadruk pozostałych elementów | Paski i „K” na D3–D9, „+” na elektrolitach, spłaszczenia TO-92, wycięcie DIP-8, opisy J5 1–6 oraz J7 B+/GND. Tekst 1,0 / 0,15 mm. |

## Ocena jakości pracy

Proces jest wzorowy. DRC i kontrole są powtarzalne i związane z hashami, a próby ujemne potwierdzają, że kontrole działają. Wymagania funkcjonalne z R3 (Kelvin LK1, TP przy Q1, termiki J7, kotwy wiązek) zostały zamienione na sprawdzalne reguły. Dokumentacja jest uczciwa co do tego, czego nie zbadano. Tor mocy jest zwymiarowany poprawnie i z zapasem.

Słabością jest to, czego automatyczne kontrole nie obejmują: **interakcja mechaniki z miedzią** (radiator na ścieżkach) oraz **montaż** (orientacja Q2). Oba błędy są tego samego rodzaju co R1-01 w schemacie: zapis jest wierny, ale nikt nie zadał pytania „co tu fizycznie dotyka czego”. Do tego dochodzi rozmieszczenie typowe dla automatu — elektrycznie poprawne, ale nie takie, jakie zrobiłby człowiek znający funkcję bloków.

Po PCB1-01 i PCB1-02 (oraz najlepiej PCB1-03 przy tej samej zmianie) płytka nadaje się do wydruku 1:1 i przymiarki.
