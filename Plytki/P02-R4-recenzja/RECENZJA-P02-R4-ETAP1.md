# Recenzja P02 R4 — etap 1 (schemat)

29.09.2026 · Claude (sesja lokalna).

**Przedmiot:** PR #2, gałąź `p02-r4-schemat`:
- commit b220e04 — krok 0 środowiska;
- commit cace623 — etap 1.

Pakiet `Plytki/P02-R4-review` jest bez PCB. Pracowałem na kopii rozpakowanej z gałęzi.

**Zakres:** zgodność ze specyfikacją i `STAN-PRAC.md`, poprawność obliczeń, pliki wspólne.

## Werdykt

**Etap 1 jest przyjęty i scalony (4ac375d).** Schemat realizuje specyfikację po poprawce architektury:
- Q9 i Q1 pracują przeciwsobnie;
- tor bramki pochodzi z P01 R3, z R23 = 22 kΩ.

Kontrole są rzetelne i mają próby ujemne. Sesja sama wskazała trzy niezgodności ze specyfikacją. Użytkownik rozstrzygnął je według rekomendacji niżej.

## Co sprawdziłem

| Kontrola | Wynik |
|---|---|
| Wyniki sesji | ERC 0 (4 arkusze), netlista 317/317 pinów, 35/35 kontroli elektrycznych, 19/19 prób ujemnych z próbą zerową |
| UVLO niezależnie (wzór z `obliczenia.py`, wartości z BOM) | 13,53 / 12,56 V wobec 13,50 / 12,55 V w pakiecie — różnica mieści się w U01 |
| Udar przy wpięciu XT60 (reguła z P01 R1) | 25 V × C5/(C5 + C6 + Ciss) = 0,29 V przy granicy 0,8 V |
| Podtrzymanie (Z-08) | bilans energii C_H z oboma spadkami na diodach daje ok. 10,9 ms, pakiet podaje 11,1 ms; zapas nad 10 ms ok. 10 % |
| Odwrotna polaryzacja | Q9: D = BAT_IN, S = SW_COM. Odwrotne napięcie pakietu widzi tylko dren Q9 (T02). |
| Odstępstwo od D-06 (PFAIL_N z U2A buforującej OK) | uzasadnione: wariant dosłowny grozi drganiami PFAIL_N albo fałszywym powrotem zasilania; jest próbą ujemną |
| Krok 0 | wersje przypięte, ngspice z obrazu KiCada, próg 2 % dla PNG, uwaga o PDF |
| Pliki wspólne | końce linii zachowane: AKTYWNE 66 linii LF, 01-overview i CHMURA CRLF, STAN-PRAC LF |
| Arkusz WEJ (oględziny) | czytelny, połączenia etykietami jak w R3 |

## Decyzje użytkownika (29.09.2026)

| ID | Temat | Decyzja |
|---|---|---|
| R4E1-01 | Z-01 a transil D3 5KP18A. Przewodzi od 20 V, a pakiet 5S włożony przez pomyłkę ma 21 V. | **5KP24A.** VR 24 V, VBR min 26,7 V. Przy prądach rzędu amperów ogranicza do ok. 30 V, czyli poniżej 35 V kondensatorów i 36 V TSR. Obudowa P600 jak dotąd. |
| R4E1-02 | Z-08: 11,1 ms w najgorszym narożniku zamiast 14 ms | **C_H zostaje 2200 µF.** Firmware potrzebuje ≤ 10 ms. Najgorszy narożnik to wyłączenie przez UVLO przy rozładowanym pakiecie; wyłączenie PWR przy pełnym pakiecie daje ok. 30 ms. 3300 µF/35 V ma zwykle 31–36 mm wysokości wobec limitu 35 mm (Z-15). Z-08 przepisane na ≥ 10 ms w najgorszym narożniku. |
| R4E1-03 | Z-02: obwiednia UVLO 12,90–14,08 V (załączenie) i 11,98–13,11 V (wyłączenie) zamiast ±0,34 V | **Bez zmian w układzie.** ±0,34 V w specyfikacji było zaniżone: składają się na to rezystory 1 %, TL431 i offset LM2903. Wymagania funkcjonalne są spełnione: 3S nie startuje, 4S przy 3,6 V/ogniwo startuje, wyłączenie następuje przed BMS, histereza ≥ 0,84 V. Z-02 i O-02 przepisane na obwiednię. |

## Nowe uwagi

- **R4E1-04 (P11):** włącznik PWR (J14) przewodzi ok. 0,3 mA, czyli pracuje w obwodzie „suchym”. Styki srebrne mogą z czasem dawać przerwy. Przerwa dłuższa niż filtr C13 (ok. 0,1 ms) wyłącza przyrząd w trakcie pomiaru. Dlatego na panelu potrzebny jest przełącznik ze złoconymi stykami, jak SW1 w P05.
- **R4E1-05 (BOM):** R40 — dobrać konkretny rezystor bezpiecznikowy 22 Ω/2 W w obudowie jak PR02; do zrobienia przy liście zakupowej.
- **R4E1-06 (dokumenty):** bezpiecznik przy klemie akumulatora ma mieć 1 A, jak w Z-12; BOM etapu 1 podawał 0,5 A.

## Dla etapu 2

- Wprowadzić do schematu R4E1-01 i R4E1-06 i powtórzyć kontrole.
- Dodać kontrolę Z-01: VBR min transila ≥ 25 V.

Zadanie: `Plytki/P02-R4-specyfikacja/ZADANIE-P02-R4-ETAP2.md`.
