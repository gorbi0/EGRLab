# Niezależna recenzja paczek produkcyjnych przed wspólnym zamówieniem (zadanie dla sesji w chmurze, 4.10.2026)

**Ustawienia sesji:** Opus 5.5, wysiłek high. Baza: `origin/zamowienie-s1`. Gałąź zadania: `recenzja-zamowienia-s1`, wynik (sam raport) jako PR do `zamowienie-s1`.

**Cel:** użytkownik zamawia w JLCPCB naraz sześć płytek (decyzja 4.10). Przed wysłaniem plików niezależny przegląd ma znaleźć wszystko, co zrobi z płytki złom albo wymusi poprawki lutownicą. **Niczego w paczkach nie poprawiać** — tylko raport.

**Paczki:** `Plytki/P02-PCB-R4-zamowienie`, `P03-PCB-R6-zamowienie`, `P05-PCB-R3-zamowienie`, `P06-PCB-R2-zamowienie`, `P09-PCB-R2-zamowienie`, `P10-PCB-R2-zamowienie`. Każda ma `DO-ZAMOWIENIA_*.zip`, `gerber/`, `podglad/`, `verification/` i kopię wydania w `projekt/` (schemat, PCB, BOM, README, PDF). P09 jest wstrzymana do pomiaru modułu MAX31856 przez użytkownika.

**Pamięć:** `docs/pamiec-claude/MEMORY.md` (indeks), `format-s1.md`, `chmura-limity.md`, `kicad-pipeline-quirks.md`. Wcześniejsze recenzje P05 / P06 (2.10) i ich poprawki są w README tych wydań — nie powtarzać tamtych ustaleń, chyba że poprawka nie zadziałała.

## Zasady

`docs/CHMURA.md` 1–9. Zamknięte pakiety uruchamiać **tylko na kopii** w scratchpad (skrypty zapisują do własnego pakietu). Bez trasowania i bez zmian w `Plytki/`.

## Co sprawdzić (priorytety)

1. **Stos S1 między płytkami:** położenia otworów M3, złączy J_BP (IDC kątowe na krawędzi A) i wysokości części względem `Plytki/Format-S1/format-s1.json` — czy płytki sąsiednich poziomów i slotów się skręcą, a taśmy do P12 dojdą (P02 poziom 1, P03 poziom 2, P05 + P09 poziom 3, P06 + P10 poziom 4). Części od spodu ≤ 1,5 mm, od góry ≤ 16,5 mm.
2. **Footprinty z kart katalogowych** dla części, których nie da się poprawić po zamówieniu: P05 SW1 (E-Switch 100 kątowy M6, karta `Plytki/P05-R3-review/reference/E-Switch-100-series.pdf`), P05 / P06 kondensatory 220 µF EEUFR1C221 (średnica, raster), P06 bocznik WSK25125L000FEA (Kelvin), złącza IDC 2×10 / 2×8 / 2×5 kątowe, P09 moduły MAX31856 (raster i rozstaw rzędów — porównać z typowymi modułami i zapisać, co użytkownik ma zmierzyć), P10 złącze OBD / CAN, P02 TSR 2-2450, przełączniki i duże elementy THT. Pin 1, kierunek, średnice otworów wobec wyprowadzeń (+0,2–0,4 mm).
3. **Możliwości JLCPCB** (2 warstwy, 1 oz): ścieżka / odstęp (P05 ma 0,15 mm między wylewką a polami w pierścieniach U1 / U3), pierścienie, najmniejsze otwory, odstęp otwór–otwór, nadruk ≥ 1,0 / 0,15 mm, maska między polami drobnego rastra, miedź przy krawędzi.
4. **Polaryzacje i opisy:** diody, elektrolity, układy (pin 1 na nadruku zgodny z footprintem), czytelność oznaczeń przy częściach od spodu.
5. **Prądy:** tory 5V_SYS, mocy P02 i siły P06 (ECU_P1 / EGR_P1, 6 A, 10 A w próbie) wobec IPC-2152 przy 35 µm.
6. Zgodność BOM ↔ footprint ↔ netlista dla pozycji zmienionych 2.10 (P05 C35, nóżki SW1; P06 C17, szprychy J3 / J4).

## Wynik

`Plytki/Recenzja-zamowienia-S1/RAPORT.md`: dla każdej płytki ustalenia BLOCKER / MAJOR / MINOR z dowodem (plik, współrzędne, strona karty) i propozycją poprawki; na początku jednoznaczna rekomendacja „zamawiać / nie zamawiać” per płytka. Skrypty pomocnicze w `Plytki/Recenzja-zamowienia-S1/src/`. Po PR zakończyć pracę.
