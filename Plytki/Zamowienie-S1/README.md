# Wspólne zamówienie płytek S1 (JLCPCB) — 4.10.2026

*Uzupełnienie 4.10 wieczorem: P11 R2 (PCB po schemacie z chmury) i P12 R1 (płytka połączeń krawędzi A, wariant LOGGER).*

Decyzja użytkownika 4.10.2026: paczki produkcyjne dla wszystkich płytek z zatwierdzonym layoutem i jedno zamówienie. Każda paczka ma DRC 0 / 0 / 0, kontrolę CAM 20/20, próby ujemne CAM 8/8 z próbą zerową i oględziny podglądów; stan `FABRICATION_FILES_VERIFIED`. Przymiarka 1:1 i odbiór sprzętu: **NIE ZBADANO**.

| Płytka | Plik do wgrania | Wymiar [mm] | Opis | PTH / NPTH | SHA-256 ZIP | Stan |
|---|---|---|---|---|---|---|
| P02 R4 | `P02-PCB-R4-zamowienie/DO-ZAMOWIENIA_P02-PCB-R4.zip` | 160 × 100 | obie | 363 / 16 | `83585ce0…` | zamawiać |
| P03 R6 | `P03-PCB-R6-zamowienie/DO-ZAMOWIENIA_P03-PCB-R6.zip` | 160 × 100 | góra | 448 / 14 | `05997683…` | zamawiać |
| P05 R3 | `P05-PCB-R3-zamowienie/DO-ZAMOWIENIA_P05-PCB-R3.zip` | 106,5 × 100 | obie | 362 / 12 | `2b922d52…` | zamawiać |
| P06 R2 | `P06-PCB-R2-zamowienie/DO-ZAMOWIENIA_P06-PCB-R2.zip` | 106,5 × 100 | obie | 228 / 14 | `d73c5de0…` | zamawiać |
| P09 R2 | `P09-PCB-R2-zamowienie/DO-ZAMOWIENIA_P09-PCB-R2.zip` | 53 × 100 | obie | 157 / 4 | `644e0379…` | **wstrzymana** do pomiaru modułu MAX31856 |
| P10 R2 | `P10-PCB-R2-zamowienie/DO-ZAMOWIENIA_P10-PCB-R2.zip` | 53 × 100 | góra | 74 / 6 | `92e5323c…` | zamawiać |
| P11 R2 | `P11-PCB-R2-zamowienie/DO-ZAMOWIENIA_P11-PCB-R2.zip` | 36 × 100 | obie | wg paczki | `a77181a0…` | zamawiać (gałąź `p11-r2-pcb`) |
| P12 R1 | `P12-PCB-R1-zamowienie/DO-ZAMOWIENIA_P12-PCB-R1.zip` | 160 × 92 | wg paczki | wg paczki | `81cd30f9…` | zamawiać (LOGGER; 24 piny wariantu pełnego niepodłączone) |

Ustawienia JLCPCB dla wszystkich: FR-4, 2 warstwy, 1,6 mm, 1 oz, HASL bezołowiowy, maska zielona, opis biały, Via Covering: Tented, bez PCBA i szablonu. P03 i P10 mają opis tylko od góry (w ZIP nie ma warstwy dolnego opisu). Szczegóły: `SPECYFIKACJA-DLA-PRODUCENTA.txt` w każdej paczce.

Przed wysłaniem:
1. P09 — porównać zmierzony moduł MAX31856 z footprintem (J3 / J4 P09); do tego czasu P09 nie zamawiać.
2. Niezależna recenzja paczek (zadanie dla chmury `Plytki/Format-S1/zadania/ZADANIE-RECENZJA-ZAMOWIENIA-S1.md`) — zalecane przed wysłaniem plików.
3. Wydruk 1:1 z PDF wydania (`projekt/output/pdf/`) i przymiarka dużych części: C1 / C3 220 µF, złącza IDC.

**SW1 P05 (decyzja 4.10 po makiecie panelu):** przełącznik nie jest montowany na P05. Idzie na panel (E-Switch 100 z oczkami), a 5 przewodów wchodzi w otwory footprintu SW1 (1, 2, 3, 5, 4 = GND). Płytka bez zmian.

Taśmy IDC do P12 (do zakupów): 9 krótkich taśm płytka → P12 (ok. 30 mm; P12 stoi 18–20 mm przed krawędzią A) i taśma P11 → P12 ok. 100 mm (szacunek 65–80 mm). Złącza na P12: proste IDC obudowane (Amphenol T821…S100CEU — kod do potwierdzenia w zakupach). Wtyki zaciskać tak, by pin 1 trafiał w pin 1 po obu stronach (rozumowanie: `P12-R1-review/README.md`, PDF str. 5).
