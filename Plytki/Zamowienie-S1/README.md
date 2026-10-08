# Wspólne zamówienie płytek S1 (JLCPCB) — 4.10.2026

*7–8.10.2026 (gałąź `zamowienie-pelny-s1`): wariant pełny — P04 R3, P07 S1, P08 R2, P12 R2 zamiast P12 R1; recenzja P04 / P08 / P12 R2 z 6.10 i P07 z 8.10 na końcu.*

*Uzupełnienie 4.10 wieczorem: P11 R2 (PCB po schemacie z chmury) i P12 R1 (płytka połączeń krawędzi A, wariant LOGGER).*

Decyzja użytkownika 4.10.2026: paczki produkcyjne dla wszystkich płytek z zatwierdzonym layoutem i jedno zamówienie. Każda paczka ma DRC 0 / 0 / 0, kontrolę CAM 20/20, próby ujemne CAM 8/8 z próbą zerową i oględziny podglądów; stan `FABRICATION_FILES_VERIFIED`. Przymiarka 1:1 i odbiór sprzętu: **NIE ZBADANO**.

| Płytka | Plik do wgrania | Wymiar [mm] | Opis | PTH / NPTH | SHA-256 ZIP | Stan |
|---|---|---|---|---|---|---|
| P02 R4 | `P02-PCB-R4-zamowienie/DO-ZAMOWIENIA_P02-PCB-R4.zip` | 160 × 100 | obie | 363 / 16 | `83585ce0…` | zamawiać (F1 = wkładka MINI 7,5 A, decyzja 5.10) |
| P03 R6 | `P03-PCB-R6-zamowienie/DO-ZAMOWIENIA_P03-PCB-R6.zip` | 160 × 100 | góra | 448 / 14 | `05997683…` | zamawiać |
| P04 R3 | `P04-PCB-R3-zamowienie/DO-ZAMOWIENIA_P04-PCB-R3.zip` | 160 × 100 | góra | 409 / 12 | `1b7478eb…` | zamawiać (recenzja 6.10: bez BLOCKER) |
| P05 R3 | `P05-PCB-R3-zamowienie/DO-ZAMOWIENIA_P05-PCB-R3.zip` | 106,5 × 100 | obie | 362 / 12 | `2b922d52…` | zamawiać |
| P06 R2 | `P06-PCB-R2-zamowienie/DO-ZAMOWIENIA_P06-PCB-R2.zip` | 106,5 × 100 | obie | 228 / 14 | `d73c5de0…` | zamawiać |
| P07 S1 | `P07-PCB-S1-zamowienie/DO-ZAMOWIENIA_P07-PCB-S1.zip` | 106,5 × 100 | obie | 360 / 16 | `31102a53…` | zamawiać — **4 warstwy, osobna pozycja w JLCPCB** (patrz niżej) |
| P08 R2 | `P08-PCB-R2-zamowienie/DO-ZAMOWIENIA_P08-PCB-R2.zip` | 53 × 100 | obie | 153 / 6 | `18637d14…` | zamawiać (recenzja 6.10: bez BLOCKER) |
| P09 R2 | `P09-PCB-R2-zamowienie/DO-ZAMOWIENIA_P09-PCB-R2.zip` | 53 × 100 | obie | 157 / 4 | `644e0379…` | zamawiać (8.10: pomiar modułu MAX31856 XU zgodny z footprintem) |
| P10 R2 | `P10-PCB-R2-zamowienie/DO-ZAMOWIENIA_P10-PCB-R2.zip` | 53 × 100 | góra | 74 / 6 | `92e5323c…` | zamawiać |
| P11 R2 | `P11-PCB-R2-zamowienie/DO-ZAMOWIENIA_P11-PCB-R2.zip` | 36 × 100 | góra | 104 / 10 | `a77181a0…` | zamawiać |
| P12 R2 | `P12-PCB-R2-zamowienie/DO-ZAMOWIENIA_P12-PCB-R2.zip` | 160 × 136 | obie | 403 / 8 | `fd44318b…` | zamawiać (8.10: kontrakt z końcową płytką P07 potwierdzony, 56 OK / 0 czeka) |

P12 R1 (LOGGER, `P12-PCB-R1-zamowienie`) **nie wchodzi** do zamówienia — zastępuje ją P12 R2 wariantu pełnego (decyzja 5.10: wszystko razem z wariantem pełnym).

Ustawienia JLCPCB dla wszystkich **poza P07**: FR-4, 2 warstwy, 1,6 mm, 1 oz, HASL bezołowiowy, maska zielona, opis biały, Via Covering: Tented, bez PCBA i szablonu. P03 i P10 mają opis tylko od góry (w ZIP nie ma warstwy dolnego opisu). Szczegóły: `SPECYFIKACJA-DLA-PRODUCENTA.txt` w każdej paczce. **P07 S1 to osobna pozycja: 4 warstwy, stos JLC04161H-7628 (zewnętrzne 1 oz, wewnętrzne 0,5 oz), reszta jak wyżej — według `P07-PCB-S1-zamowienie/SPECYFIKACJA-DLA-PRODUCENTA.txt`** (decyzja użytkownika 6.10).

Przed wysłaniem:
1. ~~P09 — porównać zmierzony moduł MAX31856 z footprintem~~ — zrobione 8.10 (użytkownik): raster, wymiar w stronę terminala, położenie listwy, wysokość, kolejność pinów i GND zgodne; P09 zamawiać.
2. Niezależna recenzja paczek (zadanie dla chmury `Plytki/Format-S1/zadania/ZADANIE-RECENZJA-ZAMOWIENIA-S1.md`) — zalecane przed wysłaniem plików.
3. Wydruk 1:1 z PDF wydania (`projekt/output/pdf/`) i przymiarka dużych części: C1 / C3 220 µF, złącza IDC.

**SW1 P05 (decyzja 4.10 po makiecie panelu):** przełącznik nie jest montowany na P05. Idzie na panel (E-Switch 100 z oczkami), a 5 przewodów wchodzi w otwory footprintu SW1 (1, 2, 3, 5, 4 = GND). Płytka bez zmian.

Taśmy IDC do P12 (do zakupów): 9 krótkich taśm płytka → P12 (ok. 30 mm; P12 stoi 18–20 mm przed krawędzią A) i taśma P11 → P12 ok. 100 mm (szacunek 65–80 mm). Złącza na P12: proste IDC obudowane (Amphenol T821…S100CEU — kod do potwierdzenia w zakupach). Wtyki zaciskać tak, by pin 1 trafiał w pin 1 po obu stronach (rozumowanie: `P12-R1-review/README.md`, PDF str. 5).

## Recenzja 6.10 (P04 R3, P08 R2, P12 R2) i uwagi do zamówienia wariantu pełnego

Niezależny przegląd paczek (sumy ZIP, manifesty, BOM ↔ footprint, DRC z paczek, otwory M3 i J_BP wobec `Format-S1/format-s1.json`, kontrakty P12 R2 pin po pinie z płytek KiCad: 16 złączy, 276 pinów, 0 różnic; prądy 5V_SYS przez IDC): **BLOCKER brak**. Ustalenia:

1. **MAJOR (stos, poziom 5) — rozstrzygnięte w P07:** przewody 2,0 mm² P07 J1–J4 przy x = 0 szły nad P08. Decyzje użytkownika 6.10 wieczorem i 7.10: J1, J2, J4 przy krawędzi x = 106,5 (w stosie x = 160), J3 na krawędzi B; żaden przewód nad P08. P04, P08, P12 bez zmian.
2. **MINOR P04 C18** (KEMET C320C102J1G5TA, posiadany): raster nóżek 2,54 mm, footprint 5,00 mm — przy montażu rozgiąć nóżki; płytka bez zmian.
3. **MINOR (zakupy, montaż) — klucze IDC:** kontrakt pin w pin działa tylko, gdy szczelina klucza kątowych wtyków 2 × 5 / 2 × 8 / 2 × 10 jest po stronie przeciwnej do PCB (jak footprint KiCad), a gniazda P12 są wlutowane wycięciem zgodnie z nadrukiem. Taśma odwrócona o 180° łączy pin k z pinem 2N + 1 − k, czyli 5V_SYS z GND. Przy zakupie sprawdzić rysunek producenta; **przed pierwszym zasileniem P12: pomiar TP2 (5V_SYS) ↔ TP1 (GND) bez zwarcia po wpięciu każdej taśmy.**
4. **NIT:** linie nadruku z bibliotek 0,12 mm (jak w paczkach LOGGER); teksty ≥ 1,0 / 0,15 mm.

NIE ZBADANO w recenzji: przymiarki taśm i rysunków IDC T821, taśmy P11 → J10, kart MCP100 / WIMA / EEU-EB1J100, integralności SPI na P12. Po scaleniu do main: `P12-przygotowanie/zrodla.json` przełączyć na `origin/main` i powtórzyć kontrakty.

## Recenzja P07 S1 (8.10, po zamknięciu paczki)

Paczka: DRC 0 niepołączonych / 0 niezgodności (4 × lib_footprint_mismatch od przyciętego nadruku, przyjęte jak w innych paczkach), kontrole PCB 35/35, próby ujemne 41/41, CAM 24/24 (cztery warstwy miedzi, pola wewnętrzne po położeniu), próby ujemne CAM 9/9 + zerowa, oględziny podglądów (góra, F / B / In1 / In2). Stos S1: J_BP1 / J_BP2 w x 26,500 / 80,000 (kontrakt P12 R2 — 56 OK), osiem M3 w pozycjach S1, K1 15,7 mm ≤ 16,5, od spodu tylko SMD ≤ 1,5 mm ≥ 1 mm od THT. **MAJOR-1 z 6.10 zamknięty:** J1 / J2 / J4 przy krawędzi x = 106,5, J3 na krawędzi B; żaden przewód nad P08.

Uwagi (bez wpływu na zamówienie): J5 wystaje 0,45 mm za krawędź x = 106,5 (taśma do modułu na ściance — obudowa dobierana do stosu); przewody J4 → P11 obchodzą stos (ok. 450 mm, `P07-S1-review/docs/WIAZKA-MODUL.md`); decyzje sporne (ścieżki 0,2 mm, przelotki 0,6 / 0,3, logika na In2 pod blokiem przekaźnika) opisane w README wydania P07. NIE ZBADANO: przymiarka 1:1, montaż, pomiary modułu D / E.

## P09 — pomiar modułu MAX31856 (8.10)

Użytkownik zmierzył oba egzemplarze modułu MAX31856 XU bez zasilania: raster listwy 1 × 9 (2,54 mm), wymiar od osi rzędu w stronę terminala, położenie rzędu wzdłuż boku, wysokość (listwa + płytka + terminal ≤ 16,5 mm), kolejność pinów VIN … DRDY z napisów i GND — wszystko zgodne z footprintem `P09:MAX31856_XU`. P09 R2 zamawiana bez zmian. Przed lutowaniem zostają kroki elektryczne 2–4 z `P09-R2-review/docs/MODUL-KWALIFIKACJA.md` (3Vo przy VIN 3,3 V, ewentualnie wariant 5 V i JP1 / JP2).
