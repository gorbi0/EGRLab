# Odbiór S1 — narzędzia, części i kolejność montażu

*4.10.2026, sesja w chmurze (zadanie `Plytki/Format-S1/zadania/ZADANIE-ODBIOR-S1.md`). Dotyczy płytek z zamówienia S1: P02 R4, P03 R6, P05 R3, P06 R2, P09 R2, P10 R2. Źródła: README, `docs/` i `routing/solid-pads.json` wydań oraz paczek `…-zamowienie/projekt`. Procedura uruchomienia: `URUCHOMIENIE.md`, formularz: `FORMULARZ-ODBIORU.md`.*

## 1. Przyrządy

| Przyrząd | Do czego | Uwagi |
|---|---|---|
| Zasilacz laboratoryjny z ograniczeniem prądu | P02 R4: 0–17 V, do 2 A (rampa UVLO, start z C12); płytki 5 V: 5,00 V z limitem 20–800 mA | **Zakres posiadanego zasilacza nie jest zapisany w repozytorium** — pytanie w PR. Do próby odwrotnej polaryzacji P02 (O-01) wystarczy zamiana przewodów. Drugi kanał 3,3 V przydaje się dla P09/P10 (inaczej 3V3_IO z P02, rozdz. 4.4 procedury). |
| Multimetr | napięcia na kołkach, rezystancje, zwarcia, VREF | Wejście 10 MΩ: przez rezystor 10 kΩ kołka zaniża o ok. 0,1 % — **REF_2V5 (P05) i REF25 (P06) mierzyć na węźle przed skręceniem stosu** albo miernikiem ≥ 1 GΩ. |
| Wzorzec prądu dla P06 | kalibracja ±0,5…6 A, cel reszty ≤ max(30 mA, 1 %) | MS2115A (cęgowy) ma dokładność DC rzędu kilku procent — **nie wystarcza**. Wzorcem jest multimetr na zakresie 10 A DC albo bocznik 0,1 Ω 1 % (≥ 5 W) mierzony multimetrem na zakresie mV. Pytanie w PR: jaki multimetr jest na stole. |
| DHO804 + 2 sondy ×10 (Hantek PP-150) | start 5V_SYS, PFAIL_N, DAQ_OK, CONVST/BUSY, SPI, CAN | Przewody RG174 1X zostają do auta; na stole sondy ×10 z krótką masą. Sonda to 15 pF — przez rezystor kołka 1 kΩ daje 15 ns, przez 10 kΩ 150 ns. |
| Termometr odniesienia | P09: otoczenie i woda z lodem | Dowolny z kalibracją lub drugi typ K z innym odczytem. |
| Naczynie z lodem i wodą | P09: punkt 0 °C | Kruszony lód z wodą destylowaną, mieszać, końcówka termopary nie dotyka dna ani ścianek. |
| Rezystory obciążeniowe | P02: 4,7 Ω / 10 W (ok. 1,06 A = budżet LOGGER), 10 Ω / 5 W (ok. 0,5 A), 1 kΩ / 0,25 W | 4,7 Ω ≈ 6 W z VLOG razem ze stratami, 10 Ω ≈ 3 W — do O-05. |
| Kondensator 470 µF / 16 V | P02: makieta pojemności 5V_SYS przed wpięciem płytek | Razem z C22/C26 P02 daje ok. 492 µF, czyli tyle, ile ma komplet LOGGER. |
| Stanowisko P00 (jeśli zmontowane) | poziomy H/L 3,3 V przez 1 kΩ na wejścia P05/P06 bez P03 | Zasilanie P00 9–12 V z osobnego kanału. Bez P00 wystarczy przewód z 3V3_IO przez 1 kΩ. |
| Dwa węzły CAN z ACK + 2 × 120 Ω | P10: RX, brak ACK, ruch ciągły 10 min, dekoder RPM | **Brak na liście sprzętu.** Najprościej dwa tanie adaptery USB-CAN (candleLight/CANable, slcan lub gs_usb) albo jeden adapter + moduł MCP2515 z Arduino. vLinker MC+ jest testerem OBD, nie generatorem ramek. Pytanie w PR. |
| Komputer z Pythonem | wgrywanie firmware, odczyt logów | `pip install esptool pyserial`; `Rewizje/EGRLab-v6.2-s1/tools/egrlog.py` do eksportu sesji z karty SD. |
| Karta microSD FAT32 | P03: `core_probe.tmp`, sesje | **Bez karty wariant firmware zatrzymuje się na montowaniu SD** (poza trybem stołowym). |

## 2. Lutowanie i drobne części

| Pozycja | Uwagi |
|---|---|
| Stacja lutownicza ≥ 60 W z grotem dłutowym 2–3 mm | do zwykłych pól |
| **Druga, mocniejsza lutownica (≥ 80 W, grot 4–5 mm) albo podgrzewacz od spodu / gorące powietrze** | pola z pełnym połączeniem ze strefą (tabela niżej), bocznik P06, przewody 1,5–2,5 mm² |
| Topnik bezołowiowy w pisaku i żelu (no-clean) | SMD 1206, SOIC, LQFP-64 (P05 U1) |
| Cyna 0,5 mm i 0,8–1,0 mm | drobne / przewody |
| Plecionka i odsysacz | mostki na U1 P05 i SOIC |
| Lupa ≥ 5× albo mikroskop | oględziny LQFP 0,5 mm (P05 U1) i VSSOP 0,65 mm (P05 U3) |
| Alkohol IPA, pędzelek | mycie topnika przed pomiarami (topnik pod U1 P05 i przy węzłach 10 kΩ fałszuje pomiary) |
| Opaski kablowe 2,5 mm, klej (np. silikon neutralny) | kotwy przewodów P02 J1/J14/J15, P06 J3/J4/J5, P10 J3; C12 P02 leży płasko (klej lub opaska) |
| Taśma IDC 1,27 mm, 20 żył, gniazda IDC 2×5 / 2×8 / 2×10, przewody dupont F-F 20 cm, złączki Wago 221 | **połączenia stołowe bez P12** (`URUCHOMIENIE.md`, rozdz. 1.3) |
| Przewód 1,5 mm² z XT60 | pakiet 4S → P02 J1 |
| Pakiet 4S: 4 × 18650 (≥ 5 A ciągle), koszyk z odczepami, BMS 4S (≥ 8 A), bezpiecznik mini 7,5 A, XT60 | `Plytki/P02-R4-specyfikacja/SPECYFIKACJA-P02-R4.md`, rozdz. 7 |
| Bezpieczniki mini 32 V: 5 A (F1), 2 × 1 A (F2, F3) | F1–F3 są w oprawkach — na pierwsze zasilenie P02 wyjęte |

## 3. Pola z pełnym połączeniem ze strefą GND / mocy

Router odciął szprychy odciążeń termicznych, więc te pola łączą się z całą wylewką. Lutować mocniejszą lutownicą, z topnikiem, trzymać grot do pełnego zwilżenia otworu; sprawdzić lut od drugiej strony. Źródło: `routing/solid-pads.json` każdej paczki produkcyjnej (identyczne z wydaniami).

| Płytka | Pola | Uwagi |
|---|---|---|
| P02 R4 | C8.2, **D3.2**, LED1.1, U10.4, U2.4 | D3.2 to wyprowadzenie transila P600 (gruby drut) — najtrudniejsze. U2/U10 są w podstawkach: lutuje się podstawkę. |
| P03 R6 | J_BP2.5, J_BP2.7, J_BP2.9, J_BP2.11, J_BP3.15, J_BP3.19, U1.17 | piny złączy IDC na GND |
| P05 R3 | C32.2, J_BP2.9, J_BP2.11, SW1.4, U4.3, U4.5, U4.6, U4.7 | dodatkowo **wszystkie piny GND U1** łączą się pełnym polem z wylewką wewnątrz pierścienia (decyzja 4 w README P05 R3) — przy U1 topnik i gorące powietrze; SW1.4 obejmuje nóżki mocujące (oprawa na masie) |
| P06 R2 | J_BP.15 | dodatkowo **pola RSH1** (bocznik 2512) mają pełne połączenie z wylewkami mocy na obu warstwach — lutować gorącym powietrzem z podgrzewaniem od spodu, na gołej płytce, jako pierwszą część; pola J3/J4 mają 4 szprychy 2 mm |
| P09 R2 | J1.5, J1.11, J4.3 | J4.3 to GND modułu TC2 |
| P10 R2 | — | brak |

## 4. Części od spodu (SMD) — zestawienie

Z plików PCB paczek produkcyjnych (warstwa B.Cu):

| Płytka | Części od spodu | Wysokość |
|---|---|---|
| P02 R4 | **U9 (SOIC-14, 74LVC125A)**, C27, C28 | poziom 1, SOIC dozwolony (S1-2) |
| P03 R6 | brak | — |
| P05 R3 | C5, C7, C8, C11 (100 nF pod U1), C25, C26 (10 nF), R9, R21, R36–R42, R44–R55 | ≤ 1,5 mm (BOM: grubość 100 nF ≤ 1,5 mm) |
| P06 R2 | C2 (470 pF pod U3), C8, R9, R10, R14, R20, R24–R38 | ≤ 1,5 mm |
| P09 R2 | R20–R30 (rezystory listwy) | ≤ 1,5 mm |
| P10 R2 | brak | — |

Wyprowadzenia THT od spodu przyciąć do ≤ 1,5 mm na poziomach 3 i 4 (P05, P06, P09, P10) — spód leży nad częściami niższej płytki.

## 5. Kolejność montażu

Zasada: najpierw części najtrudniejsze i najniższe na gołej płytce, potem spód, potem góra od najniższych do najwyższych, na końcu złącza, elementy duże i moduły. Po każdym bloku pomiar zwarć z `URUCHOMIENIE.md`, rozdz. 2.

1. **Drobny raster od góry na gołej płytce** — tylko P05: U1 (LQFP-64, 0,5 mm) i U3 (VSSOP-8). Topnik, lut, plecionka, oględziny pod lupą, umycie. Od razu ciągłość: brak zwarć sąsiednich pinów, piny 44/45 zwarte, 36/39 nie (krok 2 ODBIOR P05).
2. **Duże pole mocy na gołej płytce** — tylko P06: RSH1 (gorące powietrze + podgrzewanie od spodu), potem przewody/pola toru mocy według kolejności bloków z `P06-R2-review/docs/ODBIOR.md` (mechanika i RSH1 → tor mocy/SW1 → R6/U4/C3/C4/D1 → U10/C5/D2 → U1/U2 → U3/U5 → U6–U9 → rezystory i listwy → J_BP).
3. **SMD od spodu** (tabela 4): płytka leży górą na miękkiej podkładce. P02: najpierw U9 (SOIC), potem C27/C28. P05: najpierw 100 nF pod U1 (C5, C7, C8, C11) — przelotki 0,14 mm od pól, nie zalać cyną; potem C25/C26 i rezystory listew. P06: C2 przy IN+/IN− U3 (krótko), C8, potem rezystory.
4. **SMD od góry:** SOIC i SOT-23 (P03: U11–U14, U21–U23 lutowane wprost; U3 SOT-23-6 i U5 TSOT-23-6 — nie zamienić; U4 LVC1G37 i U6 LVC1G17 mają ten sam układ pinów, inne funkcje — rozpoznać po oznaczeniu), potem 1206.
5. **THT niskie:** posiadane rezystory MF0207 na stojąco (P05 R13, R43; P06 R11; P10 R2, R8, R9), diody (polaryzacja), K15 (P10 C1–C3), podstawki DIP (P02 U2/U10, P03 DIP28/DIP16, P06 U2/U3).
6. **Półprzewodniki mocy i TO-220 (P02):** Q9, Q1, Q2 (SUP53P06), D1/D2 STPS20100CT (wspólna katoda = blaszka; D1 na stojąco, nóżki 4 mm), D3 P600. Kierunek według nadruku i rysunku montażowego F.Fab.
7. **Złącza:** IDC J_BP (pin 1 od mniejszego x, wycięcie klucza według nadruku), listwy kątowe J_SV (kołki ok. 6 mm za krawędź B), GMSTBA (P02 J2), oprawki bezpieczników.
8. **Duże elementy:** elektrolity (P02 C12 2200 µF płasko + klej/opaska, C3, C20; P05 C1 220 µF; P06 C3 220 µF — polaryzacja), przekaźniki P05 K1–K3 (**po próbie 10a**: napięcie zadziałania ≤ 3,9 V przy ok. 23 °C), P05 SW1 (E-Switch M6), P06 R21 PR02 leżący 3–5 mm nad płytką, P06 R6 / P05 R1 KNP01U leżące.
9. **Moduły:** P03 M1 (Waveshare N32R16V) na listwach żeńskich — wkładać dopiero po pierwszym zasileniu płytki bez modułu (`URUCHOMIENIE.md`, 4.2). P09 moduły MAX31856 lutowane wprost — **dopiero po krokach 1–4 `P09-R2-review/docs/MODUL-KWALIFIKACJA.md`** (po przylutowaniu nie ma regulacji). Na module M1 zdjąć diodę RGB z GPIO38 (BOM P03).
10. **Przewody:** P02 J1 (2 × 1,5 mm²), J14 (PWR, 2 × AWG22), J15 (VBAT, AWG22) z kotwami opasek; P06 J3/J4 (2,5 mm²), J5; P10 J3 (skrętka W3, H → pole „H”). Lutować na końcu, żeby przewody nie przeszkadzały w pomiarach.

## 6. Rzeczy łatwe do pomylenia

- **Nigdy nie łącz dwóch złączy J_BP prostą taśmą** — pinouty są różne (np. P03 J_BP2.19/20 = 5V_SYS, P05 J_BP2.19/20 = GND: prosta taśma zwiera 5V_SYS z masą). Bez P12 tylko połączenia z tabeli `URUCHOMIENIE.md` 1.3.
- Kątowa listwa serwisowa widziana z góry ma pin 1 **przy większym x** (P03, P05, P06, P09, P10); pin 1 i ostatni = GND. Zawsze sprawdzić z nadrukiem.
- Kołki serwisowe mają rezystory 1 / 4,7 / 10 kΩ — mierzy się nimi napięcia, nigdy prąd, i nie podaje się przez nie zasilania.
- P02: D1/D2 STPS20100CT to wspólna katoda (nie wspólna anoda); U9 74LVC125A od spodu, pin 1 według nadruku spodu.
- P03: Q1 AO3401A — nie zamienić źródła z drenem (G=1, S=2 do M1, D=3 do SYS).
- Nie łączyć 3V3_CORE (P03) z 3V3_IO (P02).
