# Zamówienie PCB P00, P01, P02, P04 w Satland Prototype

*28.09.2026. Pliki są zweryfikowane; przymiarka części i próby sprzętu — NIE ZBADANO.*

> **29.09.2026: P01 i P02 WSTRZYMANE** — decyzja o zasilaniu przyrządu z ogniw 18650 (P01 i HOLD w P02 zostaną zastąpione nową płytką zasilania). Zamawiać tylko **P00 i P04**. Tabele i mail niżej obejmują jeszcze cztery płytki.

**Producent:** Satland Prototype sp. z o.o., Gdańsk, ul. Zeusa 61. E-mail biuro@prototypy.com, tel. +48 58 554-07-64 (pn–pt 7:00–15:00). [Kalkulator](https://www.prototypy.com/sites_pcbplugins/pcborder/58).

Dlaczego Satland: przy miedzi 35 µm robi ścieżki i odstępy od 0,2 mm (nasze minimum: ścieżka 0,4 mm, odstęp 0,25 mm), wiercenia 0,3–6,4 mm, pierścienie od 0,2 mm, HAL, maskę i opis obustronnie, w 3–7 dni z wysyłką do paczkomatu. Fabrykapcb.pl zaleca przy 35 µm odstępy ≥ 0,3 mm i gwarantuje metalizację przy pierścieniach ≥ 0,4 mm — nasze płytki tego nie spełniają.

## Decyzja: miedź 35 µm na wszystkich płytkach (28.09.2026)

Projekt zakładał 70 µm dla P01 i P02; zmieniono na 35 µm, bo 70 µm kosztuje około 4× więcej, a pliki CAM są te same (grubość miedzi to tylko parametr zamówienia). Uzasadnienie liczbowe (IPC-2221): przy 5 A najwęższe odcinki toru mocy P01 (2 mm) grzeją się o ok. 17 °C zamiast 5 °C, przewężenie BAT_FUSED 3 mm o 9 °C zamiast 3 °C; w P02 tor VMOTOR 5 A biegnie wylewką VPROT, a szyny za F1 T2A grzeją się najwyżej o ok. 7 °C. Sam rejestrator bez P07 pobiera poniżej 1 A (nagrzewanie poniżej 2 °C). P04 (logika blokad, prądy rzędu miliamperów) od początku zakłada 35 µm. **Warunek: przed pierwszym uruchomieniem P07 wykonać próbę nagrzewania toru mocy P01 i toru VMOTOR P02 przy 0,1 / 1 / 3,5 / 5 A.** Przy zbyt dużym nagrzewaniu: wzmocnić tor przylutowanym przewodem albo zamówić P01/P02 ponownie z 70 µm z tych samych plików.

## Pliki do wysłania

Każdy ZIP to jedna płytka; zamawiać jako osobne pozycje, bez panelu.

| Płytka | Plik | SHA-256 (początek) | Specyfikacja |
|---|---|---|---|
| P00 FIXTURE | `DO-ZAMOWIENIA_P00-PCB-R3.zip` | d45254c5… | `SPECYFIKACJA-P00.txt` |
| P01 PROTECT | `DO-ZAMOWIENIA_P01-PCB-R3.1.zip` | abca5949… | `SPECYFIKACJA-P01.txt` |
| P02 PSU+HOLD | `DO-ZAMOWIENIA_P02-PCB-R3.zip` | 5d9e1479… | `SPECYFIKACJA-P02.txt` |
| P04 SAFE | `DO-ZAMOWIENIA_P04-PCB-R2.2.zip` | 1f7e9b84… | `SPECYFIKACJA-P04.txt` |

Pełne sumy w plikach `.sha256`; źródła i raporty kontroli w `Plytki/P00-PCB-R3-zamowienie`, `P01-PCB-R3.1-zamowienie`, `P02-PCB-R3-zamowienie`, `P04-PCB-R2.2-zamowienie`.

## Ustawienia w kalkulatorze

| Pole | P00 | P01 | P02 | P04 |
|---|---|---|---|---|
| Laminat | FR4 | FR4 | FR4 | FR4 |
| Liczba warstw | dwustronna | dwustronna | dwustronna | dwustronna |
| Grubość laminatu | 1,5 mm | 1,5 mm | 1,5 mm | 1,5 mm |
| Grubość miedzi | **35 µm** | **35 µm** | **35 µm** | **35 µm** |
| Wymiar | 115 × 70 mm (0,81 dm²) | 160 × 120 mm (1,92 dm²) | 160 × 120 mm (1,92 dm²) | 160 × 120 mm (1,92 dm²) |
| Cynowanie | HAL | HAL | HAL | HAL |
| Soldermaska | dwustronna, zielona | dwustronna, zielona | dwustronna, zielona | dwustronna, zielona |
| Opis | **jednostronny (góra)**, biały | **dwustronny**, biały | **jednostronny (góra)**, biały | **jednostronny (góra)**, biały |
| Złocenie, frezowanie, V-cut, metalizacja krawędzi | nie | nie | nie | nie |
| Wysyłka | Paczkomat InPost | — | — | — |

**P04 jest najdrobniejsza z czterech:** 101 przelotek 0,8/0,4 mm z pierścieniem 0,20 mm, czyli dokładnie na minimum Satlandu (pozostałe płytki mają najmniej 0,25 mm), i najwęższa ścieżka 0,3 mm. Mieści się w ich parametrach, ale w mailu jest o to osobne pytanie. W JLCPCB to bez znaczenia.

Projekt zakłada laminat 1,6 mm; Satland podaje w kalkulatorze 1,5 mm i to jest akceptowalne dla montażu THT tych płytek. Liczbę sztuk i termin wybierasz sam. Terminy w kalkulatorze: STANDARD PLUS 7 dni, EXPRESS 5 dni, SUPER EXPRESS 3 dni; 24 h i 8 h wymagają potwierdzenia telefonicznego i złożenia plików do ustalonej godziny. Czy są to dni robocze i od kiedy liczone — potwierdzić w wycenie. Cena z kalkulatora może się zmienić po weryfikacji plików.

## Przed wysłaniem

1. **Wydruki 1:1** (skala 100 %, zmierzyć belkę 100 mm i obrys):
   - P00: `P00-PCB-R3-zamowienie/projekt/output/pdf/P00-R3-PCB.pdf` (nie PDF R2 z tego samego katalogu);
   - P01: `P01-PCB-R3.1-zamowienie/projekt/output/pdf/P01-PCB-R3.1-dokumentacja.pdf`;
   - P02: `P02-PCB-R3-zamowienie/projekt/output/pdf/P02-R3-PCB.pdf`;
   - P04: `P04-PCB-R2.2-zamowienie/projekt/output/pdf/P04-R2.2-PCB.pdf`.
2. **Przymiarka części, które już masz.** P01: radiatory SK129 z Q1/D2 w tulejkach IB-6 i podkładkach, C6, J6 (MSTBA 3p), D3 5KP18A. P02: TSR 2-2450/2-2433, MCP120, 74HC08, adapter U5 z 74LVC125A. P00: TLC555 w podstawce. P04: podstawki DIP14/DIP16 i adapter Kamami SO14 z goldpinami w miejscu U8–U10 (rzędy co 15,24 mm; docelowo adapter stoi na listwach żeńskich 1×7). Reszty (Würth WS-SLTV, Mini-Fit — także J7/J8 w P04, złącza IDC J3–J6 w P04, oprawki PTF78, kondensatory 22 mF Ø35, GMSTBA) jeszcze nie masz: albo poczekać na nie, albo zamówić na podstawie footprintów z kart katalogowych.
3. **W mailu zadać trzy pytania** (tekst w `MAIL-DO-SATLAND.txt`): test elektryczny, HAL bezołowiowy, pierścień 0,2 mm przelotek P04.
4. Jeśli Satland przyśle podgląd CAM, porównać go z `podglad/CAM-top.png` i `CAM-bottom.png` z paczki każdej płytki (spód oglądany od spodu).

## Porównanie: JLCPCB

Te same ZIP-y można wgrać do konfiguratora JLCPCB (jeden ZIP = jedna pozycja). Ustawienia dla wszystkich czterech płytek: FR-4; 2 warstwy (wykrywane z plików); wymiar wykryty z pliku — może pokazać +0,05 mm, nie poprawiać; PCB Qty 5 (minimum); Industrial/Consumer electronics; Different Design 1; Single PCB; **PCB Thickness 1.6 mm**; zielona / biały; Material Type FR4 TG135; LeadFree HASL (albo tańszy HASL with lead — do ręcznego lutowania wystarczy); **Outer Copper Weight 1 oz**; Via Covering: Tented; Via Plating Method: Not Specified (nie „Conductive Adhesive”); Min via hole 0.3mm/(0.4/0.45mm); Board Outline Tolerance ±0.2 mm; Electrical Test: Flying Probe; Gold Fingers, Castellated Holes, Edge Plating, Blind Slots, UL Marking — No; bez montażu i szablonu. „Mark on PCB”: numer zamówienia JLC w dowolnym miejscu opisu albo „Remove Mark” za dopłatą. Do ceny dojdą wysyłka z Chin i VAT pokazane w koszyku.

## Po dostawie

Sprawdzić wymiary suwmiarką, średnice i metalizację otworów, lutowność pól i maskę. Multimetrem, przed montażem: brak zwarć między masą a każdą szyną zasilania — P00: VIN, 3V3; P01: szyny wejściowa i zabezpieczona (według `P01-PCB-R3.1-zamowienie/INSTRUKCJA-ZAMOWIENIA.md`, sekcja „Odbiór”); P02: VPROT, VLOG_RES, 5V_SYS, 3V3_IO; P04: 3V3_IO, 5V_SYS. Dalej montaż i uruchamianie według dokumentacji w `projekt/` każdej paczki.
